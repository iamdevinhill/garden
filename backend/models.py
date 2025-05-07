# File: backend/models.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class Plant(BaseModel):
    id: Optional[int] = None
    name: str
    species: str
    date_planted: date
    location: str
    harvest_info: Optional[str] = None