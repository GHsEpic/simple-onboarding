from app.util import calculate_completion_percentage

class CompanyData:
    """Class for holding any company data"""
    class Company():
        def __init__(self):
            self.country = ""
            self.name = ""
            self.address = ""
            self.city = ""
            self.postal_code = ""
            self.street = ""
            self.industry_codes = []
            self.legal_form = ""
            self.purpose = ""
            self.id = ""
            self.register_court = ""
            self.register_number = ""
            self.register_type = ""
            self.support_phone = ""
            self.support_email = ""
            self.status = None

    class Representatives:
        class Representative:
            def __init__(self):
                self.city = ""
                self.country = ""
                self.street = ""
                self.address = ""
                self.name = ""
                self.role = ""
                self.date_of_birth = ""
                self.phone = ""
                self.email = ""
        
        def __init__(self):
            self.people = []

    class Owners:
        class Owner:
            def __init__(self):
                self.city = ""
                self.country = ""
                self.street = ""
                self.address = ""
                self.name = ""
                self.role = ""
                self.date_of_birth = ""
                self.phone = ""
                self.email = ""
                self.shares_percentage = 0
                self.shares_nominal = 0

        def __init__(self):
            self.people = []

    class Capital:
        def __init__(self):
            self.total_amount = 0
            self.total_shares = 0
            self.currency = ""
    
    def __init__(self):
        self.company = self.Company()
        self.representatives = self.Representatives()
        self.owners = self.Owners()
        self.capital = self.Capital()
    
    def from_chatgpt(data):
        """Map ChatGPT's response to a CompanyData object (only works with the current OPENAI_RESPONSE_FORMAT)"""
        self = CompanyData()
        self.company.name =             data["company"]["name"]
        self.company.address =          data["company"]["address"]
        self.company.city =             data["company"]["city"]
        self.company.postal_code =      data["company"]["postal_code"]
        self.company.street =           data["company"]["street"]
        self.company.legal_form =       data["company"]["legal_form"]
        self.company.purpose =          data["company"]["purpose"]
        self.company.id =               data["company"]["german_company_registration_number"]
        self.company.register_court =   data["company"]["register_court"]
        self.company.register_number =  data["company"]["register_number"]
        self.company.country =          data["company"]["country"]
        self.company.register_type =    data["company"]["register_type"]
        self.company.support_phone =    data["company"]["support_phone"]
        self.company.support_email =    data["company"]["support_email"]
        self.company.status =           data["company"]["status"]
        self.company.industry_codes =   data["company"]["industry_codes"]

        for person in data["representatives"]:
            representative = self.Representatives.Representative()
            
            representative.city =           person["city"]
            representative.country =        person["country"]
            representative.street =         person["street"]
            representative.address =        person["address"]
            representative.name =           person["name"]
            representative.role =           person["role"]
            representative.date_of_birth =  person["date_of_birth"]
            representative.phone =          person["phone"]
            representative.email =          person["email"]

            self.representatives.people.append(representative)
        
        for person in data["owners"]:
            owner = self.Owners.Owner()

            owner.city =                person["city"]
            owner.country =             person["country"]
            owner.street =              person["street"]
            owner.address =             person["address"]
            owner.name =                person["name"]
            owner.role =                person["role"]
            owner.date_of_birth =       person["date_of_birth"]
            owner.phone =               person["phone"]
            owner.email =               person["email"]
            owner.shares_percentage =   person["shares_percentage"]
            owner.shares_nominal =      person["shares_nominal"]

            self.owners.people.append(owner)
        
        self.capital.total_amount = data["capital"]["total_amount"]
        self.capital.total_shares = data["capital"]["total_shares"]
        self.capital.currency =     data["capital"]["currency"]

        return self
    
    def from_openregister_details(data):
        """Map the response data from openregister/details to a CompanyData object"""
        print(data)
        self = CompanyData()
        self.company.name =             data["name"]["name"]
        self.company.address =          data["address"]["formatted_value"]
        self.company.city =             data["address"]["city"]
        self.company.postal_code =      data["address"]["postal_code"]
        self.company.street =           data["address"]["street"]
        self.company.legal_form =       data["legal_form"]
        self.company.purpose =          data.get("purpose")["purpose"] if data.get("purpose") else ""
        self.company.id =               data["id"]
        self.company.register_court =   data["register"]["register_court"]
        self.company.register_number =  data["register"]["register_number"]
        self.company.country =          data["address"]["country"]
        self.company.register_type =    data["register"]["register_type"]
        self.company.status =           data["status"]

        for person in data["representation"]:
            representative = self.Representatives.Representative()

            representative.role = person.get("role")
            representative.name = person.get("name")
            if person["type"] == "natural_person":
                representative.date_of_birth =       person["natural_person"].get("date_of_birth")
                representative.city =                person["natural_person"].get("city")
                representative.country =             person["natural_person"].get("country")
            else:
                representative.city =    person["legal_person"].get("city")
                representative.country = person["legal_person"].get("country")
                representative.date_of_birth = person["legal_person"].get("date_of_birth")

            self.representatives.people.append(representative)
        
        if data.get("capital"):
            self.capital.total_amount = data["capital"].get("amount")
            self.capital.currency =     data["capital"].get("currency")

        return self


    def from_openregister_owners(data):
        """Map the response data from openregister/owners to a CompanyData object"""
        self = CompanyData()
        for person in data:
            owner = self.owners.Owner()

            owner.role =                person.get("relation_type")
            owner.shares_nominal =      person.get("nominal_share")
            owner.shares_percentage =   person.get("percentage_share")
            if person.get("type") == "natural_person":
                owner.city =                person["natural_person"].get("city")
                owner.country =             person["natural_person"].get("country")
                owner.date_of_birth =       person["natural_person"].get("date_of_birth")
                owner.name =                person["natural_person"].get("full_name")
            elif person.get("type") == "legal_person":
                owner.city =    person["legal_person"].get("city")
                owner.country = person["legal_person"].get("country")
                owner.name =    person["legal_person"].get("name")
            
            self.owners.people.append(owner)
        
        return self
    
    def cleanup(self):
        new_owners = []
        for owner in self.owners.people:
            if calculate_completion_percentage(owner) > 0:
                new_owners.append(owner)
        
        new_representatives = []
        for representative in self.representatives.people:
            if calculate_completion_percentage(representative) > 0:
                new_representatives.append(representative)
        
        self.owners.people = new_owners
        self.representatives.people = new_representatives

    def to_dict(self) -> dict:
        """Turn the CompanyData object into a JSON-like dict for serialization"""
        self.cleanup()
        D = {}
        D["company"] = self.company.__dict__
        D["representatives"] = [person.__dict__ for person in self.representatives.people]
        D["owners"] = [person.__dict__ for person in self.owners.people]
        D["capital"] = self.capital.__dict__
        return D