import re
import yaml
import json
from pathlib import Path

def extract_json_block(raw_text: str) -> str:
    """
    Extract JSON block from raw text.
    Args:
        raw_text (str): Raw text.
    Returns:
        str: Extracted JSON block.
    """
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if match:
        return match.group(0)
    return raw_text

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
    else:
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


def save_parsed_fhir(parsed_fhir: dict, fhir_path: Path, parsed_base_dir: str = "data/parsed/") -> None:
    """
    Saves the parsed FHIR output to a structured directory under `parsed_base_dir`,
    preserving the subdirectory and filename from the original FHIR path.

    Args:
        parsed_fhir (dict): The parsed FHIR data to save.
        fhir_path (Path): The original path to the FHIR JSON file.
        parsed_base_dir (str, optional): Base directory for saving parsed output.
            Defaults to "data/parsed/".

    Returns:
        None
    """

    relative_path = fhir_path.relative_to("data/output")
    target_path = Path(parsed_base_dir) / relative_path

    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Save as JSON
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(parsed_fhir, f, indent=2, ensure_ascii=False)



