"""P05 — ampliação do painel: demografia, bairros e comunidades, eleitorado, equipamentos, economia e transporte.

Roda os conectores do P04 e acrescenta os novos. Grava:
  dados/painel.json + painel.js      (window.PAINEL: indicadores municipais, como no P04)
  dados/territorio.js                (window.TERRITORIO: bairros, comunidades urbanas, pirâmides, eleitorado)
  dados/camadas.js                   (window.CAMADAS: pontos e linhas georreferenciados)

Uso: python -I pipeline/p05_ampliacao.py [--atualizar]
Regras do P04 valem aqui: ausente é None, nunca zero; todo indicador leva fonte, URL, ano e tipo.
"""
import csv, io, json, math, re, sys, time, zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p04_publicos as B  # noqa: E402

RAIZ, BRONZE = B.RAIZ, B.BRONZE
CENSO = BRONZE / "censo"
FTP = "https://ftp.ibge.gov.br/Censos/Censo_Demografico_2022/"
AGREG = FTP + "Agregados_por_Setores_Censitarios/"
TERR = {"bairros": [], "comunidades": [], "municipios": {}, "estado": {}, "molduras": {}}
CAMADAS = {"pontos": {}, "linhas": {}}
COD = B.COD
EXTRAS = []  # conectores adicionais (TSE, equipamentos, economia, transporte) registram-se aqui


# ---------------------------------------------------------------- utilidades
def ler_csv_zip(nome, url):
    """Lê o CSV (;) de um zip do FTP do IBGE. Tenta UTF-8 e cai para latin-1."""
    p = B.baixar(url, f"censo/{nome}.zip", timeout=900)
    z = zipfile.ZipFile(p)
    raw = z.read(z.namelist()[0])
    try:
        txt = raw.decode("utf-8")
    except UnicodeDecodeError:
        txt = raw.decode("latin-1")
    return list(csv.DictReader(io.StringIO(txt), delimiter=";"))


def soma(r, cods):
    vs = [B.num(r.get(c)) for c in cods]
    return None if any(v is None for v in vs) else sum(vs)


def pct(a, b):
    return None if a is None or not b else round(a / b * 100, 2)


def simplificar(pts, tol):
    """Douglas-Peucker iterativo."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        a, b = pilha.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        n = math.hypot(dx, dy)
        dm, im = 0, None
        for i in range(a + 1, b):
            # anel fechado: início = fim, então mede a distância ao ponto
            d = abs(dy * (pts[i][0] - x1) - dx * (pts[i][1] - y1)) / n if n > 1e-9 else math.hypot(pts[i][0] - x1, pts[i][1] - y1)
            if d > dm:
                dm, im = d, i
        if im is not None and dm > tol:
            keep[im] = True
            pilha += [(a, im), (im, b)]
    return [p for p, k in zip(pts, keep) if k]


class Moldura:
    """Projeção equiretangular de lon/lat para um quadro SVG de largura fixa."""
    def __init__(self, bbox, largura=600):
        x0, y0, x1, y1 = bbox
        self.k = math.cos(math.radians((y0 + y1) / 2))
        self.x0, self.y1 = x0, y1
        self.s = largura / max((x1 - x0) * self.k, 1e-9)
        self.w, self.h = largura, round((y1 - y0) * self.s) or 1

    def xy(self, lon, lat):
        return ((lon - self.x0) * self.k * self.s, (self.y1 - lat) * self.s)

    def path(self, shape, tol=0.5):
        partes = list(shape.parts) + [len(shape.points)]
        d = []
        for a, b in zip(partes, partes[1:]):
            anel = simplificar([self.xy(*p) for p in shape.points[a:b]], tol)
            if len(anel) >= 3:
                d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in anel) + "Z")
        return "".join(d)


def ler_shp_zip(p, nome=None, enc="utf-8"):
    import shapefile
    z = zipfile.ZipFile(p)
    base = nome or next(n[:-4] for n in z.namelist() if n.lower().endswith(".shp"))
    return shapefile.Reader(shp=io.BytesIO(z.read(base + ".shp")), dbf=io.BytesIO(z.read(base + ".dbf")), encoding=enc)


def ponto_no_poligono(x, y, shape):
    partes = list(shape.parts) + [len(shape.points)]
    dentro = False
    for a, b in zip(partes, partes[1:]):
        pts = shape.points[a:b]
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                dentro = not dentro
            j = i
    return dentro


# ---------------------------------------------------------------- Censo 2022: municípios e bairros
IDADES = ["0–4", "5–9", "10–14", "15–19", "20–24", "25–29", "30–39", "40–49", "50–59", "60–69", "70+"]
V_M = [f"V010{n:02d}" for n in range(9, 20)]       # homens por faixa
V_F = [f"V010{n:02d}" for n in range(20, 31)]       # mulheres por faixa
V_T = [f"V010{n:02d}" for n in range(31, 42)]       # total por faixa
COR = {"Branca": "V01317", "Preta": "V01318", "Amarela": "V01319", "Parda": "V01320", "Indígena": "V01321"}
ALF = [f"V00{n}" for n in range(748, 761)]         # alfabetizados 15+ por faixa
ESG = {"Rede geral ou pluvial": "V00309", "Fossa séptica ligada à rede": "V00310", "Fossa séptica não ligada": "V00311",
       "Fossa rudimentar": "V00312", "Vala": "V00313", "Rio, lago ou mar": "V00314", "Outra forma": "V00315", "Sem banheiro": "V00316"}
LIXO = {"Coletado": "V00397", "Caçamba": "V00398", "Queimado": "V00399", "Enterrado": "V00400", "Terreno baldio": "V00401", "Outro": "V00402"}


def perfil_censo(rows):
    """Junta as tabelas de um nível (município ou bairro) por código. Devolve {cod: dict}."""
    out = defaultdict(dict)
    for tab, rs in rows.items():
        for r in rs:
            cod = r.get("CD_BAIRRO") or r.get("CD_MUN")
            if not cod or not cod.startswith("13"):
                continue
            o = out[cod]
            o.setdefault("nome", r.get("NM_BAIRRO") or r.get("NM_MUN"))
            if r.get("CD_MUN"):
                o.setdefault("mun", r["CD_MUN"])
            if tab == "basico":
                o.update(pop=B.num(r["v0001"]), dom=B.num(r["v0007"]), mor_dom=B.num(r["v0005"]), area=B.num(r.get("AREA_KM2")))
            elif tab == "demografia":
                o["piramide"] = {"m": [B.num(r.get(v)) for v in V_M], "f": [B.num(r.get(v)) for v in V_F]}
                t = [B.num(r.get(v)) for v in V_T]
                o["faixas"] = t
                o["homens"], o["mulheres"] = B.num(r.get("V01007")), B.num(r.get("V01008"))
            elif tab == "cor":
                o["cor"] = {k: B.num(r.get(v)) for k, v in COR.items()}
            elif tab == "alfab":
                o["alfab"] = soma(r, ALF)
            elif tab == "dom2":
                o["agua_rede"] = B.num(r.get("V00111"))
                o["esgoto"] = {k: B.num(r.get(v)) for k, v in ESG.items()}
                o["lixo"] = {k: B.num(r.get(v)) for k, v in LIXO.items()}
            elif tab == "indig":
                o["indigenas"] = B.num(r.get("V01690"))
            elif tab == "quil":
                o["quilombolas"] = B.num(r.get("V03196"))
            elif tab == "renda":
                o["renda_media"], o["renda_mediana"] = B.num(r.get("V06004")), B.num(r.get("V06006"))
    return out


def derivar(o):
    """Indicadores-resumo de um perfil censitário (município, bairro ou estado)."""
    f = o.get("faixas") or []
    pop = o.get("pop") or (sum(x for x in f if x) if f else None)
    def fx(*i):
        vs = [f[k] for k in i] if f else [None]
        return None if any(v is None for v in vs) else sum(vs)
    p15 = fx(3, 4, 5, 6, 7, 8, 9, 10)
    jovens, idosos = fx(0, 1, 2), fx(9, 10)
    esg, lixo, dom = o.get("esgoto") or {}, o.get("lixo") or {}, sum(v for v in (o.get("esgoto") or {}).values() if v) or None
    d = {
        "pop": pop, "domicilios": o.get("dom"), "moradores_dom": o.get("mor_dom"),
        "densidade": round(pop / o["area"], 1) if pop and o.get("area") else None,
        "razao_sexo": round(o["homens"] / o["mulheres"] * 100, 1) if o.get("homens") and o.get("mulheres") else None,
        "pct_0_14": pct(jovens, pop), "pct_60": pct(idosos, pop),
        "envelhecimento": round(idosos / jovens * 100, 1) if idosos is not None and jovens else None,
        "alfabetizacao": pct(o.get("alfab"), p15),
        "renda_media": o.get("renda_media"), "renda_mediana": o.get("renda_mediana"),
        "pct_indigena": pct(o.get("indigenas"), pop), "pct_quilombola": pct(o.get("quilombolas"), pop),
        "pct_parda": pct((o.get("cor") or {}).get("Parda"), pop), "pct_branca": pct((o.get("cor") or {}).get("Branca"), pop),
        "pct_preta": pct((o.get("cor") or {}).get("Preta"), pop),
        "agua_rede": pct(o.get("agua_rede"), dom),
        "esgoto_rede": pct(esg.get("Rede geral ou pluvial"), dom),
        "esgoto_precario": pct(sum(esg.get(k) or 0 for k in ("Fossa rudimentar", "Vala", "Rio, lago ou mar", "Outra forma", "Sem banheiro")) if esg else None, dom),
        "sem_banheiro": pct(esg.get("Sem banheiro"), dom),
        "lixo_coletado": pct(sum(lixo.get(k) or 0 for k in ("Coletado", "Caçamba")) if lixo else None, dom),
        "lixo_queimado": pct(lixo.get("Queimado"), dom),
    }
    return d


IND_CENSO = [  # (chave em derivar, id, área, nome, unidade, polaridade)
    ("razao_sexo", "razao_sexo", "demografia", "Razão de sexo (homens por 100 mulheres)", "por 100 mulheres", "neutra"),
    ("pct_0_14", "pct_0_14", "demografia", "População de 0 a 14 anos", "%", "neutra"),
    ("pct_60", "pct_60", "demografia", "População de 60 anos ou mais", "%", "neutra"),
    ("envelhecimento", "envelhecimento", "demografia", "Índice de envelhecimento (60+ por 100 de 0–14)", "por 100", "neutra"),
    ("moradores_dom", "moradores_dom", "demografia", "Moradores por domicílio", "pessoas", "neutra"),
    ("domicilios", "domicilios", "demografia", "Domicílios particulares ocupados", "domicílios", "neutra"),
    ("pct_indigena", "pct_indigena", "demografia", "População indígena", "%", "neutra"),
    ("pct_quilombola", "pct_quilombola", "demografia", "População quilombola", "%", "neutra"),
    ("pct_parda", "pct_parda", "demografia", "População de cor parda", "%", "neutra"),
    ("pct_branca", "pct_branca", "demografia", "População de cor branca", "%", "neutra"),
    ("pct_preta", "pct_preta", "demografia", "População de cor preta", "%", "neutra"),
    ("renda_media", "renda_media", "demografia", "Rendimento médio do responsável pelo domicílio", "R$", "maior_melhor"),
    ("renda_mediana", "renda_mediana", "demografia", "Rendimento mediano do responsável pelo domicílio", "R$", "maior_melhor"),
    ("esgoto_rede", "esgoto_rede", "saneamento", "Domicílios com esgoto em rede geral ou pluvial", "%", "maior_melhor"),
    ("esgoto_precario", "esgoto_precario", "saneamento", "Domicílios com esgoto precário (fossa rudimentar, vala, rio, outro ou sem banheiro)", "%", "menor_melhor"),
    ("sem_banheiro", "sem_banheiro", "saneamento", "Domicílios sem banheiro nem sanitário", "%", "menor_melhor"),
    ("lixo_queimado", "lixo_queimado", "saneamento", "Domicílios que queimam o lixo", "%", "menor_melhor"),
]
CALC = {"razao_sexo", "pct_0_14", "pct_60", "envelhecimento", "pct_indigena", "pct_quilombola", "pct_parda", "pct_branca",
        "pct_preta", "esgoto_rede", "esgoto_precario", "sem_banheiro", "lixo_queimado"}


def censo():
    t = time.time()
    url = AGREG + "Agregados_por_Setor_csv/"
    try:
        def tabs(nivel):
            pasta = {"bai": "Agregados_por_Bairro_csv/Agregados_por_bairros_", "mun": "Agregados_por_Municipio_csv/Agregados_por_municipios_"}[nivel]
            pref = {"bai": "bairros", "mun": "municipios"}[nivel]
            arq = {"basico": "basico_BR_20260520", "demografia": "demografia_BR", "cor": "cor_ou_raca_BR", "alfab": "alfabetizacao_BR",
                   "dom2": "caracteristicas_domicilio2_BR_20250417", "indig": "pessoas_indigenas_BR", "quil": "pessoas_quilombolas_BR"}
            r = {k: ler_csv_zip(f"{nivel}_{k}", AGREG + pasta + v + ".zip") for k, v in arq.items()}
            r["renda"] = ler_csv_zip(f"{nivel}_renda", FTP + f"Agregados_por_Setores_Censitarios_Rendimento_do_Responsavel/Agregados_por_{pref}_renda_responsavel_BR_20260508_csv.zip")
            return perfil_censo(r)

        mun = tabs("mun")
        assert len([c for c in mun if c in COD]) == 62, len(mun)
        # estado = soma dos municípios (os agregados não trazem linha da UF)
        est = {"pop": 0, "dom": 0, "homens": 0, "mulheres": 0, "faixas": [0] * 11, "piramide": {"m": [0] * 11, "f": [0] * 11},
               "cor": defaultdict(float), "alfab": 0, "agua_rede": 0, "esgoto": defaultdict(float), "lixo": defaultdict(float),
               "indigenas": 0, "quilombolas": 0, "area": 0}
        for c, o in mun.items():
            for k in ("pop", "dom", "homens", "mulheres", "alfab", "agua_rede", "indigenas", "quilombolas", "area"):
                est[k] += o.get(k) or 0
            for i in range(11):
                est["faixas"][i] += (o.get("faixas") or [0] * 11)[i] or 0
                est["piramide"]["m"][i] += o["piramide"]["m"][i] or 0
                est["piramide"]["f"][i] += o["piramide"]["f"][i] or 0
            for g in ("cor", "esgoto", "lixo"):
                for k, v in (o.get(g) or {}).items():
                    est[g][k] += v or 0
        est["mor_dom"] = round(est["pop"] / est["dom"], 2) if est["dom"] else None
        dm = {c: derivar(o) for c, o in mun.items() if c in COD}
        de = derivar(est)
        fonte_url = "https://www.ibge.gov.br/estatisticas/sociais/trabalho/22827-censo-demografico-2022.html"
        for chave, iid, area, nome, un, pol in IND_CENSO:
            renda = chave.startswith("renda")
            B.indicador(id=iid, area=area, nome=nome, unidade=un, ref="2022", polaridade=pol,
                        fonte="IBGE — Censo 2022, agregados por setores" + (" (rendimento do responsável)" if renda else ""),
                        fonte_url=fonte_url, estado=None if renda else de[chave],
                        municipios={c: d[chave] for c, d in dm.items() if d[chave] is not None},
                        tipo="calculado" if chave in CALC else "oficial",
                        metodo="Calculado a partir das contagens dos agregados por município do Censo 2022; estado = soma dos 62 municípios" if chave in CALC else None,
                        nota="Sem valor estadual nos agregados; o painel mostra a mediana dos municípios." if renda else None)
        TERR["estado"] = {"piramide": est["piramide"], "cor": dict(est["cor"]), "esgoto": dict(est["esgoto"]), "lixo": dict(est["lixo"]), **de}
        TERR["municipios"] = {c: {"piramide": o.get("piramide"), "cor": o.get("cor"), "esgoto": o.get("esgoto"), "lixo": o.get("lixo"), **dm[c]}
                              for c, o in mun.items() if c in COD}
        TERR["idades"] = IDADES

        bai = tabs("bai")
        malha = ler_shp_zip(B.baixar(AGREG + "malha_com_atributos/bairros/shp/UF/AM/AM_bairros_CD2022.zip", "censo/malha_bairros_AM_bairros_CD2022.zip"))
        campos = [f[0] for f in malha.fields[1:]]
        formas = {}
        for sr in malha.iterShapeRecords():
            r = dict(zip(campos, sr.record))
            formas[r["CD_BAIRRO"]] = (r["CD_MUN"], sr.shape)
        # uma moldura SVG por município com bairros
        por_mun = defaultdict(list)
        for cb, (cm, sh) in formas.items():
            por_mun[cm].append((cb, sh))
        for cm, lst in por_mun.items():
            bx = [min(s.bbox[0] for _, s in lst), min(s.bbox[1] for _, s in lst), max(s.bbox[2] for _, s in lst), max(s.bbox[3] for _, s in lst)]
            m = Moldura(bx)
            TERR["molduras"][cm] = {"w": m.w, "h": m.h, "bbox": bx}
            for cb, sh in lst:
                o = bai.get(cb, {})
                TERR["bairros"].append({"cod": cb, "nome": o.get("nome") or cb, "mun": cm, "d": m.path(sh, .6),
                                        "piramide": o.get("piramide"), "cor": o.get("cor"), **derivar(o)})
        TERR["_formas"] = formas  # usado pelo eleitorado (ponto no polígono); removido antes de gravar
        assert len(TERR["bairros"]) >= 400, len(TERR["bairros"])
        B.registrar("IBGE/Censo 2022 — agregados por município e bairro", t, len(mun) + len(TERR["bairros"]), url=AGREG)
    except Exception as e:
        B.registrar("IBGE/Censo 2022 — agregados por município e bairro", t, 0, repr(e)[:200], AGREG)
        raise


def comunidades():
    """Favelas e Comunidades Urbanas (Censo 2022): polígonos + população somada dos setores."""
    t = time.time()
    base = FTP + "Favelas_e_comunidades_urbanas_Resultados_do_universo/"
    try:
        import openpyxl
        setor_fcu = {}
        wb = openpyxl.load_workbook(B.baixar(base + "Anexos/FavelaseComunidadesUrbanas2022Setores_20250417.xlsx", "censo/fcu_setores.xlsx"), read_only=True)
        for r in wb["Setores_FCUs"].iter_rows(min_row=2, values_only=True):
            if str(r[5]) == "13":
                setor_fcu[str(r[0])] = str(r[1])
        pop, dom, bairro_de = defaultdict(float), defaultdict(float), defaultdict(set)
        for r in ler_csv_zip("setor_basico", AGREG + "Agregados_por_Setor_csv/Agregados_por_setores_basico_BR_20260520.zip"):
            f = setor_fcu.get(r["CD_SETOR"].split(".")[0]) if r.get("CD_UF") == "13" else None
            if f:
                pop[f] += B.num(r["v0001"]) or 0
                dom[f] += B.num(r["v0007"]) or 0
                if r.get("CD_BAIRRO"):
                    bairro_de[f].add(r["CD_BAIRRO"])
        shp = ler_shp_zip(B.baixar(base + "arquivos_vetoriais/poligonos_FCUs_shp.zip", "censo/fcu_poligonos.zip"))
        campos = [f[0] for f in shp.fields[1:]]
        mold = {c: Moldura(v["bbox"]) for c, v in TERR["molduras"].items()}
        for sr in shp.iterShapeRecords():
            r = dict(zip(campos, sr.record))
            if r["cd_uf"] != "13":
                continue
            m = mold.get(r["cd_mun"])
            TERR["comunidades"].append({"cod": r["cd_fcu"], "nome": r["nm_fcu"], "mun": r["cd_mun"], "pop": pop.get(r["cd_fcu"]) or None,
                                        "dom": dom.get(r["cd_fcu"]) or None, "bairros": sorted(bairro_de.get(r["cd_fcu"], [])),
                                        "d": m.path(sr.shape, .4) if m else None})
        tot = defaultdict(float)
        for c in TERR["comunidades"]:
            tot[c["mun"]] += c["pop"] or 0
        popm = {c: v["pop"] for c, v in TERR["municipios"].items()}
        B.indicador(id="pop_fcu", area="cidades", nome="População em favelas e comunidades urbanas", unidade="%", ref="2022",
                    polaridade="menor_melhor", tipo="calculado", fonte="IBGE — Censo 2022, Favelas e Comunidades Urbanas",
                    fonte_url=base, metodo="Soma da população dos setores censitários de cada FCU ÷ população do município",
                    estado=pct(sum(tot.values()), sum(popm.values())),
                    municipios={c: pct(tot.get(c, 0), popm[c]) for c in COD if popm.get(c)})
        B.registrar("IBGE/Censo 2022 — Favelas e Comunidades Urbanas", t, len(TERR["comunidades"]), url=base)
    except Exception as e:
        B.registrar("IBGE/Censo 2022 — Favelas e Comunidades Urbanas", t, 0, repr(e)[:200], base)


# ---------------------------------------------------------------- TSE: perfil do eleitorado 2026
TSE = "https://cdn.tse.jus.br/estatistica/sead/odsele/"
FX_TSE = [("16–17", 16, 17), ("18–24", 18, 24), ("25–34", 25, 34), ("35–44", 35, 44), ("45–59", 45, 59), ("60–69", 60, 69), ("70+", 70, 200)]
ESC_TSE = {"ANALFABETO": "Analfabeto", "LÊ E ESCREVE": "Lê e escreve", "ENSINO FUNDAMENTAL INCOMPLETO": "Fundamental incompleto",
           "ENSINO FUNDAMENTAL COMPLETO": "Fundamental completo", "ENSINO MÉDIO INCOMPLETO": "Médio incompleto",
           "ENSINO MÉDIO COMPLETO": "Médio completo", "SUPERIOR INCOMPLETO": "Superior incompleto", "SUPERIOR COMPLETO": "Superior completo"}


def faixa_tse(ds):
    m = re.match(r"(\d+)", ds or "")
    if not m:
        return None
    i = int(m.group(1))
    return next((n for n, a, b in FX_TSE if a <= i <= b), None)


def novo_perfil():
    return {"eleitores": 0, "mulheres": 0, "biometria": 0, "deficiencia": 0, "faixas": defaultdict(int), "escolaridade": defaultdict(int),
            "cor": defaultdict(int), "estado_civil": defaultdict(int)}


def somar_perfil(p, x, q):
    p["eleitores"] += q
    p["mulheres"] += q if x["DS_GENERO"] == "FEMININO" else 0
    p["biometria"] += int(x["QT_ELEITORES_BIOMETRIA"] or 0)
    p["deficiencia"] += int(x["QT_ELEITORES_DEFICIENCIA"] or 0)
    f = faixa_tse(x["DS_FAIXA_ETARIA"])
    if f:
        p["faixas"][f] += q
    p["escolaridade"][ESC_TSE.get(x["DS_GRAU_ESCOLARIDADE"], "Não informado")] += q
    p["cor"][x["DS_RACA_COR"].capitalize() if x["DS_RACA_COR"] != "NÃO INFORMADO" else "Não informado"] += q
    p["estado_civil"][x["DS_ESTADO_CIVIL"].capitalize()] += q


def resumo_perfil(p):
    e = p["eleitores"] or None
    esc = p["escolaridade"]
    cor_inf = sum(v for k, v in p["cor"].items() if k != "Não informado")
    return {"eleitores": p["eleitores"], "pct_mulheres": pct(p["mulheres"], e), "pct_biometria": pct(p["biometria"], e),
            "pct_jovens": pct(p["faixas"]["16–17"] + p["faixas"]["18–24"], e), "pct_idosos": pct(p["faixas"]["60–69"] + p["faixas"]["70+"], e),
            "pct_superior": pct(esc["Superior completo"], e), "pct_sem_fundamental": pct(esc["Analfabeto"] + esc["Lê e escreve"] + esc["Fundamental incompleto"], e),
            "pct_analfabeto": pct(esc["Analfabeto"], e),
            "faixas": [p["faixas"][n] for n, _, _ in FX_TSE], "escolaridade": {k: esc[k] for k in ESC_TSE.values()},
            "cor": dict(p["cor"]), "pct_cor_informada": pct(cor_inf, e), "estado_civil": dict(p["estado_civil"])}


def tse():
    t = time.time()
    url = TSE + "perfil_eleitor_secao/perfil_eleitor_secao_2026_AM.zip"
    try:
        z = zipfile.ZipFile(B.baixar(url, "tse/perfil_eleitor_secao_2026_AM.zip", timeout=1800))
        cod_tse = {}
        por_local, por_mun, est = defaultdict(novo_perfil), defaultdict(novo_perfil), novo_perfil()
        for x in csv.DictReader(io.TextIOWrapper(z.open("perfil_eleitor_secao_2026_AM.csv"), encoding="latin-1"), delimiter=";"):
            cm = cod_tse.setdefault(x["CD_MUNICIPIO"], B.POR_NOME.get(B.norm(x["NM_MUNICIPIO"])))
            q = int(x["QT_ELEITORES"])
            for p in (por_local[(x["CD_MUNICIPIO"], x["NR_ZONA"], x["NR_LOCAL_VOTACAO"])], por_mun[cm], est):
                somar_perfil(p, x, q)
        sem = [k for k, v in cod_tse.items() if not v]
        assert not sem, f"municípios TSE sem código IBGE: {sem}"

        z = zipfile.ZipFile(B.baixar(TSE + "eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip", "tse/eleitorado_local_votacao_2026.zip", timeout=1800))
        locais = {}
        for x in csv.DictReader(io.TextIOWrapper(z.open("eleitorado_local_votacao_2026_AM.csv"), encoding="latin-1"), delimiter=";"):
            if x["NR_TURNO"] != "1":
                continue
            k = (x["CD_MUNICIPIO"], x["NR_ZONA"], x["NR_LOCAL_VOTACAO"])
            if k not in locais:
                locais[k] = {"nome": x["NM_LOCAL_VOTACAO"].strip(), "endereco": x["DS_ENDERECO"].strip(), "bairro_tse": x["NM_BAIRRO"].strip(),
                             "lat": B.num(x["NR_LATITUDE"]), "lon": B.num(x["NR_LONGITUDE"]), "mun": cod_tse.get(x["CD_MUNICIPIO"]),
                             "zona": int(x["NR_ZONA"]), "secoes": 0}
            locais[k]["secoes"] += 1

        # local de votação -> bairro IBGE (ponto no polígono, com pré-filtro por caixa)
        formas = TERR.get("_formas", {})
        por_bairro = defaultdict(novo_perfil)
        nome_bairro = {(b["mun"], B.norm(b["nome"])): b["cod"] for b in TERR["bairros"]}
        ok_geo = 0
        for k, l in locais.items():
            l["bairro"] = None
            if l["lat"] and l["lon"] and -10 < l["lat"] < 3 and -74 < l["lon"] < -56:
                for cb, (cm, sh) in formas.items():
                    if cm == l["mun"] and sh.bbox[0] <= l["lon"] <= sh.bbox[2] and sh.bbox[1] <= l["lat"] <= sh.bbox[3] and ponto_no_poligono(l["lon"], l["lat"], sh):
                        l["bairro"] = cb
                        ok_geo += 1
                        break
            if not l["bairro"]:  # fora dos polígonos (zona rural, coordenada ruim): tenta o nome do bairro do TSE
                l["bairro"] = nome_bairro.get((l["mun"], B.norm(l["bairro_tse"])))
                l["bairro_por_nome"] = bool(l["bairro"])
            if l["bairro"] and k in por_local:
                pl, pb = por_local[k], por_bairro[l["bairro"]]
                for c in ("eleitores", "mulheres", "biometria", "deficiencia"):
                    pb[c] += pl[c]
                for g in ("faixas", "escolaridade", "cor", "estado_civil"):
                    for kk, v in pl[g].items():
                        pb[g][kk] += v

        TERR["eleitorado"] = {
            "fonte": "TSE — Perfil do eleitorado por seção 2026 e eleitorado por local de votação 2026 (1º turno)",
            "url": "https://dadosabertos.tse.jus.br/dataset/eleitorado-2026", "faixas": [n for n, _, _ in FX_TSE],
            "estado": resumo_perfil(est), "municipios": {c: resumo_perfil(p) for c, p in por_mun.items() if c},
            "bairros": {c: resumo_perfil(p) for c, p in por_bairro.items()},
            "geo_ok": ok_geo, "nome_ok": sum(1 for l in locais.values() if l.get("bairro_por_nome")), "locais_total": len(locais),
        }
        CAMADAS["pontos"]["locais_votacao"] = {
            "nome": "Locais de votação (TSE 2026)", "fonte": "TSE — eleitorado por local de votação 2026", "url": TERR["eleitorado"]["url"],
            "itens": [{"nome": l["nome"], "mun": l["mun"], "lat": l["lat"], "lon": l["lon"], "bairro": l["bairro"], "bairro_tse": l["bairro_tse"],
                       "zona": l["zona"], "secoes": l["secoes"], "eleitores": por_local.get(k, {}).get("eleitores")}
                      for k, l in locais.items() if l["lat"] and l["lon"]]}
        r = TERR["eleitorado"]["municipios"]
        popu = {c: B.POP[(c, max(y for (cc, y) in B.POP if cc == c))] for c in COD} if B.POP else {}
        defs = [("eleitores", "eleitores", "Eleitores aptos (2026)", "eleitores", "neutra", None),
                ("pct_mulheres", "eleit_mulheres", "Eleitorado feminino", "%", "neutra", None),
                ("pct_jovens", "eleit_jovens", "Eleitores de 16 a 24 anos", "%", "neutra", None),
                ("pct_idosos", "eleit_idosos", "Eleitores de 60 anos ou mais", "%", "neutra", None),
                ("pct_superior", "eleit_superior", "Eleitores com ensino superior completo", "%", "maior_melhor", None),
                ("pct_sem_fundamental", "eleit_sem_fund", "Eleitores sem ensino fundamental completo", "%", "menor_melhor", None),
                ("pct_biometria", "eleit_biometria", "Eleitores com biometria", "%", "maior_melhor", None)]
        for ch, iid, nome, un, pol, _ in defs:
            B.indicador(id=iid, area="eleitorado", nome=nome, unidade=un, ref="2026", polaridade=pol,
                        fonte="TSE — Perfil do eleitorado por seção 2026", fonte_url=TERR["eleitorado"]["url"],
                        tipo="oficial" if ch == "eleitores" else "calculado",
                        metodo=None if ch == "eleitores" else "Soma das seções do município por categoria ÷ total de eleitores",
                        estado=TERR["eleitorado"]["estado"][ch], municipios={c: v[ch] for c, v in r.items() if v[ch] is not None})
        B.indicador(id="eleit_pop", area="eleitorado", nome="Eleitores por 100 habitantes", unidade="por 100 hab.", ref="2026",
                    polaridade="neutra", tipo="calculado", fonte="TSE e IBGE", fonte_url=TERR["eleitorado"]["url"],
                    metodo="Eleitores aptos 2026 (TSE) ÷ população estimada mais recente (IBGE) × 100. Acima de 100 indica domicílio eleitoral diferente da residência.",
                    estado=pct(est["eleitores"], B.POP.get(("13", max(y for (c, y) in B.POP if c == "13")))) if B.POP else None,
                    municipios={c: pct(r[c]["eleitores"], popu.get(c)) for c in r if popu.get(c)})
        B.registrar("TSE — perfil do eleitorado 2026", t, est["eleitores"], url=url)
        print(f"      locais de votação no bairro IBGE: {ok_geo} de {len(locais)}")
    except Exception as e:
        B.registrar("TSE — perfil do eleitorado 2026", t, 0, repr(e)[:200], url)


EXTRAS.append(tse)


# ---------------------------------------------------------------- equipamentos públicos: saúde, educação, segurança
def baixar_tls(url, destino, timeout=1800):
    """Como B.baixar, mas aceita servidores com TLS antigo (download.inep.gov.br)."""
    import ssl, urllib.request
    p = BRONZE / destino
    if p.exists() and p.stat().st_size and not B.ATUALIZAR:
        return p
    p.parent.mkdir(parents=True, exist_ok=True)
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=timeout, context=ctx) as r:
        p.write_bytes(r.read())
    return p


def por_hab(cont, mil=10):
    """{cod: contagem} -> {cod: por N mil hab.} com a população estimada mais recente."""
    if not B.POP:
        return {}
    out = {}
    for c in COD:
        anos = [y for (cc, y) in B.POP if cc == c]
        p = B.POP.get((c, max(anos))) if anos else None
        if p:
            out[c] = round((cont.get(c) or 0) / p * mil * 1000, 2)
    return out


def pop_estado():
    return B.POP.get(("13", max(y for (c, y) in B.POP if c == "13"))) if B.POP else None


TIPO_CNES = {1: "UBS", 2: "UBS", 32: "UBS", 71: "UBS", 5: "Hospital", 7: "Hospital", 62: "Hospital", 15: "Hospital",
             73: "Pronto atendimento", 20: "Pronto atendimento", 21: "Pronto atendimento", 70: "CAPS", 4: "Policlínica e especialidades",
             36: "Policlínica e especialidades", 39: "Apoio diagnóstico", 43: "Farmácia", 22: "Consultório"}


def saude_equip():
    t = time.time()
    url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
    try:
        todos = json.loads((BRONZE / "cnes" / "estabelecimentos_am.json").read_text(encoding="utf-8"))
        cod6 = {c[:6]: c for c in COD}
        itens = []
        for e in todos:
            c = cod6.get(str(e.get("codigo_municipio"))[:6])
            lat, lon = e.get("latitude_estabelecimento_decimo_grau"), e.get("longitude_estabelecimento_decimo_grau")
            itens.append({"nome": (e.get("nome_fantasia") or e.get("nome_razao_social") or "").strip(), "mun": c,
                          "tipo": TIPO_CNES.get(e.get("codigo_tipo_unidade"), "Outros"), "esfera": (e.get("descricao_esfera_administrativa") or "").title() or None,
                          "sus": e.get("estabelecimento_faz_atendimento_ambulatorial_sus") == "SIM", "hospitalar": bool(e.get("estabelecimento_possui_atendimento_hospitalar")),
                          "bairro": (e.get("bairro_estabelecimento") or "").title(), "cnes": e.get("codigo_cnes"),
                          "lat": lat if lat and -10 < lat < 3 else None, "lon": lon if lon and -74 < lon < -56 else None})
        CAMADAS["pontos"]["saude"] = {"nome": "Estabelecimentos de saúde (CNES)", "fonte": "Ministério da Saúde — CNES", "url": url,
                                     "itens": [i for i in itens if i["lat"]]}
        for tipo, iid, nome in [("UBS", "ubs", "Unidades básicas de saúde"), ("Hospital", "hospitais", "Hospitais"),
                                ("Pronto atendimento", "pronto_atend", "Unidades de pronto atendimento e pronto-socorro")]:
            cont = defaultdict(int)
            for i in itens:
                if i["tipo"] == tipo and i["mun"]:
                    cont[i["mun"]] += 1
            B.indicador(id=iid, area="saude", nome=nome, unidade="unidades", ref=B.AGORA[:7], fonte="Ministério da Saúde — CNES, API de dados abertos",
                        fonte_url=url, estado=sum(cont.values()), municipios={c: cont.get(c, 0) for c in COD}, tipo="calculado",
                        metodo="Contagem de estabelecimentos CNES pelo tipo de unidade (" + ", ".join(str(k) for k, v in TIPO_CNES.items() if v == tipo) + ")")
        B.registrar("DATASUS/CNES — equipamentos georreferenciados", t, len(CAMADAS["pontos"]["saude"]["itens"]), url=url)
    except Exception as e:
        B.registrar("DATASUS/CNES — equipamentos georreferenciados", t, 0, repr(e)[:200], url)

    t = time.time()
    url = "https://opendatasus.saude.gov.br/dataset/hospitais-e-leitos"
    try:
        # CSV anual do OpenDataSUS: traz competência (COMP) e código CNES. A API JSON equivalente
        # não tem competência e repete hospitais renomeados, inflando o total.
        am = []
        for ano in range(int(B.AGORA[:4]), int(B.AGORA[:4]) - 3, -1):
            try:
                pc = B.baixar(f"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/Leitos_SUS/Leitos_{ano}.csv", f"cnes/leitos_csv/Leitos_{ano}.csv")
            except Exception:
                continue
            am = [x for x in csv.DictReader(io.StringIO(pc.read_bytes().decode("latin-1"))) if x.get("UF") == "AM"]
            if am:
                break
        assert am, "nenhum arquivo Leitos_AAAA.csv disponível"
        comp = max(x["COMP"] for x in am)
        am = [x for x in am if x["COMP"] == comp]
        ref = f"{comp[:4]}-{comp[4:6]}"
        campos = {"leitos": "LEITOS_EXISTENTES", "leitos_sus": "LEITOS_SUS", "uti": "UTI_TOTAL_EXIST", "uti_sus": "UTI_TOTAL_SUS"}
        num = lambda v: float(v or 0)
        tot = {k: defaultdict(float) for k in campos}
        coords = {str(i.get("cnes") or "").lstrip("0"): i for i in CAMADAS["pontos"].get("saude", {}).get("itens", [])}
        hosp = []
        for h in am:
            c = B.POR_NOME.get(B.norm(h.get("MUNICIPIO") or ""))
            if not c:
                continue
            for k, f in campos.items():
                tot[k][c] += num(h.get(f))
            g = coords.get((h.get("CNES") or "").lstrip("0"), {})
            hosp.append({"nome": (h.get("NOME_ESTABELECIMENTO") or "(sem nome)").title(), "mun": c, "cnes": h.get("CNES"),
                         "tipo": (h.get("DS_TIPO_UNIDADE") or "").replace("_", " ").title(), "natureza": (h.get("DESC_NATUREZA_JURIDICA") or "").replace("_", " ").title(),
                         **{k: num(h.get(f)) for k, f in campos.items()}, "lat": g.get("lat"), "lon": g.get("lon")})
        assert len(hosp) > 0.9 * len(am), f"municípios não reconhecidos: {len(am) - len(hosp)} hospitais"
        CAMADAS["pontos"]["hospitais"] = {"nome": "Hospitais e leitos", "fonte": "Ministério da Saúde — Hospitais e leitos (CNES/OpenDataSUS)", "url": url,
                                         "itens": [h for h in hosp if h["lat"]], "sem_coordenada": [h for h in hosp if not h["lat"]]}
        pe = pop_estado()
        for k, iid, nome, un in [("leitos", "leitos_total", "Leitos hospitalares", "leitos"), ("leitos_sus", "leitos_sus_hab", "Leitos SUS por mil hab.", "por mil hab."),
                                 ("uti", "leitos_uti", "Leitos de UTI", "leitos"), ("uti_sus", "uti_sus_hab", "Leitos de UTI SUS por 100 mil hab.", "por 100 mil hab.")]:
            hab = un.startswith("por")
            mil = 1 if "mil hab" in un and "100" not in un else 100
            B.indicador(id=iid, area="saude", nome=nome, unidade=un, ref=ref, fonte="Ministério da Saúde — Hospitais e leitos (CNES/OpenDataSUS)", fonte_url=url,
                        nota=f"Competência {comp[4:6]}/{comp[:4]}, última publicada no arquivo anual.",
                        tipo="calculado" if hab else "oficial", metodo=f"Soma dos leitos dos hospitais do município ÷ população estimada × {mil} mil" if hab else "Soma dos hospitais do município",
                        estado=round(sum(tot[k].values()) / pe * mil * 1000, 2) if hab and pe else sum(tot[k].values()),
                        municipios=por_hab(tot[k], mil) if hab else {c: tot[k].get(c, 0) for c in COD})
        B.registrar("DATASUS — hospitais e leitos", t, len(hosp), url=url)
    except Exception as e:
        B.registrar("DATASUS — hospitais e leitos", t, 0, repr(e)[:200], url)


DEP = {"1": "Federal", "2": "Estadual", "3": "Municipal", "4": "Privada"}


def educacao_equip():
    t = time.time()
    url = "https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2024.zip"
    try:
        z = zipfile.ZipFile(baixar_tls(url, "inep/censo_escolar_2024.zip"))
        n = next(x for x in z.namelist() if x.endswith("microdados_ed_basica_2024.csv"))
        esc = []
        for r in csv.DictReader(io.TextIOWrapper(z.open(n), encoding="latin-1"), delimiter=";"):
            if r["CO_MUNICIPIO"][:2] != "13" or r["TP_SITUACAO_FUNCIONAMENTO"] != "1":
                continue
            q = lambda k: int(r[k]) if r.get(k) not in (None, "") else 0  # noqa: E731
            esc.append({"cod": r["CO_ENTIDADE"], "nome": r["NO_ENTIDADE"].title(), "mun": r["CO_MUNICIPIO"], "rede": DEP.get(r["TP_DEPENDENCIA"]),
                        "rural": r["TP_LOCALIZACAO"] == "2", "indigena": r["IN_EDUCACAO_INDIGENA"] == "1", "bairro": (r["NO_BAIRRO"] or "").title(),
                        "mat": q("QT_MAT_BAS"), "mat_inf": q("QT_MAT_INF"), "mat_fund": q("QT_MAT_FUND"), "mat_med": q("QT_MAT_MED"),
                        "mat_eja": q("QT_MAT_EJA"), "mat_prof": q("QT_MAT_PROF"), "doc": q("QT_DOC_BAS"),
                        "internet": r["IN_INTERNET"] == "1", "agua": r["IN_AGUA_POTAVEL"] == "1", "sem_energia": r["IN_ENERGIA_INEXISTENTE"] == "1",
                        "biblioteca": r["IN_BIBLIOTECA"] == "1", "lab_info": r["IN_LABORATORIO_INFORMATICA"] == "1", "quadra": r["IN_QUADRA_ESPORTES"] == "1"})
        TERR["escolas"] = esc  # sem coordenadas no microdado: lista por município e bairro (texto do INEP)
        fonte = "INEP — Censo Escolar 2024 (microdados)"
        def ind(iid, nome, un, f, pol="neutra", calc=False, metodo=None):
            por = defaultdict(list)
            for e in esc:
                por[e["mun"]].append(e)
            B.indicador(id=iid, area="educacao", nome=nome, unidade=un, ref="2024", fonte=fonte, fonte_url=url, polaridade=pol,
                        tipo="calculado" if calc else "oficial", metodo=metodo, estado=f(esc), municipios={c: f(por.get(c, [])) for c in COD})
        ind("escolas", "Escolas em funcionamento", "escolas", len)
        ind("escolas_estaduais", "Escolas da rede estadual", "escolas", lambda l: sum(e["rede"] == "Estadual" for e in l))
        ind("escolas_rurais", "Escolas em área rural", "%", lambda l: pct(sum(e["rural"] for e in l), len(l)), calc=True)
        ind("matriculas", "Matrículas na educação básica", "alunos", lambda l: sum(e["mat"] for e in l))
        ind("mat_estadual", "Matrículas na rede estadual", "alunos", lambda l: sum(e["mat"] for e in l if e["rede"] == "Estadual"))
        ind("mat_medio", "Matrículas no ensino médio", "alunos", lambda l: sum(e["mat_med"] for e in l))
        ind("mat_eja", "Matrículas na EJA", "alunos", lambda l: sum(e["mat_eja"] for e in l))
        ind("alunos_docente", "Alunos por docente (educação básica)", "alunos", lambda l: round(sum(e["mat"] for e in l) / s, 1) if (s := sum(e["doc"] for e in l)) else None,
            "menor_melhor", True, "Matrículas ÷ docentes. Docente que leciona em mais de uma escola conta em cada uma.")
        ind("escolas_internet", "Escolas públicas com internet", "%", lambda l: pct(sum(e["internet"] for e in l if e["rede"] != "Privada"), sum(e["rede"] != "Privada" for e in l)), "maior_melhor", True)
        ind("escolas_agua", "Escolas públicas com água potável", "%", lambda l: pct(sum(e["agua"] for e in l if e["rede"] != "Privada"), sum(e["rede"] != "Privada" for e in l)), "maior_melhor", True)
        ind("escolas_biblioteca", "Escolas públicas com biblioteca", "%", lambda l: pct(sum(e["biblioteca"] for e in l if e["rede"] != "Privada"), sum(e["rede"] != "Privada" for e in l)), "maior_melhor", True)
        B.registrar("INEP — Censo Escolar 2024", t, len(esc), url=url)
    except Exception as e:
        B.registrar("INEP — Censo Escolar 2024", t, 0, repr(e)[:200], url)

    # coordenadas: o microdado não traz; o Catálogo de Escolas do INEP traz, e o geobr (IPEA) o publica em GeoPackage
    t = time.time()
    url = "https://www.ipea.gov.br/geobr/data_gpkg/schools/2023/schools_2023.gpkg"
    try:
        import sqlite3
        import struct
        con = sqlite3.connect(B.baixar(url, "inep/escolas_geobr_2023.gpkg", timeout=900))
        def ponto(b):  # GeoPackage binary: cabeçalho de 8 bytes + envelope + WKB
            env = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}[(b[3] >> 1) & 7]
            w = b[8 + env:]
            return struct.unpack(("<" if w[0] == 1 else ">") + "dd", w[5:21])
        geo = {}
        for cod, g, vazio in con.execute("select code_school, geom, empty_geo from schools_2023 where abbrev_state = 'AM'"):
            if g and not vazio:
                x, y = ponto(g)
                if x == x and y == y:  # NaN = sem coordenada
                    geo[str(cod)] = (x, y)
        con.close()
        itens = [{"nome": e["nome"], "rede": e["rede"], "zona": "Rural" if e["rural"] else "Urbana", "matriculas": e["mat"], "mun": e["mun"],
                  "lon": geo[e["cod"]][0], "lat": geo[e["cod"]][1]} for e in TERR.get("escolas", []) if e["cod"] in geo]
        assert itens, "nenhuma escola casou com o catálogo"
        CAMADAS["pontos"]["escolas"] = {"nome": "Escolas em funcionamento", "url": url,
                                        "fonte": "INEP — Censo Escolar 2024; coordenadas do Catálogo de Escolas (geobr/IPEA, 2023)",
                                        "cobertura": f"{len(itens)} de {len(TERR['escolas'])} escolas com coordenada"}
        CAMADAS["pontos"]["escolas"]["itens"] = itens
        B.registrar("IPEA/geobr — coordenadas das escolas (Catálogo INEP 2023)", t, len(itens), url=url)
    except Exception as e:
        B.registrar("IPEA/geobr — coordenadas das escolas (Catálogo INEP 2023)", t, 0, repr(e)[:200], url)

    t = time.time()
    url = "https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_2023.zip"
    try:
        z = zipfile.ZipFile(baixar_tls(url, "inep/censo_superior_2023.zip"))
        ler = lambda suf: csv.DictReader(io.TextIOWrapper(z.open(next(x for x in z.namelist() if x.endswith(suf))), encoding="latin-1"), delimiter=";")  # noqa: E731
        ies = {r["CO_IES"]: r for r in ler("ED_SUP_IES_2023.CSV")}
        CAT = {"1": "Federal", "2": "Estadual", "3": "Municipal"}
        mat, cursos, por_ies = defaultdict(int), defaultdict(int), defaultdict(lambda: {"mat": 0, "cursos": 0, "municipios": set()})
        for r in ler("CADASTRO_CURSOS_2023.CSV"):
            if r["CO_UF"] != "13" or not r["CO_MUNICIPIO"]:
                continue  # cursos EAD não têm município
            m = int(r["QT_MAT"] or 0)
            mat[r["CO_MUNICIPIO"]] += m
            cursos[r["CO_MUNICIPIO"]] += 1
            p = por_ies[r["CO_IES"]]
            p["mat"] += m
            p["cursos"] += 1
            p["municipios"].add(r["CO_MUNICIPIO"])
        TERR["ies"] = sorted([{"nome": ies.get(k, {}).get("NO_IES", k).title(), "sigla": ies.get(k, {}).get("SG_IES"),
                               "rede": CAT.get(ies.get(k, {}).get("TP_CATEGORIA_ADMINISTRATIVA"), "Privada"),
                               "mat": v["mat"], "cursos": v["cursos"], "municipios": sorted(v["municipios"])} for k, v in por_ies.items()],
                             key=lambda x: -x["mat"])
        fonte = "INEP — Censo da Educação Superior 2023 (cursos presenciais)"
        B.indicador(id="mat_superior", area="educacao", nome="Matrículas em cursos superiores presenciais", unidade="alunos", ref="2023",
                    fonte=fonte, fonte_url=url, estado=sum(mat.values()), municipios={c: mat.get(c, 0) for c in COD})
        B.indicador(id="cursos_superior", area="educacao", nome="Cursos superiores presenciais", unidade="cursos", ref="2023",
                    fonte=fonte, fonte_url=url, estado=sum(cursos.values()), municipios={c: cursos.get(c, 0) for c in COD})
        B.registrar("INEP — Censo da Educação Superior 2023", t, len(TERR["ies"]), url=url)
    except Exception as e:
        B.registrar("INEP — Censo da Educação Superior 2023", t, 0, repr(e)[:200], url)


SSP_GEO = "https://services3.arcgis.com/5yrshRp0yzXAppIi/arcgis/rest/services/"  # ArcGIS Online da SSP-AM (mapa em ssp.am.gov.br/ssp-dados)


def seguranca_equip():
    """Unidades policiais e de bombeiros: base oficial da SSP-AM; se falhar, OpenStreetMap."""
    import urllib.parse
    t = time.time()
    try:
        def camada(servico, filtro, arq):
            q = urllib.parse.urlencode(dict(where=filtro, outFields="*", outSR=4326, f="geojson", resultRecordCount=2000))
            return B.json_url(f"{SSP_GEO}{urllib.parse.quote(servico)}/FeatureServer/0/query?{q}", f"ssp_am/{arq}.json")["features"]
        cap = camada("publicação_de_várias_camadas", "TIPO IN ('POLÍCIA CIVIL','POLÍCIA MILITAR','BOMBEIRO MILITAR')", "unidades_capital")
        inte = camada("Sede_unidades_policiais_gdb", "1=1", "sedes_interior")
        rot = {"POLÍCIA CIVIL": "Polícia Civil", "POLÍCIA MILITAR": "Polícia Militar", "BOMBEIRO MILITAR": "Bombeiros"}
        itens = [{"nome": p["NOME_PONTO"].title(), "tipo": rot[p["TIPO"]], "unidade": (p["SUBTIPO"] or "").capitalize(), "bairro": (p["BAIRRO"] or "").title(),
                  "dip": p.get("DIP"), "mun": "1302603", "lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
                 for f in cap if f.get("geometry") and (p := f["properties"])]
        itens += [{"nome": p["Unidade_PMAM"] or p["Name"], "tipo": "Polícia Militar", "unidade": "Sede no interior", "local": p["Name"],
                   "efetivo": p.get("Efetivo"), "lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
                  for f in inte if f.get("geometry") and (p := f["properties"])]
        assert len(itens) > 100, len(itens)
        CAMADAS["pontos"]["seguranca"] = {"nome": "Unidades policiais e de bombeiros (SSP-AM)", "url": "https://www.ssp.am.gov.br/ssp-dados/",
                                         "fonte": "SSP-AM — mapa da segurança pública (Manaus: DIPs, especializadas, PM e bombeiros; interior: sedes da PM)",
                                         "itens": itens}
        B.registrar("SSP-AM — unidades policiais (ArcGIS)", t, len(itens), url=SSP_GEO)
        return
    except Exception as e:
        B.registrar("SSP-AM — unidades policiais (ArcGIS)", t, 0, repr(e)[:200], SSP_GEO)
    osm_seguranca()


ANUARIO = "https://office365prodam-my.sharepoint.com/:x:/g/personal/gerencia_estatistica_ssp_am_gov_br/IQBuVNcRpsAOQYVGA2xjlGs5AdRZIPtrZCgt-qk9T_FF56s?e=XAeNsV"


def ssp_anuario():
    """Anuário do Amazonas de Segurança Pública (SSP-AM/CIESP): tabelas em xlsx num link público do SharePoint."""
    import http.cookiejar
    import openpyxl
    import urllib.request
    t = time.time()
    try:
        arq = B.BRONZE / "ssp_am" / "anuario_tabelas_2026.xlsx"
        if not arq.exists() or B.ATUALIZAR:
            # o link de compartilhamento só libera o download depois de gravar o cookie da primeira visita
            op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
            op.addheaders = [("User-Agent", "Mozilla/5.0 (observatorio-amazonas)")]
            op.open(ANUARIO, timeout=60).read()
            b = op.open(ANUARIO + "&download=1", timeout=180).read()
            assert b[:2] == b"PK", "o link não devolveu um xlsx"
            arq.parent.mkdir(parents=True, exist_ok=True)
            arq.write_bytes(b)
        wb = openpyxl.load_workbook(arq, read_only=True, data_only=True)
        def linhas(aba):
            return [[c for c in r if c not in (None, "")] for r in wb[aba].iter_rows(values_only=True)]
        anos = lambda aba, n: [r for r in linhas(aba) if len(r) >= n and isinstance(r[0], int) and 1990 < r[0] < 2100]  # noqa: E731
        t3 = anos("Tabela 03", 5)  # ano, vítimas AM, variação, população, taxa (e o mesmo para Manaus)
        t2 = anos("Tabela 02", 6)  # ano, PM, PC, bombeiros, PM+PC, policiais por mil hab.
        mun, cab = {}, None
        for r in linhas("Tabela 04"):
            if r and str(r[0]).upper().startswith("MUNIC"):
                cab = r
            elif cab and r and isinstance(r[0], str) and (c := B.POR_NOME.get({"NAHMUNDA": "NHAMUNDA"}.get(B.norm(r[0]), B.norm(r[0])))):  # erro de grafia na planilha
                mun[c] = dict(zip(cab[1:], r[1:]))
        assert len(mun) == 62 and len(t3) > 20 and t2, (len(mun), len(t3), len(t2))
        ult = max(k for k in cab[1:] if isinstance(k, int))
        mil = lambda n: f"{n:,}".replace(",", ".")  # noqa: E731
        fonte = "SSP-AM — Anuário do Amazonas de Segurança Pública 2026 (CIESP)"
        url = "https://anuarioamsegpub-geoseguranca.hub.arcgis.com/"
        B.indicador(id="ssp_homicidios", area="seguranca", nome="Homicídio doloso — vítimas (SSP-AM)", unidade="vítimas", ref=str(ult),
                    fonte=fonte, fonte_url=url, polaridade="menor_melhor", estado=t3[-1][1],
                    municipios={c: mun[c].get(ult) for c in COD}, serie=[[r[0], r[1]] for r in t3],
                    nota="Contagem oficial do estado, por vítima (boletins, laudos, revisão PC-AM). Confere com o SINESP: 1.321 × 1.320 em 2022 e 1.254 × 1.246 em 2023.")
        B.indicador(id="ssp_homicidio_taxa", area="seguranca", nome="Homicídio doloso por 100 mil habitantes (SSP-AM)", unidade="por 100 mil hab.",
                    ref=str(ult), fonte=fonte, fonte_url=url, polaridade="menor_melhor", estado=round(t3[-1][4], 1),
                    serie=[[r[0], round(r[4], 1)] for r in t3], tipo="calculado",
                    municipios=por_hab({c: mun[c].get(ult) or 0 for c in COD}, 100),
                    metodo="Estado: taxa publicada pela SSP-AM. Municípios: vítimas ÷ população estimada IBGE mais recente × 100.000.",
                    nota="Em municípios pequenos, um ou dois casos mudam muito a taxa.")
        B.indicador(id="efetivo_policial", area="seguranca", nome="Efetivo de policiais civis e militares", unidade="policiais", ref=str(t2[-1][0]),
                    fonte=fonte, fonte_url=url, estado=t2[-1][4], serie=[[r[0], r[4]] for r in t2], nivel_municipal=False,
                    nota=f"PM {mil(t2[-1][1])} e PC {mil(t2[-1][2])} em {t2[-1][0]}, mais {mil(t2[-1][3])} bombeiros militares; "
                         + f"{t2[-1][5]:.2f}".replace(".", ",") + " policiais por mil habitantes.")
        B.registrar("SSP-AM — Anuário de Segurança Pública (tabelas)", t, len(mun) + len(t3) + len(t2), url=url)
    except Exception as e:
        B.registrar("SSP-AM — Anuário de Segurança Pública (tabelas)", t, 0, repr(e)[:200], ANUARIO)


def osm_seguranca():
    """Unidades policiais e bombeiros no OpenStreetMap (base colaborativa, cobertura incompleta)."""
    import urllib.parse, urllib.request
    t = time.time()
    url = "https://maps.mail.ru/osm/tools/overpass/api/interpreter"
    cache = BRONZE / "osm" / "seguranca_am.json"
    try:
        if cache.exists() and not B.ATUALIZAR:
            d = json.loads(cache.read_text(encoding="utf-8"))
        else:
            q = '[out:json][timeout:120];area["ISO3166-2"="BR-AM"]->.a;(nwr["amenity"~"^(police|fire_station)$"](area.a););out center tags;'
            with urllib.request.urlopen(urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(),
                                                               headers={"User-Agent": "observatorio-amazonas/1.0"}), timeout=180) as r:
                d = json.load(r)
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        itens = []
        for e in d["elements"]:
            lat, lon = e.get("lat") or e.get("center", {}).get("lat"), e.get("lon") or e.get("center", {}).get("lon")
            tg = e.get("tags", {})
            itens.append({"nome": tg.get("name") or ("Unidade policial" if tg.get("amenity") == "police" else "Bombeiros"),
                          "tipo": "Bombeiros" if tg.get("amenity") == "fire_station" else "Polícia", "lat": lat, "lon": lon,
                          "operador": tg.get("operator")})
        CAMADAS["pontos"]["seguranca"] = {"nome": "Delegacias, quartéis e bombeiros (OpenStreetMap)", "fonte": "OpenStreetMap (colaborativo; cobertura incompleta)",
                                         "url": "https://www.openstreetmap.org", "itens": itens}
        B.registrar("OpenStreetMap — unidades de segurança", t, len(itens), url=url)
    except Exception as e:
        B.registrar("OpenStreetMap — unidades de segurança", t, 0, repr(e)[:200], url)


EXTRAS += [saude_equip, educacao_equip, seguranca_equip, ssp_anuario]


# ---------------------------------------------------------------- economia (SIDRA) e produção rural
def sidra_produtos(tabela, var, classif, periodo="last"):
    """{cod: {produto: valor}} e ano, para tabelas com classificação de produto (c.../all)."""
    url = f"https://apisidra.ibge.gov.br/values/t/{tabela}/n6/in%20n3%2013/v/{var}/p/{periodo}/c{classif}/allxt"
    linhas = B.json_url(url, f"sidra/{tabela}_{var}_{periodo}_c{classif}_all.json")[1:]
    out, ano = defaultdict(dict), None
    for l in linhas:
        v = B.num(l["V"])
        prod = next(l[k] for k in ("D4N", "D5N") if k in l)
        ano = next(l[k] for k in ("D3C", "D2C") if re.fullmatch(r"\d{4}", str(l.get(k, ""))))
        if v:
            out[l["D1C"]][re.sub(r"^[\d.]+ - ", "", prod).rstrip("*")] = v
    return out, ano


def economia():
    t = time.time()
    url = "https://apisidra.ibge.gov.br"
    try:
        # estrutura do valor adicionado por município (mesmas consultas do P04, em cache)
        va = {k: B.sidra(5938, v, "all") for k, v in {"agro": 513, "ind": 517, "serv": 6575, "adm": 525}.items()}
        a = max(y for (c, y), v in va["serv"].items() if c in COD and v is not None)
        tot = {c: sum(va[k].get((c, a)) or 0 for k in va) for c in COD}
        for k, iid, nome in [("agro", "va_agro", "Participação da agropecuária no valor adicionado"), ("ind", "va_ind", "Participação da indústria no valor adicionado"),
                             ("serv", "va_serv", "Participação dos serviços no valor adicionado"), ("adm", "va_adm", "Participação da administração pública no valor adicionado")]:
            B.indicador(id=iid, area="economia", nome=nome, unidade="%", ref=str(a), polaridade="neutra", tipo="calculado",
                        fonte="IBGE — PIB dos Municípios (SIDRA 5938)", fonte_url="https://sidra.ibge.gov.br/tabela/5938",
                        metodo="Valor adicionado do setor ÷ soma dos quatro setores (agropecuária, indústria, serviços, administração pública)",
                        estado=pct(sum(va[k].get((c, a)) or 0 for c in COD), sum(tot.values())),
                        municipios={c: pct(va[k].get((c, a)), tot[c]) for c in COD if tot[c]})
        # CEMPRE: empresas, emprego formal e salários
        cem = {k: B.sidra(6449, v, "last", "/c12762/117897") for k, v in {"emp": 2585, "po": 707, "assal": 708, "sal": 662}.items()}
        a = B.ultimo_ano(cem["emp"])
        g = lambda k, c: cem[k].get((c, a))  # noqa: E731
        f6449 = dict(fonte="IBGE — Cadastro Central de Empresas (SIDRA 6449)", fonte_url="https://sidra.ibge.gov.br/tabela/6449", ref=str(a))
        B.indicador(id="empresas", area="economia", nome="Empresas e outras organizações", unidade="unidades", estado=g("emp", "13"),
                    municipios={c: g("emp", c) for c in COD if g("emp", c) is not None}, polaridade="maior_melhor", **f6449)
        B.indicador(id="pessoal_ocupado", area="economia", nome="Pessoal ocupado em empresas formais", unidade="pessoas", estado=g("po", "13"),
                    municipios={c: g("po", c) for c in COD if g("po", c) is not None}, **f6449)
        sm = lambda c: round(g("sal", c) * 1000 / g("assal", c) / 13, 2) if g("sal", c) and g("assal", c) else None  # noqa: E731
        B.indicador(id="salario_medio", area="economia", nome="Salário médio mensal do assalariado formal", unidade="R$", estado=sm("13"),
                    municipios={c: sm(c) for c in COD if sm(c)}, tipo="calculado", metodo="Salários e outras remunerações × 1000 ÷ assalariados ÷ 13 (inclui 13º)", **f6449)
        B.indicador(id="ocupados_hab", area="economia", nome="Pessoal ocupado formal por 100 habitantes", unidade="por 100 hab.", tipo="calculado",
                    metodo="Pessoal ocupado (CEMPRE) ÷ população estimada × 100", estado=pct(g("po", "13"), pop_estado()),
                    municipios=por_hab({c: g("po", c) for c in COD}, .1), **f6449)
        B.registrar("IBGE/SIDRA — economia municipal (PIB setorial, CEMPRE)", t, len(COD), url=url)
    except Exception as e:
        B.registrar("IBGE/SIDRA — economia municipal (PIB setorial, CEMPRE)", t, 0, repr(e)[:200], url)

    t = time.time()
    try:
        rural = defaultdict(dict)
        def prod_ind(iid, nome, un, tab, var, cl, fonte, cat_total="0"):
            d, ano = sidra_produtos(tab, var, cl)
            tot = {c: (v.get("Total") if cat_total == "0" else None) or sum(x for k, x in v.items() if k != "Total") for c, v in d.items()}
            B.indicador(id=iid, area="rural", nome=nome, unidade=un, ref=ano, fonte=fonte, fonte_url=f"https://sidra.ibge.gov.br/tabela/{tab}",
                        estado=sum(v for c, v in tot.items() if c in COD), municipios={c: tot.get(c, 0) for c in COD},
                        nota="Estado = soma dos municípios.")
            for c, v in d.items():
                rural[c][iid] = sorted(((k, x) for k, x in v.items() if k != "Total"), key=lambda z: -z[1])[:8]
            return d
        prod_ind("pam_valor", "Valor da produção agrícola (lavouras)", "R$ mil", 5457, 215, 782, "IBGE — Produção Agrícola Municipal (SIDRA 5457)")
        prod_ind("pevs_valor", "Valor da produção do extrativismo vegetal", "R$ mil", 289, 145, 193, "IBGE — Produção da Extração Vegetal e Silvicultura (SIDRA 289)")
        prod_ind("aqui_valor", "Valor da produção da aquicultura", "R$ mil", 3940, 215, 654, "IBGE — Pesquisa da Pecuária Municipal (SIDRA 3940)")
        prod_ind("animal_valor", "Valor da produção de origem animal (leite, ovos, mel)", "R$ mil", 74, 215, 80, "IBGE — Pesquisa da Pecuária Municipal (SIDRA 74)")
        reb, ano = sidra_produtos(3939, 105, 79)
        for k, iid, nome in [("Bovino", "rebanho_bovino", "Rebanho bovino"), ("Bubalino", "rebanho_bubalino", "Rebanho bubalino")]:
            B.indicador(id=iid, area="rural", nome=nome, unidade="cabeças", ref=ano, fonte="IBGE — Pesquisa da Pecuária Municipal (SIDRA 3939)",
                        fonte_url="https://sidra.ibge.gov.br/tabela/3939", estado=sum((reb.get(c) or {}).get(k, 0) for c in COD),
                        municipios={c: (reb.get(c) or {}).get(k, 0) for c in COD}, nota="Estado = soma dos municípios.")
        for c, v in reb.items():
            rural[c]["rebanhos"] = sorted(v.items(), key=lambda z: -z[1])[:8]
        est = B.sidra(6778, 183, "2017", "/c829/46302")
        fam = B.sidra(6778, 183, "2017", "/c829/46304")
        area = B.sidra(6881, 184, "2017", "/c829/46302/c222/110087")
        f17 = dict(ref="2017", fonte="IBGE — Censo Agropecuário 2017", fonte_url="https://sidra.ibge.gov.br/tabela/6778")
        B.indicador(id="agro_estab", area="rural", nome="Estabelecimentos agropecuários", unidade="estabelecimentos", estado=est.get(("13", 2017)),
                    municipios={c: v for (c, y), v in est.items() if c in COD}, **f17)
        B.indicador(id="agro_familiar", area="rural", nome="Estabelecimentos da agricultura familiar", unidade="%", tipo="calculado",
                    metodo="Estabelecimentos classificados como agricultura familiar ÷ total (Censo Agro 2017, SIDRA 6778)",
                    estado=pct(fam.get(("13", 2017)), est.get(("13", 2017))),
                    municipios={c: pct(fam.get((c, 2017)), v) for (c, y), v in est.items() if c in COD and v}, **f17)
        B.indicador(id="agro_area", area="rural", nome="Área dos estabelecimentos agropecuários", unidade="ha", estado=area.get(("13", 2017)),
                    municipios={c: v for (c, y), v in area.items() if c in COD}, **{**f17, "fonte_url": "https://sidra.ibge.gov.br/tabela/6881"})
        TERR["rural"] = {c: v for c, v in rural.items() if c in COD}
        B.registrar("IBGE/SIDRA — produção rural (PAM, PPM, PEVS, Censo Agro 2017)", t, len(TERR["rural"]), url=url)
    except Exception as e:
        B.registrar("IBGE/SIDRA — produção rural (PAM, PPM, PEVS, Censo Agro 2017)", t, 0, repr(e)[:200], url)


EXTRAS.append(economia)


def ifdm():
    """IFDM (FIRJAN). O site bloqueia downloads automáticos: o arquivo é baixado pelo navegador para bronze/publicos/firjan/."""
    t = time.time()
    url = "https://www.firjan.com.br/ifdm/downloads/"
    p = BRONZE / "firjan" / "ifdm_serie_2013_2023.xlsx"
    try:
        assert p.exists(), f"baixe 'Série Histórica IFDM' de {url} para {p}"
        import openpyxl
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        cod6 = {c[:6]: c for c in COD}
        for aba, iid, nome in [("IFDM Geral", "ifdm", "IFDM — Índice FIRJAN de Desenvolvimento Municipal"), ("IFDM Educação", "ifdm_edu", "IFDM Educação"),
                               ("IFDM Saúde", "ifdm_saude", "IFDM Saúde"), ("IFDM Emprego&Renda", "ifdm_renda", "IFDM Emprego e Renda")]:
            ws = wb[aba]
            linhas = ws.iter_rows(values_only=True)
            h = list(next(linhas))
            anos = [(i, int(re.search(r"(\d{4})$", str(x)).group(1))) for i, x in enumerate(h) if re.match(r"IFDM .*\d{4}$", str(x)) and not str(x).startswith("Ranking")]
            serie = {}
            for l in linhas:
                c = cod6.get(str(l[0])[:6])
                if c:
                    serie[c] = [[a, l[i]] for i, a in anos if isinstance(l[i], (int, float))]
            ult = max(a for _, a in anos)
            vals = {c: dict(map(tuple, s)).get(ult) for c, s in serie.items()}
            med = sorted(v for v in vals.values() if v is not None)
            B.indicador(id=iid, area="economia" if iid in ("ifdm", "ifdm_renda") else ("educacao" if iid == "ifdm_edu" else "saude"),
                        nome=nome, unidade="índice 0–1", ref=str(ult), fonte="FIRJAN — IFDM, série histórica 2013–2023", fonte_url=url,
                        municipios={c: v for c, v in vals.items() if v is not None}, serie_municipal=serie,
                        nota="Sem valor estadual: o painel mostra a mediana dos municípios. Faixas FIRJAN: até 0,4 baixo; 0,4–0,6 regular; 0,6–0,8 moderado; acima de 0,8 alto.")
        B.registrar("FIRJAN — IFDM", t, len(cod6), url=url)
    except Exception as e:
        B.registrar("FIRJAN — IFDM", t, 0, repr(e)[:200], url)


def ana():
    t = time.time()
    url = "https://metadados.snirh.gov.br/geonetwork/srv/api/records/1d8cea87-3d7b-49ff-86b8-966d96c9eb01/attachments/ATLAS_Esgotos_Tabela_Completa_por_Municipio.xlsx"
    try:
        import openpyxl
        ws = openpyxl.load_workbook(B.baixar(url, "ana/atlas_esgotos_municipios.xlsx"), read_only=True, data_only=True).worksheets[0]
        linhas = ws.iter_rows(values_only=True)
        h = list(next(linhas))
        d = {str(l[0]): dict(zip(h, l)) for l in linhas if str(l[0]) in COD}
        pu = {c: d[c]["População Urbana (2013)"] or 0 for c in d}
        def idx(col, c):
            v = d[c].get(col)
            return round(v * 100, 1) if isinstance(v, (int, float)) else None
        fonte = dict(ref="2013", fonte="ANA — Atlas Esgotos (sede urbana)", fonte_url="https://metadados.snirh.gov.br/geonetwork/srv/api/records/1d8cea87-3d7b-49ff-86b8-966d96c9eb01")
        for col, iid, nome, pol in [("Índice de Atendimento com Coleta e com Tratamento (2013)", "ana_coleta_trat", "População urbana com coleta e tratamento de esgoto", "maior_melhor"),
                                    ("Índice sem atendimento - sem Coleta e sem Tratamento (2013)", "ana_sem_atend", "População urbana sem coleta nem tratamento de esgoto", "menor_melhor")]:
            vals = {c: idx(col, c) for c in d}
            B.indicador(id=iid, area="saneamento", nome=nome, unidade="%", polaridade=pol, municipios={c: v for c, v in vals.items() if v is not None},
                        estado=round(sum((vals[c] or 0) * pu[c] for c in d) / sum(pu.values()), 1) if sum(pu.values()) else None, tipo="oficial",
                        nota="Estado = média ponderada pela população urbana de 2013.", **fonte)
        inv = {c: d[c].get("Investimentos em Coleta e Tratamento (R$)") for c in d}
        B.indicador(id="ana_invest", area="saneamento", nome="Investimento necessário em coleta e tratamento de esgoto até 2035", unidade="R$",
                    polaridade="neutra", municipios={c: round(v, 2) for c, v in inv.items() if isinstance(v, (int, float))},
                    estado=round(sum(v for v in inv.values() if isinstance(v, (int, float))), 2), **{**fonte, "ref": "2013–2035"})
        TERR["prestadores_esgoto"] = {c: d[c].get("Prestador de Serviço de Esgotamento Sanitário") for c in d}
        B.registrar("ANA — Atlas Esgotos por município", t, len(d), url=url)
    except Exception as e:
        B.registrar("ANA — Atlas Esgotos por município", t, 0, repr(e)[:200], url)


EXTRAS += [ifdm, ana]


# ---------------------------------------------------------------- transporte: DNIT (WFS) + bases locais da SEINFRA
import os  # noqa: E402

INFRA = Path(os.environ.get("OBS_INFRA", r"D:\Pedro\2-POWER BI  E PROJETOS\5-RODOVIAS\7-MAPEAMENTO GEO\3-DADOS INFRAESTRUTURA"))
DNIT = "https://servicos.dnit.gov.br/dnitgeo/geoserver/ows"


def conserta(s):
    """Texto UTF-8 lido como latin-1 (comum nos DBF da SEINFRA)."""
    if not isinstance(s, str):
        return s
    for _ in range(2):  # alguns DBF vêm com dupla codificação
        try:
            s = s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
    return s.strip()


def wfs(camada, filtro):
    import urllib.parse
    q = dict(service="WFS", version="1.0.0", request="GetFeature", typeName=camada, outputFormat="application/json", cql_filter=filtro)
    return B.json_url(DNIT + "?" + urllib.parse.urlencode(q), f"dnit/{camada.split(':')[1]}.json")["features"]


def partes_geojson(g):
    if g["type"] == "LineString":
        return [g["coordinates"]]
    if g["type"] == "MultiLineString":
        return g["coordinates"]
    return []


def ler_local(rel):
    import shapefile
    r = shapefile.Reader(str(INFRA / rel), encoding="latin-1")
    campos = [conserta(f[0]) for f in r.fields[1:]]
    return [(dict(zip(campos, [conserta(v) for v in sr.record])), sr.shape) for sr in r.iterShapeRecords()]


def km_por_mun(rel, col_mun="NM_MUN", col_km="sum"):
    import openpyxl
    ws = openpyxl.load_workbook(INFRA / rel, read_only=True, data_only=True).worksheets[0]
    linhas = list(ws.iter_rows(values_only=True))
    h = list(linhas[0])
    out = defaultdict(float)
    for l in linhas[1:]:
        c = B.POR_NOME.get(B.norm(l[h.index(col_mun)] or ""))
        if c and l[h.index(col_km)]:
            out[c] += float(l[h.index(col_km)])
    return out


def transporte():
    t = time.time()
    try:
        hoje = B.AGORA[:10]
        snv = wfs("vgeo:vw_snv_rod", f"Unidade_Federacao='AM' AND dt_ini<='{hoje}' AND dt_fim>='{hoje}'")
        CAMADAS["linhas"]["rod_federais"] = {"nome": "Rodovias federais (SNV/DNIT)", "fonte": "DNIT — Sistema Nacional de Viação, GeoServer vgeo", "url": DNIT,
                                            "itens": [{"rodovia": "BR-" + str(f["properties"]["Codigo_BR"]), "superficie": f["properties"]["Superficie_Federal"],
                                                       "km": f["properties"]["Extensao"], "trecho": f"{f['properties']['Local_Inicio']} – {f['properties']['Local_Fim']}",
                                                       "versao": f["properties"]["Versao_SNV"], "partes": partes_geojson(f["geometry"])} for f in snv]}
        obras = wfs("vgeo:tb_obras_diretas", "cd_uf='AM'")
        CAMADAS["linhas"]["obras_dnit"] = {"nome": "Obras diretas do DNIT", "fonte": "DNIT — obras diretas, GeoServer vgeo", "url": DNIT,
                                          "itens": [{"rodovia": f["properties"]["ds_br"], "objeto": f["properties"]["ds_obj_res"], "empresa": f["properties"]["nm_empresa"],
                                                     "valor": f["properties"]["vl_piar"], "km": f["properties"]["vl_ext"], "inicio": (f["properties"]["dt_inicio"] or "")[:10],
                                                     "termino": (f["properties"]["dt_termino"] or "")[:10], "programa": f["properties"]["ds_program"],
                                                     "partes": partes_geojson(f["geometry"])} for f in obras]}
        def pontos_wfs(camada, filtro, mapear):
            out = []
            for f in wfs(camada, filtro):
                g = f["geometry"]
                c = g["coordinates"][0] if g["type"] == "MultiPoint" else g["coordinates"]
                out.append({**mapear(f["properties"]), "lon": c[0], "lat": c[1]})
            return out
        CAMADAS["pontos"]["ip4"] = {"nome": "Instalações portuárias públicas de pequeno porte (IP4/DNIT)", "fonte": "DNIT — IP4, GeoServer vgeo", "url": DNIT,
                                   "itens": pontos_wfs("vgeo:daq_ip4_opr", "uf='AM'", lambda p: {"nome": p["empreendim"], "tipo": p["tipo"], "status": p["status_de_"],
                                                                                                 "municipio_txt": p["municipio"]})}
        CAMADAS["pontos"]["portos"] = {"nome": "Portos do SNV", "fonte": "DNIT — portos do Sistema Nacional de Viação", "url": DNIT,
                                      "itens": pontos_wfs("vgeo:vw_snv_portos", "Unidade_Federacao='AM'", lambda p: {"nome": p["Nome"], "rio": p["Local"]})}
        hid = wfs("vgeo:vw_snv_aqa", "BBOX(geom,-73.9,-9.9,-56.1,2.3)")
        CAMADAS["linhas"]["hidrovias"] = {"nome": "Hidrovias (SNV/DNIT)", "fonte": "DNIT — SNV aquaviário", "url": DNIT,
                                         "itens": [{"nome": f["properties"]["Nome"], "codigo": f["properties"]["Codigo"], "trecho": f["properties"]["Trecho"],
                                                    "partes": partes_geojson(f["geometry"])} for f in hid]}
        B.registrar("DNIT — GeoServer vgeo (SNV, obras, IP4, portos, hidrovias)", t, len(snv) + len(obras) + len(hid), url=DNIT)
    except Exception as e:
        B.registrar("DNIT — GeoServer vgeo (SNV, obras, IP4, portos, hidrovias)", t, 0, repr(e)[:200], DNIT)

    t = time.time()
    try:
        assert INFRA.exists(), f"pasta não encontrada: {INFRA} (defina OBS_INFRA)"
        loc = "SEINFRA-AM — base de infraestrutura (pasta local)"
        sre = ler_local("1-RODOVIAS ESTADUAIS/3-SRE SEINFRA - 2024 - REV01 - 23-04-2024/SRE SEINFRA - 2024.shp")
        CAMADAS["linhas"]["rod_estaduais"] = {"nome": "Rodovias estaduais (SRE SEINFRA 2024)", "fonte": loc, "url": None,
                                             "itens": [{"rodovia": r.get("RODOVIA"), "situacao": r.get("DESCRIÇÃO") or r.get("SITUAÇÃO"), "km": r.get("EXTENSÃO"),
                                                        "trecho": f"{r.get('INÍCIO', '')} – {r.get('FIM', '')}".replace("\n", " "),
                                                        "partes": [s.points[a:b] for a, b in zip(list(s.parts), list(s.parts[1:]) + [len(s.points)])]} for r, s in sre]}
        ram = ler_local("3-RAMAIS/1-TRAÇADO RAMAIS/RAMAIS - TRAÇADO REV06 - 16-05-2025/VICINAIS-RAMAIS-ESTRADAS - SEINFRA 2025.shp")
        km_ram, custo_ram = defaultdict(float), defaultdict(float)
        itens = []
        for r, s in ram:
            c = B.POR_NOME.get(B.norm(r.get("Município") or ""))
            km = B.num(r.get("Extensão"))
            custo = B.num(r.get("Custo Esti"))
            if c and km:
                km_ram[c] += km
            if c and custo:
                custo_ram[c] += custo
            itens.append({"nome": r.get("Descriçã"), "mun": c, "classe": r.get("Classifica"), "segmento": r.get("Segmentaç"), "km": km,
                          "revestimento": r.get("Revestimen"), "situacao": r.get("Situação"), "custo": custo,
                          "partes": [s.points[a:b] for a, b in zip(list(s.parts), list(s.parts[1:]) + [len(s.points)])]})
        CAMADAS["linhas"]["ramais"] = {"nome": "Ramais e estradas vicinais (SEINFRA 2025)", "fonte": loc, "url": None, "itens": itens}
        def pts_local(rel, mapear):
            return [{**mapear(r), "lon": s.points[0][0], "lat": s.points[0][1]} for r, s in ler_local(rel) if s.points]
        CAMADAS["pontos"]["transposicao"] = {"nome": "Pontes e meios de transposição (rodovias estaduais)", "fonte": loc, "url": None,
                                            "itens": pts_local("1-RODOVIAS ESTADUAIS/MEIOS DE TRANSPOSIÇÃO/MEIOS DE TRANSPOSIÇÃO.shp",
                                                               lambda r: {"nome": r.get("NOME"), "rodovia": r.get("RODOVIA"), "tipo": r.get("TIPO"), "km": r.get("MARCO QUIL"),
                                                                          "comprimento": r.get("COMPRIMENT")})}
        CAMADAS["pontos"]["flutuantes"] = {"nome": "Terminais flutuantes do Governo do Amazonas", "fonte": loc, "url": None,
                                          "itens": pts_local("8-TERMINAIS FLUTUANTES/TERMINAIS FLUTUANTES.shp",
                                                             lambda r: {"nome": r.get("Destino"), "localidade": r.get("Localidade")})}
        import openpyxl
        ws = openpyxl.load_workbook(INFRA / "9-REGIÕES E ESTATISTICAS/AEROPORTOS E AERODROMOS PUBLICOS - MUNICIPIOS.xlsx", read_only=True, data_only=True).worksheets[0]
        linhas = list(ws.iter_rows(values_only=True))
        h = [str(x) for x in linhas[0]]
        coord = {r.get("CIAD"): s.points[0] for r, s in ler_local("5-AERODROMOS/AEROPORTOS E AERÓDROMOS PÚBLICOS AMAZONAS/AEROPORTOS E AERÓDROMOS PÚBLICOS AMAZONAS.shp") if s.points}
        aer = []
        for l in linhas[1:]:
            d = dict(zip(h, l))
            p = coord.get(d.get("CIAD"))
            aer.append({"nome": d.get("Nome"), "icao": d.get("Código O") or l[0], "mun": str(d.get("CD_MUN") or "") or None, "outorga": d.get("Outorga"),
                        "pista_m": d.get("Compriment"), "superficie": d.get("Superfíc") or l[19], "lon": p[0] if p else None, "lat": p[1] if p else None})
        CAMADAS["pontos"]["aerodromos"] = {"nome": "Aeroportos e aeródromos públicos (ANAC)", "fonte": loc + " a partir do cadastro ANAC", "url": "https://www.gov.br/anac",
                                          "itens": aer}
        CAMADAS["pontos"]["aerodromos_priv"] = {"nome": "Aeródromos privados (ANAC)", "fonte": loc + " a partir do cadastro ANAC", "url": "https://www.gov.br/anac",
                                               "itens": pts_local("5-AERODROMOS/AERÓDROMOS PRIVADOS/AERÓDROMOS PRIVADOS AMAZONAS.shp",
                                                                  lambda r: {"nome": r.get("NOME"), "pista_m": r.get("COMPRIMENT")})}
        km_est = km_por_mun("9-REGIÕES E ESTATISTICAS/RODOVIAS ESTADUAIS - MUNICÍPIO ESTATISTICAS.xlsx")
        km_fed = km_por_mun("9-REGIÕES E ESTATISTICAS/RODOVIAS FEDERAIS - MUNICÍPIO ESTATISTICAS.xlsx")
        base = dict(area="transporte", ref="2025", fonte=loc, fonte_url="https://www.seinfra.am.gov.br", nota="Base fornecida pelo usuário (SEINFRA-AM); não é publicada em API.")
        for iid, nome, d, un in [("km_estaduais", "Rodovias estaduais", km_est, "km"), ("km_federais", "Rodovias federais", km_fed, "km"),
                                 ("km_ramais", "Ramais e estradas vicinais cadastrados", km_ram, "km")]:
            B.indicador(id=iid, nome=nome, unidade=un, estado=round(sum(d.values()), 1), municipios={c: round(d.get(c, 0), 1) for c in COD},
                        **{**base, "ref": "2024" if iid == "km_estaduais" else "2025"})
        B.indicador(id="custo_ramais", nome="Custo estimado de recuperação dos ramais", unidade="R$", estado=sum(custo_ram.values()),
                    municipios={c: custo_ram.get(c, 0) for c in COD}, polaridade="neutra", **base)
        B.registrar("SEINFRA-AM — rodovias, ramais, pontes, flutuantes e aeródromos (pasta local)", t, len(sre) + len(ram), url=str(INFRA))
    except Exception as e:
        B.registrar("SEINFRA-AM — rodovias, ramais, pontes, flutuantes e aeródromos (pasta local)", t, 0, repr(e)[:200], str(INFRA))


def contagens_transporte():
    """Indicadores de contagem por município a partir das camadas de pontos (depois de posicionar)."""
    for chave, iid, nome in [("flutuantes", "flutuantes", "Terminais flutuantes"), ("ip4", "ip4", "Instalações portuárias IP4 (DNIT)"),
                             ("aerodromos", "aerodromos", "Aeroportos e aeródromos públicos"), ("portos", "portos_snv", "Portos do SNV")]:
        cam = CAMADAS["pontos"].get(chave)
        if not cam:
            continue
        cont = defaultdict(int)
        for p in cam["itens"]:
            if p.get("mun"):
                cont[p["mun"]] += 1
        B.indicador(id=iid, area="transporte", nome=nome, unidade="unidades", ref=B.AGORA[:4], fonte=cam["fonte"], fonte_url=cam["url"] or "https://www.seinfra.am.gov.br",
                    estado=len(cam["itens"]), municipios={c: cont.get(c, 0) for c in COD}, tipo="calculado",
                    metodo="Contagem dos pontos dentro do polígono do município (malha IBGE)")


EXTRAS.append(transporte)


# ---------------------------------------------------------------- energia e telecomunicações: ANEEL (SIGA) + base EPE da pasta SEINFRA
SIGA = "https://dadosabertos.aneel.gov.br/dataset/6d90b77c-c5f5-4d81-bdec-7bc619494bb9/resource/11ec447d-698d-4ab8-977f-b424d5deee6a/download/siga-empreendimentos-geracao.csv"
TIPO_USINA = {"UTE": "Termelétrica", "UFV": "Solar fotovoltaica", "UHE": "Hidrelétrica", "PCH": "Pequena central hidrelétrica",
              "CGH": "Central geradora hidrelétrica", "EOL": "Eólica"}
EPE = "10-AMAZONIA LEGAL INFRAESTRUTURA"


def energia():
    t = time.time()
    pot, n_op = defaultdict(float), defaultdict(int)
    try:
        linhas = list(csv.DictReader(io.StringIO(B.baixar(SIGA, "aneel/siga.csv").read_bytes().decode("utf-8-sig")), delimiter=";"))
        itens = []
        for r in linhas:
            if r["SigUFPrincipal"] != "AM":
                continue
            c = B.POR_NOME.get(B.norm(r["DscMuninicpios"].split(" - ")[0]))
            mw = (B.num(r["MdaPotenciaFiscalizadaKw"]) or B.num(r["MdaPotenciaOutorgadaKw"]) or 0) / 1000
            oper = r["DscFaseUsina"] == "Operação"
            if c and oper:
                pot[c] += mw
                n_op[c] += 1
            itens.append({"nome": r["NomEmpreendimento"], "tipo": TIPO_USINA.get(r["SigTipoGeracao"], r["SigTipoGeracao"]),
                          "combustivel": r["NomFonteCombustivel"], "fase": r["DscFaseUsina"], "potencia_mw": round(mw, 2),
                          "inicio": r["DatEntradaOperacao"], "mun": c,
                          "lat": B.num(r["NumCoordNEmpreendimento"]), "lon": B.num(r["NumCoordEEmpreendimento"])})
        ref = linhas[0]["DatGeracaoConjuntoDados"]
        CAMADAS["pontos"]["usinas"] = {"nome": "Usinas de geração (ANEEL)", "fonte": f"ANEEL — SIGA, empreendimentos de geração ({dataBR(ref)})", "url": SIGA,
                                      "itens": sorted(itens, key=lambda i: -i["potencia_mw"])}
        fonte = "ANEEL — SIGA (Sistema de Informações de Geração)"
        B.indicador(id="potencia_mw", area="energia", nome="Potência instalada em operação", unidade="MW", ref=ref[:7], fonte=fonte, fonte_url=SIGA,
                    estado=round(sum(pot.values()), 1), municipios={c: round(pot.get(c, 0), 1) for c in COD}, polaridade="neutra",
                    nota="Potência fiscalizada das usinas em operação com outorga ou registro na ANEEL. Não inclui micro e minigeração distribuída.")
        B.indicador(id="usinas_oper", area="energia", nome="Usinas em operação", unidade="usinas", ref=ref[:7], fonte=fonte, fonte_url=SIGA,
                    estado=sum(n_op.values()), municipios={c: n_op.get(c, 0) for c in COD}, polaridade="neutra")
        fossil = sum(i["potencia_mw"] for i in itens if i["fase"] == "Operação" and i["tipo"] == "Termelétrica" and not re.search(r"bioma|bagaço|resíduo|lenha|óleos? vegeta", i["combustivel"] or "", re.I))
        B.indicador(id="pct_fossil", area="energia", nome="Potência térmica de origem fóssil", unidade="%", ref=ref[:7], fonte=fonte, fonte_url=SIGA,
                    estado=pct(fossil, sum(pot.values())), nivel_municipal=False, polaridade="menor_melhor", tipo="calculado",
                    metodo="Potência das termelétricas a combustível fóssil em operação ÷ potência total em operação")
        B.registrar("ANEEL — SIGA (usinas de geração)", t, len(itens), url=SIGA)
    except Exception as e:
        B.registrar("ANEEL — SIGA (usinas de geração)", t, 0, repr(e)[:200], SIGA)

    t = time.time()
    try:
        assert INFRA.exists(), f"pasta não encontrada: {INFRA} (defina OBS_INFRA)"
        loc = "EPE — WebMap, base da pasta SEINFRA (Amazônia Legal)"
        erb = [r for r, s in ler_local(f"{EPE}/Estações de Rádio Base (ERBs)/Estações de Rádio Base (ERBs).shp") if r.get("SiglaUf") == "AM"]
        cont, cont4 = defaultdict(int), defaultdict(int)
        itens = []
        for r in erb:
            c = str(r.get("CodMunicip") or "")[:7]
            cont[c] += 1
            cont4[c] += "4G" in (r.get("Tecnologia") or "") or "5G" in (r.get("Tecnologia") or "")
            itens.append({"nome": r.get("NomeEntida"), "tecnologia": r.get("Tecnologia"), "endereco": r.get("EnderecoEs"), "mun": c if c in COD else None,
                          "lat": r.get("Latitude d"), "lon": r.get("Longitud_1")})
        CAMADAS["pontos"]["erbs"] = {"nome": "Estações rádio base de telefonia móvel (ERBs)", "fonte": loc + ", a partir do licenciamento da Anatel", "url": "https://www.epe.gov.br/webmap", "itens": itens}
        # shortcut: a base EPE não traz data; o ano é o do arquivo. Para série atual, trocar pelo licenciamento da Anatel (dados abertos).
        ano = str(datetime.fromtimestamp((INFRA / EPE / "Estações de Rádio Base (ERBs)" / "Estações de Rádio Base (ERBs).shp").stat().st_mtime).year)
        base = dict(area="energia", ref=ano, fonte=loc, fonte_url="https://www.epe.gov.br/webmap", nota="Base EPE sem data; o ano de referência é o do arquivo recebido.")
        sem4 = sorted(m["nome"] for m in B.MUN if not cont4.get(m["cod"]))
        B.indicador(id="erbs", nome="Estações rádio base (ERBs)", unidade="estações", estado=len(itens), municipios={c: cont.get(c, 0) for c in COD},
                    **{**base, "nota": base["nota"] + (f" Sem ERB 4G ou 5G: {', '.join(sem4)}." if sem4 else " Os 62 municípios têm ao menos uma ERB 4G ou 5G.")})
        B.indicador(id="erbs_10mil", nome="ERBs por 10 mil habitantes", unidade="por 10 mil hab.", tipo="calculado", estado=round(len(itens) / pop_estado() * 1e4, 2) if pop_estado() else None,
                    municipios=por_hab(cont), metodo="ERBs ÷ população estimada IBGE mais recente × 10.000", **base)
        dutos = []
        for camada, tipo in [("Gasoduto de Transporte", "Gasoduto de transporte"), ("Gasoduto de Distribuição", "Gasoduto de distribuição"),
                             ("Oleoduto", "Oleoduto"), ("Poliduto", "Poliduto")]:
            for r, s in ler_local(f"{EPE}/{camada}/{camada}.shp"):
                pts = [p[:2] for p in s.points]
                if not any(-73.9 <= x <= -56.1 and -9.9 <= y <= 2.3 for x, y in pts[::max(1, len(pts) // 20)]):
                    continue
                dutos.append({"nome": repara(r.get("Nome_Dut_1") or r.get("Distrib") or tipo), "tipo": tipo, "km": B.num(r.get("COMPRIM_KM")) or None,
                              "partes": [pts[a:b] for a, b in zip(list(s.parts), list(s.parts[1:]) + [len(pts)])]})
        CAMADAS["linhas"]["dutos"] = {"nome": "Gasodutos e dutos de petróleo", "fonte": loc, "url": "https://www.epe.gov.br/webmap", "itens": dutos}
        B.registrar("EPE/SEINFRA — ERBs e dutos (pasta local)", t, len(itens) + len(dutos), url=str(INFRA / EPE))
    except Exception as e:
        B.registrar("EPE/SEINFRA — ERBs e dutos (pasta local)", t, 0, repr(e)[:200], str(INFRA / EPE))


def repara(s):
    """A base EPE perdeu acentos (caractere U+FFFD); recupera palavras que são nomes de município."""
    if "\ufffd" not in s:
        return s
    for m in B.MUN:
        for w in re.findall("\\S*\ufffd\\S*", s):
            if re.fullmatch(re.escape(w).replace("\ufffd", "."), m["nome"]):
                s = s.replace(w, m["nome"])
    return s.replace("\ufffd", "?")


def dataBR(d):
    return "/".join(reversed(d[:10].split("-")))


EXTRAS.append(energia)


# ---------------------------------------------------------------- malha municipal e posicionamento dos pontos
class Forma:
    """Polígono GeoJSON com a interface de pyshp usada aqui (points, parts, bbox)."""
    def __init__(self, geom):
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        self.points, self.parts = [], []
        for poly in polys:
            for anel in poly:
                self.parts.append(len(self.points))
                self.points += [tuple(p[:2]) for p in anel]
        xs, ys = [p[0] for p in self.points], [p[1] for p in self.points]
        self.bbox = [min(xs), min(ys), max(xs), max(ys)]


MALHA = {}


def malha_estado():
    t = time.time()
    url = "https://servicodados.ibge.gov.br/api/v3/malhas/estados/13?intrarregiao=municipio&qualidade=intermediaria&formato=application/vnd.geo%2Bjson"
    try:
        gj = B.json_url(url, "ibge/malha_am_municipios.json")
        formas = {f["properties"]["codarea"]: Forma(f["geometry"]) for f in gj["features"]}
        assert set(formas) == COD, len(formas)
        bx = [min(f.bbox[0] for f in formas.values()), min(f.bbox[1] for f in formas.values()),
              max(f.bbox[2] for f in formas.values()), max(f.bbox[3] for f in formas.values())]
        m = Moldura(bx, 800)
        MALHA.update(formas=formas, moldura=m)
        nomes = {x["cod"]: x["nome"] for x in B.MUN}
        TERR["malha"] = {"w": m.w, "h": m.h, "municipios": [{"cod": c, "nome": nomes[c], "d": m.path(f, .35)} for c, f in sorted(formas.items())]}
        B.registrar("IBGE — malha municipal (API de malhas)", t, len(formas), url=url)
    except Exception as e:
        B.registrar("IBGE — malha municipal (API de malhas)", t, 0, repr(e)[:200], url)


def posicionar_pontos():
    """Cada ponto ganha x,y no quadro do mapa estadual e, se faltar, o município por ponto no polígono."""
    if not MALHA:
        return
    m, formas = MALHA["moldura"], MALHA["formas"]
    for camada in CAMADAS["pontos"].values():
        for p in camada["itens"]:
            if p.get("lat") is None or p.get("lon") is None:
                continue
            x, y = m.xy(p["lon"], p["lat"])
            p["x"], p["y"] = round(x, 1), round(y, 1)
            if not p.get("mun"):
                p["mun"] = next((c for c, f in formas.items() if f.bbox[0] <= p["lon"] <= f.bbox[2] and f.bbox[1] <= p["lat"] <= f.bbox[3]
                                 and ponto_no_poligono(p["lon"], p["lat"], f)), None)
    for camada in CAMADAS["linhas"].values():
        for l in camada["itens"]:
            if "partes" in l:
                d = []
                for parte in l.pop("partes"):
                    pts = simplificar([m.xy(p[0], p[1]) for p in parte], .4)
                    if len(pts) > 1:
                        d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts))
                l["d"] = "".join(d)


EXTRAS.insert(0, malha_estado)


# ---------------------------------------------------------------- saída
REAREA = {"agua_rede": "saneamento", "esgoto_adequado": "saneamento", "lixo_coletado": "saneamento",
          "pop_censo": "demografia", "pop_estimada": "demografia", "densidade": "demografia", "area": "demografia"}


def main():
    B.BRONZE.mkdir(parents=True, exist_ok=True)
    for f in (B.ibge, B.ideb, B.prodes, B.queimadas, B.sinesp, B.cnes):
        f()
    geo = B.geotatica()
    censo()
    comunidades()
    for f in EXTRAS:
        f()
    posicionar_pontos()
    contagens_transporte()
    for i in B.indicadores:
        i["area"] = REAREA.get(i["id"], i["area"])
        i["municipios"] = {c: v for c, v in i["municipios"].items() if c in COD}
        assert i["fonte"] and i["fonte_url"] and i["ref"] and i["unidade"], i["id"]
        assert not i["nivel_municipal"] or len(i["municipios"]) >= 50, (i["id"], len(i["municipios"]))
    ids = [i["id"] for i in B.indicadores]
    assert len(ids) == len(set(ids)), [x for x in ids if ids.count(x) > 1]
    out = {"gerado_em": B.AGORA, "municipios": B.MUN, "indicadores": B.indicadores, "conectores": B.CONECTORES + CONECTORES_NOVOS,
           "ingestoes": B.ingestoes, "geotatica": geo}
    dados = RAIZ / "dados"
    (dados / "painel.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (dados / "painel.js").write_text("window.PAINEL = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
    TERR.pop("_formas", None)
    (dados / "territorio.js").write_text("window.TERRITORIO = " + json.dumps(TERR, ensure_ascii=False) + ";\n", encoding="utf-8")
    (dados / "camadas.js").write_text("window.CAMADAS = " + json.dumps(CAMADAS, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{len(B.indicadores)} indicadores, {len(TERR['bairros'])} bairros, {len(TERR['comunidades'])} comunidades, "
          f"{sum(len(v['itens']) for v in CAMADAS['pontos'].values())} pontos")
    falhas = [g for g in B.ingestoes if g["status"] != "ok"]
    sys.exit(1 if len(falhas) == len(B.ingestoes) else 0)


CONECTORES_NOVOS = [  # "ingestao" = nome usado em B.registrar, para a página de fontes achar o status
    {"id": "censo_setores", "ingestao": "IBGE/Censo 2022 — agregados por município e bairro", "nome": "IBGE — Censo 2022, agregados por setores (município e bairro)",
     "orgao": "IBGE", "acesso": "CSV no FTP", "periodicidade": "censitária", "url": AGREG, "cobertura": "62 municípios e 469 bairros"},
    {"id": "fcu", "ingestao": "IBGE/Censo 2022 — Favelas e Comunidades Urbanas", "nome": "IBGE — Favelas e Comunidades Urbanas 2022", "orgao": "IBGE",
     "acesso": "SHP + XLSX no FTP", "periodicidade": "censitária", "url": FTP + "Favelas_e_comunidades_urbanas_Resultados_do_universo/", "cobertura": "392 comunidades no AM"},
    {"id": "malha", "ingestao": "IBGE — malha municipal (API de malhas)", "nome": "IBGE — API de malhas", "orgao": "IBGE", "acesso": "API pública (GeoJSON)",
     "periodicidade": "anual", "url": "https://servicodados.ibge.gov.br/api/docs/malhas", "cobertura": "62 municípios"},
    {"id": "tse", "ingestao": "TSE — perfil do eleitorado 2026", "nome": "TSE — perfil do eleitorado por seção e locais de votação 2026", "orgao": "TSE",
     "acesso": "CSV (dados abertos)", "periodicidade": "por eleição", "url": "https://dadosabertos.tse.jus.br", "cobertura": "62 municípios, locais de votação"},
    {"id": "cnes_geo", "ingestao": "DATASUS/CNES — equipamentos georreferenciados", "nome": "DATASUS — CNES georreferenciado", "orgao": "Ministério da Saúde",
     "acesso": "API pública (JSON)", "periodicidade": "mensal", "url": "https://apidadosabertos.saude.gov.br", "cobertura": "estabelecimentos do AM"},
    {"id": "leitos", "ingestao": "DATASUS — hospitais e leitos", "nome": "DATASUS — hospitais e leitos", "orgao": "Ministério da Saúde", "acesso": "CSV anual (OpenDataSUS)",
     "periodicidade": "mensal", "url": "https://opendatasus.saude.gov.br/dataset/hospitais-e-leitos", "cobertura": "hospitais do AM"},
    {"id": "censo_escolar", "ingestao": "INEP — Censo Escolar 2024", "nome": "INEP — Censo Escolar 2024 (microdados)", "orgao": "INEP/MEC", "acesso": "ZIP/CSV",
     "periodicidade": "anual", "url": "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar", "cobertura": "escolas do AM"},
    {"id": "censo_superior", "ingestao": "INEP — Censo da Educação Superior 2023", "nome": "INEP — Censo da Educação Superior 2023", "orgao": "INEP/MEC",
     "acesso": "ZIP/CSV", "periodicidade": "anual", "url": "https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior", "cobertura": "IES e cursos no AM"},
    {"id": "osm", "ingestao": "OpenStreetMap — unidades de segurança", "nome": "OpenStreetMap — delegacias, quartéis e bombeiros", "orgao": "OpenStreetMap (colaborativo)",
     "acesso": "API Overpass", "periodicidade": "contínua", "url": "https://www.openstreetmap.org", "cobertura": "parcial", "nota": "Base colaborativa, usada só se a base da SSP-AM falhar."},
    {"id": "sidra_econ", "ingestao": "IBGE/SIDRA — economia municipal (PIB setorial, CEMPRE)", "nome": "IBGE — PIB setorial e Cadastro Central de Empresas", "orgao": "IBGE",
     "acesso": "API pública (JSON)", "periodicidade": "anual", "url": "https://sidra.ibge.gov.br/tabela/6449", "cobertura": "62 municípios"},
    {"id": "sidra_rural", "ingestao": "IBGE/SIDRA — produção rural (PAM, PPM, PEVS, Censo Agro 2017)", "nome": "IBGE — PAM, PPM, PEVS e Censo Agropecuário 2017",
     "orgao": "IBGE", "acesso": "API pública (JSON)", "periodicidade": "anual / censitária", "url": "https://sidra.ibge.gov.br/acervo", "cobertura": "62 municípios"},
    {"id": "ifdm", "ingestao": "FIRJAN — IFDM", "nome": "FIRJAN — IFDM (série 2013–2023)", "orgao": "FIRJAN", "acesso": "XLSX (download manual)",
     "periodicidade": "anual", "url": "https://www.firjan.com.br/ifdm/downloads/", "cobertura": "62 municípios",
     "nota": "O site bloqueia robôs: baixe a 'Série Histórica IFDM' pelo navegador para bronze/publicos/firjan/ifdm_serie_2013_2023.xlsx."},
    {"id": "ana", "ingestao": "ANA — Atlas Esgotos por município", "nome": "ANA — Atlas Esgotos", "orgao": "ANA", "acesso": "XLSX (SNIRH)", "periodicidade": "estudo (base 2013)",
     "url": "https://metadados.snirh.gov.br/geonetwork/srv/api/records/1d8cea87-3d7b-49ff-86b8-966d96c9eb01", "cobertura": "62 municípios"},
    {"id": "dnit", "ingestao": "DNIT — GeoServer vgeo (SNV, obras, IP4, portos, hidrovias)", "nome": "DNIT — GeoServer vgeo (WFS)", "orgao": "DNIT", "acesso": "WFS (GeoJSON)",
     "periodicidade": "contínua", "url": "https://servicos.dnit.gov.br/vgeo/", "cobertura": "rodovias federais, obras, IP4, portos e hidrovias do AM"},
    {"id": "seinfra", "ingestao": "SEINFRA-AM — rodovias, ramais, pontes, flutuantes e aeródromos (pasta local)", "nome": "SEINFRA-AM — base de infraestrutura",
     "orgao": "SEINFRA-AM", "acesso": "SHP/XLSX locais", "periodicidade": "revisões internas", "url": "https://www.seinfra.am.gov.br", "cobertura": "rodovias estaduais, ramais, pontes, flutuantes, aeródromos",
     "nota": "Lida da pasta local definida em OBS_INFRA (padrão: pasta 3-DADOS INFRAESTRUTURA no drive D:)."},
    {"id": "geobr_escolas", "ingestao": "IPEA/geobr — coordenadas das escolas (Catálogo INEP 2023)", "nome": "IPEA/geobr — escolas georreferenciadas (Catálogo de Escolas do INEP)",
     "orgao": "IPEA / INEP", "acesso": "GeoPackage", "periodicidade": "anual", "url": "https://ipeagit.github.io/geobr/", "cobertura": "escolas do AM com coordenada no catálogo"},
    {"id": "ssp_unidades", "ingestao": "SSP-AM — unidades policiais (ArcGIS)", "nome": "SSP-AM — mapa da segurança pública (unidades policiais)", "orgao": "SSP-AM",
     "acesso": "ArcGIS REST (GeoJSON)", "periodicidade": "contínua", "url": "https://www.ssp.am.gov.br/ssp-dados/",
     "cobertura": "Manaus: DIPs, especializadas, PM e bombeiros; interior: sedes da PM", "nota": "Delegacias do interior não estão no mapa da SSP-AM."},
    {"id": "ssp_anuario", "ingestao": "SSP-AM — Anuário de Segurança Pública (tabelas)", "nome": "SSP-AM — Anuário do Amazonas de Segurança Pública 2026", "orgao": "SSP-AM / CIESP",
     "acesso": "XLSX (link público no SharePoint)", "periodicidade": "anual", "url": "https://anuarioamsegpub-geoseguranca.hub.arcgis.com/",
     "cobertura": "homicídios por município 2017–2025, série estadual 2000–2025, efetivo policial"},
    {"id": "aneel_siga", "ingestao": "ANEEL — SIGA (usinas de geração)", "nome": "ANEEL — SIGA, empreendimentos de geração", "orgao": "ANEEL", "acesso": "CSV (dados abertos)",
     "periodicidade": "mensal", "url": "https://dadosabertos.aneel.gov.br/dataset/siga-sistema-de-informacoes-de-geracao-da-aneel", "cobertura": "usinas do AM"},
    {"id": "epe", "ingestao": "EPE/SEINFRA — ERBs e dutos (pasta local)", "nome": "EPE — WebMap (ERBs, gasodutos e dutos de petróleo)", "orgao": "EPE",
     "acesso": "SHP locais (pasta SEINFRA)", "periodicidade": "sem data", "url": "https://www.epe.gov.br/webmap", "cobertura": "ERBs e dutos no AM",
     "nota": "Lida da pasta 10-AMAZONIA LEGAL INFRAESTRUTURA em OBS_INFRA."},
]



if __name__ == "__main__":
    main()
