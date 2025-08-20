"""Openregister/Handelsregister API Client class"""

import requests
from rapidfuzz.fuzz import ratio    # Used to determine similarity in strings
from app.clients.base_client import BaseClient
from app.util import validate_german_company_id_format
from app.company_data import CompanyData
from app.auto_logging import AutoLogger

class OpenregisterClient(BaseClient):
    """Openregister/Handelsregister APi client class"""
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.logger = AutoLogger("OpenregisterClient")
        self.logger.info("Initializing openregister client")
        self.authenticate()

    def authenticate(self):
        """No additional authentication required"""
        return

    def make_openregister_request(self, url: str, 
                                  method: str = "GET", 
                                  params: dict = None, 
                                  body: dict = None) -> dict:
        """Call the Openregister API with given method and parameters"""
        params = params if params is not None else {}
        body = body if body is not None else {}
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

        res = requests.Response()
        if method.lower() == "get":
            self.logger.debug(f"Getting {url} using headers: {headers}, body: {body}, params: {params}")
            res = requests.get(url, headers=headers, timeout=10)
        elif method.lower() == "post":
            self.logger.debug(f"Posting headers: {headers}, body: {body}, params: {params} to {url}")
            res = requests.post(url, params=params, headers=headers, json=body, timeout=10)
        self.logger.debug(f"Got response code {res.status_code}")
        if res.status_code == 402:
            self.logger.warn("Out of openregister tokens")
        return res.json() if res.ok else {}

    def search_companies(self, company_name: str = None, 
                         register_number: int = None, 
                         register_type: str = None, 
                         register_court: str = None, 
                         active: bool = True, 
                         legal_form: str = None,
                         address: str = None) -> dict:
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

        self.logger.debug(f"Searching for company by query {body}")
        data = self.make_openregister_request("https://api.openregister.de/v1/search/company", "POST", body=body)
        if not data:
            self.logger.debug("Search returned no data")
            return {}

        result = {}
        for company in data["results"]:
            result[ratio(company["name"], company_name)] = company # Create a dict with similarity as key and company as value

        if max(result) > 75:
            self.logger.debug("Found a matching company")
            return result[max(result)]
        self.logger.debug("Didn't find a matching company")
        return {}

    def get_company_details(self, company_id: str) -> CompanyData:
        """Get basic company details"""
        self.logger.debug(f"Getting details of company {company_id}")
        data = self.make_openregister_request(f"https://api.openregister.de/v1/company/{company_id}", "GET")
        return CompanyData.from_openregister_details(data) if data else CompanyData()

    def get_company_owners(self, company_id: str) -> CompanyData:
        """Get company ownership information"""
        self.logger.debug(f"Getting owners of company {company_id}")
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
        self.logger.debug(f"Trying to enrich data of company {known_data.company.name} with id {known_data.company.id}")
        if not (known_data.company.country.lower() in ["de", "deutschland", "germany"]) and not known_data.company.country == "": # Immediately cancel if country is specified and not germany since this API only covers germany
            self.logger.debug(f"Country is specified and not germany; country: {known_data.company.country}")
            return known_data

        search_required = True      # Check if we need to search for the company to get it's company_id
        if known_data.company.id:
            search_required = False
            company_id = known_data.company.id
            if not validate_german_company_id_format(company_id):
                search_required = True

        self.logger.debug(f"Search for company required to get id: {search_required}")

        if search_required:     # Search for the company to get it's company_id
            available_params = {}
            if not known_data.company.name:
                return known_data
            available_params["company_name"] = known_data.company.name

            company = self.search_companies(company_name=available_params["company_name"])
            if not company:
                self.logger.debug("Could not find a mathcing company")
                return known_data
            company_id = company["company_id"]

        self.logger.debug("Found company, mapping information")
        company_data = self.get_company_details(company_id)     # Get all data on the company
        shareholder_data = self.get_company_owners(company_id)

        # Map the APIs response making sure to not overwrite with None or ""
        if shareholder_data.owners:                 known_data.owners =                     shareholder_data.owners
        if company_data.company.city:               known_data.company.city =               company_data.company.city
        if company_data.company.country:            known_data.company.country =            company_data.company.country
        if company_data.company.address:            known_data.company.address =            company_data.company.address
        if company_data.company.postal_code:        known_data.company.postal_code =        company_data.company.postal_code
        if company_data.company.street:             known_data.company.street =             company_data.company.street
        if company_data.company.id:                 known_data.company.id =                 company_data.company.id
        if company_data.company.industry_codes:     known_data.company.industry_codes =     company_data.company.industry_codes
        if company_data.company.legal_form:         known_data.company.legal_form =         company_data.company.legal_form
        if company_data.company.name:               known_data.company.name =               company_data.company.name
        if company_data.company.purpose:            known_data.company.purpose =            company_data.company.purpose
        if company_data.company.register_court:     known_data.company.register_court =     company_data.company.register_court
        if company_data.company.register_number:    known_data.company.register_number =    company_data.company.register_number
        if company_data.company.register_type:      known_data.company.register_type =      company_data.company.register_type
        if company_data.company.status:             known_data.company.status =             company_data.company.status
        if company_data.capital.total_amount:       known_data.capital.total_amount =       company_data.capital.total_amount
        if company_data.capital.currency:           known_data.capital.currency =           company_data.capital.currency
        if company_data.capital.total_shares:       known_data.capital.total_shares =       company_data.capital.total_shares

        return known_data

    def __call__(self, company_name) -> list:
        """Search for a company by name"""
        return self.search_companies(company_name)