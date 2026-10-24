"""Prepare the pinned upstream checkout and verify bundled model downloads."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
manifest = json.loads(Path(__file__).with_name('models.json').read_text())

def download(item):
    name = item['path']
    if name.startswith('buffalo_l/'):
        destination = root / 'models/insightface/models/buffalo_l' / Path(name).name
    else:
        destination = root / 'models' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    def valid(path):
        return path.exists() and path.stat().st_size == item['size'] and hashlib.file_digest(path.open('rb'), 'sha256').hexdigest() == item['sha256']
    if not valid(destination):
        part = destination.with_suffix('.download')
        subprocess.run(['curl', '-fL', '--retry', '3', '--silent', '--show-error', '-o', str(part), 'https://huggingface.co/hacksider/deep-live-cam/resolve/main/' + name], check=True)
        if not valid(part):
            raise RuntimeError('Model checksum mismatch: ' + name)
        part.replace(destination)
    print('Verified', name, flush=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(download, manifest))

# Keep the face-analysis pack with the application, avoiding hidden home writes.
p = root / 'modules/model_downloader.py'
s = p.read_text().replace('os.path.join(os.path.expanduser("~"), ".insightface", "models", name)', 'os.path.join(MODELS_DIR, "insightface", "models", name)')
p.write_text(s)
p = root / 'modules/face_analyser.py'
s = p.read_text()
if "root=os.path.join(os.path.dirname(os.path.dirname(__file__))" not in s:
    s = s.replace("name='buffalo_l',", "name='buffalo_l',\n                    root=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'insightface'),")
p.write_text(s)
p = root / 'modules/core.py'
p.write_text(p.read_text().replace('        quit()', '        sys.exit()'))
