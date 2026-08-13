import unittest

from scripts.reproduce_rset_0002 import (
    reproduce_e1606,
    reproduce_e1607,
    reproduce_e1608,
    reproduce_e1609,
)


class RunSet0002ReproductionTests(unittest.TestCase):
    def test_e1606_score_ledger(self):
        value = reproduce_e1606()
        self.assertEqual(value["rr_rank"], 3)
        self.assertAlmostEqual(value["rr_margin"], -0.030043545034063257)
        self.assertAlmostEqual(value["max_control_rr_margin"], 0.05369590033953564)

    def test_e1607_exact_hypergeometric(self):
        value = reproduce_e1607()
        self.assertEqual(value["overlap"], 4)
        self.assertAlmostEqual(value["hypergeometric_upper_p"], 0.09190809190809192)

    def test_e1608_binomial_null(self):
        value = reproduce_e1608()
        self.assertEqual(value["positionwise_matches"], 0)
        self.assertAlmostEqual(value["binomial_upper_p"], 1.0)

    def test_e1609_eligibility_count(self):
        self.assertEqual(reproduce_e1609(), {"audited_targets": 6, "eligible_targets": 0})


if __name__ == "__main__":
    unittest.main()
