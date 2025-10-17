from pydantic import BaseModel
from typing import Optional

class EncounterSchema(BaseModel):
    reason: Optional[str] = None