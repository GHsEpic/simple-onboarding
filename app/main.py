"""Main file used for running the API directly in python"""

from app.api import API

api = API() # Initialize the API instance

if __name__ == "__main__":
    api.run()   # Run the API
