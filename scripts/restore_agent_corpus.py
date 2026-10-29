"""Copy a verified corpus export and expose every document as readable text.

No API sampling, ledger copying, production writes, or fabricated completeness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def restore(source,destination):
    source=Path(source).resolve();destination=Path(destination).resolve()
    if source==destination or source in destination.parents or destination in source.parents:
        raise ValueError('Source and destination must be separate directories')
    current=json.loads((source/'.research-index/CURRENT.json').read_text())
    generation=current['generation']
    if not generation.replace('-','').isalnum():raise ValueError('Invalid generation identity')
    index=source/'.research-index/generations'/generation
    if not index.is_dir() or index.is_symlink():raise ValueError('Missing immutable source generation')
    if any(path.is_symlink() for path in index.rglob('*')):raise ValueError('Source index contains symlinks')
    manifest=json.loads((index/'manifest.json').read_text())
    with sqlite3.connect((index/'library.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Invalid source database')
        documents=[json.loads(row['metadata']) for row in db.execute('SELECT metadata FROM documents ORDER BY id')]
        page_count=db.execute('SELECT count(*) FROM pages').fetchone()[0]
        expected=manifest.get('stats',{}).get('documents')
        if expected is not None and expected!=len(documents):raise ValueError('Source document count differs from manifest')
        for document in documents:
            path=(source/document['raw_path']).resolve()
            if not path.is_relative_to(source/'corpus/raw') or (source/document['raw_path']).is_symlink():raise ValueError('Unsafe original path')
            if digest(path)!=document['sha256']:raise ValueError('Original checksum mismatch: '+document['id'])
        # Verify the complete source before creating a destination marker.
        destination.mkdir(parents=True,exist_ok=True)
        marker=destination/'READY.json'
        if marker.exists():raise ValueError('Destination is already published; choose a fresh directory')
        local_index=destination/'.research-index/generations'/generation
        shutil.copytree(index,local_index,dirs_exist_ok=True)
        text_root=destination/'agent-documents';text_root.mkdir(exist_ok=True)
        catalogue=[]
        for document in documents:
            original=destination/document['raw_path'];original.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source/document['raw_path'],original)
            if digest(original)!=document['sha256']:raise ValueError('Copied original checksum mismatch')
            rows=db.execute('SELECT page,label,text,origin,warning FROM pages WHERE doc_id=? ORDER BY page',(document['id'],)).fetchall()
            text_path=text_root/(document['id']+'.txt')
            with text_path.open('w') as stream:
                stream.write(document.get('title',document['id'])+'\n'+document['url']+'\n')
                for row in rows:
                    stream.write('\n=== Physical page '+str(row['page'])+' / '+row['label']+' ===\n')
                    if row['warning']:stream.write('[Extraction warning: '+row['warning']+']\n')
                    stream.write(row['text']+'\n')
            catalogue.append({**document,'agent_text_path':str(text_path.relative_to(destination)),'pages':len(rows)})
        (destination/'catalogue.jsonl').write_text(''.join(json.dumps(item,ensure_ascii=False)+'\n' for item in catalogue))
        (destination/'.research-index/CURRENT.json').write_text(json.dumps(current))
        report={'generation':generation,'documents':len(documents),'pages':page_count,'originals_verified':len(documents),'all_documents_exported':len(catalogue)==len(documents),'source_database_sha256':digest(index/'library.sqlite'),'copied_database_sha256':digest(local_index/'library.sqlite'),'scope':'Complete selected generation, indexed originals and all extracted page text. No usage ledger, credentials or private reports.'}
        if report['source_database_sha256']!=report['copied_database_sha256']:raise ValueError('Copied index checksum mismatch')
        marker.write_text(json.dumps(report,indent=2)+'\n')
        return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--destination',required=True)
    args=parser.parse_args();print(json.dumps(restore(args.source,args.destination),indent=2))
