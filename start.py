
from dotenv import load_dotenv, find_dotenv
import shared as s

# Load .env
load_dotenv(find_dotenv())

# Load global variables
s.init()

# Start FaceRecognition
#from surirobot.recognition_engine.recognition import FaceRecognition
#thread_reco = FaceRecognition()
#thread_reco.start()

# Init from DB
#from surirobot.management.faceloader.loader import load_faces
#load_faces()

# Launch GUI
from surirobot.core import app
app.exec_()

# Launch Flask
#from surirobot.management import app
#app.run(debug=False)
