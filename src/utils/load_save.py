from pathlib import Path
import json
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
            if vital.value and vital.unit:
                patient_str += f"\n    - {vital.vital_type}: {vital.value} {vital.unit}"

        patient_str += "\n  Laboratory Results:"
        for lab in enc.observation.get("laboratory", []):
            value_str = f"Value: {lab.value}\n      Unit: {lab.unit}" if lab.value is not None else "Not available"
            patient_str += f"\n    - {lab.test_name}:\n      {value_str}"

        patient_str += "\n  Medications:"
        for med in enc.medication:
            # Build frequency string safely
            if med.frequency and med.period:
                if med.period_unit is not None:
                    freq = f"{med.frequency}x every {med.period} {med.period_unit.value}"
                else:
                    freq = f"{med.frequency}x every {med.period} (unit N/A)"
            else:
                freq = "as needed"

            dosage = med.dosage_text or "N/A"
            reason = med.reason or "N/A"

            patient_str += (
                f"\n    - {med.name or 'Unknown'}:\n"
                f"      Dosage: {dosage}\n"
                f"      Frequency: {freq}\n"
                f"      Reason: {reason}"
            )

    patient_str += "\n\nFamily History:"
    for member in patient.family_history.members:
        patient_str += f"\n  - {member.relationship} (Deceased: {'Yes' if member.deceased else 'No'})"
        for condition in member.conditions:
            patient_str += f"\n    • Condition: {condition.condition_name}"

    return patient_str

def save_patient_summary(
        patient_info: str,
        fhir_file: Path,
        fhir_folder: Path)  -> None:
    """
    Saves the parsed FHIR output to a structured directory under `parsed_base_dir`,
    preserving the subdirectory and filename from the original FHIR path.

    Args:
        patient_info (dict): summary of patient
        patient_info (Path): Path to the FHIR JSON file
        fhir_folder (Path): Path to the FHIR output directory
    Returns:
        None
    """
    disease = fhir_file.parent.name
    case = fhir_file.stem

    summary_file = fhir_folder / "summary.txt"

    entry = (
        f"**Disease:** {disease}\n"
        f"**Case:** {case}\n"
        f"**Summary:**\n{patient_info}\n"
        "--------------------------------\n"
    )

    with summary_file.open("a", encoding="utf-8") as f:
        f.write(entry)


def save_generated_case(disease: str, case_text: str, yaml_path: str = "src/config/generated_cases.yaml") -> None:
    """
    Appends a generated case description for a given disease to a YAML file.

    Args:
        disease (str): The name of the disease for which the case was generated.
        case_text (str): The generated case text to be saved.
        yaml_path (str, optional): Path to the YAML file where the case will be stored.
            Defaults to "src/config/generated_cases.yaml".

    Returns:
        None
    """

    yaml_file = Path(yaml_path)
    yaml_file.parent.mkdir(parents=True, exist_ok=True)

    if yaml_file.exists():
        with open(yaml_file, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    if data is None:
        data = {}

    disease_key = disease.lower().replace(" ", "_")

    if disease_key not in data:
        data[disease_key] = []

    case_id = f"case_{len(data[disease_key]) + 1}"
    data[disease_key].append({
        "id": case_id,
        "text": case_text
    })

    with open(yaml_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)


