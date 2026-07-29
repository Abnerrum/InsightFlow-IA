# Como executar o InsightFlow IA no Visual Studio Code

Este guia explica, passo a passo, como baixar, configurar e executar o InsightFlow IA no Windows usando o Visual Studio Code.

> Estado atual: o sistema está em fase de MVP. A estrutura principal, o banco de dados, a importação, o dashboard, a segurança e as rotas já existem. Para testar o assistente de IA, ainda é necessário configurar uma chave válida da API da OpenAI no arquivo `.env`.

## 1. Programas necessários

Instale os seguintes programas:

- Python 3.11 ou superior;
- Git;
- MySQL Server;
- MySQL Workbench;
- Visual Studio Code.

No Visual Studio Code, instale também estas extensões:

- Python, da Microsoft;
- Pylance, da Microsoft;
- MySQL, opcional;
- GitLens, opcional.

## 2. Confirmar as instalações

Abra o PowerShell ou o Prompt de Comando e execute:

```powershell
python --version
git --version
mysql --version
code --version
```

Caso algum comando não seja reconhecido, reinicie o computador ou verifique se o programa foi adicionado ao PATH do Windows.

## 3. Baixar o projeto do GitHub

Escolha uma pasta no computador, abra o terminal nessa pasta e execute:

```powershell
git clone https://github.com/Abnerrum/InsightFlow-IA.git
cd InsightFlow-IA
```

Para abrir o projeto diretamente no Visual Studio Code:

```powershell
code .
```

Também é possível abrir pelo menu:

1. Abra o Visual Studio Code;
2. Clique em **Arquivo**;
3. Clique em **Abrir Pasta**;
4. Selecione a pasta `InsightFlow-IA`.

## 4. Abrir o terminal do Visual Studio Code

Dentro do Visual Studio Code:

1. Clique em **Terminal**;
2. Clique em **Novo Terminal**;
3. Confirme se o terminal está aberto na pasta do projeto.

O caminho deve terminar em:

```text
InsightFlow-IA
```

## 5. Criar o ambiente virtual Python

No terminal integrado do Visual Studio Code, execute:

```powershell
python -m venv .venv
```

Depois ative o ambiente virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear a ativação, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Quando o ambiente estiver ativo, o terminal deverá mostrar algo parecido com:

```text
(.venv) PS C:\...\InsightFlow-IA>
```

## 6. Selecionar o interpretador Python no Visual Studio Code

1. Pressione `Ctrl + Shift + P`;
2. Digite `Python: Select Interpreter`;
3. Selecione o interpretador localizado em:

```text
.venv\Scripts\python.exe
```

Essa etapa garante que o Visual Studio Code utilize as bibliotecas instaladas no ambiente do projeto.

## 7. Instalar as dependências

Com o ambiente virtual ativo, execute:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

As principais dependências instaladas são:

- FastAPI;
- Uvicorn;
- SQLAlchemy;
- PyMySQL;
- Pandas;
- OpenPyXL;
- Jinja2;
- OpenAI;
- Cryptography.

## 8. Criar o banco de dados no MySQL

Abra o MySQL Workbench e conecte-se com um usuário administrador.

### 8.1 Criar as tabelas iniciais

No MySQL Workbench:

1. Clique em **File**;
2. Clique em **Open SQL Script**;
3. Abra o arquivo `criar_banco.sql`;
4. Execute todo o script clicando no ícone de raio.

O script cria o banco:

```text
insightflow_ia
```

### 8.2 Aplicar a migração de segurança

Abra o arquivo:

```text
migrations/002_lgpd_security.sql
```

Antes de executar, altere esta senha de exemplo:

```sql
CREATE USER IF NOT EXISTS 'insightflow_app'@'localhost'
IDENTIFIED BY 'TROQUE_POR_SENHA_FORTE';
```

Exemplo:

```sql
CREATE USER IF NOT EXISTS 'insightflow_app'@'localhost'
IDENTIFIED BY 'MinhaSenhaForte123!';
```

Depois execute todo o arquivo no MySQL Workbench.

Essa migração:

- cria o usuário `insightflow_app`;
- limita as permissões do usuário;
- cria a tabela de auditoria;
- cria a tabela de solicitações do titular;
- adiciona campos de segurança e criptografia.

## 9. Criar o arquivo `.env`

No terminal do Visual Studio Code, execute:

```powershell
Copy-Item .env.example .env
```

Caso esteja usando o Prompt de Comando:

```cmd
copy .env.example .env
```

O arquivo `.env` guarda as configurações locais e não deve ser enviado ao GitHub.

## 10. Gerar as chaves de segurança

### 10.1 Chave de criptografia

Execute:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copie o resultado para a variável:

```env
DATA_ENCRYPTION_KEY=SUA_CHAVE_GERADA
```

### 10.2 Chave administrativa

Execute:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para:

```env
ADMIN_API_KEY=SUA_CHAVE_ADMINISTRATIVA
```

### 10.3 Segredo de auditoria

Execute novamente:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie o resultado para:

```env
AUDIT_HMAC_SECRET=SEU_SEGREDO_DE_AUDITORIA
```

## 11. Configurar o arquivo `.env`

Abra o arquivo `.env` no Visual Studio Code e configure:

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

A senha do `DATABASE_URL` deve ser a mesma senha definida para o usuário `insightflow_app` na migração do MySQL.

### Teste sem a API da OpenAI

É possível testar a página inicial, o banco, a importação e parte do dashboard sem preencher a chave da OpenAI.

Nesse caso, deixe:

```env
OPENAI_API_KEY=
```

O assistente ChatGPT não responderá até que uma chave válida seja configurada.

## 12. Executar o sistema

Com o MySQL iniciado e o ambiente virtual ativo, execute no terminal do Visual Studio Code:

```powershell
python -m uvicorn app.main:app --reload
```

Também pode ser usado:

```powershell
uvicorn app.main:app --reload
```

Quando funcionar, o terminal mostrará uma mensagem parecida com:

```text
Uvicorn running on http://127.0.0.1:8000
```

Não feche esse terminal enquanto estiver usando o sistema.

## 13. Abrir o sistema no navegador

Abra os seguintes endereços:

- Sistema: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- Verificação de saúde: `http://127.0.0.1:8000/saude`

A rota `/saude` deve apresentar uma resposta parecida com:

```json
{
  "status": "online",
  "sistema": "InsightFlow IA"
}
```

## 14. Testar o sistema passo a passo

Realize os testes nesta ordem:

### Teste 1 — Inicialização

1. Execute o Uvicorn;
2. Abra a página inicial;
3. Confirme se não aparece erro no navegador;
4. Abra `/saude` e confirme o status `online`.

### Teste 2 — Banco de dados

1. Verifique se o MySQL está iniciado;
2. Abra o MySQL Workbench;
3. Confirme se o banco `insightflow_ia` existe;
4. Confirme se as tabelas foram criadas.

### Teste 3 — Importação da planilha

1. Abra a página de importação;
2. Selecione o arquivo `modelo_importacao.csv`;
3. Envie o arquivo;
4. Confirme se a validação foi concluída;
5. Verifique no MySQL se os registros foram gravados.

### Teste 4 — Dashboard

1. Abra o dashboard;
2. Confirme se os indicadores foram carregados;
3. Compare os números com o arquivo importado;
4. Registre qualquer informação incorreta.

### Teste 5 — Assistente ChatGPT

Esse teste exige uma chave válida em `OPENAI_API_KEY`.

1. Abra a página do assistente;
2. Faça uma pergunta, por exemplo:

```text
Qual departamento precisa de mais atenção?
```

3. Confirme se a resposta utiliza os dados importados;
4. Verifique se a conversa foi salva no banco;
5. Teste a exportação para Markdown ou Obsidian.

## 15. Como parar o sistema

No terminal em que o Uvicorn está rodando, pressione:

```text
Ctrl + C
```

Para sair do ambiente virtual, execute:

```powershell
deactivate
```

## 16. Como executar novamente depois

Nas próximas vezes, não será necessário recriar o ambiente nem reinstalar tudo.

Abra o projeto no Visual Studio Code e execute:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

## 17. Atualizar o projeto pelo GitHub

Antes de começar a trabalhar, execute:

```powershell
git pull origin main
```

Depois de alterar arquivos:

```powershell
git status
git add .
git commit -m "descreva a alteração realizada"
git push origin main
```

Não envie o arquivo `.env`, senhas, chaves da API ou dados pessoais ao GitHub.

## 18. Problemas comuns

### `python` não é reconhecido

Reinstale o Python marcando a opção **Add Python to PATH**.

### Ambiente virtual não ativa

Execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Erro de conexão com MySQL

Confira:

- se o MySQL está iniciado;
- se o banco `insightflow_ia` existe;
- se o usuário `insightflow_app` foi criado;
- se a senha do `.env` está correta;
- se a porta é `3306`.

### Erro `ModuleNotFoundError`

Ative o ambiente virtual e reinstale as dependências:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Erro na API da OpenAI

Confira:

- se a chave foi colocada corretamente no `.env`;
- se a conta da API possui faturamento ou créditos configurados;
- se o modelo está disponível;
- se o servidor foi reiniciado depois da alteração do `.env`.

### Porta 8000 ocupada

Execute em outra porta:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Depois abra:

```text
http://127.0.0.1:8001
```

## 19. Informações que devem ser anotadas durante o teste

Durante a execução, registre:

- se o sistema iniciou corretamente;
- mensagens exibidas no terminal;
- erros apresentados no navegador;
- conexão com o MySQL;
- resultado da importação;
- dados apresentados no dashboard;
- resposta do ChatGPT;
- funcionamento da exportação;
- funcionalidades solicitadas pelo professor;
- melhorias necessárias para a próxima versão.

Essas informações serão utilizadas para comparar o que já funciona, o que funciona parcialmente e o que ainda falta concluir.