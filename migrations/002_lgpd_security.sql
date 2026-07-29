-- Execute com um usuário administrador do MySQL.
-- Revise senhas, host e permissões antes de produção.

USE insightflow_ia;

ALTER TABLE conversas_ia
    ADD COLUMN IF NOT EXISTS criptografado BOOLEAN NOT NULL DEFAULT TRUE;

ALTER TABLE relatorios
    ADD COLUMN IF NOT EXISTS criptografado BOOLEAN NOT NULL DEFAULT TRUE;

CREATE TABLE IF NOT EXISTS auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id VARCHAR(128) NOT NULL,
    ator_hash VARCHAR(64) NOT NULL,
    acao VARCHAR(100) NOT NULL,
    recurso VARCHAR(200) NOT NULL,
    resultado VARCHAR(30) NOT NULL,
    detalhes TEXT NULL,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_auditoria_request_id (request_id),
    INDEX idx_auditoria_ator_hash (ator_hash),
    INDEX idx_auditoria_criado_em (criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS solicitacoes_titular (
    id INT AUTO_INCREMENT PRIMARY KEY,
    protocolo VARCHAR(40) NOT NULL UNIQUE,
    titular_hash VARCHAR(64) NOT NULL,
    tipo VARCHAR(40) NOT NULL,
    descricao TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Recebida',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_solicitacao_titular_hash (titular_hash),
    INDEX idx_solicitacao_criado_em (criado_em)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Princípio do menor privilégio: a aplicação não deve usar root.
CREATE USER IF NOT EXISTS 'insightflow_app'@'localhost' IDENTIFIED BY 'TROQUE_POR_SENHA_FORTE';
GRANT SELECT, INSERT, UPDATE, DELETE ON insightflow_ia.* TO 'insightflow_app'@'localhost';
REVOKE CREATE, DROP, ALTER, INDEX, GRANT OPTION ON insightflow_ia.* FROM 'insightflow_app'@'localhost';
FLUSH PRIVILEGES;

-- Produção: habilite TLS no MySQL e use REQUIRE SSL para o usuário da aplicação.
-- ALTER USER 'insightflow_app'@'localhost' REQUIRE SSL;
