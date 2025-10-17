import re


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