# Plano de Desenvolvimento: Sistema ATS Local com Ollama Cloud

Este documento serve como o **Guia de Implementação e Especificação Técnica** para o Engenheiro de Software Fullstack responsável por construir o Sistema ATS Local. O plano foi elaborado pelo Product Manager (PM) e Tech Lead do projeto, detalhando a arquitetura, regras de negócio, padrões de código e o passo a passo para a execução.

---

## 1. Visão de Produto (PM)

O objetivo deste projeto é fornecer uma ferramenta de desktop local extremamente rápida, segura e visualmente deslumbrante para análise de currículos baseada em inteligência artificial.

### 1.1 Objetivos de UX
- **Sem Recarregamento de Página**: Toda a interação deve ocorrer de forma fluida em uma única página usando **HTMX** para atualizar dinamicamente a área de upload para a área de resultados.
- **Validação Antecipada (Zero Cliques Inválidos)**: O usuário não deve conseguir clicar em "Analisar" sem preencher os requisitos mínimos, proporcionando feedback instantâneo.
- **Identidade Visual Marcante**: Design premium voltado para tons de verde metálico e esmeralda. Sensação de uma ferramenta profissional avançada de recrutamento.
- **Privacidade de Dados**: Como se trata de um sistema local para macOS, nenhum dado sensível deve vazar ou ser transmitido para redes de terceiros fora da API oficial Ollama Cloud contratada.

---

## 2. Especificação Arquitetural e de Engenharia (Tech Lead)

### 2.1 Por que essa Stack?
- **Python 3.11.7 + FastAPI**: A combinação perfeita de alto desempenho assíncrono para operações de E/S (como chamadas de rede à Ollama Cloud) e tipagem rigorosa para evitar falhas em tempo de execução.
- **Jinja2 + HTMX**: Dispensa frameworks SPA pesados (React/Vue/Next.js) que exigem build, reduzindo a complexidade de implantação local ao mínimo e mantendo a renderização baseada no servidor.
- **PyMuPDF**: Biblioteca Python extremamente robusta e veloz para extração e reconstrução de layouts lógicos de PDFs, ideal para que o modelo ATS leia os currículos exatamente como foram estruturados.
- **asyncio.to_thread**: Uma vez que o SDK `ollama-python` realiza chamadas síncronas bloqueantes, **é obrigatório** envelopar as chamadas à API no backend usando `asyncio.to_thread()` para evitar o congelamento do loop de eventos do FastAPI sob concorrência ou espera.

### 2.2 Requisitos Não-Funcionais Críticos
1. **Controle de Payload**: Limite estrito de **10MB** para arquivos de currículo. Validação tanto client-side quanto server-side.
2. **Resiliência de Rede**: Timeout do cliente Ollama fixado em **60 segundos** com tratamento robusto de erros e exibição de alerta em tom de erro (`#C0392B`).
3. **Padrão de Resposta da IA**: Retorno 100% estruturado em JSON validado via Pydantic v2.

---

## 3. Estrutura do Projeto

Os arquivos devem ser organizados exatamente como a estrutura a seguir. Não crie arquivos fora desse padrão:

```text
ats-analyzer/
├── requirements.txt        # Dependências fixadas com versões
├── .env                    # Variáveis de ambiente (OLLAMA_API_KEY)
├── .gitignore              # Proteção de credenciais e caches
├── main.py                 # Ponto de entrada do FastAPI (rotas e ciclo de vida)
├── core/
│   ├── __init__.py
│   ├── pdf_parser.py       # Módulo de extração de PDF via PyMuPDF
│   ├── ollama_client.py    # Cliente configurado para a Ollama Cloud
│   ├── ats_engine.py       # Orquestração da chamada LLM e prompts
│   └── schemas.py          # Validação de dados de entrada/saída via Pydantic
├── templates/
│   ├── base.html           # Template principal (inclui estilos globais e scripts)
│   ├── upload.html         # Fragmento/Tela 1: Formulário de ingestão
│   └── results.html        # Fragmento/Tela 2: Exibição da análise detalhada
├── prompts/
│   └── ats_system.txt      # Instruções de sistema e restrições da IA
└── static/
    ├── styles.css          # Estilos complementares e transições
    └── form-validation.js  # Lógica Javascript pura de validação interativa
```

---

## 4. Guia de Implementação Passo a Passo (Checklist)

O dev deve seguir esta ordem cronológica para construir e validar o sistema:

### [ ] Fase 1: Setup Inicial e Configuração de Ambiente
1. Criar o ambiente virtual com `python -m venv .venv` e ativá-lo.
2. Criar e preencher o arquivo `requirements.txt` com as dependências especificadas nas diretrizes.
3. Criar `.gitignore` para garantir que `.env`, `.venv`, e `__pycache__` nunca sejam versionados.
4. Criar o arquivo `.env` contendo a chave `OLLAMA_API_KEY`.

### [ ] Fase 2: Desenvolvimento do Módulo Core (Backend)
1. **`core/pdf_parser.py`**:
   - Implementar função `extract_text_from_pdf(file_bytes: bytes) -> str`.
   - Utilizar PyMuPDF (`fitz`) para ler cada página e extrair texto limpo.
   - Tratar exceções de arquivos corrompidos ou PDFs sem texto (imagens), retornando uma mensagem de erro adequada.
2. **`core/ollama_client.py`**:
   - Configurar o cliente `ollama.Client` apontando para o host da Ollama Cloud (`https://ollama.com`) passando o token `OLLAMA_API_KEY` nos cabeçalhos como `Bearer {api_key}`.
   - Adicionar validação no carregamento para lançar exceção se a API key estiver em branco.
3. **`core/schemas.py`**:
   - Definir a classe `ATSAnalysis(BaseModel)` herdando de Pydantic v2.
   - Atributos requeridos: `score: int` (0 a 100), `strengths: list[str]`, `weaknesses: list[str]`, e `suggestions: str`.
4. **`core/ats_engine.py`**:
   - Implementar `async def analyze_resume(client: Client, job_desc: str, resume_text: str) -> dict`.
   - Ler o prompt de sistema a partir de `prompts/ats_system.txt`.
   - Chamar o modelo `minimax-m2.5:cloud` assincronamente usando `asyncio.to_thread(client.chat, ...)` com o parâmetro `format='json'`.
   - Retornar o conteúdo JSON decodificado.

### [ ] Fase 3: Prompts e Orquestração de IA
1. **`prompts/ats_system.txt`**:
   - Escrever o prompt de sistema em Português do Brasil.
   - Definir o papel técnico da IA (especialista em ATS).
   - Exigir resposta estritamente no formato JSON que case com o schema do Pydantic.
   - Adicionar diretriz clara de que a pontuação deve se basear puramente no alinhamento de habilidades técnicas e semânticas, não no visual do currículo.

### [ ] Fase 4: Servidor FastAPI (`main.py`)
1. Instanciar a aplicação FastAPI com suporte a arquivos estáticos (`static/`) e Jinja2 templates.
2. Implementar evento de inicialização (`lifespan`) para verificar se a variável `OLLAMA_API_KEY` está presente, falhando rapidamente caso contrário.
3. Implementar a rota `GET /` que serve o template `upload.html` injetado no `base.html`.
4. Implementar a rota `POST /analyze` que:
   - Recebe `job_description` (form text) e `resume_file` (UploadFile).
   - Valida server-side: tamanho do arquivo (< 10MB) e formato (deve ser PDF).
   - Extrai o texto do currículo com `pdf_parser`.
   - Invoca o `ats_engine` assincronamente.
   - Valida o retorno do modelo contra o schema Pydantic `ATSAnalysis`.
   - Retorna o fragmento HTML `results.html` para ser injetado pelo HTMX no frontend.
   - Inclui blocos `try/except` robustos para renderizar mensagens de erro amigáveis no frontend (usando cor `#C0392B`) sem derrubar a aplicação.

### [ ] Fase 5: Design do Sistema e Frontend (CSS / Templates)
1. **`templates/base.html`**:
   - Configurar tags HTML5 semânticas e estrutura responsiva.
   - Carregar Tailwind CSS via CDN se solicitado (não recomendado pelas diretrizes, priorizar CSS customizado e inline ou no `static/styles.css`).
   - Carregar a biblioteca **HTMX** de forma segura.
   - Configurar o layout geral com fundo Verde Metálico Escuro (`#1A2F23`).
2. **`static/styles.css`**:
   - Definir variáveis CSS globais com a paleta exata fornecida:
     - `--bg-primary: #1A2F23;`
     - `--bg-surface: #243B2D;`
     - `--text-primary: #E0F2E9;`
     - `--text-secondary: #8FA89A;`
     - `--accent-active: #2ECC71;`
     - `--accent-disabled: #3D4F45;`
     - `--border-subtle: #2F4A38;`
     - `--color-error: #C0392B;`
   - Configurar a transição CSS suave do botão `button` para 200ms `ease`.
   - Estilizar os inputs, textarea, barra de carregamento e cards de resultados.
3. **`static/form-validation.js`**:
   - Implementar a escuta de eventos nos campos `job-description` (textarea) e `resume-file` (file).
   - Habilitar/desabilitar o botão de submissão e gerenciar classes visuais com base nas regras de validação client-side.
4. **`templates/upload.html`**:
   - Construir o formulário integrado com HTMX:
     - `hx-post="/analyze"`
     - `hx-target="#content-area"`
     - `hx-swap="innerHTML"`
     - `hx-indicator="#loading-spinner"`
     - `enctype="multipart/form-data"`
   - Adicionar o contador visual de caracteres no textarea.
   - Adicionar o elemento indicador de carregamento (`#loading-spinner`), inicialmente oculto.
5. **`templates/results.html`**:
   - Exibir a pontuação final com uma barra de progresso colorida dinamicamente (Verde Esmeralda se ≥ 70, Verde Muted se < 70).
   - Renderizar pontos fortes (`strengths`) e fracos (`weaknesses`) em layouts limpos e com ícones adequados.
   - Renderizar as sugestões convertendo Markdown em HTML puro (usando a biblioteca `markdown` no Jinja2 ou filtro personalizado no FastAPI).
   - Botão para reiniciar a análise com HTMX que recarrega a tela de upload sem reload completo da página.

---

## 5. Arquitetura Detalhada de Código e Snippets de Referência

O engenheiro de software deve basear sua codificação nos seguintes padrões:

### 5.1 PDF Parser (`core/pdf_parser.py`)
```python
import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        
        cleaned_text = " ".join(text.split())
        if not cleaned_text.strip():
            raise ValueError("O PDF não contém texto extraível legível.")
            
        return cleaned_text
    except Exception as e:
        raise ValueError(f"Falha ao extrair texto do PDF: {str(e)}")
```

### 5.2 Schemas de Validação (`core/schemas.py`)
```python
from pydantic import BaseModel, Field

class ATSAnalysis(BaseModel):
    score: int = Field(ge=0, le=100, description="Pontuação ATS de 0 a 100 baseado na correspondência semântica e de habilidades.")
    strengths: list[str] = Field(description="Pontos fortes identificados no currículo alinhados à vaga.")
    weaknesses: list[str] = Field(description="Pontos fracos, lacunas de habilidades ou áreas não mencionadas.")
    suggestions: str = Field(description="Sugestões práticas de melhoria formatadas em Markdown.")
```

### 5.3 Validação de Arquivo no FastAPI (`main.py`)
```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from core.pdf_parser import extract_text_from_pdf

# Exemplo de validação de tamanho e tipo mime no backend
async def validate_and_parse_pdf(file: UploadFile) -> str:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas PDF é permitido.")
    
    # Limitar leitura em memória para 10MB
    max_size = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=400, detail="O arquivo PDF excede o limite de tamanho de 10MB.")
        
    return extract_text_from_pdf(content)
```

---

## 6. Plano de Testes e Critérios de Aceite (Tech Lead)

### 6.1 Critérios de Aceite Funcionais
1. O formulário não deve permitir submissão se a descrição tiver menos de 50 caracteres ou nenhum PDF estiver carregado.
2. PDFs corrompidos ou protegidos por senha devem retornar um erro visual limpo na tela na cor `#C0392B` (sem expor traceback interno).
3. A barra de carregamento ou "spinner" de processamento HTMX deve aparecer no exato instante do clique e sumir apenas quando os resultados forem renderizados.
4. O score >= 70 deve pintar a barra de progresso em verde esmeralda (`#2ECC71`); scores inferiores a 70 devem exibir cor verde muted (`#8FA89A`).

### 6.2 Critérios de Aceite Técnicos e de Segurança
1. A rota `/analyze` deve validar rigorosamente o tamanho do arquivo no servidor.
2. A integração com o Ollama Cloud deve utilizar `asyncio.to_thread` garantindo a não-bloqueabilidade da aplicação.
3. Não há vazamento de chaves de API: o arquivo `.env` não é enviado ao repositório e o servidor avisa no log caso a chave não esteja presente no startup.
4. Conformidade WCAG AA nas cores para que o texto `#E0F2E9` no fundo `#1A2F23` possua legibilidade impecável.

---

Este plano de desenvolvimento detalha exatamente como o sistema deve ser construído de ponta a ponta. Proceder para a escrita e desenvolvimento seguindo cada especificação descrita.
