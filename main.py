import os
import markdown
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.pdf_parser import extract_text_from_pdf
from core.ollama_client import get_ollama_client
from core.ats_engine import analyze_resume
from core.schemas import ATSAnalysis

# =====================================================================
# EVENTO DE INICIALIZAÇÃO (LIFESPAN)
# =====================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida do FastAPI. Realiza a validação da API Key
    do Ollama Cloud no momento de inicialização para falhar rapidamente.
    """
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key or api_key == "sua_chave_de_api_ollama_aqui":
        raise RuntimeError(
            "\n" + "="*80 + "\n"
            "ERRO CRÍTICO: A variável OLLAMA_API_KEY não foi configurada no arquivo .env!\n"
            "Por favor, configure uma chave válida para iniciar o analisador ATS.\n"
            + "="*80 + "\n"
        )
    print("OLLAMA_API_KEY detectada e validada com sucesso.")
    yield

# Instancia o FastAPI com o lifespan definido
app = FastAPI(
    title="Local ATS Analyzer",
    description="Sistema local premium para análise semântica de currículos com Ollama Cloud.",
    version="1.0.0",
    lifespan=lifespan
)

# =====================================================================
# CONFIGURAÇÃO DE ESTRUTURA E TEMPLATES
# =====================================================================
# Monta os arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura o motor de templates Jinja2
templates = Jinja2Templates(directory="templates")

# Adiciona o filtro personalizado do Markdown para o Jinja2
def markdown_filter(text: str) -> str:
    """Filtro para renderizar textos em Markdown para HTML seguro."""
    if not text:
        return ""
    # Permite renderização de tabelas e quebras automáticas de linha
    return markdown.markdown(text, extensions=['extra', 'nl2br'])

templates.env.filters["markdown"] = markdown_filter

# =====================================================================
# VALIDAÇÃO DE ARQUIVO SERVER-SIDE
# =====================================================================
async def read_and_validate_pdf(file: UploadFile) -> bytes:
    """
    Valida as regras no servidor e devolve o conteúdo do PDF em memória.
    """
    # 1. Valida o tipo do arquivo pelo tipo de mídia (mime-type) ou extensão
    filename_lower = file.filename.lower() if file.filename else ""
    if file.content_type != "application/pdf" and not filename_lower.endswith(".pdf"):
        raise ValueError("Apenas arquivos no formato PDF são permitidos.")
    
    # 2. Limita a leitura em memória para até 10MB
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    
    if len(content) > max_size:
        raise ValueError("O arquivo excede o limite de tamanho permitido de 10MB.")
        
    if len(content) == 0:
        raise ValueError("O arquivo selecionado está vazio.")

    return content


async def validate_and_parse_pdf(file: UploadFile) -> str:
    """Valida o PDF e extrai seu conteúdo textual usando o PyMuPDF."""
    content = await read_and_validate_pdf(file)
        
    return extract_text_from_pdf(content)

# =====================================================================
# ROTAS DO SISTEMA
# =====================================================================

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """
    Rota principal do sistema. Renderiza o formulário de upload.
    Diferencia requisições normais de requisições parciais do HTMX.
    """
    hx_request = request.headers.get("HX-Request") is not None
    return templates.TemplateResponse(
        "upload.html", 
        {
            "request": request, 
            "hx_request": hx_request
        }
    )


@app.post("/preview-pdf")
async def preview_pdf(resume_file: UploadFile = File(...)):
    """Extrai o texto do PDF para pré-visualização antes da análise."""
    try:
        text = await validate_and_parse_pdf(resume_file)
        return {
            "filename": resume_file.filename or "curriculo.pdf",
            "text": text,
            "character_count": len(text)
        }
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)}
        )

@app.post("/analyze", response_class=HTMLResponse)
async def post_analyze(
    request: Request,
    job_description: str = Form(...),
    resume_file: UploadFile = File(...)
):
    """
    Rota de processamento do currículo e vaga.
    Retorna apenas o fragmento HTML dos resultados ou de erro para injeção via HTMX.
    """
    try:
        # 1. Validações básicas da descrição da vaga
        cleaned_job_desc = job_description.strip()
        if len(cleaned_job_desc) < 50:
            raise ValueError("A descrição da vaga precisa ter pelo menos 50 caracteres.")
            
        # 2. Processa o arquivo PDF (validação de tipo, tamanho e extração)
        resume_text = await validate_and_parse_pdf(resume_file)
        
        # 3. Inicializa o cliente do Ollama Cloud
        client = get_ollama_client()
        
        # 4. Executa a análise semântica pela IA
        raw_analysis = await analyze_resume(client, cleaned_job_desc, resume_text)
        
        # 5. Valida o JSON retornado contra o Schema Pydantic
        analysis = ATSAnalysis(**raw_analysis)
        
        # 6. Renderiza o template de resultados
        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "analysis": analysis
            }
        )
        
    except Exception as e:
        # Tratamento robusto de erros exibido de forma visual amigável na cor do erro (#C0392B)
        error_msg = str(e)
        # Loga no console do servidor para debugging, mantendo a integridade de segurança
        print(f"[ERROR ATS-ANALYZER] {error_msg}")
        
        # Retorna um fragmento HTML de erro amigável estilizado
        return HTMLResponse(
            status_code=200,  # Retornamos 200 para o HTMX injetar corretamente o fragmento
            content=f"""
            <div class="card error-container fade-in" style="border-left: 5px solid var(--color-error, #C0392B);">
                <div class="error-header">
                    <span class="error-icon" style="font-size: 1.5rem; margin-right: 0.5rem;">⚠️</span>
                    <strong style="color: var(--text-primary, #E0F2E9);">Ocorreu um erro no processamento</strong>
                </div>
                <p class="error-body" style="color: var(--text-secondary, #8FA89A); margin-top: 0.75rem; line-height: 1.5;">
                    Não foi possível realizar a análise do currículo. Detalhe do erro:
                    <br>
                    <code style="display: block; background: rgba(192, 57, 43, 0.1); padding: 0.75rem; border-radius: 4px; color: var(--text-primary); margin-top: 0.5rem; font-family: monospace;">
                        {error_msg}
                    </code>
                </p>
                <div style="margin-top: 1.5rem;">
                    <button class="btn btn-active" 
                            hx-get="/" 
                            hx-target="#content-area" 
                            hx-swap="innerHTML"
                            style="padding: 0.5rem 1rem; font-size: 0.9rem;">
                        Tentar Novamente
                    </button>
                </div>
            </div>
            """
        )
