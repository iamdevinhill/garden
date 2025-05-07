import requests

# First, add a plant to delete
url = "http://localhost:8000/plants/"
headers = {"Content-Type": "application/json"}
data = {
    "name": "Test Plant",
    "species": "Test Species",
    "date_planted": "2024-03-20",
    "location": "Test Location",
    "harvest_info": None,
    "id": None
}

# Add the plant
response = requests.post(url, headers=headers, json=data)
print("Add plant response:", response.status_code)
print(response.text)

# Get the plant ID from the response
plant_id = response.json()["id"]

# Delete the plant
delete_url = f"http://localhost:8000/plants/{plant_id}"
delete_response = requests.delete(delete_url)
print("\nDelete plant response:", delete_response.status_code)
print(delete_response.text)

# Verify the plant is deleted
get_response = requests.get(f"http://localhost:8000/plants/{plant_id}")
print("\nGet deleted plant response:", get_response.status_code)
print(get_response.text) 