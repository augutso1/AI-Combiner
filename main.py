import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline, GPT2Tokenizer, GPT2LMHeadModel
import requests
from typing import Optional

app = FastAPI(title="AI Response Combiner")


device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

class PromptRequest(BaseModel):
    prompt: str
    openai_key: Optional[str] = None


try:
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")  
    model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)  
    gpt2_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
except Exception as e:
    print(f"Error loading DistilGPT2: {e}")
    raise RuntimeError("Failed to load DistilGPT2 model")

def get_mock_openai_response(prompt: str, api_key: Optional[str] = None) -> str:
    if api_key:
        try:
            return f"Mock OpenAI response to: {prompt}"
        except Exception as e:
            return f"Error with OpenAI API: {str(e)}"
    return f"Default OpenAI mock response to: {prompt}"

def get_mock_free_model_response(prompt: str) -> str:
    return f"Mock free model response to: {prompt}"

def normalize_response(response: str) -> str:
    return response.strip()

def combine_responses(responses: list[str]) -> str:

    combined = " and ".join(responses)

    return combined


@app.post("/generate")
async def generate_response(request: PromptRequest):
    try:
        prompt = request.prompt
        openai_key = request.openai_key


        responses = []


        openai_response = get_mock_openai_response(prompt, openai_key)
        responses.append(normalize_response(openai_response))


        gpt2_output = gpt2_pipeline(prompt, max_length=50, num_return_sequences=1)[0]["generated_text"]
        responses.append(normalize_response(gpt2_output))


        mock_free_response = get_mock_free_model_response(prompt)
        responses.append(normalize_response(mock_free_response))


        combined_response = combine_responses(responses)


        return {"combined_response": combined_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from transformers import GPT2Tokenizer, GPT2LMHeadModel
tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
model = GPT2LMHeadModel.from_pretrained("distilgpt2")
print("Model loaded successfully")

##testing codyCLI AI to generate commits automatically