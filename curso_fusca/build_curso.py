#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as apostilas do Curso Fusca Original (HTML) na identidade Aircooled Market.
Conteúdo original, foco no Fusca brasileiro. Depois renderize cada .html em PDF."""

import html as _html
from pathlib import Path

OUT = Path(__file__).resolve().parent

BEETLE_SMALL = ('<svg viewBox="0 0 120 66" fill="none"><path d="M8 48 C8 33 20 22 38 20 C48 9 66 6 80 12 '
  'C90 16 96 24 100 32 C110 33 116 40 114 48" stroke="#f3b12b" stroke-width="4.5" stroke-linecap="round"/>'
  '<path d="M8 48 L114 48" stroke="#f3b12b" stroke-width="4.5" stroke-linecap="round"/>'
  '<path d="M40 21 C48 14 64 12 78 16" stroke="#f3b12b" stroke-width="3"/>'
  '<circle cx="34" cy="49" r="11" fill="#1b1d22" stroke="#f3b12b" stroke-width="4.5"/>'
  '<circle cx="90" cy="49" r="11" fill="#1b1d22" stroke="#f3b12b" stroke-width="4.5"/>'
  '<circle cx="34" cy="49" r="2.5" fill="#f3b12b"/><circle cx="90" cy="49" r="2.5" fill="#f3b12b"/></svg>')

BEETLE_BIG = ('<svg viewBox="0 0 320 150" fill="none"><path d="M18 108 C18 74 44 50 84 46 C106 22 150 14 186 22 '
  'C214 28 232 44 244 64 C286 66 302 84 300 108" stroke="#f3b12b" stroke-width="6" stroke-linecap="round"/>'
  '<path d="M18 108 L300 108" stroke="#f3b12b" stroke-width="6" stroke-linecap="round"/>'
  '<path d="M92 48 C112 30 156 24 188 30 C206 33 220 42 230 56" stroke="#f3b12b" stroke-width="3.5" opacity="0.8"/>'
  '<path d="M150 26 L150 54" stroke="#f3b12b" stroke-width="3" opacity="0.6"/>'
  '<circle cx="86" cy="110" r="26" fill="#1b1d22" stroke="#f3b12b" stroke-width="6"/>'
  '<circle cx="232" cy="110" r="26" fill="#1b1d22" stroke="#f3b12b" stroke-width="6"/>'
  '<circle cx="86" cy="110" r="6" fill="#f3b12b"/><circle cx="232" cy="110" r="6" fill="#f3b12b"/></svg>')

CSS = """
@page { size:A4; margin:0; } @page content { margin:18mm 17mm 20mm 17mm; }
* { box-sizing:border-box; } html { -webkit-print-color-adjust:exact; print-color-adjust:exact; }
:root{ --ink:#22242a; --ink-soft:#55585f; --gold:#f3b12b; --gold-deep:#c8860f; --charcoal:#1b1d22; --line:#e6e2d8; --cream:#faf7f0; }
body { font-family:"Georgia","Times New Roman",serif; color:var(--ink); font-size:11.2pt; line-height:1.55; margin:0; }
h1,h2,h3,.kicker,th,.chk-title,.box-title,.brand,.pill { font-family:"Helvetica Neue",Arial,sans-serif; }
.cover { position:relative; width:210mm; height:297mm; background:var(--charcoal); color:#fff; page:cover; page-break-after:always; overflow:hidden; }
.cover::after{ content:""; position:absolute; left:0; right:0; bottom:0; height:4mm; background:var(--gold); }
.cover-pad { position:absolute; inset:0; padding:26mm 22mm; display:flex; flex-direction:column; justify-content:space-between; }
.brand { display:flex; align-items:center; gap:9px; font-weight:800; font-size:15pt; }
.brand .b-air{ color:var(--gold);} .brand .b-mkt{ color:#fff;} .brand svg{ width:38px; height:22px; }
.kicker { letter-spacing:.32em; text-transform:uppercase; font-size:9.5pt; color:var(--gold); font-weight:700; margin-bottom:5mm; }
.cover h1 { font-family:"Helvetica Neue",Arial,sans-serif; font-weight:800; font-size:42pt; line-height:1.03; margin:0 0 5mm; color:#fff; }
.cover h1 span { color:var(--gold); }
.cover .sub { font-size:13pt; color:#c9cbd1; font-style:italic; max-width:150mm; }
.cover-hero { text-align:center; } .cover-hero svg{ width:118mm; height:auto; }
.cover-foot { display:flex; justify-content:space-between; align-items:flex-end; font-family:"Helvetica Neue",Arial,sans-serif; font-size:9.5pt; color:#8b8e96; }
.pill { display:inline-block; border:1.5px solid var(--gold); color:var(--gold); border-radius:999px; padding:2mm 5mm; font-weight:700; font-size:9pt; letter-spacing:.06em; }
.content { page:content; }
h2 { font-size:16.5pt; color:var(--ink); margin:9mm 0 2mm; padding-bottom:2mm; border-bottom:2px solid var(--gold); }
h2 .num { color:var(--gold-deep); margin-right:7px; font-weight:800; }
h3 { font-size:12.5pt; color:var(--charcoal); margin:6mm 0 1mm; } h3::before{ content:"▸ "; color:var(--gold-deep); }
p { margin:0 0 3mm; text-align:justify; } ul,ol { margin:0 0 3mm; padding-left:6mm; } li { margin-bottom:1.5mm; }
strong { color:#141519; } .lead { font-size:12pt; color:var(--ink-soft); font-style:italic; }
.mono { font-family:"Courier New",monospace; background:#f3efe6; padding:0 2px; border-radius:3px; }
.box { border-radius:7px; padding:4mm 5mm; margin:4mm 0; page-break-inside:avoid; font-size:10.6pt; }
.box-title { font-size:9pt; text-transform:uppercase; letter-spacing:.13em; font-weight:800; margin-bottom:1.5mm; }
.box p:last-child{ margin-bottom:0; }
.box.ex { background:#fdf6e3; border-left:4px solid var(--gold); } .box.ex .box-title{ color:var(--gold-deep); }
.box.dica { background:#f1f6ef; border-left:4px solid #6f9c4b; } .box.dica .box-title{ color:#4d7a2b; }
.box.atencao { background:#fbece2; border-left:4px solid #c0392b; } .box.atencao .box-title{ color:#a5281b; }
table { width:100%; border-collapse:collapse; margin:3mm 0 4mm; font-size:10pt; page-break-inside:avoid; }
th { background:var(--charcoal); color:var(--gold); text-align:left; padding:2.5mm 3mm; font-size:9pt; text-transform:uppercase; letter-spacing:.05em; }
td { padding:2.2mm 3mm; border-bottom:1px solid var(--line); vertical-align:top; } tr:nth-child(even) td { background:var(--cream); }
.figrow{ display:flex; gap:4mm; margin:4mm 0; page-break-inside:avoid; }
.foto{ flex:1; border:2px dashed var(--gold); border-radius:7px; background:#fbf7ee; min-height:44mm; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:4mm; }
.foto .ico{ font-size:20pt; color:var(--gold); } .foto .cap{ font-family:"Helvetica Neue",Arial,sans-serif; font-size:8.4pt; margin-top:2mm; color:var(--ink-soft); font-weight:600; }
.chk { background:var(--cream); border:1px solid var(--line); border-top:3px solid var(--gold); border-radius:7px; padding:5mm 6mm; margin:4mm 0; page-break-inside:avoid; }
.chk-title { color:var(--charcoal); text-transform:uppercase; letter-spacing:.1em; font-size:10pt; font-weight:800; margin-bottom:3mm; }
.chk ul { list-style:none; padding-left:0; } .chk li { padding-left:8mm; position:relative; margin-bottom:2.5mm; }
.chk li::before { content:"☐"; position:absolute; left:0; font-size:13pt; color:var(--gold-deep); top:-1px; }
.pb { page-break-before:always; }
.foot { margin-top:8mm; padding-top:3mm; border-top:1px solid var(--line); font-size:9pt; color:#8f8a7d; font-family:"Helvetica Neue",Arial,sans-serif; }
"""

def cover(num, tag, title_main, title_hi, sub, foot_left):
    return f"""<section class="cover"><div class="cover-pad">
  <div class="brand">{BEETLE_SMALL}<span><span class="b-air">Aircooled</span> <span class="b-mkt">Market</span></span></div>
  <div><div class="kicker">{tag}</div>
    <h1>{title_main}<br><span>{title_hi}</span></h1>
    <div class="sub">{sub}</div>
    <div class="cover-hero">{BEETLE_BIG}</div></div>
  <div class="cover-foot"><span>{foot_left}</span><span class="pill">{num}</span></div>
</div></section>"""

def render_section(s):
    t = s[0]
    if t == "h2":   return f'<h2><span class="num">{s[1]}</span>{s[2]}</h2>'
    if t == "h2pb": return f'<h2 class="pb"><span class="num">{s[1]}</span>{s[2]}</h2>'
    if t == "h3":   return f'<h3>{s[1]}</h3>'
    if t == "lead": return f'<p class="lead">{s[1]}</p>'
    if t == "p":    return f'<p>{s[1]}</p>'
    if t == "ul":   return '<ul>' + ''.join(f'<li>{i}</li>' for i in s[1]) + '</ul>'
    if t == "table":
        head = ''.join(f'<th>{h}</th>' for h in s[1])
        rows = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in s[2])
        return f'<table><tr>{head}</tr>{rows}</table>'
    if t == "box":  return f'<div class="box {s[1]}"><div class="box-title">{s[2]}</div><p>{s[3]}</p></div>'
    if t == "fotos":
        cells = ''.join(f'<div class="foto"><div class="ico">📷</div><div class="cap">{c}</div></div>' for c in s[1])
        return f'<div class="figrow">{cells}</div>'
    if t == "chk":
        items = ''.join(f'<li>{i}</li>' for i in s[2])
        return f'<div class="chk"><div class="chk-title">✓ {s[1]}</div><ul>{items}</ul></div>'
    return ''

def build(mod):
    body = ''.join(render_section(s) for s in mod["sections"])
    foot = mod.get("foot", "© Aircooled Market. Todos os direitos reservados. Reprodução proibida.")
    html = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>{mod['title_main']} {mod['title_hi']}</title><style>{CSS}</style></head><body>
{cover(mod['pill'], mod['tag'], mod['title_main'], mod['title_hi'], mod['sub'], mod['foot_left'])}
<div class="content">{body}
<div class="foot">Curso Fusca Original — {mod['title_main']} {mod['title_hi']} · {foot}</div>
</div></body></html>"""
    path = OUT / mod["file"]
    path.write_text(html, encoding="utf-8")
    return path

# ---------------------------------------------------------------------------
# CONTEÚDO DOS MÓDULOS  (importado de conteudo_curso.py para manter este arquivo enxuto)
# ---------------------------------------------------------------------------
from conteudo_curso import MODULOS

if __name__ == "__main__":
    fotos = []
    for m in MODULOS:
        p = build(m)
        print("gerado:", p.name)
        for s in m["sections"]:
            if s[0] == "fotos":
                for c in s[1]:
                    fotos.append((m['title_main'] + ' ' + m['title_hi'], c))
    # lista de fotos
    print("\n===== LISTA DE FOTOS NECESSÁRIAS =====")
    atual = None
    for mod, cap in fotos:
        if mod != atual:
            print("\n#", mod); atual = mod
        print("  -", cap)
    (OUT / "fotos_necessarias.txt").write_text(
        "LISTA DE FOTOS — CURSO FUSCA ORIGINAL\n\n" +
        "\n".join(f"[{m}] {c}" for m, c in fotos), encoding="utf-8")
    print(f"\nTotal de fotos: {len(fotos)}")
