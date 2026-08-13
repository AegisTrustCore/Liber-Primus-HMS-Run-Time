import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "gp29.py"
SPEC = importlib.util.spec_from_file_location("gp29", MODULE_PATH)
gp29 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = gp29
SPEC.loader.exec_module(gp29)


class GP29Tests(unittest.TestCase):
    def test_boundary_values(self):
        self.assertEqual((gp29.lookup_token("F").index, gp29.lookup_token("F").prime), (0, 2))
        self.assertEqual((gp29.lookup_token("EA").index, gp29.lookup_token("EA").prime), (28, 109))

    def test_aliases_resolve_to_same_entry(self):
        self.assertIs(gp29.lookup_token("K"), gp29.lookup_token("C"))
        self.assertIs(gp29.lookup_token("ING"), gp29.lookup_token("NG"))
        self.assertIs(gp29.lookup_token("IA"), gp29.lookup_token("IO"))

    def test_token_and_rune_sums_match(self):
        token_sum = gp29.result(gp29.parse_token_arguments(["F", "U", "TH"]))["gp_sum"]
        rune_sum = gp29.result(gp29.parse_runes("ᚠᚢᚦ"))["gp_sum"]
        self.assertEqual(token_sum, 10)
        self.assertEqual(rune_sum, token_sum)

    def test_full_table_sum(self):
        self.assertEqual(gp29.result(list(gp29.ENTRIES))["gp_sum"], 1480)

    def test_unknown_token_is_rejected(self):
        with self.assertRaises(ValueError):
            gp29.lookup_token("Q")


if __name__ == "__main__":
    unittest.main()
