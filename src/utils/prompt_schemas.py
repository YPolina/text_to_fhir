OUTPUT_SCHEMA = {
    "patient": {
        "first_name": "string - given name of the patient (e.g., 'John')",
        "second_name": "string | None - family name of the patient (e.g., 'Doe')",
        "gender": "string | None - one of ['male', 'female', 'other', 'unknown']",
        "birthDate": "string | None - if age is provided (e.g., '42 year-old man'), calculate the year by subtracting the age from today's year (2025-10-16 → 1983). If month/day are not specified, generate random valid month/day. Format must be 'YYYY-MM-DD'. If no year can be inferred, set to None.",
        "address": {
            "text": "string | None - full address as written (optional)",
            "city": "string | None - city or locality",
            "state": "string | None - state or region (if known)",
            "country": "string | None - country name or ISO code"
        }
    },

    "encounters": [{
        "encounter_date": "string - ISO datetime 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'. For current encounter, use today's date; for past, parse from text if possible (or estimate year).",
        "reason": "string | None - reason for the medical encounter, visit, or admission (e.g., 'fever peaks over the last couple of days')",
        "observation": {
                "laboratory": [
                    {
                        "test_name": "string - laboratory test name (use LOINC term, e.g., 'Urinary Copper Excretion', 'Glucose', 'Hemoglobin A1c')",
                        "value": "float | None - numeric result of the test if provided",
                        "unit": "string | None - measurement unit (e.g., 'mmol/L', 'mg/dL')",
                        "interpretation": "string | None - qualitative interpretation (select from this enums:'high', 'low', 'normal', 'abnormal', 'critical', if None of them return None)",
                        "status": "string - FHIR Observation status (select from this enums: 'registered', 'preliminary', 'final', 'amended', 'corrected', 'cancelled', 'entered-in-error', 'unknown'), default 'final'"
                    }
                ],
                "symptom": [
                    {
                        "symptom_name": "string - name of the clinical symptom or finding (use SNOMED term, e.g., 'Abdominal tenderness', 'Insomnia')",
                        "present": "boolean - True if symptom is present, False if explicitly stated absent",
                        "interpretation": "string | None - qualitative interpretation (select from this enums:'high', 'low', 'normal', 'abnormal', 'critical', if None of them return None)",
                        "status": "string - FHIR Observation status (select from this enums: 'registered', 'preliminary', 'final', 'amended', 'corrected', 'cancelled', 'entered-in-error', 'unknown'), default 'final'"
                    }
                ],
                "vital_sign": [
                    {
                        "vital_type": "string - type of vital sign (use SNOMED term, e.g. temperature, weight, height, BMI, head_circumference, oxygen_saturation)",
                        "value": "float | None - numeric value if present",
                        "unit": "string | None - unit of measurement (e.g., 'kg', 'cm', 'degrees C', '%')",
                        "interpretation": "string | None - qualitative interpretation (select from this enums:'high', 'low', 'normal', 'abnormal', 'critical', if None of them return None)",
                        "status": "string - FHIR Observation status (select from this enums: 'registered', 'preliminary', 'final', 'amended', 'corrected', 'cancelled', 'entered-in-error', 'unknown'), default 'final'"
                    }
                ]
            },
        "medication": [
                {
                    "name": "string - name of the medication (e.g., 'Amoxicillin', 'Ibuprofen')",
                    "note": "string | None - free-text note from patient or record (e.g., 'Patient sometimes misses doses')",
                    "dosage_text": "string | None - textual description of dosage (e.g., 'one capsule three times daily')",
                    "frequency": "integer | None - number of doses per period (e.g., 3)",
                    "period": "integer | None - time interval unit count (e.g., 1 for 'once per day')",
                    "adherence": "string | None - medication adherence status (select from: 'taking', 'taking-as-directed', 'taking-not-as-directed', 'not-taking', 'on-hold', 'on-hold-as-directed', 'on-hold-not-as-directed', 'stopped', 'stopped-as-directed', 'stopped-not-as-directed', 'unknown')",
                    "period_unit": "string | None - time unit (select from: 's' [seconds], 'min' [minutes], 'h' [hours], 'd' [days], 'wk' [weeks], 'mo' [months], 'a' [years])",
                    "reason": "string | None - reason for taking or not taking medication (e.g., 'infection', 'Drugs not completed')"
                }
            ]
    }],
    "family_history": {
        "members": [
            {
                "relationship": "string - relationship to patient (e.g., 'Mother', 'Father', 'Uncle', 'Sibling')",
                "deceased": "boolean - True if explicitly stated deceased, False otherwise",
                "conditions": [
                    {
                        "condition_name": "string - medical condition or disease name",
                        "outcome": "string | None - optional outcome (select from: 'Died', 'Recovered', or None)"
                    }
                ]
            }
        ],
        "note": "string | None - optional general note about family history (e.g., 'Both parents and siblings are alive.')"
    }
}
