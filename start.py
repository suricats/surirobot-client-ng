
from dotenv import load_dotenv, find_dotenv
import sys

# Load .env
load_dotenv(find_dotenv())

# Launch GUI
from surirobot.core import app
import surirobot.services
import surirobot.core.keyboard
#import surirobot.core.controllers
import surirobot.core.api
import surirobot.core.scenario
app.exec_()

# Launch Flask
# from surirobot.management import app
# app.run(debug=True)
