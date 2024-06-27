# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['deepfinder/commands/exodeepfinder.py'],
    pathex=[],
    binaries=[],
    datas=[('examples/analyze/in/net_weights_FINAL.h5', '.')],
    hiddenimports=['scipy._lib.array_api_compat.numpy.fft','scipy.special._special_ufuncs'],
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
    [('u', None, 'OPTION')],
    exclude_binaries=True,
    name='exodeepfinder',
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
    name='exodeepfinder',
)
app = BUNDLE(
    coll,
    name='exodeepfinder.app',
    icon=None,
    bundle_identifier=None,
)
