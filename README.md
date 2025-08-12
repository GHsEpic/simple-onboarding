# simple-onboarding

**simple-onboarding** is a microservice API that streamlines the process of retrieving company information — either from user-provided documents (e.g., contracts, onboarding forms) or from the Dun & Bradstreet D-U-N-S® number (if configured).

Originally developed to simplify payment activation onboarding, it provides a REST API layer on top of several integrated services, including Google Drive/Docs OCR, D&B company lookup, and OpenAI-based document parsing with an easy-to-scale
infrastructure to add more.

---

## Features

- **Document-to-Data** — Upload a company document and extract structured company data automatically.
- **Dun & Bradstreet Lookup** — Retrieve official company information using the D-U-N-S® number.
- **Google OCR Integration** — Process scanned PDFs and images using Google Drive & Docs API.
- **Unified API Interface** — Host your own microservice and connect it to your web or mobile apps.
- **Extensible Client Architecture** — Easy to add more data providers.

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** for serving API endpoints
- **Uvicorn** for ASGI hosting
- **Google APIs** for OCR (Drive & Docs) 
- **Dun & Bradstreet API** for data from the source (once implemented)
- **OpenAI API** for structured text extraction

---

## Installation

```bash
git clone https://github.com/yourusername/simple-onboarding.git
cd simple-onboarding
pip install -e .
```

There will be a pip-able python package in the future.

---

##  Configuration

Configuration is handled via `app/config.py`

# Endpoints

Configure which endpoints should be available via setting their availability

```python
class CLIENTS:
    class google:
        available = True
        message = "Available"
    ...
```

# API-Keys & Tokens

All credentials are stored in the ```app/credentials```directory.

For the OpenAI token, paste it into ```app/credentials/openai_token.txt```.
For the Google secret (which is then used to generate token and credentials),
paste it into ```app/credentials/google_secret.json```.
**NOTE**: Please fill the files ```app/credentials/google_token.json```as well as
```app/credentials/google_credentials.json``` with {}.

---

## Running the service

To run the service either use

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

or simply run main.py

```bash
python app/main.py
```

---

## API Endpoints

| Method     | Endpoint                 | Description                            | Request body                  | Response                   |
|------------|--------------------------|----------------------------------------|-------------------------------|----------------------------|
| ```GET```  | ```/dataByDUNS/{DUNS}``` | Get company data from the D&B API      | Path param: DUNS number       | JSON with company details  |
| ```POST``` | ```/dataFromPDF/```      | Extract company data from supplied PDF | Multipart form-data with file | JSON with extracted fields |

**NOTE**: The ```/dataByDUNS/``` endpoint's logic is not yet implemented.

---

# Example D-U-N-S® lookup

**Request:**
```bash
curl -X GET "http://localhost:8000/dataByDUNS/12-345-6789"
```
**Response**
```json
{
    "status_code": 200,
    "message": "Success",
    "data": {
        "company_name": "Example Corp.",
        "address": "123 Business St., New York, NY",
        "country": "US"
    }
}
```

# Example PDF-upload

**Request:**
```bash
curl -X POST "http://localhost:8000/dataFromPDF" \
  -F "file=license.pdf"
```
**Reponse:**
```json
{
    "status_code": 200,
    "message": "Data extracted successfully",
    "data": {
        "company_name": "Example Corp.",
        "registration_number": "HRB 12345",
        "address": "123 Business St., New York, NY",
        "country": "US"
    }
}
```