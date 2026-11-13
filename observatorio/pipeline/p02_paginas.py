"""P02 — extração página a página (camada silver, entidade `document_extraction`).

Para cada documento de dados/document.json grava silver/paginas/<id>.jsonl com:
página, título de seção mais recente (maior fonte da página), texto e se a página parece ter tabela.
"""
import json, sys
from pathlib import Path

import fitz

RAIZ = Path(__file__).resolve().parents[1]
SILVER = RAIZ / "silver" / "paginas"


def titulo_da_pagina(pg):
    # maior trecho de texto em fonte grande (>= 13 pt) na página, se houver
    maior, txt = 0, ""
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = s["text"].strip()
                if len(t) > 3 and s["size"] >= 13 and s["size"] > maior:
                    maior, txt = s["size"], t
    return txt


def main(ids=None):
    SILVER.mkdir(parents=True, exist_ok=True)
    docs = json.loads((RAIZ / "dados" / "document.json").read_text(encoding="utf-8"))
    for d in docs:
        if ids and d["id"] not in ids:
            continue
        secao, linhas = "", []
        with fitz.open(RAIZ / d["arquivo"]) as pdf:
            for i, pg in enumerate(pdf, 1):
                t = titulo_da_pagina(pg)
                secao = t or secao
                texto = pg.get_text("text")
                linhas.append(json.dumps({"document_id": d["id"], "sha256": d["sha256"], "pagina": i, "secao": secao,
                                          "texto": texto, "tem_tabela": bool(pg.find_tables().tables) if len(texto) > 200 else False,
                                          "sem_texto": len(texto.strip()) < 20}, ensure_ascii=False))
        (SILVER / f"{d['id']}.jsonl").write_text("\n".join(linhas) + "\n", encoding="utf-8")
        sem = sum(json.loads(l)["sem_texto"] for l in linhas)
        print(f"{d['id']:28} {len(linhas):4} páginas  {sem:3} sem texto (imagem)")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
