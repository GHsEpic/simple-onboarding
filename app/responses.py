"""Response types for clients and API"""

from app.company_data import CompanyData

class ClientResponse:
    """Base class for Client responses."""

    def __init__(self, status_code: int = 400, message: str = "NOT OK", data: CompanyData | dict = None):
        self.status_code = status_code
        self.message = message
        self.data = data if data else CompanyData()

    def to_APIResponse(self):
        """Turn the ClientResponse into an APIResponse."""
        return APIResponse(self.status_code, self.message, self.data)


class APIResponse:
    """Base class for API responses."""
    def __init__(self, status_code: int, message: str, data: CompanyData = None):
        self.status_code = status_code
        self.message = message
        self.data = data if data else CompanyData()


    def to_dict(self) -> dict:
        """Convert the response to a dictionary.""" # Conversion needed for serialization
        return {
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data.to_dict()
        }
