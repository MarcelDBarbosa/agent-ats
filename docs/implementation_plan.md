# Implementação do Sistema ATS Local com Ollama Cloud

Este plano de implementação descreve a criação de uma aplicação web de desktop local para macOS que analisa currículos em PDF contra descrições de vagas. O sistema usará o FastAPI como backend, renderização do lado do servidor via Jinja2, atualizações de UI dinâmicas e sem recarregamento via HTMX, além da extração precisa de textos em PDF usando o PyMuPDF. A análise lógica será realizada através do modelo `minimax-m2.5:cloud` no Ollama Cloud.

---

## User Review Required

> [!IMPORTANT]
> **API Key do Ollama Cloud (`OLLAMA_API_KEY`)**: O sistema requer um arquivo `.env` contendo a chave `OLLAMA_API_KEY` válida para que as chamadas ao modelo `minimax-m2.5:cloud` funcionem. Se a chave não for fornecida, a inicialização do FastAPI falhará no startup via validação de ciclo de vida (`lifespan`).
> Por favor, certifique-se de configurar a chave correta no seu ambiente.

> [!NOTE]
> **HTMX e Bootstrap/Tailwind**: De acordo com as diretrizes e regras de UX premium, desenvolveremos estilos personalizados dedicados baseados na paleta metálica esmeralda no arquivo `static/styles.css`, sem dependência de Tailwind CSS, para garantir visual limpo, moderno, de alta performance e totalmente responsivo.

---

## Open Questions

> [!WARNING]
> **Acesso Externo ao Ollama Cloud**: O host `https://ollama.com` configurado como base para o cliente Ollama aceita requisições à API com a assinatura de Authorization header `Bearer {OLLAMA_API_KEY}`? 
> *Nota: Esta é a especificação indicada nas diretrizes e será seguida estritamente.*

---

## Proposed Changes

Faremos as alterações no diretório `ats-analyzer/` conforme a árvore de diretórios especificada.

### Componente Backend (FastAPI & Core)

#### [NEW] [requirements.txt](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/requirements.txt)
Contém as dependências do projeto fixadas.
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

#### [NEW] [.env](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/.env)
Variáveis de ambiente locais (não versionado).
```env
OLLAMA_API_KEY=seu_token_aqui
```

#### [NEW] [.gitignore](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/.gitignore)
Evitar vazamentos de chave e versionamento de lixo do python.
```text
.env
.venv/
__pycache__/
*.pyc
.DS_Store
```

#### [NEW] [pdf_parser.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/pdf_parser.py)
Parser de PDF robusto via PyMuPDF. Trata exceções de arquivos corrompidos ou sem texto legível.

#### [NEW] [ollama_client.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/ollama_client.py)
Cliente configurado para a Ollama Cloud (`https://ollama.com` via Bearer token).

#### [NEW] [schemas.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/schemas.py)
Schema de validação Pydantic `ATSAnalysis` para garantir saída estritamente estruturada (pontuação, pontos fortes, pontos fracos e sugestões).

#### [NEW] [ats_engine.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/core/ats_engine.py)
Orquestrador que lê o prompt de sistema de `prompts/ats_system.txt`, monta a chamada de chat e executa de forma assíncrona não bloqueante via `asyncio.to_thread()`.

#### [NEW] [main.py](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/main.py)
Instância principal do FastAPI. Ciclo de vida (`lifespan`) valida a API key. Rotas:
- `GET /`: serve a página inicial.
- `POST /analyze`: analisa o currículo enviado, extrai PDF, processa pela IA, valida schema Pydantic e renderiza e retorna o fragmento de resultados `results.html` para ser injetado via HTMX. Tratamento central de erros para retornar uma mensagem amigável vermelha `#C0392B` em caso de falha de conexão ou parser.

---

### Componente Frontend (Templates, CSS & JS)

#### [NEW] [ats_system.txt](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/prompts/ats_system.txt)
Prompt de sistema em Português do Brasil forçando retorno em JSON estruturado e definindo critérios de score puramente semânticos.

#### [NEW] [base.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/base.html)
Template mestre com tags semânticas, viewport responsiva, importação do HTMX e o layout em Verde Metálico Escuro (`#1A2F23`). Contém uma área central `<main id="content-area">` onde as telas serão injetadas dinamicamente.

#### [NEW] [upload.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/upload.html)
Tela 1: Formulário de upload com hx-post para `/analyze`, direcionado para `#content-area` com indicador `#loading-spinner`. Contém contador de caracteres do textarea em tempo real.

#### [NEW] [results.html](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/templates/results.html)
Tela 2: Apresentação premium dos resultados da análise. Score exibido como barra de progresso colorida (Verde Esmeralda se >= 70, Verde Acinzentado Muted se < 70). Listagem de pontos fortes, pontos fracos e sugestões formatadas com Markdown nativamente convertido em HTML pelo backend. Botão para voltar à tela inicial limpando o estado (re-injeta `upload.html` via HTMX).

#### [NEW] [styles.css](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/static/styles.css)
CSS personalizado premium para estética metálica, glassmorphism sutil nos cards, estados de foco WCAG AA, e micro-animações/transições suaves para botões ativos e desativados.

#### [NEW] [form-validation.js](file:///Users/marcel/projetos/agent%20ats/ats-analyzer/static/form-validation.js)
Lógica client-side para validação em tempo real e ativação suave do botão "Analisar", além do contador de caracteres do campo de descrição de vagas.

---

## Verification Plan

### Automated/Manual Verification
1. **Setup de Dependências**:
   - Criar `.venv` e executar `pip install -r requirements.txt`.
2. **Validação do Servidor**:
   - Inicializar o servidor usando `uvicorn main:app --reload` no diretório `ats-analyzer/`.
   - Verificar se há erro no startup caso a chave `OLLAMA_API_KEY` esteja em falta no `.env`.
3. **Validação do Fluxo de UX (Client-side)**:
   - Carregar a interface localmente em `http://127.0.0.1:8000`.
   - Testar o bloqueio e desbloqueio dinâmico do botão "Analisar": o botão deve estar desabilitado (`#3D4F45`) até que a descrição da vaga atinja 50 caracteres e um PDF válido seja selecionado. O botão deve mudar de cor com transição de 200ms para `#2ECC71`.
   - Testar o contador de caracteres do textarea.
   - Testar arquivos maiores de 10MB ou formatos que não sejam PDF, validando o erro no frontend sem recarregar a página.
4. **Validação da Chamada de Análise (End-to-End)**:
   - Fornecer uma descrição de vaga válida (>50 caracteres) e fazer upload de um PDF real de currículo.
   - Clicar em "Analisar" e confirmar que o spinner de carregamento HTMX aparece e permanece na tela até a conclusão.
   - Confirmar que a tela transiciona suavemente para a visualização de resultados sem recarregar a página.
   - Verificar a barra de progresso: cor verde esmeralda para notas >= 70, e cor verde muted para notas < 70.
   - Verificar se as sugestões formatadas em Markdown estão renderizadas perfeitamente como HTML puro (ex: listas, negrito).
   - Testar o botão "Nova Análise" para resetar o fluxo com HTMX de volta para a tela de ingestão.
5. **Tratamento de Erros e Timeout**:
   - Simular indisponibilidade do Ollama Cloud ou credenciais inválidas para certificar que o erro é capturado e uma mensagem legível com cor de erro `#C0392B` é exibida no frontend.
