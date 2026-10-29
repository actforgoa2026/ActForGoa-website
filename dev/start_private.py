"""Run the private editable workspace using its previously configured gateway."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
STATE=Path('/workspace/.research-private/connection.json')
if not STATE.is_file():
    raise SystemExit('Configure the private sandbox gateway first; no public preview is started automatically.')
state=json.loads(STATE.read_text())
processes=[]
try:
    env={**os.environ,'RESEARCH_API_ORIGIN':'http://127.0.0.1:8093','DEV_RELAY_MODE':'1'}
    processes.append(subprocess.Popen([sys.executable,'-m','uvicorn','backend.dev_app:app','--host','127.0.0.1','--port','8093','--reload','--reload-dir','backend'],cwd=ROOT,env=env))
    processes.append(subprocess.Popen(['npm','run','dev:web','--','--port','4176'],cwd=ROOT,env=env))
    processes.append(subprocess.Popen([sys.executable,'dev/relay_worker.py'],cwd=ROOT,env=env))
    print('Private live workspace running. Use its invitation link, not a localhost or public preview URL.',flush=True)
    while all(process.poll() is None for process in processes):time.sleep(.5)
except KeyboardInterrupt:
    pass
finally:
    for process in processes:
        if process.poll() is None:process.send_signal(signal.SIGINT)
    for process in processes:
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.terminate()
