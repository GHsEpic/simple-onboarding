"""API class"""

import io
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from app.util import format_duns, validate_duns_format
from app.clients.dnb_client import DNBClient
from app.clients.google_client import GoogleClient
from app.clients.openai_client import OpenAIClient
from app.clients.openregister_client import OpenregisterClient
from app.config import CLIENTS, CREDENTIALS
from app.auto_logging import AutoLogger
from app.responses import APIResponse
from app.company_data import CompanyData

class API:
    """API class to handle FastAPI application and routes."""
    def __init__(self) -> None:
        self.app = FastAPI()
        self.setup_logging()
        self.setup_routes()
        self.enable_cors()
        self.dnb_client, self.google_client, self.openai_client, self.openregister_client = (
            None, None, None, None)
        if CLIENTS.dnb.available:
            self.dnb_client = DNBClient(token=CREDENTIALS.dnb_token)
        if CLIENTS.google.available:
            self.google_client = GoogleClient(token=CREDENTIALS.google_token)
        if CLIENTS.openai.available:
            self.openai_client = OpenAIClient(token=CREDENTIALS.openai_token)  
        if CLIENTS.openregister.available:
            self.openregister_client = OpenregisterClient(token=CREDENTIALS.openregister)

    def run(self) -> None:
        """Run the FastAPI application."""
        self.logger.info("Running API")
        uvicorn.run(self.app, host="127.0.0.1", port=8000)

    def setup_routes(self) -> None:
        """Set up API routes."""

        @self.app.get("/")
        async def health():
            return {"status": "ok"}
        
        self.logger.info("Setting up routes")
        @self.app.get("/dataByDUNS/{DUNS}")
        async def get_data_from_duns(DUNS) -> dict:
            if not CLIENTS.dnb.available:
                return APIResponse(status_code=503, message="Route unavailable", data={}).to_dict()
            success, formatted_duns = format_duns(DUNS)
            if not success:
                return APIResponse(status_code=415, message="Invalid DUNS format", data={}).to_dict()
            valid = validate_duns_format(formatted_duns)
            if not valid:
                return APIResponse(status_code=415, message="Invalid DUNS format", data={}).to_dict()

            response = self.dnb_client(formatted_duns)
            return response.to_dict()
                                                           
        @self.app.post("/dataFromPDF/")
        async def get_data_from_pdf(file: UploadFile = File(...)) -> dict:
            if not CLIENTS.openai.available:
                return APIResponse(status_code=503, message="Route is unavailable", data={}).to_dict()
            if not file.filename.lower().endswith('.pdf'):
                return APIResponse(status_code=415, message="File must be a PDF", data={}).to_dict()
            contents = await file.read()
            file_stream = io.BytesIO(contents)
            response = self.openai_client(file_stream, self.google_client)
            if CLIENTS.openregister.available:
                self.openregister_client.enrich_data(response.data)
            return response.to_dict()

        @self.app.get("/dataByCompanyName/{company_name}")
        async def get_german_company_data(company_name):
            if not CLIENTS.openregister.available:
                return APIResponse(status_code=503, message="Route is unavailable", data={}).to_dict()
            data = CompanyData()
            data.company.name = company_name
            data = self.openregister_client.enrich_data(data)
            return APIResponse(200, "Got the data", data).to_dict()

    def setup_logging(self) -> None:
        """Set up automatic logging middleware."""
        self.logger = AutoLogger("API")

    def enable_cors(self):
        """Enable CORS for the API"""
        self.logger.info("Enabling CORS")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # or ["http://localhost:3000"] for specific origin
            allow_credentials=True,
            allow_methods=["*"],  # ["GET", "POST"] if you want to restrict
            allow_headers=["*"],
        )
