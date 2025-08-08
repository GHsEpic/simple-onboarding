from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from util import format_duns, validate_duns_format
from clients.dnb_client import DNBClient
from clients.google_client import GoogleClient
from clients.openai_client import OpenAIClient
import io
from config import *
from autoLogging import AutoLogger

class API:
    """API class to handle FastAPI application and routes."""
    def __init__(self) -> None:
        self.app = FastAPI()                                                                       #Initialize FastAPI application
        self.setup_logging()                                                                    #Set up automatic logging middleware
        self.setup_routes()
        if CLIENTS.dnb.available:                                                                        #Set up API routes
            self.dnb_client = DNBClient(api_key=CREDENTIALS.dnb_token) #Initialize D&B client with token
        if CLIENTS.google.available:                                                               #Check if Google client is available
            self.google_client = GoogleClient(token=CREDENTIALS.google_token, credentials=CREDENTIALS.google_credentials)                                                        #Initialize Google client for Drive and Docs operations
        if CLIENTS.openai.available:                                                               #Check if OpenAI client is available
            self.openai_client = OpenAIClient(api_key=CREDENTIALS.openai_token)                                              #Initialize OpenAI client (not yet implemented)

    def run(self) -> None:
        """Run the FastAPI application."""
        import uvicorn                                                                             #Import Uvicorn for running the FastAPI app
        uvicorn.run(self.app, host="127.0.0.1", port=8000)                                         #Run the app on localhost:8000
    
    def setup_routes(self) -> None:
        """Set up API routes."""
        @self.app.get("/")                                                                         #Define the root route
        async def read_root(request: Request) -> dict:
            return {"message": "Welcome to the API"}

        @self.app.get("/dataByDUNS/{DUNS}")                                                        #Define route for DUNS number retrieval
        async def duns_route(DUNS) -> dict:
            if not CLIENTS.dnb.available:                                                          #Check if D&B client is available
                return {"error": "D&B client is currently unavailable."}
            success, formatted_duns = format_duns(DUNS)                                            #Format the DUNS number
            if not success:                                                                        #Check if formatting was successful
                return {"DUNS must follow format": "XX-XXX-XXXX"}
            valid = validate_duns_format(formatted_duns)                                           #Validate the DUNS number's format
            if not valid:                                                                          #Check if the DUNS number's format is valid
                return {"DUNS must follow format": "XX-XXX-XXXX"}
            
            data = self.dnb_client(formatted_duns)                                                 #Retrieve data from D&B client using the formatted DUNS number
            return data
                                                                          
        @self.app.post("/dataFromPDF/")
        async def readPDF_route(file: UploadFile = File(...)) -> dict:
            if not CLIENTS.openai.available:                                                      #Check if Google client is available
                return {"error": "PDF processing is currently unavailable."}
            if not file.filename.endswith('.pdf'):
                return {"error": "File must be a PDF"}
            contents = await file.read()
            file_stream = io.BytesIO(contents)
            data = self.openai_client(file_stream)
            return {"data": data}
    
    def setup_logging(self) -> None:
        """Set up automatic logging middleware."""
        self.logger = AutoLogger(self.app, __name__)