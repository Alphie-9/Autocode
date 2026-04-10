import re
import os
import requests
from dotenv import load_dotenv
from prompts import SYSTEM_PROMPT
from executor import execute_python_code

load_dotenv()  # Load variables from .env file

# Using Ollama locally (make sure Ollama is running on your machine)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "tinyllama"  # Tiny, fast model perfect for CPU


def extract_code(text: str) -> str | None:
    """Extract Python code from markdown code block."""
    match = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def run_agent(user_message: str, conversation_history: list) -> dict:
    """
    Main agent loop:
    1. Send message to LLM
    2. Extract code
    3. Execute code
    4. Send result back to LLM for interpretation
    5. If error, retry once (self-correction)
    """
    messages = conversation_history + [{"role": "user", "content": user_message}]

    # Step 1: Get LLM response
    prompt = SYSTEM_PROMPT + "\n\n" + "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=300)  # Increased to 5 minutes for model loading
        response.raise_for_status()
        response_json = response.json()
        
        print(f"DEBUG: Response JSON: {response_json}")  # Debug logging
        
        # Ollama returns response in "response" field
        llm_text = response_json.get("response", "")
            
        if not llm_text:
            print(f"DEBUG: Empty response, full response: {response_json}")  # Debug logging
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: API Error: {str(e)}")  # Debug logging
        return {
            "llm_response": f"Error calling Ollama API: {str(e)}. Make sure Ollama is running on localhost:11434",
            "code": None,
            "execution": None,
            "interpretation": f"API Error: {str(e)}",
            "retry_attempted": False
        }

    # Step 2: Extract and execute code
    code = extract_code(llm_text)
    execution_result = None
    interpretation = ""
    retry_attempted = False

    if code:
        execution_result = execute_python_code(code)

        # Step 3: Self-correction if error
        if not execution_result["success"] and not retry_attempted:
            retry_attempted = True
            error_msg = execution_result["stderr"]
            retry_prompt = SYSTEM_PROMPT + "\n\nError: " + error_msg + "\n\nPlease fix it and try again."
            
            retry_payload = {
                "model": MODEL_NAME,
                "prompt": retry_prompt,
                "stream": False,
                "temperature": 0.7
            }
            try:
                retry_response = requests.post(OLLAMA_URL, json=retry_payload, timeout=300)
                retry_response.raise_for_status()
                retry_json = retry_response.json()
                llm_text = retry_json.get("response", "")
                code = extract_code(llm_text)
                if code:
                    execution_result = execute_python_code(code)
            except requests.exceptions.RequestException:
                pass

        # Step 4: Get interpretation from LLM
        if execution_result:
            exec_summary = f"stdout:\n{execution_result['stdout']}\n"
            if not execution_result["success"]:
                exec_summary += f"stderr:\n{execution_result['stderr']}\n"

            interp_prompt = SYSTEM_PROMPT + "\n\nExecution result:\n" + exec_summary + "\n\nNow provide your concise interpretation."
            interp_payload = {
                "model": MODEL_NAME,
                "prompt": interp_prompt,
                "stream": False,
                "temperature": 0.7
            }
            try:
                interp_response = requests.post(OLLAMA_URL, json=interp_payload, timeout=300)
                interp_response.raise_for_status()
                interp_json = interp_response.json()
                interpretation = interp_json.get("response", "")
            except requests.exceptions.RequestException:
                interpretation = "Could not get interpretation from API"
    else:
        interpretation = llm_text

    return {
        "llm_response": llm_text,
        "code": code,
        "execution": execution_result,
        "interpretation": interpretation,
        "retry_attempted": retry_attempted
    }
