import requests
from app.clients.BaseClient import BaseClient
from rapidfuzz.fuzz import ratio    # Used to determine similarity in strings
from util import validate_german_company_id_format
from company_data import CompanyData
from autoLogging import AutoLogger

class OpenregisterClient(BaseClient):
    def __init__(self, token: str):
        self.token = token
        self.logger = AutoLogger("OpenregisterClient")
        self.logger.info("Initializing openregister client")
        self.authenticate()
 
    def authenticate(self):
        """No additional authentication required"""
        return
    
    def make_openregister_request(self, url: str, method: str = "GET", params: dict = None, body: dict = None) -> dict:
        """Call the Openregister API with given method and parameters"""
        params = params if params is not None else {}
        body = body if body is not None else {}
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

        if method.lower() == "get":
            res = requests.get(url, headers=headers)
        elif method.lower() == "post":
            res = requests.post(url, params=params, headers=headers, json=body)
        return res.json() if res.ok else {}

    def search_companies(self, company_name: str = None, 
                         register_number: int = None, 
                         register_type: str = None, 
                         register_court: str = None, 
                         active: bool = True, 
                         legal_form: str = None,
                         address: str = None) -> list:
        """Search all german companies"""
        
        
        body = {"query":{}} # Create the query parameters
        if any([register_number, register_type, register_court, active, legal_form, address]):
            body["filters"] = [] # Add a list for filters if any are specified

        if company_name:    # Add the filters
            body["query"]["value"] = company_name
        if register_number:
            body["filters"].append({"field": "register_number", "value":register_number})
        if register_type:
            body["filters"].append({"field": "register_type", "value":register_type})
        if register_court:
            body["filters"].append({"field": "register_court", "value":register_court})
        if active is not None:
            body["filters"].append({"field": "active", "value":str(active).lower()})
        if legal_form:
            body["filters"].append({"field": "legal_form", "value":legal_form})
        if address:
            body["filters"].append({"field": "address", "value":address})

        data = self.make_openregister_request("https://api.openregister.de/v1/search/company", "POST", body=body)
        result = {}
        for company in data["results"]:
            result[ratio(company["name"], company_name)] = company # Create a dict with similarity as key and company as value
        return result[max(result)] if max(result) > 75 else [] # Return highest similarity company if over 75% similar
    
    def get_company_details(self, company_id: str) -> CompanyData:
        """Get basic company details"""
        data = self.make_openregister_request(f"https://api.openregister.de/v1/company/{company_id}", "GET")
        return CompanyData.from_openregister_details(data) if data else CompanyData()

    def get_company_owners(self, company_id: str) -> CompanyData:
        """Get company ownership information"""
        data = self.make_openregister_request(f"https://api.openregister.de/v1/company/{company_id}/owners", "GET") # Use the owners endpoint instead of shareholders since the docs say to do so
        return CompanyData.from_openregister_owners(data["owners"]) if data else CompanyData()
    
    def validate_existence(self, company_name: str, company_id: str = "") -> bool:
        """Validate that the company is registered in the german Handelsregister"""
        companies = self.search_companies(company_name=company_name)
        if any([company["company_id"] == company_id if company_id else True and 
                ratio(company["name"], company_name) > 75 if company_name else True] for company in companies): # Check if any companies name is at least 75% similar with the one provided
            return True
        return False

    def enrich_data(self, known_data: CompanyData) -> CompanyData:
        """Retrieve and add any data there is left about the company in the Handelsregister"""
        if not (known_data.company.country.lower() in ["de", "deutschland", "germany"]) and not known_data.company.country == "": # Immediately cancel if country is specified and not germany since this API only covers germany
            return known_data
        
        search_required = True      # Check if we need to search for the company to get it's company_id
        if known_data.company.id:
            search_required = False
            company_id = known_data.company.id
            if not validate_german_company_id_format(company_id):
                search_required = True

        if search_required:     # Search for the company to get it's company_id
            available_params = {}
            if not known_data.company.name: return known_data
            available_params["company_name"] = known_data.company.name

            companies = self.search_companies(company_name=available_params["company_name"])
            if not companies:
                return known_data
            company_id = companies[0]["company_id"]

        company_data = self.get_company_details(company_id)     # Get all data on the company
        shareholder_data = self.get_company_owners(company_id)

        # Map the APIs response to our format
        known_data.owners =                     shareholder_data.owners
        known_data.company.city =               company_data.company.city
        known_data.company.country =            company_data.company.country
        known_data.company.address =            company_data.company.address
        known_data.company.postal_code =        company_data.company.postal_code
        known_data.company.street =             company_data.company.street
        known_data.company.id =                 company_data.company.id
        known_data.company.industry_codes =     company_data.company.industry_codes
        known_data.company.legal_form =         company_data.company.legal_form
        known_data.company.name =               company_data.company.name
        known_data.company.purpose =            company_data.company.purpose
        known_data.company.register_court =     company_data.company.register_court
        known_data.company.register_number =    company_data.company.register_number
        known_data.company.register_type =      company_data.company.register_type
        known_data.company.status =             company_data.company.status
        known_data.capital.total_amount =       company_data.capital.total_amount
        known_data.capital.currency =           company_data.capital.currency
        known_data.capital.total_shares =       company_data.capital.total_shares

        return known_data

    def __call__(self, company_name) -> list:
        """Search for a company by name"""
        return self.search_companies(company_name)