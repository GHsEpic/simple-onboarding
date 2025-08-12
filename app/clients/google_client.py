import os, io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload
from app.clients.BaseClient import BaseClient
from app.response import APIResponse


class GoogleClient(BaseClient):
    """GoogleClient class to handle Google Drive and Docs operations."""
    def __init__(self, token=None, credentials=None) -> None:
        self.token = token
        self.credentials = credentials                                                                                   
        self.SCOPES = [                                             # Google API scopes for Drive and Docs
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents.readonly'
        ]
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate the Google client using OAuth2 credentials."""
        if self.token:
            self.credentials = Credentials.from_authorized_user_info(self.token, self.SCOPES) # Create credentials from token

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request()) # Refresh the credentials if expired 
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials/google_secret.json", scopes=self.SCOPES)
                self.credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent") # Open the browser on an authentication prompt, offline and consent are required for getting a refresh_token

            with open("credentials/google_token.json", 'w') as token:
                token.write(self.credentials.to_json()) # Save the credentials

    def upload_pdf(self, file_path: str) -> str:
        """Upload a PDF file to Google Drive, convert it to a Google Doc and return the document ID."""
        drive_service = build('drive', 'v3', credentials=self.credentials) # Build the Drive service

        file_metadata = {                           # Metadata for the file to be uploaded
            'name': os.path.basename(file_path),
            'mimeType': 'application/vnd.google-apps.document' # Converts PDF to Google Doc
        }
        media = MediaFileUpload(file_path, mimetype='application/pdf') # Media file upload object

        file = drive_service.files().create(    # Create the file in Google Drive
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id') # Return the file ID of the uploaded document
    
    def upload_pdf_stream(self, file_stream: io.BytesIO) -> str:
        """Upload a PDF file stream to Google Drive, convert it to a Google Doc and return the document ID."""
        drive_service = build('drive', 'v3', credentials=self.credentials) # Build the Drive service

        file_metadata = {            # Metadata for the file to be uploaded
            'name': 'Uploaded PDF',
            'mimeType': 'application/vnd.google-apps.document' # Converts PDF to Google Doc
        }
        media = MediaIoBaseUpload(file_stream, mimetype='application/pdf') # Media file upload object

        file = drive_service.files().create( # Create the file in Google Drive
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id') # Return the file ID of the uploaded document
    
    def delete_file(self, doc_id: str) -> None:
        drive_service = build('drive', 'v3', credentials=self.credentials) # Build the Drive service
        drive_service.files().delete(fileId=doc_id).execute() # Delete the document by ID

    def extract_text_from_doc(self, doc_id: str) -> str:
        """Extract text from a Google Doc by its document ID."""
        docs_service = build('docs', 'v1', credentials=self.credentials) # Build the Docs service
        doc = docs_service.documents().get(documentId=doc_id).execute() # Get the document by ID

        text = ''
        for content in doc.get('body').get('content'):
            if 'paragraph' in content:
                elements = content['paragraph'].get('elements')
                for element in elements:
                    if 'textRun' in element:
                        text += element['textRun'].get('content', '')

        return text
    
    def extract_text_from_pdf(self, file_path: str | os.PathLike) -> str: # All-in-one method to extract text from a PDF file
        """Extract text from a PDF file by uploading it to Google Drive,
          converting it to a Google Doc, and extracting the text."""
        try:
            doc_id = self.upload_pdf(file_path)
            text = self.extract_text_from_doc(doc_id)
            self.delete_file(doc_id)
        except:
            return APIResponse(status_code=400, message="Something went wrong", data={})
        return APIResponse(status_code=200, message="Extracted text from PDF", data={"text":text})
    
    def __call__(self, file_stream: io.BytesIO) -> str:
        """Extract text from a PDF file stream."""
        try:
            doc_id = self.upload_pdf_stream(file_stream)
            text = self.extract_text_from_doc(doc_id)
            self.delete_file(doc_id)
        except:
            return APIResponse(status_code=400, message="Something went wrong", data={})
        #Format text since OCR may return text looking like "Stutt g a rt" or "Stutt o art" instead of "Stuttgart"
        #Somehow extract relevant information from the text
        return APIResponse(status_code=200, message="Extracted text from PDF", data={"text": text})