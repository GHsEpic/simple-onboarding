import io, json
from openai import OpenAI, RateLimitError
from app.clients.BaseClient import BaseClient
from util import extract_text_from_pdf
from app.responses import ClientResponse, APIResponse
from company_data import CompanyData
from config import OPENAI_RESPONSE_FORMAT
from autoLogging import AutoLogger


class OpenAIClient(BaseClient):
    def __init__(self, token: str):
        self.client = OpenAI(api_key=token)
        self.JSON_SCHEMA = OPENAI_RESPONSE_FORMAT
        self.logger = AutoLogger("OpenAIClient")
        self.logger.info("Initializing OpenAI client")
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate the OpenAI client using the provided API key."""
        # No additional authentication needed for OpenAI client
    
    def extract_and_format(self, file_text: str) -> APIResponse:
        """Process the PDF text with OpenAI's GPT model."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1", # response_format* does not work on gpt-3.5, gpt-3.5-turb0, etc. (even though the docs say so)
                messages=[ # System message as instructions, user message as text to extract data from
                    {"role": "system", "content": "You are a data analyst. Extract all wanted information from the text, translate to English if necessary, and respond exclusively in JSON. Fill any unknown field with ''."},
                    {"role": "user", "content": file_text}
                ],
                response_format=self.JSON_SCHEMA #<- *
            )
            return True, json.loads(response.choices[0].message.content)    # Return success & response pairs
        except RateLimitError as e:
            return False, ClientResponse(status_code=429, message="Rate limit exceeded").to_APIResponse()
        except Exception as e:
            return False, ClientResponse(status_code=400, message=str(e)).to_APIResponse()
        
    
    def __call__(self, filestream: io.BytesIO, google_client) -> APIResponse:
        file_text = extract_text_from_pdf(filestream, google_client)
        if not file_text:
            return ClientResponse(status_code=400, message="Failed to extract text from PDF").to_APIResponse() # May be raised if google client is unavailable and a scanned PDF is passed
        
        success, response = self.extract_and_format(file_text) # Call ChatGPT

        if not success:
            return response # Return the error-APIResponse (something went wrong on our side)

        if not response["success"]: # ChatGPT says it couldn't find anything
            return response

        return ClientResponse(status_code=200, message="Data processed successfully", data=CompanyData.from_chatgpt(response["data"])).to_APIResponse()