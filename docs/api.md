# **API**

## The API class
The API class is used to define properties and functions of the API.
It is a wrapper for a FastAPI app.

**Overview**
| Function name      | Functionality         |
|--------------------|-----------------------|
| ```__init__```     | Initialize the API    |
| ```run```          | Run the API in python |
| ```setup_routes``` | Setup the API routes  |
| ```setup_logging```| Setup logging         |
| ```enable_cors```  | Enable CORS           |

**NOTE** that the setup functions are called in ```__init__```, they do not
have to be called manually.

---

# Routes / Endpoints

## Built-in
| Method     | Endpoint                         | Description                            | Request body                  | Response                   |
|------------|----------------------------------|----------------------------------------|-------------------------------|----------------------------|
| ```GET```  | ```/dataByDUNS/{DUNS}```         | Get company data from the D&B API      | Path param: DUNS number       | JSON with company details  |
| ```GET```  | ```/dataByCompanyName/{name}```  | Get company data from company name     | Path param: Company name      | Json with company details  |
                                                  (only supports german companies)                                                                    
| ```POST``` | ```/dataFromPDF/```              | Extract company data from supplied PDF | Multipart form-data with file | JSON with company details  |

---

## Add your own routes
Adding your own routes is as easy as can be:
To add your own route, simply take a look into ```API.setup_routes```. You'll find 
that all routes are defined as decorated functions following this schema:
```python
class API:
    def setup_routes(self):
        @self.app._method("_route")
        async def _routes_function_name():
            # your logic here
            response = APIResponse(status_code=200, message="OK", data=_your_data)
            return response.to_dict()
```
Here, the _fields correspond to:
- ```_method```: The method you want to allow for this endpoint (GET, POST, etc.)
- ```_route```: The URL-Path your endpoint listens to (e.g. ```"/myEndPoint/"```)
- ```_routes_function_name```: The name of the function, like any other in python 
    (doesn't really matter since it's not gonna be called anywhere else anyway)
- ```_your_data```: The data your route returns, as a dict

**NOTE:** Make sure to define an the function as ```async``` to avoid delays and
the app breaking entirely.

Now, to add your own route, simply copy this or the other routes' code, replace
every _field with your own, add your own logic and you're all set.

## Adding parameters
What parameters you want your route to take directly decides what method you need
to use. If you want a simple path parameter like ```/your_route/parameter```, you
are going to have to use GET. If, however, you want your route to process files,
you will have to use POST.

### Path parameters
To add a path parameter, you simply adjust the URL-path of your 

**Choosing the right method**
What method to use is very important, since e.g. GET cannot be used with additional
request data. 