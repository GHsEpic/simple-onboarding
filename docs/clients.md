# **Clients**

# Built-in

## BaseClient
The ```BaseClient``` class from ```app/clients/base_client.py``` is an abstract base class
for other clients.

## Dun & Bradstreet Client
The ```DNBClient``` from ```app/clients/dnb_client.py``` is used for calling the Dun & Bradstreet API.
**NOTE:** Sadly the D&B Client is not yet implemented and probably never will be, since Dun & Bradstreet
did not respond to any of my numerous attempts to reach out.

## Google Client
The ```GoogleClient```from ```app/clients/google_client.py``` is used for calling the Google Docs and
Google Drive API to upload files (mainly PDFs) and extract their text using Google Docs' built-in OCR.

**Overview**
| Function name                 | Functionality                     | Arguments       | Return type | Return value |
|-------------------------------|-----------------------------------|-----------------|-------------|--------------|
| ```authenticate```            | Authenticate the client           | ```None```      | ```None```  | ```None```   |
| ```upload_pdf```              | Upload a PDF to Docs from file    | ```file_path``` | ```string```| ```doc_id``` |
| ```upload_pdf_stream```       | Upload a PDF to Docs from stream  | ```stream```    | ```string```| ```doc_id``` |
| ```delete_file```             | Delete a file from docs by ID     | ```doc_id```    | ```None```  | ```None```   |
| ```extract_text_from_doc```   | Extract text from doc by ID       | ```doc_id```    | ```string```| ```text```   |
| ```extract_text_from_pdf```   | Extract text from a PDF file      | ```file_path``` | ```string```| ```text```   |
| ```__call__```                | Extract text from a file stream   | ```stream```    | ```string```| ```text```   |

## OpenAI Client
The ```OpenAIClient``` from ```app/clients/openai_client.py```is used for interacting with ChatGPT to
ait in extracting and formatting the data from extracted text.

**Overview**
| Function name                 | Functionality                     | Arguments                          | Return type                              | Return value                 |
|-------------------------------|-----------------------------------|------------------------------------|------------------------------------------|------------------------------|
| ```authenticate```            | Authenticate the client           | ```None```                         | ```None```                               | ```None```                    |
| ```extract_and_format```      | Extract data from text via ChatGPT| ```file_text```                    | ```tuple[boolean, ClientResponse/dict]```| ```success, response/data```              |
| ```__call__```                | Extract text from a file stream   | ```file_stream, GoogleClient```    | ```ClientResponse```                     | ```The client's response```          |

## Openregister/Handelsregister Client
The ```OpenregisterClient```from ```app/clients/openregister_client.py```is used for fetching data about
german companies from the official german "Handelsregister" (company/business register)

| Function name                  | Functionality                     | Arguments                       | Return type      | Return value         |
|--------------------------------|-----------------------------------|---------------------------------|------------------|----------------------|
| ```authenticate```             | Authenticate the client           | ```None```                      | ```None```       | ```None```           |
| ```make_openregister_request```| GET or POST a request to the API  | ```url, ...```                  | ```dict```       | ```company data```   |
| ```search_companies```         | Search for companies by filters   | ```company_name, ...```         | ```dict```       | ```company data```   |
| ```get_company_details```      | Get company details               | ```company_id```                | ```dict```       | ```company details```|
| ```get_company_owners```       | Get company owners                | ```company_id```                | ```dict```       | ```company owners``` |
| ```validate_existence```       | Validate that a company exists    | ```company_name, company_id```  | ```bool```       | ```found```          |
| ```enrich_data```              | Update data with anything found   | ```known_data```                | ```CompanyData```| ```old + new data``` |

**NOTE:** These tables don't show all functions.

---

# Create your own
The API is built to be easily scalable, so adding new clients and functionality is very easy.

## 1. Creating the client
In the ```app/clients```directory, add a new file for your client's code, e.g.:
```
app/
|- clients/
| |- base_client.py
| |- your_client.py
```

In the file, import the abstract base class for clients from ```app/clients/base_client.py```
and inherit from it like so:
```python
"""My own client"""
from app.clients.base_client import BaseClient

class MyClient(BaseClient):
    def __init__(self, token):
        self.token = token
        self.authenticate()
    
    def authenticate(self):
        """Authenticate the client"""
        #Your authentication logic
        return
    
    def __call__(self, data):
        #Your call logic#
        return
```
**NOTE** that the base class will require your client to implement the ```authenticate``` and 
```__call__``` methods.

## 2. Adding your clients config
In ```app/config.py``` you will find this:
```python
class CLIENTS:
    class dnb:
        available = false
        message = "Not yet implemented"
```
In the CLIENTS class, add your client as a subclass and give it the availability and message fields.
This is recommended but not necessary, since you'll implement the checks yourself.

You will also find the ```CREDENTIALS```class, which holds all client credentials.
Now just copy how the other keys are loaded and change the name and .env key.
**NOTE** that is can be omitted if your client does not require a key.

## 2.1 Adding your client's key to the .env
In ```.env```, following ```.env.example``` just add the key to a variable and make sure the variable
name matches what you load using ```os.getenv(variable)``` in ```app/config.py```.

## 3 Adding your client to the API
Now that you've set up your client and it's config, you can add it to the API.
In ```app/api.py``` in the ```API``` class, you will find:
```python
class API:
    def __init__(self):
        if CLIENTS.dnb.available:
            self.dnb_client = DNBClient(CREDENTIALS.dnb_token)
        if CLIENTS.google.available:
            self.google_client = GoogleClient(CREDENTIALS.google_token)
```
Just add another check if your client is available (if you implemented that) and initialize an instance
of your client using your credentials (again, if implemented).

Congratulations, you've added your client to the API. To add actual functionality, please have a look at
[Adding routes to the API](api.md#add-your-own-routes)