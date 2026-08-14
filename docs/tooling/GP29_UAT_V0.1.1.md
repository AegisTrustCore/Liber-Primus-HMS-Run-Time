# GP29 v0.1.1 ordinary-user acceptance

Use this only with the exact v0.1.1 candidate named in its release manifest. Record every failure or confusing step; do not approve a rebuilt or substituted ZIP under the same result.

## Start and orientation

1. Extract the ZIP into a new folder on a Windows 10/11 x64 machine.
2. Verify the ZIP checksum against the official candidate record.
3. Verify every extracted file against `SHA256SUMS`.
4. Read `START-HERE.txt` and launch `HMS-GP29.exe` without assistance.
5. Confirm the calculator, input, result area, mode explanation, and Gematria Primus alphabet are readable without resizing the window.
6. Confirm the alphabet contains 29 selectable rows with rune, sound, prime, L, R, N, and Q columns.

## English H regression

7. Leave **English letters (A-Z)** selected, enter `H`, and calculate.
8. Confirm one H token appears with rune count 1 and prime / GP sum 23.
9. Enter `TH` in English-letter mode and calculate.
10. Confirm the tokens are `T H`, rune count is 2, and prime / GP sum is 82.
11. Select **Latin sounds (longest match)**, enter `TH`, and calculate.
12. Confirm the token is `TH`, rune count is 1, and prime / GP sum is 5.

## Selectable alphabet

13. Clear the input, select the H row, and choose **Insert sound token**.
14. Confirm the app selects explicit-token mode and inserts `H`.
15. Select the TH row and insert its sound token; confirm the input becomes `H TH`.
16. Calculate and confirm the tokens remain exactly `H TH`.
17. Clear the input, select the H row, and choose **Insert rune**.
18. Confirm the app selects rune mode, inserts the H rune, and calculates it as prime / GP sum 23.
19. Enter ordinary English text, then attempt an incompatible alphabet insertion. Confirm the app asks before clearing the existing input and that **No** preserves it.

## Package and export

20. Export a calculation to JSON and confirm the chosen file opens as readable UTF-8 JSON.
21. Run the desktop **Self-test** and confirm 5 passed, 0 failed.
22. Run `HMS-GP29-CLI.exe self-test` and confirm 5 passed, 0 failed.
23. Run `HMS-GP29-CLI.exe gp29 H --mode letters` and confirm prime / GP sum 23.
24. Confirm no account, network connection, Python installation, or telemetry permission was requested.

## Acceptance record

Record the candidate filename, ZIP SHA-256, operating system, display scaling, tester, date, every failed or confusing step, and the final decision: `APPROVE`, `REJECT`, or `APPROVE WITH RECORDED LIMITATION`.
