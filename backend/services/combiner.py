import nest_asyncio
import os
from typing import Dict, Optional, Generator
from textwrap import dedent
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

nest_asyncio.apply()

def create_agent(
    system_prompt: str = "Você é um assistente prestativo.",
    model_name: str = "llama3-8b-8192",
    **llm_kwargs
) -> RunnableSerializable[Dict, str]:
    """Cria uma cadeia de conversação com o modelo de linguagem especificado."""
    # O {helper_response} foi removido do prompt do sistema padrão para maior simplicidade.
    # Ele será usado especificamente para o agente sintetizador.
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages", optional=True),
        ("human", "{input}")
    ])
    llm = ChatGroq(model=model_name, **llm_kwargs)
    chain = prompt | llm | StrOutputParser()
    return chain

def format_synthesizer_prompt(
    inputs: Dict[str, str]
) -> str:
    """Formata as respostas dos modelos para o prompt do agente sintetizador."""
    
    # Este prompt instrui o modelo final sobre como agir.
    synthesis_prompt_template = dedent("""
    Você é um assistente especialista em sintetizar informações. Você recebeu uma pergunta de um usuário e múltiplas respostas de diferentes assistentes de IA.
    Sua tarefa é analisar criticamente todas as respostas, identificar os pontos fortes e as informações corretas de cada uma, e combiná-las em uma única resposta final, coesa e abrangente.
    Ignore qualquer informação contraditória ou incorreta. Sua resposta final deve ser a melhor versão possível, respondendo diretamente à pergunta original do usuário.

    Respostas dos modelos para sua avaliação:
    {responses}
    """)

    # Formata as respostas individuais para serem incluídas no prompt.
    formatted_responses = ""
    for model_name, response_text in inputs.items():
        formatted_responses += f"--- Resposta do modelo '{model_name}' ---\n{response_text}\n\n"

    return synthesis_prompt_template.format(responses=formatted_responses)

# Memória para manter o contexto da conversa final
CHAT_MEMORY = ConversationBufferMemory(
    memory_key="messages",
    return_messages=True
)

# O Agente Sintetizador. Usamos um modelo poderoso para a tarefa de combinar.
# Llama 3 70B é uma excelente escolha para raciocínio e síntese.
SYNTHESIZER_AGENT = create_agent(
    model_name="llama-3.3-70b-versatile",
    system_prompt="{helper_response}", # O prompt do sistema será o nosso template de síntese.
    temperature=0.2, # Uma temperatura baixa para manter o foco na tarefa.
)

def chat_stream(query: str, models: list) -> Generator[str, None, None]:
    """
    Função principal de chat. Coleta respostas e as sintetiza em uma resposta final.
    """
    # Se menos de dois modelos forem selecionados, a síntese não faz sentido.
    # Neste caso, apenas executamos o primeiro modelo selecionado.
    if len(models) < 2:
        model_to_run = models[0] if models else "llama3-8b-8192" # Modelo padrão se nenhum for escolhido
        yield f"--- Executando um único modelo: {model_to_run} ---\n\n"
        agent = create_agent(model_name=model_to_run)
        llm_input = {
            'input': query,
            'messages': CHAT_MEMORY.load_memory_variables({})['messages']
        }
        final_response = ""
        for chunk in agent.stream(llm_input):
            final_response += chunk
            yield chunk
        CHAT_MEMORY.save_context({'input': query}, {'output': final_response})
        return

    # --- Lógica Principal de Síntese ---
    
    # 1. Coleta as respostas completas de todos os modelos selecionados.
    initial_responses: Dict[str, str] = {}
    print(f"Coletando respostas de: {models}")
    for model in models:
        # Criamos um agente simples para cada modelo.
        agent = create_agent(model_name=model, system_prompt="Responda diretamente à pergunta do usuário.")
        llm_input = {'input': query, 'messages': []} # Não usamos memória para os agentes individuais.
        
        # Usamos .invoke() para obter a resposta completa, em vez de .stream().
        response = agent.invoke(llm_input)
        initial_responses[model] = response
        print(f"Recebida resposta de: {model}")

    # 2. Prepara o prompt para o agente sintetizador com as respostas coletadas.
    print("Sintetizando respostas...")
    synthesizer_prompt_context = format_synthesizer_prompt(initial_responses)
    
    # 3. Executa o agente sintetizador e transmite a resposta final.
    synthesizer_input = {
        'input': query,
        'messages': CHAT_MEMORY.load_memory_variables({})['messages'],
        'helper_response': synthesizer_prompt_context # Injeta as respostas no prompt do sistema.
    }

    yield "--- Resposta Combinada e Refinada ---\n\n"
    final_synthesized_response = ""
    for chunk in SYNTHESIZER_AGENT.stream(synthesizer_input):
        final_synthesized_response += chunk
        yield chunk
    
    # 4. Salva o contexto final na memória.
    CHAT_MEMORY.save_context({'input': query}, {'output': final_synthesized_response})


def start_cli():
    """Função para iniciar a interface de linha de comando."""
    # (a lógica do CLI continua a mesma)
    while True:
        inp = input("\nFaça uma pergunta: ")
        print(f"\nUsuário: {inp}")
        if inp.lower() == "sair":
            print("\nInterrompido pelo Usuário\n")
            break
        # Exemplo de uso no CLI com dois modelos para teste
        stream = chat_stream(inp, ["llama3-8b-8192", "gemma2-9b-it"])
        print(f"IA: ", end="")
        for chunk in stream:
            print(chunk, end="", flush=True)

def get_available_models():
    """Lê os modelos disponíveis de um arquivo de texto."""
    try:
        with open("models.txt") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        # Retorna uma lista padrão se o arquivo não for encontrado.
        return ["llama-3.3-70b-versatile", "llama3-8b-8192", "gemma2-9b-it"]
