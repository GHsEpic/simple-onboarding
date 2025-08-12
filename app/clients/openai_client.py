from openai import OpenAI, RateLimitError
from .BaseClient import BaseClient
import io, json
from util import extract_text_from_pdf
from response import APIResponse


class OpenAIClient(BaseClient):
    def __init__(self, token: str):
        self.client = OpenAI(api_key=token)
        with open("openai_response_format.json", "r") as f: # Get the JSON response schema for ChatGPT
            self.JSON_SCHEMA = json.loads(f.read())
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate the OpenAI client using the provided API key."""
        # No additional authentication needed for OpenAI client
    
    def extract_and_format(self, file_text: str) -> dict:
        """Process the PDF text with OpenAI's GPT model."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1", # response_format does not work on gpt-3.5, gpt-3.5-turb0, etc. (even though the docs say so)
                messages=[ # System message as instructions, user message as text to extract data from
                    {"role": "system", "content": "You are a data analyst. Extract all wanted information from the text, translate to English if necessary, and respond exclusively in JSON. Fill any unknown field with '?'."},
                    {"role": "user", "content": file_text}
                ],
                response_format=self.JSON_SCHEMA
            )
            return True, json.loads(response.choices[0].message.content)
        except RateLimitError as e:
            return False, APIResponse(status_code=429, message="Rate limit exceeded")
        except Exception as e:
            return False, APIResponse(status_code=400, message=str(e))
        
    
    def __call__(self, filestream: io.BytesIO, google_client) -> dict:
        file_text = extract_text_from_pdf(filestream, google_client)
        if not file_text:
            return APIResponse(status_code=400, message="Failed to extract text from PDF") # May be raised if google client is unavailable and a scanned PDF is passed
        
        success, response = self.extract_and_format(file_text) # Call ChatGPT

        if not success:
            return response # Return the error-APIResponse (something went wrong on our side)

        if not response["success"]: # ChatGPT says it couldn't find anything
            return response

        return APIResponse(status_code=200, message="Data processed successfully", data=response["data"])