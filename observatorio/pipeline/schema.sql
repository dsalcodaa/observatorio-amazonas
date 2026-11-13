-- Modelo de dados do Observatório Amazonas (seção 7 da especificação).
-- SQL portável: roda em SQLite (protótipo) e migra para PostgreSQL/PostGIS sem mudar a estrutura.
-- Regras: nulo nunca vira zero; valor original guardado ao lado do normalizado; toda linha aponta para documento e página.

CREATE TABLE IF NOT EXISTS ppa_version (
  id TEXT PRIMARY KEY, nome TEXT NOT NULL, instrumento_legal TEXT, data_publicacao TEXT,
  vigencia_inicial TEXT, vigencia_final TEXT, status TEXT CHECK (status IN ('vigente','substituida','historica')),
  documento_id TEXT, justificativa TEXT
);
CREATE TABLE IF NOT EXISTS document (
  id TEXT PRIMARY KEY, titulo TEXT, tipo TEXT, url TEXT, arquivo TEXT, sha256 TEXT NOT NULL, bytes INTEGER,
  paginas INTEGER, data_publicacao TEXT, data_ingestao TEXT, ppa_version_id TEXT, exercicio INTEGER
);
CREATE TABLE IF NOT EXISTS result_area (
  id TEXT PRIMARY KEY, nome TEXT NOT NULL, nomes_originais TEXT  -- JSON: grafias encontradas por documento
);
CREATE TABLE IF NOT EXISTS organization (
  id TEXT PRIMARY KEY, nome TEXT, sigla TEXT, tipo TEXT, orgao_superior TEXT, status TEXT
);
CREATE TABLE IF NOT EXISTS program (
  id TEXT PRIMARY KEY, codigo TEXT NOT NULL, nome TEXT, tipo TEXT, abrangencia TEXT, area_resultado_id TEXT,
  objetivo TEXT, publico_alvo TEXT, orgao_responsavel TEXT, orgaos_participantes TEXT, ods TEXT,
  ppa_version_id TEXT, documento_id TEXT, pagina INTEGER, confianca TEXT
);
CREATE TABLE IF NOT EXISTS indicator (
  id TEXT PRIMARY KEY, program_id TEXT, nome TEXT NOT NULL, unidade TEXT, periodicidade TEXT,
  polaridade TEXT CHECK (polaridade IN ('maior_melhor','menor_melhor','faixa','indefinida')),
  polaridade_origem TEXT,           -- 'documento' | 'inferida' (precisa validação humana)
  tipo TEXT DEFAULT 'resultado',    -- indicador de programa (resultado); produtos de ação ficam em action_delivery
  formula TEXT, fonte_preferencial TEXT, responsavel TEXT, observacoes TEXT, status_cadastro TEXT DEFAULT 'oficial'
);
CREATE TABLE IF NOT EXISTS indicator_target (
  id TEXT PRIMARY KEY, indicator_id TEXT NOT NULL, ppa_version_id TEXT, exercicio INTEGER, valor REAL, valor_original TEXT,
  unidade TEXT, territorio TEXT DEFAULT 'AM', orgao TEXT, documento_id TEXT, pagina INTEGER
);
CREATE TABLE IF NOT EXISTS indicator_observation (
  id TEXT PRIMARY KEY, indicator_id TEXT NOT NULL, data_referencia TEXT, valor REAL, valor_original TEXT, unidade TEXT,
  territorio TEXT DEFAULT 'AM', fonte TEXT, documento_id TEXT, pagina INTEGER, data_publicacao TEXT, data_ingestao TEXT,
  status_qualidade TEXT,            -- 'extraido_documento' | 'oficial_publicado' | 'calculado' | 'estimado' | 'preliminar' | 'em_validacao'
  pct_publicado REAL, pct_publicado_original TEXT, analise TEXT
);
CREATE TABLE IF NOT EXISTS document_extraction (
  id TEXT PRIMARY KEY, document_id TEXT, pagina INTEGER, secao TEXT, tabela TEXT, texto TEXT, confianca TEXT, status_revisao TEXT
);
CREATE TABLE IF NOT EXISTS ingestion_run (
  id TEXT PRIMARY KEY, data_hora TEXT, fonte TEXT, registros_recebidos INTEGER, registros_aceitos INTEGER,
  registros_rejeitados INTEGER, status TEXT, log TEXT, hash_arquivo TEXT
);
