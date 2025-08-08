from util import load_key
from logging import getLogger

configLogger = getLogger("config")


DEBUG = True
configLogger.debug("Loading configuration...")

class CLIENTS:
    class dnb:
        available = False
        message = "Not yet implemented"
    class google:
        available = True
        message = "Accessible"
    class openai:
        available = False
        message = "No tokens"



class CREDENTIALS:
    if CLIENTS.dnb.available:
        success, _ = load_key("credentials/dnb_token.txt")
    
        if success:
            dnb_token = _
        else:
            CLIENTS.dnb.available = False
            CLIENTS.dnb.message = _

    if CLIENTS.google.available:
        success, _ = load_key("credentials/google_credentials.json")
        if success:
            google_credentials = _
        else:
            CLIENTS.google.available = False
            CLIENTS.google.message = _
    
        success, _ = load_key("credentials/google_token.json")
        if success:
            google_token = _
        else:
            CLIENTS.google.available = False
            CLIENTS.google.message = _
    
    if CLIENTS.openai.available:
        success, _ = load_key("credentials/openai_token.txt")
        if success:
            openai_token = _
        else:
            CLIENTS.openai.available = False
            CLIENTS.openai.message = _