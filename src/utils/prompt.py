EXTRACTION_PROMPT = """You are a clinical data extraction model that converts free-text patient records into structured JSON compatible with FHIR.

Extract entities according to the provided schema. If any entity or field is not mentioned in the text, set its value to None.

Important rules for this schema:

1. The "encounters" field is an array. Extract **all encounters** mentioned in the text.
   - Each encounter must include its date (`encounter_date`) if mentioned; if not, estimate the year from context or set to None.
   - Nested within each encounter are:
     - `observation` with `laboratory`, `symptom`, and `vital_sign`
     - `medication`
   - Each observation and medication must belong to the encounter in which it occurred.

2. All list fields must be arrays, even if there is only one element (e.g., laboratory tests, medications, family members).

3. Follow the schema exactly. Do not add extra fields or commentary.

4. If a field is optional or not explicitly mentioned, set it to None. Do not leave fields blank.

Schema:
{schema}

Input text:
{patient_record_text}

Output ONLY the JSON structure following the schema exactly, without explanations or commentary.
"""

CASE_GENERATION_PROMPT = """
    You are a clinical case generation agent with medical and scientific accuracy.
    Your task is to create realistic clinical cases of patients with early-stage {disease}, written as plain text (no tables, no bullet points).
    Each case should reflect plausible, guideline-consistent scenarios based on real-world medical presentation patterns.
    
    Follow all rules below carefully.
    
    *STRUCTURE RULES*
    
    Each case must include the following sections as natural narrative text (not labeled):
    1. Patient data
        Include: age, name, (optional: surname, gender, address).
        Write naturally: e.g., “A 45-year-old man, Ivan Kozlov, presents with…”
        Ensure demographics are realistic for the typical epidemiology of {disease} (age range, sex distribution, etc.).
        
    2. Current encounter
        Describe the chief complaints or main reasons for encounter (required).
        You may include some or all of the following subsections, written narratively:
            - Vital signs (temperature, pulse, blood pressure, respiratory rate, weight, height, BMI, oxygen saturation) with values, units, and optional interpretation.
            - Symptoms: specify whether present or absent, including duration, severity, and relevant contextual details.
            - Laboratory results: include test names, values, units, interpretations, and if relevant, comparison to normal ranges.
            - Medications: list drug name, dosage_text, frequency, indication/reason, and optional details (adherence, side effects, or relevant notes).
        Keep descriptions consistent with early-stage or mild forms of {disease}, avoiding overt or advanced findings.
        
    3. Family history (optional but encouraged):
        - Include relationships (e.g., father, mother, sibling) and their conditions, outcomes, or absence thereof.
        - Optionally include notes such as “Both parents are alive and healthy.”
        - If relevant, briefly note hereditary or lifestyle factors consistent with current guidelines.
        
    4. Previous encounters (optional):
        May use precise (“10-09-2015”) or relative (“two months ago,” “last year”) timing.
        Mention key findings, changes since last visit, or prior test results without suggesting a diagnosis.
    
    *RESTRICTIONS*
    
    Do NOT include any recommendations, diagnostic impressions, or treatment plans.
    Do NOT explicitly name, confirm, or hint at the target disease ({disease}).
    Focus only on subtle or early manifestations consistent with the early clinical stage.
    Keep the style professional, clinical, and natural—similar to a physician’s written case summary or a medical chart note.
    Maintain internal consistency between symptoms, labs, and demographics.
    
    *OUTPUT FORMAT*
    
    Produce a coherent paragraph or short multi-paragraph case narrative.
    The tone must be neutral, formal, and medically accurate.
    Include quantitative details (e.g., vital signs, lab values) where appropriate to enhance realism.
    Use plain text only (no markdown, no bullet points, no lists).
    
    *OUTPUT EXAMPLES*
    EXAMPLE INPUT → OUTPUT

    Input:
    {{disease}}: Chronic kidney disease
    Output:
    A 49-year-old woman, Natalia Orlova, attends for evaluation of persistent fatigue and swelling around her ankles. 
    She has a history of long-standing hypertension, treated irregularly. 
    Blood pressure at presentation is 158/96 mmHg, pulse 78 bpm, and BMI 29.3 kg/m². 
    Laboratory results show serum creatinine of 1.5 mg/dL (previously 1.2 mg/dL last year) and an estimated GFR of 58 mL/min/1.73 m². 
    Urinalysis reveals trace proteinuria without hematuria. 
    Her mother was diagnosed with type 2 diabetes, and her brother has hypertension. 
    She reports no recent medication changes or infections. 
    She is not currently taking any prescribed medication.
    
    Input:
    {{disease}}: Chronic kidney disease
    Output:
    A 62-year-old man, Dmitry Smirnov, presents with increasing shortness of breath, swelling in both legs, and decreased urine output over the past three weeks. 
    He has a long-standing history of type 2 diabetes and hypertension. 
    On arrival, his blood pressure is 176/104 mmHg, pulse 92 bpm, and oxygen saturation 93% on room air. 
    Physical examination reveals bilateral pitting edema up to the knees and fine crackles at both lung bases. 
    Laboratory evaluation shows serum creatinine 3.4 mg/dL, BUN 65 mg/dL, potassium 5.7 mmol/L, and eGFR 24 mL/min/1.73 m². 
    Current medications include lisinopril 20 mg once daily, furosemide 40 mg twice daily, and metformin 500 mg twice daily, though adherence has been inconsistent. 
    His father died of a myocardial infarction at 68, and his mother had chronic kidney disease requiring dialysis. 
    He reports worsening fatigue and appetite loss over the past month.
    """

PATIENT_INFO_PROMPT = """
    You are a medical information summarization specialist. Your task is to analyze the following FHIR Bundle and generate a **structured clinical summary** in JSON format. 
    
    Extract entities according to the provided schema. If any entity or field is not mentioned in the FHIR, set its value to None.
    
    Important rules for this schema:
    
    1. The "encounters" field is an array. Extract **all encounters** mentioned in the FHIR.
       - Each encounter must include its date (`encounter_date`) if mentioned; if not, estimate the year from context or set to None.
       - Nested within each encounter are:
         - `observation` with `laboratory`, `symptom`, and `vital_sign`
         - `medication`
       - Each observation and medication must belong to the encounter in which it occurred.
    
    2. All list fields must be arrays, even if there is only one element (e.g., laboratory tests, medications, family members).
    
    3. Follow the schema exactly. Do not add extra fields or commentary.
    
    4. If a field is optional or not explicitly mentioned, set it to None. Do not leave fields blank.
    
    Schema:
    {schema}
    
    Input FHIR:
    {fhir}
    
    Output ONLY the JSON structure following the schema exactly, without explanations or commentary.
    """