
from dotenv import load_dotenv, find_dotenv
import os
import logging
# Load .env
load_dotenv(find_dotenv())
# Logging configuration
if int(os.environ.get('DEBUG', '0')):
    print('DEBUG MODE : on')
    logging.basicConfig(level=logging.DEBUG)
else:
    print('DEBUG MODE : off')
    logging.basicConfig(level=logging.INFO)
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
    app.aboutToQuit.connect(manager.delete_temporary_files)

app.exec_()
