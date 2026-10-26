"""Start both local services, and stop both when this launcher exits."""
from pathlib import Path
import signal
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
processes=[]
try:
    processes.append(subprocess.Popen([sys.executable,'-m','uvicorn','backend.app:app','--host','127.0.0.1','--port','8091'],cwd=ROOT))
    processes.append(subprocess.Popen(['npm','run','dev:web','--','--port','4174'],cwd=ROOT))
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
