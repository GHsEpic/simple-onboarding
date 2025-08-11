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
        available = True
        message = "No tokens"



class CREDENTIALS:
    dnb_token, google_credentials, google_token, openai_token = None, None, None, None
    
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
            #CLIENTS.google.available = False
            CLIENTS.google.message = _
    
    if CLIENTS.openai.available:
        success, _ = load_key("credentials/openai_token.txt")
        if success:
            openai_token = _
        else:
            CLIENTS.openai.available = False
            CLIENTS.openai.message = _


OPENAI_JSON_SCHEMA = {
                "type": "json_schema",  # Changed back to json_schema
                "json_schema": {  # Added json_schema key
                    "name": "test",
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,  # Added this line
                        "properties": {
                            "success": {
                                "type": "boolean"
                            },
                            "data": {
                                "type": "object",
                                "additionalProperties": False,  # Added this line
                                "properties": {
                                    "company_name": {"type": "string"},
                                    "founding_date": {"type": "string"},
                                    "shareholders": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "additionalProperties": False,  # Added this line
                                            "properties": {
                                                "name": {"type": "string"},
                                                "shares": {"type": "string"},
                                                "date_of_birth": {"type": "string"},
                                                "phone": {"type": "string"}
                                            },
                                            "required": ["name", "shares", "date_of_birth", "phone"]
                                    }
                                }
                            },
                            "required": ["company_name", "founding_date", "shareholders"]
                        }
                    },
                    "required": ["success", "data"]
                    }
                }
            }