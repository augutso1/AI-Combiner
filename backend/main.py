import nest_asyncio
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Importações relativas para funcionar com a estrutura de pacotes
from .api import routes as api_router
from .services import combiner

# Carrega a chave de API do arquivo .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

nest_asyncio.apply()

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(api_router.router)

# Monta o diretório 'frontend' na raiz. 
# Esta deve ser a última montagem para não sobrepor as rotas da API.
# O caminho é relativo ao diretório raiz do projeto.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# Lógica para iniciar o servidor ou o modo CLI
if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Verifica se o modo CLI foi solicitado
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        combiner.start_cli()
    else:
        print("Iniciando servidor web. Acesse http://localhost:8000")
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
