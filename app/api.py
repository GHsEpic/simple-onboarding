from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from util import format_duns, validate_duns_format
from clients.dnb_client import DNBClient
from clients.google_client import GoogleClient
from clients.openai_client import OpenAIClient
import io
from config import *
from autoLogging import AutoLogger
from response import APIResponse

class API:
    """API class to handle FastAPI application and routes."""
    def __init__(self) -> None:
        self.app = FastAPI()
        self.setup_logging()
        self.setup_routes()
        self.dnb_client, self.google_client, self.openai_client = None, None, None
        if CLIENTS.dnb.available: self.dnb_client = DNBClient(token=CREDENTIALS.dnb_token)
        if CLIENTS.google.available: self.google_client = GoogleClient(token=CREDENTIALS.google_token)
        if CLIENTS.openai.available: self.openai_client = OpenAIClient(token=CREDENTIALS.openai_token)  

    def run(self) -> None:
        """Run the FastAPI application."""
        print(CLIENTS.google.available, CLIENTS.google.message)
        import uvicorn
        uvicorn.run(self.app, host="127.0.0.1", port=8000)
    
    def setup_routes(self) -> None:
        """Set up API routes."""
        @self.app.get("/dataByDUNS/{DUNS}")
        async def get_data_from_duns(DUNS) -> dict:
            if not CLIENTS.dnb.available:
                return APIResponse(status_code=503, message="Route unavailable", data={}).to_dict()
            success, formatted_duns = format_duns(DUNS)
            if not success:
                return APIResponse(status_code=400, message="Invalid DUNS format", data={}).to_dict()
            valid = validate_duns_format(formatted_duns)
            if not valid:
                return APIResponse(status_code=400, message="Invalid DUNS format", data={}).to_dict()
            
            response = self.dnb_client(formatted_duns)
            return response.to_dict()
                                                                          
        @self.app.post("/dataFromPDF/")
        async def get_data_from_pdf(file: UploadFile = File(...)) -> dict:
            if not file.filename.endswith('.pdf'):
                return APIResponse(status_code=400, message="File must be a PDF", data={}).to_dict()
            contents = await file.read()
            file_stream = io.BytesIO(contents)
            response = self.openai_client(file_stream, self.google_client)
            return response.to_dict()
    
    def setup_logging(self) -> None:
        """Set up automatic logging middleware."""
        self.logger = AutoLogger(self.app, __name__)