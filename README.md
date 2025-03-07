# AI Response Combiner

A FastAPI-based system that combines responses from multiple powerful AI models through API calls to Groq's API. The system supports various state-of-the-art models and includes a web interface for easy interaction.

## Features

- **Input**: Accepts a prompt via a FastAPI endpoint or web interface
- **Supported Models**:
  - Llama 3.3 70B Versatile
  - Whisper Large V3 Turbo
  - Gemma 2 9B
  - Mixtral 8x7B (32768 context)
  - Distil Whisper Large V3
- **Output**: Combines responses from multiple models with proper attribution
- **Web Interface**: Simple HTML/CSS/JS interface for interacting with the API
- **API Endpoint**: RESTful API for programmatic access

## Setup Instructions

1. **Install Python 3.9+**:

   ```bash
   brew install python  # On macOS
   ```

2. **Create a Virtual Environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install fastapi uvicorn requests pydantic transformers torch
   ```

4. **Configuration**:

   - Create a `.env` file with your Groq API key:
     ```
     GROQ_API_KEY=your_api_key_here
     ```

5. **Run the Application**:

   ```bash
   python main.py
   ```

6. **Access the Web Interface**:
   ```
   http://localhost:8000/static/index.html
   ```

## API Usage

Send a POST request to `/generate` with the following JSON body:

```json
{
  "prompt": "Your question or prompt here",
  "api_key": "your_api_key_here",
  "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"] // Optional - will use default models if not specified
}
```

Example using curl:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain quantum computing",
    "api_key": "your_api_key_here"
  }'
```

## Web Interface

The application includes a simple web interface that allows you to:

- Enter your prompt
- Select one or multiple AI models
- View the combined response

To use the web interface, simply open `http://localhost:8000/static/index.html` in your browser after starting the application.

## Response Format

The API returns a combined response that includes the best answer from the selected models. The combination algorithm currently selects the most detailed response.

## Error Handling

The system includes robust error handling for:

- API authentication issues
- Model-specific errors
- Rate limiting
- Network connectivity problems

Each error is properly logged and returned with appropriate HTTP status codes.

## Future Improvements

- Implement more sophisticated response combination algorithms
- Add streaming support for real-time responses
- Implement response caching for frequently asked questions
- Add model-specific parameter tuning
- Implement fallback mechanisms for model unavailability
- Enhance the web interface with additional features
