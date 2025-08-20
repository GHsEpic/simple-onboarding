"""Base class for storing company data"""

from app.util import calculate_completion_percentage

class CompanyData:
    """Class for holding any company data"""
    class Company():
        """Subclass for holding information about the company itself"""
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
        """Subclass to hold information about the representatives"""
        class Representative:
            """Subclass to hold information about a single representative"""
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
        """Subclass to hold information about the company owners (>25% equity)"""
        class Owner:
            """Subclass to hold information about a single owner (>25% equity)"""
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
        """Subclass to hold information about the companies capital"""
        def __init__(self):
            self.total_amount = 0
            self.total_shares = 0
            self.currency = ""

    def __init__(self):
        self.company = self.Company()
        self.representatives = self.Representatives()
        self.owners = self.Owners()
        self.capital = self.Capital()

    def from_chatgpt(self=None, data=None):
        """Map ChatGPT's response to a CompanyData object 
        (only works with the current OPENAI_RESPONSE_FORMAT)"""
        new_company_data = CompanyData() if not self else self
        if not data:
            return
        new_company_data.company.name =             data["company"]["name"]
        new_company_data.company.address =          data["company"]["address"]
        new_company_data.company.city =             data["company"]["city"]
        new_company_data.company.postal_code =      data["company"]["postal_code"]
        new_company_data.company.street =           data["company"]["street"]
        new_company_data.company.legal_form =       data["company"]["legal_form"]
        new_company_data.company.purpose =          data["company"]["purpose"]
        new_company_data.company.id =               data["company"]["german_company_registration_number"]
        new_company_data.company.register_court =   data["company"]["register_court"]
        new_company_data.company.register_number =  data["company"]["register_number"]
        new_company_data.company.country =          data["company"]["country"]
        new_company_data.company.register_type =    data["company"]["register_type"]
        new_company_data.company.support_phone =    data["company"]["support_phone"]
        new_company_data.company.support_email =    data["company"]["support_email"]
        new_company_data.company.status =           data["company"]["status"]
        new_company_data.company.industry_codes =   data["company"]["industry_codes"]

        for person in data.get("representatives"):
            representative = new_company_data.Representatives.Representative()

            representative.city =           person["city"]
            representative.country =        person["country"]
            representative.street =         person["street"]
            representative.address =        person["address"]
            representative.name =           person["name"]
            representative.role =           person["role"]
            representative.date_of_birth =  person["date_of_birth"]
            representative.phone =          person["phone"]
            representative.email =          person["email"]

            new_company_data.representatives.people.append(representative)

        for person in data.get("owners"):
            owner = new_company_data.Owners.Owner()

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

            new_company_data.owners.people.append(owner)

        new_company_data.capital.total_amount = data["capital"]["total_amount"]
        new_company_data.capital.total_shares = data["capital"]["total_shares"]
        new_company_data.capital.currency =     data["capital"]["currency"]

        return new_company_data

    def from_openregister_details(self=None, data=None):
        """Map the response data from openregister/details to a CompanyData object"""
        new_company_data = CompanyData() if not self else self
        if not data:
            return
        new_company_data.company.name =             data["name"]["name"]
        new_company_data.company.address =          data["address"]["formatted_value"]
        new_company_data.company.city =             data["address"]["city"]
        new_company_data.company.postal_code =      data["address"]["postal_code"]
        new_company_data.company.street =           data["address"]["street"]
        new_company_data.company.legal_form =       data["legal_form"]
        new_company_data.company.purpose =          data.get("purpose")["purpose"] if data.get("purpose") else ""
        new_company_data.company.id =               data["id"]
        new_company_data.company.register_court =   data["register"]["register_court"]
        new_company_data.company.register_number =  data["register"]["register_number"]
        new_company_data.company.country =          data["address"]["country"]
        new_company_data.company.register_type =    data["register"]["register_type"]
        new_company_data.company.status =           data["status"]

        for person in data.get("representation"):
            representative = new_company_data.Representatives.Representative()

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

            new_company_data.representatives.people.append(representative)

        if data.get("capital"):
            new_company_data.capital.total_amount = data["capital"].get("amount")
            new_company_data.capital.currency =     data["capital"].get("currency")

        return new_company_data


    def from_openregister_owners(self=None, data: list=None):
        """Map the response data from openregister/owners to a CompanyData object"""
        new_company_data = CompanyData() if not new_company_data else new_company_data
        for person in data:
            owner = new_company_data.owners.Owner()

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

            new_company_data.owners.people.append(owner)

        return new_company_data

    def cleanup(self):
        """Clean up the data by removing any unfilled owners/representatives"""
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
        return_dict = {}
        return_dict["company"] = self.company.__dict__
        return_dict["representatives"] = [person.__dict__ for person in self.representatives.people]
        return_dict["owners"] = [person.__dict__ for person in self.owners.people]
        return_dict["capital"] = self.capital.__dict__
        return return_dict
