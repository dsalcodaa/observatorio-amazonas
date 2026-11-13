"""P01 — catálogo documental (camada bronze).

Baixa cada documento de fontes/documentos.json para bronze/documentos/ sem alterar o arquivo,
calcula SHA-256 e grava dados/document.json (entidade `document` da especificação).
Se o arquivo já existe com o mesmo hash, não baixa de novo; se a fonte mudou, guarda a nova versão ao lado.
"""
import hashlib, json, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF

RAIZ = Path(__file__).resolve().parents[1]
BRONZE = RAIZ / "bronze" / "documentos"
SAIDA = RAIZ / "dados" / "document.json"


def baixar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (observatorio-amazonas)"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main():
    BRONZE.mkdir(parents=True, exist_ok=True)
    fontes = json.loads((RAIZ / "fontes" / "documentos.json").read_text(encoding="utf-8"))
    antigo = {d["id"]: d for d in json.loads(SAIDA.read_text(encoding="utf-8"))} if SAIDA.exists() else {}
    docs, falhas = [], []
    for f in fontes:
        try:
            dados = baixar(f["url"])
        except Exception as e:  # registra a falha e segue com os demais
            falhas.append((f["id"], str(e)))
            if f["id"] in antigo:
                docs.append({**antigo[f["id"]], "ultima_verificacao_falhou": str(e)})
            continue
        sha = hashlib.sha256(dados).hexdigest()
        arq = BRONZE / f"{f['id']}__{sha[:12]}.pdf"
        if not arq.exists():
            arq.write_bytes(dados)
        assert hashlib.sha256(arq.read_bytes()).hexdigest() == sha
        with fitz.open(arq) as pdf:
            paginas, meta = pdf.page_count, pdf.metadata or {}
        ant = antigo.get(f["id"], {})
        docs.append({
            **f, "arquivo": str(arq.relative_to(RAIZ)).replace("\\", "/"), "sha256": sha, "bytes": len(dados),
            "paginas": paginas, "pdf_titulo": meta.get("title") or None, "pdf_criado": meta.get("creationDate") or None,
            "data_ingestao": ant.get("data_ingestao") if ant.get("sha256") == sha else datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "versoes_anteriores": ant.get("versoes_anteriores", []) + ([ant["sha256"]] if ant.get("sha256") and ant["sha256"] != sha else []),
        })
        print(f"ok  {f['id']:28} {paginas:4} p  {len(dados)/1e6:6.1f} MB  {sha[:12]}")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(docs, ensure_ascii=False, indent=1), encoding="utf-8")
    for i, e in falhas:
        print(f"FALHA {i}: {e}", file=sys.stderr)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
