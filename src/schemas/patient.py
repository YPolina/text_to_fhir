from pydantic import BaseModel
from typing import Optional
from src.enums.patient_enum import Gender

class Patient_Address(BaseModel):
    text: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]

class Patient_schema(BaseModel):
    first_name: str
    second_name: Optional[str] = None
    gender: Optional[Gender] = None
    birthDate: Optional[str] = None
    address: Optional[Patient_Address] = None
