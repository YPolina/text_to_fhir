from pydantic import BaseModel, Field, field_validator
from typing import Optional
from src.enums.observation_enum import Interpretation, Status


class ObservationBase(BaseModel):
    interpretation: Optional[Interpretation] = None
    status: Optional[Status] = Field(default=Status.final)

    # Normalize interpretation before validation
    @field_validator("interpretation", mode="before")
    def normalize_interpretation(cls, v):
        if v is None:
            return None
        try:
            return Interpretation(str(v).lower())
        except Exception:
            return None

    # Normalize status before validation
    @field_validator("status", mode="before")
    def normalize_status(cls, v):
        if v is None:
            return Status.final
        try:
            return Status(str(v).lower())
        except Exception:
            return Status.final


class LabObservation_schema(ObservationBase):
    test_name: str
    value: Optional[float] = None
    unit: Optional[str] = None


class SymptomObservation_schema(ObservationBase):
    symptom_name: str
    present: Optional[bool] = Field(default=True)
    interpretation: Optional[Interpretation] = Field(default=Interpretation.abnormal)


class VitalSignObservation_schema(ObservationBase):
    vital_type: str
    value: Optional[float] = None
    unit: Optional[str] = None
