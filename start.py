
from dotenv import load_dotenv, find_dotenv
import os
import logging
# Load .env
load_dotenv(find_dotenv())
# Logging configuration
from surirobot.core.common import Dir
import time

if int(os.environ.get('DEBUG', '0')):
    print('DEBUG MODE : on')
    if int(os.environ.get('LOG', '0')):
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(name)-12.12s][%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()
        rootLogger.setLevel(level=logging.DEBUG)
        filename = '{}{}.txt'.format(Dir.LOG, time.strftime("%Y_%m_%d_%H_%M_%S"))
        fileHandler = logging.FileHandler(filename)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)
    else:
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(name)-12.12s][%(levelname)-5.5s]  %(message)s")
        rootLogger = logging.getLogger()
        rootLogger.setLevel(level=logging.DEBUG)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)


else:
    print('DEBUG MODE : off')
    logging.basicConfig(level=logging.INFO)

# Launch GUI
from surirobot.core import app

# Launch device services
import surirobot.devices
# Launch API callers
import surirobot.core.api

# Launch services
import surirobot.services

# Launch keyboard listener




# Launch manager
from surirobot.core.manager import manager
if not int(os.environ.get('TEMPORARY_FILES', '0')):
    app.aboutToQuit.connect(manager.delete_temporary_files)

app.exec_()
