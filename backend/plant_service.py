import requests
import os
import time
import logging
import json
from typing import List, Optional
from models import Plant

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlantService:
    def __init__(self):
        self.plants: List[Plant] = []
        self.next_id = 1
        self.ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        self.ollama_url = f"http://{self.ollama_host}:11434"
        self.max_retries = 10
        self.retry_delay = 10
        self.request_timeout = 300
        logger.info(f"Initialized PlantService with Ollama host: {self.ollama_host}")
        logger.info(f"Ollama URL: {self.ollama_url}")
        self._ensure_model_loaded()

    def _ensure_model_loaded(self):
        """Ensure the Llama3.2 3B model is loaded."""
        for attempt in range(self.max_retries):
            try:
                # First check if Ollama is available
                logger.info("Checking if Ollama server is available...")
                health_check = requests.get(f"{self.ollama_url}/", timeout=30)
                health_check.raise_for_status()
                logger.info("Ollama server is available")

                # Check if model is already loaded
                logger.info("Checking if Llama3.2 3B model is loaded...")
                models_response = requests.get(f"{self.ollama_url}/api/tags", timeout=30)
                models_response.raise_for_status()
                models = models_response.json().get("models", [])
                
                if not any(model.get("name") == "llama3.2" for model in models):
                    logger.info("Llama3.2 model not found, pulling it now...")
                    try:
                        pull_response = requests.post(
                            f"{self.ollama_url}/api/pull",
                            json={"name": "llama3.2"},
                            timeout=1800  # 30 minutes timeout for model pull
                        )
                        pull_response.raise_for_status()
                        logger.info("Successfully pulled Llama3.2 model")
                    except Exception as e:
                        logger.warning(f"Failed to pull Llama3.2 model: {str(e)}. Will continue without model.")
                        return
                else:
                    logger.info("Llama3.2 model is already loaded")
                return
            except requests.exceptions.RequestException as e:
                logger.error(f"Error ensuring model is loaded: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
                logger.warning(f"Failed to ensure model is loaded after {self.max_retries} attempts: {str(e)}. Will continue without model.")
                return

    def _query_ollama(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to query Ollama (attempt {attempt + 1}/{self.max_retries})")
                logger.info(f"Query URL: {self.ollama_url}/api/generate")
                logger.info(f"Prompt: {prompt}")
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "llama3.2",
                        "prompt": prompt,
                        "stream": True
                    },
                    timeout=self.request_timeout,
                    stream=True
                )
                
                if response.status_code == 404:
                    logger.warning("Model not found, returning default response")
                    return "Harvest information is not available at this time. Please check back later."
                
                response.raise_for_status()
                
                # Collect all chunks of the response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                full_response += chunk['response']
                        except json.JSONDecodeError:
                            continue
                
                logger.info("Successfully received response from Ollama")
                return full_response.strip()
            except requests.exceptions.RequestException as e:
                logger.error(f"Error querying Ollama: {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    continue
                logger.warning(f"Failed to get response from Ollama after {self.max_retries} attempts: {str(e)}")
                return "Harvest information is not available at this time. Please check back later."

    def add_plant(self, plant: Plant) -> Plant:
        # Query Ollama for harvest information
        prompt = f"""Given the following plant information:
        Name: {plant.name}
        Species: {plant.species}
        Date Planted: {plant.date_planted}
        Location: {plant.location}
        
        Please analyze this information and provide:
        1. Estimated harvest time based on the planting date and typical growth cycle
        2. Specific signs to look for to determine if the plant is ready for harvest
        3. Any location-specific considerations that might affect the harvest timing
        4. Best practices for harvesting this specific plant
        
        Format your response in a clear, structured way with these sections."""

        try:
            logger.info(f"Adding plant: {plant.name}")
            harvest_info = self._query_ollama(prompt)
            plant.harvest_info = harvest_info
            logger.info(f"Successfully added plant with harvest info")
        except Exception as e:
            logger.error(f"Error getting harvest information: {str(e)}")
            plant.harvest_info = f"Error getting harvest information: {str(e)}"

        # Assign an ID to the plant
        plant.id = self.next_id
        self.next_id += 1
        
        # Create a new Plant instance with all fields
        new_plant = Plant(
            id=plant.id,
            name=plant.name,
            species=plant.species,
            date_planted=plant.date_planted,
            location=plant.location,
            harvest_info=plant.harvest_info
        )
        
        self.plants.append(new_plant)
        return new_plant

    def get_all_plants(self) -> List[Plant]:
        return self.plants

    def get_plant(self, plant_id: int) -> Plant:
        for plant in self.plants:
            if plant.id == plant_id:
                return plant
        raise ValueError("Plant not found")

    def delete_plant(self, plant_id: int) -> Optional[Plant]:
        """
        Delete a plant by its ID.
        
        Args:
            plant_id: The ID of the plant to delete
            
        Returns:
            The deleted plant if found, None otherwise
            
        Raises:
            ValueError: If the plant is not found
        """
        for i, plant in enumerate(self.plants):
            if plant.id == plant_id:
                deleted_plant = self.plants.pop(i)
                return deleted_plant
        raise ValueError(f"Plant with ID {plant_id} not found") 