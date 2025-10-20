from pydantic import BaseModel, Field, field_validator
from typing import Optional
from src.enums.medication_enum import PeriodUnitEnum, AdherenceEnum

class MedicationSchema(BaseModel):
    name: str
    note: Optional[str] = None
    dosage_text: Optional[str] = None
    frequency: Optional[int] = None
    period: Optional[float] = None
    period_unit: Optional[PeriodUnitEnum] = Field(default=None)
    adherence: Optional[AdherenceEnum] = Field(default=None)
    reason: Optional[str] = Field(default="Drugs not taken/completed")

    @field_validator("period_unit", mode="before")
    def validate_period_unit(cls, v):
        if v is None:
            return None
        try:
            return PeriodUnitEnum(v)
        except ValueError:
            return None

    @field_validator("adherence", mode="before")
    def validate_adherence(cls, v):
        if v is None:
            return None
        try:
            return AdherenceEnum(v)
        except ValueError:
            return None