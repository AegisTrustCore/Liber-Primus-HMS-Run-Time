from __future__ import annotations

import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hms_tools.expedition_001 import HINTS, hint_text, instructions_text


class ExpeditionGuidanceChecks(unittest.TestCase):
    def test_beginner_instructions_are_complete(self) -> None:
        instructions = instructions_text()
        self.assertIn("LOGS", instructions)
        self.assertIn("VOCABULARY", instructions)
        self.assertIn("STEPS", instructions)
        self.assertIn("2, 3, 3, 9, and 1", instructions)
        self.assertNotIn("PASS — XPD-0001", instructions)

    def test_progressive_hints_are_available_without_answer(self) -> None:
        self.assertEqual(len(HINTS), 4)
        for level in range(1, 5):
            self.assertTrue(hint_text(level).startswith(f"HINT {level}"))
        with self.assertRaises(ValueError):
            hint_text(0)


if __name__ == "__main__":
    unittest.main()
