
from dotenv import load_dotenv, find_dotenv
import os
# Load .env
load_dotenv(find_dotenv())

# Launch GUI
from surirobot.core import app

# Launch services
import surirobot.services

# Launch keyboard listener
import surirobot.core.keyboard

# Launch API callers
import surirobot.core.api

# Launch manager
from surirobot.core.manager import manager
if not int(os.environ.get('TEMPORARY_FILES', '0')):
    print('banana')
    app.aboutToQuit.connect(manager.delete_temporary_files)

app.exec_()
