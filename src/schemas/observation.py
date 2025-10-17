from pydantic import BaseModel, Field
from typing import Optional
from src.enums.observation_enum import Interpretation, Status


class LabObservation_schema(BaseModel):
    test_name: str
    value: Optional[float] = None
    unit: Optional[str] = None
    interpretation: Optional[Interpretation] = None
    status: Optional[Status] = Field(default=Status.final)

class SymptomObservation_schema(BaseModel):
    symptom_name: str
    present: Optional[bool] = Field(default=True)
    interpretation: Optional[Interpretation] = Field(
        default=Interpretation.abnormal)
    status: Optional[Status] = Field(default=Status.final)

class VitalSignObservation_schema(BaseModel):
    vital_type: str
    value: Optional[float] = None
    unit: Optional[str] = None
    interpretation: Optional[Interpretation] = None
    status: Optional[Status] = Field(default=Status.final)