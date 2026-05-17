import json
import requests
from app.core.config import settings

def extract_cv_data_via_llm(raw_text: str) -> dict:
    """
    Pass raw text to Hugging Face Inference API and extract standard JSON schema.
    Schema expected: {"Skills": [], "Experience_Years": 0, "Education_Level": "", "Job_Titles": []}
    """
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    prompt = f"""[INST] Extract the following information from the provided CV text and output strictly a JSON object. 
    The JSON object must have exactly these keys: "Skills" (list of strings), "Experience_Years" (integer representing total years of experience), "Education_Level" (string, e.g., 'Bachelor', 'Master'), "Job_Titles" (list of strings).
    Do not include any explanation or extra text, just the raw JSON.
    CV Text: {raw_text}
    [/INST]"""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "return_full_text": False,
            "temperature": 0.1
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        generated_text = response.json()[0]['generated_text'].strip()
        
        # Try to parse the generated text as JSON. Might need regex or cleanup in production if the LLM output is wrapped in ```json ... ```
        if "```json" in generated_text:
            generated_text = generated_text.split("```json")[1].split("```")[0].strip()
        elif "```" in generated_text:
            generated_text = generated_text.split("```")[1].strip()
            
        return json.loads(generated_text)
    except Exception as e:
        print(f"LLM extraction error: {e}")
        # Return fallback empty structure
        return {"Skills": [], "Experience_Years": 0, "Education_Level": "", "Job_Titles": []}

def optimize_cv(cv_text: str, job_description: str) -> str:
    """Rewrite CV experience bullet points based on the job description."""
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
    
    prompt = f"""[INST] Rewrite the following CV's experience bullet points to highlight the skills required in the provided job description, without fabricating facts. Return only the rewritten experience section.
    Job Description: {job_description}
    Original CV: {cv_text}
    [/INST]"""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "return_full_text": False,
            "temperature": 0.3
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()[0]['generated_text'].strip()
    except Exception as e:
        print(f"CV Optimization error: {e}")
        return "Failed to optimize CV."
