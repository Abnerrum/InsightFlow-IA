# InsightFlow IA

MVP do Projeto Integrador desenvolvido com Python, FastAPI, MySQL, Pandas,
API da OpenAI e exportação de relatórios em Markdown para o Obsidian.

## Funcionalidades entregues nesta primeira versão

- Página inicial;
- Importação de CSV e Excel;
- Tratamento dos dados com Pandas;
- Armazenamento no MySQL;
- Dashboard de indicadores;
- Assistente ChatGPT dentro do sistema;
- Histórico das conversas no banco;
- Exportação da resposta para um Vault do Obsidian;
- Swagger em `/docs`.

## 1. Preparar o MySQL

Execute:

```sql
SOURCE criar_banco.sql;
```

Ou abra o arquivo `criar_banco.sql` no MySQL Workbench.

## 2. Criar o ambiente Python

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Configurar o sistema

Copie `.env.example` para `.env` e altere:

```env
DATABASE_URL=mysql+pymysql://root:SUA_SENHA@localhost:3306/insightflow_ia
OPENAI_API_KEY=SUA_CHAVE
OPENAI_MODEL=gpt-5
```

A chave da API deve permanecer somente no backend e nunca ser publicada no GitHub.

## 4. Executar

```powershell
uvicorn app.main:app --reload
```

Abra:

- Sistema: http://127.0.0.1:8000
- API Swagger: http://127.0.0.1:8000/docs

## 5. Testar

1. Acesse **Importar**.
2. Envie `modelo_importacao.csv`.
3. Abra o **Dashboard**.
4. Entre em **ChatGPT**.
5. Pergunte: `Qual departamento precisa de mais atenção?`
6. Exporte a resposta para o Obsidian.

## Próxima etapa

- Login e perfis de acesso;
- Gráficos com Chart.js;
- Filtros por período;
- Validação avançada da planilha;
- CRUD de departamentos e registros;
- Testes automatizados;
- Integração opcional com banco não relacional e IoT.
