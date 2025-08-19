# simple-onboarding

**simple-onboarding** is a self-hostable, dockerized microservice API that streamlines the process of retrieving company information — either from user-provided documents (e.g., contracts, onboarding forms) or from the Dun & Bradstreet D-U-N-S® number (if configured).

Originally developed to simplify payment activation onboarding, it provides a REST API layer on top of several integrated services, including Google Drive/Docs OCR, D&B company lookup, and OpenAI-based document parsing with an easy-to-scale
infrastructure to add more.

---

## Features

- **Document-to-Data** — Upload a company document and extract structured company data automatically.
- **Dun & Bradstreet Lookup** — Retrieve official company information using the D-U-N-S® number.
- **Google OCR Integration** — Process scanned PDFs and images using Google Drive & Docs API.
- **German Handelsregister** — Access the german Handelsregister (company/business register) for data about german companies
- **Unified API Interface** — Host your own microservice and connect it to your web or mobile apps.
- **Extensible Client Architecture** — Easy to add more data providers.

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** for serving API endpoints
- **Uvicorn** for ASGI hosting
- **Docker** for running in an enclosed container
- **Google APIs** for OCR (Drive & Docs) 
- **Dun & Bradstreet API** for data from the source (once implemented)
- **OpenAI API** for structured text extraction
- **Handelsregister API** for access to the german registry of companies

---

## Installation

To install the package in an editable manner, use:
```bash
git clone https://github.com/GHsEpic/simple-onboarding.git
cd simple-onboarding
pip install -e . #Optional, recommended if you want to modify the package
make build
```

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

All credentials are stored in ```app/.env``` using the same structure as
shown in ```app/.env.example```

---

## Running the service

To run the service either use
```bash
make run
```
to run using docker

or simply run main.py
```bash
python app/main.py
```
to run directly in python.

---

## API Endpoints

| Method     | Endpoint                         | Description                            | Request body                  | Response                   |
|------------|----------------------------------|----------------------------------------|-------------------------------|----------------------------|
| ```GET```  | ```/dataByDUNS/{DUNS}```         | Get company data from the D&B API      | Path param: DUNS number       | JSON with company details  |
| ```GET```  | ```/dataByCompanyName/{name}```  | Get company data from company name     | Path param: Company name      | Json with company details  |
|            |                                  | (only supports german companies)       |                               |                            |
| ```POST``` | ```/dataFromPDF/```              | Extract company data from supplied PDF | Multipart form-data with file | JSON with company details  |


**NOTE**: The ```/dataByDUNS/``` endpoint's logic is not yet implemented.

---

## Response codes

| 200 | OK                                  |
|-----|-------------------------------------|
| 400 | Not OK                              |
|-----|-------------------------------------|
| 415 | Invalid DUNS/File isn't a PDF       |
|-----|-------------------------------------|
| 429 | Rate limit exceeded (Internally)    |
|-----|-------------------------------------|
| 503 | Route unavailable                   |

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
        "company": {
            "company_name": "Example Corp.",
            "address": "123 Business St., New York, NY",
            "country": "US"
        },
        "owners": [
            {
                "name": "John Smith",
                "date_of_birth": "1.2.1980"
            }
        ],
        "representatives": [
            {
                "name": "John Smith",
                "date_of_birth": "1.2.1980"
            }
        ],
        "capital": {
            "total_shares": 123,
            "total_amount": 123,
            "currency": "USD"
        }
    }
}
```

# Example name lookup

**Request:**
```bash
curl -X GET "http://localhost:8000/dataByCompanyName/Beispielfirma
```
**Response**
```json
{
    "status_code": 200,
    "message": "Success",
    "data": {
        "company": {
            "company_name": "Example Corp.",
            "address": "123 Business St., New York, NY",
            "country": "US"
        },
        "owners": [
            {
                "name": "Hans Schmidt",
                "date_of_birth": "1.2.1980"
            }
        ],
        "representatives": [
            {
                "name": "Hans Schmidt",
                "date_of_birth": "1.2.1980"
            }
        ],
        "capital": {
            "total_shares": 123,
            "total_amount": 123,
            "currency": "EUR"
        }
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
    "message": "Success",
    "data": {
        "company": {
            "company_name": "Example Corp.",
            "address": "123 Business St., New York, NY",
            "country": "US"
        },
        "owners": [
            {
                "name": "John Smith",
                "date_of_birth": "1.2.1980"
            }
        ],
        "representatives": [
            {
                "name": "John Smith",
                "date_of_birth": "1.2.1980"
            }
        ],
        "capital": {
            "total_shares": 123,
            "total_amount": 123,
            "currency": "USD"
        }
    }
}
```

# Reponse format

The API **always** returns data in this format:
```json
{
    "success": <boolean>,
    "message": <string>,
    "data": {
        "company": {
            "name": <string>,
            "address": <string>,
            "city": <string>,
            "postal_code": <integer>,
            "street": <string>,
            "country": <string>,
            "legal_form": <string>,
            "purpose": <string>,
            "id": <string>,
            "register_court": <string>,
            "register_number": <integer>,
            "register_type": <string>,
            "support_phone": <string>,
            "support_email": <string>,
            "status": <boolean>,
            "industry_codes": <array>
        },
        "representatives": [
            {
                "city": <string>,
                "country": <string>,
                "street": <string>,
                "address": <string>,
                "name": <string>,
                "role": <string>,
                "date_of_birth": <string>,
                "phone": <string>,
                "email": <string>
            },
            ...
        ],
        "owners": [
            {
                "city": <string>,
                "country": <string>,
                "street": <string>,
                "address": <string>,
                "name": <string>,
                "role": <string>,
                "date_o:_birth": <string>,
                "phone": <string>,
                "email": <string>,
                "shares_percentage": <float>,
                "shares_nominal": <float>
            },
            ...
        ],
        "capital": {
            "total_shares": <integer>,
            "total_amount": <integer>,
            "currency": <string>
        }
    }
}

```

**NOTE** that the default value is "" for string and 0 for numbers, not null.