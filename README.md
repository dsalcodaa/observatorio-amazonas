# Plataforma de Gestão Governamental — Amazonas (protótipo)

Protótipo de monitoramento dos indicadores do *Plano Estratégico de Desenvolvimento do Amazonas* (e-books Eixos 01–03) e de projetos das secretarias de estado.

## Como abrir
Abra `dashboard/plataforma.html` no navegador (não precisa de servidor). O catálogo dos indicadores está em `dashboard/index.html`.

## Observatório Amazonas (painel com dados públicos)
Online: https://dsalcodaa.github.io/observatorio-amazonas/ (publicado pelo GitHub Actions a cada push na `main`).
Servidor local na raiz: `python -m http.server 8765` → `http://127.0.0.1:8765/observatorio/painel.html`.
Atualizar dados: `python -I observatorio/pipeline/p05_ampliacao.py --atualizar` (roda o P04 e acrescenta Censo 2022 por município e bairro, favelas e comunidades urbanas, TSE 2026, CNES georreferenciado e leitos, INEP Censo Escolar e Superior, OSM, SIDRA economia e produção rural, IFDM, ANA, DNIT, a base local da SEINFRA, ANEEL/SIGA, EPE, SSP-AM (unidades policiais e Anuário) e escolas georreferenciadas do geobr/IPEA).
- Base local da SEINFRA: pasta em `OBS_INFRA` (padrão `D:\Pedro\2-POWER BI  E PROJETOS\5-RODOVIAS\7-MAPEAMENTO GEO\3-DADOS INFRAESTRUTURA`).
- IFDM: o site da FIRJAN bloqueia robôs; baixe a "Série Histórica IFDM" pelo navegador para `observatorio/bronze/publicos/firjan/ifdm_serie_2013_2023.xlsx`.
- Requer `pip install pyshp`. Detalhes em `Sessao_Continuacao.md`.

## O que tem
- **Catálogo do plano**: 610 indicadores em 31 áreas, com fichas e trechos dos PDFs.
- **Sala do Governador**: consolidado por secretaria, pontos de atenção, determinações.
- **Secretarias**: indicadores, projetos, ações, equipe e conversa com o governador; cada perfil vê só o próprio escopo.
- **Projetos**: métricas próprias com medições, orçamento e histórico, marcos, riscos, anexos, mapa por município, relatório em PDF.
- **Modelos de projeto** (13) e **carteira de exemplo** com 67 projetos simulados.

## Dados
- Indicadores: `Indicadores_Monitoramento_Eixos_01_02_03.md` → `python gerar_dados.py` gera `dados.js` e `indicadores.csv`.
- Estrutura do Executivo: Portal da Transparência AM → `gerar_orgaos.py` gera `orgaos.js`.
- Municípios: APIs públicas do IBGE → `gerar_municipios.py` gera `municipios.js`.
- Os PDFs não estão no repositório (tamanho); os links "ver no PDF" esperam os arquivos na pasta raiz.

## Limitações
Protótipo: dados salvos só no navegador (localStorage), perfis simulados sem login. Projetos de exemplo são fictícios e marcados "(exemplo)".
