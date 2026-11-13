"""P04 — indicadores de fontes públicas nacionais para os 62 municípios do Amazonas.

Baixa os arquivos originais para bronze/publicos/ (cache: só baixa de novo com --atualizar),
extrai os indicadores e grava dados/painel.json e dados/painel.js (window.PAINEL).

Fontes:
  IBGE/SIDRA  — população (Censo 2022 e estimativas), PIB municipal, saneamento e alfabetização (Censo 2022)
  INEP        — IDEB 2005–2023, rede pública, anos iniciais e finais
  INPE        — PRODES (desmatamento por município) e BDQueimadas (focos de calor, satélite de referência)
  MJSP/SINESP — BancoVDE (eventos de segurança pública por município e mês)
  DATASUS     — CNES (estabelecimentos de saúde) pela API de dados abertos
  GeoTática   — catálogo de fontes (descoberta e metadados, não é API)

Regras: valor ausente fica None (nunca zero); cada indicador leva fonte, URL, ano de referência e tipo
(oficial = publicado pela fonte; calculado = derivado aqui, com a fórmula em `metodo`).
"""
import csv, io, json, re, sys, time, unicodedata, urllib.request, zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BRONZE = RAIZ / "bronze" / "publicos"
SAIDA = RAIZ / "dados" / "painel.json"
MUNIC_JS = RAIZ.parent / "dashboard" / "municipios.js"
ATUALIZAR = "--atualizar" in sys.argv
sys.stdout.reconfigure(encoding="utf-8")
AGORA = datetime.now(timezone.utc).isoformat(timespec="seconds")
ANO_ATUAL = datetime.now().year

ingestoes, indicadores = [], []


def baixar(url, destino, timeout=300):
    """Baixa para bronze (cache). Devolve o caminho."""
    destino = BRONZE / destino
    if destino.exists() and destino.stat().st_size > 0 and not ATUALIZAR:
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (observatorio-amazonas)"})
    for tentativa in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                destino.write_bytes(r.read())
            return destino
        except Exception:
            if tentativa == 2:
                raise
            time.sleep(3)


def json_url(url, destino):
    return json.loads(baixar(url, destino).read_text(encoding="utf-8"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z]", "", s)


def num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    v = str(v).strip()
    if v in ("", "-", "...", "X", "..", "ND"):
        return None
    try:
        return float(v.replace(",", "."))
    except ValueError:
        return None


def registrar(fonte, inicio, n, erro=None, url=None):
    ingestoes.append({"fonte": fonte, "url": url, "data_hora": AGORA, "duracao_s": round(time.time() - inicio, 1),
                      "registros": n, "status": "falha" if erro else "ok", "erro": erro})
    print(f"{'FALHA' if erro else 'ok   '} {fonte}: {n} registros{(' — ' + erro) if erro else ''}")


def indicador(**k):
    base = dict(estado=None, municipios={}, serie=[], tipo="oficial", polaridade="maior_melhor", metodo=None,
                nivel_municipal=True, nota=None)
    base.update(k)
    indicadores.append(base)


# ---------------------------------------------------------------- municípios
def municipios():
    txt = MUNIC_JS.read_text(encoding="utf-8")
    m = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
    return [{"cod": x["cod"], "nome": x["nome"]} for x in m["municipios"]]


MUN = municipios()
COD = {m["cod"] for m in MUN}
POR_NOME = {norm(m["nome"]): m["cod"] for m in MUN}


# ---------------------------------------------------------------- IBGE / SIDRA
def sidra(tabela, var, periodo="last", classif="", destino=None):
    """Devolve {(cod, ano): valor} para N6 (municípios do AM) e N3 (estado = '13')."""
    out = {}
    for nivel in ("n6/in%20n3%2013", "n3/13"):
        url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/{nivel}/v/{var}/p/{periodo}{classif}"
        nome = f"sidra/{tabela}_{var}_{periodo}_{re.sub(r'[^0-9a-z]', '', classif)}_{nivel[:2]}.json"
        linhas = json_url(url, nome)[1:]
        for l in linhas:
            cod = l["D1C"][:7] if nivel.startswith("n6") else "13"
            ano = int(next(l[k] for k in ("D3C", "D2C", "D4C") if k in l and re.fullmatch(r"\d{4}", str(l[k]))))
            out[(cod, ano)] = num(l["V"])
    return out


def ultimo_ano(d):
    return max(a for (_, a) in d)


def ibge():
    t = time.time()
    try:
        c22 = {v: sidra(4714, v, "2022") for v in (93, 6318, 614)}
        indicador(id="pop_censo", area="socioeconomia", nome="População residente (Censo 2022)", unidade="pessoas",
                  fonte="IBGE — Censo Demográfico 2022 (SIDRA 4714)", fonte_url="https://sidra.ibge.gov.br/tabela/4714",
                  ref="2022", estado=c22[93][("13", 2022)],
                  municipios={c: v for (c, a), v in c22[93].items() if c in COD})
        indicador(id="densidade", area="socioeconomia", nome="Densidade demográfica", unidade="hab/km²",
                  fonte="IBGE — Censo Demográfico 2022 (SIDRA 4714)", fonte_url="https://sidra.ibge.gov.br/tabela/4714",
                  ref="2022", estado=c22[614][("13", 2022)], polaridade="neutra",
                  municipios={c: v for (c, a), v in c22[614].items() if c in COD})
        indicador(id="area", area="socioeconomia", nome="Área territorial", unidade="km²", polaridade="neutra",
                  fonte="IBGE — Censo Demográfico 2022 (SIDRA 4714)", fonte_url="https://sidra.ibge.gov.br/tabela/4714",
                  ref="2022", estado=c22[6318][("13", 2022)],
                  municipios={c: v for (c, a), v in c22[6318].items() if c in COD})

        est = sidra(6579, 9324, "all")
        a = ultimo_ano(est)
        indicador(id="pop_estimada", area="socioeconomia", nome=f"População estimada {a}", unidade="pessoas",
                  fonte="IBGE — Estimativas da população (SIDRA 6579)", fonte_url="https://sidra.ibge.gov.br/tabela/6579",
                  ref=str(a), estado=est[("13", a)], municipios={c: v for (c, y), v in est.items() if y == a and c in COD},
                  serie=sorted([y, v] for (c, y), v in est.items() if c == "13"), polaridade="neutra")
        global POP
        POP = est

        pib = sidra(5938, 37, "all")
        a = ultimo_ano(pib)
        indicador(id="pib", area="socioeconomia", nome="PIB a preços correntes", unidade="R$ mil",
                  fonte="IBGE — PIB dos Municípios (SIDRA 5938)", fonte_url="https://sidra.ibge.gov.br/tabela/5938",
                  ref=str(a), estado=pib[("13", a)], municipios={c: v for (c, y), v in pib.items() if y == a and c in COD},
                  serie=sorted([y, v] for (c, y), v in pib.items() if c == "13"))
        pc = {}
        def pop_ano(c, y):
            if y == 2022:
                return c22[93].get((c, 2022))
            if (c, y) in est:
                return est[(c, y)]
            if y == 2023 and (c, 2024) in est and (c, 2022) in c22[93]:  # IBGE não estimou 2023
                return (c22[93][(c, 2022)] + est[(c, 2024)]) / 2
            return None
        for (c, y), v in pib.items():
            p = pop_ano(c, y)
            if v is not None and p:
                pc[(c, y)] = round(v * 1000 / p, 2)
        indicador(id="pib_pc", area="socioeconomia", nome="PIB per capita", unidade="R$", tipo="calculado",
                  metodo="PIB a preços correntes (SIDRA 5938) × 1000 ÷ população do mesmo ano (estimativa SIDRA 6579; 2022 usa o Censo; 2023, sem estimativa publicada, usa a média entre Censo 2022 e estimativa 2024)",
                  fonte="IBGE — SIDRA 5938 e 6579", fonte_url="https://sidra.ibge.gov.br/tabela/5938", ref=str(a),
                  estado=pc.get(("13", a)), municipios={c: v for (c, y), v in pc.items() if y == a and c in COD},
                  serie=sorted([y, v] for (c, y), v in pc.items() if c == "13"))
        va = {"Agropecuária": 513, "Indústria": 517, "Serviços": 6575, "Administração pública": 525}
        comp = {k: sidra(5938, v, "all") for k, v in va.items()}
        # o detalhamento setorial sai depois do PIB total: usa o último ano com os quatro setores publicados
        av = max(y for (c, y), v in comp["Serviços"].items() if c in COD and v is not None)
        indicador(id="va_setores", area="socioeconomia", nome="Valor adicionado por setor", unidade="R$ mil",
                  fonte="IBGE — PIB dos Municípios (SIDRA 5938)", fonte_url="https://sidra.ibge.gov.br/tabela/5938",
                  ref=str(av), polaridade="neutra", nivel_municipal=False, tipo="calculado",
                  metodo="Soma dos 62 municípios (SIDRA 5938); a tabela não traz o detalhamento setorial por UF",
                  composicao={k: (sum(v for (c, y), v in d.items() if y == av and c in COD and v is not None) or None) for k, d in comp.items()},
                  municipios={})

        san = [("agua_rede", 6803, "/c1821/72144", "Domicílios ligados à rede geral de água (uso principal)"),
               ("esgoto_adequado", 6805, "/c11558/46290", "Domicílios com esgoto por rede geral, pluvial ou fossa ligada à rede"),
               ("lixo_coletado", 6892, "/c67/2520", "Domicílios com lixo coletado")]
        for iid, tab, cl, nome in san:
            d = sidra(tab, 1000381, "2022", cl)
            indicador(id=iid, area="infraestrutura", nome=nome, unidade="%", ref="2022",
                      fonte=f"IBGE — Censo Demográfico 2022 (SIDRA {tab})", fonte_url=f"https://sidra.ibge.gov.br/tabela/{tab}",
                      estado=d.get(("13", 2022)), municipios={c: v for (c, y), v in d.items() if c in COD})
        alf = sidra(9543, 2513, "2022", "/c2/6794/c86/95251/c287/100362")
        indicador(id="alfabetizacao", area="educacao", nome="Taxa de alfabetização (15 anos ou mais)", unidade="%",
                  ref="2022", fonte="IBGE — Censo Demográfico 2022 (SIDRA 9543)", fonte_url="https://sidra.ibge.gov.br/tabela/9543",
                  estado=alf.get(("13", 2022)), municipios={c: v for (c, y), v in alf.items() if c in COD})
        registrar("IBGE/SIDRA", t, sum(len(i["municipios"]) for i in indicadores), url="https://apisidra.ibge.gov.br")
    except Exception as e:
        registrar("IBGE/SIDRA", t, 0, repr(e)[:200], "https://apisidra.ibge.gov.br")


POP = {}


# ---------------------------------------------------------------- INEP / IDEB
def ideb():
    for etapa, rot in (("iniciais", "anos iniciais"), ("finais", "anos finais")):
        t = time.time()
        url = f"https://download.inep.gov.br/ideb/resultados/divulgacao_anos_{etapa}_municipios_2023.zip"
        try:
            import openpyxl
            z = zipfile.ZipFile(baixar(url, f"inep/ideb_{etapa}_municipios_2023.zip"))
            xl = next(n for n in z.namelist() if n.endswith(".xlsx"))
            ws = openpyxl.load_workbook(io.BytesIO(z.read(xl)), read_only=True).worksheets[0]
            cab, serie_mun = None, {}
            for r in ws.iter_rows(values_only=True):
                if r and r[0] == "SG_UF":
                    cab = list(r)
                    continue
                if cab and r[0] == "AM" and r[3] == "Pública":
                    d = dict(zip(cab, r))
                    serie_mun[str(d["CO_MUNICIPIO"])] = {int(k[-4:]): num(v) for k, v in d.items()
                                                         if k and k.startswith("VL_OBSERVADO_")}
            anos = sorted({a for s in serie_mun.values() for a in s})
            mun = {c: s.get(2023) for c, s in serie_mun.items() if c in COD}
            # estado: mediana municipal só como referência visual; o IDEB estadual oficial vem do arquivo de UFs
            indicador(id=f"ideb_{etapa[:2]}", area="educacao", nome=f"IDEB — {rot} (rede pública)", unidade="índice",
                      ref="2023", fonte="INEP — IDEB 2023, resultados por município", fonte_url=url,
                      municipios=mun, serie_municipal={c: [[a, s.get(a)] for a in anos] for c, s in serie_mun.items() if c in COD},
                      nota="Valor estadual não publicado neste arquivo; o painel mostra a distribuição municipal.")
            registrar(f"INEP/IDEB {rot}", t, len(mun), url=url)
        except Exception as e:
            registrar(f"INEP/IDEB {rot}", t, 0, repr(e)[:200], url)


# ---------------------------------------------------------------- INPE / PRODES
def prodes():
    t = time.time()
    for ano in (ANO_ATUAL, ANO_ATUAL - 1, ANO_ATUAL - 2, 2022):
        url = f"http://www.dpi.inpe.br/prodesdigital/tabelatxt.php?ano={ano}&estado=AM&ordem=MUNICIPIO&type=tabela&output=txt"
        try:
            txt = baixar(url, f"inpe/prodes_am_{ano}.txt").read_bytes().decode("latin-1")
            linhas = list(csv.DictReader(io.StringIO(txt)))
            if not linhas or f"incremento{ano}" not in [k.strip() for k in linhas[0]]:
                continue
            linhas = [{k.strip(): v for k, v in l.items()} for l in linhas]
            anos = sorted(int(k[10:]) for k in linhas[0] if k.startswith("incremento"))
            inc = {l["CodIbge"]: {a: num(l[f"incremento{a}"]) for a in anos} for l in linhas if l["CodIbge"] in COD}
            flo = {l["CodIbge"]: num(l.get(f"Floresta{ano}")) for l in linhas if l["CodIbge"] in COD}
            area = {l["CodIbge"]: num(l["AreaKm2"]) for l in linhas if l["CodIbge"] in COD}
            serie = [[a, round(sum(v[a] or 0 for v in inc.values()), 1)] for a in anos]
            indicador(id="desmatamento", area="meio_ambiente", nome=f"Desmatamento (incremento anual PRODES {ano})", unidade="km²",
                      ref=str(ano), polaridade="menor_melhor", fonte="INPE — PRODES Amazônia, tabela por município",
                      fonte_url="http://www.dpi.inpe.br/prodesdigital/prodesmunicipal.php",
                      estado=serie[-1][1], municipios={c: v[ano] for c, v in inc.items()}, serie=serie,
                      serie_municipal={c: [[a, v[a]] for a in anos] for c, v in inc.items()},
                      nota="Soma estadual calculada a partir das linhas municipais da tabela PRODES.")
            tot_flo = sum(v or 0 for v in flo.values())
            indicador(id="floresta", area="meio_ambiente", nome=f"Floresta remanescente {ano}", unidade="% da área",
                      ref=str(ano), tipo="calculado", metodo=f"Floresta{ano} ÷ AreaKm2 da tabela PRODES × 100",
                      fonte="INPE — PRODES Amazônia", fonte_url="http://www.dpi.inpe.br/prodesdigital/prodesmunicipal.php",
                      estado=round(tot_flo / sum(area.values()) * 100, 2),
                      municipios={c: round(flo[c] / area[c] * 100, 2) for c in flo if flo[c] is not None and area[c]})
            registrar("INPE/PRODES", t, len(inc), url=url)
            return
        except Exception as e:
            erro = repr(e)[:200]
    registrar("INPE/PRODES", t, 0, locals().get("erro", "sem ano disponível"), "http://www.dpi.inpe.br/prodesdigital/")


# ---------------------------------------------------------------- INPE / Queimadas
def queimadas():
    t = time.time()
    base = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv"
    contagem = defaultdict(lambda: defaultdict(int))  # ano -> cod -> focos
    mensal = defaultdict(int)  # 'AAAA-MM' -> focos no estado
    sem_mun = 0
    try:
        def soma(linhas, filtro_am):
            nonlocal sem_mun
            for l in linhas:
                # mensais nacionais trazem todos os satélites: manter só o de referência, como nos anuais
                if filtro_am and (norm(l.get("estado", "")) != "AMAZONAS" or l.get("satelite") != "AQUA_M-T"):
                    continue
                data = (l.get("data_pas") or l.get("data_hora_gmt") or "")[:7]
                cod = l.get("municipio_id") if l.get("municipio_id") in COD else POR_NOME.get(norm(l.get("municipio", "")))
                if not data:
                    continue
                mensal[data] += 1
                if cod:
                    contagem[int(data[:4])][cod] += 1
                else:
                    sem_mun += 1

        for ano in range(2003, ANO_ATUAL):
            try:
                z = zipfile.ZipFile(baixar(f"{base}/anual/EstadosBr_sat_ref/AM/focos_br_am_ref_{ano}.zip", f"inpe/focos_am_{ano}.zip"))
                soma(csv.DictReader(io.StringIO(z.read(z.namelist()[0]).decode("utf-8", "replace"))), False)
            except Exception:
                # ano corrente ainda sem arquivo anual: usa os mensais nacionais filtrando o AM
                for mes in range(1, 13):
                    try:
                        p = baixar(f"{base}/mensal/Brasil/focos_mensal_br_{ano}{mes:02d}.csv", f"inpe/focos_br_{ano}{mes:02d}.csv")
                        soma(csv.DictReader(io.StringIO(p.read_bytes().decode("utf-8", "replace"))), True)
                    except Exception:
                        pass
        for mes in range(1, 13):
            try:
                p = baixar(f"{base}/mensal/Brasil/focos_mensal_br_{ANO_ATUAL}{mes:02d}.csv", f"inpe/focos_br_{ANO_ATUAL}{mes:02d}.csv")
                soma(csv.DictReader(io.StringIO(p.read_bytes().decode("utf-8", "replace"))), True)
            except Exception:
                pass
        anos = sorted(contagem)
        ult = max(a for a in anos if a < ANO_ATUAL)
        meses = sorted(mensal)
        indicador(id="focos", area="meio_ambiente", nome=f"Focos de calor {ult}", unidade="focos", ref=str(ult),
                  polaridade="menor_melhor", fonte="INPE — BDQueimadas, satélite de referência",
                  fonte_url=f"{base}/anual/EstadosBr_sat_ref/AM/",
                  estado=sum(contagem[ult].values()), municipios={c: contagem[ult].get(c, 0) for c in COD},
                  serie=[[a, sum(contagem[a].values())] for a in anos],
                  serie_mensal=[[m, mensal[m]] for m in meses],
                  serie_municipal={c: [[a, contagem[a].get(c, 0)] for a in anos] for c in COD},
                  nota=f"{ANO_ATUAL} parcial até {meses[-1]} (arquivos mensais). {sem_mun} focos sem município reconhecido ficam só no total mensal.")
        registrar("INPE/BDQueimadas", t, sum(mensal.values()), url=base)
    except Exception as e:
        registrar("INPE/BDQueimadas", t, 0, repr(e)[:200], base)


# ---------------------------------------------------------------- MJSP / SINESP VDE
EVENTOS = {
    "Homicídio doloso": "homicidio", "Feminicídio": "feminicidio", "Roubo seguido de morte (latrocínio)": "latrocinio",
    "Lesão corporal seguida de morte": "lesao_morte", "Tentativa de homicídio": "tentativa_homicidio",
    "Tentativa de feminicídio": "tentativa_feminicidio", "Mortes no trânsito": "transito",
    "Morte no trânsito ou em decorrência dele (exceto homicídio doloso)": "transito",
    "Suicídio": "suicidio", "Mortes a esclarecer (sem indício de crime)": "mortes_esclarecer",
    "Morte por intervenção de Agente do Estado": "intervencao_estado",
    "Estupro": "estupro", "Estupro de vulnerável": "estupro_vulneravel", "Roubo de veículo": "roubo_veiculo",
    "Furto de veículo": "furto_veiculo", "Roubo de carga": "roubo_carga", "Tráfico de drogas": "trafico",
    "Arma de Fogo Apreendida": "armas_apreendidas", "Pessoa Desaparecida": "desaparecidos",
}
CVLI = ("homicidio", "feminicidio", "latrocinio", "lesao_morte")


def sinesp_ano(ano):
    """Linhas do AM do BancoVDE de um ano, em cache json (a planilha nacional leva ~1 min para ler)."""
    cache = BRONZE / "sinesp" / f"vde_am_{ano}.json"
    if cache.exists() and not ATUALIZAR:
        return json.loads(cache.read_text(encoding="utf-8"))
    import openpyxl
    url = f"https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados/bancovde-{ano}.xlsx/@@download/file"
    p = baixar(url, f"sinesp/bancovde-{ano}.xlsx", timeout=600)
    if p.read_bytes()[:2] != b"PK":
        p.unlink()
        raise ValueError("arquivo não é xlsx")
    ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]
    it = ws.iter_rows(values_only=True)
    cab = list(next(it))
    linhas = []
    for r in it:
        d = dict(zip(cab, r))
        if d["uf"] != "AM":
            continue
        dr = d["data_referencia"]
        linhas.append({"municipio": d["municipio"], "evento": d["evento"],
                       "mes": dr.strftime("%Y-%m") if hasattr(dr, "strftime") else str(dr)[:7],
                       "vitimas": num(d["total_vitima"]), "total": num(d["total"]), "abrangencia": d["abrangencia"]})
    cache.write_text(json.dumps(linhas, ensure_ascii=False), encoding="utf-8")
    return linhas


def sinesp():
    t = time.time()
    fonte_url = "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados"
    mun_ano = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))  # ev -> ano -> cod -> n
    mensal = defaultdict(lambda: defaultdict(float))  # ev -> mes -> n (estado)
    anos_ok, n, nao_casados = [], 0, set()
    for ano in range(2019, ANO_ATUAL + 1):
        try:
            linhas = sinesp_ano(ano)
        except Exception as e:
            print(f"      SINESP {ano}: {repr(e)[:120]}")
            continue
        anos_ok.append(ano)
        for l in linhas:
            ev = EVENTOS.get(l["evento"])
            if not ev:
                continue
            # eventos letais vêm por vítima; os demais por ocorrência (total)
            v = l["vitimas"] if l["vitimas"] is not None and l["total"] is None else (l["total"] if l["total"] is not None else l["vitimas"])
            if v is None:
                continue
            n += 1
            mensal[ev][l["mes"]] += v
            cod = POR_NOME.get(norm(l["municipio"] or ""))
            if cod:
                mun_ano[ev][int(l["mes"][:4])][cod] += v
            elif l["abrangencia"] != "Estadual" or l["municipio"]:
                nao_casados.add(l["municipio"])
    if not anos_ok:
        registrar("MJSP/SINESP VDE", t, 0, "nenhum ano baixado", fonte_url)
        return
    for ev in CVLI:
        for m, v in mensal[ev].items():
            mensal["cvli"][m] += v
        for a, d in mun_ano[ev].items():
            for c, v in d.items():
                mun_ano["cvli"][a][c] += v
    meses_cvli = sorted(mensal["cvli"])
    ult_mes = meses_cvli[-1]
    ano_fech = max(a for a in anos_ok if sum(1 for m in mensal["cvli"] if m.startswith(str(a))) == 12)

    def pop(c, a):
        return POP.get((c, a)) or POP.get((c, max((y for (cc, y) in POP if cc == c and y <= a), default=0)))

    def taxa(ev, a):
        out = {}
        for c in COD:
            p = pop(c, a)
            v = mun_ano[ev][a].get(c, 0)
            out[c] = round(v / p * 1e5, 1) if p else None
        return out

    tot = sum(v for m, v in mensal["cvli"].items() if m.startswith(str(ano_fech)))
    indicador(id="cvli_taxa", area="seguranca", nome=f"CVLI por 100 mil habitantes ({ano_fech})", unidade="por 100 mil hab.",
              ref=str(ano_fech), tipo="calculado", polaridade="menor_melhor",
              metodo="(homicídio doloso + feminicídio + latrocínio + lesão corporal seguida de morte, vítimas SINESP VDE) ÷ população estimada IBGE × 100.000",
              fonte="MJSP — SINESP VDE (BancoVDE) e IBGE", fonte_url=fonte_url,
              estado=round(tot / pop("13", ano_fech) * 1e5, 1) if pop("13", ano_fech) else None,
              municipios=taxa("cvli", ano_fech),
              # só anos completos: taxa de ano parcial não é comparável
              serie=[[a, round(sum(v for m, v in mensal["cvli"].items() if m.startswith(str(a))) / pop("13", a) * 1e5, 1)]
                     for a in anos_ok if pop("13", a) and a <= ano_fech],
              nota=f"Dados mensais até {ult_mes}; a série anual da taxa usa só anos completos. Taxa municipal usa a estimativa populacional mais recente disponível para o ano.")
    rotulos = {"cvli": "CVLI (vítimas)", "homicidio": "Homicídio doloso (vítimas)", "feminicidio": "Feminicídio (vítimas)",
               "latrocinio": "Latrocínio (vítimas)", "transito": "Mortes no trânsito (vítimas)",
               "tentativa_homicidio": "Tentativa de homicídio", "estupro": "Estupro (ocorrências)",
               "roubo_veiculo": "Roubo de veículo (ocorrências)", "trafico": "Tráfico de drogas (ocorrências)",
               "armas_apreendidas": "Armas de fogo apreendidas", "suicidio": "Suicídio (vítimas)",
               "intervencao_estado": "Mortes por intervenção de agente do Estado"}
    for ev, nome in rotulos.items():
        if ev not in mensal:
            continue
        tem_mun = bool(mun_ano[ev].get(ano_fech))
        indicador(id=f"sinesp_{ev}", area="seguranca", nome=nome, unidade="registros", ref=str(ano_fech),
                  polaridade="maior_melhor" if ev == "armas_apreendidas" else "menor_melhor",
                  fonte="MJSP — SINESP VDE (BancoVDE)", fonte_url=fonte_url, nivel_municipal=tem_mun,
                  estado=round(sum(v for m, v in mensal[ev].items() if m.startswith(str(ano_fech)))),
                  municipios={c: mun_ano[ev][ano_fech].get(c, 0) for c in COD} if tem_mun else {},
                  serie=[[a, round(sum(v for m, v in mensal[ev].items() if m.startswith(str(a))))] for a in anos_ok],
                  serie_mensal=[[m, round(mensal[ev][m])] for m in sorted(mensal[ev])],
                  nota=None if tem_mun else "Publicado só no total estadual.")
    registrar("MJSP/SINESP VDE", t, n, url=fonte_url)
    if nao_casados:
        print("      municípios SINESP não reconhecidos:", sorted(x for x in nao_casados if x)[:10])


# ---------------------------------------------------------------- DATASUS / CNES
def cnes():
    t = time.time()
    url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
    cache = BRONZE / "cnes" / "estabelecimentos_am.json"
    try:
        if cache.exists() and not ATUALIZAR:
            todos = json.loads(cache.read_text(encoding="utf-8"))
        else:
            todos, off = [], 0
            while True:
                req = urllib.request.Request(f"{url}?codigo_uf=13&limit=20&offset={off}", headers={"User-Agent": "observatorio-amazonas"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    lote = json.loads(r.read()).get("estabelecimentos", [])
                todos += lote
                if len(lote) < 20:
                    break
                off += 1  # nesta API `offset` é o número da página, não do registro
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(todos, ensure_ascii=False), encoding="utf-8")
        cod6 = {c[:6]: c for c in COD}
        por = defaultdict(int)
        ubs = defaultdict(int)
        for e in todos:
            c = cod6.get(str(e.get("codigo_municipio"))[:6])
            if c:
                por[c] += 1
                if e.get("codigo_tipo_unidade") in (1, 2, 32, 71):  # posto, centro de saúde/UBS, unidade móvel fluvial, centro de apoio à saúde da família
                    ubs[c] += 1
        indicador(id="cnes_estab", area="saude", nome="Estabelecimentos de saúde cadastrados (CNES)", unidade="estabelecimentos",
                  ref=AGORA[:7], fonte="Ministério da Saúde — CNES, API de dados abertos", fonte_url=url,
                  estado=sum(por.values()), municipios={c: por.get(c, 0) for c in COD})
        pc = {c: round(ubs.get(c, 0) / POP[(c, max(y for (cc, y) in POP if cc == c))] * 1e4, 2) for c in COD if POP}
        indicador(id="atencao_basica", area="saude", nome="Unidades de atenção básica por 10 mil hab.", unidade="por 10 mil hab.",
                  ref=AGORA[:7], tipo="calculado",
                  metodo="Estabelecimentos CNES dos tipos 01 (posto), 02 (centro de saúde/UBS), 32 (unidade móvel fluvial) e 71 (apoio à saúde da família) ÷ população estimada × 10.000",
                  fonte="CNES e IBGE", fonte_url=url, municipios=pc,
                  estado=round(sum(ubs.values()) / POP[("13", max(y for (c, y) in POP if c == "13"))] * 1e4, 2) if POP else None)
        registrar("DATASUS/CNES", t, len(todos), url=url)
    except Exception as e:
        registrar("DATASUS/CNES", t, 0, repr(e)[:200], url)


# ---------------------------------------------------------------- GeoTática (catálogo de fontes)
TEMAS_OBS = {"saude", "educacao", "seguranca_publica", "socioeconomico", "meio_ambiente", "uso_cobertura_solo",
             "clima_meteorologia", "hidrografia", "riscos_desastres", "infraestrutura_urbana", "mobilidade_transportes",
             "energia_mineracao", "governanca_politicas_publicas", "limites_divisoes", "cadastro_planejamento",
             "agricultura_agropecuaria", "biodiversidade", "cartografia_referencia", "imagens_satelite"}


def geotatica():
    t = time.time()
    url = "https://geotatica.github.io/Plataforma_Dados/script.js"
    try:
        s = baixar(url, "geotatica/script.js").read_text(encoding="utf-8")
        i = s.index("const sources = [") + len("const sources = ")
        fontes, _ = json.JSONDecoder().raw_decode(s[i:])
        sel = []
        for f in fontes:
            temas = set(f.get("curadoria", {}).get("temas") or [f.get("tema_principal")])
            texto = norm(" ".join([f.get("name", ""), f.get("desc", ""), f.get("meta", "")]))
            relevante = f.get("escala") == "brasil" or "AMAZONAS" in texto or "AMAZONIA" in texto
            if relevante and temas & TEMAS_OBS:
                sel.append({"nome": f["name"], "url": f["url"], "tema": f.get("tema2_validado_planilha") or f.get("tema_principal"),
                            "temas": sorted(temas), "escala": f.get("escala"), "acesso": f.get("acesso"),
                            "tipo": f.get("tipo_fonte_rotulo"), "estrutura": f.get("estrutura_tecnica"),
                            "formatos": f.get("formatos"), "licenca": f.get("licenca"), "atualizacao": f.get("atualizacao"),
                            "status": f.get("status_fonte")})
        registrar("GeoTática (catálogo)", t, len(sel), url="https://geotatica.github.io/Plataforma_Dados/")
        return {"total_catalogo": len(fontes), "selecionadas": sel}
    except Exception as e:
        registrar("GeoTática (catálogo)", t, 0, repr(e)[:200], url)
        return {"total_catalogo": None, "selecionadas": []}


# ---------------------------------------------------------------- saída
CONECTORES = [
    {"id": "ibge", "nome": "IBGE — SIDRA", "orgao": "IBGE", "acesso": "API pública (JSON)", "periodicidade": "anual / censitária",
     "url": "https://apisidra.ibge.gov.br", "cobertura": "62 municípios"},
    {"id": "inep", "nome": "INEP — IDEB", "orgao": "INEP/MEC", "acesso": "arquivo XLSX", "periodicidade": "bienal",
     "url": "https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados", "cobertura": "62 municípios"},
    {"id": "prodes", "nome": "INPE — PRODES", "orgao": "INPE", "acesso": "arquivo CSV", "periodicidade": "anual",
     "url": "http://www.dpi.inpe.br/prodesdigital/prodesmunicipal.php", "cobertura": "62 municípios"},
    {"id": "queimadas", "nome": "INPE — BDQueimadas", "orgao": "INPE", "acesso": "arquivo CSV", "periodicidade": "diária (arquivos mensais)",
     "url": "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/", "cobertura": "62 municípios"},
    {"id": "sinesp", "nome": "MJSP — SINESP VDE", "orgao": "MJSP/SENASP", "acesso": "arquivo XLSX", "periodicidade": "mensal",
     "url": "https://www.gov.br/mj/pt-br/assuntos/sua-seguranca/seguranca-publica/estatistica/download/dnsp-base-de-dados", "cobertura": "62 municípios (eventos letais)"},
    {"id": "api_sinesp_rayon", "nome": "API Segurança Pública (rayonnunes)", "orgao": "projeto independente (MIT)", "acesso": "API HTTP",
     "periodicidade": "—", "url": "https://github.com/rayonnunes/api_seguranca_publica", "cobertura": "nacional",
     "nota": "Endpoint de produção HTTP sem resposta em 12/11/2026. Usada como referência: o painel lê a base oficial SINESP VDE que ela espelhava (mesmas categorias e granularidade município × mês)."},
    {"id": "cnes", "nome": "DATASUS — CNES", "orgao": "Ministério da Saúde", "acesso": "API pública (JSON)", "periodicidade": "mensal",
     "url": "https://apidadosabertos.saude.gov.br", "cobertura": "62 municípios"},
    {"id": "ppa", "nome": "PPA 2024–2027 — Relatórios de Avaliação", "orgao": "SEDECTI/AM", "acesso": "PDF (OCR + texto)",
     "periodicidade": "anual", "url": "https://portaldoplanejamento.am.gov.br/ppa-2024-2027/", "cobertura": "estado"},
    {"id": "geotatica", "nome": "GeoTática — Plataforma de Dados", "orgao": "GeoTática", "acesso": "catálogo (descoberta)",
     "periodicidade": "—", "url": "https://geotatica.github.io/Plataforma_Dados/", "cobertura": "catálogo"},
]


def main():
    BRONZE.mkdir(parents=True, exist_ok=True)
    ibge()
    ideb()
    prodes()
    queimadas()
    sinesp()
    cnes()
    geo = geotatica()
    assert len(MUN) == 62, len(MUN)
    for i in indicadores:  # garante ausente != zero e só municípios conhecidos
        i["municipios"] = {c: v for c, v in i["municipios"].items() if c in COD}
        assert i["fonte"] and i["fonte_url"] and i["ref"] and i["unidade"], i["id"]  # critério 1 da especificação
        assert not i["nivel_municipal"] or len(i["municipios"]) >= 50, (i["id"], len(i["municipios"]))
    out = {"gerado_em": AGORA, "municipios": MUN, "indicadores": indicadores, "conectores": CONECTORES,
           "ingestoes": ingestoes, "geotatica": geo}
    SAIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    SAIDA.with_suffix(".js").write_text("window.PAINEL = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{len(indicadores)} indicadores → {SAIDA.relative_to(RAIZ)} e painel.js")
    falhas = [g for g in ingestoes if g["status"] != "ok"]
    sys.exit(1 if len(falhas) == len(ingestoes) else 0)


if __name__ == "__main__":
    main()
