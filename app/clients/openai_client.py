from openai import OpenAI, RateLimitError
from .BaseClient import BaseClient
import io, json
from util import extract_text_from_pdf
from response import APIResponse
from config import OPENAI_JSON_SCHEMA


class OpenAIClient(BaseClient):
    def __init__(self, token: str):
        self.client = OpenAI(api_key=token)
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate the OpenAI client using the provided API key."""
        # No additional authentication needed for OpenAI client
    
    def extract_and_format(self, file_text: str) -> dict:
        """Process the PDF text with OpenAI's GPT model."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are a data analyst. Extract all wanted information from the text, translate to English if necessary, and respond exclusively in JSON. Fill any unknown field with '?'."},
                    {"role": "user", "content": file_text}
                ],
                response_format=OPENAI_JSON_SCHEMA
            )
            return True, json.loads(response.choices[0].message.content)
        except RateLimitError as e:
            return False, APIResponse(status_code=429, message="Rate limit exceeded")
        except Exception as e:
            return False, APIResponse(status_code=500, message=str(e))
        
    
    def __call__(self, filestream: io.BytesIO, google_client) -> dict:
        file_text = extract_text_from_pdf(filestream, google_client)
        if not file_text:
            return APIResponse(status_code=400, message="Failed to extract text from PDF")
        
        success, response = self.extract_and_format(file_text)

        if not success:
            return response

        if not response["success"]:
            return response

        return APIResponse(status_code=200, message="Data processed successfully", data=response["data"])