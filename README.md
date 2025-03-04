# AI Response Combiner Prototype

A FastAPI-based system that takes a user prompt, queries multiple AI models (one paid mock, one local free model, and one free mock), and combines their responses into a single output. Built for a MacBook Pro M1 Pro (16GB RAM, Apple Silicon with MPS support).

## Features

- **Input**: Accepts a prompt via a FastAPI endpoint, with an optional OpenAI API key.
- **Models**:
  - Mock OpenAI (placeholder for a paid model).
  - Local GPT-2 (free, runs on-device with MPS acceleration).
  - Mock second free model (hardcoded response).
- **Output**: Combines responses with a simple "and" separator, returned as JSON.
- **Limitations**: Progress is stalled due to reliance on free models. Real paid models (e.g., OpenAI) or larger free models (e.g., Mistral-7B) could improve output quality, but they require API keys or more memory than available.

## Setup Instructions (macOS)

1. **Install Python 3.9+**:

   - Use Homebrew: `brew install python`

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate

   ```

3. **Install Dependencies**

```bash
pip install torch torchvision  # MPS-enabled PyTorch for Apple Silicon
pip install transformers requests fastapi uvicorn pydantic
```

4. **Run the Application**

```bash
python main.py
```

5. **Test the Endpoint:**
   Use curl or Postman:

```bash
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d '{"prompt": "Tell me about AI", "openai_key": null}'
```

**How It Works**
The system queries three sources:
A mocked OpenAI response (static text).
GPT-2 running locally (small free model, 124M parameters).
A mocked second free model (static text).
Responses are combined with "and" and returned as JSON.
Current Limitations
Free Models Only: Using GPT-2 and mocks limits output quality. Paid models or larger free models could enhance results, but:
Paid APIs (e.g., OpenAI) require keys I don’t have.
Larger models (e.g., Mistral-7B) exceed my 16GB RAM.
Simple Combiner: The "and" concatenation isn’t smart—it just glues responses together, making them hard to read.
Progress Stalled: Without access to better models or more hardware, I can’t refine this further.
Future Improvements (Blocked)
Replace mocks with real APIs (needs funding/keys).
Use a smarter combiner (e.g., summarizer model, needs more RAM or fine-tuning).
Upgrade to a bigger model (needs >16GB RAM or cloud resources).
