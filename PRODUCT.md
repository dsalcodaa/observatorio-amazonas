# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JS opened directly in the browser, fed by Python pipeline scripts that download public data and write JSON/JS files (`observatorio/pipeline/`). The user plans to evolve the stack later (spec section 11 suggests PostgreSQL/PostGIS + API).

## Users

The Governor of Amazonas and the technical team, consulting the platform together during meetings: one person drives, others read the screen (often projected). They need to answer "how is the State doing in area X, and where (which municipality)?" in seconds, then drill into the source of a number.

## Product Purpose

Observatório Amazonas: monitor the State of Amazonas across every policy area (socioeconomics, environment, education, health, public security, infrastructure) and the PPA 2024–2027 goals, using only public data. Success: every number on screen has source, unit, reference period and update date, and the team trusts it enough to decide in the meeting.

## Positioning

Joins the official PPA 2024–2027 targets (extracted page by page from the State's evaluation reports) with independent public series (IBGE, INEP, INPE, SINESP/MJSP, DATASUS) for all 62 municipalities, keeping provenance to the original document page.

## Operating Context

- Meeting room, shared screen or projector; also laptop review before meetings.
- Spec: `especificacao_observatorio_amazonas.md` (modules, data model, formulas, acceptance criteria).
- Phase 1 already built: `observatorio/` (PPA document catalog, SQLite, `dados/ppa.js` with 109 indicators, 247 observations).
- Required sources named by the user: `github.com/rayonnunes/api_seguranca_publica` (SINESP-based API; spec says do not call its HTTP endpoint from the browser) and `geotatica.github.io/Plataforma_Dados` (catalog of 2,185 sources; use as discovery catalog, not as APIs).

## Capabilities and Constraints

- Official vs. calculated vs. estimated must be distinguishable; missing is not zero; reduction indicators need correct polarity.
- No individual crime locations; aggregate only.
- No login/backend yet; data refresh happens by re-running the pipeline.
- Indicators outside the PPA are labelled "complementar/proposto".

## Brand Commitments

- Layout structure follows the Velzon admin dashboard pattern (dark collapsible sidebar, top bar with search and filters, KPI cards, chart cards, dense tables), confirmed by the user on 2026-11-12. Identity (colors, type) is the Observatório's own; no Velzon code or assets.

## Evidence on Hand

- Official PPA data: `observatorio/dados/ppa.json`.
- Municipal geometry: `dashboard/municipios.js` (IBGE).
- Campaign plan indicators: `dashboard/dados.js` (610 indicators from the e-books).
- No real-time feeds; every series carries its own reference year.

## Product Principles

1. Every number shows its source and date; no orphan figures.
2. Territory first: every area answers "where" across the 62 municipalities.
3. Readable from across a meeting room: few strong numbers, detail on demand.
4. Never invent or interpolate values; gaps stay visible.
