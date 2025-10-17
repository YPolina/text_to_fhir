from pydantic import BaseModel, Field
from typing import Optional
from src.enums.medication_enum import PeriodUnitEnum, AdherenceEnum

class MedicationSchema(BaseModel):
    name: str
    note: Optional[str] = None
    dosage_text: Optional[str] = None
    frequency: Optional[int] = None
    period: Optional[float] = None
    period_unit: Optional[PeriodUnitEnum] = Field(default=PeriodUnitEnum.d)
    adherence: Optional[AdherenceEnum] = Field(default=AdherenceEnum.taking)
    reason: Optional[str] = Field(default="Drugs not taken/completed")