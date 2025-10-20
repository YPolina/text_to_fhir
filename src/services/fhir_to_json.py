import json
from src.utils.llm_utils import extract_json_block
from src.core import settings
from src.utils.prompt import PATIENT_INFO_PROMPT
from src.utils.prompt_schemas import OUTPUT_SCHEMA

def process_fhir_bundle(fhir:str, client, model, logger) -> dict:
    """
    Extract metadata and compounds from text using LLM.

    Args:
        fhir (Path): Path for patient record in FHIR format
        client (boto3.client): AWS boto3 client.
        model (ModelID): AWS model ID.
        logger (logging.Logger): Logger.
    Returns:
        dict: The extracted metadata.
    """
    schema_str = json.dumps(OUTPUT_SCHEMA, indent=2)
    with open(fhir, "r", encoding="utf-8") as fh:
        fhir_content = fh.read()
        fhir_str = json.loads(fhir_content)
    prompt = PATIENT_INFO_PROMPT.format(schema=schema_str, fhir=fhir_str)

    conversation = [{
        "role": "user",
        "content": [{"text": prompt}]
    }]


    response = client.converse(
        modelId=model,
        messages=conversation,
        inferenceConfig={"maxTokens": settings.PROMPT_MAX_TOKENS, "temperature": settings.PROMPT_TEMPERATURE}
    )
    logger.debug("Received response from model")

    raw_text = response["output"]["message"]["content"][0].get("text", "").strip()
    cleaned = extract_json_block(raw_text)

    try:
        parsed = json.loads(cleaned)
        logger.info("Successfully parsed JSON response")
        return parsed
    except Exception as e:
        logger.error(f"Parse error: {e}")
        logger.debug(f"RAW OUTPUT:\n{raw_text}")
        parsed = {}
        return parsed