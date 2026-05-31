# ATS Analyzer

Sistema web local para macOS que atua como um analisador de currículos baseado em ATS (Applicant Tracking System). Processa PDFs de currículos, compara com descrições de vagas e retorna uma análise estruturada via IA generativa hospedada no Ollama Cloud.

![Python](https://img.shields.io/badge/Python-3.11-3776AB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688) ![HTMX](https://img.shields.io/badge/HTMX-2.0-3366CC) ![PyMuPDF](https://img.shields.io/badge/PyMuPDF-1.25-F5792A)

---

## Funcionalidades

- **Extração inteligente de PDF** — PyMuPDF extrai o texto preservando a estrutura lógica do currículo
- **Comparação semântica com a vaga** — IA especialista em ATS analisa a compatibilidade técnica entre currículo e descrição
- **Score ATS (0–100)** — Pontuação calculada exclusivamente por correspondência técnica e semântica
- **Análise estruturada** — Pontos fortes, pontos fracos e sugestões detalhadas de melhoria
- **Interface responsiva** — Tema escuro em tons de verde metálico com transições suaves e validação em tempo real
- **Navegação sem reload** — HTMX injeta os fragmentos de forma dinâmica

## Stack Tecnológica

| Camada        | Tecnologia                                |
| ------------- | ----------------------------------------- |
| Linguagem     | Python 3.11.7                             |
| Framework Web | FastAPI (assíncrono, Pydantic v2)         |
| Frontend      | Jinja2 + HTMX + Vanilla JS               |
| Extração PDF  | PyMuPDF                                   |
| LLM           | Ollama Cloud (`minimax-m2.5:cloud`)        |
| Validação     | Pydantic v2                                |

## Estrutura do Projeto

```
ats-analyzer/
├── requirements.txt          # Dependências fixadas
├── .env                      # OLLAMA_API_KEY=chave_aqui
├── .gitignore
├── main.py                   # Entry point FastAPI (rotas e middlewares)
├── core/
│   ├── __init__.py
│   ├── pdf_parser.py         # Extração e limpeza de texto via PyMuPDF
│   ├── ollama_client.py      # Conexão com Ollama Cloud
│   ├── ats_engine.py         # Lógica de negócio e prompt assembly
│   └── schemas.py            # Modelos Pydantic (ATSAnalysis)
├── templates/
│   ├── base.html             # Layout base com paleta e HTMX
│   ├── upload.html           # Tela de ingestão de dados
│   └── results.html          # Tela de resultados da análise
├── prompts/
│   └── ats_system.txt        # Prompt template para o modelo
└── static/
    ├── styles.css            # Estilos customizados
    └── form-validation.js    # Validação client-side em tempo real
```

## Como Usar

### 1. Configurar API Key

Crie o arquivo `.env` na raiz do projeto:

```env
OLLAMA_API_KEY=sua_chave_aqui
```

### 2. Instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Iniciar o servidor

```bash
uvicorn main:app --reload
```

### 4. Acessar

Abra [http://127.0.0.1:8000](http://127.0.0.1:8000) no navegador.

### Fluxo de uso

1. Cole a descrição da vaga no campo de texto (mínimo 50 caracteres)
2. Arraste ou selecione um arquivo PDF de currículo (máx. 10 MB)
3. O botão "Analisar" será ativado automaticamente
4. Clique para processar — a análise é exibida sem recarregar a página
5. Use "Analisar Outro Currículo" para reiniciar

## API

| Método | Rota          | Descrição                                    |
| ------ | ------------- | -------------------------------------------- |
| GET    | `/`           | Renderiza tela de upload                      |
| POST   | `/analyze`    | Envia vaga + PDF, retorna fragmento com análise |

## Esquema de Resposta (JSON)

```json
{
  "score": 78,
  "strengths": ["Experiência com Python e FastAPI", ...],
  "weaknesses": ["Falta experiência em liderança técnica", ...],
  "suggestions": "Considere destacar projetos pessoais que demonstrem..."
}
```

## Testes

```bash
source .venv/bin/activate
python test_core.py
```

## Licença

MIT
