# GP29 Calculator

Status: **RELEASE CANDIDATE**

Version: `0.1.0-rc.1`

Access: Observer / public

This is the first executable HMS Endeavour Lite component. It provides a strict, inspectable Gematria Primus lookup and summation engine for the 29-symbol ordering used by the project.

It does not decode Liber Primus, choose a cipher, infer word boundaries, or claim that a numerical coincidence is meaningful.

## Use

```bash
python tools/gp29/gp29.py table
python tools/gp29/gp29.py lookup ING
python tools/gp29/gp29.py sum F U TH
python tools/gp29/gp29.py runes "ᚠᚢᚦ"
python tools/gp29/gp29.py --json sum F U TH
```

Latin input is token-based to avoid silently choosing between multi-character symbols such as `TH`, `ING`, `EO`, `IA`, and `EA`. Separate tokens with spaces or commas. Rune input is read one Unicode rune at a time; whitespace is ignored.

## Test

```bash
python -m unittest discover -s tools/gp29/tests -v
```

The calculator uses only the Python standard library.
