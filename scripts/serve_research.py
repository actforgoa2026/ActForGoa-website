"""Start both local services, and stop both when this launcher exits."""
from pathlib import Path
import argparse
import os
import signal
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Research development with live frontend reload; no production build.')
parser.add_argument('--live-api', action='store_true', help='Use the existing answer API and its existing usage ledger; backend prompt changes are not applied.')
args=parser.parse_args()
processes=[]
try:
    env=os.environ.copy()
    if args.live_api:
        env['RESEARCH_API_ORIGIN']='http://127.0.0.1:8092'
        processes.append(subprocess.Popen([sys.executable,'-m','uvicorn','scripts.dev_research_proxy:app','--host','127.0.0.1','--port','8092'],cwd=ROOT,env=env))
        print('Development UI + current live answer engine. Existing production quota applies; local backend prompt edits are not active.',flush=True)
    else:
        data_root=Path(env.get('RESEARCH_DATA_ROOT',ROOT))
        if not (data_root/'.research-index/CURRENT.json').is_file():
            raise SystemExit('Full research index is absent. Set RESEARCH_DATA_ROOT to the corpus checkout, or use --live-api to test the current answer engine.')
        processes.append(subprocess.Popen([sys.executable,'-m','uvicorn','backend.app:app','--host','127.0.0.1','--port','8091','--reload','--reload-dir','backend'],cwd=ROOT,env=env))
    processes.append(subprocess.Popen(['npm','run','dev:web','--','--port','4174'],cwd=ROOT,env=env))
    print('ActForGoa research: http://127.0.0.1:4174/ask',flush=True)
    while all(p.poll() is None for p in processes):time.sleep(.5)
except KeyboardInterrupt:
    pass
finally:
    for process in processes:
        if process.poll() is None:process.send_signal(signal.SIGINT)
    for process in processes:
        try:process.wait(timeout=8)
        except subprocess.TimeoutExpired:process.terminate()
