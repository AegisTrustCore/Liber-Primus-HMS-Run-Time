from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from hms_tools.gp29 import GP29InputError, PRIMES, RUNES, calculate, format_human, parse_latin, parse_letters, parse_tokens, self_test
from hms_tools.runtime import RuntimeStore, create_job, execute_job


ROOT = Path(__file__).resolve().parents[1]


class GP29Tests(unittest.TestCase):
    def test_full_rune_row_uses_first_29_primes(self):
        result = calculate(RUNES, "runes")
        self.assertEqual(result["rune_count"], 29)
        self.assertEqual(result["gp_sum"], sum(PRIMES))

    def test_alias_tokens_are_explicit(self):
        result = calculate("F V TH K J IA Z ING", "tokens")
        self.assertEqual(result["normalized_tokens"], ["F", "U/V", "TH", "C/K", "I/J", "IO/IA", "S/Z", "NG/ING"])

    def test_token_mode_rejects_unseparated_tokens(self):
        with self.assertRaises(GP29InputError):
            parse_tokens("FUTH")

    def test_continuous_latin_uses_frozen_longest_alias(self):
        self.assertEqual([entry.sound for entry in parse_latin("THING")], ["TH", "NG/ING"])
        self.assertEqual(calculate("CICADA", "latin")["normalized_tokens"], ["C/K", "I/J", "C/K", "A", "D", "A"])

    def test_english_letters_do_not_merge_sound_clusters(self):
        self.assertEqual([entry.sound for entry in parse_letters("THING")], ["T", "H", "I/J", "N", "G"])
        self.assertEqual(calculate("H", "letters")["normalized_tokens"], ["H"])
        self.assertEqual(calculate("TH", "letters")["normalized_tokens"], ["T", "H"])
        self.assertEqual(calculate("TH", "latin")["normalized_tokens"], ["TH"])

    def test_english_letters_reject_non_letters(self):
        with self.assertRaises(GP29InputError):
            parse_letters("H2")

    def test_lr_prime_nq_registers(self):
        result = calculate("F U/V TH", "tokens")
        self.assertEqual(
            [(entry["L"], entry["R"], entry["prime"], entry["N"], entry["Q"]) for entry in result["entries"]],
            [(0, 0, 2, 2, 0), (1, 28, 3, 3, 0), (2, 27, 5, 5, 0)],
        )
        self.assertEqual(result["prime_sum"], 10)
        self.assertEqual(result["gp_sum"], result["prime_sum"])

    def test_result_digest_is_deterministic(self):
        self.assertEqual(calculate("F U TH"), calculate("F U TH"))

    def test_human_output_explains_registers_and_scope(self):
        rendered = format_human(calculate("CICADA", "latin"))
        self.assertIn("Prime / GP sum: 340", rendered)
        self.assertIn("PER-RUNE VALUES", rendered)
        self.assertIn("not a Liber Primus decode", rendered)

    def test_self_test(self):
        result = self_test()
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["passed"], 5)


class RuntimeTests(unittest.TestCase):
    def test_job_identity_is_deterministic(self):
        self.assertEqual(create_job("F U TH"), create_job("F U TH"))

    def test_tampered_job_is_rejected(self):
        job = create_job("F")
        job["input"]["text"] = "U"
        with self.assertRaises(ValueError):
            execute_job(job)

    def test_runtime_store_executes_gp29(self):
        store = RuntimeStore()
        job = create_job("F U TH")
        job_id = store.submit(job)
        result = store.run(job_id)
        self.assertEqual(result["output"]["gp_sum"], 10)
        self.assertEqual(store.get_result(job_id), result)

    def test_cli_self_test(self):
        completed = subprocess.run(
            [sys.executable, "scripts/hms_runtime.py", "self-test"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["failed"], 0)


if __name__ == "__main__":
    unittest.main()
