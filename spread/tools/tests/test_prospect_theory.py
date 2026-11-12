"""Checks the calculator against the claims the playbook makes.

Run: python3 -m unittest discover -s tools/tests
"""

import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import prospect_theory as pt  # noqa: E402


class ValueFunction(unittest.TestCase):
    def test_reference_point_is_zero(self):
        self.assertEqual(pt.value(0), 0)

    def test_concave_gains_convex_losses(self):
        # Diminishing sensitivity in both domains.
        self.assertGreater(pt.value(5) - pt.value(0), pt.value(1005) - pt.value(1000))
        self.assertGreater(pt.value(0) - pt.value(-5), pt.value(-1000) - pt.value(-1005))

    def test_loss_aversion_about_double(self):
        ratio = -pt.value(-100) / pt.value(100)
        self.assertAlmostEqual(ratio, 2.25, places=6)

    def test_inverse(self):
        for x in (-250.0, -1.0, 0.0, 3.0, 1000.0):
            self.assertAlmostEqual(pt.inverse_value(pt.value(x)), x, places=6)


class ProbabilityWeighting(unittest.TestCase):
    def test_article_numbers(self):
        # "un 1 % real se procesa como si fuera un 6 % y un 95 % ... cerca de un 80 %"
        self.assertAlmostEqual(pt.weight(0.01), 0.055, delta=0.005)
        self.assertAlmostEqual(pt.weight(0.95), 0.79, delta=0.01)

    def test_overweights_small_underweights_large(self):
        for p in (0.001, 0.01, 0.05, 0.1):
            self.assertGreater(pt.weight(p), p)
        for p in (0.5, 0.8, 0.95, 0.99):
            self.assertLess(pt.weight(p), p)

    def test_endpoints_and_range(self):
        self.assertEqual(pt.weight(0.0), 0.0)
        self.assertEqual(pt.weight(1.0), 1.0)
        with self.assertRaises(ValueError):
            pt.weight(1.5)


class Prospects(unittest.TestCase):
    def test_risk_averse_for_gains(self):
        # Sure $5 beats a coin flip for $0 or $10.
        self.assertGreater(pt.prospect_value([(5, 1)]), pt.prospect_value([(10, .5), (0, .5)]))

    def test_risk_seeking_for_losses(self):
        # Coin flip for -$10 or $0 beats a sure -$5.
        self.assertGreater(pt.prospect_value([(-10, .5), (0, .5)]), pt.prospect_value([(-5, 1)]))

    def test_lottery_and_insurance_same_day(self):
        # Buys the lottery ticket (CE > EV) and the insurance (pays more than EV to avoid loss).
        self.assertGreater(pt.certainty_equivalent([(1000, .01), (0, .99)]), 10)
        self.assertLess(pt.certainty_equivalent([(-1000, .01), (0, .99)]), -10)

    def test_probabilities_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            pt.prospect_value([(10, .5), (0, .4)])

    def test_ties_are_merged(self):
        self.assertAlmostEqual(pt.prospect_value([(10, .25), (10, .25), (0, .5)]),
                               pt.prospect_value([(10, .5), (0, .5)]))


class HedonicEditing(unittest.TestCase):
    def test_segregate_gains(self):
        r = pt.hedonic_edit([40, 40])
        self.assertEqual(r.recommendation, "segregate")
        self.assertTrue(r.agrees)

    def test_integrate_losses(self):
        r = pt.hedonic_edit([-40, -40])
        self.assertEqual(r.recommendation, "integrate")
        self.assertTrue(r.agrees)

    def test_cancellation(self):
        r = pt.hedonic_edit([1000, -20])
        self.assertEqual(r.recommendation, "integrate")
        self.assertTrue(r.agrees)

    def test_silver_lining_only_when_gain_is_tiny(self):
        # The playbook warns that with lambda = 2.25 rule 4 needs loss/gain > ~300.
        self.assertEqual(pt.hedonic_edit([2, -1000]).recommendation, "segregate")
        realistic = pt.hedonic_edit([2, -10])  # $2 cashback on a $10 monthly fee
        self.assertEqual(realistic.heuristic, "segregate")
        self.assertEqual(realistic.recommendation, "integrate")
        self.assertFalse(realistic.agrees)

    def test_silver_lining_holds_without_loss_aversion(self):
        no_la = pt.Params(lam=1.0)
        self.assertEqual(pt.hedonic_edit([20, -1000], no_la).recommendation, "segregate")


class ProductHelpers(unittest.TestCase):
    def test_frame(self):
        r = pt.frame_comparison(300)
        self.assertAlmostEqual(r.ratio, 2.25, places=6)
        self.assertGreater(r.loss_frame, 2 * r.gain_frame)

    def test_raffle_beats_same_cost_sure_reward(self):
        r = pt.raffle(1000, 0.01, sure=10)
        self.assertAlmostEqual(r.expected_value, 10)
        self.assertGreater(r.felt_value, r.sure_reward)
        self.assertAlmostEqual(r.felt_value, 37.2, delta=0.5)

    def test_cli_runs(self):
        for argv in (["value", "5", "-5"], ["weight", "0.01"], ["edit", "2", "-10"],
                     ["frame", "300"], ["raffle", "--prize", "1000", "--prob", "0.01"],
                     ["prospect", "--", "-10:0.5,0:0.5", "-5:1"]):
            with self.subTest(argv=argv):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(pt.main(argv), 0)


if __name__ == "__main__":
    unittest.main()
