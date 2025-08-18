from logging import getLogger, Formatter, StreamHandler
from os import getenv

DEBUG = bool(getenv("DEBUG")) #Do NOT import DEBUG from config (circular import)

# ANSI escape codes for colors
COLORS = {
    'DEBUG': '\033[94m',   # Blue
    'INFO': '\033[92m',    # Green
    'WARNING': '\033[93m', # Yellow
    'ERROR': '\033[91m',   # Red
    'CRITICAL': '\033[95m' # Magenta
}
RESET = '\033[0m'

class ColorFormatter(Formatter):    # Class for formatting for using colors in logging
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        message = super().format(record)
        return f"{log_color}{message}{RESET}"
    
class AutoLogger:
    """Middleware for automatic logging of requests and responses."""
    def __init__(self, name: str) -> None:
        self.logger = getLogger(name)
        self.logger.setLevel("DEBUG")

        console_handler = StreamHandler()
        console_handler.setLevel("DEBUG")
        console_handler.setFormatter(ColorFormatter('%(levelname)s: %(message)s'))
        self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)
    
    def warn(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log a debug message"""
        if DEBUG:
            self.logger.debug(message)