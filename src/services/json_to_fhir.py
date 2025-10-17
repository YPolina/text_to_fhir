from pydantic import ValidationError
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import uuid

#Patient
from fhir.resources.patient import Patient
from src.schemas.patient import Patient_schema
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address

#Observations
from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
from fhir.resources.quantity import Quantity
from src.schemas.observation import LabObservation_schema, SymptomObservation_schema, VitalSignObservation_schema
from src.utils.codes_request import get_loinc_code, interpretation_map, get_snomed_code

#FamilyHistory
from fhir.resources.list import List as FHIRList
from fhir.resources.familymemberhistory import FamilyMemberHistory
from src.schemas.familymemberhistory import FamilyHistorySchema

#Medication
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.codeablereference import CodeableReference
from fhir.resources.annotation import Annotation
from fhir.resources.dosage import Dosage
from fhir.resources.timing import Timing
from src.schemas.medication import MedicationSchema
from src.enums.medication_enum import AdherenceEnum

#Encounter
from src.schemas.encounter import EncounterSchema
from fhir.resources.encounter import Encounter
from fhir.resources.identifier import Identifier

#Bundle
from fhir.resources.bundle import Bundle, BundleEntry, BundleEntryRequest


def patient_to_fhir(
        data: Dict[str, Any]
) -> Tuple[Patient, int, str]:
    """
    Convert validated patient data into a FHIR Patient resource.

    Args:
        data (Dict[str, Any]): Dictionary containing patient information.
            Expected keys:
                - first_name (str): Patient's given name.
                - second_name (str): Patient's family name.
                - address (dict): Address details with keys 'text', 'city', 'state', 'country'.
                - gender (str): Patient's gender ("male", "female", "other", "unknown").
                - birthdate (str): Patient's birth date in ISO format (YYYY-MM-DD).

    Returns:
        Tuple[Patient, patient_id]: JSON string representation of the FHIR Patient resource and patient_id.

    Raises:
        ValidationError: If the input data does not conform to Patient_schema.
    """
    try:
        Patient_schema.model_validate(data)
    except ValidationError as err:
        raise ValidationError(err.messages[0])

    resource_type = "Patient"
    patient_id = str(uuid.uuid4())
    human_name = HumanName(
        family=data.get("second_name"),
        given=[data.get("first_name")]
    )
    addr_data = data.get("address", {})
    address = Address(
        text=addr_data.get("text"),
        city=addr_data.get("city"),
        state=addr_data.get("state"),
        country=addr_data.get("country")
    )
    gender = data.get("gender")
    birthdate = data.get("birthdate")

    patient = Patient(
        id=patient_id,
        resourceType=resource_type,
        name=[human_name],
        gender=gender,
        birthDate=birthdate,
        address=[address]
    )

    return patient, patient_id, f'{data.get("first_name")} {data.get("second_name")}'



def lab_observation_to_fhir(
        data: Dict[str, Any],
        patient_id: int,
        encounter_id: int,
        date: Optional[str] = None
) -> Observation:
    """
    Convert validated lab observation data into a FHIR Observation resource.

    Args:
        data (Dict[str, Any]): Dictionary containing observation details.
        patient_id (int): ID of the patient to reference in the Observation.
        encounter_id (int): ID of the encounter to reference in the Observation.
        date (Optional[str]): ISO 8601 datetime string for when the observation was effective.
            Defaults to current UTC time if not provided.

    Returns:
        str: JSON string representation of the FHIR Observation resource.

    Raises:
        ValueError: If the input data does not conform to LabObservation_schema.
    """
    try:
        obs = LabObservation_schema(**data)
    except ValidationError as err:
        raise ValueError(f"Invalid lab observation structure: {err}")

    loinc_info = get_loinc_code(obs.test_name)
    if loinc_info:
        loinc_code, loinc_display = loinc_info
    else:
        loinc_code, loinc_display = "unknown", obs.test_name


    observation = Observation(
        id=str(uuid.uuid4()),
        resourceType="Observation",
        status=obs.status.value,
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="laboratory",
                        display="Laboratory"
                    )
                ],
                text="Laboratory"
            )
        ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://loinc.org",
                    code=loinc_code,
                    display=loinc_display
                )
            ],
            text=obs.test_name
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        encounter=Reference(reference=f"Encounter/{encounter_id}"),
        effectiveDateTime=date or datetime.now(timezone.utc).isoformat()
    )

    # Add valueQuantity if present
    if obs.value is not None and obs.unit:
        observation.valueQuantity = Quantity(
            value=obs.value,
            unit=obs.unit,
            system="http://unitsofmeasure.org",
            code=obs.unit
        )

    # Add interpretation if exists
    if obs.interpretation:
        code = interpretation_map.get(obs.interpretation.value, "A")
        observation.interpretation = [
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        code=code,
                        display=obs.interpretation.value.capitalize()
                    )
                ]
            )
        ]

    # Add definition (LOINC reference page)
    if loinc_code != "unknown":
        observation.note = [{
            "text": f"Definition: https://loinc.org/{loinc_code}/"
        }]

    return observation

def symptom_observation_to_fhir(
    data: Dict[str, Any],
    patient_id: str,
    encounter_id: Optional[str] = None,
    date: Optional[str] = None
) -> Observation:
    """
    Convert validated symptom observation data into a FHIR Observation resource.
    Mirrors lab_observation_to_fhir structure using fhir.resources classes.

    Args:
        data (Dict[str, Any]): Dictionary containing symptom observation details.
        patient_id (str): Patient reference ID.
        encounter_id (Optional[str]): Encounter reference ID.
        date (Optional[str]): ISO 8601 datetime string. Defaults to current UTC.

    Returns:
        str: JSON string of FHIR Observation.
    Raises:
        ValueError: If the input `data` does not conform to the SymptomObservation_schema.
        Exception: For any unexpected FHIR object construction or serialization errors.
    """
    try:
        obs = SymptomObservation_schema(**data)
    except ValidationError as err:
        raise ValueError(f"Invalid symptom observation structure: {err}")

    snomed_info = get_snomed_code(obs.symptom_name)
    if snomed_info:
        snomed_code, snomed_display = snomed_info
    else:
        snomed_code, snomed_display = "unknown", obs.symptom_name

    # Build Observation
    observation = Observation(
        id=str(uuid.uuid4()),
        resourceType="Observation",
        status=obs.status.value,
        category=[
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/observation-category",
                        code="exam",
                        display="Exam"
                    )
                ],
                text="Exam"
            )
        ],
        code=CodeableConcept(
            coding=[
                Coding(
                    system="http://snomed.info/sct",
                    code=snomed_code,
                    display=snomed_display
                )
            ],
            text=obs.symptom_name
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        encounter=Reference(reference=f"Encounter/{encounter_id}"),
        effectivePeriod={
            "start": date or datetime.now(timezone.utc).isoformat()
        }
    )

    # Symptom presence
    observation.valueBoolean = bool(obs.present)

    # Interpretation if exists
    if obs.interpretation:
        code = interpretation_map.get(obs.interpretation.value, "A")
        observation.interpretation = [
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                        code=code,
                        display=obs.interpretation.value.capitalize()
                    )
                ],
                text=obs.interpretation.value.capitalize()
            )
        ]

    # SNOMED reference
    if snomed_code != "unknown":
        observation.note = [{
            "text": f"Definition: https://snomed.info/id/{snomed_code}"
        }]

    return observation


def vital_observation_to_fhir(
    data: dict,
    patient_id: str,
    encounter_id: Optional[str] = None,
    date: Optional[str] = None
) -> Observation:
    """
    Convert a validated vital sign observation into a FHIR-compliant Observation resource.

    Args:
        data (dict): Dictionary containing vital observation details following the
            VitalSignObservation_schema format
        patient_id (str): Unique FHIR Patient resource ID reference.
        encounter_id (Optional[str]): Optional FHIR Encounter resource ID reference.
        date (Optional[str]): ISO 8601 datetime string indicating when the observation
            was effective. Defaults to current UTC time if not provided.

    Returns:
        str: JSON-formatted string representing the FHIR Observation resource
             (resourceType = "Observation"), suitable for use in clinical data exchange
             or FHIR servers.

    Raises:
        ValueError: If the input `data` does not conform to the VitalSignObservation_schema.
        Exception: For any unexpected FHIR object construction or serialization errors.
    """

    try:
        obs = VitalSignObservation_schema(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid vital observation structure: {e}")

    loinc_info = get_loinc_code(obs.vital_type)
    if loinc_info:
        loinc_code, loinc_display = loinc_info
    else:
        loinc_code, loinc_display = "unknown", obs.vital_type


    observation = Observation(
            id=str(uuid.uuid4()),
            resourceType="Observation",
            status=obs.status.value,
            category=[
                CodeableConcept(
                    coding=[
                        Coding(
                            system="http://terminology.hl7.org/CodeSystem/observation-category",
                            code="vital-signs",
                            display="Vital Signs"
                        )
                    ],
                    text="Vital Signs"
                )
            ],
            code=CodeableConcept(
                coding=[Coding(system="http://loinc.org", code=loinc_code, display=loinc_display)],
                text=obs.vital_type
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            encounter=Reference(reference=f"Encounter/{encounter_id}"),
            effectiveDateTime=date or datetime.now(timezone.utc).isoformat()
        )

    if obs.value is not None and obs.unit:
        observation.valueQuantity = Quantity(
            value=obs.value,
            unit=obs.unit,
            system="http://unitsofmeasure.org",
            code=obs.unit
        )

    if obs.interpretation:
        code = interpretation_map.get(obs.interpretation.value, "A")
        observation.interpretation = [
            CodeableConcept(
                coding=[Coding(
                    system="http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    code=code,
                    display=obs.interpretation.value.capitalize()
                )],
                text=obs.interpretation.value.capitalize()
            )
        ]

    return observation


def family_history_to_fhir_json(
        data: Dict,
        patient_id: str
) -> FamilyMemberHistory:
    """
    Convert structured family history data (parsed from LLM output) into a FHIR-compliant JSON string.
    Args:
        data (dict): Dictionary containing structured family history data following the
            FamilyHistorySchema format
        patient_id (str): Unique FHIR Patient ID to link the FamilyMemberHistory resources to.
    Returns:
        str: A JSON-formatted string representing the complete FHIR List resource with nested
        FamilyMemberHistory entries. The JSON structure complies with FHIR R4 standards.

    Raises:
        ValueError: If the provided JSON does not conform to the FamilyHistorySchema.
        Exception: For unexpected FHIR construction or serialization errors.
    """

    # Validate and parse the LLM JSON
    try:
        fam_history = FamilyHistorySchema(**data)
    except ValidationError as e:
        raise ValueError(f"Invalid family history structure: {e}")

    members = fam_history.members
    list_note_text = fam_history.note

    contained_resources = []
    entries = []

    for idx, member in enumerate(members, start=1):
        fmh_id = f"fmh-{idx}"

        # Map relationship
        for idx, member in enumerate(members, start=1):
            fmh_id = f"fmh-{idx}"

            rel_code, rel_display = get_snomed_code(member.relationship) or ("unknown", member.relationship)

        #Map condition
        condition_list = []
        for cond in member.conditions:
            cond_name = cond.condition_name
            cond_outcome = cond.outcome
            cond_code, cond_display = get_snomed_code(cond_name) or ("unknown", cond_name)
            cond_entry = {
                "code": {
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": cond_code,
                        "display": cond_display
                    }]
                }
            }

            if cond_outcome:
                outcome_code, outcome_display = get_snomed_code(cond_outcome) or ("unknown", cond_outcome)
                cond_entry["outcome"] = {
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": outcome_code,
                        "display": outcome_display
                    }]
                }
            condition_list.append(cond_entry)

        fmh_resource = FamilyMemberHistory(
            id=fmh_id,
            resourceType="FamilyMemberHistory",
            status="completed",
            patient=Reference(reference=f"Patient/{patient_id}"),
            relationship=CodeableConcept(
                coding=[Coding(system="http://snomed.info/sct", code=rel_code, display=rel_display)]
            ),
            deceasedBoolean=member.deceased,
            condition=condition_list
        )

        contained_resources.append(fmh_resource)
        entries.append({"item": {"reference": f"#{fmh_id}"}})

        family_history = FHIRList(
            id=str(uuid.uuid4()),
            resourceType="List",
            contained=contained_resources,
            status="current",
            mode="snapshot",
            code=CodeableConcept(
                coding=[Coding(
                    system="http://loinc.org",
                    code="8670-2",
                    display="History of family member diseases"
                )]
            ),
            subject=[Reference(reference=f"Patient/{patient_id}")],
            note=[{"text": list_note_text}] if list_note_text else None,
            entry=entries
        )

        return family_history


def medication_to_fhir(
        data: Dict[str, Any],
        patient_id: int,
        encounter_id: Optional[int] = None,
        date: Optional[str] = None
) -> MedicationStatement:
    """
    Convert validated medication data into a FHIR MedicationStatement resource
    with full adherence and timing support.
    """
    try:
        med = MedicationSchema(**data)
    except ValidationError as err:
        raise ValueError(f"Invalid medication structure: {err}")

    snomed_code, snomed_display = get_snomed_code(med.name)

    med_statement = MedicationStatement(
        id=str(uuid.uuid4()),
        resourceType="MedicationStatement",
        status="recorded",
        medication=CodeableReference(
            concept=CodeableConcept(
                coding=[Coding(
                    system="http://snomed.info/sct",
                    code=snomed_code,
                    display=snomed_display
                )],
                text=med.name
            )
        ),
        subject=Reference(reference=f"Patient/{patient_id}"),
        encounter=Reference(reference=f"Encounter/{encounter_id}"),
        effectiveDateTime=date or datetime.now(timezone.utc).isoformat(),
        informationSource=[Reference(reference=f"Patient/{patient_id}")]
    )

    # Note
    if med.note:
        med_statement.note = [Annotation(text=med.note)]

    # Dosage with timing
    if med.dosage_text or (med.frequency and med.period):
        timing = None
        if med.frequency and med.period:
            timing = Timing(
                repeat={
                    "frequency": med.frequency,
                    "period": med.period,
                    "periodUnit": med.period_unit.value
                }
            )
        dosage = Dosage(
            text=med.dosage_text,
            timing=timing
        )
        med_statement.dosage = [dosage]

    if med.adherence:
        # Adherence
        adherence_dict = {
            "code": {
                "coding": [{
                    "system": "http://hl7.org/fhir/CodeSystem/medication-statement-adherence",
                    "code": med.adherence.value,
                    "display": med.adherence.value.replace("-", " ").title()
                }]
            }
        }

        # Reason for non-taking / stopped / on-hold
        if med.adherence not in {AdherenceEnum.taking, AdherenceEnum.taking_as_directed,
                                 AdherenceEnum.taking_not_as_directed}:
            adherence_dict["reason"] = {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    # default Drugs not taken/completed
                    "code": "266710000",
                    "display": med.reason
                }]
            }

        med_statement.adherence = adherence_dict

    return med_statement

def encounter_to_fhir(
        data: dict,
        patient_id: str,
        patient_name: Optional[str] = None
) -> tuple[Encounter, int]:
    """
    Convert LLM data into a FHIR Encounter resource.

    Args:
        data: LLM data
        patient_id: Patient ID
        patient_name: Patient name
    Returns:
        Tuple[Encounter, int]: Encounter and patient ID.
    """
    try:
        encounter = EncounterSchema(**data)
    except ValidationError as err:
        raise ValueError(f"Invalid encounter structure: {err}")

    encounter_id = str(uuid.uuid4())
    try:
        encounter_resource = Encounter(
            id=encounter_id,
            resourceType="Encounter",
            identifier=[Identifier(
                use="temp",
                value=f"Encounter_{patient_name if patient_name else patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )],
            status="completed",
            priority=CodeableConcept(
                coding=[Coding(
                    system="http://snomed.info/sct",
                    code="17621005",
                    display="Normal"
                )]
            ),
            type=[CodeableConcept(
                coding=[Coding(
                    system="http://snomed.info/sct",
                    code="11429006",
                    display="Consultation"
                )]
            )],
            subject=Reference(
                reference=f"Patient/{patient_id}",
                display=patient_name
            )
        )
    except ValidationError as err:
        raise ValueError(f"Invalid encounter structure: {err}")

    # Assign reason from LLM if provided
    if encounter.reason:
        encounter_resource.reason = [{
            "value": [{
                "concept": {
                    "text": encounter.reason
                }
            }]
        }]

    return encounter_resource, encounter_id

def to_fhir_bundle(
        llm_output: Dict[str, Any],
        case_id: int,
        output_dir:Path = './data/output') -> str:
    """
    Convert the structured LLM output (patient case) into a full FHIR Bundle.

    Args:
        llm_output: LLM output
        case_id: case ID
        output_dir: Output directory
    Returns:
        str: Output directory for FHIR Bundle
    """

    entries: List[BundleEntry] = []

    # PATIENT
    patient_resource, patient_id, patient_name = patient_to_fhir(llm_output["patient"])
    entries.append(
        BundleEntry(
            fullUrl=f"urn:uuid:{patient_id}",
            resource=patient_resource,
            request=BundleEntryRequest(method="POST", url="Patient")
        )
    )

    # ENCOUNTER
    encounter_resource, encounter_id = encounter_to_fhir(
        llm_output["encounter"], patient_id, patient_name
    )
    entries.append(
        BundleEntry(
            fullUrl=f"urn:uuid:{encounter_id}",
            resource=encounter_resource,
            request=BundleEntryRequest(method="POST", url="Encounter")
        )
    )

    # OBSERVATION
    if "observation" in llm_output:
        obs_data = llm_output["observation"]

        for lab in obs_data.get("laboratory", []):
            obs = lab_observation_to_fhir(lab, patient_id, encounter_id)
            entries.append(
                BundleEntry(
                    fullUrl=f"urn:uuid:{obs.id}",
                    resource=obs,
                    request=BundleEntryRequest(method="POST", url="Observation")
                )
            )

        for sym in obs_data.get("symptom", []):
            obs = symptom_observation_to_fhir(sym, patient_id, encounter_id)
            entries.append(
                BundleEntry(
                    fullUrl=f"urn:uuid:{obs.id}",
                    resource=obs,
                    request=BundleEntryRequest(method="POST", url="Observation")
                )
            )

        for vital in obs_data.get("vital_sign", []):
            obs = vital_observation_to_fhir(vital, patient_id, encounter_id)
            entries.append(
                BundleEntry(
                    fullUrl=f"urn:uuid:{obs.id}",
                    resource=obs,
                    request=BundleEntryRequest(method="POST", url="Observation")
                )
            )

    # FAMILY HISTORY
    if "family_history" in llm_output and llm_output["family_history"].get("members"):
        fam_hist = family_history_to_fhir_json(llm_output["family_history"], patient_id)
        entries.append(
            BundleEntry(
                fullUrl=f"urn:uuid:{fam_hist.id}",
                resource=fam_hist,
                request=BundleEntryRequest(method="POST", url="FamilyMemberHistory")
            )
        )

    # MEDICATION
    if "medication" in llm_output and llm_output["medication"]:
        for med in llm_output["medication"]:
            med_res = medication_to_fhir(med, patient_id, encounter_id)
            entries.append(
                BundleEntry(
                    fullUrl=f"urn:uuid:{med_res.id}",
                    resource=med_res,
                    request=BundleEntryRequest(method="POST", url="MedicationStatement")
                )
            )

    # BUNDLE
    bundle = Bundle(
        type="transaction",
        entry=entries
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = output_dir / f"{case_id}_{patient_id}.json"
    bundle_json = bundle.model_dump_json(indent=2)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(bundle_json)
    return filename

