import os
from dotenv import load_dotenv
import uvicorn

if __name__ == '__main__':
    os.umask(0o077)
    load_dotenv('.env.local',override=False)
    uvicorn.run('satellite.app:create_app',factory=True,host='0.0.0.0',port=int(os.getenv('PORT','8092')),access_log=False,workers=1)
