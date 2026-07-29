# InsightFlow IA

MVP de análise empresarial desenvolvido como Projeto Integrador, capaz de importar planilhas, tratar dados, gerar indicadores, produzir análises com inteligência artificial e exportar relatórios em Markdown para o Obsidian.

O sistema utiliza Python, FastAPI, MySQL, Pandas, SQLAlchemy e a API da OpenAI.

## Status do projeto

**Versão atual: 0.2.0 — MVP funcional em desenvolvimento.**

O projeto já possui o fluxo principal funcionando:

```text
CSV/Excel → validação → Pandas → MySQL → Dashboard → IA → Relatório Markdown
```

## Funcionalidades implementadas

- Página inicial com interface web;
- Importação de arquivos CSV e Excel;
- Validação de extensão, tipo, tamanho, colunas e quantidade de registros;
- Tratamento dos dados com Pandas;
- Armazenamento dos registros no MySQL;
- Dashboard de indicadores empresariais;
- Assistente de IA integrado à API da OpenAI;
- Análise baseada em dados agregados por departamento;
- Histórico de perguntas e respostas no banco;
- Criptografia das conversas e relatórios com Fernet;
- Exportação de análises em Markdown para um Vault do Obsidian;
- Auditoria pseudonimizada com HMAC-SHA256;
- Limitação de requisições por IP e rota;
- CORS configurável;
- Cabeçalhos HTTP de segurança;
- Identificador único para cada requisição;
- Rotina de retenção e descarte de conversas e relatórios;
- Canal para solicitações relacionadas aos direitos do titular;
- Documentação automática da API pelo Swagger em ambiente de desenvolvimento;
- Endpoint de verificação de saúde em `/saude`.

## Tecnologias utilizadas

- Python 3.11 ou superior;
- FastAPI;
- Uvicorn;
- MySQL;
- SQLAlchemy;
- PyMySQL;
- Pandas;
- OpenPyXL;
- Jinja2;
- HTML, CSS e JavaScript;
- API da OpenAI;
- Cryptography/Fernet;
- Obsidian e Markdown.

## Estrutura principal

```text
InsightFlow-IA/
├── app/
│   ├── middleware/
│   ├── routes/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── docs/
│   └── SEGURANCA_LGPD.md
├── migrations/
│   └── 002_lgpd_security.sql
├── .env.example
├── criar_banco.sql
├── modelo_importacao.csv
├── requirements.txt
└── README.md
```

# Como executar o projeto

## 1. Pré-requisitos

Instale no computador:

- Python 3.11 ou superior;
- MySQL Server;
- MySQL Workbench, opcional;
- Git;
- Visual Studio Code, recomendado.

Confirme as instalações:

```powershell
python --version
git --version
mysql --version
```

## 2. Clonar o repositório

```powershell
git clone https://github.com/Abnerrum/InsightFlow-IA.git
cd InsightFlow-IA
```

## 3. Criar o banco de dados

Abra o MySQL Workbench e execute o arquivo:

```text
criar_banco.sql
```

Também é possível executar pelo terminal do MySQL:

```sql
SOURCE criar_banco.sql;
```

O script cria o banco `insightflow_ia` e as tabelas iniciais do sistema.

## 4. Aplicar a migração de segurança e LGPD

Antes de executar a migração, abra o arquivo:

```text
migrations/002_lgpd_security.sql
```

Localize esta linha e altere a senha de exemplo:

```sql
CREATE USER IF NOT EXISTS 'insightflow_app'@'localhost'
IDENTIFIED BY 'TROQUE_POR_SENHA_FORTE';
```

Depois execute com um usuário administrador do MySQL:

```sql
SOURCE migrations/002_lgpd_security.sql;
```

Essa migração:

- adiciona campos de controle de criptografia;
- cria a tabela de auditoria;
- cria a tabela de solicitações do titular;
- cria o usuário `insightflow_app`;
- aplica o princípio do menor privilégio no banco.

A aplicação não deve utilizar o usuário `root` em produção.

## 5. Criar o ambiente virtual

No PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a ativação, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

No Prompt de Comando:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

## 6. Instalar as dependências

Com o ambiente virtual ativado:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 7. Criar o arquivo de configuração

Copie o arquivo `.env.example` para `.env`.

No PowerShell:

```powershell
Copy-Item .env.example .env
```

No Prompt de Comando:

```cmd
copy .env.example .env
```

O arquivo `.env` não deve ser enviado ao GitHub.

## 8. Gerar as chaves de segurança

### Chave de criptografia Fernet

Execute:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copie o resultado para:

```env
DATA_ENCRYPTION_KEY=SUA_CHAVE_FERNET
```

### Chave administrativa

Execute:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para:

```env
ADMIN_API_KEY=SUA_CHAVE_ADMINISTRATIVA
```

### Segredo de auditoria

Execute novamente:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para:

```env
AUDIT_HMAC_SECRET=SEU_SEGREDO_DE_AUDITORIA
```

## 9. Configurar o arquivo `.env`

Exemplo para desenvolvimento local:

```env
APP_NAME=InsightFlow IA
APP_ENV=development

DATABASE_URL=mysql+pymysql://insightflow_app:SUA_SENHA@localhost:3306/insightflow_ia

OPENAI_API_KEY=SUA_CHAVE_DA_OPENAI
OPENAI_MODEL=gpt-5

OBSIDIAN_VAULT_PATH=./obsidian-vault

ADMIN_API_KEY=SUA_CHAVE_ADMINISTRATIVA
DATA_ENCRYPTION_KEY=SUA_CHAVE_FERNET
AUDIT_HMAC_SECRET=SEU_SEGREDO_DE_AUDITORIA

ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_MB=10

CONVERSATION_RETENTION_DAYS=90
REPORT_RETENTION_DAYS=365
PRIVACY_CONTACT_EMAIL=privacidade@suaempresa.com
```

Substitua todos os valores de exemplo por valores reais e seguros.

### Sobre a chave da OpenAI

A chave deve ficar somente no arquivo `.env` do backend.

Nunca coloque a chave diretamente no código, no frontend, no README ou em commits do GitHub.

Sem `OPENAI_API_KEY`, as páginas básicas e o processamento local podem funcionar, mas o assistente não conseguirá gerar respostas pela API.

## 10. Executar o sistema

Com o ambiente virtual ativado:

```powershell
uvicorn app.main:app --reload
```

Também pode ser executado assim:

```powershell
python -m uvicorn app.main:app --reload
```

Abra no navegador:

- Sistema: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Verificação de saúde: `http://127.0.0.1:8000/saude`

Em produção, o Swagger é desabilitado automaticamente quando:

```env
APP_ENV=production
```

## 11. Testar o fluxo principal

1. Acesse o sistema;
2. Abra a página de importação;
3. Envie o arquivo `modelo_importacao.csv`;
4. Aguarde a validação e o processamento;
5. Abra o dashboard;
6. Confira os indicadores gerados;
7. Entre no assistente de IA;
8. Faça uma pergunta, por exemplo:

```text
Qual departamento precisa de mais atenção?
```

9. Gere a análise;
10. Exporte a resposta para o Obsidian.

## Rotas importantes

```text
GET  /                         Página inicial
GET  /saude                    Status da aplicação
GET  /docs                     Documentação Swagger em desenvolvimento
GET  /privacidade/aviso        Aviso de privacidade
POST /privacidade/solicitacoes Solicitação relacionada ao titular
POST /privacidade/retencao/executar
```

A rota administrativa de retenção exige o cabeçalho:

```text
X-Admin-Key: valor_configurado_no_env
```

## Segurança e privacidade

O projeto implementa controles técnicos para reduzir riscos, incluindo:

- criptografia de conversas e relatórios;
- pseudonimização de identificadores de auditoria;
- validação de arquivos antes da gravação;
- processamento de uploads em memória;
- transações com rollback em caso de falha;
- restrição de origens permitidas;
- cabeçalhos de segurança;
- limitação de requisições;
- retenção configurável;
- usuário do banco com privilégios reduzidos.

A implementação atual envia ao assistente somente dados agregados por departamento. Evite enviar nomes, documentos, telefones, e-mails ou dados pessoais sensíveis para a IA.

Consulte a documentação detalhada:

```text
docs/SEGURANCA_LGPD.md
```

Esses controles ajudam na adequação técnica, mas não garantem conformidade jurídica completa com a LGPD. Uma implantação real ainda exige definição de finalidade, base legal, política de privacidade, contratos, responsáveis, plano de incidentes e processos organizacionais.

## Problemas comuns

### Erro de conexão com o MySQL

Confira:

- se o MySQL está iniciado;
- se o banco `insightflow_ia` foi criado;
- se o usuário `insightflow_app` existe;
- se a senha do `.env` é a mesma definida na migração;
- se a porta do MySQL é `3306`.

### Erro ao importar Excel

Confirme se o ambiente possui:

```powershell
pip install pandas openpyxl
```

### Erro de chave de criptografia

Gere uma nova chave Fernet e copie o valor completo para `DATA_ENCRYPTION_KEY`.

Não altere essa chave depois de gravar dados criptografados, pois os registros antigos poderão deixar de ser descriptografados.

### Erro na API da OpenAI

Confira:

- se a chave está correta;
- se existe saldo ou faturamento configurado na conta da API;
- se o modelo configurado está disponível;
- se a variável `OPENAI_API_KEY` foi carregada corretamente.

### Porta 8000 ocupada

Execute em outra porta:

```powershell
uvicorn app.main:app --reload --port 8001
```

## Próximas etapas

- Login e autenticação real de usuários;
- Perfis de administrador, gestor e usuário;
- Autorização por empresa e departamento;
- Filtros por período no dashboard;
- Mais gráficos e indicadores;
- CRUD de departamentos e registros;
- Testes automatizados com Pytest;
- Migrações versionadas com Alembic;
- Redis para rate limit distribuído;
- MFA para administradores;
- Cofre de segredos em produção;
- Deploy com HTTPS;
- Monitoramento e backups automatizados.

## Aviso

Este projeto é um MVP acadêmico e de portfólio. Antes de utilizar dados reais de uma empresa, revise as configurações de segurança, privacidade, infraestrutura, acesso ao banco e tratamento dos dados.

## Autor

Desenvolvido por **Abner Luiz**.

GitHub: `Abnerrum`
