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
        counts={'documents':len(documents),'pages':page_count,'chunks':db.execute('SELECT count(*) FROM chunks').fetchone()[0]}
        for key,count in counts.items():
            if manifest.get('stats',{}).get(key)!=count:raise ValueError('Source '+key+' count differs from manifest')
        if manifest.get('scope')!='full_corpus':raise ValueError('Not a full corpus manifest')
        if db.execute('SELECT count(*) FROM pages p LEFT JOIN documents d ON d.id=p.doc_id WHERE d.id IS NULL').fetchone()[0]:raise ValueError('Orphaned pages')
        inventory={str(p.relative_to(source)):digest(p) for p in index.rglob('*') if p.is_file()}
        for document in documents:
            path=(source/document['raw_path']).resolve()
            if not path.is_relative_to(source/'corpus/raw') or (source/document['raw_path']).is_symlink():raise ValueError('Unsafe original path')
            if digest(path)!=document['sha256']:raise ValueError('Original checksum mismatch: '+document['id'])
            inventory[document['raw_path']]=document['sha256']
        # Verify the complete source before creating a destination marker.
        if destination.exists():raise ValueError('Destination must be new; never overwrite a preserved copy')
        destination.mkdir(parents=True)
        marker=destination/'READY.json'
        if marker.exists():raise ValueError('Destination is already published; choose a fresh directory')
        local_index=destination/'.research-index/generations'/generation
        shutil.copytree(index,local_index,dirs_exist_ok=True)
        text_root=destination/'agent-documents';text_root.mkdir(exist_ok=True)
        catalogue=[]
        metadata_root=destination/'metadata';metadata_root.mkdir()
        search=sqlite3.connect(destination/'agent-search.sqlite')
        search.execute('CREATE VIRTUAL TABLE page_search USING fts5(doc_id UNINDEXED,page UNINDEXED,title,text, tokenize="unicode61")')
        for document in documents:
            original=destination/document['raw_path'];original.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source/document['raw_path'],original)
            if digest(original)!=document['sha256']:raise ValueError('Copied original checksum mismatch')
            rows=db.execute('SELECT page,label,text,origin,warning FROM pages WHERE doc_id=? ORDER BY page',(document['id'],)).fetchall()
            if len(rows)!=document['page_count']:raise ValueError('Document page count mismatch: '+document['id'])
            (metadata_root/(document['id']+'.json')).write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n')
            search.executemany('INSERT INTO page_search VALUES(?,?,?,?)',[(document['id'],r['page'],document.get('title',''),r['text']) for r in rows])
            text_path=text_root/(document['id']+'.txt')
            with text_path.open('w') as stream:
                stream.write(document.get('title',document['id'])+'\n'+document['url']+'\n')
                for row in rows:
                    stream.write('\n=== Physical page '+str(row['page'])+' / '+row['label']+' ===\n')
                    if row['warning']:stream.write('[Extraction warning: '+row['warning']+']\n')
                    stream.write(row['text']+'\n')
            catalogue.append({**document,'agent_text_path':str(text_path.relative_to(destination)),'pages':len(rows)})
        search.commit();search.close()
        (destination/'catalogue.jsonl').write_text(''.join(json.dumps(item,ensure_ascii=False)+'\n' for item in catalogue))
        (destination/'.research-index/CURRENT.json').write_text(json.dumps(current))
        report={'generation':generation,'documents':len(documents),'pages':page_count,'originals_verified':len(documents),'all_documents_exported':len(catalogue)==len(documents),'source_database_sha256':digest(index/'library.sqlite'),'copied_database_sha256':digest(local_index/'library.sqlite'),'scope':'Complete selected generation, indexed originals and all extracted page text. No usage ledger, credentials or private reports.'}
        if report['source_database_sha256']!=report['copied_database_sha256']:raise ValueError('Copied index checksum mismatch')
        for relative,sha in inventory.items():
            if digest(source/relative)!=sha or digest(destination/relative)!=sha:raise ValueError('Source changed or copy mismatch: '+relative)
        report.update(manifest_stats=manifest['stats'],index_files_verified=sum(k.startswith('.research-index/') for k in inventory),source_root=str(source),warnings_preserved=True,all_pages_searchable=True)
        (destination/'SOURCE-SHA256.json').write_text(json.dumps(inventory,indent=2)+'\n')
        marker.write_text(json.dumps(report,indent=2)+'\n')
        for path in destination.rglob('*'):
            if path.is_file():path.chmod(0o444)
        for path in sorted(destination.rglob('*'),reverse=True):
            if path.is_dir():path.chmod(0o555)
        destination.chmod(0o555)
        return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);parser.add_argument('--destination',required=True)
    args=parser.parse_args();print(json.dumps(restore(args.source,args.destination),indent=2))
