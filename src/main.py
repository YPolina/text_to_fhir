import os
import sys
import yaml
from pathlib import Path
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import boto3
import argparse
from src.core import settings
from src.services.generation import generate_case
from src.services.text_to_json import process_patient_records
from src.utils.llm_utils import save_generated_case, save_parsed_fhir
from src.services.json_to_fhir import to_fhir_bundle
from src.services.fhir_to_json import process_fhir_bundle
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

    session = boto3.Session(
        aws_access_key_id=settings.AWS_KEY,
        aws_secret_access_key=settings.AWS_SECRET,
        region_name=settings.AWS_REGION,
    )
    logger.info("AWS session initialized")

    client = session.client("bedrock-runtime")
    logger.info("Bedrock client created")

    args = parser.parse_args()

    config = load_config(args.config)

    mode = config["mode"]
    logger.info(f"Mode: {mode}")
    if mode == 'rag_preparation':
        fhir_base_dir = Path(config["fhir_directory"])
        parsed_base_dir = Path(config["parsed_fhir_dir"])

        for fhir_file in fhir_base_dir.rglob("*.json"):
            logger.info(f"Processing FHIR bundle: {fhir_file}")

            llm_output = process_fhir_bundle(fhir_file, client, settings.MODEL_ID, logger)

            save_parsed_fhir(llm_output, fhir_file, fhir_base_dir, parsed_base_dir)

            logger.info(f"Parsed FHIR bundle saved: {fhir_file}")

    elif mode == "generate":
        for disease_entry in config["diseases"]:
            disease = disease_entry["name"]
            num_gen = disease_entry.get("num_generation", 1)

            for i in range(num_gen):
                logger.info(f"Generating case {i + 1} for {disease}...")
                case_text = generate_case(disease, client, settings.MODEL_ID, logger)
                if case_text:
                    save_generated_case(disease, case_text, config["cases_file"])

    if mode in ["generate", "pre-defined"]:
        cases = load_config(Path(config["cases_file"]))
        output_dir = Path(config["output_dir"])
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
                logger.info(f"Processed fhir bundle {llm_output}")

                filename = to_fhir_bundle(llm_output, case_id, disease_dir)
                logger.info(f"FHIR bundle saved to {filename}")

