import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import Optional, List, Dict
import os
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware

# =============================================================================
# DEFINIÇÕES DE MODELOS DE DADOS
# =============================================================================

# Define uma enumeração para os tipos de modelos disponíveis na API Groq
class ModelType(Enum):
    """
    Enumeração dos modelos de IA disponíveis na API Groq.
    """
    LLAMA_70B = "llama-3.3-70b-versatile"
    WHISPER_LARGE = "whisper-large-v3-turbo"
    GEMMA = "gemma2-9b-it"
    MIXTRAL = "mixtral-8x7b-32768"
    DISTIL_WHISPER = "distil-whisper-large-v3-en"

# Define o modelo de dados para as requisições recebidas pela API
class PromptRequest(BaseModel):
    """
    Modelo Pydantic para validação das requisições recebidas.
    """
    prompt: str  # O texto para o qual queremos gerar respostas
    api_key: str  # Chave da API Groq fornecida pelo usuário
    models: Optional[List[str]] = None  # Lista opcional de modelos a serem consultados

# =============================================================================
# CONFIGURAÇÃO DA API
# =============================================================================

# Inicializa a aplicação FastAPI com um título descritivo
app = FastAPI(title="AI Response Combiner")

# Configura o middleware CORS para permitir requisições de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

print("Initializing AI Response Combiner API")

# =============================================================================
# MÓDULO DE IA - IMPLEMENTAÇÃO DOS MODELOS E LÓGICA DE IA
# =============================================================================

# URL base da API Groq para completions de chat
API_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

# Lista de modelos padrão utilizados quando o usuário não especifica modelos
DEFAULT_MODELS = [
    "llama-3.3-70b-versatile",
    "mixtral-8x7b-32768",
    "gemma2-9b-it"
]

async def query_model(prompt: str, model: str, api_key: str) -> str:
    """
    Consulta um modelo específico na API Groq e retorna a resposta.
    Lida com erros de timeout e outros problemas de conexão.
    
    Args:
        prompt: Texto para o qual queremos a resposta do modelo
        model: Nome do modelo a ser consultado
        api_key: Chave de API para autenticação
        
    Returns:
        Resposta do modelo ou mensagem de erro
    """
    # Prepara os cabeçalhos com a autenticação
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prepara o payload da requisição com o prompt do usuário
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": model,
        "max_tokens": 150,  # Limita o tamanho da resposta
        "temperature": 0.7  # Define a criatividade/aleatoriedade do modelo
    }
    
    try:
        # Registra informações da requisição para debug
        print(f"\nSending request to {API_BASE_URL}")
        print(f"Payload: {payload}")
        
        # Envia a requisição para a API Groq
        response = requests.post(
            API_BASE_URL.rstrip('/'),  # Remove barra final se existir
            headers=headers,
            json=payload,
            timeout=30  # Timeout de 30 segundos
        )
        
        # Registra a resposta recebida para debug
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body: {response.text}")
        
        # Verifica se houve erro na requisição
        response.raise_for_status()
        response_json = response.json()
        
        # Extrai o conteúdo da resposta do modelo
        if "choices" in response_json and len(response_json["choices"]) > 0:
            content = response_json["choices"][0]["message"]["content"]
            print(f"Extracted content: {content}")
            return content
        else:
            print(f"Unexpected response format: {response_json}")
            return "Error: Unexpected response format"
            
    except requests.exceptions.Timeout:
        # Trata erro de timeout
        print(f"Timeout error querying {model}")
        return f"Error: Request timeout for {model}"
    except Exception as e:
        # Trata outros erros
        print(f"Error querying {model}: {str(e)}")
        print(f"Exception type: {type(e)}")
        if isinstance(e, requests.exceptions.RequestException):
            print(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}")
        return f"Error: Failed to get response from {model}"

def normalize_response(response: str) -> str:
    """
    Normaliza a resposta removendo espaços extras no início e fim.
    Retorna string vazia se a resposta for None.
    
    Args:
        response: Texto a ser normalizado
        
    Returns:
        Texto normalizado
    """
    if not response:
        return ""
    
    return response.strip()

def combine_responses(responses: List[Dict[str, str]]) -> str:
    """
    Combina múltiplas respostas de diferentes modelos.
    Atualmente seleciona a resposta mais longa como a melhor.
    
    Args:
        responses: Lista de dicionários contendo as respostas dos modelos
        
    Returns:
        Resposta combinada ou mensagem de erro
    """
    if not responses:
        return "No responses available."
    
    # Filtra apenas respostas válidas (não vazias e sem erros)
    valid_responses = [r for r in responses if r["response"].strip() and not r["response"].startswith("Error:")]
    
    if not valid_responses:
        return "No valid responses available."
    
    # Seleciona a resposta mais longa como a melhor
    best_response = max(valid_responses, key=lambda x: len(x["response"]))
    
    # Limita a resposta a 500 caracteres
    return best_response["response"][:500].strip()

# =============================================================================
# MÓDULO DE ROTEAMENTO HTTP - ENDPOINTS DA API
# =============================================================================

@app.post("/generate")
async def generate_response(request: PromptRequest):
    """
    Endpoint principal que recebe o prompt, consulta vários modelos
    e retorna uma resposta combinada.
    
    Args:
        request: Objeto PromptRequest contendo os dados da requisição
        
    Returns:
        Dicionário com a resposta combinada
        
    Raises:
        HTTPException: Em caso de erro no processamento
    """
    try:
        prompt = request.prompt
        api_key = request.api_key
        # Usa modelos padrão se nenhum for especificado
        models = request.models or DEFAULT_MODELS

        responses = []
        
        # Consulta cada modelo e coleta as respostas
        for model in models:
            response = await query_model(prompt, model, api_key)
            responses.append({
                "model": model,
                "response": normalize_response(response)
            })

        # Combina as respostas dos diferentes modelos
        combined_response = combine_responses(responses)

        return {"combined_response": combined_response}
    except Exception as e:
        # Trata erros gerais na execução do endpoint
        print(f"Error in generate_response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# =============================================================================
# PONTO DE ENTRADA DA APLICAÇÃO
# =============================================================================

# Ponto de entrada para execução direta do script
if __name__ == "__main__":
    import uvicorn
    # Inicia o servidor uvicorn para servir a API
    uvicorn.run(app, host="0.0.0.0", port=8000)

