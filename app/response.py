class APIResponse:
    """Base class for API/Client responses."""
    
    def __init__(self, status_code: int, message: str, data: dict = None) -> None:
        self.status_code = status_code
        self.message = message
        self.data = data if data is not None else {}
    
    def to_dict(self) -> dict:
        """Convert the response to a dictionary.""" # Converts the response to a dictionary to be serialized
        return {
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data
        }