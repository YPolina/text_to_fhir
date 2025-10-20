import re
import yaml
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

def save_generated_case(disease: str, case_text:str, yaml_path: str = "src/config/generated_cases.yaml"):

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




