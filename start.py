
from dotenv import load_dotenv, find_dotenv
import signal
import sys
import shared as s

# Load .env
load_dotenv(find_dotenv())

# Init thread
s.init()


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        s.stop()
        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

# Init from DB
from surirobot.services.facerecognition.loader import load_faces
load_faces()

# Launch GUI
from surirobot.core import app
app.exec_()

# Launch Flask
#from surirobot.management import app
#app.run(debug=False)
