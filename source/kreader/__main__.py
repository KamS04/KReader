import os
from .ui import constants
import asyncio

CURR_DIR = os.path.dirname( os.path.abspath(__file__) )
CONFIG_FILE_PATH = os.path.join(CURR_DIR, 'kprefs.json')

os.environ[constants.CONFIG_KEY] = CONFIG_FILE_PATH
os.environ[constants.DEBUG_KEY] = str(True)

def main():
    from .ui import app
    asyncio.run(app.main())

if __name__ == '__main__':
    main()
