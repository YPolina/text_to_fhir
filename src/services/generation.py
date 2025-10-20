from src.core import settings
from src.utils.prompt import CASE_GENERATION_PROMPT


def generate_case(disease:str, client, model, logger) -> dict:
    """
    Extract metadata and compounds from text using LLM.

    Args:
        disease (str): disease for case generation
        client (boto3.client): AWS boto3 client.
        model (ModelID): AWS model ID.
        logger (logging.Logger): Logger.
    """
    prompt = CASE_GENERATION_PROMPT.format(disease=disease)

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

    if not raw_text:
        logger.warning("Empty response received from model")
        return ""
    return raw_text