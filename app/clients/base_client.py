"""CLient base class"""

from abc import ABC, abstractmethod

class BaseClient(ABC):
    """Abstract base class for clients"""
    def __init__(self):
        return

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """Call the client with given arguments."""
        return

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate the client."""
        return
