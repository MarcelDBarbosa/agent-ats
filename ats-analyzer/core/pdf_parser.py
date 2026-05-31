import fitz  # PyMuPDF

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Lê um buffer de bytes contendo um PDF, extrai todo o texto limpo
    e trata exceções e arquivos sem texto.
    """
    try:
        # Abre o documento PDF a partir do stream de bytes em memória
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        
        # Itera por todas as páginas do PDF e acumula o texto
        for page in doc:
            page_text = page.get_text()
            if page_text:
                text += page_text + " "
        
        # Fecha o documento para liberar recursos
        doc.close()
        
        # Limpa espaços em branco extras, tabs e quebras de linha
        cleaned_text = " ".join(text.split())
        
        # Valida se o texto extraído é vazio (ex: PDF apenas com imagens/escaners sem OCR)
        if not cleaned_text.strip():
            raise ValueError("O PDF não contém texto extraível legível.")
            
        return cleaned_text
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Falha ao extrair texto do PDF: {str(e)}")
