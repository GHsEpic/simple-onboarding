import json, io
from PyPDF2 import PdfReader

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

def load_key(file_path: str) -> str:
    """Load a key from a file."""
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
        if file_path.endswith('.json'):
            return (True, json.loads(data) or {})  # Return JSON data as a dictionary
        else:
            return (True, data)
    except FileNotFoundError:
        with open(file_path, 'w') as file:
            file.write("#Replace with your key")   # Create file with placeholder
        return (False, f"File not found: {file_path}")
    
def extract_text_from_pdf(file_stream: io.BytesIO, google_client) -> str:
    """Extract text from a PDF file stream."""
    try:
        reader = PdfReader(file_stream)     # Try reading text from the PDF (only works with typed PDFs)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        text = text.strip()
    except Exception as e:
        return ""
    
    if text or not google_client:           # Successfully extracted text or no fallback
        return text
    
    file_stream.seek(0)                     # Reset stream position
    response = google_client(file_stream)   # Use the google client for OCR

    return response.data["text"] if response.status_code == 200 else ""