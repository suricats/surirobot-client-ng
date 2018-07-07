
from dotenv import load_dotenv, find_dotenv

# Load .env
load_dotenv(find_dotenv())

# Launch GUI
from surirobot.core import app

from surirobot.core.manager import manager
app.aboutToQuit.connect(manager.delete_temporary_files)
app.exec_()
# Launch Flask
# from surirobot.management import app
# app.run(debug=True)
