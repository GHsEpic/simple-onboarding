from openai import OpenAI
from .BaseClient import BaseClient
import io, json

class OpenAIClient(BaseClient):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate the OpenAI client using the provided API key."""
        if not self.client.api_key:
            raise ValueError("OpenAI API key is required for authentication.")
        # No additional authentication needed for OpenAI client
    
    def upload_file(self, file_stream: io.BytesIO) -> str:
        response = self.client.files.create(
            file=file_stream,
            purpose="user_data"
        )
        return response.id
    
    def cleanup(self, file_id: str, completion_id: str) -> None:
        self.client.files.delete(file_id)
        self.client.completions.delete(completion_id)
    
    def file_to_json_using_gpt(self, file_id: str) -> dict:
        response = self.client.chat.completions.create(
                messages=[
                    {"role": "system",
                        "content": [
                            {"type": "text", "text": "You're a PDF analyst. Extract all information from the PDF file, translate to english if necessary and respond exclusively in JSON. Do NOT give an explanation or any other text."},
                        ]
                    },
                    {"role": "user",
                        "content": [
                            {"type": "file", "file_id": file_id}
                        ]
                    }
                ],
            model="gpt-3.5-turbo",
            temperature=0
        )

        completion_id, json_response = response["id"] , response.choices[0].message.content

        try:
            return completion_id, json.loads(json_response)
        except:
            return ####
    
    def __call__(self, filestream: io.BytesIO) -> dict:
        file_id = self.upload_file(filestream)
        completion_id, data = self.file_to_json_using_gpt(file_id)
        self.cleanup(file_id, completion_id)
        return data
    
if __name__ == "__main__":
    print("Testing OpenAIClient")
    with open("app/credentials/openai.txt", "r") as f:
        api_key = f.read().strip()
    client = OpenAIClient(api_key=api_key)
    with open("app/test_files/pdfs/Gesellschafterliste.pdf", "rb") as f:
        file_stream = io.BytesIO(f.read())
    data = client(file_stream)
    print(data)