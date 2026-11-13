# Plataforma de Gestão Governamental — Amazonas (protótipo)

Documentação completa do trabalho feito em 10 e 11/11/2026: da leitura dos e-books do Plano Estratégico até a plataforma publicada no GitHub.

- **Plataforma online:** https://dsalcodaa.github.io/plataforma-gestao-amazonas/dashboard/plataforma.html
- **Catálogo de indicadores online:** https://dsalcodaa.github.io/plataforma-gestao-amazonas/dashboard/index.html
- **Repositório (público):** https://github.com/dsalcodaa/plataforma-gestao-amazonas
- **Pasta local:** `Downloads\Omar_Eixos` (é o próprio repositório git)

---

## 1. Objetivo

Construir uma "super plataforma" de controle de indicadores e monitoramento de projetos, em que as secretarias de estado conversam com seus secretários, equipes e o governador. A base são o *Plano Estratégico de Desenvolvimento do Amazonas* e a estrutura oficial do Poder Executivo.

## 2. Fontes (todas públicas)

| Fonte | Uso |
|---|---|
| E-books "Plano Estratégico de Desenvolvimento do Amazonas", Eixos 01, 02 e 03 (omargovernador.com.br, distribuição gratuita, 2026) | Indicadores, metas, prazos, responsáveis e trechos explicativos |
| Portal da Transparência AM — Estrutura Organizacional (https://www.transparencia.am.gov.br/estrutura-organizacional/, atualizado em 31/10/2026; Leis Delegadas 122 e 123/2019) | 76 órgãos, titulares, categorias e vínculos |
| IBGE — APIs de malhas e localidades | Contorno e nomes dos 62 municípios do AM |

## 3. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `EBOOK-...-Eixo01.pdf`, `...-Eixo02.pdf`, `EIXO_...-EIXO3.pdf` | E-books (633, 501 e 609 páginas). **Não vão para o GitHub** (206 MB; limite de 100 MB por arquivo) |
| `Eixo01_...md`, `Eixo02_...md`, `Eixo03_...md` | Resumo de cada livro |
| `Indicadores_Monitoramento_Eixos_01_02_03.md` | Lista de indicadores por eixo e área. **Fonte da verdade** dos indicadores |
| `Sessao_Continuacao.md` | Notas para retomar o trabalho, versão a versão |
| `Plataforma_Gestao_AM_Documentacao.md` | Este documento |
| `README.md`, `.gitignore` | Apresentação do repositório; `.gitignore` exclui os PDFs |
| `dashboard/index.html` | Catálogo do plano: painel por área e fichas dos indicadores |
| `dashboard/plataforma.html` + `plataforma.js` | A plataforma (estilo no HTML, lógica no JS) |
| `dashboard/dados.js`, `indicadores.csv` | Indicadores gerados por `gerar_dados.py` |
| `dashboard/orgaos.js` | Órgãos gerados por `gerar_orgaos.py` a partir de `fonte/estrutura_organizacional_2026-11-11.json` |
| `dashboard/municipios.js` | Municípios gerados por `gerar_municipios.py` |
| `dashboard/exemplos.js` | Modelos de projeto e gerador da carteira simulada |

## 4. Histórico do trabalho

1. **PDFs** baixados com Playwright.
2. **Um MD por livro**, com texto extraído por PyMuPDF/pdftotext. A hierarquia vem do tamanho da fonte: capítulo ≥ 27,5 pt; seção ≥ 21,5 pt; subtítulo ≥ 13 pt; tabela < 8,5 pt.
3. **Lista de indicadores** de monitoramento por área.
4. **Dashboard/catálogo** (`index.html`) com abas Painel e Fichas.
5. **Plataforma v1:** estrutura do Executivo, distribuição de indicadores, telas de secretaria e Sala do Governador.
6. **v2:** perfil de secretaria vê só o próprio escopo; módulo Projetos com dashboard por projeto.
7. **v3:** mapa por município, histórico do orçamento, riscos, anexos e relatório em PDF.
8. **v4:** 13 modelos de projeto e carteira simulada de 67 projetos em 47 órgãos.
9. **Publicação** no GitHub. Os commits usam o e-mail anônimo do GitHub. O repositório é público, com GitHub Pages ativo.

## 5. Indicadores do plano

- **610 indicadores em 31 áreas**, das quais 28 têm indicadores.
  - **Eixo 01:** Fiscal, Reforma Tributária, ZEE, Regularização Fundiária, Infraestrutura/Logística, Energia, Fruticultura, Aquicultura, Florestais, Indústria, Comércio, Mineração, Turismo, Fitofármacos, Serviços Ambientais, CT&I, IA, Economia Criativa, Atração de Investimentos.
  - **Eixo 02:** Segurança Pública, Saúde, Assistência Social.
  - **Eixo 03:** Educação, Meio Ambiente, Cultura, FAPEAM, CETAM, Habitação, Governo Digital, Política Indigenista.
- **Campos:** id (ex.: `E2-A21-001`), eixo, área, grupo, indicador, base, meta, prazo, responsável, valor_atual, data_referencia, fonte_dado, observação e trechos do PDF.
- **Fichas:** ao clicar num indicador aparecem base, meta, prazo, responsável e até 2 trechos do PDF que o explicam, com link para a página. Os trechos foram localizados automaticamente em 606 dos 610 indicadores. Ficaram sem trecho: tCO₂e (2), P&D e "Editais PPBIO e FAPEAM".
- **Ajustes feitos no MD de indicadores:**
  - Fruticultura e Aquicultura: o plano não publica quadro de indicadores (as páginas eram fotos). Entraram as entregas do plano de ação, com prazo e responsável.
  - Saúde: refeita pelo Quadro 15 (p. 367).
    - Glosa: 11,3% → 6,0% → < 5,0%.
    - UTI por 100 mil habitantes: 5,2 → 6,5 → 8,0.
    - Mortalidade materna: 94 → 68 → < 50.
    - Vacinação: 79% → 92% → 95%.
    - Desertos críticos: 29 → 15 → ≤ 5.
- **Inconsistências do próprio plano:**
  - Vacinação aparece com base 79% num trecho e 66,6% (DTP3) em outro.
  - A meta de mortalidade materna aparece como < 50, < 40 e 35.
  - Em Meio Ambiente, os títulos dos objetivos 1–13 são resumos; só o 14 é texto fiel.
  - FAPEAM: "tempo de resposta < 50%" foi lido como redução > 50%.
  - Fiscal, Reforma Tributária e Indústria não trazem indicadores.

## 6. Estrutura do Executivo

- **76 órgãos**, com sigla, nome, categoria, cargo, titular, site e vínculo.
- **Vínculos:** um órgão vinculado sobe para a secretaria supervisora. Exemplos: IDAM → SEPROR; SUHAB, COSAMA e UGPE → SEDURB; SNPH → SEINFRA; FVS, FCECON e FHEMOAM → SES; CETAM e UGPPADEAM → SEDUC; IPAAM → SEMA; FEPIAM e PROCON → SEJUSC.
- **Sugestão de órgão por indicador:** primeiro, a sigla citada como responsável no plano. Na falta dela, uma regra por grupo e depois uma tabela por área (`SUG_AREA` em `plataforma.js`). A tabela por área é proposta minha e **precisa ser validada**.

## 7. A plataforma, tela por tela

### Perfis ("Atuando como")
- **Governador:** vê tudo.
- **Titular de secretaria ou órgão:** vê e edita só a própria secretaria e os órgãos vinculados.
- **Membro de equipe:** cadastrado na aba Equipe da secretaria.
- Os perfis são **simulados, sem login**. Um perfil de secretaria que tenta abrir outra secretaria ou a Sala do Governador pelo endereço volta para a própria tela.

### Sala do Governador
- **Quadros-resumo:** projetos ativos, orçamento em projetos e % pago, projetos com alerta, indicadores com órgão, indicadores alimentados e mensagens não lidas.
- **Tabela por secretaria:** projetos ativos, com alerta, orçamento, indicadores alimentados, críticos, ações atrasadas, mensagens e última atualização.
- **Pontos de atenção:** projetos com alerta, indicadores críticos ou em atenção e ações atrasadas.
- **Determinações** para qualquer órgão e feed de conversas e atualizações.
- **Botão Relatório (PDF).**

### Distribuição de indicadores (Governador)
- **Filtros:** eixo, área, situação e busca.
- **Atribuição:** um indicador por vez ou em lote. Também dá para aplicar a sugestão em lote.

### Secretaria
- **Abas:** Projetos, Indicadores do plano (valor, data, fonte, situação e responsável), Ações (prazo, situação e % executado), Equipe e Conversa com o governador, com histórico de atualizações.

### Projetos
- **Lista:** filtros, quadros-resumo, carteira por tipo de projeto e mapa por município. Clicar num município filtra a lista.
- **Cadastro:** nome, órgão executor, tipo, situação, descrição, municípios (nomes do IBGE), início e prazo, gerente, responsáveis, orçamento previsto/empenhado/pago, fonte e indicadores do plano relacionados. Opcionalmente parte de um **modelo**.
- **Dashboard do projeto:**
  - Execução física e financeira.
  - Métricas próprias com medições datadas e gráfico até a meta.
  - Orçamento em barras e histórico do orçamento.
  - Marcos com prazo.
  - Riscos (probabilidade × impacto, mitigação, responsável e situação).
  - Indicadores do plano relacionados.
- **Outras abas:** Anexos (arquivo até 1 MB ou link), Comentários (secretaria ↔ governador) e Histórico.
- **Relatório (PDF):** usa a impressão do navegador, sem menus nem formulários.

### Modelos de projeto
Os 13 modelos estão listados com métricas, marcos e riscos. O botão "Usar este modelo" cria o projeto já preenchido.

### Estrutura do Executivo
Órgãos por categoria, com titular, vinculados, número de indicadores e projetos, e link para o site.

## 8. Regras de cálculo

| Item | Regra |
|---|---|
| Progresso de uma métrica | (último valor − base) / (meta − base), limitado a 0–100%. Funciona também para metas de redução (ex.: homicídios por mês) |
| Execução física | Média do progresso das métricas; sem métricas, a fração de marcos concluídos |
| Execução financeira | Pago / previsto |
| **Alerta de projeto** | Prazo final vencido; **ou** situação Paralisado; **ou** marco atrasado; **ou** financeiro mais de 25 pontos à frente do físico; **ou** risco Alta × Alto não encerrado |
| Nível do risco | Probabilidade (1–3) × impacto (1–3): ≥ 9 alto, ≥ 4 médio, abaixo disso baixo |
| Ação atrasada | Não concluída e com prazo vencido |

## 9. Modelos de projeto (13)

| Modelo | Tipo | Métricas principais |
|---|---|---|
| Obra — construção de edificações | Obra | Quantidade entregue; avanço físico (boletim) |
| Obra linear — rodovia, ramal, rede | Obra | Quantidade executada (km, ligações); avanço físico |
| Reforma / requalificação | Reforma | Quantidade reformada e entregue; avanço físico |
| Aquisição de bens e equipamentos | Aquisição | Quantidade recebida; distribuída / em operação |
| Serviço continuado | Serviço | Atendimentos acumulados; cumprimento do SLA |
| Programa social / transferência | Programa social | Beneficiários; municípios ativos; cadastros validados |
| Capacitação / formação | Capacitação | Concluintes; turmas; taxa de conclusão |
| Sistema / transformação digital | Sistema/Tecnologia | Módulos/serviços entregues; usuários ativos |
| Programa estruturante (financiamento externo) | Programa estruturante | Componentes; avanço ponderado; desembolso; beneficiários |
| Campanha / mutirão | Campanha/mutirão | Realizado; cobertura da população-alvo |
| Regularização / licenciamento / passivo | Serviço | Processos analisados; títulos/licenças/acordos |
| Evento / circuito cultural e turístico | Evento | Eventos realizados; público |
| Operação / ação integrada | Operação | Operações realizadas; ocorrências por mês (redução) |

Cada modelo traz de 5 a 8 marcos e de 2 a 4 riscos típicos, com mitigação.

## 10. Carteira de exemplo (simulada)

- **67 projetos fictícios em 47 órgãos**, todos com "(exemplo)" no título. Gerentes aparecem por cargo, sem nome de pessoa.
- **Como carregar:** em Projetos, "Carregar carteira de exemplo". Para apagar, "Remover projetos de exemplo"; os projetos cadastrados por você ficam.
- **Áreas cobertas:**
  - **Infraestrutura e habitação:** rodovias, ramais, pontes, terminais hidroviários, conjunto habitacional, saneamento, urbanização de igarapés.
  - **Saúde:** UTI, ambulâncias, ambulanchas, hospital regional, telessaúde, vacinação, cirurgias eletivas, acelerador linear, hemonúcleos.
  - **Educação:** escolas, reformas, notebooks, transporte fluvial, cursos técnicos, licenciatura indígena, programa com financiamento externo.
  - **Assistência e cidadania:** transferência de renda, cestas na estiagem, CRAS, água potável, documentos itinerantes, segurança alimentar indígena, cadeiras de rodas.
  - **Segurança:** operação contra homicídios, bases fluviais, viaturas, delegacia virtual, embarcações de resgate, unidade prisional, ressocialização.
  - **Meio ambiente e produção:** pagamento por serviços ambientais, queimadas, licenciamento, regularização fundiária, ATER, patrulhas mecanizadas, sanidade animal, agricultura familiar, entrepostos de pescado, piscicultura.
  - **Economia, cultura e gestão:** microcrédito, bolsas, abertura de empresas, festivais, bioeconomia, circuito cultural, restauro, arenas, governo digital, escola de governo, internet via satélite, malha fiscal com IA, dívida ativa, painel de obras, CNH social, eletrificação rural, gás natural.
- **Perfis simulados:** no rumo, atrasado, paralisado, concluído, planejamento, financeiro adiantado e prazo vencido.
- **Como os dados são gerados:**
  - A geração é determinística: a mesma carteira sai a cada carga, com datas contadas a partir do dia em que é carregada.
  - As medições são mensais e seguem uma curva S.
  - Cada projeto tem histórico de orçamento, marcos cumpridos conforme o avanço e riscos.
  - Os projetos com problema já trazem a cobrança do governador e a resposta da secretaria.
  - 8 projetos ficaram ligados a indicadores do plano.
- **Resultado na carga:** cerca de 62 projetos ativos, R$ 4 bilhões em orçamento e 23 projetos com alerta.

## 11. Como usar e atualizar

- **Abrir:** pelo link online ou com dois cliques em `dashboard/plataforma.html`. Não precisa de servidor.
- **Mudar indicadores:** editar `Indicadores_Monitoramento_Eixos_01_02_03.md` e rodar `python gerar_dados.py` na pasta `dashboard`. Os IDs dependem da ordem no MD.
- **Atualizar órgãos:** recapturar a página do Portal da Transparência para `fonte/` e rodar `python gerar_orgaos.py`.
- **Regerar municípios:** `python gerar_municipios.py`, que precisa de internet (API do IBGE).
- **Dados do navegador:** o rodapé tem Exportar e Importar em JSON e Apagar dados do protótipo.
- **Publicar mudanças** (na pasta `Omar_Eixos`):
  ```
  git add -A
  git commit -m "descrição da mudança"
  git push
  ```
  O GitHub Pages atualiza sozinho em cerca de 1 minuto.

## 12. Publicação

- **Repositório:** público, com GitHub Pages ativo na branch `main`.
- **Autoria:** os commits usam o e-mail anônimo do GitHub (`…+dsalcodaa@users.noreply.github.com`). O histórico foi reescrito para tirar o e-mail interno.
- **PDFs:** fora do repositório, por causa do tamanho. Por isso o link "ver no PDF" do catálogo só funciona na cópia local.

## 13. Limitações atuais

- **Dados só no navegador** (localStorage, cerca de 5 MB). Cada computador e cada visitante do site tem os seus. Não há trabalho em equipe real.
- **Sem login:** os perfis são simulados.
- **Anexos:** limitados a 1 MB cada, por caberem no navegador.
- **Relatório:** usa a impressão do navegador, não um PDF com layout próprio.
- **Mapa:** fica só na tela Projetos.
- **Carga da carteira de exemplo:** se faltar espaço no navegador, a carteira não entra e nenhuma mensagem avisa.
- **Projetos e números de exemplo** são fictícios.

## 14. Decisões em aberto

1. **Validar a tabela área → órgão** usada nas sugestões (`SUG_AREA`).
2. **Definir os perfis reais:** quem acessa (Casa Civil, SEGOV, secretários, equipes) e o que cada um pode fazer.
3. **Fechar o conteúdo obrigatório** de um projeto e de uma ação: municípios, fontes, contratos, riscos.
4. **Escolher como alimentar `valor_atual`** dos indicadores: planilha, banco de dados ou coletores automáticos de fontes oficiais.

## 15. Próximos passos sugeridos

1. **Banco de dados com login** (ex.: Supabase), para secretarias e governador trabalharem nos mesmos dados.
2. **Importação de planilha** para indicadores e projetos.
3. **Coletores de fontes oficiais:** DataSUS, INEP, SSP, Portal da Transparência.
4. **Mapa e consolidação por município** também na Sala do Governador.
5. **Relatório em PDF com layout próprio** e envio periódico.
6. **OCR das páginas-foto** de Fruticultura e Aquicultura e cruzamento de metas entre eixos (conectividade, telessaúde, desmatamento).
