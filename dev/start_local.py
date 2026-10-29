"""Private localhost research UI with Vite HMR and Uvicorn reload. No deployment."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]
STATE=Path(os.getenv('ACTFORGOA_DEV_STATE',str(Path.home()/'.local/share/actforgoa-research-dev')))
STATE.mkdir(mode=0o700,parents=True,exist_ok=True)
credentials=Path(os.getenv('ACTFORGOA_CREDENTIAL_FILE',str(Path.home()/'code/ActForGoa/.env.local')))
key=dotenv_values(credentials).get('ANTHROPIC_API_KEY') if credentials.is_file() else None
common={**os.environ,'ACTFORGOA_DEV_STATE':str(STATE),'ACTFORGOA_CRM_STATE':str(STATE/'crm')}
# The frontend never inherits provider keys or other loaded credential variables.
frontend={k:v for k,v in common.items() if not any(s in k for s in ('ANTHROPIC','API_KEY','AUTH_TOKEN','SECRET'))}
frontend.update(RESEARCH_API_ORIGIN='http://127.0.0.1:8093',VITE_LOCAL_AGENT='1')
backend={**common,**({'ANTHROPIC_API_KEY':key} if key else {})}
processes=[]
try:
    processes.append(subprocess.Popen([sys.executable,'-m','uvicorn','backend.local_agent_app:app','--host','127.0.0.1','--port','8093','--reload','--reload-dir','backend','--no-access-log'],cwd=ROOT,env=backend))
    processes.append(subprocess.Popen(['npm','run','dev:web','--','--port','4276'],cwd=ROOT,env=frontend))
    print('Local workspace: http://127.0.0.1:4276/ask | Corpus/CRM read-only. Paid calls require reconciled dev accounting.',flush=True)
    while all(p.poll() is None for p in processes):time.sleep(.5)
except KeyboardInterrupt:pass
finally:
    for p in processes:
        if p.poll() is None:p.send_signal(signal.SIGINT)
    for p in processes:
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.terminate()
