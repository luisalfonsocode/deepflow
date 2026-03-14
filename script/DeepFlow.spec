# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/Users/luis/workspace/deepflow/main.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/luis/workspace/deepflow/styles.qss', '.'), ('/Users/luis/workspace/deepflow/config', 'config')],
    hiddenimports=['yaml', 'cffi', '_cffi_backend'],
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
    [],
    exclude_binaries=True,
    name='DeepFlow',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DeepFlow',
)
app = BUNDLE(
    coll,
    name='DeepFlow.app',
    icon=None,
    bundle_identifier=None,
)
