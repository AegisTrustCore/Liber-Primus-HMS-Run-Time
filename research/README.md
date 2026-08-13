# HMS Endeavour Research Archive

Structured objects—not prose alone—are the public research record.

[**EXPLORE RESULTS**](results/README.md) · [Browse runs](runs/README.md) · [Research capsules](capsules/README.md) · [Curated run sets](runsets/README.md) · [Searchable offline archive](index.html)

## Current computed inventory

| Category | Count |
|---|---:|
| Hash-inventoried source artifacts | 1,322 |
| Published Runs | 8 |
| Published Results | 8 |
| Published Capsules | 3 |
| Published Run Sets | 2 |
| Staged Run Sets | 1 |

**1,322 source artifacts does not mean 1,322 results.** It is the audited file count in the supplied Personal Research tree.

## Object hierarchy

```text
RAW EXECUTION → RUN-#### → RES-#### → CAP-#### → RSET-####
```

- A **Run** records what was executed.
- A **Result** records what one or more runs support.
- A **Capsule** groups a coherent investigation.
- A **Run Set** is a curated distribution unit.

`manifest.json` is authoritative inside each package. HTML, text, Markdown, CSV, indexes, checksums, and ZIP files are generated with `python scripts/build_research_archive.py`.

Legacy flat objects under `records/` are retained as historical release snapshots. New consumers should use the package indexes above.
