-- Script SQL para criação do banco de dados do Sistema de Gestão Logística

-- Criação da tabela Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    id SERIAL PRIMARY KEY,
    nome_usuario VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(20) NOT NULL DEFAULT 'operador',
    ativo BOOLEAN DEFAULT TRUE
);

-- Criação da tabela Clientes
CREATE TABLE IF NOT EXISTS Clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cnpj_cpf VARCHAR(20) UNIQUE,
    contato VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(100)
);

-- Criação da tabela Materiais
CREATE TABLE IF NOT EXISTS Materiais (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    descricao TEXT NOT NULL,
    localizacao VARCHAR(100) NOT NULL,
    unidade_medida VARCHAR(10)
);

-- Índices para a tabela Materiais para otimizar o Finder
CREATE INDEX IF NOT EXISTS idx_materiais_codigo ON Materiais (codigo);
CREATE INDEX IF NOT EXISTS idx_materiais_descricao_trgm ON Materiais USING gin (descricao gin_trgm_ops);

-- Criação da tabela Estoque
CREATE TABLE IF NOT EXISTS Estoque (
    id SERIAL PRIMARY KEY,
    material_id INTEGER NOT NULL REFERENCES Materiais(id),
    quantidade NUMERIC(10,2) NOT NULL,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_movimento VARCHAR(20),
    referencia_movimento VARCHAR(100)
);

-- Criação da tabela OrdensServico
CREATE TABLE IF NOT EXISTS OrdensServico (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES Clientes(id),
    numero_os VARCHAR(50) UNIQUE NOT NULL,
    data_criacao DATE NOT NULL,
    descricao TEXT
);

-- Criação da tabela Pedidos
CREATE TABLE IF NOT EXISTS Pedidos (
    id SERIAL PRIMARY KEY,
    os_id INTEGER NOT NULL REFERENCES OrdensServico(id),
    numero_pedido VARCHAR(50) UNIQUE NOT NULL,
    data_solicitacao DATE NOT NULL,
    data_despacho_prevista DATE,
    status VARCHAR(20) DEFAULT 'pendente'
);

-- Criação da tabela ItensPedido
CREATE TABLE IF NOT EXISTS ItensPedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES Pedidos(id),
    material_id INTEGER NOT NULL REFERENCES Materiais(id),
    quantidade_solicitada NUMERIC(10,2) NOT NULL,
    quantidade_despachada NUMERIC(10,2) DEFAULT 0
);

-- Criação da tabela IluminacaoPublicaPontos
CREATE TABLE IF NOT EXISTS IluminacaoPublicaPontos (
    id SERIAL PRIMARY KEY,
    bairro VARCHAR(50) NOT NULL,
    descricao_problema TEXT NOT NULL,
    data_registro DATE NOT NULL,
    rota VARCHAR(10),
    status VARCHAR(20) DEFAULT 'pendente'
);

-- Adicionar extensão pg_trgm para otimização de busca por similaridade na descrição
CREATE EXTENSION IF NOT EXISTS pg_trgm;
