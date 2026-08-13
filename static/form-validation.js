function initializeUploadForm() {
    const jobField = document.getElementById('job-description');
    const fileInput = document.getElementById('resume-file');
    const submitBtn = document.getElementById('analyze-btn');
    const charCounter = document.getElementById('char-counter');
    const dropzone = document.getElementById('dropzone');
    const fileNameDisplay = document.getElementById('file-name-display');
    const pdfPreview = document.getElementById('pdf-preview');
    const pdfPreviewStatus = document.getElementById('pdf-preview-status');
    const pdfPreviewDetails = document.getElementById('pdf-preview-details');
    const pdfPreviewText = document.getElementById('pdf-preview-text');

    if (!jobField || !fileInput || !submitBtn) return;
    if (fileInput.dataset.previewInitialized === 'true') return;
    fileInput.dataset.previewInitialized = 'true';

    // Regra de limite de tamanho em bytes: 10MB
    const MAX_FILE_SIZE = 10 * 1024 * 1024;
    let previewReady = false;
    let previewRequestId = 0;

    function resetPreview() {
        previewReady = false;
        if (pdfPreview) pdfPreview.hidden = true;
        if (pdfPreviewStatus) pdfPreviewStatus.textContent = '';
        if (pdfPreviewText) pdfPreviewText.textContent = '';
        if (pdfPreviewDetails) pdfPreviewDetails.open = false;
    }

    function setPreviewError(message) {
        previewReady = false;
        if (pdfPreview) pdfPreview.hidden = false;
        if (pdfPreviewStatus) {
            pdfPreviewStatus.textContent = message;
            pdfPreviewStatus.className = 'preview-status preview-error';
        }
        if (pdfPreviewText) pdfPreviewText.textContent = '';
        if (pdfPreviewDetails) pdfPreviewDetails.open = false;
    }

    async function previewSelectedFile(file) {
        const requestId = ++previewRequestId;
        resetPreview();

        const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
        const isWithinSize = file.size > 0 && file.size <= MAX_FILE_SIZE;
        if (!isPdf || !isWithinSize) {
            validateForm();
            return;
        }

        if (pdfPreview) pdfPreview.hidden = false;
        if (pdfPreviewStatus) {
            pdfPreviewStatus.textContent = 'Extraindo o conteúdo do PDF...';
            pdfPreviewStatus.className = 'preview-status preview-loading';
        }
        validateForm();

        try {
            const formData = new FormData();
            formData.append('resume_file', file);
            const response = await fetch('/preview-pdf', {
                method: 'POST',
                body: formData
            });
            const payload = await response.json();

            if (requestId !== previewRequestId) return;
            if (!response.ok) throw new Error(payload.detail || 'Não foi possível extrair o conteúdo do PDF.');

            previewReady = true;
            if (pdfPreviewStatus) {
                pdfPreviewStatus.textContent = `Conteúdo extraído com sucesso (${payload.character_count} caracteres).`;
                pdfPreviewStatus.className = 'preview-status preview-success';
            }
            if (pdfPreviewText) pdfPreviewText.textContent = payload.text;
            if (pdfPreviewDetails) pdfPreviewDetails.open = true;
            validateForm();
        } catch (error) {
            if (requestId !== previewRequestId) return;
            setPreviewError(error.message || 'Não foi possível extrair o conteúdo do PDF.');
            validateForm();
        }
    }

    function validateForm() {
        const textValue = jobField.value.trim();
        const charCount = textValue.length;
        
        // 1. Atualiza o contador de caracteres visualmente
        if (charCounter) {
            if (charCount >= 50) {
                charCounter.textContent = `${charCount} caracteres (Mínimo atingido)`;
                charCounter.style.color = 'var(--accent-active)';
            } else {
                charCounter.textContent = `${charCount} / 50 caracteres mínimos`;
                charCounter.style.color = 'var(--text-secondary)';
            }
        }

        // 2. Validações principais
        const hasJobText = charCount >= 50;
        let hasValidFile = false;

        if (fileInput.files.length > 0) {
            const file = fileInput.files[0];
            // Deve ser PDF e menor ou igual a 10MB
            const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
            const isWithinSize = file.size > 0 && file.size <= MAX_FILE_SIZE;
            
            hasValidFile = isPdf && isWithinSize;

            if (fileNameDisplay) {
                if (!isPdf) {
                    fileNameDisplay.textContent = 'Erro: Apenas arquivos PDF são aceitos.';
                    fileNameDisplay.style.color = 'var(--color-error)';
                } else if (file.size === 0) {
                    fileNameDisplay.textContent = 'Erro: O arquivo selecionado está vazio.';
                    fileNameDisplay.style.color = 'var(--color-error)';
                } else if (!isWithinSize) {
                    fileNameDisplay.textContent = `Erro: O arquivo excede o limite de 10MB (Tamanho: ${(file.size / (1024 * 1024)).toFixed(2)}MB).`;
                    fileNameDisplay.style.color = 'var(--color-error)';
                } else {
                    fileNameDisplay.textContent = `Selecionado: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                    fileNameDisplay.style.color = 'var(--accent-active)';
                }
            }
        } else {
            if (fileNameDisplay) {
                fileNameDisplay.textContent = 'Arraste seu arquivo PDF aqui ou clique para selecionar';
                fileNameDisplay.style.color = 'var(--text-secondary)';
            }
        }

        // 3. Modifica o botão de acordo com a validação completa
        const isFormValid = hasJobText && hasValidFile && previewReady;
        submitBtn.disabled = !isFormValid;

        if (isFormValid) {
            submitBtn.classList.remove('btn-disabled');
            submitBtn.classList.add('btn-active');
        } else {
            submitBtn.classList.remove('btn-active');
            submitBtn.classList.add('btn-disabled');
        }
    }

    // =====================================================================
    // REGISTRO DE EVENTOS DOS CAMPOS DO FORMULÁRIO
    // =====================================================================
    jobField.addEventListener('input', validateForm);
    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (!file) {
            previewRequestId += 1;
            resetPreview();
            validateForm();
            return;
        }
        previewSelectedFile(file);
    });

    // =====================================================================
    // EVENTOS DE DRAG-AND-DROP NA DROPZONE
    // =====================================================================
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                // Atribui o arquivo arrastado ao input nativo
                fileInput.files = files;
                // Dispara o evento de mudança para rodar a validação
                fileInput.dispatchEvent(new Event('change'));
            }
        }, false);
    }

    // Estado inicial
    validateForm();
}

document.addEventListener('DOMContentLoaded', initializeUploadForm);
document.body.addEventListener('htmx:afterSwap', initializeUploadForm);
