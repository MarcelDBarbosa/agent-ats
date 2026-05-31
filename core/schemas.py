from pydantic import BaseModel, Field

class ATSAnalysis(BaseModel):
    """
    Representa a estrutura de dados validada da análise do currículo.
    Compatível com Pydantic v2.
    """
    score: int = Field(
        ge=0, 
        le=100, 
        description="Pontuação ATS de 0 a 100 baseada na correspondência semântica e técnica entre a vaga e o currículo."
    )
    strengths: list[str] = Field(
        description="Lista de pontos fortes e habilidades alinhadas encontradas no currículo."
    )
    weaknesses: list[str] = Field(
        description="Lista de lacunas de habilidades ou áreas não mencionadas de acordo com os requisitos."
    )
    suggestions: str = Field(
        description="Sugestões detalhadas e acionáveis de melhoria formatadas em Markdown."
    )
