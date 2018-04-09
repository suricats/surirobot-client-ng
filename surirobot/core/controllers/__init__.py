from surirobot.core import ui
from surirobot.services import serv_fr

# Start ConverseManager
from surirobot.core.controllers.conversemanager import ConverseManager
man_conv = ConverseManager()
#man_conv.setAudioPeriod(4)
man_conv.startAll()

# Start GeneralManager
from surirobot.core.controllers.generalmanager import GeneralManager
man_gen = GeneralManager()
man_gen.configureHandlers()
#man_gen.connectToUI(ui)

# Start FaceManager
serv_fr.person_changed.connect(ui.setTextMiddle)
### manager_face = FaceManager()
