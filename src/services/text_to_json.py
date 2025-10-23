import json
from src.utils.llm_utils import extract_json_block
from src.core import settings
from src.utils.prompt import EXTRACTION_PROMPT
from src.utils.prompt_schemas import OUTPUT_SCHEMA
import logging

logger = logging.getLogger(__name__)

def process_patient_records(patient_record_text:str, client, model, logger) -> dict:
    """
    Extract metadata and compounds from text using LLM.

    Args:
        patient_record_text (str): patient record text.
        client (boto3.client): AWS boto3 client.
        model (ModelID): AWS model ID.
        logger (logging.Logger): Logger.
    Returns:
        dict: The extracted metadata.
    """
    schema_str = json.dumps(OUTPUT_SCHEMA, indent=2)
    prompt = EXTRACTION_PROMPT.format(schema=schema_str, patient_record_text=patient_record_text)

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

    logger.info("Successfully parsed JSON response")
    return cleaned