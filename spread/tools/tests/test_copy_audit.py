"""Checks each auditor rule fires on the copy it targets and stays quiet on noise.

Run: python3 -m unittest discover -s tools/tests
"""

import contextlib
import io
import os
import re
import sys
import tempfile
import unittest
import unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import copy_audit as ca  # noqa: E402



def rules_for(text):
    return {f.rule for f in ca.audit_text(text)}


class Fires(unittest.TestCase):
    CASES = {
        "PT01": "Comisión: $120\nSpread: 0,8%\nFee de red: USD 1,20",
        "PT02": "Cuota mensual $10 menos cashback $2",
        "PT03": "Este mes ganaste $4.500 en total",
        "PT04": "Activá rendimientos y ganá 300 USD al año",
        "PT05": "Enviá dinero al exterior más rápido y más barato que con SWIFT",
        "PT06": "Participá del sorteo de un iPhone",
        "PT07": "Invitá a un amigo y llevate $5",
        "PT08": "Increase your conversion rate.",
        "SP01": "Our AI agents turn buying signals into pipeline.",
        "PT90": "Transferencias gratis*",
    }

    def test_each_rule(self):
        for rule, text in self.CASES.items():
            with self.subTest(rule=rule):
                self.assertIn(rule, rules_for(text))

    def test_english(self):
        self.assertIn("PT04", rules_for("Earn up to 5% APY on your idle balance."))
        self.assertIn("PT03", rules_for("You've earned $320 so far this year."))
        self.assertIn("PT05", rules_for("Save up to 80% vs. your bank on international wires."))
        self.assertIn("PT02", rules_for("Cashback is applied to your statement balance."))
        self.assertIn("PT01", rules_for("Commission: $3\nNetwork fee: $1.20"))

    def test_inertia_context_raises_priority(self):
        f = [x for x in ca.audit_text("Más barato que tu banco") if x.rule == "PT05"][0]
        self.assertIn("prioridad alta", f.why)

    def test_b2b(self):
        self.assertIn("PT08", rules_for("Aumentá tus ventas con un sistema de outbound"))
        self.assertIn("PT08", rules_for("We help B2B SaaS grow pipeline"))
        self.assertIn("SP01", rules_for("Usamos Prospect Theory y economía conductual"))
        f = [x for x in ca.audit_text("Get more meetings than your agency ever booked") if x.rule == "PT08"][0]
        self.assertIn("prioridad alta", f.why)

    def test_loss_framed_promise_is_not_flagged(self):
        # The house example: already a loss frame.
        text = ("You're already paying to bring the right companies to your site. "
                "We're fixing what happens before they disappear.")
        self.assertNotIn("PT08", rules_for(text))
        self.assertNotIn("PT08", rules_for("Estás perdiendo reuniones: aumentá tu conversión"))

    def test_brand_name_spread_is_not_a_cost(self):
        self.assertEqual(rules_for("Spread arma tu pipeline. Fee mensual: $5.000"), set())
        self.assertIn("PT01", rules_for("Spread: 0,8%\nComisión: $3"))

    def test_soft_comparison_needs_inertia_context(self):
        self.assertNotIn("PT05", rules_for("Una app más simple"))
        self.assertIn("PT05", rules_for("Una forma más simple de dolarizar"))


class StaysQuiet(unittest.TestCase):
    NOISE = [
        "Al menos 3 personas quedan a cargo del soporte",
        "Tengo ganas de viajar",
        "Guardá tus cambios (save)",
        "TNA 35% anual",
        "Our fee is a flat $2 per transfer.",
        "Who is in charge of this account?",
        '"fee.title": "Comisión $5"',  # one cost; the key is not copy
        "Comisión: sin cargo",  # no amount, not an itemised breakdown
    ]

    def test_noise(self):
        for text in self.NOISE:
            with self.subTest(text=text):
                self.assertEqual(rules_for(text), set())

    def test_inline_ignore(self):
        self.assertEqual(rules_for("Ganá 100 USD hoy  prospect-audit: ignore"), set())

    def test_rule_filter(self):
        text = "Ganá 300 USD al año\nParticipá del sorteo"
        self.assertEqual({f.rule for f in ca.audit_text(text, rules={"PT06"})}, {"PT06"})


class Files(unittest.TestCase):
    def test_walk_skips_vendor_and_binaries(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "node_modules"))
            with open(os.path.join(d, "node_modules", "x.json"), "w") as fh:
                fh.write("Ganá 300 USD")
            with open(os.path.join(d, "a.json"), "w", encoding="utf-8") as fh:
                fh.write('{"cta": "Ganá 300 USD al año"}')
            with open(os.path.join(d, "b.png"), "wb") as fh:
                fh.write(b"\x89PNG\x00Gana 300 USD")
            findings, scanned = ca.audit_paths([d])
            self.assertEqual(scanned, 1)
            self.assertEqual({f.rule for f in findings}, {"PT04"})

    def test_renderers(self):
        findings = ca.audit_text("Ganá 300 USD al año\nParticipá del sorteo")
        self.assertIn("PT04", ca.render_text(findings, 1))
        md = ca.render_md(findings, 1)
        self.assertIn("## PT04", md)
        self.assertIn("## PT06", md)

    def test_strict_exit_code(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
            fh.write("Ganá 300 USD al año")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ca.main([fh.name, "--format", "json"]), 0)
                self.assertEqual(ca.main([fh.name, "--strict", "--format", "json"]), 1)
        finally:
            os.unlink(fh.name)


def github_slug(heading):
    """Approximation of GitHub's heading anchor algorithm."""
    s = heading.strip().lower()
    s = "".join(ch for ch in s if ch.isalnum() or ch in " -_" or unicodedata.category(ch) == "Mn")
    return s.replace(" ", "-")


class PlaybookLinks(unittest.TestCase):
    def test_every_rule_anchor_exists(self):
        with open(ca.PLAYBOOK_FILE, encoding="utf-8") as fh:
            text = re.sub(r"^```.*?^```", "", fh.read(), flags=re.M | re.S)  # skip code blocks
        headings = re.findall(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.M)
        slugs = {github_slug(h) for h in headings}
        for rule in ca.RULES.values():
            with self.subTest(rule=rule.id):
                self.assertIn(rule.anchor, slugs)


class DocLinks(unittest.TestCase):
    def test_relative_links_resolve(self):
        spread = os.path.normpath(os.path.join(os.path.dirname(ca.PLAYBOOK_FILE), ".."))
        for dirpath, _, files in os.walk(spread):
            for name in files:
                if not name.endswith(".md"):
                    continue
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8") as fh:
                    text = fh.read()
                for target in re.findall(r"\]\(([^)#:]+?)(?:#[^)]*)?\)", text):
                    with self.subTest(doc=os.path.relpath(path, spread), link=target):
                        self.assertTrue(os.path.exists(os.path.join(dirpath, target)))


if __name__ == "__main__":
    unittest.main()
