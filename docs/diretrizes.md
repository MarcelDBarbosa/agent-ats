# Diretrizes Técnicas: Sistema ATS Local com Ollama Cloud

## 1. Visão Geral do Projeto

Desenvolver um sistema web local para macOS que atua como um analisador de currículos baseado em ATS (Applicant Tracking System). O sistema deve processar PDFs de currículos, compará-los com descrições de vagas e retornar uma análise estruturada via modelo `minimax-m2.5:cloud` hospedado no Ollama Cloud. A interface será dividida em duas telas: ingestão de dados e apresentação de resultados, com identidade visual em tons de verde metálico e validação interativa de formulário.

## 2. Stack Tecnológica

-   **Linguagem:** Python 3.11.7
    -   Justificativa: Versão estável e compatível com todas as bibliotecas necessárias, alinhada ao ambiente já configurado no macOS.
-   **Framework Web:** FastAPI
    -   Justificativa: Performance assíncrona nativa, ideal para chamadas à API cloud sem bloqueio; tipagem forte via Pydantic integrada; ecossistema maduro para APIs JSON.
-   **Frontend:** Jinja2 + HTMX + Vanilla JS
    -   Justificativa: Renderização server-side leve, interatividade dinâmica sem SPA framework, integração nativa com FastAPI e simplicidade para sistemas locais de duas telas. Vanilla JS para validação client-side em tempo real.
-   **Extração de PDF:** PyMuPDF (`pymupdf`)
    -   Justificativa: Reconstrução fiel do fluxo de leitura e estrutura lógica, essencial para precisão na análise ATS. Superior ao `pdf.js` para extração semântica de documentos complexos.
-   **Integração LLM:** `ollama-python` (configurado para endpoint cloud)
-   **Validação de Dados:** Pydantic v2 (nativo do FastAPI)
-   **Gerenciador de Pacotes:** pip
    -   Uso obrigatório de `requirements.txt` versionado e ambiente virtual isolado (`venv`).

## 3. Identidade Visual e Paleta de Cores

### 3.1 Paleta Definida

| Função               | Cor       | Código Hex | Notas                                  |
| :------------------- | :-------- | :--------- | :------------------------------------- |
| Fundo Principal      | Verde Metálico Escuro | `#1A2F23`  | Base da página, tom profundo e sóbrio  |
| Superfície/Cards     | Verde Escuro Mate     | `#243B2D`  | Contraste sutil contra o fundo         |
| Texto Primário       | Verde Claro Gelo      | `#E0F2E9`  | Alta legibilidade sobre fundo escuro   |
| Texto Secundário     | Verde Muted           | `#8FA89A`  | Labels, placeholders, metadados        |
| Acento/Botão Ativo   | Verde Esmeralda Vivo  | `#2ECC71`  | Ação primária, estado habilitado       |
| Botão Desativado     | Verde Acinzentado     | `#3D4F45`  | Estado inerte, sem interação           |
| Bordas/Divisores     | Verde Sutil           | `#2F4A38`  | Separação discreta de elementos        |
| Erro/Alerta          | Vermelho Suave        | `#C0392B`  | Contraste acessível sobre verde escuro |

### 3.2 Diretrizes de Aplicação

-   O fundo verde metálico escuro (`#1A2F23`) deve ser aplicado no `body` e em todos os containers raiz.
-   Cards de resultados e campos de formulário utilizam a cor de superfície (`#243B2D`) com borda sutil (`#2F4A38`).
-   O botão "Analisar" deve transitar suavemente entre os estados desativado (`#3D4F45`, cursor `not-allowed`) e ativo (`#2ECC71`, cursor `pointer`) com transição CSS de 200ms.
-   Garantir contraste WCAG AA mínimo de 4.5:1 entre texto e fundo em todas as combinações.
-   Evitar gradientes ou efeitos brilhantes; manter estética mate/metálica consistente.

## 4. Estrutura de Arquivos

```text
ats-analyzer/
├── requirements.txt        # Dependências fixadas com versões
├── .env                    # OLLAMA_API_KEY=chave_aqui
├── .gitignore              # Deve incluir .env, __pycache__, .venv
├── main.py                 # Entry point FastAPI (rotas e middlewares)
├── core/
│   ├── __init__.py
│   ├── pdf_parser.py       # Extração e limpeza de texto via PyMuPDF
│   ├── ollama_client.py    # Encapsulamento da conexão com Ollama Cloud
│   ├── ats_engine.py       # Lógica de negócio, prompt assembly e parsing
│   └── schemas.py          # Modelos Pydantic para requisição/resposta
├── templates/
│   ├── base.html           # Layout base com paleta, HTMX e CSS inline
│   ├── upload.html         # Tela 1: Formulário com validação em tempo real
│   └── results.html        # Tela 2: Apresentação da análise
├── prompts/
│   └── ats_system.txt      # Prompt template versionado externamente
└── static/
    ├── styles.css          # Estilos customizados complementares
    └── form-validation.js  # Lógica de ativação do botão
```

## 5. Validação Interativa do Formulário

### 5.1 Regras de Ativação do Botão

O botão "Analisar" deve permanecer **desativado** até que ambas as condições sejam satisfeitas simultaneamente:

1.  Campo de descrição da vaga contém pelo menos 50 caracteres não-brancos.
2.  Arquivo PDF foi selecionado e possui tamanho > 0 bytes.

### 5.2 Implementação (`static/form-validation.js`)

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const jobField = document.getElementById('job-description');
    const fileInput = document.getElementById('resume-file');
    const submitBtn = document.getElementById('analyze-btn');

    function validateForm() {
        const hasJobText = jobField.value.trim().length >= 50;
        const hasFile = fileInput.files.length > 0 && fileInput.files[0].size > 0;
        submitBtn.disabled = !(hasJobText && hasFile);
    }

    jobField.addEventListener('input', validateForm);
    fileInput.addEventListener('change', validateForm);

    // Estado inicial
    validateForm();
});
```

### 5.3 Integração com HTML (`templates/upload.html`)

-   Botão renderizado com atributo `disabled` por padrão (segurança progressiva).
-   Classes CSS condicionais aplicadas via JS para estilização dos estados.
-   Feedback visual opcional: contador de caracteres abaixo do campo de vaga indicando progresso até 50 caracteres.
-   Validação server-side no FastAPI permanece obrigatória como camada de segurança; a validação client-side é exclusivamente para UX.

## 6. Especificações de Integração Ollama Cloud

### 6.1 Configuração do Cliente (`core/ollama_client.py`)

```python
import os
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

def get_ollama_client() -> Client:
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        raise ValueError("OLLAMA_API_KEY não encontrada. Verifique o arquivo .env")

    return Client(
        host="https://ollama.com",
        headers={"Authorization": f"Bearer {api_key}"}
    )
```

### 6.2 Chamada de Análise Assíncrona (`core/ats_engine.py`)

> **Nota Crítica:** Como o FastAPI é assíncrono e a biblioteca `ollama-python` é síncrona, encapsule a chamada em `asyncio.to_thread()` para evitar bloqueio do event loop durante a espera pela API cloud.

```python
import asyncio
from ollama import Client

async def analyze_resume(client: Client, job_desc: str, resume_text: str) -> dict:
    response = await asyncio.to_thread(
        client.chat,
        model='minimax-m2.5:cloud',
        messages=[
            {'role': 'system', 'content': open('prompts/ats_system.txt').read()},
            {'role': 'user', 'content': f"VAGA:\n{job_desc}\n\nCURRÍCULO:\n{resume_text}"}
        ],
        format='json'
    )
    return response.message.content
```

### 6.3 Schema de Resposta Esperado (`core/schemas.py`)

```python
from pydantic import BaseModel, Field

class ATSAnalysis(BaseModel):
    score: int = Field(ge=0, le=100, description="Pontuação ATS de 0 a 100")
    strengths: list[str] = Field(description="Pontos positivos do currículo")
    weaknesses: list[str] = Field(description="Pontos negativos ou gaps")
    suggestions: str = Field(description="Sugestões detalhadas de melhoria")
```

## 7. Especificações Funcionais das Telas

### Tela 1: Ingestão de Dados (`templates/upload.html`)

-   Formulário HTML com `enctype="multipart/form-data"` submetido via POST para `/analyze`.
-   Campo de texto para descrição da vaga (`textarea`, máximo 4000 tokens, mínimo 50 caracteres para ativação).
-   Input de arquivo aceitando exclusivamente `.pdf`, máximo 10MB.
-   Botão "Analisar" inicialmente desativado, ativado dinamicamente via JS conforme seção 5.
-   Indicador de carregamento via HTMX `hx-indicator` durante submissão.
-   Contador de caracteres visuais abaixo do campo de vaga.

### Tela 2: Resultados (`templates/results.html`)

-   Score ATS exibido como barra de progresso colorida conforme paleta (verde esmeralda para ≥70, verde muted para <70).
-   Listas separadas para pontos positivos e negativos com ícones distintivos.
-   Bloco de sugestões com renderização markdown (usar filtro Jinja2 ou biblioteca `markdown`).
-   Botão "Nova Análise" que redireciona para a tela inicial limpando estado.
-   Transição entre telas via HTMX (`hx-target`, `hx-swap`) sem reload completo.
-   Todos os elementos respeitam a paleta de cores definida na seção 3.

### Rotas FastAPI (`main.py`)

-   `GET /` → Renderiza `upload.html`.
-   `POST /analyze` → Recebe formulário, valida server-side, extrai PDF, chama IA, retorna `results.html` como fragmento HTMX.
-   Middleware de validação de API Key no startup (evento `lifespan`).

## 8. Requisitos Não-Funcionais

### Latência e UX

-   Utilizar `asyncio.to_thread()` obrigatoriamente para chamadas ao Ollama Cloud.
-   Configurar timeout de 60s no cliente Ollama.
-   Exibir indicador de carregamento durante toda a operação (extração + inferência).
-   Transições de estado do botão devem ser suaves (200ms ease).

### Tratamento de Erros

-   Validar resposta JSON via Pydantic dentro de bloco `try/except`.
-   Em caso de falha, retornar fragmento HTML com mensagem amigável via HTMX, estilizada com cor de erro da paleta.
-   Log de erros no console do servidor para debugging, nunca expor ao frontend.

### Segurança

-   API Key exclusivamente via `.env`, nunca hardcoded.
-   `.env` obrigatoriamente no `.gitignore`.
-   Validar tipo MIME e tamanho do arquivo no backend, não confiar apenas em validação client-side.
-   Nenhum dado trafega para serviços externos além da API Ollama Cloud autorizada.

## 9. Diretrizes de Prompt (`prompts/ats_system.txt`)

O prompt deve conter:

1.  Definição de papel: "Você é um especialista sênior em ATS e recrutamento técnico."
2.  Instrução explícita: "Responda EXCLUSIVAMENTE com JSON válido, sem texto adicional."
3.  Schema JSON esperado como exemplo few-shot.
4.  Diretriz de avaliação: "Baseie a pontuação exclusivamente em correspondência técnica e semântica entre vaga e currículo. Não considere formatação estética."
5.  Idioma de resposta: Português do Brasil.

## 10. Dependências (`requirements.txt`)

```text
fastapi==0.115.*
uvicorn[standard]==0.34.*
python-dotenv==1.0.*
pymupdf==1.25.*
ollama==0.4.*
pydantic==2.10.*
jinja2==3.1.*
python-multipart==0.0.*
markdown==3.7.*
```

> **Nota:** Fixar versões mínimas compatíveis com Python 3.11.7. Executar `pip install -r requirements.txt` dentro de ambiente virtual isolado.