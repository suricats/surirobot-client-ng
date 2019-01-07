import os
from .exceptions import URLNotDefinedAPIException
from .emotional import EmotionalAPICaller

from .converse import ConverseApiCaller
converse_url = os.environ.get('API_CONVERSE_URL')
if converse_url:
    api_converse = ConverseApiCaller(converse_url)
    api_converse.start()
else:
    raise URLNotDefinedAPIException('Converse')

from .emotional import EmotionalAPICaller
vocal_url = os.environ.get('BEYONDVERBAL_API_URL')
if vocal_url:
    api_vocal = EmotionalAPICaller(vocal_url)
    api_vocal.start()
else:
    raise URLNotDefinedAPIException('VOCAL')

from .tts import TtsApiCaller
tts_url = os.environ.get('API_CONVERSE_URL')
if tts_url:
    api_tts = TtsApiCaller(tts_url)
    api_tts.start()
else:
    raise URLNotDefinedAPIException('TTS')

from .stt import SttApiCaller
stt_url = os.environ.get('API_CONVERSE_URL')
if stt_url:
    api_stt = SttApiCaller(stt_url)
    api_stt.start()
else:
    raise URLNotDefinedAPIException('STT')

from .nlp import NlpApiCaller
nlp_url = os.environ.get('API_CONVERSE_URL')
if nlp_url:
    api_nlp = NlpApiCaller(nlp_url)
    api_nlp.start()
else:
    raise URLNotDefinedAPIException('NLP')

from .memory import MemoryApiCaller
memory_url = os.environ.get('API_MEMORY_URL')
if memory_url:
    api_memory = MemoryApiCaller(memory_url)
    api_memory.start()
