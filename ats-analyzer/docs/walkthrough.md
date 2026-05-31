# Walkthrough de Desenvolvimento: Sistema ATS Local

O desenvolvimento do Sistema ATS Local com integração ao Ollama Cloud foi concluído com sucesso. Implementamos uma arquitetura robusta, segura, de alta performance e com interface premium em tons verde metálico esmeralda.

---

## 🛠️ O que foi Implementado

O projeto foi estruturado no diretório `ats-analyzer/` exatamente de acordo com as especificações técnicas aprovadas:

### 1. Backend e Regras de Negócio (Python + FastAPI)
* **[requirements.txt](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/requirements.txt)**: Versões de bibliotecas fixadas e instaladas com sucesso (FastAPI, Uvicorn, PyMuPDF, Pydantic v2, Ollama).
* **[core/pdf_parser.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/pdf_parser.py)**: Extração de PDF precisa através do PyMuPDF, limpando espaços em branco e tratando arquivos corrompidos ou sem texto (imagens) com desvios seguros.
* **[core/ollama_client.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/ollama_client.py)**: Conexão direta ao endpoint cloud do Ollama (`https://ollama.com`) usando a assinatura de Authorization Bearer token a partir da variável `OLLAMA_API_KEY`.
* **[core/schemas.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/schemas.py)**: Validação estrita do payload JSON de análise via Pydantic v2 (`ATSAnalysis`), garantindo integridade e consistência dos limites (score 0-100, pontos fortes/fracos, sugestões).
* **[core/ats_engine.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/ats_engine.py)**: Orquestrador que monta a requisição à IA de forma assíncrona não bloqueante usando `asyncio.to_thread` para chamadas do SDK `ollama`.
* **[main.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/main.py)**: Ponto de entrada da aplicação, contendo:
  - Inicializador `lifespan` que valida a chave de API e para a execução no startup em caso de falta.
  - Validador server-side robusto limitando uploads a **10MB** e arquivos estritamente **PDF**.
  - Rota `GET /` com suporte inteligente a requisições HTMX (retorna o fragmento da tela inicial se solicitado, ou a página inteira `base.html` + `upload.html`).
  - Rota `POST /analyze` que orquestra todo o fluxo e retorna `results.html` para injeção sem reload de página.
  - Tratamento de exceção centralizado que exibe mensagens amigáveis na cor da paleta de erro (`#C0392B`) sem expor código ao usuário.

### 2. Frontend de Alta Fidelidade (Jinja2 + HTMX + CSS + JS)
* **[prompts/ats_system.txt](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/prompts/ats_system.txt)**: Prompt em PT-BR para guiar o modelo sênior ATS exigindo JSON e focando puramente no alinhamento técnico/semântico.
* **[templates/base.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/base.html)**: Layout raiz com tipografia moderna (Outfit e Inter), integração segura do HTMX e contêiner central.
* **[templates/fragment_base.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/fragment_base.html)**: Suporte para injeção limpa de templates parciais via HTMX.
* **[templates/upload.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/upload.html)**: Form com HTMX (post, target, indicator) incluindo dropzone interativa para PDF e contador mínimo de 50 caracteres em tempo real.
* **[templates/results.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/results.html)**: Resultados com Score circular dinâmico (verde esmeralda se ≥ 70, verde muted se < 70), cards de pontos e sugestões Markdown convertidas em HTML seguro pelo backend.
* **[static/styles.css](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/static/styles.css)**: CSS personalizado com paleta metálica, glassmorphism sutil nos cards, transições de foco WCAG AA e suavização de estados (200ms ease).
* **[static/form-validation.js](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/static/form-validation.js)**: Validação em tempo real, ativação do botão e suporte completo para arrastar e soltar PDFs (drag-and-drop).

---

## 🧪 Testes Realizados e Validação

### 1. Testes Automatizados (Core)
Escrevemos uma suíte de testes de unidade nativos em **[test_core.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/test_core.py)** validando os schemas Pydantic e o parser de PDFs.
Executamos os testes no ambiente isolado da aplicação:
```bash
source .venv/bin/activate
python test_core.py
```
**Resultado:**
```text
Ran 4 tests in 0.001s
OK
```
Os testes validaram:
* Aceitação correta de dados válidos pelo schema `ATSAnalysis`.
* Rejeição e lançamento de exceção para score superior a 100 ou inferior a 0.
* Tratamento robusto para parsing de arquivos corrompidos ou mal estruturados.

---

## 🚀 Como Executar e Validar a Aplicação Localmente

Siga o passo a passo abaixo para testar toda a interface de forma local:

### Passo 1: Configurar a API Key
Abra o arquivo **[.env](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/.env)** e insira sua chave válida de acesso à nuvem do Ollama:
```env
OLLAMA_API_KEY=sua_chave_real_aqui
```

### Passo 2: Inicializar o Servidor FastAPI
Execute os seguintes comandos no terminal a partir do diretório raiz do projeto:
```bash
cd "/Users/marcel/projetos/agent ats/ats-analyzer"
source .venv/bin/activate
uvicorn main:app --reload
```

### Passo 3: Interagir na Web
Abra seu navegador no endereço: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.
1. **Validação do Botão**: Digite uma descrição na caixa de texto. Veja o contador avisar o mínimo de 50 caracteres. O botão permanecerá cinza (`#3D4F45`).
2. **Arraste de Arquivo**: Arraste um arquivo PDF real para a dropzone, ou clique para selecionar. Veja o nome e tamanho do arquivo ficarem destacados em verde.
3. **Ativação**: Quando ambos os campos estiverem preenchidos e validados, o botão transitará suavemente em 200ms para verde esmeralda brilhante (`#2ECC71`).
4. **Análise (HTMX)**: Clique em "Analisar". A tela escurecerá levemente com um indicador "Processando Currículo..." premium contendo um spinner esmeralda dinâmico.
5. **Apresentação**: Sem recarregar a página, a tela será substituída pela análise detalhada contendo o gauge de pontuação colorido de acordo com a nota, listas limpas de pontos fortes/fracos e o plano de ação formatado.
6. **Reset**: Clique em "Analisar Outro Currículo" para voltar instantaneamente para o formulário limpo, sem recarregamento.
7. **Erro Visual**: Se você enviar um PDF inválido ou houver falha de rede/API, um card vermelho `#C0392B` elegante exibirá os detalhes de forma amigável com um botão para tentar novamente.
