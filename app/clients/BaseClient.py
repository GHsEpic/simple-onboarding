from abc import ABC, abstractmethod

class BaseClient(ABC):
    """Abstract base class for clients"""
    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Call the client with given arguments."""
        pass

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate the client."""
        pass

    
