# Fonte de build: executar na raiz com python -m PyInstaller FilaME.spec.
# Credenciais e .env nunca entram no bundle.
from PyInstaller.utils.hooks import collect_all
from pathlib import Path

binary_datas, binary_binaries, binary_hidden = collect_all('psycopg_binary')
a = Analysis(
    ['src/fila_me/app.py'], pathex=[SPECPATH],
    binaries=binary_binaries, datas=binary_datas + [(str(Path(SPECPATH) / "src/fila_me/ui/assets/icones"), "src/fila_me/ui/assets/icones")],
    hiddenimports=binary_hidden, hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='FilaME', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=False, console=False)
