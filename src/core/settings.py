from dotenv import load_dotenv
import os

load_dotenv()

# ==== BEDROCK Settings ====
MODEL_ID = os.getenv("MODEL_ID", "us.meta.llama3-3-70b-instruct-v1:0")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "3000"))
BEDROCK_ROLE_ARN = os.getenv("BEDROCK_ROLE_ARN", "arn:aws:iam::338861521122:role/BedrockBatchExecutionRole-us-east-1")

# ==== Prompt building ====
PROMPT_TEMPERATURE = 0.3
PROMPT_TOP_P = 0.7
PROMPT_MAX_TOKENS = 3000

GENERATION_PROMPT_TEMPERATURE = 0.9
GENERATION_PROMPT_TOP_P = 0.9

# ==== AWS Settings ====
AWS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


EMAIL = os.getenv("EMAIL")
BIOPORTAL_API_KEY = os.getenv("BIOPORTAL_API_KEY")

#LOINC
LOINC_PASSWORD = os.getenv("LOINC_PASSWORD")
LOINC_USERNAME = os.getenv("LOINC_USER")

# ==== Logging ====
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")