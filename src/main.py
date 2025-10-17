import os
import sys
import yaml
from pathlib import Path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import boto3
import argparse
from src.core import settings
from src.services.text_to_json import process_patient_records
from src.services.json_to_fhir import to_fhir_bundle
from src.utils.load import load_config
import logging

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)

logger = logging.getLogger("fhir_agent")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Converter Patient data to FHIR")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"),
                        help="Path to YAML config file")
    args = parser.parse_args()

    config = load_config(args.config)

    cases = load_config(Path(config["cases_file"]))
    output_dir = Path(config["output_dir"])

    session = boto3.Session(
        aws_access_key_id=settings.AWS_KEY,
        aws_secret_access_key=settings.AWS_SECRET,
        region_name=settings.AWS_REGION,
    )
    logger.info("AWS session initialized")

    client = session.client("bedrock-runtime")
    logger.info("Bedrock client created")

    # Process all diseases and cases
    for disease, case_list in cases.items():
        disease_dir = output_dir / disease
        disease_dir.mkdir(parents=True, exist_ok=True)

        for case in case_list:
            case_id = case["id"]
            case_text = case["text"]

            logger.info(f"Processing {disease} - {case_id}")

            # Run your LLM pipeline on the case text
            llm_output = process_patient_records(case_text, client, settings.MODEL_ID, logger=logger)
            logger.info(f"LLM output for {case_id}: {llm_output}")

            filename = to_fhir_bundle(llm_output, case_id, disease_dir)
            logger.info(f"FHIR bundle saved to {filename}")
