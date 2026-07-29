from openai import OpenAI

from app.config import get_settings


def gerar_analise(pergunta: str, dados: str) -> str:
    settings = get_settings()

    if not settings.openai_api_key:
        return (
            "Modo demonstração: a chave OPENAI_API_KEY ainda não foi configurada.\n\n"
            f"Pergunta recebida: {pergunta}\n\n"
            f"Resumo disponível no sistema:\n{dados}"
        )

    client = OpenAI(api_key=settings.openai_api_key)
    instrucoes = """
Você é o assistente de análise empresarial do sistema InsightFlow IA.
Responda em português do Brasil e utilize somente os dados fornecidos.
Não invente números ou fatos. Quando faltarem dados, informe claramente.
Organize a resposta em: resumo, evidências, pontos de atenção e recomendações.
"""

    try:
        resposta = client.responses.create(
            model=settings.openai_model,
            instructions=instrucoes,
            input=f"DADOS DO SISTEMA:\n{dados}\n\nPERGUNTA:\n{pergunta}",
            store=False,
        )
        return resposta.output_text
    except Exception as erro:
        raise RuntimeError(
            "Não foi possível consultar a IA. Confira a chave, o modelo e a conexão."
        ) from erro
