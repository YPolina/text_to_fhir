from pydantic import BaseModel, Field
from typing import List, Optional

class FamilyCondition(BaseModel):
    condition_name: str
    outcome: Optional[str] = None

class FamilyMember(BaseModel):
    relationship: str
    deceased: Optional[bool] = False
    conditions: List[FamilyCondition] = Field(default_factory=list)

class FamilyHistorySchema(BaseModel):
    members: List[FamilyMember]
    note: Optional[str] = None