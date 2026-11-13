/* Observatório Amazonas — painel (HTML estático; dados em dados/painel.js, territorio.js, camadas.js e ppa.js). */
(() => {
  "use strict";
  const P = window.PAINEL, PPA = window.PPA, T = window.TERRITORIO || {}, CAM = window.CAMADAS || { pontos: {}, linhas: {} };
  const GEO = T.malha || window.MUNICIPIOS; // a malha do pipeline usa a mesma projeção dos pontos
  const $ = (s, el = document) => el.querySelector(s);
  const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const page = $("#page"), tip = $("#tip");

  if (!P || !GEO) {
    page.innerHTML = `<div class="card"><div class="empty">Dados não encontrados. Rode <code>python -I pipeline/p05_ampliacao.py</code> na pasta <code>observatorio/</code> e recarregue.</div></div>`;
    return;
  }

  /* ---------------- ícones (traço único, 24px) */
  const I = {
    home: "M3 11 12 4l9 7M5 10v10h14V10M10 20v-6h4v6",
    coins: "M12 7c4.4 0 8-1.3 8-3s-3.6-3-8-3-8 1.3-8 3 3.6 3 8 3ZM4 4v6c0 1.7 3.6 3 8 3s8-1.3 8-3V4M4 10v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6",
    book: "M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5ZM4 19a2 2 0 0 1 2-2h13",
    heart: "M12 20s-7-4.4-9-9a5 5 0 0 1 9-3 5 5 0 0 1 9 3c-2 4.6-9 9-9 9ZM7 11h3l1-2 2 4 1-2h3",
    shield: "M12 3 4 6v6c0 4.5 3.4 8 8 9 4.6-1 8-4.5 8-9V6l-8-3Z",
    leaf: "M5 19c0-8 5-14 15-15-1 10-7 15-15 15ZM5 19l7-7",
    road: "M7 21 10 3M17 21 14 3M12 7v2M12 13v2M12 19v2",
    target: "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM12 12h.01",
    pin: "M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11ZM12 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z",
    db: "M12 8c4.4 0 8-1.3 8-3s-3.6-3-8-3-8 1.3-8 3 3.6 3 8 3ZM4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3",
    users: "M16 20v-1a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v1M9.5 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM21 20v-1a4 4 0 0 0-3-3.9M16 4.1a3.5 3.5 0 0 1 0 6.8",
    flame: "M12 21a6 6 0 0 0 6-6c0-4-3-6-4-10-2 2-3 4-3 6-1-1-2-2-2-4-2 2-3 5-3 8a6 6 0 0 0 6 6Z",
    drop: "M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11Z",
    check: "M5 12.5 10 17l9-10",
    alert: "M12 8v5M12 16.5h.01M10.3 3.9 2.6 17a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z",
    x: "M6 6l12 12M18 6 6 18",
    minus: "M6 12h12",
    ext: "M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5",
    down: "M12 5v14M6 13l6 6 6-6",
    vote: "M4 13h16v7H4zM8 13V5h8v8M10 9l2 2 3-4",
    sprout: "M12 21v-9M12 12c0-4 3-7 8-7 0 5-3 7-8 7ZM12 14c0-3-2-5-7-5 0 4 2 5 7 5Z",
    city: "M3 21h18M5 21V8l5-3v16M10 21V10h9v11M13 13h3M13 17h3",
    pipe: "M3 9h8a3 3 0 0 1 3 3v9M3 5h8a7 7 0 0 1 7 7v9M8 9V5",
    route: "M6 19a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM18 9a2 2 0 1 0 0-4 2 2 0 0 0 0 4ZM6 15V9a4 4 0 0 1 4-4h6M18 9v6a4 4 0 0 1-4 4H8",
    grid: "M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z",
    bolt: "M13 3 5 14h6l-1 7 8-11h-6l1-7Z",
  };
  const ico = (n, cls = "") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true"><path d="${I[n]}"/></svg>`;

  /* ---------------- dados */
  const IND = Object.fromEntries(P.indicadores.map(i => [i.id, i]));
  const MUN = Object.fromEntries(P.municipios.map(m => [m.cod, m]));
  const PATH = Object.fromEntries(GEO.municipios.map(m => [m.cod, m.d]));
  const OBS_PPA = PPA ? PPA.indicadores.flatMap(i => i.observacoes.map(o => ({ ...o, ind: i }))) : [];
  const PROG = PPA ? Object.fromEntries(PPA.programas.map(p => [p.id, p])) : {};
  const AREA_PPA = PPA ? Object.fromEntries(PPA.areas.map(a => [a.id, a])) : {};
  const DOC = PPA ? Object.fromEntries(PPA.documentos.map(d => [d.id, d])) : {};

  // indicadores municipais de uma ou mais áreas do pipeline, na ordem em que foram gerados
  const daArea = (...ar) => P.indicadores.filter(i => ar.includes(i.area) && Object.keys(i.municipios).length).map(i => i.id);
  const AREAS = [
    { g: "Pessoas" },
    { id: "demografia", nome: "Demografia", icon: "users", resumo: "Censo 2022: idade, sexo, cor ou raça, povos indígenas e quilombolas, domicílios e rendimento.",
      kpis: ["pop_estimada", "pct_0_14", "pct_60", "pct_indigena"], series: ["pop_estimada"], mapa: daArea("demografia"), ppa: /prote..o social|identidade/i },
    { id: "eleitorado", nome: "Eleitorado", icon: "vote", resumo: "Perfil do eleitorado de 2026 (TSE) por município, cruzado com o Censo 2022.",
      kpis: ["eleitores", "eleit_mulheres", "eleit_jovens", "eleit_superior"], series: [], mapa: daArea("eleitorado"), ppa: null },
    { g: "Economia" },
    { id: "economia", nome: "Economia e renda", icon: "coins", resumo: "PIB, estrutura produtiva, empresas, emprego formal e IFDM (FIRJAN).",
      kpis: ["pib_pc", "pib", "ifdm", "salario_medio"], series: ["pib_pc", "pib"], mapa: daArea("socioeconomia", "economia"), ppa: /desenvolvimento econ|regional/i },
    { id: "rural", nome: "Produção rural", icon: "sprout", resumo: "Lavouras, rebanhos, extrativismo e aquicultura (IBGE) e o Censo Agropecuário 2017.",
      kpis: ["pam_valor", "pevs_valor", "rebanho_bovino", "agro_estab"], series: [], mapa: daArea("rural"), ppa: /rural|agro|produ..o|econ/i },
    { g: "Serviços públicos" },
    { id: "educacao", nome: "Educação", icon: "book", resumo: "Escolas, matrículas, infraestrutura escolar, IDEB, ensino superior e alfabetização.",
      kpis: ["matriculas", "escolas", "ideb_in", "mat_superior"], series: [], mapa: daArea("educacao"), ppa: /educa/i },
    { id: "saude", nome: "Saúde", icon: "heart", resumo: "Leitos, hospitais, UBS e rede cadastrada no CNES, com localização.",
      kpis: ["leitos_sus_hab", "uti_sus_hab", "hospitais", "ubs"], series: [], mapa: daArea("saude"), ppa: /sa.de/i },
    { id: "seguranca", nome: "Segurança pública", icon: "shield", resumo: "Mortes violentas e ocorrências registradas no SINESP, por mês e município, e unidades policiais.",
      kpis: ["cvli_taxa", "sinesp_cvli", "sinesp_feminicidio", "sinesp_transito"],
      series: ["sinesp_cvli", "sinesp_homicidio", "sinesp_feminicidio", "sinesp_latrocinio", "sinesp_transito", "sinesp_tentativa_homicidio", "sinesp_estupro", "sinesp_roubo_veiculo", "sinesp_trafico", "sinesp_armas_apreendidas"],
      mensal: true, mapa: daArea("seguranca"), ppa: /paz|seguran/i },
    { g: "Infraestrutura" },
    { id: "transporte", nome: "Transporte", icon: "route", resumo: "Rodovias federais e estaduais, ramais, hidrovias, portos, terminais flutuantes, pontes e aeródromos.",
      kpis: ["km_federais", "km_estaduais", "km_ramais", "flutuantes"], series: [], mapa: daArea("transporte"), ppa: /infra|log.stica|mobil/i },
    { id: "energia", nome: "Energia e telecomunicações", icon: "bolt", resumo: "Usinas de geração (ANEEL), gasodutos e estações rádio base de telefonia móvel.",
      kpis: ["potencia_mw", "pct_fossil", "erbs", "erbs_10mil"], series: [], mapa: daArea("energia"), ppa: /energ|conectiv|telecom|digital|infra/i },
    { id: "cidades", nome: "Cidades", icon: "city", resumo: "Favelas e comunidades urbanas, densidade e domicílios (Censo 2022).",
      kpis: ["pop_fcu", "domicilios", "moradores_dom", "densidade"], series: [], mapa: [...daArea("cidades"), "densidade", "domicilios", "moradores_dom"], ppa: /cidade|habita|urban/i },
    { id: "saneamento", nome: "Saneamento", icon: "pipe", resumo: "Água, esgoto e lixo nos domicílios (Censo 2022) e atendimento e investimento em esgoto (ANA).",
      kpis: ["agua_rede", "esgoto_rede", "lixo_coletado", "ana_coleta_trat"], series: [], mapa: daArea("saneamento"), ppa: /saneamento|.gua|infra/i },
    { id: "meio-ambiente", nome: "Meio ambiente", icon: "leaf", resumo: "Desmatamento (PRODES), focos de calor e floresta remanescente.",
      kpis: ["desmatamento", "focos", "floresta"], series: ["desmatamento", "focos"], mapa: ["desmatamento", "focos", "floresta"], ppa: /ambient|sustent|clima/i },
  ].filter(a => a.g || a.kpis.some(k => IND[k]));
  const AREA = Object.fromEntries(AREAS.filter(a => a.id).map(a => [a.id, a]));
  AREA.socioeconomia = AREA.economia; // links antigos

  /* ---------------- formatação */
  const nf = (v, d = 0) => v == null || isNaN(v) ? "—" : v.toLocaleString("pt-BR", { minimumFractionDigits: d, maximumFractionDigits: d });
  function fmt(v, u, curto = false) {
    if (v == null || isNaN(v)) return "—";
    if (u === "R$ mil") { const r = v * 1000; return r >= 1e9 ? `R$ ${nf(r / 1e9, 1)} bi` : `R$ ${nf(r / 1e6, 1)} mi`; }
    if (u === "R$") return `R$ ${nf(v, 0)}`;
    if (u === "%" || u === "% da área") return `${nf(v, 1)}%`;
    if (u === "índice") return nf(v, 1);
    if (/por 10|por 100/.test(u)) return nf(v, 1);
    if (u === "km²" || u === "hab/km²") return nf(v, v < 100 ? 1 : 0);
    if (curto && v >= 1e6) return `${nf(v / 1e6, 2)} mi`;
    return nf(v, Number.isInteger(v) ? 0 : 1);
  }
  const unidadeCurta = u => ({ "R$ mil": "", "R$": "", "%": "", "% da área": "", "índice": "", pessoas: "hab.", registros: "", focos: "focos", estabelecimentos: "" }[u] ?? u);
  const fonteCurta = i => i.fonte.split(" — ")[0] + (i.fonte.includes("SIDRA") ? " / SIDRA" : "");
  const dataBR = d => String(d || "").replace(/^(\d{4})-(\d{2})-(\d{2})$/, "$3/$2/$1");
  const refFmt = r => String(r).replace(/^(\d{4})-(\d{2})(-\d{2})?$/, (_, a, m) => `${m}/${a}`);
  const mediana = a => { const s = a.filter(v => v != null).sort((x, y) => x - y); if (!s.length) return null; const m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

  function valorEstado(i) {
    if (i.estado != null) return { v: i.estado, obs: null };
    const m = mediana(Object.values(i.municipios));
    return { v: m, obs: "mediana municipal" };
  }

  /* ---------------- tooltip */
  function showTip(html, ev) {
    tip.innerHTML = html; tip.hidden = false;
    const r = tip.getBoundingClientRect();
    let x = ev.clientX + 14, y = ev.clientY + 14;
    if (x + r.width > innerWidth - 8) x = ev.clientX - r.width - 14;
    if (y + r.height > innerHeight - 8) y = ev.clientY - r.height - 14;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  const hideTip = () => { tip.hidden = true; };

  /* ---------------- gráficos SVG */
  const W = 760;
  function niceMax(m) { if (m <= 0) return 1; const p = 10 ** Math.floor(Math.log10(m)); const n = m / p; return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p; }

  function chart(serie, { tipo = "line", u = "", h = 260, parcialDe = null, w = W } = {}) {
    const W = w;
    const pts = serie.filter(p => p[1] != null);
    if (pts.length < 2) return `<div class="chart-empty">Série com menos de dois pontos.</div>`;
    const pad = { l: 56, r: 12, t: 14, b: 28 }, iw = W - pad.l - pad.r, ih = h - pad.t - pad.b;
    const passo = niceMax(Math.max(...pts.map(p => p[1])) / 4), nt = Math.max(1, Math.ceil(Math.max(...pts.map(p => p[1])) / passo));
    const max = passo * nt, n = serie.length;
    const x = k => pad.l + (tipo === "bar" ? (k + .5) * iw / n : k * iw / (n - 1));
    const y = v => pad.t + ih - v / max * ih;
    let g = "";
    for (let t = 0; t <= nt; t++) {
      const v = passo * t;
      const tk = Number.isInteger(passo) && !/R\$/.test(u) ? nf(v, 0) : fmt(v, u, true);
      g += `<line class="grid-l" x1="${pad.l}" x2="${W - pad.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${pad.l - 8}" y="${y(v) + 4}" text-anchor="end">${tk}</text>`;
    }
    const step = Math.ceil(n / 12);
    serie.forEach((p, k) => { if (k === n - 1 || (k % step === 0 && n - 1 - k >= step * .7)) g += `<text x="${x(k)}" y="${h - 8}" text-anchor="middle">${esc(String(p[0]).replace(/^(\d{4})-(\d{2})$/, (_, a, m) => `${m}/${a.slice(2)}`))}</text>`; });
    let marks = "";
    if (tipo === "bar") {
      const bw = Math.max(2, Math.min(28, iw / n - 3));
      serie.forEach((p, k) => {
        if (p[1] == null) return;
        const yy = y(p[1]), hh = pad.t + ih - yy, parcial = parcialDe && String(p[0]) >= parcialDe;
        marks += `<path class="bar${parcial ? " partial" : ""}" d="M${x(k) - bw / 2},${pad.t + ih}V${yy + Math.min(3, hh)}q0,-3 3,-3h${bw - 6}q3,0 3,3V${pad.t + ih}Z"/>`;
      });
      const l = n - 1 - [...serie].reverse().findIndex(p => p[1] != null);
      marks += `<text class="lbl" x="${x(l)}" y="${y(serie[l][1]) - 7}" text-anchor="middle">${fmt(serie[l][1], u, true)}</text>`;
    } else {
      let d = "", a = "";
      serie.forEach((p, k) => { if (p[1] == null) return; d += (d && serie[k - 1]?.[1] != null ? "L" : "M") + x(k) + "," + y(p[1]); });
      const f = serie.findIndex(p => p[1] != null), l = serie.length - 1 - [...serie].reverse().findIndex(p => p[1] != null);
      a = d + `L${x(l)},${pad.t + ih}L${x(f)},${pad.t + ih}Z`;
      marks = `<path class="area" d="${a.replace(/M/g, (m, i) => i ? "L" : "M")}"/><path class="line" d="${d}"/>`;
      const last = serie[l];
      marks += `<circle class="dot" cx="${x(l)}" cy="${y(last[1])}" r="4.5"/><text class="lbl" x="${x(l) - 6}" y="${y(last[1]) - 10}" text-anchor="end">${fmt(last[1], u, true)}</text>`;
    }
    const hits = serie.map((p, k) => `<rect class="hit" data-k="${k}" x="${x(k) - iw / n / 2}" y="${pad.t}" width="${iw / n}" height="${ih}"/>`).join("");
    const id = "c" + Math.random().toString(36).slice(2, 8);
    queueMicrotask(() => {
      const svg = document.getElementById(id); if (!svg) return;
      const cross = svg.querySelector(".cross");
      // texto em px fixo, independente da escala do viewBox (legível em projetor e no celular)
      const fit = () => svg.clientWidth && svg.style.setProperty("--fs", Math.min(22, 12.5 * W / svg.clientWidth) + "px");
      fit(); new ResizeObserver(fit).observe(svg);
      svg.addEventListener("mousemove", e => {
        const k = e.target.dataset?.k; if (k == null) return;
        const p = serie[k];
        cross.setAttribute("x1", x(+k)); cross.setAttribute("x2", x(+k)); cross.style.display = "";
        showTip(`<b>${esc(p[0])}</b><br>${p[1] == null ? "sem dado" : fmt(p[1], u)} ${esc(unidadeCurta(u))}${parcialDe && String(p[0]) >= parcialDe ? '<br><span class="t-sub">período parcial</span>' : ""}`, e);
      });
      svg.addEventListener("mouseleave", () => { cross.style.display = "none"; hideTip(); });
    });
    return `<svg id="${id}" class="chart" viewBox="0 0 ${W} ${h}" role="img" aria-label="Gráfico de ${tipo === "bar" ? "barras" : "linha"}">${g}<line class="axis-l" x1="${pad.l}" x2="${W - pad.r}" y1="${pad.t + ih}" y2="${pad.t + ih}"/>${marks}<line class="cross" y1="${pad.t}" y2="${pad.t + ih}" style="display:none"/>${hits}</svg>`;
  }

  /* ---------------- mapa coroplético */
  const SEQ = ["--seq-1", "--seq-2", "--seq-3", "--seq-4", "--seq-5", "--seq-6"].map(v => `var(${v})`);
  function classes(vals) {
    const s = [...new Set(vals.filter(v => v != null))].sort((a, b) => a - b);
    if (!s.length) return [];
    const k = Math.min(6, s.length), q = [];
    for (let j = 1; j < k; j++) q.push(s[Math.floor(j * s.length / k)]);
    return [...new Set(q)];
  }
  function mapa(ind, { destaque = null, localizar = false } = {}) {
    const vals = P.municipios.map(m => ind.municipios[m.cod] ?? null);
    const br = classes(vals);
    const cor = v => localizar ? "var(--line)" : v == null ? null : SEQ[Math.min(SEQ.length - 1, br.filter(b => v >= b).length + (br.length < 5 ? 1 : 0))];
    const paths = GEO.municipios.map(m => {
      const v = ind.municipios[m.cod], c = localizar && m.cod === destaque ? "var(--clay)" : cor(v);
      return `<path d="${m.d}" data-cod="${m.cod}" class="${c ? "" : "nodata"}${m.cod === destaque ? " on" : ""}" ${c ? `style="fill:${c}"` : ""}><title>${esc(m.nome)}</title></path>`;
    }).join("");
    const id = "m" + Math.random().toString(36).slice(2, 8);
    queueMicrotask(() => {
      const el = document.getElementById(id); if (!el) return;
      el.querySelectorAll("title").forEach(t => t.remove());
      el.addEventListener("mousemove", e => {
        const c = e.target.dataset?.cod; if (!c) return hideTip();
        showTip(`<b>${esc(MUN[c].nome)}</b><br>${fmt(ind.municipios[c], ind.unidade)} ${esc(unidadeCurta(ind.unidade))}<br><span class="t-sub">${esc(ind.nome)} · ${esc(ind.ref)}</span>`, e);
      });
      el.addEventListener("mouseover", e => { if (e.target.dataset?.cod) e.target.parentNode.appendChild(e.target); });
      el.addEventListener("mouseleave", hideTip);
      el.addEventListener("click", e => { const c = e.target.dataset?.cod; if (c) location.hash = `#/municipios/${c}`; });
    });
    const lims = localizar ? [] : [Math.min(...vals.filter(v => v != null)), ...br];
    const leg = lims.map((b, j) => `<span><i style="background:${cor(b)}"></i>${j === lims.length - 1 ? "≥ " : ""}${fmt(b, ind.unidade, true)}${j < lims.length - 1 ? "–" + fmt(lims[j + 1], ind.unidade, true) : ""}</span>`).join("")
      + (!localizar && vals.some(v => v == null) ? `<span><i class="nd"></i>sem dado</span>` : "");
    return `<div class="map-wrap"><div class="map" id="${id}"><svg viewBox="0 0 ${GEO.w} ${GEO.h}" role="img" aria-label="Mapa dos municípios: ${esc(ind.nome)}"><defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff"/><line x1="0" y1="0" x2="0" y2="5" stroke="var(--nodata)" stroke-width="2"/></pattern></defs>${paths}</svg></div><div class="legend">${leg}</div></div>`;
  }

  /* ---------------- tabela municipal ordenável */
  function tabelaMun(ind, { limite = null } = {}) {
    const linhas = P.municipios.map(m => ({ cod: m.cod, nome: m.nome, v: ind.municipios[m.cod] ?? null }));
    const max = Math.max(...linhas.map(l => l.v ?? 0)) || 1;
    const id = "t" + Math.random().toString(36).slice(2, 8);
    let ord = { k: "v", d: -1 };
    const corpo = () => {
      const s = [...linhas].sort((a, b) => ord.k === "nome" ? a.nome.localeCompare(b.nome) * ord.d
        : (a.v == null) - (b.v == null) || (a.v - b.v) * ord.d || a.nome.localeCompare(b.nome));
      return (limite ? s.slice(0, limite) : s).map(l => `<tr class="click" data-cod="${l.cod}" tabindex="0"><td>${esc(l.nome)}</td><td class="n"><div class="bar-cell">${l.v == null ? '<span class="muted">sem dado</span>' : `${fmt(l.v, ind.unidade)}<i style="width:${Math.max(2, l.v / max * 70)}px"></i>`}</div></td></tr>`).join("");
    };
    queueMicrotask(() => {
      const t = document.getElementById(id); if (!t) return;
      t.addEventListener("click", e => {
        const b = e.target.closest("th button");
        if (b) { const k = b.dataset.k; ord = { k, d: ord.k === k ? -ord.d : (k === "nome" ? 1 : -1) }; t.tBodies[0].innerHTML = corpo(); t.querySelectorAll("th").forEach(th => th.setAttribute("aria-sort", th.dataset.k === ord.k ? (ord.d > 0 ? "ascending" : "descending") : "none")); return; }
        const tr = e.target.closest("tr[data-cod]"); if (tr) location.hash = `#/municipios/${tr.dataset.cod}`;
      });
      t.addEventListener("keydown", e => { const tr = e.target.closest("tr[data-cod]"); if (tr && e.key === "Enter") location.hash = `#/municipios/${tr.dataset.cod}`; });
    });
    return `<div class="table-wrap"><table id="${id}"><thead><tr><th data-k="nome" aria-sort="none"><button data-k="nome">Município${ico("down", "sort-i")}</button></th><th class="n" data-k="v" aria-sort="descending"><button data-k="v">${esc(ind.unidade)}${ico("down", "sort-i")}</button></th></tr></thead><tbody>${corpo()}</tbody></table></div>`;
  }

  /* ---------------- blocos */
  function kpi(id, { link = null, col = "c3" } = {}) {
    const i = IND[id];
    if (!i) return `<div class="card kpi ${col}"><div class="kpi-label">Indicador indisponível</div><div class="kpi-meta">Fonte não carregada nesta execução do pipeline.</div></div>`;
    const { v, obs } = valorEstado(i);
    const s = (i.serie || []).filter(p => p[1] != null);
    let delta = "";
    if (s.length >= 2) {
      const a = s[s.length - 1], b = s[s.length - 2];
      if (String(a[0]) === i.ref && b[1]) {
        const pct = (a[1] - b[1]) / b[1] * 100;
        delta = `<div class="kpi-delta">${pct >= 0 ? "+" : ""}${nf(pct, 1)}% em relação a ${esc(b[0])}</div>`;
      }
    }
    const tag = obs ? `<span class="tag calc" title="Não há valor estadual publicado nesta fonte">${obs}</span>` : i.tipo === "calculado" ? `<span class="tag calc" title="${esc(i.metodo)}">calculado</span>` : `<span class="tag">oficial</span>`;
    const tagName = link ? "a" : "div";
    return `<${tagName} class="card kpi ${col}"${link ? ` href="${link}"` : ""}>
      <div class="kpi-label">${esc(i.nome)}</div>
      <div class="kpi-value">${fmt(v, i.unidade)}<small>${esc(unidadeCurta(i.unidade))}</small></div>${delta}
      <div class="kpi-meta">${tag}<span>${esc(fonteCurta(i))} · ${esc(refFmt(i.ref))}</span></div></${tagName}>`;
  }

  const ST = {
    meta_atingida: ["ok", "check", "Meta atingida"], atencao: ["at", "alert", "Atenção"], fora_da_trajetoria: ["fo", "x", "Fora da trajetória"],
    sem_dado: ["sd", "minus", "Sem dado"], meta_nao_aplicavel: ["sd", "minus", "Meta não aplicável"],
  };
  const status = s => { const [c, i, t] = ST[s] || ST.sem_dado; return `<span class="st ${c}">${ico(i)}${t}</span>`; };
  const COR_ST = { meta_atingida: "var(--good)", atencao: "var(--warn)", fora_da_trajetoria: "var(--crit)", sem_dado: "var(--nodata)", meta_nao_aplicavel: "var(--line-strong)" };

  function contagemStatus(obs) {
    const c = { meta_atingida: 0, atencao: 0, fora_da_trajetoria: 0, sem_dado: 0, meta_nao_aplicavel: 0 };
    obs.forEach(o => { c[o.status] = (c[o.status] || 0) + 1; });
    return c;
  }
  function trilha(c) {
    const tot = Object.values(c).reduce((a, b) => a + b, 0) || 1;
    return `<div class="track" role="img" aria-label="${Object.entries(c).map(([k, v]) => `${ST[k][2]}: ${v}`).join(", ")}">${Object.entries(c).filter(([, v]) => v).map(([k, v]) => `<span style="width:${v / tot * 100}%;background:${COR_ST[k]}" title="${ST[k][2]}: ${v}"></span>`).join("")}</div>`;
  }
  const legendaStatus = c => `<div class="stack-legend">${Object.entries(c).filter(([, v]) => v).map(([k, v]) => `${status(k)}<span class="num muted">${v}</span>`).join("")}</div>`;

  const ultimoExercicio = () => Math.max(...OBS_PPA.map(o => +o.data_referencia.slice(0, 4)));
  function obsPPA(re = null, ano = ultimoExercicio()) {
    return OBS_PPA.filter(o => +o.data_referencia.slice(0, 4) === ano && (!re || re.test(AREA_PPA[PROG[o.ind.program_id]?.area_resultado_id]?.nome || "")));
  }
  const linkPDF = o => { const d = DOC[o.documento_id]; return d ? `<a href="${esc(d.arquivo)}#page=${o.pagina}" target="_blank" rel="noopener" class="nw" title="Abrir a página do relatório">p.&nbsp;${o.pagina}</a>` : ""; };

  function cardPPA(re, titulo) {
    const ano = ultimoExercicio(), obs = obsPPA(re, ano);
    if (!obs.length) return `<div class="card c4"><div class="card-head"><h2>${titulo}</h2></div><div class="empty">Nenhum indicador do PPA associado a esta área no exercício ${ano}.</div></div>`;
    const c = contagemStatus(obs);
    const ordem = { fora_da_trajetoria: 0, atencao: 1, sem_dado: 2, meta_nao_aplicavel: 3, meta_atingida: 4 };
    const itens = [...obs].sort((a, b) => ordem[a.status] - ordem[b.status]).slice(0, 4);
    return `<div class="card c4"><div class="card-head"><h2>${titulo}</h2><span class="sub">exercício ${ano} · ${obs.length} indicadores</span></div>
      <div class="card-body">${trilha(c)}${legendaStatus(c)}
      <ul class="list" style="margin-top:10px">${itens.map(o => `<li><div class="l-main"><div class="l-title">${esc(o.ind.nome)}</div><div class="l-sub">meta ${fmt(o.meta, o.unidade)} · apurado ${fmt(o.valor, o.unidade)} ${esc(o.unidade || "")} · ${linkPDF(o)}</div></div>${status(o.status)}</li>`).join("")}</ul></div>
      <div class="card-foot"><a href="#/ppa">Ver todos os indicadores do PPA</a> · fonte: Relatório Anual de Avaliação ${ano}</div></div>`;
  }

  function seletor(ids, atual, attr) {
    const ok = ids.filter(id => IND[id]);
    if (ok.length <= 1) return "";
    return `<select class="sel" ${attr} aria-label="Escolher indicador">${ok.map(id => `<option value="${id}"${id === atual ? " selected" : ""}>${esc(IND[id].nome)}</option>`).join("")}</select>`;
  }

  function cardSerie(ids, titulo, { mensal = false, col = "c8" } = {}) {
    const ok = ids.filter(id => IND[id] && (IND[id].serie?.length > 1 || (mensal && IND[id].serie_mensal?.length)));
    if (!ok.length) return "";
    let atual = ok[0], modo = mensal ? "mensal" : "anual";
    const render = () => {
      const i = IND[atual];
      const parcial = new Date().getFullYear().toString();
      const serie = modo === "mensal" && i.serie_mensal?.length ? i.serie_mensal.slice(-36) : i.serie;
      const ok2 = serie.filter(p => p[1] != null), ult = ok2[ok2.length - 1], ant = ok2[ok2.length - 2];
      const pico = ok2.reduce((m, p) => p[1] > m[1] ? p : m, ok2[0]);
      const lb = r => esc(refFmt(r));
      const strip = ult ? `<div class="counters"><div><span>Último (${lb(ult[0])})</span><b>${fmt(ult[1], i.unidade)}</b></div>${ant && ant[1] ? `<div><span>Variação sobre ${lb(ant[0])}</span><b>${ult[1] >= ant[1] ? "+" : ""}${nf((ult[1] - ant[1]) / ant[1] * 100, 1)}%</b></div>` : ""}<div><span>Maior valor (${lb(pico[0])})</span><b>${fmt(pico[1], i.unidade)}</b></div><div><span>Período</span><b>${lb(ok2[0][0])}–${lb(ult[0])}</b></div></div>` : "";
      return `${strip}${chart(serie, { tipo: modo === "mensal" || i.id.startsWith("sinesp") || i.id === "ssp_homicidios" || i.id === "focos" || i.id === "desmatamento" ? "bar" : "line", u: i.unidade, h: 330, parcialDe: modo === "mensal" ? null : parcial })}
        <p class="note" style="margin-top:10px"><b>${esc(i.nome)}</b> — ${esc(i.fonte)}${i.metodo ? `. Método: ${esc(i.metodo)}` : ""}${i.nota ? `. ${esc(i.nota)}` : ""}</p>`;
    };
    const id = "s" + Math.random().toString(36).slice(2, 8);
    queueMicrotask(() => {
      const el = document.getElementById(id); if (!el) return;
      el.addEventListener("change", e => { if (e.target.matches("[data-serie]")) { atual = e.target.value; $(".card-body", el).innerHTML = render(); } });
      el.addEventListener("click", e => {
        const b = e.target.closest("[data-modo]"); if (!b) return;
        modo = b.dataset.modo; el.querySelectorAll("[data-modo]").forEach(x => x.setAttribute("aria-pressed", x === b));
        $(".card-body", el).innerHTML = render();
      });
    });
    return `<div class="card ${col}" id="${id}"><div class="card-head"><h2>${titulo}</h2><div class="filters">${seletor(ok, atual, "data-serie")}${mensal ? `<div class="seg"><button data-modo="mensal" aria-pressed="true">Mensal</button><button data-modo="anual" aria-pressed="false">Anual</button></div>` : ""}</div></div><div class="card-body">${render()}</div></div>`;
  }

  function cardMapa(ids, titulo, { destaque = null } = {}) {
    const ok = ids.filter(id => IND[id] && Object.keys(IND[id].municipios).length);
    if (!ok.length) return "";
    let atual = ok[0];
    const id = "k" + Math.random().toString(36).slice(2, 8);
    const corpo = () => `<div class="card c7"><div class="card-head"><h2>${titulo}</h2>${seletor(ok, atual, "data-mapa")}</div><div class="card-body">${mapa(IND[atual], { destaque })}</div><div class="card-foot">${esc(IND[atual].fonte)} · ${esc(refFmt(IND[atual].ref))} · classes por quantis; cores indicam magnitude, não avaliação. Clique no município para abrir a ficha.</div></div>
      <div class="card c5"><div class="card-head"><h2>Municípios</h2><span class="sub">${esc(IND[atual].nome)}</span></div>${tabelaMun(IND[atual])}</div>`;
    queueMicrotask(() => {
      const el = document.getElementById(id); if (!el) return;
      el.addEventListener("change", e => { if (e.target.matches("[data-mapa]")) { atual = e.target.value; el.innerHTML = corpo(); } });
      const acende = (e, on) => { const tr = e.target.closest?.("tr[data-cod]"); const p = tr && el.querySelector(`.map path[data-cod="${tr.dataset.cod}"]`); if (!p) return; p.classList.toggle("on", on); if (on) p.parentNode.appendChild(p); };
      el.addEventListener("mouseover", e => acende(e, true)); el.addEventListener("mouseout", e => acende(e, false));
      el.addEventListener("focusin", e => acende(e, true)); el.addEventListener("focusout", e => acende(e, false));
    });
    return `<div class="grid" id="${id}" style="grid-column:span 12;margin:0">${corpo()}</div>`;
  }

  /* ---------------- páginas */
  function cabecalho(titulo, texto, crumbs = "") {
    return `<div class="page-head"><div>${crumbs ? `<div class="crumbs">${crumbs}</div>` : ""}<h1>${titulo}</h1>${texto ? `<p>${texto}</p>` : ""}</div></div>`;
  }

  function visao() {
    const obs = obsPPA(), c = contagemStatus(obs), ano = ultimoExercicio();
    const porArea = PPA ? PPA.areas.map(a => { const o = obs.filter(x => PROG[x.ind.program_id]?.area_resultado_id === a.id); return { a, o, c: contagemStatus(o) }; }).filter(x => x.o.length) : [];
    const resumo = AREAS.filter(a => a.id).flatMap(a => a.kpis.filter(k => IND[k]).map(k => ({ a, i: IND[k] })));
    return cabecalho("Visão geral do Amazonas", "Indicadores públicos dos 62 municípios e metas do PPA 2024–2027. Cada número traz ano de referência e fonte.")
      + `<div class="grid">${["pop_estimada", "pib_pc", "eleitores", "cvli_taxa", "matriculas", "leitos_sus_hab", "km_ramais", "desmatamento"].filter(k => IND[k]).map(k => kpi(k, { link: `#/${AREAS.find(a => a.kpis?.includes(k))?.id}` })).join("")}</div>
      <div class="grid">${cardSerie(["cvli_taxa", "desmatamento", "focos", "pib_pc", "pop_estimada"], "Evolução no estado")}
        <div class="card c4"><div class="card-head"><h2>Metas do PPA</h2><span class="sub">exercício ${ano}</span></div><div class="card-body">
          <div class="sbar"><div class="sbar-top"><span>${obs.length} indicadores apurados</span><b>${nf(c.meta_atingida / (obs.length - c.sem_dado - c.meta_nao_aplicavel || 1) * 100, 0)}%</b></div>${trilha(c)}<span class="muted" style="font-size:12px">atingiram a meta, entre os que têm dado e meta aplicável</span></div>
          ${legendaStatus(c)}
          <ul class="list area-list" style="margin-top:12px">${porArea.map(x => `<li><span class="l-title" title="${esc(x.a.nome)}">${esc(x.a.nome)}</span>${trilha(x.c)}<span class="num muted">${x.c.meta_atingida}/${x.o.length}</span></li>`).join("")}</ul>
        </div><div class="card-foot"><a href="#/ppa">Abrir o painel do PPA</a></div></div></div>
      <div class="grid">${cardMapa(["cvli_taxa", "pib_pc", "ifdm", "eleitores", "renda_media", "ideb_in", "matriculas", "leitos_sus_hab", "esgoto_rede", "pop_fcu", "km_ramais", "pam_valor", "desmatamento", "focos", "alfabetizacao"], "Mapa dos municípios")}</div>
      <div class="grid"><div class="card c12"><div class="card-head"><h2>Panorama por área</h2><span class="sub">valor estadual mais recente de cada indicador</span></div>
        <div class="table-wrap" style="max-height:none"><table><thead><tr><th class="hide-m">Área</th><th>Indicador</th><th class="n">Amazonas</th><th>Ref.</th><th class="hide-m">Tipo</th><th class="hide-m">Fonte</th></tr></thead><tbody>
        ${resumo.map(({ a, i }) => { const { v, obs } = valorEstado(i); return `<tr class="click" tabindex="0" onclick="location.hash='#/${a.id}'" onkeydown="if(event.key==='Enter')location.hash='#/${a.id}'"><td class="hide-m">${esc(a.nome)}</td><td>${esc(i.nome)}</td><td class="n">${fmt(v, i.unidade)} <span class="muted">${esc(unidadeCurta(i.unidade))}</span></td><td>${esc(refFmt(i.ref))}</td><td class="hide-m">${obs ? `<span class="tag calc">${obs}</span>` : i.tipo === "calculado" ? '<span class="tag calc">calculado</span>' : '<span class="tag">oficial</span>'}</td><td class="muted hide-m">${esc(i.fonte)}</td></tr>`; }).join("")}
        </tbody></table></div></div></div>`;
  }

  function area(a) {
    const lado = ladoArea(a), princ = principalArea(a);
    return cabecalho(a.nome, a.resumo, `<a href="#/visao">Visão geral</a> / ${a.nome}`)
      + `<div class="grid">${a.kpis.filter(k => IND[k]).map((k, _, l) => kpi(k, { col: l.length === 3 ? "c4" : l.length === 2 ? "c6" : "c3" })).join("")}</div>`
      + `<div class="grid">${lado ? princ : princ.replace('class="card c8"', 'class="card c12"')}${lado}</div>`
      + `<div class="grid">${cardMapa(a.mapa, "Distribuição territorial")}</div>`
      + rodapeArea(a);
  }

  function cardIdeb(a) {
    // áreas sem série estadual: mostra a série municipal do IDEB (educação) ou a distribuição municipal
    const ids = a.mapa.filter(id => IND[id]?.serie_municipal);
    if (ids.length) {
      const i = IND[ids[0]];
      const anos = [...new Set(Object.values(i.serie_municipal).flatMap(s => s.map(p => p[0])))].sort();
      const med = anos.map(y => [y, mediana(Object.values(i.serie_municipal).map(s => (s.find(p => p[0] === y) || [])[1]))]);
      return `<div class="card c8"><div class="card-head"><h2>${esc(i.nome)}: mediana dos municípios</h2><span class="sub">INEP · ${anos[0]}–${anos[anos.length - 1]}</span></div><div class="card-body">${chart(med, { u: "índice" })}<p class="note" style="margin-top:10px">O arquivo municipal do INEP não traz o IDEB do estado; a linha mostra a mediana dos municípios com resultado em cada edição (calculado).</p></div></div>`;
    }
    const i = IND[a.mapa.find(id => IND[id])];
    if (!i) return `<div class="card c8"><div class="empty">Sem dados carregados para esta área.</div></div>`;
    const vals = Object.values(i.municipios).filter(v => v != null);
    const top = [...P.municipios].filter(m => i.municipios[m.cod] != null).sort((x, y) => i.municipios[y.cod] - i.municipios[x.cod]);
    return `<div class="card c8"><div class="card-head"><h2>${esc(i.nome)}: distribuição</h2><span class="sub">${esc(refFmt(i.ref))}</span></div><div class="card-body">
      ${chart(top.map(m => [m.nome.length > 12 ? m.nome.slice(0, 11) + "…" : m.nome, i.municipios[m.cod]]).slice(0, 20), { tipo: "bar", u: i.unidade })}
      <p class="note" style="margin-top:10px">Os 20 maiores valores entre ${vals.length} municípios com dado. Mediana: <b>${fmt(mediana(vals), i.unidade)}</b>; amplitude: ${fmt(Math.min(...vals), i.unidade)} a ${fmt(Math.max(...vals), i.unidade)}.</p></div></div>`;
  }

  function cardSetores() {
    const i = IND.va_setores; if (!i?.composicao) return "";
    const ent = Object.entries(i.composicao).filter(([, v]) => v != null), tot = ent.reduce((s, [, v]) => s + v, 0);
    const cores = ["var(--s1)", "var(--s2)", "var(--s3)", "var(--s4)"];
    return `<div class="grid"><div class="card c12"><div class="card-head"><h2>Valor adicionado por setor</h2><span class="sub">${esc(refFmt(i.ref))} · ${esc(i.fonte)}</span></div><div class="card-body">
      <div class="track" style="height:18px;border-radius:4px">${ent.map(([k, v], j) => `<span style="width:${v / tot * 100}%;background:${cores[j]}" title="${esc(k)}: ${nf(v / tot * 100, 1)}%"></span>`).join("")}</div>
      <div class="stack-legend" style="margin-top:10px">${ent.map(([k, v], j) => `<span class="legend"><span><i style="background:${cores[j]}"></i>${esc(k)} <b>${nf(v / tot * 100, 1)}%</b> <span class="muted">(${fmt(v, "R$ mil")})</span></span></span>`).join("")}</div></div></div></div>`;
  }

  /* ---------------- composição, pirâmide e perfis */
  const soma = a => a.reduce((s, v) => s + (v || 0), 0);
  const pctf = (v, t) => t ? v / t * 100 : null;
  function barras(lista, { u = "", total = null, limite = 12, cor = "var(--s1)" } = {}) {
    const l = lista.filter(x => x[1] != null).slice(0, limite), max = Math.max(...l.map(x => x[1])) || 1, tot = total ?? soma(l.map(x => x[1]));
    return `<ul class="hbars">${l.map(([k, v]) => `<li><span class="hb-k" title="${esc(k)}">${esc(k)}</span><span class="hb-bar"><i style="width:${v / max * 100}%;background:${cor}"></i></span><span class="hb-v num">${fmt(v, u, true)}${u === "%" ? "" : ` <small class="muted">${nf(pctf(v, tot), 1)}%</small>`}</span></li>`).join("")}</ul>`;
  }
  function piramide(p, rotulos, { titulo = "", comp = null, compNome = "" } = {}) {
    if (!p?.m) return `<div class="empty">Sem pirâmide etária para este recorte.</div>`;
    const tot = soma(p.m) + soma(p.f) || 1, max = Math.max(...p.m, ...p.f) / tot * 100 || 1;
    const linha = (k) => { const hm = p.m[k] / tot * 100, hf = p.f[k] / tot * 100;
      return `<div class="pir-row" title="${esc(rotulos[k])}: homens ${nf(hm, 1)}%, mulheres ${nf(hf, 1)}%"><span class="pir-bar m"><i style="width:${hm / max * 100}%"></i></span><span class="pir-k">${esc(rotulos[k])}</span><span class="pir-bar f"><i style="width:${hf / max * 100}%"></i></span></div>`; };
    return `<div class="pir" role="img" aria-label="Pirâmide etária ${esc(titulo)}"><div class="pir-head"><span>Homens ${nf(soma(p.m) / tot * 100, 1)}%</span><span></span><span>Mulheres ${nf(soma(p.f) / tot * 100, 1)}%</span></div>${rotulos.map((_, k) => linha(rotulos.length - 1 - k)).join("")}</div>`;
  }
  const IDADES = T.idades || [];
  function perfilEleitor(e, { titulo = "" } = {}) {
    if (!e) return `<div class="empty">Nenhum local de votação do TSE fica neste recorte.</div>`;
    const F = T.eleitorado.faixas;
    return `<div class="duo"><div><h3 class="h3">Faixa etária</h3>${barras(F.map((f, k) => [f, e.faixas[k]]), { total: e.eleitores, limite: 10, cor: "var(--s2)" })}</div>
      <div><h3 class="h3">Escolaridade declarada</h3>${barras(Object.entries(e.escolaridade), { total: e.eleitores, limite: 10, cor: "var(--s3)" })}</div></div>
      <p class="note">${nf(e.eleitores)} eleitores · ${nf(e.pct_mulheres, 1)}% mulheres · biometria ${nf(e.pct_biometria, 1)}%. Cor ou raça informada por só ${nf(e.pct_cor_informada, 0)}% do eleitorado, por isso não é comparada ao Censo.</p>`;
  }

  /* ---------------- mapa com camadas (pontos e linhas georreferenciados) */
  const COR_CAM = { rod_federais: "#1c5fbf", rod_estaduais: "#c98a3d", ramais: "#8a6d3b", hidrovias: "#3a8fd6", obras_dnit: "#c0392b",
    flutuantes: "#0f7b6c", ip4: "#3a8fd6", portos: "#1c3f73", aerodromos: "#5b3fa0", aerodromos_priv: "#9a86c7", transposicao: "#8a6d3b",
    saude: "#2e7d32", hospitais: "#c0392b", seguranca: "#1c3f73", locais_votacao: "#5b3fa0",
    usinas: "#c0392b", erbs: "#5b3fa0", dutos: "#c98a3d", escolas: "#1c5fbf" };
  function mapaCamadas(ids, { cod = null, base = null, ligadas = null } = {}) {
    const lig = new Set(ligadas || ids);
    const cams = ids.map(k => [k, CAM.pontos[k] ? "p" : "l", CAM.pontos[k] || CAM.linhas[k]]).filter(x => x[2]?.itens?.length);
    if (!cams.length) return `<div class="empty">Camadas não carregadas. Rode o pipeline p05.</div>`;
    let vb = `0 0 ${GEO.w} ${GEO.h}`, alvo = cod ? GEO.municipios.find(m => m.cod === cod) : null;
    if (alvo) { const n = alvo.d.match(/-?\d+(\.\d+)?/g).map(Number), xs = n.filter((_, i) => !(i % 2)), ys = n.filter((_, i) => i % 2);
      const x0 = Math.min(...xs), y0 = Math.min(...ys), w = Math.max(...xs) - x0, h = Math.max(...ys) - y0, p = Math.max(w, h) * .08;
      vb = `${x0 - p} ${y0 - p} ${w + 2 * p} ${h + 2 * p}`; }
    const esc0 = alvo ? Math.max(.25, Math.min(1, Math.max(...vb.split(" ").slice(2).map(Number)) / GEO.w)) : 1;
    const fundo = GEO.municipios.map(m => `<path d="${m.d}" class="cm-base${m.cod === cod ? " alvo" : ""}"${base ? ` style="fill:${base(m.cod) || "#f4f6f5"}"` : ""} data-cod="${m.cod}"/>`).join("");
    const camadas = cams.map(([k, t, c]) => `<g data-cam="${k}" ${lig.has(k) ? "" : 'style="display:none"'}>${t === "l"
      ? c.itens.filter(i => i.d).map((i, j) => `<path class="cm-l" d="${i.d}" style="stroke:${COR_CAM[k] || "#555"};stroke-width:${(k === "ramais" ? 1 : k === "obras_dnit" ? 3 : 1.8) * esc0}px" data-i="${j}"/>`).join("")
      : c.itens.filter(i => i.x != null && (!cod || i.mun === cod)).map((i, j) => `<circle class="cm-p" cx="${i.x}" cy="${i.y}" r="${3.2 * esc0}" style="fill:${COR_CAM[k] || "#555"};stroke-width:${esc0}px" data-i="${c.itens.indexOf(i)}"/>`).join("")}</g>`).join("");
    const id = "cm" + Math.random().toString(36).slice(2, 8);
    queueMicrotask(() => {
      const el = document.getElementById(id); if (!el) return;
      el.addEventListener("change", e => { const k = e.target.dataset?.tog; if (k) el.querySelector(`g[data-cam="${k}"]`).style.display = e.target.checked ? "" : "none"; });
      el.addEventListener("mousemove", e => {
        const g = e.target.closest?.("g[data-cam]"), i = e.target.dataset?.i;
        if (!g || i == null) { const c = e.target.dataset?.cod; return c ? showTip(`<b>${esc(MUN[c]?.nome)}</b>`, e) : hideTip(); }
        const k = g.dataset.cam, it = (CAM.pontos[k] || CAM.linhas[k]).itens[+i];
        const campos = Object.entries(it).filter(([f, v]) => v != null && v !== "" && !["x", "y", "lat", "lon", "d", "mun", "nome", "rodovia", "bairro"].includes(f) && typeof v !== "object").slice(0, 6);
        showTip(`<b>${esc(it.nome || it.rodovia || "")}</b>${it.mun && MUN[it.mun] ? ` · ${esc(MUN[it.mun].nome)}` : ""}<br>${campos.map(([f, v]) => `<span class="t-sub">${esc(f)}:</span> ${esc(typeof v === "number" ? nf(v, Number.isInteger(v) ? 0 : 1) : v)}`).join("<br>")}<br><span class="t-sub">${esc((CAM.pontos[k] || CAM.linhas[k]).nome)}</span>`, e);
      });
      el.addEventListener("mouseleave", hideTip);
      el.addEventListener("click", e => { const c = e.target.dataset?.cod; if (c && !cod) location.hash = `#/municipios/${c}`; });
    });
    const legenda = cams.map(([k, t, c]) => `<label class="tog"><input type="checkbox" data-tog="${k}"${lig.has(k) ? " checked" : ""}><i class="${t === "l" ? "ln" : "pt"}" style="--c:${COR_CAM[k] || "#555"}"></i>${esc(c.nome)} <span class="muted">(${nf(t === "p" && cod ? c.itens.filter(i => i.mun === cod).length : c.itens.length)})</span></label>`).join("");
    return `<div class="cmap" id="${id}"><svg viewBox="${vb}" role="img" aria-label="Mapa de equipamentos e infraestrutura">${fundo}${camadas}</svg><div class="toggles">${legenda}</div>
      <p class="note">Fontes: ${[...new Set(cams.map(([, , c]) => c.fonte))].map(esc).join("; ")}.</p></div>`;
  }

  /* ---------------- blocos específicos de cada área */
  function ladoArea(a) {
    if (a.id === "eleitorado" && T.eleitorado) return `<div class="card c4"><div class="card-head"><h2>Escolaridade do eleitorado</h2><span class="sub">TSE 2026</span></div><div class="card-body">${barras(Object.entries(T.eleitorado.estado.escolaridade), { total: T.eleitorado.estado.eleitores, cor: "var(--s3)" })}</div></div>`;
    return a.ppa ? cardPPA(a.ppa, "Metas do PPA nesta área") : "";
  }
  function principalArea(a) {
    if (a.id === "demografia" && T.estado?.piramide) return `<div class="card c8"><div class="card-head"><h2>Pirâmide etária e cor ou raça</h2><span class="sub">Censo 2022 · soma dos 62 municípios</span></div><div class="card-body duo">
      <div>${piramide(T.estado.piramide, IDADES)}</div><div><h3 class="h3">Cor ou raça</h3>${barras(Object.entries(T.estado.cor).sort((x, y) => y[1] - x[1]), { cor: "var(--s2)" })}
      <h3 class="h3" style="margin-top:14px">Povos e comunidades</h3>${barras([["Indígenas", IND.pct_indigena?.estado], ["Quilombolas", IND.pct_quilombola?.estado]], { u: "%", cor: "var(--s4)" })}</div></div></div>`;
    if (a.id === "eleitorado" && T.eleitorado) return `<div class="card c8"><div class="card-head"><h2>Perfil do eleitorado do Amazonas</h2><span class="sub">${esc(T.eleitorado.fonte)}</span></div><div class="card-body">${perfilEleitor(T.eleitorado.estado)}</div></div>`;
    if (a.id === "saneamento" && T.estado?.esgoto) return `<div class="card c8"><div class="card-head"><h2>Destino do esgoto e do lixo nos domicílios</h2><span class="sub">Censo 2022 · soma dos 62 municípios</span></div><div class="card-body duo">
      <div><h3 class="h3">Esgoto</h3>${barras(Object.entries(T.estado.esgoto).sort((x, y) => y[1] - x[1]), { cor: "var(--s1)" })}</div><div><h3 class="h3">Lixo</h3>${barras(Object.entries(T.estado.lixo).sort((x, y) => y[1] - x[1]), { cor: "var(--s2)" })}</div></div></div>`;
    if (a.id === "rural" && T.rural) {
      const tot = k => { const s = {}; Object.values(T.rural).forEach(r => (r[k] || []).forEach(([p, v]) => { s[p] = (s[p] || 0) + v; })); return Object.entries(s).sort((x, y) => y[1] - x[1]); };
      return `<div class="card c8"><div class="card-head"><h2>Principais produtos do estado</h2><span class="sub">IBGE · PAM e PEVS (valor, R$ mil) · ${esc(IND.pam_valor?.ref || "")}</span></div><div class="card-body duo">
        <div><h3 class="h3">Lavouras</h3>${barras(tot("pam_valor"), { u: "R$ mil", limite: 10, cor: "var(--s2)" })}</div><div><h3 class="h3">Extrativismo vegetal</h3>${barras(tot("pevs_valor"), { u: "R$ mil", limite: 10, cor: "var(--s3)" })}</div></div>
        <div class="card-foot">Rebanhos (cabeças): ${tot("rebanhos").slice(0, 5).map(([k, v]) => `${esc(k)} ${nf(v)}`).join(" · ")}</div></div>`;
    }
    if (a.id === "transporte") return `<div class="card c8"><div class="card-head"><h2>Rede de transporte</h2><span class="sub">ligue e desligue as camadas</span></div><div class="card-body">${mapaCamadas(["hidrovias", "rod_federais", "rod_estaduais", "ramais", "obras_dnit", "flutuantes", "ip4", "portos", "aerodromos", "aerodromos_priv", "transposicao"], { ligadas: ["hidrovias", "rod_federais", "rod_estaduais", "ramais", "flutuantes", "aerodromos"] })}</div></div>`;
    if (a.id === "energia") return `<div class="card c8"><div class="card-head"><h2>Geração de energia e telecomunicações</h2><span class="sub">ligue e desligue as camadas</span></div><div class="card-body">${mapaCamadas(["usinas", "dutos", "erbs"], { ligadas: ["usinas", "dutos"] })}</div></div>`;
    if (a.id === "saude") return `<div class="card c8"><div class="card-head"><h2>Rede de saúde georreferenciada</h2><span class="sub">CNES</span></div><div class="card-body">${mapaCamadas(["hospitais", "saude"], { ligadas: ["hospitais"] })}</div></div>`;
    if (a.id === "cidades" && T.comunidades?.length) return `<div class="card c8"><div class="card-head"><h2>Maiores favelas e comunidades urbanas</h2><span class="sub">Censo 2022 · ${nf(T.comunidades.length)} no Amazonas</span></div><div class="card-body">${barras([...T.comunidades].sort((x, y) => (y.pop || 0) - (x.pop || 0)).map(c => [`${c.nome} (${MUN[c.mun]?.nome || ""})`, c.pop]), { limite: 14, cor: "var(--s4)" })}</div><div class="card-foot"><a href="#/bairros/1302603">Ver comunidades e bairros no mapa de Manaus</a></div></div>`;
    return a.series.length ? cardSerie(a.series, a.mensal ? "Registros no estado" : "Série histórica do estado", { mensal: a.mensal }) : cardIdeb(a);
  }
  function rodapeArea(a) {
    if (a.id === "economia") return cardSetores();
    if (a.id === "seguranca") return `<div class="grid">${cardSerie(["ssp_homicidios", "ssp_homicidio_taxa", "efetivo_policial"], "Série oficial do estado (SSP-AM)", { col: "c12" })}<div class="card c12"><div class="card-head"><h2>Unidades policiais e de bombeiros</h2><span class="sub">${esc(CAM.pontos.seguranca?.nome || "")}</span></div><div class="card-body">${mapaCamadas(["seguranca"])}</div></div></div>
      <p class="note">Dados de ocorrências agregados por município e mês (SINESP VDE) e por ano (Anuário SSP-AM). O mapa da SSP-AM traz as unidades de Manaus e as sedes da PM no interior; delegacias do interior não estão nele. O painel não mostra localização de ocorrências individuais. A API <a href="https://github.com/rayonnunes/api_seguranca_publica" target="_blank" rel="noopener">rayonnunes/api_seguranca_publica</a> serviu de referência; seu endpoint público não respondeu, então os dados vêm direto do arquivo oficial do MJSP.</p>`;
    if (a.id === "educacao" && T.escolas) {
      const rede = {}; T.escolas.forEach(e => { const r = rede[e.rede] ||= { esc: 0, mat: 0, rur: 0, net: 0 }; r.esc++; r.mat += e.mat; r.rur += e.rural; r.net += e.internet; });
      const ce = CAM.pontos.escolas;
      return `${ce ? `<div class="grid"><div class="card c12"><div class="card-head"><h2>Escolas no mapa</h2><span class="sub">${esc(ce.cobertura || "")}</span></div><div class="card-body">${mapaCamadas(["escolas"])}</div></div></div>` : ""}<div class="grid"><div class="card c6"><div class="card-head"><h2>Escolas e matrículas por rede</h2><span class="sub">INEP · Censo Escolar 2024</span></div><div class="table-wrap" style="max-height:none"><table><thead><tr><th>Rede</th><th class="n">Escolas</th><th class="n">Matrículas</th><th class="n">Rurais</th><th class="n">Com internet</th></tr></thead><tbody>
        ${Object.entries(rede).sort((x, y) => y[1].mat - x[1].mat).map(([k, r]) => `<tr><td>${esc(k)}</td><td class="n">${nf(r.esc)}</td><td class="n">${nf(r.mat)}</td><td class="n">${nf(pctf(r.rur, r.esc), 0)}%</td><td class="n">${nf(pctf(r.net, r.esc), 0)}%</td></tr>`).join("")}</tbody></table></div></div>
        <div class="card c6"><div class="card-head"><h2>Ensino superior presencial</h2><span class="sub">INEP · Censo da Educação Superior 2023</span></div><div class="table-wrap" style="max-height:340px"><table><thead><tr><th>Instituição</th><th>Rede</th><th class="n">Matrículas</th><th class="n">Municípios</th></tr></thead><tbody>
        ${(T.ies || []).filter(x => x.mat).map(x => `<tr><td>${esc(x.sigla || x.nome)}<div class="muted" style="font-size:12px">${esc(x.nome)}</div></td><td class="muted">${esc(x.rede)}</td><td class="n">${nf(x.mat)}</td><td class="n" title="${esc(x.municipios.map(c => MUN[c]?.nome).join(", "))}">${x.municipios.length}</td></tr>`).join("")}</tbody></table></div></div></div>`;
    }
    if (a.id === "transporte") {
      const ob = CAM.linhas.obras_dnit?.itens || [], ram = {};
      (CAM.linhas.ramais?.itens || []).forEach(r => { if (!r.mun) return; const x = ram[r.mun] ||= { n: 0, km: 0, custo: 0, natural: 0 }; x.n++; x.km += r.km || 0; x.custo += r.custo || 0; x.natural += /NATURAL/i.test(r.revestimento || "") ? r.km || 0 : 0; });
      return `<div class="grid"><div class="card c7"><div class="card-head"><h2>Ramais por município</h2><span class="sub">SEINFRA 2025</span></div><div class="table-wrap" style="max-height:420px"><table><thead><tr><th>Município</th><th class="n">Ramais</th><th class="n">km</th><th class="n">Leito natural</th><th class="n">Custo estimado</th></tr></thead><tbody>
        ${Object.entries(ram).sort((x, y) => y[1].km - x[1].km).map(([c, r]) => `<tr class="click" tabindex="0" onclick="location.hash='#/municipios/${c}'"><td>${esc(MUN[c]?.nome)}</td><td class="n">${nf(r.n)}</td><td class="n">${nf(r.km, 1)}</td><td class="n">${nf(pctf(r.natural, r.km), 0)}%</td><td class="n">R$ ${nf(r.custo / 1e6, 1)} mi</td></tr>`).join("")}</tbody></table></div></div>
        <div class="card c5"><div class="card-head"><h2>Obras diretas do DNIT no AM</h2></div><div class="card-body">${ob.length ? `<ul class="list">${ob.map(o => `<li><div class="l-main"><div class="l-title">${esc(o.rodovia)} — ${esc(o.objeto)}</div><div class="l-sub">${esc(o.empresa)} · ${nf(o.km, 1)} km · R$ ${nf((o.valor || 0) / 1e6, 1)} mi · ${esc(dataBR(o.inicio))} a ${esc(dataBR(o.termino))}</div></div></li>`).join("")}</ul>` : '<div class="empty">Nenhuma obra direta listada.</div>'}</div><div class="card-foot">Fonte: DNIT, GeoServer vgeo (WFS).</div></div></div>`;
    }
    if (a.id === "energia" && CAM.pontos.usinas) {
      const u = CAM.pontos.usinas.itens;
      return `<div class="grid"><div class="card c12"><div class="card-head"><h2>Usinas de geração no Amazonas</h2><span class="sub">${nf(u.length)} usinas · ${esc(CAM.pontos.usinas.fonte)}</span></div><div class="table-wrap" style="max-height:420px"><table><thead><tr><th>Usina</th><th>Município</th><th>Tipo</th><th>Combustível</th><th>Fase</th><th class="n">Potência (MW)</th><th>Início da operação</th></tr></thead><tbody>
        ${u.map(x => `<tr><td>${esc(x.nome)}</td><td>${esc(MUN[x.mun]?.nome || "")}</td><td class="muted">${esc(x.tipo)}</td><td class="muted">${esc(x.combustivel || "")}</td><td class="muted">${esc(x.fase)}</td><td class="n">${nf(x.potencia_mw, x.potencia_mw < 10 ? 2 : 1)}</td><td>${esc(dataBR(x.inicio))}</td></tr>`).join("")}</tbody></table></div></div></div>`;
    }
    if (a.id === "saude" && CAM.pontos.hospitais) {
      const h = [...CAM.pontos.hospitais.itens, ...(CAM.pontos.hospitais.sem_coordenada || [])].sort((x, y) => (y.leitos || 0) - (x.leitos || 0));
      return `<div class="grid"><div class="card c12"><div class="card-head"><h2>Hospitais e leitos</h2><span class="sub">${nf(h.length)} hospitais · ${esc(CAM.pontos.hospitais.fonte)}</span></div><div class="table-wrap" style="max-height:420px"><table><thead><tr><th>Hospital</th><th>Município</th><th>Natureza</th><th class="n">Leitos</th><th class="n">SUS</th><th class="n">UTI</th><th class="n">UTI SUS</th></tr></thead><tbody>
        ${h.map(x => `<tr><td>${esc(x.nome)}</td><td>${esc(MUN[x.mun]?.nome || "")}</td><td class="muted">${esc(x.natureza)}</td><td class="n">${nf(x.leitos)}</td><td class="n">${nf(x.leitos_sus)}</td><td class="n">${nf(x.uti)}</td><td class="n">${nf(x.uti_sus)}</td></tr>`).join("")}</tbody></table></div></div></div>`;
    }
    if (a.id === "eleitorado" && T.eleitorado) {
      const E = T.eleitorado.municipios;
      const jov = c => { const p = T.municipios?.[c]?.piramide; return p ? pctf(p.m[3] + p.m[4] + p.f[3] + p.f[4], soma(p.m) + soma(p.f)) : null; };
      const linhas = P.municipios.filter(m => E[m.cod]).map(m => { const e = E[m.cod], d = T.municipios?.[m.cod] || {};
        return `<tr class="click" tabindex="0" onclick="location.hash='#/municipios/${m.cod}'"><td>${esc(m.nome)}</td><td class="n">${nf(d.pop)}</td><td class="n">${nf(e.eleitores)}</td><td class="n">${nf(IND.eleit_pop?.municipios[m.cod], 1)}</td><td class="n">${nf(e.pct_jovens, 1)}%</td><td class="n">${nf(jov(m.cod), 1)}%</td><td class="n">${nf(e.pct_idosos, 1)}%</td><td class="n">${nf(d.pct_60, 1)}%</td><td class="n">${nf(e.pct_sem_fundamental, 1)}%</td><td class="n">${nf(d.alfabetizacao, 1)}%</td><td class="n">${fmt(d.renda_media, "R$")}</td></tr>`; }).join("");
      return `<div class="grid"><div class="card c12"><div class="card-head"><h2>Eleitorado × Censo, por município</h2><span class="sub">TSE 2026 e IBGE Censo 2022</span></div><div class="table-wrap" style="max-height:520px"><table class="sortable"><thead><tr><th>Município</th><th class="n">População (Censo)</th><th class="n">Eleitores</th><th class="n">Eleitores / 100 hab.</th><th class="n">Eleitores 16–24</th><th class="n">População 15–24</th><th class="n">Eleitores 60+</th><th class="n">População 60+</th><th class="n">Eleitores sem fundamental</th><th class="n">Alfabetização 15+</th><th class="n">Renda média resp.</th></tr></thead><tbody>${linhas}</tbody></table></div>
        <div class="card-foot">Eleitores votam onde têm domicílio eleitoral, que pode diferir da residência; por isso a razão eleitores/habitantes passa de 100 em alguns municípios. Faixas do TSE (16–24) e do Censo (15–24) não coincidem exatamente.</div></div></div>`;
    }
    return "";
  }

  /* ---------------- bairros e comunidades */
  const IND_BAIRRO = [["pop", "População (Censo 2022)", "pessoas"], ["densidade", "Densidade", "hab/km²"], ["renda_media", "Rendimento médio do responsável", "R$"],
    ["alfabetizacao", "Alfabetização 15+", "%"], ["pct_0_14", "População 0–14 anos", "%"], ["pct_60", "População 60+", "%"], ["pct_indigena", "População indígena", "%"],
    ["agua_rede", "Água pela rede geral", "%"], ["esgoto_rede", "Esgoto em rede geral", "%"], ["esgoto_precario", "Esgoto precário", "%"], ["lixo_coletado", "Lixo coletado", "%"],
    ["eleitores", "Eleitores (TSE, pelo local de votação)", "eleitores"], ["eleit_jovens", "Eleitores 16–24", "%"], ["eleit_superior", "Eleitores com superior completo", "%"], ["eleit_sem_fund", "Eleitores sem fundamental", "%"]];
  function valBairro(b, k) {
    const e = T.eleitorado?.bairros?.[b.cod];
    if (k === "eleitores") return e?.eleitores ?? null;
    if (k === "eleit_jovens") return e?.pct_jovens ?? null;
    if (k === "eleit_superior") return e?.pct_superior ?? null;
    if (k === "eleit_sem_fund") return e?.pct_sem_fundamental ?? null;
    return b[k] ?? null;
  }
  function bairros(cod) {
    const comB = [...new Set((T.bairros || []).map(b => b.mun))];
    if (!comB.length) return cabecalho("Bairros e comunidades", "Rode o pipeline p05 para gerar dados/territorio.js.");
    cod = comB.includes(cod) ? cod : "1302603";
    const lista = T.bairros.filter(b => b.mun === cod), mold = T.molduras[cod], fcu = (T.comunidades || []).filter(c => c.mun === cod);
    let ind = "renda_media", sel = null, verFcu = true;
    const id = "bx" + Math.random().toString(36).slice(2, 8);
    const corpo = () => {
      const [k, nome, u] = IND_BAIRRO.find(x => x[0] === ind), vals = lista.map(b => valBairro(b, k)), br = classes(vals);
      const cor = v => v == null ? null : SEQ[Math.min(SEQ.length - 1, br.filter(b => v >= b).length + (br.length < 5 ? 1 : 0))];
      const paths = lista.map(b => { const c = cor(valBairro(b, k)); return `<path d="${b.d}" data-b="${b.cod}" class="${c ? "" : "nodata"}${b.cod === sel ? " on" : ""}" ${c ? `style="fill:${c}"` : ""}/>`; }).join("");
      const fc = verFcu ? fcu.filter(c => c.d).map(c => `<path class="fcu" d="${c.d}" data-f="${c.cod}"/>`).join("") : "";
      const lims = [Math.min(...vals.filter(v => v != null)), ...br];
      const leg = lims.map((b, j) => `<span><i style="background:${cor(b)}"></i>${j === lims.length - 1 ? "≥ " : ""}${fmt(b, u, true)}${j < lims.length - 1 ? "–" + fmt(lims[j + 1], u, true) : ""}</span>`).join("") + (vals.some(v => v == null) ? `<span><i class="nd"></i>sem dado</span>` : "") + (verFcu && fcu.length ? `<span><i class="fcu-i"></i>favela ou comunidade urbana</span>` : "");
      const ord = [...lista].sort((x, y) => (valBairro(y, k) ?? -1e15) - (valBairro(x, k) ?? -1e15));
      const b = lista.find(x => x.cod === sel), e = b && T.eleitorado?.bairros?.[b.cod];
      const det = b ? `<div class="card c12"><div class="card-head"><h2>${esc(b.nome)}</h2><span class="sub">${esc(MUN[cod].nome)} · Censo 2022 e TSE 2026</span></div><div class="card-body">
          <div class="counters">${[["População", nf(b.pop)], ["Domicílios", nf(b.domicilios)], ["Renda média resp.", fmt(b.renda_media, "R$")], ["Alfabetização 15+", `${nf(b.alfabetizacao, 1)}%`], ["Esgoto em rede", `${nf(b.esgoto_rede, 1)}%`], ["Eleitores (locais no bairro)", nf(e?.eleitores)]].map(([x, y]) => `<div><span>${x}</span><b>${y}</b></div>`).join("")}</div>
          <div class="duo"><div><h3 class="h3">Pirâmide etária (Censo)</h3>${piramide(b.piramide, IDADES)}</div><div><h3 class="h3">Eleitorado votando no bairro (TSE)</h3>${perfilEleitor(e)}</div></div>
          ${fcu.filter(c => c.bairros.includes(b.cod)).length ? `<h3 class="h3">Favelas e comunidades urbanas no bairro</h3>${barras(fcu.filter(c => c.bairros.includes(b.cod)).map(c => [c.nome, c.pop]), { cor: "var(--s4)" })}` : ""}
          <p class="note">Eleitores são contados pelo local de votação dentro do bairro; quem vota ali pode morar em outro bairro.</p></div></div>` : "";
      return `<div class="card c7"><div class="card-head"><h2>Mapa de bairros</h2><div class="filters"><select class="sel" data-ind aria-label="Indicador">${IND_BAIRRO.map(([x, n]) => `<option value="${x}"${x === ind ? " selected" : ""}>${esc(n)}</option>`).join("")}</select>${fcu.length ? `<label class="tog"><input type="checkbox" data-fcu${verFcu ? " checked" : ""}>Comunidades</label>` : ""}</div></div>
          <div class="card-body"><div class="map bmap"><svg viewBox="0 0 ${mold.w} ${mold.h}" role="img" aria-label="Bairros de ${esc(MUN[cod].nome)}: ${esc(nome)}"><defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="5" height="5" fill="#fff"/><line x1="0" y1="0" x2="0" y2="5" stroke="var(--nodata)" stroke-width="2"/></pattern></defs>${paths}${fc}</svg></div><div class="legend">${leg}</div></div>
          <div class="card-foot">IBGE, malha de bairros do Censo 2022 · classes por quantis. Clique num bairro para ver o perfil.</div></div>
        <div class="card c5"><div class="card-head"><h2>${lista.length} bairros</h2><span class="sub">${esc(nome)}</span></div><div class="table-wrap" style="max-height:560px"><table><thead><tr><th>Bairro</th><th class="n">${esc(nome)}</th><th class="n">População</th></tr></thead><tbody>
          ${ord.map(x => `<tr class="click${x.cod === sel ? " sel" : ""}" tabindex="0" data-b="${x.cod}"><td>${esc(x.nome)}</td><td class="n">${fmt(valBairro(x, k), u)}</td><td class="n">${nf(x.pop)}</td></tr>`).join("")}</tbody></table></div></div>${det}`;
    };
    queueMicrotask(() => {
      const el = document.getElementById(id); if (!el) return;
      const go = c => { sel = sel === c ? null : c; el.innerHTML = corpo(); if (sel) el.querySelector(".c12")?.scrollIntoView({ behavior: "smooth", block: "start" }); };
      el.addEventListener("change", e => { if (e.target.matches("[data-ind]")) ind = e.target.value; if (e.target.matches("[data-fcu]")) verFcu = e.target.checked; el.innerHTML = corpo(); });
      el.addEventListener("click", e => { const c = e.target.closest?.("[data-b]")?.dataset.b; if (c) go(c); });
      el.addEventListener("keydown", e => { const c = e.target.closest?.("tr[data-b]")?.dataset.b; if (c && e.key === "Enter") go(c); });
      el.addEventListener("mousemove", e => {
        const f = e.target.dataset?.f, c = e.target.dataset?.b;
        if (f) { const x = fcu.find(z => z.cod === f); return showTip(`<b>${esc(x.nome)}</b><br>${nf(x.pop)} pessoas · ${nf(x.dom)} domicílios<br><span class="t-sub">Favela ou comunidade urbana (IBGE 2022)</span>`, e); }
        if (!c) return hideTip();
        const b = lista.find(z => z.cod === c), [k, nome, u] = IND_BAIRRO.find(x => x[0] === ind);
        showTip(`<b>${esc(b.nome)}</b><br>${fmt(valBairro(b, k), u)} ${esc(unidadeCurta(u))}<br><span class="t-sub">${esc(nome)}</span>`, e);
      });
      el.addEventListener("mouseleave", hideTip);
      el.addEventListener("mouseover", e => { if (e.target.dataset?.b && e.target.tagName === "path") e.target.parentNode.insertBefore(e.target, e.target.parentNode.querySelector(".fcu")); });
    });
    const opc = comB.map(c => MUN[c]).filter(Boolean).sort((x, y) => x.nome.localeCompare(y.nome));
    return cabecalho("Bairros e comunidades", `Indicadores do Censo 2022 por bairro, favelas e comunidades urbanas e o perfil do eleitorado de 2026 pelos locais de votação de cada bairro. ${opc.length} municípios têm malha de bairros no IBGE.`, `<a href="#/visao">Visão geral</a> / Bairros`)
      + `<div class="filters" style="margin-bottom:16px"><label class="muted" for="bx-mun">Município</label><select class="sel" id="bx-mun" onchange="location.hash='#/bairros/'+this.value">${opc.map(m => `<option value="${m.cod}"${m.cod === cod ? " selected" : ""}>${esc(m.nome)} (${T.bairros.filter(b => b.mun === m.cod).length})</option>`).join("")}</select></div>`
      + `<div class="grid" id="${id}">${corpo()}</div>`
      + (fcu.length ? `<div class="grid"><div class="card c12"><div class="card-head"><h2>Favelas e comunidades urbanas em ${esc(MUN[cod].nome)}</h2><span class="sub">${fcu.length} · IBGE Censo 2022</span></div><div class="table-wrap" style="max-height:420px"><table><thead><tr><th>Comunidade</th><th>Bairros</th><th class="n">População</th><th class="n">Domicílios</th></tr></thead><tbody>
        ${[...fcu].sort((x, y) => (y.pop || 0) - (x.pop || 0)).map(c => `<tr><td>${esc(c.nome)}</td><td class="muted">${esc(c.bairros.map(x => T.bairros.find(b => b.cod === x)?.nome).filter(Boolean).join(", "))}</td><td class="n">${nf(c.pop)}</td><td class="n">${nf(c.dom)}</td></tr>`).join("")}</tbody></table></div></div></div>` : "");
  }

  function ppaPagina() {
    if (!PPA) return cabecalho("PPA 2024–2027", "dados/ppa.js não encontrado. Rode os scripts p01–p03.");
    const anos = [...new Set(OBS_PPA.map(o => +o.data_referencia.slice(0, 4)))].sort();
    let f = { ano: ultimoExercicio(), area: "", st: "", q: "" };
    const linhas = () => OBS_PPA.filter(o => +o.data_referencia.slice(0, 4) === f.ano && (!f.area || PROG[o.ind.program_id]?.area_resultado_id === f.area) && (!f.st || o.status === f.st)
      && (!f.q || (o.ind.nome + " " + (PROG[o.ind.program_id]?.nome || "")).toLowerCase().includes(f.q.toLowerCase())));
    const tabela = () => { const l = linhas(); return `${trilha(contagemStatus(l))}${legendaStatus(contagemStatus(l))}<div class="table-wrap" style="margin-top:12px;max-height:640px"><table><thead><tr><th>Indicador</th><th>Programa</th><th class="n">Meta</th><th class="n">Apurado</th><th>Unid.</th><th>Polaridade</th><th>Situação</th><th>Fonte</th></tr></thead><tbody>${l.map(o => `<tr><td>${esc(o.ind.nome)}${o.status_qualidade !== "extraido_documento" ? ' <span class="tag calc" title="Extração conferida por OCR com divergência; aguarda validação humana">em validação</span>' : ""}</td><td class="muted">${esc(o.ind.program_id)} · ${esc(PROG[o.ind.program_id]?.nome || "")}</td><td class="n">${fmt(o.meta, o.unidade)}</td><td class="n">${fmt(o.valor, o.unidade)}</td><td class="muted">${esc(o.unidade || "")}</td><td class="muted" style="white-space:nowrap">${o.ind.polaridade === "menor_melhor" ? "menor é melhor" : "maior é melhor"}${o.ind.polaridade_origem === "inferida" ? "*" : ""}</td><td>${status(o.status)}</td><td>${linkPDF(o)}</td></tr>`).join("") || `<tr><td colspan="8" class="empty">Nenhum indicador com esses filtros.</td></tr>`}</tbody></table></div>`; };
    queueMicrotask(() => {
      const box = $("#ppa-box"), fl = $("#ppa-f");
      fl.addEventListener("input", e => { const t = e.target; f[t.name] = t.name === "ano" ? +t.value : t.value; box.innerHTML = tabela(); });
    });
    return cabecalho("PPA 2024–2027", "Metas e valores apurados extraídos dos Relatórios Anuais de Avaliação, página a página. O status é recalculado pela polaridade de cada indicador.", `<a href="#/visao">Visão geral</a> / PPA`)
      + `<div class="grid"><div class="card c12"><div class="card-head"><h2>Indicadores de resultado</h2><div class="filters" id="ppa-f">
        <select class="sel" name="ano" aria-label="Exercício">${anos.map(a => `<option${a === f.ano ? " selected" : ""}>${a}</option>`).join("")}</select>
        <select class="sel" name="area" aria-label="Área de resultado"><option value="">Todas as áreas</option>${PPA.areas.map(a => `<option value="${a.id}">${esc(a.nome)}</option>`).join("")}</select>
        <select class="sel" name="st" aria-label="Situação"><option value="">Todas as situações</option>${Object.keys(ST).map(k => `<option value="${k}">${ST[k][2]}</option>`).join("")}</select>
        <input type="search" name="q" placeholder="Buscar indicador ou programa" aria-label="Buscar indicador"></div></div>
        <div class="card-body" id="ppa-box">${tabela()}</div><div class="card-foot">* polaridade inferida pelo nome do indicador; precisa de validação humana. Valores conferidos contra o PDF (link “p.” abre a página).</div></div></div>`;
  }

  function municipio(cod) {
    const m = MUN[cod];
    if (!m) return cabecalho("Município não encontrado", `Código ${esc(cod)} não está entre os 62 municípios do Amazonas.`);
    const grupos = AREAS.filter(a => a.id).map(a => ({ a, ids: [...new Set([...a.kpis, ...a.mapa])].filter(id => IND[id] && Object.keys(IND[id].municipios).length) })).filter(g => g.ids.length);
    const rank = id => { const v = IND[id].municipios[cod]; if (v == null) return ""; const s = Object.values(IND[id].municipios).filter(x => x != null).sort((a, b) => b - a); return `<span class="nw">${s.indexOf(v) + 1}º de ${s.length}</span>`; };
    const series = ["desmatamento", "focos", "ideb_in", "ideb_fi"].filter(id => IND[id]?.serie_municipal?.[cod]);
    const chave = ["pop_estimada", "eleitores", "pib_pc", "ifdm", "renda_media", "cvli_taxa", "leitos_sus_hab", "matriculas"].filter(id => IND[id] && IND[id].municipios[cod] != null);
    return cabecalho(m.nome, `Código IBGE ${cod}. Valores do município, do estado (quando publicado) e posição entre os 62 municípios (ordem decrescente, sem juízo de valor).`, `<a href="#/municipios">Municípios</a> / ${esc(m.nome)}`)
      + `<div class="grid"><div class="card c12"><div class="card-body"><div class="counters">${chave.map(id => `<div><span>${esc(IND[id].nome.replace(/ \(.*\)| \d{4}/g, ""))}</span><b>${fmt(IND[id].municipios[cod], IND[id].unidade)}</b><small class="muted">${rank(id)} · ${esc(refFmt(IND[id].ref))}</small></div>`).join("")}</div></div></div></div>`
      + fichaExtras(cod)
      + `<div class="grid"><div class="card c12"><div class="card-head"><h2>Todos os indicadores por área</h2><span class="sub">${nf(grupos.reduce((s, g) => s + g.ids.length, 0))} indicadores</span></div><div class="card-body">
        ${grupos.map((g, j) => `<details class="grp"${j < 2 ? " open" : ""}><summary>${ico(g.a.icon)}${esc(g.a.nome)} <span class="muted">(${g.ids.length})</span></summary><div class="table-wrap" style="max-height:none"><table><thead><tr><th>Indicador</th><th class="n">${esc(m.nome)}</th><th class="n">Amazonas</th><th>Posição</th><th>Ref.</th></tr></thead><tbody>
        ${g.ids.map(id => { const i = IND[id], e = valorEstado(i); return `<tr><td>${esc(i.nome)}</td><td class="n"><b>${fmt(i.municipios[cod], i.unidade)}</b></td><td class="n">${fmt(e.v, i.unidade)}${e.obs ? ' <span class="muted">(mediana)</span>' : ""}</td><td class="muted">${rank(id)}</td><td class="muted">${esc(refFmt(i.ref))}</td></tr>`; }).join("")}</tbody></table></div></details>`).join("")}</div></div></div>`
      + (series.length ? `<div class="grid">${series.map(id => `<div class="card c6"><div class="card-head"><h2>${esc(IND[id].nome.replace(/ \d{4}| \(.*\)/g, ""))}</h2><span class="sub">${esc(IND[id].fonte.split(" — ")[0])}</span></div><div class="card-body">${chart(IND[id].serie_municipal[cod], { tipo: id.startsWith("ideb") ? "line" : "bar", u: IND[id].unidade, h: 240, w: 520, parcialDe: id.startsWith("ideb") ? null : String(new Date().getFullYear()) })}</div></div>`).join("")}</div>` : "");
  }

  function fichaExtras(cod) {
    const d = T.municipios?.[cod], e = T.eleitorado?.municipios?.[cod], r = T.rural?.[cod];
    const esc_ = (T.escolas || []).filter(x => x.mun === cod), rede = {};
    esc_.forEach(x => { const z = rede[x.rede] ||= [0, 0]; z[0]++; z[1] += x.mat; });
    const cont = k => (CAM.pontos[k]?.itens || []).filter(i => i.mun === cod).length;
    const temB = (T.bairros || []).some(b => b.mun === cod);
    const fcu = (T.comunidades || []).filter(c => c.mun === cod);
    const equip = [["Escolas", esc_.length], ["Estabelecimentos de saúde (CNES)", cont("saude")], ["Hospitais", (CAM.pontos.hospitais ? [...CAM.pontos.hospitais.itens, ...(CAM.pontos.hospitais.sem_coordenada || [])] : []).filter(h => h.mun === cod).length],
      ["Unidades policiais e bombeiros (OSM)", cont("seguranca")], ["Locais de votação", cont("locais_votacao")], ["Terminais flutuantes", cont("flutuantes")], ["Instalações IP4", cont("ip4")],
      ["Aeródromos públicos", cont("aerodromos")], ["Portos do SNV", cont("portos")], ["Favelas e comunidades urbanas", fcu.length]];
    return `<div class="grid">
      ${d ? `<div class="card c6"><div class="card-head"><h2>Pirâmide etária</h2><span class="sub">Censo 2022</span></div><div class="card-body">${piramide(d.piramide, IDADES)}<h3 class="h3" style="margin-top:12px">Cor ou raça</h3>${barras(Object.entries(d.cor || {}).sort((x, y) => y[1] - x[1]), { cor: "var(--s2)" })}</div></div>` : ""}
      ${e ? `<div class="card c6"><div class="card-head"><h2>Eleitorado</h2><span class="sub">TSE 2026</span></div><div class="card-body">${perfilEleitor(e)}</div></div>` : ""}
      <div class="card c6"><div class="card-head"><h2>Equipamentos e infraestrutura</h2>${temB ? `<a class="sub" href="#/bairros/${cod}">ver bairros</a>` : ""}</div><div class="card-body">
        <ul class="list kv">${equip.map(([k, v]) => `<li><span>${k}</span><b class="num">${nf(v)}</b></li>`).join("")}</ul>
        ${Object.keys(rede).length ? `<h3 class="h3" style="margin-top:12px">Escolas por rede (matrículas)</h3>${barras(Object.entries(rede).sort((x, y) => y[1][1] - x[1][1]).map(([k, v]) => [`${k} · ${v[0]} escolas`, v[1]]), { cor: "var(--s1)" })}` : ""}</div></div>
      <div class="card c6"><div class="card-head"><h2>Mapa do município</h2><span class="sub">ligue e desligue as camadas</span></div><div class="card-body">${mapaCamadas(["rod_federais", "rod_estaduais", "ramais", "hidrovias", "hospitais", "saude", "seguranca", "escolas", "usinas", "erbs", "flutuantes", "ip4", "aerodromos", "locais_votacao"], { cod, ligadas: ["rod_federais", "rod_estaduais", "ramais", "hidrovias", "hospitais", "seguranca", "flutuantes", "aerodromos"] })}</div></div>
      ${r ? `<div class="card c12"><div class="card-head"><h2>Produção rural</h2><span class="sub">IBGE · PAM, PEVS e PPM (valor em R$ mil; rebanhos em cabeças)</span></div><div class="card-body duo">
        <div><h3 class="h3">Lavouras</h3>${barras(r.pam_valor || [], { u: "R$ mil", cor: "var(--s2)", limite: 6 })}</div><div><h3 class="h3">Extrativismo e rebanhos</h3>${barras(r.pevs_valor || [], { u: "R$ mil", cor: "var(--s3)", limite: 4 })}${barras(r.rebanhos || [], { cor: "var(--s4)", limite: 4 })}</div></div></div>` : ""}
    </div>`;
  }

  function municipios() {
    const cols = ["pop_estimada", "eleitores", "pib_pc", "ifdm", "renda_media", "matriculas", "ideb_in", "leitos_sus_hab", "cvli_taxa", "esgoto_rede", "km_ramais", "desmatamento"].filter(id => IND[id]);
    return cabecalho("Municípios", "Os 62 municípios com os principais indicadores. Clique para abrir a ficha.", `<a href="#/visao">Visão geral</a> / Municípios`)
      + `<div class="grid"><div class="card c12"><div class="table-wrap" style="max-height:none"><table><thead><tr><th>Município</th>${cols.map(id => `<th class="n">${esc(IND[id].nome.replace(/ \(.*\)/, ""))}<br><span class="muted" style="font-weight:400">${esc(refFmt(IND[id].ref))}</span></th>`).join("")}</tr></thead><tbody>
      ${P.municipios.map(m => `<tr class="click" tabindex="0" onclick="location.hash='#/municipios/${m.cod}'" onkeydown="if(event.key==='Enter')location.hash='#/municipios/${m.cod}'"><td>${esc(m.nome)}</td>${cols.map(id => `<td class="n">${fmt(IND[id].municipios[m.cod], IND[id].unidade)}</td>`).join("")}</tr>`).join("")}</tbody></table></div></div></div>`;
  }

  function fontes() {
    const ing = P.ingestoes;
    const st = c => c.ingestao ? ing.find(g => g.fonte === c.ingestao) : ing.find(g => g.fonte.toLowerCase().includes(c.id === "inep" ? "inep" : c.id === "prodes" ? "prodes" : c.id === "queimadas" ? "queimadas" : c.id === "sinesp" ? "sinesp" : c.id === "cnes" ? "cnes" : c.id === "ibge" ? "ibge" : c.id === "geotatica" ? "geot" : "@@"));
    const geo = P.geotatica?.selecionadas || [];
    const temas = [...new Set(geo.map(g => g.tema).filter(Boolean))].sort();
    let f = { q: "", tema: "" };
    const linhasGeo = () => geo.filter(g => (!f.tema || g.tema === f.tema) && (!f.q || (g.nome + " " + g.url).toLowerCase().includes(f.q.toLowerCase())));
    const tabGeo = () => { const l = linhasGeo(); return `<div class="table-wrap" style="max-height:560px"><table><thead><tr><th>Fonte (${l.length})</th><th>Tema</th><th>Escala</th><th>Acesso</th><th>Tipo</th><th>Licença</th></tr></thead><tbody>${l.slice(0, 400).map(g => `<tr><td><a href="${esc(g.url)}" target="_blank" rel="noopener">${esc(g.nome)}</a></td><td class="muted">${esc(g.tema)}</td><td class="muted">${esc(g.escala)}</td><td class="muted">${esc(g.acesso)}</td><td class="muted">${esc(g.tipo)}</td><td class="muted">${esc(g.licenca)}</td></tr>`).join("")}</tbody></table></div>${l.length > 400 ? `<p class="note">Mostrando 400 de ${l.length}; refine a busca.</p>` : ""}`; };
    queueMicrotask(() => { const fl = $("#geo-f"); fl?.addEventListener("input", e => { f[e.target.name] = e.target.value; $("#geo-box").innerHTML = tabGeo(); }); });
    return cabecalho("Fontes de dados", `Conectores ativos, última execução do pipeline (${new Date(P.gerado_em).toLocaleString("pt-BR")}) e o catálogo GeoTática usado para descobrir novas fontes.`, `<a href="#/visao">Visão geral</a> / Fontes`)
      + `<div class="grid"><div class="card c12"><div class="card-head"><h2>Conectores</h2><span class="sub">para atualizar: <code>python -I pipeline/p05_ampliacao.py --atualizar</code></span></div><div class="table-wrap" style="max-height:none"><table><thead><tr><th>Fonte</th><th>Órgão</th><th>Acesso</th><th>Periodicidade</th><th>Cobertura</th><th>Última execução</th><th class="n">Registros</th></tr></thead><tbody>
      ${P.conectores.map(c => { const g = st(c); return `<tr><td><a href="${esc(c.url)}" target="_blank" rel="noopener">${esc(c.nome)}</a>${c.nota ? `<div class="muted" style="font-size:12px;max-width:60ch">${esc(c.nota)}</div>` : ""}</td><td class="muted">${esc(c.orgao)}</td><td class="muted">${esc(c.acesso)}</td><td class="muted">${esc(c.periodicidade)}</td><td class="muted">${esc(c.cobertura)}</td><td>${g ? `<span class="${g.status === "ok" ? "ok-dot" : "fail-dot"}"></span>${g.status === "ok" ? "ok" : "falha: " + esc(g.erro)}` : c.id === "ppa" ? `<span class="ok-dot"></span>pipeline p01–p03` : '<span class="muted">referência</span>'}</td><td class="n">${g ? nf(g.registros) : c.id === "ppa" ? nf(OBS_PPA.length) : "—"}</td></tr>`; }).join("")}
      </tbody></table></div></div></div>
      <div class="grid"><div class="card c12"><div class="card-head"><h2>Catálogo GeoTática</h2><div class="filters" id="geo-f"><select class="sel" name="tema" aria-label="Tema"><option value="">Todos os temas</option>${temas.map(t => `<option>${esc(t)}</option>`).join("")}</select><input type="search" name="q" placeholder="Buscar fonte" aria-label="Buscar fonte"></div></div>
      <div class="card-body" id="geo-box">${tabGeo()}</div><div class="card-foot">${nf(geo.length)} fontes nacionais ou do Amazonas, em temas do Observatório, de ${nf(P.geotatica?.total_catalogo)} no catálogo. Catálogo de descoberta: cada fonte precisa ser avaliada (licença, formato, periodicidade) antes de virar conector.</div></div></div>`;
  }

  /* ---------------- navegação */
  const MENU = [
    { g: "Painel" }, { id: "visao", nome: "Visão geral", icon: "home" },
    ...AREAS,
    { g: "Território" }, { id: "municipios", nome: "Municípios", icon: "pin" }, { id: "bairros", nome: "Bairros e comunidades", icon: "grid" },
    { g: "Planejamento e dados" }, { id: "ppa", nome: "PPA 2024–2027", icon: "target" }, { id: "fontes", nome: "Fontes de dados", icon: "db" },
  ];
  $("#menu").innerHTML = MENU.map(x => x.g ? `<div class="menu-group">${x.g}</div>` : `<a class="menu-item" href="#/${x.id}" data-id="${x.id}" title="${esc(x.nome)}">${ico(x.icon)}<span>${esc(x.nome)}</span></a>`).join("");
  $("#lista-mun").innerHTML = P.municipios.map(m => `<option value="${esc(m.nome)}">`).join("");
  $("#stamp").textContent = `Dados atualizados em ${new Date(P.gerado_em).toLocaleDateString("pt-BR")}`;
  $("#sidebar-foot").textContent = `${P.indicadores.length} indicadores públicos · ${PPA ? PPA.indicadores.length : 0} do PPA · 62 municípios`;

  $("#busca").addEventListener("change", e => {
    const n = e.target.value.trim().toLowerCase(); if (!n) return;
    const m = P.municipios.find(x => x.nome.toLowerCase() === n) || P.municipios.find(x => x.nome.toLowerCase().startsWith(n));
    if (m) { location.hash = `#/municipios/${m.cod}`; e.target.value = ""; }
  });
  const app = $("#app");
  $("#toggle-menu").addEventListener("click", () => {
    const mobile = matchMedia("(max-width: 900px)").matches;
    app.classList.toggle(mobile ? "menu-open" : "collapsed");
    $("#toggle-menu").setAttribute("aria-expanded", mobile ? app.classList.contains("menu-open") : !app.classList.contains("collapsed"));
  });
  $("#btn-imprimir").addEventListener("click", () => print());

  function rota() {
    const [, r = "visao", sub] = location.hash.split("/");
    hideTip(); app.classList.remove("menu-open");
    let html;
    if (r === "visao") html = visao();
    else if (AREA[r]) html = area(AREA[r]);
    else if (r === "ppa") html = ppaPagina();
    else if (r === "municipios") html = sub ? municipio(sub) : municipios();
    else if (r === "fontes") html = fontes();
    else if (r === "bairros") html = bairros(sub);
    else html = visao();
    page.innerHTML = html;
    const atual = AREA[r] ? AREA[r].id : ["ppa", "municipios", "fontes", "bairros"].includes(r) ? r : "visao";
    document.querySelectorAll(".menu-item").forEach(a => a.dataset.id === atual ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
    document.title = `${$("h1", page)?.textContent || "Painel"} — Observatório Amazonas`;
    scrollTo(0, 0);
  }
  addEventListener("hashchange", rota);
  rota();
})();
