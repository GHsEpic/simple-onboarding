import os
import io
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build, MediaFileUpload


class GoogleClient:
    """GoogleClient class to handle Google Drive and Docs operations."""
    def __init__(self) -> None:
        self.creds = None                                                                                   
        self.SCOPES = [                                                                            #Google API scopes for Drive and Docs
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/documents.readonly'
        ]
        self.authenticate()                                                                        #Authenticate the client

    def authenticate(self) -> None:
        """Authenticate the Google client using OAuth2 credentials."""
        if os.path.exists('app/credentials/token.json'):                                           #Check if token.json exists for credentials
            self.creds = Credentials.from_authorized_user_file('app/credentials/token.json', self.SCOPES)

        if not self.creds or not self.creds.valid:                                                 #Check if credentials are valid
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())                                                      #Refresh the credentials if expired 
            else:
                flow = InstalledAppFlow.from_client_secrets_file('app/credentials/credentials.json',    #Load client secrets
                                                                  self.SCOPES)   
                self.creds = flow.run_local_server(port=0)                                         #Run the local server for authentication

            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())                                                  #Save the credentials to token.json

    def upload_pdf_to_drive(self, file_path: str) -> str:
        """Upload a PDF file to Google Drive, convert it to a Google Doc and return the document ID."""
        drive_service = build('drive', 'v3', credentials=self.creds)                               #Build the Drive service

        file_metadata = {                                                                          #Metadata for the file to be uploaded
            'name': os.path.basename(file_path),
            'mimeType': 'application/vnd.google-apps.document'                                     #Converts PDF to Google Doc
        }
        media = MediaFileUpload(file_path, mimetype='application/pdf')                             #Media file upload object

        file = drive_service.files().create(                                                       #Create the file in Google Drive
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')                                                                      #Return the file ID of the uploaded document
    
    def extract_text_from_doc(self, doc_id: str) -> str:
        """Extract text from a Google Doc by its ID."""
        docs_service = build('docs', 'v1', credentials=self.creds)                                 #Build the Docs service
        document = docs_service.documents().get(documentId=doc_id).execute()                       #Get the document by ID

        content = document.get('body').get('content')                                              #Extract the content from the document
        text = ''
        for item in content:                                                                       #Iterate through the content items
            if 'paragraph' in item:                                                                #Check if the item is a paragraph
                elements = item['paragraph']['elements']
                for elem in elements:
                    text += elem.get('textRun', {}).get('content', '')                             #Extract the text from the paragraph elements
        return text
    
    def delete_file(self, doc_id: str) -> None:
        drive_service = build('drive', 'v3', credentials=self.creds)                               #Build the Drive service
        drive_service.files().delete(fileId=doc_id).execute()                                      #Delete the document by ID
    
    def extract_text_from_pdf(self, file_path: str | os.PathLike) -> str:                          #All-in-one method to extract text from a PDF file
        """Extract text from a PDF file by uploading it to Google Drive,
          converting it to a Google Doc, and extracting the text."""
        doc_id = self.upload_pdf_to_drive(file_path)
        text = self.extract_text_from_doc(doc_id)
        self.delete_file(doc_id)
        return text



if __name__ == '__main__':
    FILE_PATH = 'app/test_files/Gesellschaftsvertrag.pdf'
    client = GoogleClient()
    print(client.extract_text_from_pdf(FILE_PATH))
