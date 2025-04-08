# AI Response Combiner

Um sistema que combina respostas de múltiplos modelos de IA poderosos através de chamadas API para o serviço Groq. Suporta diversos modelos de última geração e inclui tanto uma interface web quanto uma interface de linha de comando para fácil interação.

## Funcionalidades

- **Modo Web API**: API FastAPI com endpoint REST e interface web
- **Modo Terminal**: Interface de linha de comando para interação direta
- **Modelos Suportados**:
  - Llama 3.3 70B (8192 contexto)
  - Llama 3 8B (8192 contexto)
  - Gemma 2 9B
  - Whisper Large V3 Turbo
  - Distil Whisper Large V3
- **Método de Combinação**: Pipeline LCEL (LangChain Expression Language) com múltiplos ciclos de aprimoramento
- **Memória de Conversação**: Mantém o contexto das interações anteriores
- **Interface Web**: Interface HTML/CSS/JS simples para interagir com a API
- **Interface de Linha de Comando**: Modo interativo para consultas diretas via terminal

## Arquitetura

O projeto está estruturado em dois módulos principais:

- **main.py**: Implementação da API FastAPI para uso via web
- **mixture.py**: Implementação da interface de linha de comando e do sistema de combinação de agentes via LangChain

## Instruções de Configuração

1. **Instalar Python 3.9+**:

   ```bash
   brew install python  # No macOS
   ```

2. **Criar um Ambiente Virtual**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar Dependências**:

   ```bash
   pip install fastapi uvicorn langchain langchain-groq nest_asyncio pydantic
   ```

4. **Configuração**:

   - Configure sua chave de API Groq diretamente no arquivo mixture.py ou main.py:
     ```python
     os.environ["GROQ_API_KEY"] = "sua_chave_api_aqui"
     ```
   - Ou crie um arquivo `.env` com sua chave:
     ```
     GROQ_API_KEY=sua_chave_api_aqui
     ```

## Execução da Aplicação

### Modo Linha de Comando

```bash
python mixture.py
```

Você verá um prompt interativo onde pode fazer perguntas diretamente ao sistema combinado de modelos.

### Modo Servidor Web

```bash
python main.py
```

Acesse a interface web em:

```
http://localhost:8000/static/index.html
```

## Uso da API

Envie uma requisição POST para `/generate` com o seguinte corpo JSON:

```json
{
  "prompt": "Sua pergunta ou instrução aqui",
  "api_key": "sua_chave_api_aqui",
  "models": ["llama-3.3-70b-versatile", "llama3-8b-8192"] // Opcional - usará modelos padrão se não especificado
}
```

Exemplo usando curl:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explique computação quântica",
    "api_key": "sua_chave_api_aqui"
  }'
```

## Funcionamento do Sistema de Combinação (mixture.py)

O sistema utiliza a abordagem LCEL (LangChain Expression Language) para criar um pipeline de agentes que:

1. Processa a entrada do usuário através de vários modelos de IA em paralelo
2. Combina as respostas iniciais em um formato estruturado
3. Usa esse resultado como contexto para um modelo principal gerar a resposta final
4. Mantém o histórico da conversa para contextualização

O sistema executa até 3 ciclos de refinamento para cada consulta, melhorando progressivamente a qualidade da resposta.

## Tratamento de Erros

O sistema inclui tratamento robusto de erros para:

- Problemas de autenticação com a API
- Erros específicos de cada modelo
- Limitação de taxa (rate limiting)
- Problemas de conectividade de rede

Cada erro é devidamente registrado e retornado com códigos de status HTTP apropriados.

## Melhorias Futuras

- Implementar algoritmos mais sofisticados de combinação de respostas
- Adicionar suporte a streaming para respostas em tempo real
- Implementar cache de respostas para perguntas frequentes
- Adicionar ajuste de parâmetros específicos para cada modelo
- Implementar mecanismos de fallback para indisponibilidade de modelos
- Aprimorar a interface web com recursos adicionais
