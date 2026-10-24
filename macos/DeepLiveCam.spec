from pathlib import Path
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

root = Path(os.environ['DLC_SOURCE']).resolve()
datas = [(str(root / 'models'), 'models'), (str(root / 'locales'), 'locales'), (str(root / 'LICENSE'), '.')]
for package in ('insightface', 'onnxruntime', 'opennsfw2'):
    datas += collect_data_files(package)
hidden = collect_submodules('insightface') + collect_submodules('onnxruntime')
for path in (root / 'modules').rglob('*.py'):
    hidden.append('.'.join(path.relative_to(root).with_suffix('').parts).removesuffix('.__init__'))
a = Analysis([str(root / 'run.py')], pathex=[str(root)],
    binaries=collect_dynamic_libs('onnxruntime'), datas=datas, hiddenimports=hidden,
    excludes=['tensorflow', 'jax', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebEngineQuick'],
    noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='DeepLiveCam',
    console=True, strip=False, upx=False, target_arch='arm64')
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='DeepLiveCam')
