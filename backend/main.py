# File: backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
from plant_service import PlantService
from database import db
from models import Plant

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
plant_service = PlantService()

class Interaction(BaseModel):
    user_input: str
    llm_response: str

@app.post("/plants/", response_model=Plant)
def add_plant(plant: Plant):
    try:
        # Get harvest information from Ollama
        result = plant_service.add_plant(plant)
        
        # Store the interaction in Neo4j
        try:
            db.create_interaction(
                user_input=f"Add plant: {plant.name}",
                llm_response=result.harvest_info if result.harvest_info else ""
            )
        except Exception as e:
            logger.error(f"Failed to store interaction in Neo4j: {str(e)}")
            # Continue even if Neo4j storage fails
        
        return result
    except Exception as e:
        logger.error(f"Error adding plant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/plants/", response_model=List[Plant])
def get_plants():
    return plant_service.get_all_plants()

@app.get("/plants/{plant_id}", response_model=Plant)
def get_plant(plant_id: int):
    try:
        plant = plant_service.get_plant(plant_id)
        if not plant:
            raise HTTPException(status_code=404, detail="Plant not found")
        return plant
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/plants/{plant_id}")
def delete_plant(plant_id: int):
    try:
        plant = plant_service.delete_plant(plant_id)
        
        # Store the interaction in Neo4j
        try:
            db.create_interaction(
                user_input=f"Delete plant: {plant.name}",
                llm_response=f"Successfully deleted plant with ID {plant_id}"
            )
        except Exception as e:
            logger.error(f"Failed to store interaction in Neo4j: {str(e)}")
            # Continue even if Neo4j storage fails
        
        return {"message": f"Plant {plant_id} deleted successfully", "deleted_plant": plant}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting plant: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interactions/")
def get_interactions():
    try:
        interactions = db.get_all_interactions()
        return interactions
    except Exception as e:
        logger.error(f"Error getting interactions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)