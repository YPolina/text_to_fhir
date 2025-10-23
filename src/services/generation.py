from typing import Optional
import logging
import boto3
from src.core.settings import GENERATION_PROMPT_TEMPERATURE, GENERATION_PROMPT_TOP_P, PROMPT_MAX_TOKENS
from src.utils.prompt import CASE_GENERATION_PROMPT


def generate_case(
    disease: str,
    client: boto3.client,
    model: str,
    logger: logging.Logger
) -> Optional[str]:
    """
    Generates a synthetic clinical case description for a given disease using an LLM via AWS Bedrock.

    Args:
        disease (str): The name of the disease for which to generate a case.
        client (boto3.client): An initialized AWS Bedrock runtime client.
        model (str): The model ID to use for generation (e.g., Meta Llama 3 or Anthropic Claude).
        logger (logging.Logger): Logger instance for logging progress and debugging.

    Returns:
        Optional[str]: The generated case text if successful, otherwise None.
    """
    prompt = CASE_GENERATION_PROMPT.format(disease=disease)

    conversation = [{
        "role": "user",
        "content": [{"text": prompt}]
    }]

    response = client.converse(
        modelId=model,
        messages=conversation,
        inferenceConfig={"maxTokens": PROMPT_MAX_TOKENS, "temperature": GENERATION_PROMPT_TEMPERATURE, "topP": GENERATION_PROMPT_TOP_P}
    )

    logger.debug("Received response from model")

    raw_text = response["output"]["message"]["content"][0].get("text", "").strip()

    if not raw_text:
        logger.warning("Empty response received from model")
        return ""
    return raw_text