# Melhorias do Front-end — InsightFlow IA

Esta atualização transforma o MVP em uma interface administrativa mais profissional, responsiva e adequada para apresentação do Projeto Integrador.

## Melhorias implementadas

### Layout principal
- Sidebar fixa com ícones e identificação do usuário;
- Cabeçalho superior com notificações;
- Menu responsivo para celulares e tablets;
- Tema claro e escuro com preferência salva no `localStorage`.

### Dashboard executivo
- Cartões de KPI para total, concluídos, atrasados e valor total;
- Taxa de conclusão;
- Gráfico de desempenho por departamento;
- Gráfico de distribuição por status;
- Registros recentes;
- Área de pontos de atenção;
- Estrutura visual de filtros por período e departamento.

### Importação de dados
- Área de arrastar e soltar arquivos;
- Suporte a CSV, XLS e XLSX;
- Informações de nome e tamanho do arquivo;
- Barra de progresso;
- Pré-visualização das primeiras linhas;
- Download do modelo CSV.

### Assistente ChatGPT
- Interface em formato de chat;
- Balões de conversa para usuário e IA;
- Horário das mensagens;
- Perguntas sugeridas;
- Atalho `Ctrl + Enter`;
- Nova conversa;
- Exportação da análise para o Obsidian.

### Central de relatórios
- Histórico de relatórios armazenados no MySQL;
- Visualização do conteúdo;
- Data de geração;
- Identificação do formato Markdown;
- Integração com o Vault do Obsidian.

## Tecnologias adicionadas ao front-end
- Bootstrap 5;
- Bootstrap Icons;
- Chart.js;
- SweetAlert2;
- SheetJS;
- JavaScript;
- CSS responsivo;
- Jinja2.

## Arquivos principais alterados
- `app/templates/base.html`
- `app/templates/index.html`
- `app/templates/dashboard.html`
- `app/templates/importar.html`
- `app/templates/assistente.html`
- `app/templates/relatorios.html`
- `app/static/css/style.css`
- `app/static/js/app.js`
- `app/static/js/importacao.js`
- `app/static/js/assistente.js`
- `app/routes/dashboard.py`
- `app/routes/relatorios.py`

## Como testar

```powershell
uvicorn app.main:app --reload
```

Acesse `http://127.0.0.1:8000`, importe o arquivo `modelo_importacao.csv`, abra o dashboard, faça uma pergunta ao assistente e exporte a resposta para o Obsidian.

## Próximas etapas
- Conectar os filtros às consultas do MySQL;
- Adicionar login e perfis de acesso;
- Criar notificações reais;
- Adicionar paginação e pesquisa;
- Criar edição e exclusão de relatórios;
- Implementar testes automatizados.
