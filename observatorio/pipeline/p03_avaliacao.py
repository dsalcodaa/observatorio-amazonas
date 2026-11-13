"""P03 — estrutura os Relatórios Anuais de Avaliação do PPA (camada gold).

Lê os documentos tipo 'avaliacao' (exercícios 2024, 2025…) e grava em dados/observatorio.sqlite:
áreas de resultado, programas, indicadores, metas anuais (indicator_target) e valores apurados
(indicator_observation), sempre com documento e página. Exporta dados/ppa.json para a interface.

Cuidados da especificação aplicados:
- valor original (texto do PDF) guardado ao lado do número normalizado; vazio fica nulo, nunca zero;
- polaridade não vem no relatório: é inferida pelo nome e marcada 'inferida' para validação humana;
- o '% (B/A)' publicado é guardado como está; o status é recalculado pela plataforma conforme a polaridade.
"""
import hashlib, json, os, re, sqlite3, sys, unicodedata
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

# OCR: Tesseract 5 com o modelo 'por' (tessdata oficial) em %LOCALAPPDATA%\tessdata
pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
os.environ.setdefault("TESSDATA_PREFIX", os.path.join(os.environ.get("LOCALAPPDATA", ""), "tessdata"))
OCR_DPI = 300

RAIZ = Path(__file__).resolve().parents[1]
DB = RAIZ / "dados" / "observatorio.sqlite"
ABRANGENCIAS = {"Setorial", "Multissetorial", "Intersetorial", "Transversal"}
# termos que indicam "quanto menor, melhor" (inferência; revisar caso a caso)
MENOR = ["mortalidade", "obito", "casos", "incidencia", "infestacao", "homicid", "crime", "violen", "vitima", "abandono",
         "distorcao", "desmat", "foco", "queimad", "tempo de espera", "tempo medio", "evasao", "reincid", "acidente",
         "afetad", "sifilis", "aids", "malaria", "internacao por condicoes sensiveis", "deficit", "letalidade", "roubo", "furto"]


def norm(s):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()).strip()


def numero(txt):
    """'27.460.629,000 0' -> 27460629.0 ; '' -> None (nunca zero)."""
    t = re.sub(r"[^\d,.\-]", "", txt or "")  # OCR solta lixo como "/" entre dígitos
    if not t or not re.search(r"\d", t):
        return None
    t = t.replace(".", "").replace(",", ".")
    try:
        return float(t)
    except ValueError:
        return None


def slug(s, n=10):
    return hashlib.sha1(norm(s).encode()).hexdigest()[:n]


def area_id(nome):
    # grafias mudam entre anos ("Desenvolvimento Regional" x "Desenvolvimento Regional e Crescimento…"): chave pelas 2 primeiras palavras
    p = [w for w in norm(nome).replace("&", " ").split() if w not in {"e", "de", "do", "da", "pela", "pelo"}]
    return "-".join(p[:2])


def polaridade(nome):
    n = norm(nome)
    return "menor_melhor" if any(k in n for k in MENOR) else "maior_melhor"


def cabecalho_programa(texto):
    """Campos do quadro do programa, pela ordem fixa em que o PDF os apresenta."""
    m = re.search(r"Programa\s*\n\s*(\d{4})\s*-\s*([^\n]+)\n", texto)  # âncora evita o "2024-2027" do cabeçalho
    if not m:
        return None
    i = texto.find("Público Alvo")
    linhas = [l.strip() for l in texto[i:].split("\n")[1:] if l.strip()] if i >= 0 else []
    k = next((j for j, l in enumerate(linhas) if l in ABRANGENCIAS), None)
    if k is None or k < 3:
        return {"codigo": m.group(1), "nome": m.group(2).strip(), "confianca": "baixa"}
    ods = [l for l in linhas[k + 1:k + 12] if l.startswith("ODS")]
    part = linhas[k + 1] if k + 1 < len(linhas) and not linhas[k + 1].startswith("ODS") else None
    return {"codigo": m.group(1), "nome": m.group(2).strip(), "tipo": linhas[0], "orgao_responsavel": linhas[1],
            "objetivo": " ".join(linhas[2:k - 1]), "publico_alvo": linhas[k - 1], "abrangencia": linhas[k],
            "orgaos_participantes": part, "ods": "; ".join(ods), "confianca": "media"}


def ocr_palavras(pg, doc_id):
    """OCR da página renderizada a 300 dpi (Tesseract, português), com cache em silver/ocr/.
    Devolve palavras com caixa em coordenadas da página (as mesmas de find_tables)."""
    cache = RAIZ / "silver" / "ocr" / doc_id / f"{pg.number + 1}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    pix = pg.get_pixmap(dpi=OCR_DPI)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = pytesseract.image_to_data(img, lang="por", config="--psm 11", output_type=pytesseract.Output.DICT)
    k = 72 / OCR_DPI
    ws = [[d["left"][i] * k, d["top"][i] * k, (d["left"][i] + d["width"][i]) * k, (d["top"][i] + d["height"][i]) * k, d["text"][i], float(d["conf"][i])]
          for i in range(len(d["text"])) if d["text"][i].strip()]
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(ws, ensure_ascii=False), encoding="utf-8")
    return ws


def texto_ocr(palavras, caixa):
    """Palavras cujo centro cai na caixa, agrupadas em linhas pela altura e lidas da esquerda para a direita."""
    x0, y0, x1, y1 = caixa
    ws = sorted((w for w in palavras if x0 <= (w[0] + w[2]) / 2 <= x1 and y0 <= (w[1] + w[3]) / 2 <= y1), key=lambda w: (w[1] + w[3]) / 2)
    linhas, atual = [], []
    for w in ws:
        if atual and (w[1] + w[3]) / 2 - (atual[0][1] + atual[0][3]) / 2 > 0.5 * (atual[0][3] - atual[0][1]):
            linhas.append(atual); atual = []
        atual.append(w)
    if atual:
        linhas.append(atual)
    return " ".join(w[4] for l in linhas for w in sorted(l, key=lambda w: w[0])).strip(), (min((w[5] for w in ws), default=None))


def linhas_indicadores(pg, doc_id):
    """Linhas da tabela 'Indicadores': o OCR lê; a camada de texto do PDF confere campos curtos e números."""
    palavras = None
    for t in pg.find_tables().tables:
        dados = t.extract()  # camada de texto (corta nomes no meio, mas números e unidades vêm exatos)
        if not dados or "Indicadores" not in (dados[0][0] or "") or len(dados[0]) < 8:
            continue
        palavras = palavras or ocr_palavras(pg, doc_id)
        anterior = ""
        for r, linha in enumerate(dados):
            if r < 2 or not any(linha):
                continue
            cel = t.rows[r].cells
            caixas = [c for c in cel[:2] if c]
            caixa_nome = (min(c[0] for c in caixas), min(c[1] for c in caixas), max(c[2] for c in caixas), max(c[3] for c in caixas))
            nome, conf_nome = texto_ocr(palavras, caixa_nome)
            campos, divergencias = {}, []
            for j, k in enumerate(["periodicidade", "unidade", "ano", "previsto", "apurado", "pct"], start=2):
                ocr = texto_ocr(palavras, cel[j])[0] if cel[j] else ""
                txt = re.sub(r"\s+", " ", linha[j] or "").strip()
                if k in ("previsto", "apurado", "pct"):
                    # a camada de texto traz os dígitos certos mas embaralha "." e ","; o OCR traz a pontuação
                    dig = re.sub(r"\D", "", txt)
                    igual = re.sub(r"\D", "", ocr) == dig
                    # divergência (OCR lê "7" como "/", troca 3/8): dígitos da camada de texto + posição da vírgula lida pelo OCR
                    ent = len(re.sub(r"\D", "", ocr.rsplit(",", 1)[0])) if "," in ocr else len(dig)
                    sinal = "-" if "-" in ocr + txt else ""
                    campos[k] = ocr if igual or not dig else sinal + dig[:ent] + ("," + dig[ent:] if dig[ent:] else "")
                else:
                    igual = norm(ocr) == norm(txt)
                    campos[k] = txt if txt else ocr  # campo curto: vale a camada de texto
                if not igual and (k in ("previsto", "apurado", "pct") or not txt):  # campo curto com texto: OCR só erra o "%" ("Y%")
                    divergencias.append(f"{k}: OCR '{ocr}' x texto '{txt}'")
            nome = nome or re.sub(r"\s+", " ", " ".join(x or "" for x in linha[:2])).strip() or anterior  # linha vazia = outro ano do mesmo indicador
            anterior = nome
            yield {"nome": nome, **campos,
                   "confianca_ocr_nome": conf_nome, "divergencias": divergencias}


def processa(con, d, versao):
    doc = pymupdf.open(RAIZ / d["arquivo"])
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    area, prog, n_ind, rejeitados, log = None, None, 0, 0, []
    for i, pg in enumerate(doc, 1):
        texto = pg.get_text()
        m = re.search(r"ÁREA DE RESULTADO:\s*([^\n]+)", texto)
        if m and "Tipo do Programa" not in texto:
            nome = m.group(1).strip()
            area = area_id(nome)
            ant = con.execute("SELECT nomes_originais FROM result_area WHERE id=?", (area,)).fetchone()
            nomes = sorted(set(json.loads(ant[0]) if ant else []) | {nome})
            con.execute("INSERT OR REPLACE INTO result_area VALUES (?,?,?)", (area, nomes[0], json.dumps(nomes, ensure_ascii=False)))
        if "Tipo do Programa" in texto:
            c = cabecalho_programa(texto)
            if c:
                prog = c["codigo"]
                # a versão mais recente do relatório prevalece nos atributos descritivos
                con.execute("""INSERT OR REPLACE INTO program (id,codigo,nome,tipo,abrangencia,area_resultado_id,objetivo,publico_alvo,
                    orgao_responsavel,orgaos_participantes,ods,ppa_version_id,documento_id,pagina,confianca) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (prog, prog, c["nome"], c.get("tipo"), c.get("abrangencia"), area, c.get("objetivo"), c.get("publico_alvo"),
                     c.get("orgao_responsavel"), c.get("orgaos_participantes"), c.get("ods"), versao, d["id"], i, c["confianca"]))
        if prog and "Previsto Ano" in texto:
            for l in linhas_indicadores(pg, d["id"]):
                if not l["nome"] or not l["ano"].isdigit():
                    rejeitados += 1; log.append(f"p{i}: linha sem nome/ano {l}"); continue
                ind = f"{prog}-{slug(l['nome'])}"
                pol = polaridade(l["nome"])
                con.execute("""INSERT INTO indicator (id,program_id,nome,unidade,periodicidade,polaridade,polaridade_origem)
                    VALUES (?,?,?,?,?,?,'inferida') ON CONFLICT(id) DO UPDATE SET unidade=excluded.unidade, periodicidade=excluded.periodicidade""",
                    (ind, prog, l["nome"], l["unidade"], l["periodicidade"], pol))
                ano = int(l["ano"])
                con.execute("INSERT OR REPLACE INTO indicator_target VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                            (f"{ind}-{ano}-{d['id']}", ind, versao, ano, numero(l["previsto"]), l["previsto"].strip(), l["unidade"], "AM", prog, d["id"], i))
                con.execute("INSERT OR REPLACE INTO indicator_observation VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (f"{ind}-{ano}-{d['id']}", ind, f"{ano}-12-31", numero(l["apurado"]), l["apurado"].strip(), l["unidade"], "AM",
                             d["titulo"], d["id"], i, d.get("data_publicacao"), agora,
                             "em_validacao" if l["divergencias"] else "extraido_documento",
                             numero(l["pct"]), l["pct"].strip(), None))
                con.execute("INSERT OR REPLACE INTO document_extraction VALUES (?,?,?,?,?,?,?,?)",
                            (f"{ind}-{ano}-{d['id']}", d["id"], i, prog, "indicadores", json.dumps(l, ensure_ascii=False),
                             "revisar" if l["divergencias"] else f"ocr_conf_min={l['confianca_ocr_nome']}",
                             "pendente" if l["divergencias"] else "automatico_conferido"))
                n_ind += 1
    con.execute("INSERT INTO ingestion_run VALUES (?,?,?,?,?,?,?,?,?)",
                (f"{d['id']}-{agora}", agora, d["id"], n_ind + rejeitados, n_ind, rejeitados, "ok" if not rejeitados else "ok_com_rejeicoes",
                 "\n".join(log), d["sha256"]))
    return n_ind, rejeitados


def status(ind, meta, obs):
    """Status descritivo (seção 8.5), calculado pela plataforma conforme a polaridade."""
    if obs is None:
        return "sem_dado"
    if meta is None:
        return "meta_nao_aplicavel"
    if ind["polaridade"] == "menor_melhor":
        if obs <= meta: return "meta_atingida"
        return "atencao" if meta and obs <= meta * 1.10 else "fora_da_trajetoria"
    if obs >= meta: return "meta_atingida"
    return "atencao" if meta and obs >= meta * 0.90 else "fora_da_trajetoria"


def exporta(con):
    con.row_factory = sqlite3.Row
    q = lambda s, *a: [dict(r) for r in con.execute(s, a)]
    progs = q("SELECT * FROM program ORDER BY area_resultado_id, codigo")
    inds = q("SELECT * FROM indicator ORDER BY program_id, nome")
    metas = q("SELECT * FROM indicator_target")
    obs = q("SELECT * FROM indicator_observation")
    for i in inds:
        i["metas"] = sorted([m for m in metas if m["indicator_id"] == i["id"]], key=lambda m: m["exercicio"])
        i["observacoes"] = sorted([o for o in obs if o["indicator_id"] == i["id"]], key=lambda o: (o["data_referencia"], o["data_publicacao"] or ""))  # republicação mais recente por último
        for o in i["observacoes"]:
            ano = int(o["data_referencia"][:4])
            meta = next((m["valor"] for m in i["metas"] if m["exercicio"] == ano and m["documento_id"] == o["documento_id"]), None)
            o["meta"], o["status"] = meta, status(i, meta, o["valor"])
    saida = {"gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "ppa_versions": q("SELECT * FROM ppa_version"), "documentos": q("SELECT * FROM document"),
             "areas": q("SELECT * FROM result_area ORDER BY nome"), "programas": progs, "indicadores": inds,
             "ingestoes": q("SELECT id,data_hora,fonte,registros_recebidos,registros_aceitos,registros_rejeitados,status,hash_arquivo FROM ingestion_run")}
    (RAIZ / "dados" / "ppa.json").write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    (RAIZ / "dados" / "ppa.js").write_text("window.PPA = " + json.dumps(saida, ensure_ascii=False) + ";\n", encoding="utf-8")
    return saida


def main():
    docs = json.loads((RAIZ / "dados" / "document.json").read_text(encoding="utf-8"))
    DB.unlink(missing_ok=True)  # gold é sempre reconstruído a partir do bronze
    con = sqlite3.connect(DB)
    con.executescript((RAIZ / "pipeline" / "schema.sql").read_text(encoding="utf-8"))
    con.executemany("INSERT INTO ppa_version VALUES (?,?,?,?,?,?,?,?,?)", [
        ("PPA-2024-2027-original", "PPA 2024–2027 — versão original", "Lei nº 6.671, de 28/12/2023", "2023-12-28",
         "2024-01-01", "2027-12-31", "historica", "lei-6671-2023", None),
        ("PPA-2024-2027-rev-2026-2027", "PPA 2024–2027 — revisão para 2026–2027", "Lei nº 7.978, de 16/12/2025", "2025-12-16",
         "2026-01-01", "2027-12-31", "vigente", "lei-7978-2025", "Revisão das metas e atributos para o biênio 2026–2027"),
    ])
    for d in docs:
        con.execute("INSERT INTO document VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (d["id"], d["titulo"], d["tipo"], d["url"], d["arquivo"], d["sha256"], d["bytes"], d["paginas"],
                     d.get("data_publicacao"), d.get("data_ingestao"), d.get("ppa_version"), d.get("exercicio")))
    for d in sorted((d for d in docs if d["tipo"] == "avaliacao"), key=lambda d: d["exercicio"]):
        n, rej = processa(con, d, d["ppa_version"])
        print(f"{d['id']}: {n} linhas de indicador, {rej} rejeitadas")
    con.commit()
    s = exporta(con)
    print(f"{len(s['areas'])} áreas, {len(s['programas'])} programas, {len(s['indicadores'])} indicadores")


if __name__ == "__main__":
    sys.exit(main())
