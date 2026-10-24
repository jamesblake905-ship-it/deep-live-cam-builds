"""Add a Finder launcher to a portable, locally built application folder."""
from pathlib import Path
import plistlib
import sys

folder = Path(sys.argv[1]).resolve()
app = folder / 'Deep Live Cam.app'
macos = app / 'Contents/MacOS'
macos.mkdir(parents=True, exist_ok=True)
resources = app / 'Contents/Resources'
resources.mkdir(parents=True, exist_ok=True)
info = {
    'CFBundleName': 'Deep Live Cam',
    'CFBundleDisplayName': 'Deep Live Cam',
    'CFBundleIdentifier': 'local.jamesblake.deeplivecam',
    'CFBundleExecutable': 'launch',
    'CFBundlePackageType': 'APPL',
    'CFBundleShortVersionString': '2026.10.24',
    'CFBundleVersion': '20261024',
    'NSCameraUsageDescription': 'Deep Live Cam uses the camera for a local live face-swap preview when you click Live.',
    'NSHighResolutionCapable': True,
    'CFBundleIconFile': 'AppIcon',
}
(app / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
script = '''#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
mkdir -p Logs
export PATH="$ROOT/runtime:$PATH"
export KERAS_BACKEND=torch
export KERAS_HOME="$ROOT/State/keras"
export OPENNSFW2_HOME="$ROOT/State/opennsfw2"
exec "$ROOT/runtime/DeepLiveCam" --execution-provider coreml --det-size 320 --execution-threads 4 "$@" >> "$ROOT/Logs/application.log" 2>&1
'''
(macos / 'launch').write_text(script)
(macos / 'launch').chmod(0o755)
(folder / 'Start Deep Live Cam.command').write_text('''#!/bin/bash
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/Deep Live Cam.app/Contents/MacOS/launch" "$@"
''')
(folder / 'Start Deep Live Cam.command').chmod(0o755)
print(app)
