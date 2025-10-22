from pathlib import Path
from src.schemas.patient import Patient
from datetime import datetime
import yaml

def load_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_address(address):
    if address.text is not None:
        return (
            f"Address: {address.text}"
            f"  City: {address.city or 'N/A'}\n"
            f"  State: {address.state or 'N/A'}\n"
            f"  Country: {address.country or 'N/A'}"
        )
    else:
        return f"Address: {address.text}"

def get_patient_str(patient):
    # Calculate age
    birth_date = datetime.strptime(patient.patient_info.birthDate, "%Y-%m-%d")
    age = datetime.now().year - birth_date.year - (
        (datetime.now().month, datetime.now().day) < (birth_date.month, birth_date.day)
    )

    patient_str = f"""
    Patient Summary
    ---------------
    Patient ID: {patient.id}
    Name: {patient.patient_info.first_name} {patient.patient_info.second_name}
    Gender: {patient.patient_info.gender.value}
    Age: {age}
    Birth Date: {patient.patient_info.birthDate}
    {format_address(patient.patient_info.address)}
    
    Encounters:
"""

    for i, enc in enumerate(patient.encounters, start=1):
        patient_str += f"""
Encounter {i}:
  Date: {enc.encounter_date}
  Reason: {enc.reason}
  Symptoms:"""
        for symptom in enc.observation.get("symptom", []):
            patient_str += f"\n    - {symptom.symptom_name}: {'Present' if symptom.present else 'Absent'}"

        patient_str += "\n  Vital Signs:"
        for vital in enc.observation.get("vital_sign", []):
            patient_str += f"\n    - {vital.vital_type}: {vital.value} {vital.unit}"

        patient_str += "\n  Laboratory Results:"
        for lab in enc.observation.get("laboratory", []):
            value_str = f"Value: {lab.value}\n      Unit: {lab.unit}" if lab.value is not None else "Not available"
            patient_str += f"\n    - {lab.test_name}:\n      {value_str}"

        patient_str += "\n  Medications:"
        for med in enc.medication:
            if med.frequency and med.period:
                freq = f"{med.frequency}x every {med.period} {med.period_unit.value}"
            else:
                freq = "as needed"
            patient_str += (
                f"\n    - {med.name}:\n"
                f"      Dosage: {med.dosage_text}\n"
                f"      Frequency: {freq}\n"
                f"      Reason: {med.reason}"
            )

    patient_str += "\n\nFamily History:"
    for member in patient.family_history.members:
        patient_str += f"\n  - {member.relationship} (Deceased: {'Yes' if member.deceased else 'No'})"
        for condition in member.conditions:
            patient_str += f"\n    • Condition: {condition.condition_name}"

    return patient_str