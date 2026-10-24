"""Add a Finder launcher to a portable, locally built application folder."""
from pathlib import Path
import plistlib
import shutil
import sys
import subprocess

folder = Path(sys.argv[1]).resolve()
app = folder / 'Deep Live Cam.app'
macos = app / 'Contents/MacOS'
macos.mkdir(parents=True, exist_ok=True)
resources = app / 'Contents/Resources'
resources.mkdir(parents=True, exist_ok=True)
icon = Path(__file__).with_name('AppIcon.icns')
if icon.exists():
    shutil.copy2(icon, resources / 'AppIcon.icns')
info = {
    'CFBundleName': 'Deep Live Cam',
    'CFBundleDisplayName': 'Deep Live Cam',
    'CFBundleIdentifier': 'local.jamesblake.deeplivecam',
    'CFBundleExecutable': 'DeepLiveCam',
    'CFBundlePackageType': 'APPL',
    'CFBundleShortVersionString': '2026.10.24',
    'CFBundleVersion': '20261024',
    'NSCameraUsageDescription': 'Deep Live Cam uses the camera for a local live face-swap preview when you click Live.',
    'NSHighResolutionCapable': True,
    'CFBundleIconFile': 'AppIcon',
}
(app / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
# A native main executable gives macOS a real application bundle and camera
# usage description. Share the adjacent runtime data without duplicating it.
staged_executable = macos / 'DeepLiveCam.new'
shutil.copy2(folder / 'runtime/DeepLiveCam', staged_executable)
staged_executable.replace(macos / 'DeepLiveCam')
internal = macos / '_internal'
if not internal.exists():
    internal.symlink_to('../../../runtime/_internal', target_is_directory=True)
frameworks = app / 'Contents/Frameworks'
if not frameworks.exists():
    frameworks.symlink_to('../../runtime/_internal', target_is_directory=True)
(folder / 'Start Deep Live Cam.command').write_text('''#!/bin/bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/Deep Live Cam.app/Contents/MacOS/DeepLiveCam" "$@"
''')
(folder / 'Start Deep Live Cam.command').chmod(0o755)
# Strip only Finder metadata from this generated bundle before ad-hoc signing.
if subprocess.run(['xattr', '-p', 'com.apple.FinderInfo', str(app)], capture_output=True).returncode == 0:
    subprocess.run(['xattr', '-d', 'com.apple.FinderInfo', str(app)], check=True)
subprocess.run(['codesign', '--force', '--sign', '-', str(app)], check=True)
subprocess.run(['codesign', '--verify', '--verbose=2', str(app)], check=True)
print(app)
