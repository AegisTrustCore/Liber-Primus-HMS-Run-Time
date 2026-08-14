# Corpus Verifier synthetic demo

This demo contains invented text only. It lets anyone exercise every required verifier outcome without downloading or redistributing Liber Primus source images.

Use `manifest.json` with each folder in strict mode:

| Case | Expected result | Expected detail |
|---|---|---|
| `cases/GOOD` | PASS | 2 verified |
| `cases/ALTERED` | FAIL | 1 verified, 1 mismatch |
| `cases/MISSING` | FAIL | 1 verified, 1 missing |
| `cases/EXTRA` | FAIL | 2 verified, 1 unexpected |

The fifth case is a malicious manifest rather than a folder:

| Case | Expected result |
|---|---|
| `traversal-manifest.json` | Rejected before filesystem verification because `../outside.txt` is unsafe |

From the repository root:

```text
python scripts/corpus_manifest.py verify demo/corpus-verifier/manifest.json demo/corpus-verifier/cases/GOOD --strict
python scripts/corpus_manifest.py demo-self-test
```

These controls prove the verifier's behavior. They do not establish the authenticity or correctness of any historical corpus.
