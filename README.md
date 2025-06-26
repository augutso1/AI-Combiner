# AI Response Combiner

A system that unites replies from multiple powerful AI models via API calls to the Groq service. It supports various cutting-edge models and includes both a web interface and a command-line interface for effortless interaction.

## Features

  - **Web API Mode**: FastAPI API with a REST endpoint and web interface
  - **Terminal Mode**: Command-line interface for direct interaction
  - **Supported Models**:
      - Llama 4 Maverick 17B (Instruct)
      - Llama 3.3 70B Versatile
      - Llama 3 70B (8192 context)
      - DeepSeek R1 Distill Llama 70B
      - Gemma 2 9B IT
      - Llama 4 Scout 17B (Instruct)
      - Qwen 3 32B
  - **Combination Method**: LCEL (LangChain Expression Language) pipeline with multiple refinement cycles
  - **Conversation Memory**: Upholds the context of prior interactions
  - **Web Interface**: Simple HTML/CSS/JS interface for interacting with the API
  - **Command-Line Interface**: Interactive mode for direct queries via terminal

## Architecture

The project is structured into two chief modules:

### Backend

  - **api/**: API routes and endpoints
  - **schemas/**: Data models and validation
  - **services/**: Business logic and model combination
  - **main.py**: FastAPI server and CLI

### Frontend

  - **index.html**: Primary web interface
  - **script.js**: Logic for interacting with the API
  - **style.css**: Interface styling

## Configuration Instructions

1.  **Install Python 3.9+**:

   `bash    brew install python  # On macOS    `

2.  **Create a Virtual Environment**:

   `bash    python3 -m venv venv    source venv/bin/activate    `

3.  **Install Dependencies**:

   `bash    pip install -r requirements.txt    `

4.  **Configuration**:

   - Configure your Groq API key via environment variable:
     `bash      export GROQ_API_KEY="your_api_key_here"      `
   - Or forge a `.env` file with your key:
     `       GROQ_API_KEY=your_api_key_here       `

## Application Execution

### Command-Line Mode

```bash
python -m backend.main --cli
```

You'll behold an interactive prompt where you can pose inquiries directly to the combined model system.

### Web Server Mode

```bash
python -m backend.main
```

Access the web interface at:

```
http://localhost:8000
```

## API Usage

Dispatch a POST request to `/api/generate` with the following JSON body:

```json
{
  "prompt": "Your inquiry or instruction here",
  "api_key": "your_api_key_here",
  "models": ["llama-4-maverick-17b", "gemma2-9b-it"] // Optional - will employ default models if not specified
}
```

Instance using curl:

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Expound on quantum computing",
    "api_key": "your_api_key_here"
  }'
```

## How the Combination System Operates

The system harnesses the LCEL (LangChain Expression Language) approach to craft an agent pipeline that:

1.  Processes user input through various AI models in parallel
2.  Merges the initial replies into a structured format
3.  Utilizes this outcome as context for a chief model to forge the ultimate response
4.  Sustains conversation history for contextualization

The system performs up to 3 cycles of refinement for each query, progressively ameliorating the response quality.

## Error Handling

The system encompasses robust error management for:

  - Authentication issues with the API
  - Model-specific errors
  - Rate limiting
  - Network connectivity woes

Each error is properly logged and returned with appropriate HTTP status codes.

## Future Enhancements

  - Implement more sophisticated response combination algorithms
  - Append streaming support for real-time replies
  - Institute response caching for frequent inquiries
  - Incorporate parameter tuning specific to each model
  - Deploy fallback mechanisms for model unavailability
  - Improve the web interface with additional functionalities
