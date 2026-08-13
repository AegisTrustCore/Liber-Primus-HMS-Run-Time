# PyInstaller specification for the Windows portable Expedition verifier.

from pathlib import Path

root = Path.cwd()

a = Analysis(
    [str(root / "scripts" / "verify_challenge_gui.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(root / "challenges" / "manifest.json"), "challenges")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="HMS-XPD-0001-Verifier-v0.2.0-Windows-x64",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
