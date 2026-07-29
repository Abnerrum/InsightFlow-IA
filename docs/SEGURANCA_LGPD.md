# Segurança do Back-end e LGPD

## Objetivo

Esta camada reduz riscos de acesso não autorizado, perda, alteração, vazamento e tratamento excessivo de dados pessoais. Ela ajuda na adequação técnica do InsightFlow IA, mas não garante conformidade jurídica isoladamente. O controlador ainda precisa definir finalidades, bases legais, responsáveis, contratos, política de privacidade, resposta a incidentes e prazos reais de retenção.

## Controles implementados

### 1. Criptografia de dados no banco

Perguntas e respostas do assistente são criptografadas antes da gravação no MySQL com Fernet. A chave é lida de `DATA_ENCRYPTION_KEY` e nunca deve ser enviada ao GitHub.

Gere a chave:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Pseudonimização de auditoria

Identificadores usados nos logs são transformados com HMAC-SHA256. O banco guarda um hash estável para correlação, sem gravar diretamente IP, e-mail ou código do usuário nos registros de auditoria.

### 3. Menor privilégio no MySQL

A aplicação não deve usar `root`. A migração cria `insightflow_app` com apenas `SELECT`, `INSERT`, `UPDATE` e `DELETE`. Mudanças de estrutura devem ser executadas por uma conta administrativa separada.

Execute:

```sql
SOURCE migrations/002_lgpd_security.sql;
```

Troque a senha presente no script antes da execução.

### 4. Segurança em trânsito

Em produção, publique o FastAPI somente atrás de HTTPS e habilite TLS na conexão com o MySQL. Configure o usuário do banco com `REQUIRE SSL` quando o servidor suportar.

### 5. Controle de origem e cabeçalhos

O sistema possui:

- CORS limitado aos domínios configurados;
- Content Security Policy;
- bloqueio de incorporação em iframe;
- proteção contra interpretação incorreta de conteúdo;
- política restrita de câmera, microfone e localização;
- HSTS em produção;
- identificador único por requisição.

### 6. Proteção contra abuso

Existe limitação de requisições por IP e rota. Para ambientes com múltiplas instâncias, substitua a memória local por Redis ou serviço equivalente.

### 7. Upload seguro

A importação valida:

- extensão e tipo MIME;
- tamanho máximo;
- quantidade máxima de linhas;
- colunas obrigatórias;
- limites de caracteres;
- datas e valores antes da gravação;
- transação com rollback em caso de erro.

O arquivo é processado em memória e não é salvo automaticamente no servidor.

### 8. Auditoria

As operações relevantes registram:

- identificador da requisição;
- ator pseudonimizado;
- ação;
- recurso;
- resultado;
- data e hora.

Evite colocar conteúdo pessoal, senhas, tokens ou respostas completas da IA no campo de detalhes.

### 9. Retenção e descarte

A rota administrativa abaixo elimina conversas e relatórios vencidos:

```http
POST /privacidade/retencao/executar
X-Admin-Key: sua-chave-administrativa
```

Prazos são configurados por:

```env
CONVERSATION_RETENTION_DAYS=90
REPORT_RETENTION_DAYS=365
```

Esses números são exemplos e devem ser aprovados pelo controlador conforme finalidade, obrigação legal e necessidade do negócio.

### 10. Direitos do titular

O sistema oferece:

```http
GET  /privacidade/aviso
POST /privacidade/solicitacoes
```

Tipos aceitos: `acesso`, `correcao`, `eliminacao`, `portabilidade`, `oposicao` e `informacao`.

A solicitação recebe protocolo, mas a validação de identidade e a decisão final precisam de processo humano seguro.

## Variáveis obrigatórias

```env
APP_ENV=production
DATABASE_URL=mysql+pymysql://insightflow_app:SENHA@servidor:3306/insightflow_ia
ADMIN_API_KEY=CHAVE_LONGA_E_ALEATORIA
DATA_ENCRYPTION_KEY=CHAVE_FERNET
AUDIT_HMAC_SECRET=SEGREDO_LONGO_E_ALEATORIO
ALLOWED_ORIGINS=https://seu-dominio.com.br
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_MB=10
PRIVACY_CONTACT_EMAIL=privacidade@suaempresa.com
```

## Cuidados com a OpenAI

Antes de enviar dados à IA:

1. envie somente indicadores necessários;
2. remova nomes, documentos, telefones, e-mails e descrições pessoais;
3. não envie dados pessoais sensíveis sem avaliação específica;
4. documente fornecedor, finalidade, base legal e eventual transferência internacional;
5. mantenha `store=False` na chamada da API quando compatível com a arquitetura.

A implementação atual envia somente dados agregados por departamento ao assistente.

## Banco de dados em produção

- backups criptografados e testados;
- acesso restrito por rede ou firewall;
- logs de acesso protegidos contra alteração;
- rotação periódica de senhas e chaves;
- segregação entre desenvolvimento e produção;
- restauração testada;
- atualizações de MySQL e dependências;
- monitoramento de tentativas de acesso;
- exclusão segura de backups após o prazo aplicável.

## Plano de incidentes

O projeto deve possuir um procedimento com:

1. detecção e contenção;
2. preservação de evidências;
3. avaliação dos dados e titulares afetados;
4. correção da causa;
5. decisão sobre comunicação à ANPD e aos titulares;
6. registro das medidas adotadas;
7. revisão posterior do incidente.

## Limitações atuais

Para uma versão de produção ainda são necessários:

- autenticação real de usuários;
- autorização por perfil e departamento;
- MFA para administradores;
- Redis para rate limiting distribuído;
- migrations com Alembic;
- cofre de segredos;
- testes automatizados de segurança;
- antivírus ou sandbox para uploads;
- gestão formal de consentimento quando essa for a base legal;
- relatório de impacto quando aplicável;
- processo validado para atendimento ao titular.

## Referências oficiais

- Lei nº 13.709/2018, especialmente princípios, direitos dos titulares, segurança e boas práticas;
- Guia Orientativo de Segurança da Informação para Agentes de Tratamento de Pequeno Porte da ANPD;
- Guias da ANPD sobre agentes de tratamento e encarregado.
