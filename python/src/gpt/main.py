import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../../../connector-secrets.txt')

import uvicorn
from gpt.server.server import app

SERVER_PORT = os.environ.get('SERVER_PORT', '9999')

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(SERVER_PORT))
