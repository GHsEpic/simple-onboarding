import io
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

def validate_german_company_id_format(company_id) -> bool:
    """Validate that the company_id follows the format DE-HR[A/B]-XXXXXX-XXXXX"""
    as_list = company_id.lower().split("-")
    if len(as_list) != 4: return False
    if as_list[0] != "de": return False
    if not as_list[1].startswith("hr"): return False
    if not as_list["2"].isdigit() or not as_list["3"].is_digit(): return False
    return True