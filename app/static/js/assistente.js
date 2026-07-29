const botao = document.getElementById("enviar");
const exportar = document.getElementById("exportar");
const campo = document.getElementById("pergunta");
const resposta = document.getElementById("resposta");
const statusBox = document.getElementById("status");

botao.addEventListener("click", async () => {
  const pergunta = campo.value.trim();
  if (pergunta.length < 3) {
    statusBox.innerHTML = '<div class="alert alert-warning">Digite uma pergunta válida.</div>';
    return;
  }
  botao.disabled = true;
  exportar.disabled = true;
  statusBox.innerHTML = '<div class="alert alert-info">Analisando os dados...</div>';
  resposta.classList.add("d-none");
  try {
    const requisicao = await fetch("/assistente/perguntar", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({pergunta})
    });
    const dados = await requisicao.json();
    if (!requisicao.ok) throw new Error(dados.detail || "Falha na consulta.");
    resposta.textContent = dados.resposta;
    resposta.classList.remove("d-none");
    statusBox.innerHTML = "";
    exportar.disabled = false;
  } catch (erro) {
    statusBox.innerHTML = `<div class="alert alert-danger">${erro.message}</div>`;
  } finally {
    botao.disabled = false;
  }
});

exportar.addEventListener("click", async () => {
  const conteudo = resposta.textContent.trim();
  const titulo = prompt("Título do relatório:", "Análise empresarial");
  if (!titulo || !conteudo) return;
  const requisicao = await fetch("/relatorios/exportar", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({titulo, conteudo})
  });
  const dados = await requisicao.json();
  statusBox.innerHTML = requisicao.ok
    ? `<div class="alert alert-success">${dados.mensagem}<br>${dados.arquivo}</div>`
    : `<div class="alert alert-danger">${dados.detail || "Falha ao exportar."}</div>`;
});
