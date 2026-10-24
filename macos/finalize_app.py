from pathlib import Path
import shutil,subprocess,sys
app=Path(sys.argv[1]).resolve()
for name in ('ffmpeg','ffprobe'):
    shutil.copyfile(Path(sys.argv[2])/name,app/'Contents/MacOS'/name)
    (app/'Contents/MacOS'/name).chmod(0o755)
weights=app/'Contents/Resources/opennsfw2-data'
shutil.copytree(sys.argv[3],weights)
(app/'Contents/Frameworks/opennsfw2-data').symlink_to('../Resources/opennsfw2-data',target_is_directory=True)
subprocess.run(['xattr','-r','-d','com.apple.FinderInfo',str(app)],capture_output=True)
subprocess.run(['codesign','--force','--sign','-',str(app)],check=True)
subprocess.run(['codesign','--verify','--deep','--strict',str(app)],check=True)
