# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['AssoGestion.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('IHM', 'IHM'),
        ('modele', 'modele'),
        ('utils', 'utils'),
        ('config_assogestion.ini', '.'),
        ('*.png', '.'),
        ('version.txt', '.')
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtPrintSupport',
        'PyQt5.QtSql',
        'PyQt5.uic'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AssoGestion',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo_abo_tech.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AssoGestion'
)
