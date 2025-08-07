from fastapi import Request
from logging import getLogger

class AutoLogger:
    """Middleware for automatic logging of requests and responses."""
    def __init__(self, name: str) -> None:
        self.logger = getLogger(name)

    def __call__(self, content) -> None:
        """Log the content of the request or response."""
        if isinstance(content, Request):
            self.logger.info(f"Request: {content.method} {content.url}")
        elif isinstance(content, str):
            self.logger.info(content)
        else:
            self.logger.info(f"Log: {content}")
    

def format_duns(duns) -> tuple[bool, str]:
    """Format DUNS number to XX-XXX-XXXX format if possible."""
    if isinstance(duns, int):                   # Duns was entered as an integer without hyphens
        if duns < 0:
            return (False, duns)
        as_str = str(duns)
    elif isinstance(duns, str):                 # Duns was entered as a string with hyphens
        as_str = duns.replace("-", "")

    return (True, f"{as_str[:2]}-{as_str[2:5]}-{as_str[5:]}")


def validate_duns_format(duns: str) -> bool:    # Validate DUNS number format, pass formatted DUNS
    """Validate the format of a DUNS number."""
    if len(duns) != 11:                         # DUNS is improperly formatted
        return False
    if not duns.replace("-", "").isdigit():     # DUNS contains non-digit characters
        return False
    return True