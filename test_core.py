import unittest
from pydantic import ValidationError
from core.schemas import ATSAnalysis
from core.pdf_parser import extract_text_from_pdf

class TestATSCore(unittest.TestCase):
    """
    Testes de unidade para validar a robustez e regras de negócio do core do ATS.
    """

    def test_schema_valid_data(self):
        """Valida que o schema Pydantic aceita dados corretos."""
        data = {
            "score": 85,
            "strengths": ["Experiência em Python", "Domínio de Docker"],
            "weaknesses": ["Falta de Cloud"],
            "suggestions": "### Dicas\n\nAdicione Cloud ao currículo."
        }
        analysis = ATSAnalysis(**data)
        self.assertEqual(analysis.score, 85)
        self.assertEqual(len(analysis.strengths), 2)
        self.assertEqual(analysis.weaknesses[0], "Falta de Cloud")

    def test_schema_score_out_of_bounds_high(self):
        """Valida que o schema rejeita pontuação acima de 100."""
        data = {
            "score": 105,  # Inválido
            "strengths": ["Python"],
            "weaknesses": [],
            "suggestions": "Dica"
        }
        with self.assertRaises(ValidationError):
            ATSAnalysis(**data)

    def test_schema_score_out_of_bounds_low(self):
        """Valida que o schema rejeita pontuação abaixo de 0."""
        data = {
            "score": -5,  # Inválido
            "strengths": ["Python"],
            "weaknesses": [],
            "suggestions": "Dica"
        }
        with self.assertRaises(ValidationError):
            ATSAnalysis(**data)

    def test_pdf_parser_corrupted_data(self):
        """Valida que o parser de PDF trata de forma limpa erros de arquivos corrompidos."""
        corrupted_bytes = b"This is not a PDF file structure at all!"
        with self.assertRaises(ValueError) as context:
            extract_text_from_pdf(corrupted_bytes)
        
        self.assertIn("Falha ao extrair texto do PDF", str(context.exception))

if __name__ == "__main__":
    unittest.main()
