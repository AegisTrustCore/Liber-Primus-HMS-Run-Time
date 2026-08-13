from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from hms_tools.gp29 import GP29InputError, PRIMES, RUNES, calculate, parse_tokens, self_test
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

    def test_continuous_latin_is_rejected_as_ambiguous(self):
        with self.assertRaises(GP29InputError):
            parse_tokens("FUTH")

    def test_result_digest_is_deterministic(self):
        self.assertEqual(calculate("F U TH"), calculate("F U TH"))

    def test_self_test(self):
        result = self_test()
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["passed"], 3)


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
