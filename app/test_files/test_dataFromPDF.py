import requests, os
from io import BytesIO

for file_path in os.listdir("../test_files/pdfs"):  # Get all files in the test directory for PDFs
    print(f"Testing {file_path}")
    file_path = f"../test_files/pdfs/{file_path}"
    with open(file_path, "rb") as f:
        file_content = BytesIO(f.read())    # Turn file into a stream
    files = {"file": ("upload.pdf", file_content, "application/pdf")}
    response = requests.post("http://127.0.0.1:8000/dataFromPDF/", files=files) # Post the request
    print(response.json()) # Print the result
    input("Press Enter to continue...")