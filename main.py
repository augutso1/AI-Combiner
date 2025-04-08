import nest_asyncio
import os
from typing import Dict, Optional, Generator
from textwrap import dedent
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =============================================================================
# CONFIGURAÇÃO INICIAL
# =============================================================================

os.environ["GROQ_API_KEY"] = "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"

# Aplica o asyncio para permitir execução em notebooks Jupyter
nest_asyncio.apply()

# Cria a aplicação FastAPI
app = FastAPI()

# Configura o CORS para permitir requisições de diferentes origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo para a requisição de chat
class ChatRequest(BaseModel):
    query: str

# Configura os arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# =============================================================================
# DEFINIÇÃO DOS AGENTES E FUNÇÕES AUXILIARES
# =============================================================================

# Método auxiliar para criar uma cadeia LCEL (LangChain Expression Language)
def create_agent(
    system_prompt: str = "Você é um assistente prestativo.\n{helper_response}",
    model_name: str = "llama3-8b-8192",
    **llm_kwargs
) -> RunnableSerializable[Dict, str]:
    """Cria um agente simples de cadeia LCEL (LangChain Expression Language) baseado em um prompt de sistema"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages", optional=True),
        ("human", "{input}")
    ])

    assert 'helper_response' in prompt.input_variables, "{helper_response} variável de prompt não encontrada. Por favor, adicione-a" # Para garantir que podemos adicionar saídas do agente de camada no prompt
    llm = ChatGroq(model=model_name, **llm_kwargs)
    
    chain = prompt | llm | StrOutputParser()
    return chain

def concat_response(
    inputs: Dict[str, str],
    reference_system_prompt: Optional[str] = None
) -> str:
    """Concatena e formata as respostas dos agentes de camada"""

    REFERENCE_SYSTEM_PROMPT = dedent("""\
    Você recebeu um conjunto de respostas de vários modelos de código aberto para a consulta mais recente do usuário.
    Sua tarefa é sintetizar essas respostas em uma única resposta de alta qualidade.
    É crucial avaliar criticamente as informações fornecidas nessas respostas, reconhecendo que algumas delas podem ser tendenciosas ou incorretas.
    Sua resposta não deve simplesmente replicar as respostas dadas, mas oferecer uma resposta refinada, precisa e abrangente à instrução.
    Certifique-se de que sua resposta seja bem estruturada, coerente e atenda aos mais altos padrões de precisão e confiabilidade.
    Respostas dos modelos:
    {responses}
    """)
    reference_system_prompt = reference_system_prompt or REFERENCE_SYSTEM_PROMPT

    assert "{responses}" in reference_system_prompt, "{responses} variável de prompt não encontrada no prompt. Por favor, adicione-a"
    responses = ""
    res_list = []
    for i, out in enumerate(inputs.values()):
        responses += f"{i}. {out}\n"
        res_list.append(out)

    formatted_prompt = reference_system_prompt.format(responses=responses)
    return formatted_prompt

# =============================================================================
# CONFIGURAÇÃO DOS AGENTES E HIPERPARÂMETROS
# =============================================================================

# Hiperparâmetros do agente
# Execute novamente se quiser apagar as conversas
CHAT_MEMORY = ConversationBufferMemory(
    memory_key="messages",
    return_messages=True
)
CYCLES = 3
LAYER_AGENT = ( # Cada agente de camada neste dicionário é executado em paralelo
    {
        'layer_agent_1': RunnablePassthrough() | create_agent(
            system_prompt="Você é um agente planejador especialista. Divida e planeje como você pode responder à pergunta do usuário {helper_response}",
            model_name='llama3-8b-8192'
        ),
        'layer_agent_3': RunnablePassthrough() | create_agent(
            system_prompt="Pense na sua resposta passo a passo. {helper_response}",
            model_name='gemma2-9b-it'
        ),
        # Adicione/Remova agentes conforme necessário...
    }
    |
    RunnableLambda(concat_response) # Formata as saídas dos agentes de camada
)

MAIN_AGENT = create_agent(
    system_prompt="Você é um assistente prestativo.\n{helper_response}",
    model_name="llama3-70b-8192",
    temperature=0.1,
)

# =============================================================================
# LÓGICA DE FLUXO DE CONVERSA - PIPELINE DE GERAÇÃO E GERENCIAMENTO DE CONTEXTO
# =============================================================================

def chat_stream(query: str) -> Generator[str, None, None]:
    """Executa o pipeline de Mistura de Agentes LCEL (LangChain Expression Language)"""

    llm_inp = {
    'input': query,
    'messages': CHAT_MEMORY.load_memory_variables({})['messages'],
    'helper_response': ""
    }
    for _ in range(CYCLES):
        llm_inp = {
            'input': query,
            'messages': CHAT_MEMORY.load_memory_variables({})['messages'],
            'helper_response': LAYER_AGENT.invoke(llm_inp)
        }

    response = ""
    for chunk in MAIN_AGENT.stream(llm_inp):
        yield chunk
        response += chunk
    
    # Salva a resposta na memória
    CHAT_MEMORY.save_context({'input': query}, {'output': response})

# =============================================================================
# ENDPOINTS DA API FASTAPI
# =============================================================================

@app.get("/")
async def read_root():
    """Redireciona para a interface do usuário"""
    return {"message": "Bem-vindo à API do AI Combiner. Acesse /static/index.html para a interface."}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Endpoint para streaming de respostas de chat"""
    return StreamingResponse(
        chat_stream(request.query),
        media_type="text/plain"
    )

# =============================================================================
# INTERFACE DE LINHA DE COMANDO - PONTO DE ENTRADA DA APLICAÇÃO
# =============================================================================

# Função para interface de linha de comando
def start_cli():
    """Inicia a interface de linha de comando"""
    while True:
        inp = input("\nFaça uma pergunta: ")
        print(f"\nUsuário: {inp}")
        if inp.lower() == "sair":
            print("\nInterrompido pelo Usuário\n")
            break
        stream = chat_stream(inp)
        print(f"IA: ", end="")
        for chunk in stream:
            print(chunk, end="", flush=True)

# Ponto de entrada da aplicação
if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Verifica se há argumento de linha de comando
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Modo de linha de comando
        start_cli()
    else:
        # Modo servidor web
        print("Iniciando servidor web. Acesse http://localhost:8000/static/index.html")
        uvicorn.run(app, host="0.0.0.0", port=8000)