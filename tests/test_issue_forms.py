"""Checks the issue forms and config.yml against GitHub's issue-form rules.

GitHub only reports a broken form when someone opens the issue chooser, so this catches it first.
"""

import json
import re
import unittest

from helpers import FORMS_DIR, ROOT, form_paths, load_yaml

TOP_LEVEL = {"name", "description", "title", "labels", "assignees", "projects", "type", "body"}
ATTRIBUTES = {
    "markdown": {"value"},
    "textarea": {"label", "description", "placeholder", "value", "render"},
    "input": {"label", "description", "placeholder", "value"},
    "dropdown": {"label", "description", "multiple", "options", "default"},
    "checkboxes": {"label", "description", "options"},
}
ID = re.compile(r"^[A-Za-z0-9_-]+$")


class IssueForms(unittest.TestCase):
    def test_there_are_forms(self):
        self.assertGreaterEqual(len(form_paths()), 2)

    def test_each_form_is_valid(self):
        names = set()
        for path in form_paths():
            with self.subTest(form=path.name):
                form = load_yaml(path)
                self.assertLessEqual(set(form), TOP_LEVEL, "unknown top-level key")
                for key in ("name", "description", "body"):
                    self.assertTrue(form.get(key), f"missing {key}")
                self.assertNotIn(form["name"], names, "two forms share a name")
                names.add(form["name"])
                self.assertIsInstance(form.get("labels", []), list)

                ids, labels = set(), set()
                for item in form["body"]:
                    kind = item.get("type")
                    self.assertIn(kind, ATTRIBUTES, f"unknown body type {kind!r}")
                    self.assertLessEqual(set(item), {"type", "id", "attributes", "validations"})
                    attributes = item.get("attributes", {})
                    self.assertLessEqual(set(attributes), ATTRIBUTES[kind], f"unknown attribute in {kind}")

                    if kind == "markdown":
                        self.assertTrue(attributes.get("value"))
                        self.assertNotIn("id", item)
                        self.assertNotIn("validations", item)
                        continue

                    label = attributes.get("label")
                    self.assertTrue(label, "field without a label")
                    self.assertNotIn(label, labels, f"duplicate label {label!r}")
                    labels.add(label)
                    if "id" in item:
                        self.assertRegex(item["id"], ID)
                        self.assertNotIn(item["id"], ids, f"duplicate id {item['id']!r}")
                        ids.add(item["id"])
                    self.assertLessEqual(set(item.get("validations", {})), {"required"})

                    if kind == "dropdown":
                        options = attributes.get("options")
                        self.assertTrue(options, f"{label}: no options")
                        self.assertEqual(len(options), len(set(options)), f"{label}: duplicate option")
                        self.assertNotIn("None", options, f"{label}: 'None' is reserved by GitHub")
                    if kind == "checkboxes":
                        options = [option["label"] for option in attributes.get("options", [])]
                        self.assertTrue(options, f"{label}: no options")
                        self.assertEqual(len(options), len(set(options)), f"{label}: duplicate option")

    def test_shared_dropdowns_offer_the_same_choices(self):
        # Priority means the same thing in every form, so the labels it creates stay comparable.
        seen = {}
        for path in form_paths():
            for item in load_yaml(path)["body"]:
                if item["type"] != "dropdown":
                    continue
                label = item["attributes"]["label"]
                options = item["attributes"]["options"]
                if label in seen:
                    self.assertEqual(options, seen[label], f"{label} differs in {path.name}")
                seen[label] = options

    def test_config(self):
        config = load_yaml(FORMS_DIR / "config.yml")
        self.assertLessEqual(set(config), {"blank_issues_enabled", "contact_links"})
        self.assertIsInstance(config["blank_issues_enabled"], bool)
        for link in config.get("contact_links", []):
            self.assertEqual(set(link), {"name", "url", "about"})
            self.assertTrue(link["url"].startswith("https://"))


class WorkflowTemplate(unittest.TestCase):
    def test_properties(self):
        for path in (ROOT / "workflow-templates").glob("*.properties.json"):
            with self.subTest(template=path.name):
                properties = json.loads(path.read_text(encoding="utf-8"))
                self.assertTrue(properties.get("name"))
                self.assertTrue(properties.get("description"))
                workflow = path.with_name(path.name.replace(".properties.json", ".yml"))
                self.assertTrue(workflow.exists(), f"{workflow.name} is missing")


if __name__ == "__main__":
    unittest.main()
