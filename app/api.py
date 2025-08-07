from fastapi import FastAPI, HTTPException, Request
from util import format_duns, validate_duns_format, AutoLogger
from dnb_client import DNBClient
from google_client import GoogleClient

class API:
    """API class to handle FastAPI application and routes."""
    def __init__(self) -> None:
        self.app = FastAPI()                                                                       #Initialize FastAPI application
        #self.logger = AutoLogger(__name__)                                                         #Set up automatic logging
        #self.app.add_middleware(AutoLogger)                                                        #Add middleware for automatic logging
        self.setup_routes()                                                                        #Set up API routes
        self.dnb_client = DNBClient(token="Sadly we do not yet have a token for D&B API access")      #Initialize D&B client with token
        self.google_client = GoogleClient()                                                        #Initialize Google client for Drive and Docs operations

    def run(self) -> None:
        """Run the FastAPI application."""
        import uvicorn                                                                             #Import Uvicorn for running the FastAPI app
        uvicorn.run(self.app, host="127.0.0.1", port=8000)                                         #Run the app on localhost:8000
    
    def setup_routes(self) -> None:
        """Set up API routes."""
        @self.app.get("/")                                                                         #Define the root route
        async def read_root(request: Request) -> dict:
            return {"message": "Welcome to the API"}

        @self.app.get("/duns/{DUNS}")                                                              #Define route for DUNS number retrieval
        async def duns_route(DUNS) -> dict:
            success, formatted_duns = format_duns(DUNS)                                            #Format the DUNS number
            if not success:                                                                        #Check if formatting was successful
                raise HTTPException(status_code=400, detail="DUNS must follow format XX-XXX-XXXX")
                return {"DUNS must follow format": "XX-XXX-XXXX"}
            valid = validate_duns_format(formatted_duns)                                           #Validate the DUNS number's format
            if not valid:                                                                          #Check if the DUNS number's format is valid
                raise HTTPException(status_code=400, detail="DUNS must follow format XX-XXX-XXXX")
                return {"DUNS must follow format": "XX-XXX-XXXX"}
            
            data = self.dnb_client.retrieve_data(formatted_duns)                                   #Retrieve data from D&B client using the formatted DUNS number
            return data