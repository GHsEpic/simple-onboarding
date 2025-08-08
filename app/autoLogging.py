from fastapi import Request
from logging import getLogger

class AutoLogger:
    """Middleware for automatic logging of requests and responses."""
    def __init__(self, app, name: str) -> None:
        self.app = app
        self.logger = getLogger(name)

        @self.app.middleware("https")
        @self.app.middleware("http")
        async def log_request(request: Request, call_next):
            self.logger.info(f"Request: {request.method} {request.url}")
            response = await call_next(request)
            self.logger.info(f"Response: {response.status_code}")
            return response