import os
import logging
from typing import Optional, Tuple
from src.core.settings import LOINC_PASSWORD, LOINC_USERNAME, BIOPORTAL_API_KEY

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

interpretation_map = {
            "high": "H",
            "low": "L",
            "normal": "N",
            "abnormal": "A",
            "critical": "HH"
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create a session with authentication
session = requests.Session()
if LOINC_USERNAME and LOINC_PASSWORD:
    session.auth = HTTPBasicAuth(LOINC_USERNAME, LOINC_PASSWORD)


def get_loinc_code(
    search_term: str,
    session: requests.Session = session,
) -> Optional[Tuple[str, str]]:
    """
    Query the Clinical Tables LOINC API for a given lab test name and attempt
    to select a single 'canonical' LOINC code.

    Problem:
        The LOINC database often returns multiple codes for a single test name
        (e.g., "HDL cholesterol" yields codes for HDL2, HDL3, ultracentrifugation,
        ratios, etc.). In practice, you usually want to pick one canonical code
        (e.g., 2085-9 for HDL cholesterol in serum/plasma, mass concentration).
        This function applies a simple heuristic to select the most common,
        methodless, serum/plasma, quantitative, mass concentration code.

    Args:
        search_term (str): The lab test name to search for (e.g., "HDL cholesterol").
        session (requests.Session): An authenticated requests session.

    Returns:
        Optional[Tuple[str, str]]: A tuple of (LOINC code, display name) if found,
        otherwise None.

    Raises:
        requests.RequestException: If the API call fails.
    """
    url = "https://clinicaltables.nlm.nih.gov/api/loinc_items/v3/search"
    params = {"terms": search_term}

    try:
        resp = session.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        codes = data[1]
        names = [n[0] for n in data[3]]

        if not codes or not names:
            logger.warning("No LOINC results for search term '%s'.", search_term)
            return None

        # Safely pick the first result
        code, name = codes[0], names[0]
        if code and name:
            return code, name

        logger.warning("No canonical code found for search term '%s'.", search_term)
        return None

    except requests.RequestException as e:
        logger.error("Error querying LOINC API: %s", e)
        raise


def get_snomed_code(term:str)->Optional[Tuple[str, str]]:
    """
    Query BioPortal for a symptom term and return the first SNOMED CT code.

    Parameters:
        term (str): The symptom or test name to search.
    Returns:
        tuple: (snomed_code, pref_label) or (None, None) if not found.
    """
    url = "https://data.bioontology.org/search"
    params = {
        "q": term,
        "ontologies": "SNOMEDCT",
        "apikey": BIOPORTAL_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Take the first result if available
        results = data.get("collection", [])
        if not results:
            return None, None

        result = results[0]
        pref_label = result.get("prefLabel")
        concept_id = result.get("@id")

        snomed_code = concept_id.split("/")[-1] if concept_id else None
        return snomed_code, pref_label

    except Exception as e:
        print("Error:", e)
        return None, None