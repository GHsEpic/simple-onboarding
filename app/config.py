"""All config variables for the API"""

import os
import json
import dotenv
from app.auto_logging import AutoLogger

dotenv.load_dotenv()

configLogger = AutoLogger("config")

DEBUG = bool(os.getenv("DEBUG"))

configLogger.info("Loading configuration")

class CLIENTS:  # Set client accesibility and message
    """Holds the availability of the clients"""
    class dnb:
        """DNBClients availability"""
        available = False
        message = "Not yet implemented"
    class google:
        """Google clients availability"""
        available = True
        message = "Accessible"
    class openai:
        """OpenAI clients availability"""
        available = True
        message = "Accessible"
    class openregister:
        """Openregister clients availability"""
        available = True
        message = "Accessible"

configLogger.info(f"""D&B available: {CLIENTS.dnb.available}
                      Message: {CLIENTS.dnb.message}""")
configLogger.info(f"""Google available: {CLIENTS.google.available}
                      Message: {CLIENTS.google.message}""")
configLogger.info(f"""OpenAI available: {CLIENTS.openai.available}
                      Message: {CLIENTS.openai.message}""")
configLogger.info(f"""OpenRegister available: {CLIENTS.openregister.available}
                      Message: {CLIENTS.openregister.message}""")

class CREDENTIALS: # Load credentials if available
    """Class to hold the client credentials"""
    dnb_token, google_credentials, google_token, openai_token, openregister = (
        None, None, None, None, None
    )

    if CLIENTS.dnb.available:
        dnb_token = os.getenv("DNB_TOKEN")

    if CLIENTS.google.available:
        google_credentials = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        google_token = json.loads(os.getenv("GOOGLE_TOKEN"))

    if CLIENTS.openai.available:
        openai_token = os.getenv("OPENAI_TOKEN")

    if CLIENTS.openregister.available:
        openregister = os.getenv("OPENREGISTER_TOKEN")

try:    # Load the response format for ChatGPT
    with open("app/openai_response_format.json", mode="r", encoding="utf-8") as f:
        OPENAI_RESPONSE_FORMAT = json.loads(f.read())
    configLogger.info("Succesfully loaded ChatGPT response format")
except ExceptionGroup("", [FileNotFoundError, json.JSONDecodeError]):
    #with open("openai_response_format.json", "w") as f:
    #    f.write("{}")
    configLogger.warn("Couldn't load ChatGPT response format, did not create placeholder")
    OPENAI_RESPONSE_FORMAT = {}
