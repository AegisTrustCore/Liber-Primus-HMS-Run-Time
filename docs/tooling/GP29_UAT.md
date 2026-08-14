# GP29 v0.1.0 ordinary-user acceptance

The tester receives only the candidate ZIP and the instructions inside it. The test must run on a clean Windows 10/11 x64 environment without Python or developer tools.

## Acceptance run

1. Download the candidate package.
2. Verify its published SHA-256 value.
3. Extract it to a path containing spaces.
4. Find and read `START-HERE.txt`.
5. Launch `HMS-GP29.exe` without assistance.
6. Enter the documented Latin test.
7. Confirm the expected Latin result.
8. Enter the documented rune test.
9. Confirm the expected rune result.
10. Enter the documented explicit-token test.
11. Confirm the expected token result.
12. Load a UTF-8 text file.
13. Calculate the loaded input successfully.
14. Export JSON.
15. Locate and open the exported JSON.
16. Identify the `L`, `R`, `prime`, `N`, and `Q` fields and aggregate values.
17. Run the desktop self-test.
18. Exit and relaunch without corruption.
19. Run `HMS-GP29-CLI.exe self-test`.
20. Run the documented CLI calculation and UTF-8-file example.
21. Disconnect networking and repeat a calculation.
22. Confirm no account, telemetry, or network access is requested.
23. Explain what the result does and does not claim.
24. Report every confusing instruction, label, warning, or workflow.

Acceptance requires all steps to pass and `tester_help_required` to be `false`.

## Evidence template

```json
{
  "schema": "HMS_GP29_UAT_V1",
  "test_id": "UAT-GP29-0001",
  "instrument": "GP29",
  "candidate": "0.1.0",
  "os": "",
  "architecture": "x64",
  "fresh_machine": true,
  "python_installed": false,
  "developer_tools_installed": false,
  "steps_total": 24,
  "steps_passed": 0,
  "steps_failed": 0,
  "tester_help_required": null,
  "artifact_sha256": "",
  "network_required": false,
  "telemetry_observed": false,
  "notes": []
}
```

If any candidate file changes after this record is produced, the record is invalid and the next RC must repeat the complete test.
