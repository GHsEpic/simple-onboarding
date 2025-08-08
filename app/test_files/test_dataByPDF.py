import requests, os

for file_path in os.listdir("../test_files/pdfs"):
    file_path = f"../test_files/pdfs/{file_path}"
    files = {"file": (file_path, open(file_path, "rb"), "application/pdf")}  #Replace with your PDF file path
    response = requests.post("http://127.0.0.1:8000/dataFromPDF/", files=files)
    print(response.json())
    input("Press Enter to continue...")