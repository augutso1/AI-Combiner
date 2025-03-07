import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel
import requests
from typing import Optional, List, Dict
import os
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="AI Response Combiner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ModelType(Enum):
    LLAMA_70B = "llama-3.3-70b-versatile"
    WHISPER_LARGE = "whisper-large-v3-turbo"
    GEMMA = "gemma2-9b-it"
    MIXTRAL = "mixtral-8x7b-32768"
    DISTIL_WHISPER = "distil-whisper-large-v3-en"

class PromptRequest(BaseModel):
    prompt: str
    api_key: str
    models: Optional[List[str]] = None  


API_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"


DEFAULT_MODELS = [
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

print("Initializing AI Response Combiner API")

async def query_model(prompt: str, model: str, api_key: str) -> str:
    """

    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": model,
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        print(f"\nSending request to {API_BASE_URL}")
        print(f"Payload: {payload}")
        
        response = requests.post(
            API_BASE_URL.rstrip('/'),  
            headers=headers,
            json=payload,
            timeout=30  
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text}")
        
        response.raise_for_status()
        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            content = response_json["choices"][0]["message"]["content"]
            print(f"Extracted content: {content}")
            return content
        else:
            print(f"Unexpected response format: {response_json}")
            return "Error: Unexpected response format"
            
    except requests.exceptions.Timeout:
        print(f"Timeout error querying {model}")
        return f"Error: Request timeout for {model}"
    except Exception as e:
        print(f"Error querying {model}: {str(e)}")
        print(f"Exception type: {type(e)}")
        if isinstance(e, requests.exceptions.RequestException):
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}")
        return f"Error: Failed to get response from {model}"

def normalize_response(response: str) -> str:
    """

    """
    if not response:
        return ""
    
    return response.strip()

def combine_responses(responses: List[Dict[str, str]]) -> str:
    """

    """
    if not responses:
        return "No responses available."
    
    valid_responses = [r for r in responses if r["response"].strip() and not r["response"].startswith("Error:")]
    
    if not valid_responses:
        return "No valid responses available."
    
    best_response = max(valid_responses, key=lambda x: len(x["response"]))
    
    return best_response["response"][:500].strip()

@app.post("/generate")
async def generate_response(request: PromptRequest):
    try:
        prompt = request.prompt
        api_key = request.api_key
        models = request.models or DEFAULT_MODELS

        responses = []
        
        for model in models:
            response = await query_model(prompt, model, api_key)
            responses.append({
                "model": model,
                "response": normalize_response(response)
            })

        combined_response = combine_responses(responses)

        return {"combined_response": combined_response}
    except Exception as e:
        print(f"Error in generate_response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

