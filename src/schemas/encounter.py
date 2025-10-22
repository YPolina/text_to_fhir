from pydantic import BaseModel
from typing import Optional, List, Dict
from src.schemas.medication import MedicationSchema

class EncounterSchema(BaseModel):
    reason: Optional[str] = None

class Encounter(BaseModel):
    encounter_date: Optional[str] = None
    reason: Optional[str] = None
    observation: Optional[Dict] = None
    medication: Optional[List[MedicationSchema]] = None