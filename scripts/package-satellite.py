"""Stage only committed satellite runtime files; never include local env or results."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args()
def git(*parts):
    return subprocess.check_output(['git', *parts], cwd=root, text=True).strip()
if git('status','--porcelain','--untracked-files=all'):
    raise SystemExit('Commit and verify source before packaging.')
target = Path(args.output).resolve()
if target.exists():
    raise SystemExit('Choose a new output directory.')
paths = [p for p in git('ls-files','satellite').splitlines() if p.endswith(('.py','.geojson','.md')) or p.endswith('EVE-LICENSE')]
files = [(p,p) for p in paths] + [(f'deploy/satellite/{"Dockerfile.railway" if p == "Dockerfile" else p}',p) for p in ('Dockerfile','requirements.txt','railway.json')]
manifest = []
for source,destination in files:
    data = (root/source).read_bytes()
    path = target/'service'/destination
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    manifest.append({'path':destination,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
(target/'manifest.json').write_text(json.dumps({'commit':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),'files':manifest},indent=2)+'\n')
print(f'Staged {len(files)} allowlisted files at {target}/service')
