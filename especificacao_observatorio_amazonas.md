# OBSERVATÓRIO AMAZONAS
## Especificação funcional, técnica e de dados para uma plataforma de monitoramento governamental do Estado do Amazonas

**Versão:** 1.0  
**Data de referência da pesquisa:** 12 de novembro de 2026  
**Escopo:** Poder Executivo do Estado do Amazonas, com detalhamento estadual, regional e municipal  
**Natureza do documento:** visão de produto, requisitos funcionais, arquitetura de dados, catálogo inicial de indicadores e plano de implementação.

---

# 1. Visão do produto

Construir uma plataforma web abrangente para monitorar o planejamento, a execução orçamentária, as entregas governamentais e os resultados das políticas públicas do Governo do Estado do Amazonas.

A plataforma deve funcionar como um observatório de inteligência governamental e territorial, permitindo responder:

- O que o Governo planejou entregar?
- Quais são as metas vigentes de cada programa, secretaria e ação?
- Quanto foi executado física e financeiramente?
- Qual é o último resultado conhecido de cada indicador?
- O resultado atual está acima ou abaixo da meta?
- Qual é a evolução histórica do indicador?
- Quais municípios e regiões apresentam maiores déficits?
- Quais obras, programas ou políticas estão atrasados?
- Quanto foi autorizado, empenhado, liquidado e pago?
- O gasto público está produzindo as entregas e os resultados esperados?
- Quais dados estão atualizados, quais estão defasados e quais ainda não foram publicados?

A plataforma não deve ser apenas um conjunto de dashboards. Deve possuir uma camada estruturada de dados, um catálogo de indicadores, mecanismos de ingestão e atualização, histórico de metas, rastreabilidade das fontes, análise territorial e ferramentas de investigação.

## 1.1. Nome de trabalho

**Observatório Amazonas — Monitoramento Governamental e Inteligência Territorial**

A identidade visual poderá ser definida posteriormente. A plataforma deve ter aparência institucional, contemporânea, sóbria, responsiva e orientada à leitura de dados.

## 1.2. Princípios do produto

1. **Rastreabilidade:** todo número deve apontar para sua fonte, período, metodologia e data de atualização.
2. **Temporalidade:** metas, valores apurados e versões do planejamento devem ser preservados ao longo do tempo.
3. **Comparabilidade:** permitir comparações entre anos, municípios, regiões, secretarias e programas, respeitando diferenças metodológicas.
4. **Territorialização:** os dados devem ser associados, sempre que possível, a municípios, regiões de planejamento, localidades e geometrias.
5. **Separação entre planejamento e resultado:** execução financeira, entrega física e impacto social não podem ser confundidos.
6. **Transparência sobre lacunas:** ausência de dado não deve ser representada como zero.
7. **Atualização controlada:** cada fonte deve ter periodicidade, responsável técnico, status de atualização e registro de falhas.
8. **Neutralidade analítica:** apresentar evidências e metodologia, sem produzir julgamentos políticos automáticos.
9. **Reprodutibilidade:** fórmulas e transformações devem ser documentadas e versionadas.
10. **Acessibilidade:** interface responsiva, navegação por teclado, contraste adequado e linguagem compreensível.

---

# 2. Escopo institucional e territorial

## 2.1. Abrangência institucional

O catálogo deve contemplar:

- Secretarias de Estado;
- Secretarias executivas e unidades vinculadas;
- Fundações;
- Autarquias;
- Empresas públicas e sociedades de economia mista, quando houver dados públicos pertinentes;
- Fundos estaduais;
- Programas e ações orçamentárias;
- Unidades responsáveis pela execução de políticas públicas.

A estrutura institucional deve ser versionada. Mudanças de nome, competência, vinculação ou código de órgão não podem apagar o histórico.

## 2.2. Áreas de resultado do PPA

O PPA 2024–2027 do Amazonas organiza os programas em áreas de resultado. O relatório de avaliação do exercício de 2024 apresenta, entre outras, as seguintes áreas:

1. Saúde Integral;
2. Educação Transformadora;
3. Amazonas pela Paz;
4. Atenção e Proteção Social e Direitos Humanos;
5. Infraestrutura e Logística de Integração;
6. Desenvolvimento Integrado e Inovação, Ciência e Tecnologia;
7. Desenvolvimento Regional;
8. Identidade Amazonense;
9. Meio Ambiente e Sustentabilidade;
10. Desburocratização e Governo Digital;
11. Governo Sempre Presente.

Essas áreas devem constituir uma dimensão central de navegação, mantendo associação com programas, objetivos, indicadores e ações oficiais.

## 2.3. Abrangência territorial

A plataforma deve permitir visualizar:

- Estado do Amazonas;
- Regiões de planejamento utilizadas pelo Estado;
- Municípios;
- Áreas urbanas e rurais, quando houver dados;
- Distritos, comunidades e localidades, quando a fonte permitir;
- Bacias hidrográficas e calhas de rios;
- Rodovias estaduais, federais e vicinais;
- Unidades de saúde, escolas, equipamentos públicos e obras georreferenciadas.

**Atenção:** não presumir que regiões de planejamento estaduais sejam equivalentes às regiões geográficas imediatas/intermediárias do IBGE. Guardar os códigos e as geometrias de cada recorte separadamente.

---

# 3. Base oficial de planejamento: PPA 2024–2027

## 3.1. Documentos essenciais

O PPA deve ser a espinha dorsal da plataforma. Os documentos abaixo precisam ser incorporados ao repositório documental e ao processo de extração.

| Documento | Finalidade | Uso na plataforma |
|---|---|---|
| Lei nº 6.671, de 28/12/2023 | Institui o PPA 2024–2027 | Base legal e versão original do plano |
| Anexos I, II e III do PPA | Diretrizes, programas, objetivos, indicadores, metas e ações | Cadastro estruturado do planejamento |
| PPA de Bolso 2024–2027 | Síntese do planejamento | Navegação executiva e conferência |
| Relatório Anual de Avaliação — Exercício 2024 | Apresenta resultados apurados e execução dos programas | Linha de base observada e validação dos indicadores |
| Anexo I do Relatório de Avaliação 2024 | Dados físicos e financeiros por programa, ação e região | Execução regionalizada |
| Anexo II do Relatório de Avaliação 2024 | Execução financeira de programas fora do escopo principal da avaliação | Complementação financeira |
| Lei nº 7.978, de 16/12/2025 | Altera o PPA para 2026–2027 | Nova versão das metas e atributos |
| Relatórios de Ação Governamental | Entregas e execução das ações | Histórico de produtos e entregas |
| Manuais do SPLAM | Regras de cadastro, monitoramento e avaliação | Regras de modelagem e validação |

### Links oficiais

- Portal do PPA: https://portaldoplanejamento.am.gov.br/ppa/
- Página do PPA 2024–2027: https://portaldoplanejamento.am.gov.br/ppa-2024-2027/
- Lei nº 6.671/2023: https://legisla.imprensaoficial.am.gov.br/diario_am/12/2023/12/10939
- Relatório de Avaliação PPA 2024–2027 — Exercício 2024:  
  https://portaldoplanejamento.am.gov.br/wp-content/uploads/2025/04/AVALIACAO-PPA-2024-2027_EXERCICIO-2024.pdf
- Diretório de documentos e bases do Portal do Planejamento:  
  https://portaldoplanejamento.am.gov.br/wp-content/uploads/2024/08/
- Portal de Planejamento e SPLAM: https://portaldoplanejamento.am.gov.br/ppa/
- Sistema SPLAM: https://splam.sedecti.am.gov.br/
- Lei nº 7.978/2025 — Diário Oficial:  
  https://diario.imprensaoficial.am.gov.br/portal/edicoes/download/17985

O Portal do Planejamento descreve o monitoramento como acompanhamento sistemático e contínuo das metas físicas, financeiras e dos indicadores dos programas e ações do PPA. O SPLAM é apresentado como sistema de acompanhamento da execução física e financeira.

## 3.2. Regra fundamental: versionamento do PPA

Não sobrescrever a meta original quando houver revisão legislativa ou administrativa.

Criar uma entidade `ppa_version` com:

- código da versão;
- instrumento legal;
- data de publicação;
- início de vigência;
- fim de vigência;
- exercício ou biênio afetado;
- documento de origem;
- status (vigente, substituída, histórica);
- justificativa da alteração.

Cada programa, ação, indicador e meta deve apontar para a versão válida.

**Regra de apresentação:** ao exibir uma meta de 2026, utilizar a versão vigente para 2026, considerando a Lei nº 7.978/2025 e demais revisões posteriores. Preservar a meta original de 2024–2027 para comparação histórica.

## 3.3. Extração e concatenação dos PDFs

Implementar um pipeline documental para:

1. Baixar os PDFs oficiais;
2. Armazenar o arquivo original sem alterações;
3. Calcular hash SHA-256;
4. Extrair texto, tabelas e metadados;
5. Preservar número da página e título da seção;
6. Identificar tabelas de programas, indicadores, metas e execução;
7. Normalizar números, unidades e nomes;
8. Detectar duplicidades;
9. Relacionar metas com programas e ações;
10. Submeter dados ambíguos à validação humana;
11. Registrar a versão do documento e a data da extração.

### Campos que devem ser extraídos

**Programa**
- Código do programa;
- Nome;
- Área de resultado;
- Objetivo geral;
- Público-alvo;
- Órgão responsável;
- Unidade orçamentária;
- Vigência;
- Objetivos de Desenvolvimento Sustentável associados.

**Indicador**
- Código, quando existir;
- Nome;
- Descrição;
- Fórmula de cálculo;
- Unidade de medida;
- Periodicidade;
- Polaridade (quanto maior, melhor; quanto menor, melhor; faixa ideal);
- Índice de referência;
- Ano de referência;
- Fonte;
- Meta anual;
- Valor apurado;
- Percentual de execução;
- Observações metodológicas.

**Ação**
- Código;
- Nome;
- Programa relacionado;
- Unidade responsável;
- Produto/entrega;
- Unidade de medida;
- Localizador territorial;
- Meta física programada;
- Realização física;
- Dotação programada;
- Valor autorizado;
- Valor realizado;
- Valor pago;
- Percentual de execução física;
- Percentual de execução financeira.

**Meta**
- Indicador ou produto relacionado;
- Valor-alvo;
- Unidade;
- Ano;
- território;
- órgão responsável;
- versão do PPA;
- fonte documental;
- página;
- status de vigência.

## 3.4. Não confundir indicador de resultado com produto de ação

O relatório oficial possui dois tipos de informação que devem ser apresentados separadamente:

- **Indicadores de programa:** medem resultados, condições ou fenômenos associados à política pública.
- **Produtos de ações:** medem entregas administrativas e físicas, como quilômetros recuperados, unidades construídas, pessoas atendidas ou documentos expedidos.

O sistema deve permitir navegar entre eles, mas não somá-los em um mesmo índice sem uma metodologia explicitamente documentada.

---

# 4. Indicadores e dados já identificados no relatório oficial de 2024

Os números desta seção são valores publicados no Relatório Anual de Avaliação do PPA, exercício de 2024. São uma linha de base histórica verificada, não uma afirmação sobre a situação atual em novembro de 2026.

## 4.1. Saúde

| Indicador | Meta 2024 | Apurado 2024 | Execução publicada |
|---|---:|---:|---:|
| Avaliação do desempenho da rede laboratorial estadual | 18.000 | 25.374 | 140,97% |
| Cobertura da vacina tríplice viral em crianças de 1 ano | 95% | 98,86% | 104,06% |
| Índice de infestação predial com larvas de Aedes aegypti | 1,00% | 0,955% | 95,50% |
| Monitoramento da rede estadual de laboratórios | 169 | 160 | 94,67% |
| Casos autóctones de malária | 31.525 | 62.297 | 197,61% |
| Casos novos de AIDS em menores de 5 anos | 3 | 9 | 300,00% |
| Casos novos de sífilis congênita em menores de 1 ano | 358 | 567 | 158,38% |
| Exames realizados pela rede de laboratórios FVS-RCP | 300.969 | 329.888 | 109,61% |
| Municípios que realizam pelo menos seis grupos de ações de vigilância sanitária | 55% | 35,48% | 64,51% |
| Óbitos de mulheres em idade fértil investigados | 91% | 82,46% | 90,62% |
| Profissionais de laboratórios qualificados | 571 | 500 | 87,57% |
| Ações de matriciamento realizadas por CAPS com Atenção Básica | 67% | 62,5% | 93,28% |
| Mortalidade prematura por quatro principais DCNT | 200 por 100 mil | 218,59 por 100 mil | 109,30% |
| Procedimentos ambulatoriais de média e alta complexidade | 27.460.629 | 30.008.516 | 109,28% |
| Participação da despesa com medicamentos na despesa total com saúde | 4,99% | 9,66% | 193,59% |
| Abastecimento de medicamentos e produtos para saúde | 76% | 61% | 80,26% |
| Proporção de parto normal | 60% | 54,5% | 90,83% |
| Taxa de leitos de internação por habitante | 1,56 | 1,53 | 98,08% |
| Taxa de mortalidade infantil | 15 por mil | 15,1 por mil | 100,67% |

**Atenção à polaridade:** indicadores como casos de malária, AIDS, sífilis e mortalidade são indicadores de redução. Um percentual de execução acima de 100% pode representar piora, e não superação positiva da meta. A plataforma deve calcular o status com base na polaridade e no sentido da meta, e não apenas no quociente entre realizado e previsto.

## 4.2. Infraestrutura — Programa 3300 MAIS INFRA / SEINFRA

Dados extraídos do Anexo I do relatório de avaliação de 2024:

| Produto/entrega | Programado | Realizado | Execução física |
|---|---:|---:|---:|
| Rua pavimentada | 71 km | 35,89 km | 50,55% |
| Área construída/melhorada em espaços e prédios públicos | 4.085 m² | 3.962,04 m² | 96,99% |
| Porto/terminal implantado ou modernizado | 4 un. | 2 un. | 50,00% |
| Estrada/rodovia construída ou recuperada | 46 km | 25,09 km | 54,54% |
| Sistema de abastecimento de água ampliado/recuperado | 6 km | 1,75 km | 29,17% |
| Sistema de esgoto sanitário ampliado/recuperado | 4 km | 0 km | 0,00% |

### Execução financeira de algumas entregas

| Entrega | Programado | Autorizado | Realizado | Pago |
|---|---:|---:|---:|---:|
| Rua pavimentada | R$ 70,415 mi | R$ 82,934 mi | R$ 58,364 mi | R$ 58,364 mi |
| Área construída/melhorada | R$ 3,400 mi | R$ 12,317 mi | R$ 4,317 mi | R$ 4,317 mi |
| Porto/terminal | R$ 3,615 mi | R$ 1,434 mi | R$ 1,396 mi | R$ 1,396 mi |
| Estrada/rodovia construída ou recuperada | R$ 72,542 mi | R$ 103,145 mi | R$ 72,304 mi | R$ 72,304 mi |
| Sistema de abastecimento de água | R$ 3,215 mi | R$ 1,946 mi | R$ 1,931 mi | R$ 1,931 mi |

Os valores são os registros do relatório de avaliação e devem ser preservados com suas categorias originais. Não interpretar “realizado” como sinônimo de “pago” sem verificar a definição do demonstrativo.

### Exemplos de regionalização de obras

A entrega de 46 km de estradas e rodovias foi detalhada por localizador. O relatório registra, entre outros valores:

- Estado: programado 46 km; realizado 12,47 km;
- Alto Solimões: realizado 0,36 km;
- Rio Negro/Solimões: realizado 0,08 km;
- Triângulo (Jutaí, Juruá, Solimões): realizado 0,90 km;
- Região Metropolitana: realizado 11,28 km.

Esses recortes devem ser armazenados como localizadores oficiais do relatório, sem convertê-los automaticamente em município. Se houver dados geográficos que permitam associá-los a municípios, manter a relação como uma correspondência documentada.

### Outras entregas encontradas no relatório

- Lâmpadas LED instaladas: 387 programadas; 490 realizadas.
- Área beneficiada por projetos especiais: meta física de 2 km²; resultado consolidado reportado no quadro.
- Documentos de regularização fundiária expedidos: 4.000 programados; 1.310 realizados.
- Ponte sobre o Rio Negro operacionalizada: 1 programada; 0 realizada no demonstrativo.
- Investimentos em segurança pública: ação com 1 iniciativa programada e 29 iniciativas registradas no quadro de execução; validar o significado da unidade/produto antes de interpretar o percentual.

**Observação:** as tabelas de execução física e financeira devem ser importadas integralmente do relatório e conferidas por página. Os exemplos acima são amostras documentais, não substituem a extração completa de todas as ações do PPA.

## 4.3. Segurança pública

O relatório de 2024 também apresenta informações de segurança e defesa civil:

- Taxa de crimes violentos reportada: 28,59%;
- Redução reportada de 16,33% nas mortes violentas em relação ao ano anterior;
- 1.127 vítimas de crimes como feminicídio, homicídio doloso, latrocínio e lesão corporal seguida de morte;
- 261 acidentes com vítimas fatais em 2024;
- Frota de 1.241.598 veículos;
- Taxa de vítimas fatais em acidentes de trânsito reportada: 21,02%;
- 532.565 pessoas afetadas por desastres segundo o relatório, incluindo estiagem, inundações, incêndios e outros eventos.

A definição exata de cada taxa, denominador e período deve ser importada do documento metodológico. Não misturar contagem de vítimas, ocorrências e taxas por população ou frota.

## 4.4. Indicadores sociais e econômicos

O relatório anual inclui capítulo específico de cenário macroeconômico e indicadores sociais. A extração integral deve contemplar:

- PIB estadual;
- PIB per capita;
- composição setorial do PIB;
- mercado de trabalho;
- renda;
- inflação, quando aplicável;
- comércio exterior;
- indicadores demográficos;
- indicadores de pobreza e vulnerabilidade;
- educação;
- saúde;
- saneamento;
- condições habitacionais.

Os dados devem ser armazenados com ano de referência e fonte original. Não utilizar um dado de 2022 ou 2023 como “situação atual” sem exibir claramente a data.

---

# 5. Catálogo de indicadores por secretaria e área de política pública

O catálogo deve combinar os indicadores oficiais do PPA com indicadores complementares de resultado e contexto. Os indicadores complementares precisam ser marcados como **propostos** até que sua fórmula, fonte, periodicidade e responsável sejam validados.

## 5.1. Saúde — SES-AM, FVS-RCP, FES e unidades vinculadas

**Indicadores de resultado**
- Mortalidade infantil;
- mortalidade materna;
- mortalidade prematura por doenças crônicas;
- incidência de malária;
- incidência de dengue;
- incidência de tuberculose;
- incidência de hanseníase;
- casos de sífilis congênita;
- cobertura vacinal por imunizante;
- taxa de internação por condições sensíveis à atenção primária.

**Indicadores de acesso e capacidade**
- Consultas especializadas realizadas;
- tempo mediano de espera por consulta;
- tempo mediano de espera por cirurgia;
- cirurgias realizadas;
- leitos por habitante;
- taxa de ocupação de leitos;
- exames realizados;
- unidades de saúde em funcionamento;
- disponibilidade de medicamentos essenciais;
- cobertura de serviços de saúde por município;
- tempo de deslocamento até serviço de referência.

**Indicadores territoriais**
- População sem acesso oportuno a atendimento;
- municípios sem determinada especialidade;
- distribuição de leitos e profissionais;
- concentração de serviços em Manaus;
- comunidades ribeirinhas atendidas por ações itinerantes.

## 5.2. Educação — SEDUC-AM, CEE, CETAM e unidades vinculadas

- IDEB por etapa;
- resultados do SAEB;
- taxa de alfabetização;
- taxa de aprovação;
- taxa de abandono;
- distorção idade-série;
- matrículas por etapa e município;
- taxa de conclusão do ensino médio;
- escolas com água, energia, internet e saneamento;
- escolas com biblioteca e laboratório;
- transporte escolar rural;
- vagas de educação profissional;
- estudantes matriculados em tempo integral;
- frequência escolar;
- resultados de aprendizagem por município.

## 5.3. Segurança pública — SSP-AM, Polícia Militar, Polícia Civil, Bombeiros e SEAP

- Homicídios dolosos;
- mortes violentas intencionais;
- feminicídios;
- latrocínios;
- roubos de veículos;
- furtos de veículos;
- roubos de carga;
- estupros;
- lesões corporais seguidas de morte;
- ocorrências por 100 mil habitantes;
- taxa de elucidação de homicídios;
- inquéritos concluídos;
- tempo de resposta policial;
- chamadas atendidas;
- efetivo por habitante;
- apreensões de drogas;
- população prisional;
- taxa de ocupação do sistema prisional;
- vagas prisionais;
- reincidência, quando houver metodologia disponível;
- ocorrências e atendimentos dos Bombeiros;
- mortes no trânsito e acidentes com vítimas.

**Cuidados:** padronizar a tipologia criminal e distinguir boletim de ocorrência, ocorrência agregada, vítima e procedimento policial. Controlar revisões e retificações das bases.

## 5.4. Infraestrutura — SEINFRA e órgãos executores

- Quilômetros de rodovias pavimentadas;
- quilômetros de rodovias recuperadas;
- quilômetros de vicinais recuperadas;
- extensão da malha estadual em condição boa, regular e ruim;
- percentual de contratos com execução física dentro do cronograma;
- obras concluídas;
- obras paralisadas;
- obras com atraso;
- percentual de execução física;
- percentual de execução financeira;
- custo por quilômetro;
- custo por metro quadrado;
- pontes construídas ou recuperadas;
- portos e terminais implantados ou modernizados;
- obras de drenagem;
- obras de mobilidade urbana;
- tempo de deslocamento entre municípios;
- acessibilidade durante cheia e estiagem;
- investimento por município;
- investimento por região;
- prazo médio de contratação;
- prazo médio de conclusão;
- aditivos de prazo e valor;
- percentual de contratos com medições atualizadas.

### Submódulo SEINFRA — Obras e contratos

Cada obra deve possuir:
- Identificador único;
- número do contrato/convênio;
- órgão contratante;
- empresa contratada;
- objeto;
- município;
- localidade;
- coordenadas/geometria;
- segmento (rodovia, vicinal, prédio, ponte, porto, saneamento etc.);
- valor inicial;
- aditivos;
- reajustes;
- valor global atualizado;
- valor empenhado;
- valor liquidado;
- valor pago;
- data de início;
- prazo original;
- prazo vigente;
- término previsto;
- término real;
- execução física;
- execução financeira;
- medição mais recente;
- status;
- fonte e data da atualização.

**Importante:** contrato e obra não são necessariamente a mesma entidade. Um contrato pode abranger várias obras e uma obra pode ter mais de um instrumento contratual. O modelo deve permitir relações 1:N e N:N, sem duplicar valores financeiros.

## 5.5. Cidades, habitação, saneamento e desenvolvimento urbano

- Déficit habitacional;
- unidades habitacionais contratadas, iniciadas e entregues;
- famílias beneficiadas;
- regularização fundiária;
- população em assentamentos precários;
- população em áreas de risco;
- cobertura de abastecimento de água;
- cobertura de coleta de esgoto;
- tratamento de esgoto;
- coleta de resíduos sólidos;
- perdas de água;
- drenagem urbana;
- áreas urbanizadas;
- municípios com plano diretor;
- municípios com plano de saneamento;
- infraestrutura urbana implantada.

## 5.6. Assistência social, direitos humanos e cidadania

- Famílias no CadÚnico;
- famílias atendidas por programas estaduais;
- cobertura de CRAS e CREAS;
- pessoas atendidas por serviços socioassistenciais;
- insegurança alimentar;
- pessoas em situação de rua;
- atendimentos a mulheres vítimas de violência;
- denúncias de violações de direitos;
- crianças e adolescentes atendidos;
- pessoas idosas atendidas;
- pessoas com deficiência atendidas;
- documentação civil emitida;
- municípios alcançados por ações itinerantes.

## 5.7. Produção rural, agricultura, pesca e desenvolvimento sustentável

- Produção agrícola por cultura;
- área plantada;
- produtividade por hectare;
- produção pecuária;
- produção pesqueira;
- produção aquícola;
- agricultores familiares atendidos;
- produtores com assistência técnica;
- crédito rural contratado;
- volume comercializado;
- participação em compras públicas;
- renda de produtores;
- estabelecimentos regularizados;
- inspeções sanitárias;
- escoamento da produção;
- custo logístico por tonelada.

## 5.8. Economia, ciência, tecnologia e trabalho

- PIB estadual e municipal;
- PIB per capita;
- saldo de empregos formais;
- estoque de empregos;
- rendimento médio;
- taxa de desemprego;
- informalidade;
- exportações;
- importações;
- saldo comercial;
- investimentos privados anunciados e realizados;
- empresas abertas e encerradas;
- empresas apoiadas;
- projetos de inovação;
- bolsas e pesquisas financiadas;
- patentes;
- pesquisadores;
- cursos profissionalizantes;
- pessoas qualificadas e inseridas no mercado de trabalho.

## 5.9. Meio ambiente, clima e defesa civil

- Desmatamento anual;
- alertas de desmatamento;
- focos de calor;
- área queimada;
- emissões de gases de efeito estufa;
- áreas protegidas;
- áreas recuperadas;
- autos de infração;
- licenças ambientais;
- qualidade da água;
- municípios afetados por cheias;
- municípios afetados por secas;
- população afetada;
- comunidades isoladas;
- tempo de resposta da Defesa Civil;
- perdas econômicas por eventos extremos;
- áreas suscetíveis a erosão e inundação.

## 5.10. Fazenda, planejamento, administração e controle

- Receita corrente líquida;
- arrecadação de ICMS;
- arrecadação própria;
- transferências constitucionais;
- despesas por função;
- despesa com pessoal;
- dívida consolidada;
- resultado primário;
- restos a pagar;
- disponibilidade de caixa;
- percentual de execução orçamentária;
- percentual de execução do PPA;
- metas alcançadas;
- indicadores sem atualização;
- compras públicas;
- economia em licitações;
- tempo médio de contratação;
- auditorias;
- recomendações implementadas;
- serviços públicos digitalizados;
- satisfação dos usuários.

---

# 6. Fontes de dados e integrações obrigatórias

A plataforma deve possuir um **Catálogo de Fontes** com descrição, órgão responsável, URL, tipo de acesso, formato, cobertura territorial, periodicidade, licença, limitações, data de verificação e status da integração.

## 6.1. Repositório 1 — API de Segurança Pública

**URL:** https://github.com/rayonnunes/api_seguranca_publica

O repositório descreve uma WebAPI baseada em dados abertos do SINESP. O README documenta:

- Endpoint de consulta GET;
- filtros por região, UF, município, tipo de crime, ano e mês;
- paginação;
- limite documentado de até 1.000 registros por página;
- retorno de total de resultados e total de ocorrências;
- categorias criminais codificadas;
- projeto implementado em Python/Flask e MongoDB.

O README informa um endpoint de produção em HTTP, não HTTPS. Portanto:

1. Não conectar o navegador diretamente ao endpoint;
2. Não enviar dados sensíveis;
3. Não assumir disponibilidade atual do serviço;
4. Validar o estado do endpoint antes de qualquer integração;
5. Preferir baixar a base oficial do SINESP ou operar uma instância própria;
6. Revisar dependências, código, licença MIT e segurança;
7. Implementar HTTPS, autenticação administrativa, cache e limitação de requisições;
8. Guardar a origem e a data de extração;
9. Validar a compatibilidade da tipologia criminal com as categorias oficiais vigentes.

### Parâmetros documentados no README

| Parâmetro | Uso |
|---|---|
| `regiao` | Região brasileira |
| `uf` | Unidade federativa |
| `municipio` | Município |
| `crime` | Código de categoria criminal |
| `ano` | Ano ou intervalo |
| `mes` | Mês ou intervalo |
| `per_page` | Itens por página |
| `page` | Página |

Exemplo conceitual de consulta:

```http
GET /api?uf=am&ano=2020-2024&crime=3&per_page=1000&page=1
```

A plataforma deve armazenar dados mensais e permitir séries históricas. A cobertura descrita no README não equivale a todos os indicadores de segurança pública: o conjunto de crimes documentado é limitado a categorias específicas.

**Recomendação:** utilizar o repositório como referência técnica ou ponto de partida, mas construir um conector próprio, testado e mantido.

## 6.2. Repositório 2 — GeoTática: Plataforma de Dados

**URL:** https://geotatica.github.io/Plataforma_Dados/

A página informa um catálogo curado com 2.185 fontes de dados e 29 temas, reunindo fontes gratuitas de dados geográficos, cartográficos, ambientais, territoriais e estatísticos.

A curadoria organiza a navegação por:

- temas;
- tipos de dados;
- aplicações;
- recorte territorial;
- estrutura técnica;
- fontes;
- mapas;
- materiais de apoio.

Temas relevantes para o Observatório:

- Cartografia de referência;
- limites e divisões territoriais;
- cadastro e planejamento;
- agricultura e agropecuária;
- uso e cobertura do solo;
- biodiversidade;
- meio ambiente;
- clima e meteorologia;
- hidrografia;
- relevo;
- imagens de satélite;
- energia e mineração;
- infraestrutura urbana;
- mobilidade e transportes;
- governança e políticas públicas;
- socioeconômico;
- saúde;
- educação;
- segurança pública;
- riscos e desastres.

### Como integrar

A GeoTática deve ser usada prioritariamente como **catálogo de descoberta e metadados**, não como se todas as 2.185 fontes fossem APIs prontas.

Para cada fonte selecionada, registrar:

- nome;
- instituição;
- tema;
- escala territorial;
- tipo de dado;
- formato;
- URL;
- método de acesso;
- periodicidade;
- licença;
- data da última verificação;
- limitações;
- aplicação potencial;
- status do conector.

Não fazer scraping indiscriminado. Cada fonte deve ser avaliada individualmente, respeitando licença, termos de uso, estabilidade e qualidade.

## 6.3. Fontes nacionais complementares

| Instituição/base | Dados de interesse |
|---|---|
| IBGE | População, PIB municipal, Censo, renda, trabalho, território e malhas municipais |
| DATASUS / TabNet | Mortalidade, internações, nascimentos, produção ambulatorial e informações de saúde |
| SINAN | Agravos e notificações epidemiológicas |
| SIM | Mortalidade |
| SINASC | Nascidos vivos |
| SIH/SUS | Internações hospitalares |
| CNES | Estabelecimentos, leitos e profissionais de saúde |
| INEP | Censo Escolar, IDEB, SAEB, matrículas e infraestrutura escolar |
| SINESP / MJSP | Estatísticas de segurança pública |
| SICONFI / Tesouro Nacional | Receitas, despesas, RREO, RGF e finanças públicas |
| Portal da Transparência | Transferências, despesas e convênios |
| PNCP | Contratações públicas, editais, contratos e atas |
| Transferegov | Transferências e instrumentos da União |
| DNIT | Rodovias federais, obras, tráfego e infraestrutura |
| ANTT | Concessões, transporte e infraestrutura regulada |
| ANAC | Transporte aéreo e aeroportos |
| ANTAQ | Transporte aquaviário, portos e movimentação de cargas |
| ANA | Recursos hídricos, segurança hídrica e dados de água |
| INPE | PRODES, DETER, queimadas e dados ambientais |
| MapBiomas | Uso e cobertura da terra, fogo e mudanças territoriais |
| SNIS / SINISA | Água, esgoto, resíduos e saneamento |
| CONAB | Produção, abastecimento e preços agrícolas |
| Novo CAGED / RAIS | Emprego formal e mercado de trabalho |
| Banco Central | Indicadores econômicos e financeiros |
| IPEA | Estudos, indicadores sociais e bases de políticas públicas |

A existência de uma fonte não significa que haja API aberta ou atualização em tempo real. Cada integração deve verificar formato, autenticação, limites, licença e periodicidade.

## 6.4. Fontes estaduais prioritárias

- Portal do Planejamento do Amazonas;
- SPLAM;
- Portal da Transparência do Amazonas;
- Diário Oficial do Estado;
- SEFAZ-AM;
- SEINFRA-AM;
- SES-AM;
- FVS-RCP;
- SEDUC-AM;
- SSP-AM;
- DETRAN-AM;
- SEMA-AM;
- IPAAM;
- Defesa Civil;
- SEPROR;
- SEDECTI;
- FAPEAM;
- órgãos de habitação, saneamento, mobilidade e desenvolvimento urbano.

Para cada fonte estadual, registrar se o acesso é:
- API pública;
- arquivo CSV/XLSX;
- PDF;
- painel web;
- serviço geográfico WMS/WFS/ArcGIS REST;
- consulta manual;
- integração institucional autorizada.

---

# 7. Modelo de dados

A plataforma deve adotar um modelo relacional e temporal. Recomenda-se PostgreSQL com PostGIS.

## 7.1. Entidades principais

### `organization`
- id;
- nome;
- sigla;
- código institucional;
- tipo;
- órgão superior;
- data de início;
- data de fim;
- status.

### `ppa_version`
- id;
- nome;
- instrumento legal;
- data de publicação;
- vigência inicial;
- vigência final;
- status;
- documento original.

### `program`
- id;
- código;
- nome;
- descrição;
- área de resultado;
- objetivo;
- público-alvo;
- órgão responsável;
- versão do PPA.

### `program_objective`
- id;
- program_id;
- código;
- descrição;
- objetivo específico.

### `indicator`
- id;
- código;
- nome;
- descrição;
- fórmula;
- unidade;
- periodicidade;
- polaridade;
- tipo (insumo, processo, produto, resultado, impacto);
- fonte preferencial;
- responsável;
- método de cálculo;
- observações.

### `indicator_observation`
- id;
- indicator_id;
- data de referência;
- valor;
- unidade;
- município;
- região;
- organização;
- fonte;
- data de publicação;
- data de ingestão;
- status de qualidade;
- versão metodológica.

### `indicator_target`
- id;
- indicator_id;
- ppa_version_id;
- exercício;
- valor da meta;
- unidade;
- território;
- órgão;
- data de vigência;
- fonte documental;
- página.

### `government_action`
- id;
- código;
- nome;
- programa;
- órgão executor;
- produto;
- unidade de medida;
- vigência.

### `action_delivery`
- id;
- action_id;
- período;
- localizador;
- município;
- meta física;
- realizado físico;
- fonte.

### `budget_execution`
- id;
- exercício;
- órgão;
- unidade orçamentária;
- programa;
- ação;
- função;
- subfunção;
- fonte de recurso;
- dotação inicial;
- dotação atualizada;
- empenhado;
- liquidado;
- pago;
- restos a pagar.

### `territory`
- id;
- código IBGE ou código oficial;
- nome;
- tipo;
- região;
- geometria;
- vigência.

### `data_source`
- id;
- nome;
- instituição;
- URL;
- tipo de fonte;
- formato;
- periodicidade;
- licença;
- método de acesso;
- status.

### `ingestion_run`
- id;
- data/hora;
- fonte;
- início;
- fim;
- registros recebidos;
- registros aceitos;
- registros rejeitados;
- status;
- log;
- hash do arquivo.

### `document`
- id;
- título;
- tipo;
- URL;
- arquivo;
- hash;
- versão;
- data de publicação;
- data de ingestão.

### `document_extraction`
- id;
- document_id;
- página;
- seção;
- tabela;
- texto extraído;
- confiança;
- status de revisão.

### `project_work`
- id;
- nome;
- contrato;
- órgão;
- empresa;
- objeto;
- município;
- geometria;
- valor inicial;
- valor atualizado;
- prazo;
- status.

### `work_measurement`
- id;
- project_work_id;
- data;
- medição;
- valor medido;
- percentual físico;
- valor financeiro;
- documento comprobatório.

## 7.2. Regras de integridade

- Guardar valores originais e valores normalizados;
- não substituir nulos por zero;
- não somar taxas ou percentuais;
- não somar indicadores de unidades diferentes;
- não somar valores financeiros duplicados por join;
- preservar códigos originais;
- manter histórico de alterações;
- registrar fonte e página de origem;
- permitir múltiplas fontes para o mesmo indicador;
- manter datas de referência e de publicação separadas;
- distinguir dados preliminares, revisados e definitivos.

---

# 8. Fórmulas e metodologia de monitoramento

## 8.1. Execução física

Para metas de aumento, em que maior é melhor:

```text
execucao_fisica_pct = realizado / meta * 100
```

Exemplo: 25,09 km realizados para uma meta de 46 km.

## 8.2. Execução financeira

A execução financeira deve oferecer visões separadas:

```text
execucao_orcamentaria_pct = empenhado / dotacao_atualizada * 100
execucao_liquidacao_pct = liquidado / dotacao_atualizada * 100
execucao_pagamento_pct = pago / dotacao_atualizada * 100
```

A plataforma deve exibir também:
- dotação inicial;
- dotação atualizada;
- empenhado;
- liquidado;
- pago;
- restos a pagar;
- saldo disponível.

Não usar uma única taxa para representar toda a execução financeira.

## 8.3. Indicadores de redução

Para indicadores em que menor é melhor, o percentual simples realizado/meta pode ser enganoso.

Exemplo: meta de no máximo 31.525 casos de malária e resultado de 62.297 casos.

Exibir:
- valor-alvo;
- valor observado;
- diferença absoluta;
- variação percentual em relação à meta;
- status conforme polaridade;
- série histórica.

## 8.4. Indicadores com faixa ideal

Alguns indicadores não são necessariamente melhores quando crescem ou diminuem. Devem aceitar:
- valor mínimo;
- valor máximo;
- faixa ideal;
- limites de alerta.

## 8.5. Status de desempenho

Usar status descritivos e configuráveis, sem transformar automaticamente a situação em avaliação política:

- Meta atingida;
- trajetória compatível;
- atenção;
- fora da trajetória;
- sem dado atualizado;
- meta não aplicável;
- metodologia em revisão.

A regra de status deve considerar polaridade, periodicidade, sazonalidade, data de referência e progresso esperado até o período.

## 8.6. Progresso temporal esperado

Para metas anuais ou plurianuais, calcular a trajetória esperada considerando:
- data de início;
- data final;
- distribuição linear ou curva de execução;
- sazonalidade;
- calendário de medição;
- metas anuais intermediárias.

Não presumir distribuição linear quando o cronograma físico-financeiro tiver marcos próprios.

---

# 9. Funcionalidades e módulos da plataforma

## 9.1. Painel geral — visão do Estado

A tela inicial deve apresentar:

- total de programas monitorados;
- total de indicadores cadastrados;
- indicadores com dados atualizados;
- indicadores sem atualização;
- metas atingidas;
- metas em atenção;
- metas fora da trajetória;
- execução orçamentária agregada;
- execução física agregada, apenas quando comparável;
- obras em andamento;
- obras atrasadas;
- distribuição dos investimentos;
- mapa dos municípios;
- evolução dos principais indicadores.

Filtros globais:
- ano;
- período;
- secretaria;
- área de resultado;
- programa;
- município;
- região;
- fonte;
- status;
- tipo de indicador.

## 9.2. Módulo PPA

- Catálogo de programas;
- objetivos;
- indicadores;
- ações;
- metas anuais;
- metas plurianuais;
- órgãos responsáveis;
- histórico de versões;
- comparação entre meta original e meta revisada;
- acompanhamento por exercício;
- relatório de execução;
- exportação CSV/XLSX/PDF.

## 9.3. Módulo Indicadores

Cada indicador deve ter uma página própria contendo:

1. Nome e descrição;
2. órgão responsável;
3. programa associado;
4. fórmula;
5. unidade;
6. polaridade;
7. periodicidade;
8. meta vigente;
9. último valor disponível;
10. data de referência;
11. fonte;
12. linha do tempo;
13. gráfico histórico;
14. comparação com meta;
15. comparação territorial;
16. observações metodológicas;
17. histórico de revisões;
18. link para documento original.

### Visualizações
- linha temporal;
- barra de meta versus realizado;
- cartões de valor atual e variação;
- mapa coroplético;
- ranking tabular sem classificação valorativa;
- dispersão entre municípios;
- distribuição por faixa;
- comparação de séries.

## 9.4. Módulo Secretarias

Página de cada secretaria:
- orçamento;
- programas;
- ações;
- indicadores;
- metas;
- entregas;
- contratos e obras;
- evolução temporal;
- municípios atendidos;
- dados sem atualização;
- documentos oficiais;
- relatórios exportáveis.

## 9.5. Módulo Orçamento

- Dotação inicial e atualizada;
- empenhado;
- liquidado;
- pago;
- restos a pagar;
- execução por órgão;
- execução por programa;
- execução por ação;
- execução por função e subfunção;
- fonte de recurso;
- série histórica;
- orçamento por município;
- comparação entre execução física e financeira.

Não interpretar baixa execução financeira isoladamente como ineficiência. Mostrar contexto, cronograma, modalidade de execução, transferências e estágios da despesa.

## 9.6. Módulo Obras e Infraestrutura

- Mapa de obras;
- filtros por órgão, município, segmento e status;
- ficha individual da obra;
- contrato e empresa;
- valor inicial e atualizado;
- aditivos;
- medições;
- execução física;
- execução financeira;
- prazo original e atual;
- fotografias e documentos;
- cronograma;
- alertas de atraso;
- histórico de mudanças;
- comparação entre regiões.

Gráficos:
- planejado versus realizado;
- curva S física;
- curva S financeira;
- desembolso mensal;
- percentual de execução;
- prazo transcorrido versus avanço;
- custo por unidade;
- distribuição geográfica.

## 9.7. Módulo Segurança Pública

- ocorrências por categoria;
- vítimas;
- taxas por população;
- evolução mensal e anual;
- comparação entre municípios;
- mapa de concentração;
- sazonalidade;
- recortes por tipo de crime;
- fonte e metodologia;
- alertas de dados incompletos.

Não apresentar localização de ocorrências individuais que permita identificar vítimas ou comprometer investigações. Usar agregação espacial e temporal adequada.

## 9.8. Módulo Inteligência Territorial

- mapa estadual;
- mapa municipal;
- camadas de infraestrutura;
- equipamentos públicos;
- rodovias;
- hidrografia;
- cobertura vegetal;
- desmatamento;
- queimadas;
- população;
- renda;
- saúde;
- educação;
- segurança;
- saneamento;
- obras;
- investimentos;
- áreas de risco.

Permitir cruzamentos espaciais:
- população a determinada distância de uma unidade de saúde;
- escolas sem acesso adequado;
- áreas rurais sem conectividade;
- trechos rodoviários críticos;
- municípios com maior vulnerabilidade;
- relação entre investimento público e indicadores sociais.

## 9.9. Módulo Relatórios

Relatórios pré-configurados:
- balanço anual do PPA;
- monitoramento por secretaria;
- execução física e financeira;
- metas atrasadas;
- indicadores sem atualização;
- obras em atraso;
- perfil territorial por município;
- painel de saúde;
- painel de educação;
- painel de segurança;
- painel de infraestrutura;
- relatório de desigualdades regionais.

Permitir gerar PDF, CSV e XLSX, sempre com data de extração, fonte e metodologia.

## 9.10. Módulo Administração e governança dos dados

- cadastro de fontes;
- cadastro de indicadores;
- cadastro de fórmulas;
- gestão de metas;
- validação de dados extraídos;
- revisão de documentos;
- execução dos conectores;
- monitoramento de falhas;
- controle de permissões;
- logs de auditoria;
- aprovação de alterações;
- histórico de versões.

---

# 10. Gráficos, linhas temporais e análises

A plataforma deve oferecer um conjunto consistente de visualizações.

## 10.1. Gráficos obrigatórios

| Visualização | Aplicação |
|---|---|
| Linha temporal | Evolução mensal, trimestral ou anual |
| Barra horizontal | Comparação entre municípios ou secretarias |
| Barra meta x realizado | Acompanhamento de metas |
| Curva S | Obras e projetos |
| Área empilhada | Composição de orçamento ou categorias |
| Mapa coroplético | Indicadores municipais |
| Mapa de pontos | Obras e equipamentos |
| Dispersão | Relação entre investimento e resultado |
| Histograma | Distribuição de indicadores |
| Heatmap | Intensidade por município e período |
| Cascata | Variação orçamentária |
| Bullet chart | Atual versus meta e faixa de referência |

## 10.2. Linhas temporais

Cada série deve permitir:
- alternar mensal, trimestral e anual;
- selecionar intervalo;
- comparar exercícios;
- exibir meta como linha de referência;
- marcar revisões metodológicas;
- indicar períodos sem dados;
- diferenciar dado preliminar de definitivo;
- exibir notas e eventos relevantes.

Não interpolar automaticamente valores ausentes. Se uma série não tiver observação em determinado período, mostrar lacuna.

## 10.3. Análises automáticas assistidas

O sistema pode produzir textos descritivos, por exemplo:

> “O indicador apresentou aumento de X% em relação ao período anterior. O último dado disponível refere-se a [data]. A meta vigente é [valor]. A série contém [n] observações e apresenta [lacuna/alteração metodológica].”

Toda análise automática deve apontar para os dados que a sustentam. Não atribuir causalidade a correlações simples.

---

# 11. Arquitetura técnica recomendada

## 11.1. Stack sugerida

| Camada | Tecnologia recomendada | Função |
|---|---|---|
| Frontend | Next.js + TypeScript | Aplicação web responsiva |
| UI | Tailwind CSS + biblioteca de componentes | Interface consistente |
| Gráficos | ECharts ou Plotly | Séries, comparações e gráficos avançados |
| Mapas | MapLibre GL JS | Mapas interativos |
| Backend | Python + FastAPI | API principal e regras de negócio |
| Banco | PostgreSQL | Dados relacionais |
| Geodados | PostGIS | Geometrias e análises espaciais |
| Cache | Redis | Cache e filas |
| Processamento | Python, Pandas/Polars | Limpeza e transformação |
| Orquestração | Prefect ou Dagster | Agendamento de pipelines |
| Transformações | dbt, quando aplicável | Modelagem analítica |
| Arquivos | Object storage compatível com S3 | PDFs, planilhas e evidências |
| Autenticação | OIDC/OAuth2 | Login e controle de acesso |
| Observabilidade | OpenTelemetry + logs | Monitoramento técnico |
| Deploy | Docker | Ambientes reproduzíveis |

A stack pode ser ajustada à infraestrutura e ao orçamento disponíveis. O ponto essencial é separar frontend, API, banco de dados, ingestão e processamento.

## 11.2. Arquitetura lógica

```text
FONTES DE DADOS
  ├── PPA / PDFs / SPLAM
  ├── Portal da Transparência
  ├── API / dados SINESP
  ├── IBGE / DATASUS / INEP
  ├── SICONFI / Tesouro
  ├── DNIT / ANTT / ANTAQ
  ├── INPE / MapBiomas / ANA
  ├── GeoTática / catálogo de fontes
  └── Planilhas e bases institucionais
          |
          v
CONECTORES E INGESTÃO
  ├── API clients
  ├── Download de arquivos
  ├── Extração de PDF e tabelas
  ├── Importação CSV/XLSX
  └── Serviços geográficos
          |
          v
CAMADA BRONZE — DADOS BRUTOS
  ├── Arquivos originais
  ├── Respostas originais de APIs
  ├── Metadados
  └── Hash e logs
          |
          v
CAMADA SILVER — DADOS NORMALIZADOS
  ├── Padronização de códigos
  ├── Datas e unidades
  ├── Tratamento de duplicidades
  ├── Validação
  └── Correspondência territorial
          |
          v
CAMADA GOLD — DADOS ANALÍTICOS
  ├── Indicadores
  ├── Metas
  ├── Séries temporais
  ├── Execução orçamentária
  ├── Obras
  └── Indicadores territoriais
          |
          v
POSTGRESQL + POSTGIS
          |
          v
API FASTAPI
          |
          v
FRONTEND NEXT.JS
  ├── Painéis
  ├── Gráficos
  ├── Mapas
  ├── Relatórios
  └── Administração
```

## 11.3. Separação entre dados brutos e analíticos

Nunca substituir o dado bruto pela versão tratada.

- **Bronze:** cópia imutável da fonte.
- **Silver:** dado padronizado e validado.
- **Gold:** tabelas analíticas e indicadores calculados.

Cada registro analítico deve poder ser rastreado até o dado bruto e sua fonte.

---

# 12. Atualização e automação

## 12.1. Frequência por tipo de fonte

| Tipo de fonte | Frequência inicial sugerida |
|---|---|
| Orçamento e transparência | Diária ou semanal, conforme disponibilidade |
| Contratos e obras | Semanal ou mensal |
| Segurança pública | Mensal, conforme publicação |
| Saúde epidemiológica | Semanal ou mensal, conforme base |
| Educação | Anual ou conforme divulgação |
| IBGE e PIB municipal | Conforme calendário de publicação |
| Desmatamento e queimadas | Mensal ou conforme produto |
| PPA e metas | Sempre que houver revisão ou novo documento |
| PDFs de avaliação | Na publicação de cada exercício |
| Catálogo GeoTática | Verificação trimestral ou semestral |

A periodicidade real deve respeitar a publicação oficial. Não rotular uma base como tempo real se ela é divulgada mensalmente ou anualmente.

## 12.2. Pipeline de atualização

1. Verificar disponibilidade da fonte;
2. executar coleta;
3. salvar resposta original;
4. registrar timestamp;
5. validar estrutura;
6. normalizar;
7. comparar com a versão anterior;
8. identificar novos registros e retificações;
9. executar regras de qualidade;
10. atualizar tabelas analíticas;
11. recalcular indicadores dependentes;
12. atualizar painéis;
13. registrar log e resultado;
14. notificar administrador em caso de falha.

## 12.3. Indicadores de qualidade dos dados

- percentual de campos preenchidos;
- quantidade de registros rejeitados;
- duplicidades;
- atraso de atualização;
- divergência entre fontes;
- mudanças de metodologia;
- cobertura territorial;
- cobertura temporal;
- confiabilidade da extração documental.

Criar um selo informativo por dado:
- oficial publicado;
- extraído de documento;
- calculado pela plataforma;
- estimado;
- preliminar;
- em validação;
- desatualizado.

---

# 13. Segurança, LGPD e integridade

- Utilizar HTTPS em todos os ambientes;
- armazenar segredos em variáveis protegidas ou secret manager;
- aplicar RBAC (perfis e permissões);
- separar ambiente de desenvolvimento, homologação e produção;
- registrar logs de acesso e alteração;
- realizar backups e testes de restauração;
- criptografar dados sensíveis em repouso quando aplicável;
- evitar armazenar dados pessoais desnecessários;
- anonimizar ou agregar dados de segurança e saúde;
- aplicar controles de retenção;
- revisar licenças e termos de uso;
- documentar bases com dados pessoais;
- não expor tokens ou credenciais no frontend;
- não permitir execução arbitrária de consultas SQL pelo usuário;
- proteger endpoints contra abuso e scraping.

Perfis sugeridos:
- visitante público;
- analista;
- editor de dados;
- administrador;
- auditor.

---

# 14. Experiência do usuário e navegação

## 14.1. Menu principal

1. Visão Geral;
2. PPA e Planejamento;
3. Indicadores;
4. Secretarias;
5. Orçamento;
6. Obras e Infraestrutura;
7. Segurança Pública;
8. Saúde;
9. Educação;
10. Desenvolvimento Econômico;
11. Meio Ambiente;
12. Inteligência Territorial;
13. Municípios;
14. Relatórios;
15. Fontes de Dados;
16. Administração.

## 14.2. Filtros persistentes

- exercício;
- período;
- secretaria;
- programa;
- ação;
- indicador;
- município;
- região;
- área de resultado;
- fonte;
- status da atualização.

Os filtros devem ser sincronizados entre mapa, gráficos, tabelas e cartões, evitando resultados contraditórios.

## 14.3. Responsividade

Desktop:
- visão analítica completa;
- tabelas densas;
- mapas e painéis lado a lado.

Tablet:
- filtros recolhíveis;
- gráficos empilhados;
- tabelas com colunas prioritárias.

Mobile:
- cartões de indicadores;
- gráficos em coluna;
- mapa com painel inferior;
- filtros em drawer;
- tabelas convertidas em listas;
- navegação simplificada.

---

# 15. Indicadores estratégicos específicos do Amazonas

Além do PPA, criar um eixo transversal para acompanhar características territoriais e logísticas próprias do Estado.

## 15.1. Conectividade territorial

- percentual de municípios conectados por rodovia;
- municípios com acesso rodoviário permanente;
- quilômetros de estradas vicinais em condição de trafegabilidade;
- comunidades com acesso fluvial regular;
- tempo de deslocamento até a sede municipal;
- tempo de deslocamento até serviços de saúde;
- tempo de deslocamento até serviços educacionais.

## 15.2. Logística e integração regional

- custo logístico por tonelada;
- tempo de transporte entre municípios;
- movimentação portuária;
- disponibilidade de terminais hidroviários;
- capacidade de armazenagem;
- interrupções de transporte por seca ou cheia;
- custo de abastecimento de localidades remotas.

## 15.3. Vulnerabilidade climática

- população exposta a cheias;
- população exposta à estiagem;
- comunidades isoladas;
- municípios em emergência;
- áreas queimadas;
- perdas econômicas;
- interrupção de serviços públicos;
- tempo de resposta da Defesa Civil.

## 15.4. Acesso a serviços públicos

- população a até determinada distância de unidade de saúde;
- população a até determinada distância de escola;
- escolas com internet;
- unidades de saúde com infraestrutura adequada;
- municípios com serviços especializados;
- cobertura de água e esgoto;
- cobertura de coleta de resíduos.

## 15.5. Desenvolvimento econômico territorial

- PIB per capita municipal;
- emprego formal por habitante;
- renda média;
- produção agropecuária;
- empresas ativas;
- acesso ao crédito;
- investimentos públicos por habitante;
- participação de fornecedores locais em compras públicas.

Esses indicadores devem ser marcados como **complementares/propostos** quando não fizerem parte do cadastro oficial do PPA.

---

# 16. Análises e recursos avançados

## 16.1. Relação entre orçamento e resultado

Permitir cruzar:
- investimento por município;
- execução física;
- entrega de serviços;
- evolução de indicadores sociais.

Exemplo: comparar investimentos rodoviários por município com tempo de deslocamento, acesso a serviços e produção econômica.

A plataforma deve apresentar associação estatística, não causalidade automática.

## 16.2. Análise de desigualdade territorial

- dispersão de indicadores entre municípios;
- distância entre maior e menor valor;
- mediana estadual;
- distribuição por região;
- mapas de concentração;
- evolução da desigualdade ao longo do tempo.

## 16.3. Alertas

Criar alertas configuráveis:
- indicador sem atualização;
- meta fora da trajetória;
- execução financeira muito superior à execução física;
- obra com prazo vencido;
- contrato sem medição recente;
- queda abrupta em série;
- mudança metodológica;
- fonte indisponível;
- divergência entre fontes.

O alerta deve explicar a regra que o disparou e a fonte utilizada.

## 16.4. Assistente analítico

Um assistente de IA pode responder perguntas sobre os dados disponíveis:

- Quais municípios têm menor cobertura de saneamento?
- Quais obras estão atrasadas?
- Qual secretaria possui mais indicadores sem atualização?
- Como evoluiu a mortalidade infantil?
- Qual foi a execução física e financeira do programa MAIS INFRA?
- Quais metas foram revisadas para 2026–2027?

O assistente deve:
- consultar apenas dados indexados e autorizados;
- citar fonte, período e data de atualização;
- apresentar fórmula;
- informar quando não houver dado;
- não inventar valores;
- não misturar versões do PPA;
- registrar a consulta e a versão dos dados usados.

---

# 17. Requisitos de qualidade e aceitação

A plataforma só deve ser considerada funcional quando:

1. Todos os indicadores exibidos tiverem fonte, unidade, período e data de atualização.
2. Metas históricas e vigentes estiverem versionadas.
3. O usuário puder abrir o documento original e localizar a página de origem.
4. Valores ausentes forem distintos de zero.
5. Séries temporais preservarem lacunas e revisões.
6. Execução física e financeira forem exibidas separadamente.
7. Indicadores de redução tiverem polaridade correta.
8. Filtros territoriais não duplicarem valores.
9. Contratos e obras não provocarem dupla contagem financeira.
10. Os painéis funcionarem em desktop e mobile.
11. A ingestão registrar sucesso, falha e quantidade de registros.
12. Os dados brutos forem preservados.
13. Os relatórios puderem ser exportados.
14. O usuário conseguir identificar se o dado é oficial, calculado ou estimado.
15. O sistema conseguir reproduzir um indicador a partir da fonte e fórmula registradas.

---

# 18. Plano de implementação por fases

## Fase 1 — Fundação documental e PPA

- Baixar e catalogar Lei nº 6.671/2023;
- importar anexos do PPA;
- importar PPA de Bolso;
- importar Relatório de Avaliação 2024;
- importar Anexo I e Anexo II;
- importar Lei nº 7.978/2025;
- extrair programas, ações, indicadores e metas;
- construir cadastro de versões;
- validar amostras com documentos originais.

**Entrega:** catálogo pesquisável do PPA, metas e indicadores oficiais.

## Fase 2 — Modelo de dados e painel geral

- PostgreSQL e PostGIS;
- API principal;
- cadastro de secretarias;
- cadastro de programas;
- cadastro de indicadores;
- metas e observações;
- filtros globais;
- painel geral;
- gráficos de séries temporais.

**Entrega:** primeira versão navegável do Observatório.

## Fase 3 — Orçamento e transparência

- integrar dados orçamentários;
- organizar dotação, empenho, liquidação e pagamento;
- construir painéis por órgão, programa e ação;
- comparar execução física e financeira;
- criar relatórios exportáveis.

**Entrega:** módulo de execução orçamentária.

## Fase 4 — Obras e infraestrutura

- integrar contratos;
- importar base de obras;
- associar obras a municípios e geometrias;
- cadastrar medições;
- calcular execução física e financeira;
- construir mapa de obras;
- criar alertas de prazo e medição.

**Entrega:** módulo de infraestrutura e obras.

## Fase 5 — Indicadores setoriais

Prioridade de integração:
1. Saúde;
2. Educação;
3. Segurança pública;
4. Meio ambiente;
5. Economia e trabalho;
6. Saneamento e habitação;
7. Agricultura e produção rural.

**Entrega:** painéis setoriais e séries históricas.

## Fase 6 — Inteligência territorial

- malha municipal;
- regiões de planejamento;
- rodovias;
- hidrografia;
- equipamentos públicos;
- camadas ambientais;
- mapas coropléticos;
- análise espacial;
- indicadores municipais.

**Entrega:** atlas de indicadores e desigualdades territoriais.

## Fase 7 — Automação, alertas e IA

- orquestração de atualizações;
- monitoramento de conectores;
- detecção de anomalias;
- alertas;
- assistente analítico com citações;
- geração automatizada de relatórios.

**Entrega:** observatório com atualização recorrente e análise assistida.

---

# 19. Backlog inicial de desenvolvimento

| ID | Prioridade | Item | Critério de conclusão |
|---|---|---|---|
| P01 | Crítica | Catálogo documental | PDFs e leis catalogados com hash e metadados |
| P02 | Crítica | Extração do PPA | Programas, indicadores, ações e metas estruturados |
| P03 | Crítica | Versionamento de metas | Metas originais e revisadas coexistem |
| P04 | Crítica | Modelo territorial | Municípios e regiões com códigos e geometrias |
| P05 | Alta | Cadastro de indicadores | Fórmula, unidade, polaridade e fonte |
| P06 | Alta | Painel geral | Cartões, filtros, séries e mapas |
| P07 | Alta | Séries históricas | Observações com data e origem |
| P08 | Alta | Execução orçamentária | Dotação, empenho, liquidação e pagamento |
| P09 | Alta | Módulo de obras | Contratos, obras, medições e mapa |
| P10 | Alta | Segurança pública | Integração e séries históricas |
| P11 | Média | Saúde e educação | Indicadores e comparações municipais |
| P12 | Média | Meio ambiente | Desmatamento, queimadas e clima |
| P13 | Média | Relatórios | Exportação PDF, CSV e XLSX |
| P14 | Média | Qualidade dos dados | Alertas, logs e validações |
| P15 | Média | Assistente de IA | Perguntas respondidas com fontes |
| P16 | Média | Aplicação mobile | Layout responsivo e filtros adaptados |

---

# 20. Primeira carga de dados: prioridades concretas

Para evitar começar com muitos conectores e pouca entrega, a primeira versão deve carregar um conjunto fechado de dados de alta utilidade:

### Pacote A — Planejamento
- PPA 2024–2027;
- versão original da Lei nº 6.671/2023;
- revisão de 2026–2027 da Lei nº 7.978/2025;
- Relatório de Avaliação 2024;
- Anexo I e Anexo II;
- PPA de Bolso.

### Pacote B — Território
- malha municipal do IBGE;
- regiões de planejamento do Estado;
- rodovias estaduais e federais;
- hidrografia;
- sedes municipais;
- equipamentos públicos disponíveis.

### Pacote C — Indicadores
- saúde;
- educação;
- segurança;
- emprego e renda;
- PIB municipal;
- saneamento;
- desmatamento e queimadas.

### Pacote D — Execução
- orçamento por órgão e ação;
- contratos e convênios;
- obras e medições;
- entregas físicas;
- valores empenhados, liquidados e pagos.

---

# 21. Referências e links de trabalho

## Planejamento estadual

- [Portal do Planejamento do Amazonas — PPA](https://portaldoplanejamento.am.gov.br/ppa/)
- [PPA 2024–2027](https://portaldoplanejamento.am.gov.br/ppa-2024-2027/)
- [Lei nº 6.671/2023](https://legisla.imprensaoficial.am.gov.br/diario_am/12/2023/12/10939)
- [Relatório de Avaliação PPA 2024–2027 — Exercício 2024 (PDF)](https://portaldoplanejamento.am.gov.br/wp-content/uploads/2025/04/AVALIACAO-PPA-2024-2027_EXERCICIO-2024.pdf)
- [Diretório de documentos do Portal do Planejamento](https://portaldoplanejamento.am.gov.br/wp-content/uploads/2024/08/)
- [SPLAM](https://splam.sedecti.am.gov.br/)
- [Lei nº 7.978/2025 — Diário Oficial](https://diario.imprensaoficial.am.gov.br/portal/edicoes/download/17985)

## Repositórios solicitados

- [API Segurança Pública — GitHub](https://github.com/rayonnunes/api_seguranca_publica)
- [GeoTática — Plataforma de Dados](https://geotatica.github.io/Plataforma_Dados/)

## Fontes nacionais

- [IBGE](https://www.ibge.gov.br/)
- [SIDRA/IBGE](https://sidra.ibge.gov.br/)
- [DATASUS](https://datasus.saude.gov.br/)
- [INEP](https://www.gov.br/inep/)
- [SINESP](https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica)
- [SICONFI](https://siconfi.tesouro.gov.br/)
- [Portal da Transparência Federal](https://portaldatransparencia.gov.br/)
- [PNCP](https://pncp.gov.br/)
- [Transferegov](https://www.gov.br/transferegov/pt-br)
- [DNIT](https://www.gov.br/dnit/)
- [ANTT](https://www.gov.br/antt/)
- [ANTAQ](https://www.gov.br/antaq/)
- [ANA](https://www.gov.br/ana/)
- [INPE](https://www.gov.br/inpe/)
- [MapBiomas](https://mapbiomas.org/)
- [SINISA](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa)

---

# 22. Orientação final para o desenvolvimento

O Observatório deve ser construído em torno de uma estrutura de dados confiável, e não em torno de telas isoladas.

A ordem recomendada é:

1. Extrair e estruturar integralmente o PPA e seus relatórios;
2. validar metas e valores com os PDFs originais;
3. construir o banco histórico e territorial;
4. integrar fontes oficiais;
5. calcular indicadores com metodologia documentada;
6. criar painéis, gráficos, mapas e relatórios;
7. automatizar atualizações;
8. adicionar análises assistidas por IA.

**Não preencher lacunas com números estimados sem identificação.** Quando não houver dado atualizado, a interface deve mostrar o último valor conhecido, a data de referência e o status de atualização.

**Não chamar dado anual de tempo real.** Cada indicador deve exibir a periodicidade de publicação e a data da última observação.

**Não usar metas antigas como metas vigentes.** Toda meta deve estar vinculada à versão legal e ao período de validade.

**Não confundir execução orçamentária com resultado social.** A plataforma deve permitir observar as relações entre orçamento, entregas e resultados, mas preservar cada dimensão.

O resultado esperado é uma plataforma que permita acompanhar o Governo do Amazonas em quatro dimensões integradas: **planejamento, orçamento, entregas e resultados territoriais**.
