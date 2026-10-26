"""Build explicit service/data allowlists; never package env files or unrelated corpus content."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tarfile

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--data-root',type=Path,default=ROOT);p.add_argument('--output',type=Path,default=ROOT/'.research-release');p.add_argument('--stage-data',action='store_true',help='Stage a directory for volume upload instead of a compressed archive; use APFS clones on macOS.');args=p.parse_args()
source=args.data_root.resolve();output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
service=output/'service';service.mkdir(exist_ok=True)
for name in ['backend','public/models/all-MiniLM-L6-v2']:
    shutil.copytree(ROOT/name,service/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
for name in ['Dockerfile','railway.json','requirements-runtime.txt']:shutil.copy2(ROOT/'deploy/research'/name,service/name)
(service/'.dockerignore').write_text('.env*\n__pycache__/\n')
generation=json.loads((source/'.research-index/CURRENT.json').read_text())['generation']
if not generation.replace('-','').isalnum():raise ValueError('Invalid generation')
gen=source/'.research-index/generations'/generation
with sqlite3.connect(f'file:{gen/"library.sqlite"}?mode=ro',uri=True) as db:
    docs=[json.loads(row[0]) for row in db.execute('SELECT metadata FROM documents')]
raw={}
for doc in docs:
    path=(source/doc['raw_path']).resolve()
    if not path.is_relative_to(source/'corpus/raw') or (source/doc['raw_path']).is_symlink():raise ValueError('Invalid original path')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=doc['sha256']:raise ValueError('Original checksum mismatch')
    raw[doc['raw_path']]=path
if any(path.is_symlink() for path in gen.rglob('*')):raise ValueError('Index cannot contain symlinks')
files={'.research-index/CURRENT.json':source/'.research-index/CURRENT.json',**raw}
files.update({str(path.relative_to(source)):path for path in gen.rglob('*') if path.is_file()})
directories=sorted(str(path.relative_to(source)) for path in gen.rglob('*') if path.is_dir())
entries=[]
for name,path in sorted(files.items()):
    with path.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
    entries.append({'path':name,'bytes':path.stat().st_size,'sha256':digest})
if args.stage_data:
    stage=output/'data';stage.mkdir(exist_ok=True)
    # Empty Zvec segments are required by its manifest and must survive packaging.
    for name in directories:(stage/name).mkdir(parents=True,exist_ok=True)
    for name,path in files.items():
        destination=stage/name;destination.parent.mkdir(parents=True,exist_ok=True)
        if sys.platform=='darwin':subprocess.run(['cp','-c',str(path),str(destination)],check=True)
        else:shutil.copy2(path,destination)
    artifact={'directory':str(stage)}
else:
    archive=output/(generation+'.tar.gz')
    with tarfile.open(archive,'w:gz',compresslevel=3) as tar:
        for name in directories:tar.add(source/name,arcname='research/'+name,recursive=False)
        for name,path in files.items():tar.add(path,arcname='research/'+name)
    with archive.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
    artifact={'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest}
manifest=json.dumps(entries,sort_keys=True,separators=(',',':'))
(output/'files.json').write_text(manifest+'\n')
report={'generation':generation,'documents':len(docs),'originals':len(raw),**artifact,'files_manifest_sha256':hashlib.sha256((manifest+'\n').encode()).hexdigest(),'directories':directories,'service':str(service),'scope':'Only indexed original files, current immutable index, code and bundled model. No keys or private report/CRM data.'}
(output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
