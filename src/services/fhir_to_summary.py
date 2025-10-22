import json
from typing import Dict, List
from src.utils.load import get_patient_str
from src.schemas.patient import Patient_schema, Patient_Address, Patient
from src.schemas.encounter import Encounter
from src.schemas.observation import LabObservation_schema, VitalSignObservation_schema, SymptomObservation_schema
from src.schemas.medication import MedicationSchema
from src.schemas.familymemberhistory import FamilyHistorySchema, FamilyCondition, FamilyMember

def process_fhir_bundle(fhir:str, logger) -> dict:
    """
    Process fhir bundle and convert into patient summary

    Args:
        fhir (Path): Path for patient record in FHIR format
        logger (logging.Logger): Logger.
    Returns:
        dict: The extracted metadata.
    """
    try:
        with open(fhir, "r", encoding="utf-8") as fh:
            bundle = json.load(fh)
            logger.debug(f"Bundle loaded from {fhir}")
    except Exception as e:
        logger.error(f"Error reading FHIR file: {e}")
        raise

    patient_data = None
    encounters_dict: Dict[str, Encounter] = {}
    observations_dict: Dict[str, List] = {}
    medications_dict: Dict[str, List[MedicationSchema]] = {}
    family_members: List[FamilyMember] = []

    # --- Iterate bundle entries ---
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        r_type = resource.get("resourceType")

        if r_type == "Patient":
            name_info = resource.get("name", [{}])[0]
            given_names = name_info.get("given", [])
            patient_id = resource.get("id")

            patient_data = Patient_schema(
                patient_id=patient_id,
                first_name=given_names[0] if given_names else None,
                second_name=name_info.get("family"),
                gender=resource.get("gender"),
                birthDate=resource.get("birthDate"),
                address=Patient_Address(**(resource.get("address", [{}])[0] or {}))
            )

        elif r_type == "Encounter":
            enc_id = resource.get("id")
            reason_list = resource.get("reason", [])
            reason_text = None
            if reason_list and "value" in reason_list[0]:
                val = reason_list[0]["value"]
                if val and len(val) > 0 and "concept" in val[0]:
                    reason_text = val[0]["concept"].get("text")
            encounters_dict[enc_id] = Encounter(
                encounter_date=None,
                reason=reason_text,
                observation={},
                medication=[]
            )

        elif r_type == "Observation":
            encounter_ref = resource.get("encounter", {}).get("reference")
            if not encounter_ref:
                continue
            enc_id = encounter_ref.split("/")[-1]
            category = resource.get("category", [{}])[0].get("coding", [{}])[0].get("code", "").lower()
            obs_list = observations_dict.setdefault(enc_id, [])

            obs_date_str = resource.get("effectiveDateTime")
            if obs_date_str and enc_id in encounters_dict:
                if not encounters_dict[enc_id].encounter_date:
                    encounters_dict[enc_id].encounter_date = obs_date_str
                else:
                    existing = encounters_dict[enc_id].encounter_date
                    if obs_date_str < existing:
                        encounters_dict[enc_id].encounter_date = obs_date_str

            if category == "laboratory":
                test_name = resource.get("code", {}).get("coding", [{}])[0].get("display")
                value_qty = resource.get("valueQuantity", {})
                obs_list.append(LabObservation_schema(
                    test_name=test_name,
                    value=value_qty.get("value"),
                    unit=value_qty.get("unit"),
                    interpretation=(resource.get("interpretation", [{}])[0].get("coding", [{}])[0].get("code")),
                    status=resource.get("status")
                ))

            elif category == "vital-signs":
                obs_list.append(VitalSignObservation_schema(
                    vital_type=resource.get("code", {}).get("text"),
                    value=resource.get("valueQuantity", {}).get("value"),
                    unit=resource.get("valueQuantity", {}).get("unit"),
                    interpretation=None,
                    status=resource.get("status")
                ))

            else:
                obs_list.append(SymptomObservation_schema(
                    symptom_name=resource.get("code", {}).get("text"),
                    present=True,
                    interpretation=None,
                    status=resource.get("status")
                ))

            observations_dict[enc_id] = obs_list

        elif r_type == "MedicationStatement":
            enc_ref = resource.get("encounter", {}).get("reference")
            if not enc_ref:
                continue

            enc_id = enc_ref.split("/")[-1]
            med_info = resource.get("medication", {}).get("concept", {})
            med_name = med_info.get("text")
            dosage_info = resource.get("dosage", [{}])[0]
            freq = dosage_info.get("timing", {}).get("repeat", {}).get("frequency")
            period = dosage_info.get("timing", {}).get("repeat", {}).get("period")
            period_unit = dosage_info.get("timing", {}).get("repeat", {}).get("periodUnit")

            med = MedicationSchema(
                name=med_name,
                dosage_text=dosage_info.get("text"),
                frequency=freq,
                period=period,
                period_unit=period_unit
            )
            medications_dict.setdefault(enc_id, []).append(med)

        elif r_type == "List":
            contained = resource.get("contained", [])
            for fmh in contained:
                if fmh.get("resourceType") == "FamilyMemberHistory":
                    rel = fmh.get("relationship", {}).get("coding", [{}])[0].get("display")
                    deceased = fmh.get("deceasedBoolean", False)
                    conditions_list = []
                    for cond in fmh.get("condition", []):
                        cond_name = cond.get("code", {}).get("coding", [{}])[0].get("display")
                        conditions_list.append(FamilyCondition(condition_name=cond_name))
                    family_members.append(FamilyMember(
                        relationship=rel,
                        deceased=deceased,
                        conditions=conditions_list
                    ))

    for enc_id, enc in encounters_dict.items():
        enc.observation = {
            "laboratory": [o for o in observations_dict.get(enc_id, []) if isinstance(o, LabObservation_schema)],
            "vital_sign": [o for o in observations_dict.get(enc_id, []) if isinstance(o, VitalSignObservation_schema)],
            "symptom": [o for o in observations_dict.get(enc_id, []) if isinstance(o, SymptomObservation_schema)]
        }
        enc.medication = medications_dict.get(enc_id, [])

    patient_obj = Patient(
        id = patient_id,
        patient_info=patient_data,
        encounters=list(encounters_dict.values()),
        family_history=FamilyHistorySchema(members=family_members)
    )
    print(patient_obj)
    patient_info = get_patient_str(patient_obj)
    return patient_info