"""The Dun&Bradstreet API client class"""

from app.clients.base_client import BaseClient
from app.responses import ClientResponse
from app.company_data import CompanyData
from app.auto_logging import AutoLogger

class DNBClient(BaseClient):
    """Client for interacting with D&B API."""  #NOTE: We do not have D&B API access yet
    def __init__(self, token: str) -> None:
        super().__init__()
        self.token = token
        self.logger = AutoLogger("D&BClient")
        self.logger.info("Initializing D&BClient")
        self.authenticate()

    def authenticate(self) -> None:
        """Authenticate the D&B client."""
        if not self.token:
            raise ValueError("D&B API token is required for authentication.")
        # No access yet

    def __call__(self, duns: str) -> CompanyData:
        """Retrieve data from D&B using the DUNS number."""
        #call dnb api
        data = CompanyData()
        return ClientResponse(status_code=200, message="Data retrieved successfully", data=data)
