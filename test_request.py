import requests
import json
from datetime import date

url = "http://localhost:8000/plants/"
headers = {"Content-Type": "application/json"}
data = {
    "name": "Tomato",
    "species": "Solanum lycopersicum",
    "date_planted": str(date.today()),
    "location": "Backyard Garden",
    "harvest_info": None,
    "id": None
}

response = requests.post(url, headers=headers, json=data)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}") 