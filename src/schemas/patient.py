from pydantic import BaseModel, Field
from typing import Optional, List
from src.enums.patient_enum import Gender
from src.schemas.encounter import Encounter
from src.schemas.familymemberhistory import FamilyHistorySchema

class Patient_Address(BaseModel):
    text: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None

class Patient_schema(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    gender: Optional[Gender] = None
    birthDate: Optional[str] = None
    address: Optional[Patient_Address] = None


class Patient(BaseModel):
    id: Optional[str] = None
    patient_info: Patient_schema
    encounters: List[Encounter] = Field(default_factory=list)
    family_history: FamilyHistorySchema = Field(default_factory=FamilyHistorySchema)