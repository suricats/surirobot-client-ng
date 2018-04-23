import os

from surirobot.core.api.converse import ConverseApiCaller
api_converse = ConverseApiCaller(
    os.environ.get('API_CONVERSE_URL')
)
api_converse.start()

from surirobot.core.api.tts import TtsApiCaller
api_tts = TtsApiCaller(
    os.environ.get('API_TTS_URL')
)
api_tts.start()

from surirobot.core.api.stt import SttApiCaller
api_stt = SttApiCaller(
    os.environ.get('API_STT_URL')
)
api_stt.start()

from surirobot.core.api.nlp import NlpApiCaller
api_nlp = NlpApiCaller(
    os.environ.get('API_NLP_URL')
)
api_nlp.start()
