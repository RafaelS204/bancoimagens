# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_customtkinter.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('indexador.py', '.'), ('embeddings', 'embeddings'), ('logs', 'logs'), ('modelos.py', '.'), ('C:\\Users\\sergi\\Documents\\QSYNC_MAIN\\Projetos_Dev\\ProjetosPython\\BancoImagens\\venv\\Lib\\site-packages\\open_clip', 'open_clip')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='BancoDeImagens',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\icons\\icon_main.png'],
)
