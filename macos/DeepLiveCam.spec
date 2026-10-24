from pathlib import Path
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules, copy_metadata
from importlib.metadata import distributions

root = Path(os.environ['DLC_SOURCE']).resolve()
datas = [(str(root / 'models'), 'models'), (str(root / 'locales'), 'locales'), (str(root / 'LICENSE'), '.')]
for package in ('insightface', 'onnxruntime', 'opennsfw2'):
    datas += collect_data_files(package)
# Runtime version queries (notably gdown) need distribution metadata too.
for distribution in distributions():
    datas += copy_metadata(distribution.metadata['Name'])
hidden = collect_submodules('insightface') + collect_submodules('onnxruntime')
for path in (root / 'modules').rglob('*.py'):
    hidden.append('.'.join(path.relative_to(root).with_suffix('').parts).removesuffix('.__init__'))
a = Analysis([str(root / 'run.py')], pathex=[str(root)],
    binaries=collect_dynamic_libs('onnxruntime'), datas=datas, hiddenimports=hidden,
    excludes=['tensorflow', 'jax', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineQuick'],
    noarchive=False)
# Python's relocated build configuration contains the build user's home path.
# It is not used for extension compilation in this frozen application.
import sys, importlib
from PyInstaller.config import CONF
name = '_sysconfigdata__darwin_darwin'
module = importlib.import_module(name)
sanitized = Path(workpath) / 'portable-sysconfig.py'
sanitized.write_text(Path(module.__file__).read_text().replace(sys.base_prefix, '/opt/deeplivecam/python'))
a.pure = [(n, str(sanitized) if n == name else p, t) for n, p, t in a.pure]
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='DeepLiveCam',
    console=True, strip=False, upx=False, target_arch='arm64')
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='DeepLiveCam')
app = BUNDLE(coll, name='Deep Live Cam.app', icon='AppIcon.icns', bundle_identifier='org.deeplivecam.portable', info_plist={'CFBundleShortVersionString':'2026.10.24','CFBundleVersion':'20261024','LSMinimumSystemVersion':'14.4','NSCameraUsageDescription':'Deep Live Cam uses the camera for a local preview when you click Live.','NSHighResolutionCapable':True})
