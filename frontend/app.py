import streamlit as st
import requests
from datetime import date
import json

# Configure the page
st.set_page_config(page_title="Garden Tracker", layout="wide")

# Constants
API_URL = "http://backend:8000"  # Using Docker service name instead of localhost

def add_plant(name, species, date_planted, location):
    try:
        response = requests.post(
            f"{API_URL}/plants/",
            json={
                "name": name,
                "species": species,
                "date_planted": date_planted.isoformat(),
                "location": location
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error adding plant: {str(e)}")
        return None

def get_plants():
    try:
        response = requests.get(f"{API_URL}/plants/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching plants: {str(e)}")
        return []

def delete_plant(plant_id: int):
    try:
        response = requests.delete(f"{API_URL}/plants/{plant_id}")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error deleting plant: {str(e)}")
        return False

# Main app
st.title("🌱 Garden Tracker")

# Add new plant form
with st.form("add_plant_form"):
    st.subheader("Add New Plant")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Plant Name")
        species = st.text_input("Species")
    
    with col2:
        date_planted = st.date_input("Date Planted", value=date.today())
        location = st.text_input("Location")
    
    submitted = st.form_submit_button("Add Plant")
    
    if submitted:
        if name and species and location:
            plant = add_plant(name, species, date_planted, location)
            if plant:
                st.success(f"Successfully added {name}!")
        else:
            st.warning("Please fill in all required fields")

# Display existing plants
st.subheader("Your Plants")
plants = get_plants()

if plants:
    for plant in plants:
        with st.expander(f"{plant['name']} ({plant['species']})"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write("**Basic Information**")
                st.write(f"📍 **Location:** {plant['location']}")
                st.write(f"📅 **Date Planted:** {plant['date_planted']}")
            
            with col2:
                if plant.get('harvest_info'):
                    st.write("**Harvest Information**")
                    # Split the harvest info into sections if it contains numbered points
                    harvest_info = plant['harvest_info'].split('\n')
                    for line in harvest_info:
                        if line.strip():
                            if line.strip().startswith(('1.', '2.', '3.', '4.')):
                                st.write(f"🌱 {line.strip()}")
                            else:
                                st.write(line.strip())
                else:
                    st.info("Harvest information is being generated...")
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{plant['id']}"):
                    if delete_plant(plant['id']):
                        st.success(f"Successfully deleted {plant['name']}!")
                        st.rerun()
else:
    st.info("No plants added yet. Add your first plant using the form above!") 