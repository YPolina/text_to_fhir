from enum import Enum

class Interpretation(str, Enum):
    high = "high"
    low = "low"
    normal = "normal"
    abnormal = "abnormal"
    critical = "critical"

class Status(str, Enum):
    registered = "registered"
    preliminary = "preliminary"
    final = "final"
    amended = "amended"
    corrected = "corrected"
    cancelled = "cancelled"
    entered_in_error = "entered-in-error"
    unknown = "unknown"