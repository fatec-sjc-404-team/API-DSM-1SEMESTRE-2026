-- Este arquivo se trata apenas do script usado para criar o modelo fisico do banco

CREATE DATABASE IF NOT EXISTS AvoCredit

    -- Escolho utf8mb4 para guardar corretamente acentos e outros caracteres.
    CHARACTER SET utf8mb4
    -- Defino comparações de texto sem diferenciar maiúsculas de minúsculas.
    COLLATE utf8mb4_unicode_ci;

USE AvoCredit;

CREATE TABLE IF NOT EXISTS BCB (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    data_base DATE NOT NULL,
    uf CHAR(2) NOT NULL,
    segmento VARCHAR(100) NOT NULL,
    cliente VARCHAR(20) NOT NULL,
    cnae_ocupacao VARCHAR(255) NOT NULL,

    porte VARCHAR(100) NOT NULL,
    modalidade VARCHAR(255) NOT NULL,
    submodalidade VARCHAR(255) NOT NULL,
    origem VARCHAR(100) NOT NULL,
    indexador VARCHAR(100) NOT NULL,
    numero_de_operacoes BIGINT NOT NULL,

    a_vencer_ate_90_dias DECIMAL(20, 2) NOT NULL,
    a_vencer_de_91_ate_360_dias DECIMAL(20, 2) NOT NULL,
    a_vencer_de_361_ate_1080_dias DECIMAL(20, 2) NOT NULL,
    a_vencer_de_1081_ate_1800_dias DECIMAL(20, 2) NOT NULL,
    a_vencer_de_1801_ate_5400_dias DECIMAL(20, 2) NOT NULL,
    a_vencer_acima_de_5400_dias DECIMAL(20, 2) NOT NULL,

    carteira_a_vencer DECIMAL(20, 2) NOT NULL,
    vencido_de_15_ate_90_dias DECIMAL(20, 2) NOT NULL,
    vencido_acima_de_90_dias DECIMAL(20, 2) NOT NULL,

    carteira_vencida DECIMAL(20, 2) NOT NULL,
    carteira_ativa DECIMAL(20, 2) NOT NULL,
    carteira_inadimplencia DECIMAL(20, 2) NOT NULL,
    ativo_problematico DECIMAL(20, 2) NOT NULL,

    PRIMARY KEY (id),
    -- Otimizo consultas que filtram ou ordenam os dados pela data-base.
    INDEX idx_bcb_data_base (data_base)
)
  -- Escolho InnoDB para ter suporte a transações e recuperação de falhas.
  ENGINE=InnoDB

  -- Mantenho utf8mb4 como padrão de texto desta tabela.
  DEFAULT CHARACTER SET=utf8mb4
  
  -- Uso comparações que não diferenciam letras maiúsculas e minúsculas.
  COLLATE=utf8mb4_unicode_ci;
