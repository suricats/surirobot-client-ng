
from dotenv import load_dotenv, find_dotenv
import shared as s

# Load .env
load_dotenv(find_dotenv())

# Load global variables
s.init()

# Start FaceRecognition
from recognition_engine.recognition import FaceRecognition
thread_reco = FaceRecognition()
thread_reco.start()

# Init from DB
#from management.faceloader.loader import load_faces
#load_faces()

# Launch GUI
from gui.ui import Gui
gui = Gui()
gui.start()

# Launch Flask
from management import app
app.run(debug=False)
