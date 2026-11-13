# Sessão — Plano Estratégico de Desenvolvimento do Amazonas (Eixos 01, 02, 03)

Data: 10/11/2026. Arquivo para retomar o trabalho em outra conversa.

## Contexto
Análise dos e-books públicos "Plano Estratégico de Desenvolvimento do Amazonas" (site omargovernador.com.br, coordenação Omar Aziz, PSD, distribuição gratuita, 2026), divididos em Eixo 01, 02 e 03.

## Pedidos feitos e status
1. Baixar os PDFs dos eixos 01, 02 e 03 via Playwright — **concluído**.
2. Ler cada PDF e gerar um MD por livro — **concluído**.
3. Listar todos os indicadores de monitoramento dos 3 eixos por área — **concluído**.
4. Salvar MD da conversa — este arquivo.

## Arquivos (raiz deste repositório)
| Arquivo | Conteúdo |
|---|---|
| `EBOOK-LIVRO-OMAR-Plano-estrategico-de-desenvolvimento-Eixo01.pdf` | Eixo 01, 633 p., 112 MB |
| `EBOOK-LIVRO-OMAR-Plano-estrategico-de-desenvolvimento-Eixo02.pdf` | Eixo 02, 501 p., 68 MB |
| `EIXO_DE_DESENVOLVIMENTO-OMAR_AZIZ-EIXO3.pdf` | Eixo 03, 609 p., 26 MB |
| `Eixo01_Plano_Estrategico_Desenvolvimento.md` | Resumo do Eixo 01 |
| `Eixo02_Seguranca_Saude_Assistencia_Social.md` | Resumo do Eixo 02 |
| `Eixo03_Educacao_MeioAmbiente_Cultura_e_outros.md` | Resumo do Eixo 03 |
| `Indicadores_Monitoramento_Eixos_01_02_03.md` | Indicadores de monitoramento por eixo e área |
| `Sessao_Continuacao.md` | Este arquivo |

## Áreas por eixo
- **Eixo 01:** Fiscal, Reforma Tributária, ZEE, Regularização Fundiária, Infraestrutura/Logística, Energia, Fruticultura, Aquicultura, Florestais, Indústria, Comércio, Mineração, Turismo, Fitofármacos, Serviços Ambientais, CT&I, IA, Economia Criativa, Atração de Investimentos.
- **Eixo 02:** Segurança Pública, Saúde, Assistência Social.
- **Eixo 03 (páginas do PDF):** Educação 9–147, Meio Ambiente 148–257, Cultura 258–334, FAPEAM 335–367, CETAM 368–396, Habitação 397–465, Governo Digital 466–517, Indigenista 518–568, Outros órgãos 569–573, Final/Anexo 574–598.

## Pendências e ressalvas
- Fruticultura (p. 205) e Aquicultura (p. 225) do Eixo 01: quadros de indicadores em imagem; exigiriam OCR ou leitura manual.
- Fiscal, Reforma Tributária e Indústria: o livro não traz indicadores.
- Saúde (Eixo 02): o livro diverge consigo mesmo. A vacinação tem base de 79% num trecho e 66,6% (DTP3) em outro. A meta de mortalidade materna aparece como <50, <40 e 35.
- Meio Ambiente (Eixo 03): os títulos dos objetivos 1–13 no MD de indicadores são resumos meus; só o objetivo 14 é texto fiel.
- FAPEAM: o original diz "tempo de resposta <50%", interpretado como redução >50%.

## Método técnico (para refazer extrações)
- Texto extraído com PyMuPDF (pymupdf) e pdftotext.
- Hierarquia por tamanho de fonte: capítulo ≥ 27,5 pt; seção ≥ 21,5 pt; subtítulo ≥ 13 pt; texto de tabela < 8,5 pt.
- Os JSONs intermediários ficaram na pasta temporária da sessão anterior e podem ter sido apagados; regenerar a partir dos PDFs se necessário.

## Dashboard (11/11/2026)
Pasta `dashboard\`: `index.html` (abre direto no navegador), `dados.js` (gerado), `indicadores.csv` (gerado, separador `;`), `gerar_dados.py` (lê o MD de indicadores e gera os dois).
- 610 indicadores em 31 áreas (28 com indicadores). Campos: id, eixo, área, grupo, indicador, base, meta, prazo, responsável, valor_atual, data_referencia, fonte_dado, observacao.
- Fruticultura e Aquicultura: confirmado que não há quadro de indicadores (as páginas eram fotos); entraram as entregas do plano de ação.
- Para mudar indicadores: editar o MD e rodar `python gerar_dados.py`. Os IDs dependem da ordem no MD.
- Aba "Fichas dos indicadores": clicar num indicador mostra base/meta/prazo/responsável e até 2 trechos do PDF que o explicam, com link para a página. Os trechos são localizados automaticamente por `gerar_dados.py` (busca pelos termos do indicador no capítulo da área; tabela `CAPITULOS` no script). 4 indicadores ficaram sem trecho (tCO₂e x2, P&D, Editais PPBIO e FAPEAM).
- Saúde corrigida pelo Quadro 15 (p. 367): mortalidade materna 94 → 68 → < 50; desertos críticos 29 → 15 → ≤ 5; IDH-H 2028 = 62.
- Próximo passo: definir como alimentar `valor_atual` (planilha, Supabase ou coletores de fontes oficiais).

## Plataforma de monitoramento — versão inicial (11/11/2026)
`dashboard\plataforma.html` (abre direto no navegador). Usa `dados.js` (indicadores) e `orgaos.js` (estrutura do Executivo).
- Estrutura: capturada via Playwright de https://www.transparencia.am.gov.br/estrutura-organizacional/ (atualizada no portal em 31/10/2026). HTML bruto em `dashboard\fonte\`; `gerar_orgaos.py` gera `orgaos.js` (76 órgãos, titular, categoria, vínculo).
- Telas: Sala do Governador (consolidado por secretaria, pontos de atenção, determinações, feed); Distribuição de indicadores (sugestão automática + atribuição individual/lote); Secretarias (indicadores com valor/data/fonte/situação/responsável, ações, equipe, conversa com o governador); Estrutura do Executivo.
- Órgão vinculado (ex.: IDAM) sobe para a secretaria supervisora (SEPROR).
- Perfis simulados no seletor "Atuando como" (Governador, titular, membro de equipe) — sem login real.
- Dados salvos só no navegador (localStorage), com exportar/importar JSON. Para uso multiusuário real: backend (Supabase) + login.
- Sugestões de órgão por área são minhas (tabela `SUG_AREA` em `plataforma.js`) — precisam ser validadas.

### Versão 2 (11/11/2026) — escopo por perfil + projetos
- Código em `plataforma.js` (HTML só tem CSS e estrutura).
- Perfil de secretaria (titular ou membro) vê só a própria secretaria e os vinculados: menu reduzido a "Minha secretaria" e "Projetos"; rotas de outras secretarias/Sala do Governador redirecionam.
- Módulo **Projetos**: cadastro (nome, executor, tipo, situação, descrição, municípios, início/prazo, gerente, responsáveis, orçamento previsto/empenhado/pago, fonte, indicadores do plano relacionados); dashboard por projeto com execução física (média do progresso das métricas, ou marcos), execução financeira (pago/previsto), métricas próprias com meta, base e medições datadas + gráfico, orçamento em barras, marcos com prazo, comentários (secretaria ↔ governador) e histórico.
- Alertas de projeto: prazo final vencido, paralisado, marco atrasado, financeiro >25 pontos à frente do físico.
- Sala do Governador consolida projetos por secretaria (ativos, com alerta, orçamento).
- Botão "Carregar 2 projetos de exemplo" (20 casas/SUHAB e 20 leitos de UTI/SES), marcados "(exemplo)".

### Versão 3 (11/11/2026) — mapa, riscos, anexos, histórico do orçamento, relatório
- **Mapa por município**: `municipios.js` (62 municípios do AM, contorno em SVG) gerado por `gerar_municipios.py` a partir das APIs públicas do IBGE. Na tela Projetos: mapa colorido pelo número de projetos, tabela por município (projetos, orçamento, com alerta) e clique para filtrar. O campo Município(s) do projeto sugere os nomes do IBGE e recusa nomes não reconhecidos (aceita sem acento/minúscula).
- **Histórico do orçamento**: cada atualização (no dashboard, com data, ou na edição do projeto) grava um registro em `orcHist`; tabela no card Orçamento.
- **Riscos**: probabilidade × impacto, mitigação, responsável, situação (Aberto/Em tratamento/Encerrado). Risco Alta × Alto aberto gera alerta no projeto e na Sala do Governador.
- **Anexos**: aba no projeto; arquivo até 1 MB (foto aparece em miniatura) ou link (SEI, Drive). Arquivos ficam no localStorage (limite ~5 MB no total; o sistema avisa se faltar espaço).
- **Relatório (PDF)**: botão no projeto e na Sala do Governador; abre a impressão do navegador (escolher "Salvar como PDF"), sem menus nem formulários.

### Versão 4 (11/11/2026) — modelos de projeto e carteira simulada
- `dashboard\exemplos.js`: 13 **modelos** (obra de edificação, obra linear, reforma, aquisição, serviço continuado, programa social, capacitação, sistema/TI, programa estruturante com financiamento externo, campanha/mutirão, regularização/licenciamento, evento, operação integrada). Cada um tem métricas, marcos e riscos típicos.
- **Carteira de exemplo**: 67 projetos fictícios em 47 órgãos, gerados de forma determinística com datas relativas ao dia da carga. Perfis: no rumo, atrasado, paralisado, concluído, planejamento, financeiro adiantado e prazo vencido. Incluem medições mensais (curva S), histórico do orçamento, marcos, riscos e comentários governador ↔ secretaria nos projetos com problema. Alguns estão ligados a indicadores do plano.
- Projetos → "Carregar carteira de exemplo" / "Remover projetos de exemplo" (remove também os 2 exemplos da v2).
- Nova tela **Modelos de projeto**; "+ Novo projeto" permite escolher o modelo, a unidade e a meta, e cria o projeto já com métricas, marcos (prazos proporcionais entre início e fim) e riscos.
- Tela Projetos ganhou "Carteira por tipo de projeto". Novos tipos: Capacitação, Programa estruturante, Campanha/mutirão, Evento, Operação.

## Possíveis próximos passos
- OCR dos quadros de Fruticultura e Aquicultura.
- Converter os indicadores em planilha (xlsx) ou painel.
- Cruzar metas entre eixos (ex.: conectividade, telessaúde, desmatamento aparecem em mais de um eixo).

## Observatório Amazonas — Fase 1 (12/11/2026)

Especificação: `especificacao_observatorio_amazonas.md`. Pasta `observatorio/`:

- `fontes/documentos.json`: registro dos 9 documentos oficiais (Lei 6.671/2023, Lei 7.978/2025, PPA de Bolso, Avaliações 2024 e 2025, RAG, manuais).
- `pipeline/p01_documentos.py`: baixa para `bronze/documentos/` com SHA-256 e gera `dados/document.json`.
- `pipeline/p02_paginas.py`: texto por página em `silver/paginas/*.jsonl`.
- `pipeline/p03_avaliacao.py`: lê as tabelas de indicadores dos Relatórios de Avaliação. O OCR (Tesseract, português, 300 dpi, cache em `silver/ocr/`) lê as células. A camada de texto do PDF confere os dígitos. Se divergir, usa os dígitos do texto com a vírgula do OCR e marca "em validação". Gera `dados/observatorio.sqlite` (modelo em `pipeline/schema.sql`) e `dados/ppa.json`/`ppa.js`.
- `index.html`: catálogo com indicadores (filtros por exercício, área, programa, status e busca), ficha do indicador (meta × apurado, linha do tempo, link para a página do PDF), programas por área e documentos/ingestões.

Resultado: 11 áreas de resultado, 23 programas, 109 indicadores, 247 linhas (89 de 2024 e 158 de 2025), 0 rejeitadas, 18 em validação. Polaridade é inferida pelo nome e precisa de validação humana.

Pendente: Anexo I (entregas e orçamento por região), metas 2026–2027 da Lei 7.978, anexos da Lei 6.671. Para rodar: `python -I pipeline/p01_documentos.py`, depois `p02` e `p03`, a partir da pasta `observatorio/`. Tesseract em `C:\Program Files\Tesseract-OCR` com `por.traineddata` em `%LOCALAPPDATA%\tessdata`.

## Observatório Amazonas — Fase 2: painel com fontes públicas (12/11/2026)

`observatorio/painel.html` (estrutura de admin no padrão Velzon, identidade própria "Encontro das Águas"). Abrir por servidor local, a partir da raiz do repositório: `python -m http.server 8765` e acessar `http://127.0.0.1:8765/observatorio/painel.html`. Também abre direto no navegador (file://).

- Telas: Visão geral, Socioeconomia, Educação, Saúde, Segurança pública, Meio ambiente, Infraestrutura, PPA 2024–2027, Municípios (lista e ficha por município), Fontes de dados.
- Cada área: cartões com ano e fonte (marca oficial/calculado/mediana), série do estado, metas do PPA da área com status, mapa coroplético dos 62 municípios (quantis, hachura = sem dado) e tabela ordenável.
- Gráficos em SVG próprio (sem CDN, funciona offline). Paleta de dados validada (skill dataviz).

Pipeline `observatorio/pipeline/p04_publicos.py` (cache em `bronze/publicos/`, `--atualizar` baixa de novo) gera `dados/painel.json` e `dados/painel.js`. 31 indicadores:
- IBGE/SIDRA: Censo 2022 (população, área, densidade, água, esgoto, lixo, alfabetização), estimativas 2001–2026, PIB municipal 2002–2023, valor adicionado por setor (2021, último com setores).
- INEP: IDEB 2005–2023 rede pública, anos iniciais e finais, por município (o arquivo não traz o estado; o painel mostra a mediana municipal, marcada).
- INPE: PRODES por município 2001–2024; focos de calor (satélite de referência AQUA_M-T) 2003–2026, anual + mensal.
- MJSP/SINESP VDE (BancoVDE 2019–2026, xlsx do gov.br): CVLI, homicídio, feminicídio, latrocínio, trânsito etc.; taxa CVLI por 100 mil calculada com a população IBGE.
- DATASUS/CNES (API): 4.612 estabelecimentos; unidades de atenção básica por 10 mil hab.
- GeoTática: 228 fontes nacionais/AM em temas do Observatório, de 2.185 do catálogo (extraído do script.js do site).

Decisões e ressalvas:
- API rayonnunes/api_seguranca_publica: endpoint de produção HTTP sem resposta em 12/11/2026. Usada como referência; os dados vêm do arquivo oficial do MJSP que ela espelhava.
- PIB per capita 2023: IBGE não estimou a população de 2023; usa a média entre Censo 2022 e estimativa 2024 (registrado no método).
- CNES: o parâmetro `offset` da API é número de página.
- Taxa CVLI: série anual só com anos completos; 2026 é parcial (até set/2026).
- Arquivos PRODES 2025/2026 ainda não publicados; o pipeline tenta de novo a cada execução com `--atualizar`.
- Classes de cor do mapa indicam magnitude, não avaliação (ranking neutro, conforme a especificação).

Pendente: alfabetização/IDEB estadual oficial, mortalidade infantil e vacinação (DATASUS/SIM/SINASC), conectividade, obras/orçamento (Fases 3–4 da especificação).

## Fase 3 — ampliação (2026-11-12)
- Pipeline `observatorio/pipeline/p05_ampliacao.py` (importa o P04). Saídas: `dados/painel.js`, `dados/territorio.js` (bairros, comunidades, pirâmides, eleitorado, escolas, IES, produção rural), `dados/camadas.js` (pontos e linhas com x,y na projeção da malha IBGE).
- Fontes novas: Censo 2022 agregados por município e bairro (FTP IBGE), malha de bairros AM, Favelas e Comunidades Urbanas 2022, API de malhas IBGE, TSE perfil do eleitor por seção 2026 + locais de votação (ponto no polígono do bairro; fallback pelo nome do bairro), CNES com coordenadas, API hospitais e leitos (série sem competência: guarda o último registro de cada hospital), INEP Censo Escolar 2024 e Superior 2023 (download com TLS SECLEVEL=1), OSM via espelho Overpass mail.ru, SIDRA 5938/6449/5457/289/3939/3940/74/6778/6881, IFDM FIRJAN (manual), ANA Atlas Esgotos, DNIT GeoServer WFS (`servicos.dnit.gov.br/dnitgeo/geoserver/ows`), base local SEINFRA.
- Painel: menu em grupos (Pessoas, Economia, Serviços públicos, Infraestrutura, Território, Planejamento e dados); páginas Demografia, Eleitorado, Economia e renda, Produção rural, Transporte, Cidades, Saneamento; página Bairros e comunidades (`#/bairros/<cod>`); ficha do município com pirâmide, eleitorado, equipamentos, mapa com camadas e produção rural.

### Situação em 13/11/2026
- Leitos: trocada a API JSON (sem competência, hospitais repetidos, ~19 mil leitos inflados) pelo CSV anual do OpenDataSUS `Leitos_AAAA.csv` (competência 04/2025: 113 hospitais, 7.475 leitos, 6.177 SUS, 807 UTI). Páginas da API (~1,5 GB) apagadas.
- BDQueimadas 286.354 está certo: só satélite de referência (AQUA); os 721 mil antigos somavam todos os satélites dos mensais.
- SEINFRA-AM recarregada com o drive D: conectado (961 registros, 109 indicadores no total). Sem o drive, o pipeline roda mas o painel perde Transporte.

### Para retomar (próxima sessão)
1. Servidor: na raiz `Omar_Eixos`, `python -m http.server 8765` → http://127.0.0.1:8765/observatorio/painel.html
2. Atualizar dados (com drive D: conectado): em `observatorio/`, `python -I pipeline/p05_ampliacao.py`
3. Repositório público: https://github.com/dsalcodaa/observatorio-amazonas (remoto `observatorio`; o `origin` antigo é plataforma-gestao-amazonas). Site: https://dsalcodaa.github.io/observatorio-amazonas/ — o workflow `.github/workflows/pages.yml` publica a cada push na `main`. Para atualizar dados: rodar o p05, fazer commit e `git push observatorio main`.
4. Prints conferidos em 13/11/2026 no site publicado: Energia, Segurança, Eleitorado, Demografia (1440 px) e Energia no celular (390 px, sem rolagem horizontal).

### Pendências resolvidas em 13/11/2026 (p05)
- **Energia e telecomunicações** (página nova): usinas do SIGA/ANEEL (CSV de dados abertos, base 01/11/2026; 181 usinas no AM, 160 em operação, 2.709 MW, 89% térmica fóssil); ERBs (1.378) e gasodutos/oleodutos (86 trechos) da base EPE em `3-DADOS INFRAESTRUTURA/10-AMAZONIA LEGAL INFRAESTRUTURA`. A pasta `7-ENERGIA` (IBGE BC250 2017) quase não cobre o AM e não foi usada. A base EPE não tem data; o ano é o do arquivo. Nomes com acento perdido (U+FFFD) são recuperados quando são nome de município (`repara`).
- **Delegacias**: a SSP-AM publica um mapa ArcGIS (ssp.am.gov.br/ssp-dados, webmap db1a7ff8c16747e69c3ecbf452e4e508). O pipeline lê as camadas `publicação_de_várias_camadas` (Manaus: 30 DIPs, especializadas, PM, bombeiros) e `Sede_unidades_policiais_gdb` (61 sedes da PM no interior): 173 unidades. Delegacias do interior não estão no mapa. OSM ficou só como reserva (`osm_seguranca`).
- **Arquivo estadual**: o SINESP 2022–2023 já estava completo. A fonte estadual é o Anuário do Amazonas de Segurança Pública 2026 (SSP-AM/CIESP), xlsx em link público do SharePoint (download exige o cookie da primeira visita). Entraram homicídio doloso por município 2017–2025, série estadual 2000–2025, taxa e efetivo policial. Confere com o SINESP: 1.321 × 1.320 (2022), 1.254 × 1.246 (2023). A planilha grafa "NAHMUNDA" (tratado).
- **Escolas georreferenciadas**: coordenadas do Catálogo de Escolas do INEP via geobr/IPEA (schools_2023.gpkg, 101 MB). 3.812 das 5.542 escolas do Censo 2024 casaram pelo código INEP (69%). Mapa na página Educação e camada no mapa do município.
- Painel: 117 indicadores.
