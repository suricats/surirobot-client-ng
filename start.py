
from dotenv import load_dotenv, find_dotenv
import os
# Load .env
load_dotenv(find_dotenv())

# Launch GUI
from surirobot.core import app
import surirobot.services
import surirobot.core.keyboard

import surirobot.core.api
from surirobot.core.manager import manager
if not int(os.environ.get('TEMPORARY_FILES', '0')):
    print('banana')
    app.aboutToQuit.connect(manager.delete_temporary_files)
app.exec_()
# Launch Flask
# from surirobot.management import app
# app.run(debug=True)
