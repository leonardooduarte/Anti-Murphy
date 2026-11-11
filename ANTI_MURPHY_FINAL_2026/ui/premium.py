from __future__ import annotations

import html
import json
from typing import Any, Dict, List

import streamlit as st
import streamlit.components.v1 as components

from simulation.intelligence import propagation_levels


def _e(value: Any) -> str:
    return html.escape(str(value))


def render_copilot_panel(recommendations: List[Dict[str, Any]], resilience: Dict[str, Any], height: int = 330):
    cards = []
    for i, rec in enumerate(recommendations[:4]):
        conf = int(rec.get("confidence", 0))
        cards.append(f'''
        <div class="rec" style="--d:{i*80}ms">
          <div class="rec-top"><span>{_e(rec.get('signal','SINAL'))}</span><b>{conf}%</b></div>
          <div class="rec-title">{_e(rec.get('title',''))}</div>
          <div class="rec-why">{_e(rec.get('why',''))}</div>
          <div class="rec-action">{_e(rec.get('action',''))}</div>
        </div>''')
    score = float(resilience.get("score", 0))
    band = _e(resilience.get("band", "-"))
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
    .shell{{height:310px;border-radius:24px;overflow:hidden;position:relative;background:linear-gradient(135deg,#101719,#172326);border:1px solid rgba(255,255,255,.08);color:#eef2ef;padding:20px;box-shadow:0 22px 60px rgba(16,24,26,.18)}}
    .shell:before{{content:"";position:absolute;width:360px;height:360px;border-radius:50%;right:-150px;top:-190px;background:radial-gradient(circle,rgba(255,104,27,.17),transparent 66%);animation:orb 7s ease-in-out infinite alternate}}@keyframes orb{{to{{transform:translate(-35px,25px) scale(1.1)}}}}
    .head{{display:flex;justify-content:space-between;align-items:flex-start;position:relative;z-index:2}}.ey{{font-size:9px;letter-spacing:.17em;text-transform:uppercase;color:#ff8245;font-weight:850}}.ttl{{font-size:21px;font-weight:820;letter-spacing:-.035em;margin-top:4px}}.sub{{font-size:10px;color:#83918e;margin-top:5px;max-width:620px;line-height:1.45}}
    .res{{display:flex;align-items:center;gap:10px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.035);border-radius:16px;padding:9px 12px}}.res strong{{font-size:24px;color:#6bc1b5;line-height:1}}.res span{{display:block;color:#7e8e8a;font-size:8px;letter-spacing:.12em;text-transform:uppercase}}.res b{{font-size:10px;color:#dce5e2}}
    .grid{{position:relative;z-index:2;display:grid;grid-template-columns:repeat(4,1fr);gap:9px;margin-top:15px}}.rec{{min-height:163px;border:1px solid rgba(255,255,255,.075);background:rgba(255,255,255,.035);border-radius:15px;padding:12px;opacity:0;transform:translateY(8px);animation:in .45s ease forwards;animation-delay:var(--d);transition:.2s ease}}@keyframes in{{to{{opacity:1;transform:none}}}}.rec:hover{{transform:translateY(-4px);border-color:rgba(255,104,27,.34)}}
    .rec-top{{display:flex;justify-content:space-between;align-items:center;font-size:8px;color:#72827f;letter-spacing:.12em;font-weight:800}}.rec-top b{{color:#ff8b51;font-size:9px}}.rec-title{{font-size:12px;font-weight:760;color:#f3f5f0;margin-top:9px;line-height:1.25}}.rec-why{{font-size:9px;color:#90a09c;line-height:1.45;margin-top:7px}}.rec-action{{font-size:8px;color:#62b9ae;margin-top:9px;border-top:1px solid rgba(255,255,255,.06);padding-top:7px}}
    @media(max-width:900px){{.grid{{grid-template-columns:1fr 1fr}}.shell{{height:520px}}}}
    </style></head><body><div class="shell"><div class="head"><div><div class="ey">Murphy Copilot · explainable decision support</div><div class="ttl">Próximos testes recomendados</div><div class="sub">Heurísticas transparentes baseadas no resultado da simulação. O Copilot sugere experimentos; a decisão continua sendo do usuário.</div></div><div class="res"><strong>{score:.0f}</strong><div><span>Resiliência</span><b>{band}</b></div></div></div><div class="grid">{''.join(cards)}</div></div></body></html>'''
    components.html(doc, height=height, scrolling=False)


def render_propagation_map(result: Dict[str, Any], source_sid: str | None = None, height: int = 300):
    levels = propagation_levels(result, source_sid)
    if not levels:
        return
    count = len(levels)
    nodes = []
    for i, x in enumerate(levels):
        impact = float(x["impact"])
        cls = "source" if x["source"] else ("hot" if impact >= 70 else "warm" if impact >= 45 else "cool")
        nodes.append(f'''
        <div class="node {cls}" style="--d:{i*100}ms">
          <div class="ring"><i style="--p:{impact:.1f}"></i><b>{impact:.0f}</b></div>
          <div class="nid">{_e(x['Posto'])}</div><div class="name">{_e(x['Nome'])}</div>
          <div class="meta">{x['queue']} fila · {x['wait']:.1f} min</div>
        </div>''')
    src = _e(source_sid or result.get("bottleneck", "-"))
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Inter,-apple-system,"Segoe UI",sans-serif}}.map{{height:276px;border-radius:22px;background:linear-gradient(135deg,#121a1d,#182326);border:1px solid rgba(255,255,255,.08);color:#eef2ef;padding:18px 20px;position:relative;overflow:hidden}}.map:after{{content:"";position:absolute;left:0;right:0;top:139px;height:1px;background:linear-gradient(90deg,transparent,#405250 10%,#657c78 50%,#405250 90%,transparent)}}
    .head{{display:flex;justify-content:space-between;position:relative;z-index:3}}.ey{{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:#ff8245;font-weight:850}}.title{{font-size:18px;font-weight:800;margin-top:3px}}.src{{font-size:9px;color:#95a39f;border:1px solid rgba(255,255,255,.08);border-radius:99px;padding:7px 10px}}.src b{{color:#ff8a4c}}
    .nodes{{position:relative;z-index:3;display:grid;grid-template-columns:repeat({count},1fr);gap:10px;margin-top:18px}}.node{{text-align:center;opacity:0;transform:translateY(8px);animation:show .5s ease forwards;animation-delay:var(--d)}}@keyframes show{{to{{opacity:1;transform:none}}}}.ring{{width:62px;height:62px;border-radius:50%;margin:auto;display:grid;place-items:center;position:relative;background:#172225;border:1px solid #344542;box-shadow:0 0 0 5px #121b1d}}.ring:before{{content:"";position:absolute;inset:5px;border-radius:50%;border:4px solid #31423f}}.ring i{{position:absolute;inset:5px;border-radius:50%;background:conic-gradient(#5bb7aa calc(var(--p)*1%),transparent 0);mask:radial-gradient(circle,transparent 53%,#000 55%)}}.ring b{{font-size:15px;z-index:2}}.hot .ring i,.source .ring i{{background:conic-gradient(#ff681b calc(var(--p)*1%),transparent 0)}}.source .ring{{border-color:#ff8245;box-shadow:0 0 0 5px #121b1d,0 0 22px rgba(255,104,27,.24);animation:pulse 1.8s infinite}}@keyframes pulse{{50%{{transform:scale(1.04)}}}}.nid{{font-size:8px;color:#ff8a4c;letter-spacing:.12em;font-weight:850;margin-top:10px}}.cool .nid{{color:#6db5ac}}.name{{font-size:10px;color:#dce5e2;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}.meta{{font-size:8px;color:#71827e;margin-top:4px}}
    </style></head><body><div class="map"><div class="head"><div><div class="ey">Impact propagation map</div><div class="title">Como a pressão se espalha pela operação</div></div><div class="src">origem <b>{src}</b></div></div><div class="nodes">{''.join(nodes)}</div></div></body></html>'''
    components.html(doc, height=height, scrolling=False)


def render_demo_story(base: Dict[str, Any], crisis: Dict[str, Any], recovery: Dict[str, Any], intervention: str, height: int = 410):
    def vals(r):
        return float(r.get("throughput_h",0)), float(r.get("sla_pct",0)), float(r.get("unit_cost",0)), float(r.get("makespan_h",0))
    btp,bsla,bc,bm = vals(base); ctp,csla,cc,cm = vals(crisis); rtp,rsla,rc,rm = vals(recovery)
    data = json.dumps({"b":[btp,bsla,bc,bm],"c":[ctp,csla,cc,cm],"r":[rtp,rsla,rc,rm]})
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Inter,-apple-system,"Segoe UI",sans-serif}}.story{{height:382px;border-radius:25px;overflow:hidden;position:relative;background:linear-gradient(135deg,#0f1719,#182326);border:1px solid rgba(255,255,255,.08);color:#eef2ef;padding:20px 22px}}.story:before{{content:"";position:absolute;inset:0;background:radial-gradient(circle at 80% 0,rgba(255,104,27,.13),transparent 30%),radial-gradient(circle at 0 100%,rgba(63,142,137,.14),transparent 30%)}}
    .head{{position:relative;z-index:2;display:flex;justify-content:space-between}}.ey{{font-size:9px;color:#ff8245;letter-spacing:.16em;font-weight:850;text-transform:uppercase}}.ttl{{font-size:21px;font-weight:820;margin-top:4px}}.badge{{font-size:9px;border:1px solid rgba(255,255,255,.09);border-radius:99px;padding:7px 10px;color:#9dacaa}}
    .timeline{{position:relative;z-index:2;display:grid;grid-template-columns:1fr 70px 1fr 70px 1fr;align-items:center;margin-top:22px}}.phase{{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:14px;min-height:232px;opacity:0;animation:enter .55s ease forwards}}.phase.crisis{{animation-delay:.65s;border-color:rgba(255,104,27,.38)}}.phase.recover{{animation-delay:1.3s;border-color:rgba(83,184,167,.32)}}@keyframes enter{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:none}}}}.num{{font-size:9px;color:#6f817d;letter-spacing:.14em}}.phase h3{{font-size:15px;margin:6px 0 12px}}.phase.crisis h3{{color:#ff8245}}.phase.recover h3{{color:#69c0b4}}.k{{display:flex;justify-content:space-between;border-top:1px solid rgba(255,255,255,.06);padding:8px 0;font-size:9px;color:#80918d}}.k b{{color:#e7eeeb;font-size:11px}}.arrow{{height:2px;background:#3b4c49;position:relative;overflow:visible}}.arrow:after{{content:"";position:absolute;right:-1px;top:-4px;border-left:7px solid #647976;border-top:5px solid transparent;border-bottom:5px solid transparent}}.arrow i{{position:absolute;width:10px;height:10px;border-radius:50%;top:-4px;left:0;background:#ff681b;box-shadow:0 0 14px rgba(255,104,27,.7);animation:move 1.4s ease-in-out infinite}}.arrow.good i{{background:#55b7aa;box-shadow:0 0 14px rgba(85,183,170,.7);animation-delay:.7s}}@keyframes move{{to{{left:calc(100% - 8px)}}}}.intervention{{font-size:8px;color:#98a6a3;line-height:1.4;margin-top:8px}}.intervention b{{color:#f0f3ef}}
    </style></head><body><div class="story"><div class="head"><div><div class="ey">Presentation mode · guided story</div><div class="ttl">Do problema à recuperação em uma única narrativa</div></div><div class="badge">DEMO AUTOMÁTICA</div></div><div class="timeline"><div class="phase"><div class="num">01 · BASE</div><h3>Operação normal</h3><div class="k"><span>Throughput</span><b>{btp:.2f}</b></div><div class="k"><span>SLA</span><b>{bsla:.0f}%</b></div><div class="k"><span>Custo/un</span><b>R$ {bc:.2f}</b></div><div class="k"><span>Gargalo</span><b>{_e(base.get('bottleneck'))}</b></div></div><div class="arrow"><i></i></div><div class="phase crisis"><div class="num">02 · MURPHY</div><h3>Evento crítico</h3><div class="k"><span>Throughput</span><b>{ctp:.2f}</b></div><div class="k"><span>SLA</span><b>{csla:.0f}%</b></div><div class="k"><span>Makespan</span><b>{cm:.1f}h</b></div><div class="k"><span>Gargalo</span><b>{_e(crisis.get('bottleneck'))}</b></div></div><div class="arrow good"><i></i></div><div class="phase recover"><div class="num">03 · RESPOSTA</div><h3>Sistema estabilizado</h3><div class="k"><span>Throughput</span><b>{rtp:.2f}</b></div><div class="k"><span>SLA</span><b>{rsla:.0f}%</b></div><div class="k"><span>Custo/un</span><b>R$ {rc:.2f}</b></div><div class="k"><span>Gargalo</span><b>{_e(recovery.get('bottleneck'))}</b></div><div class="intervention"><b>Intervenção:</b> {_e(intervention)}</div></div></div></div><script>const DATA={data};</script></body></html>'''
    components.html(doc, height=height, scrolling=False)


def render_decision_timeline(history: List[Dict[str, Any]], height: int = 280):
    if not history:
        st.info("Ainda não há decisões registradas nesta sessão.")
        return
    items = []
    for i, h in enumerate(history[-7:]):
        delta = h.get("delta", {})
        items.append(f'''<div class="item"><div class="dot"></div><div class="idx">{i+1:02d}</div><div class="body"><b>{_e(h.get('name','Cenário'))}</b><span>{_e(h.get('source','Experimento'))} · gargalo {_e(h.get('bottleneck','-'))}</span></div><div class="chips"><i>{float(delta.get('throughput_pct',0)):+.1f}% TP</i><i>{float(delta.get('sla_pp',0)):+.1f}pp SLA</i></div></div>''')
    doc=f'''<style>*{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Inter,-apple-system,"Segoe UI",sans-serif}}.tl{{border-radius:20px;background:#162124;border:1px solid #2e3d40;padding:15px 18px;color:#eef2ef}}.head{{font-size:9px;color:#ff8245;letter-spacing:.15em;text-transform:uppercase;font-weight:850;margin-bottom:8px}}.item{{display:grid;grid-template-columns:14px 30px 1fr auto;align-items:center;gap:8px;position:relative;padding:9px 0;border-top:1px solid #29373a}}.item:first-of-type{{border-top:0}}.dot{{width:8px;height:8px;border-radius:50%;background:#5bb8ad;box-shadow:0 0 0 4px rgba(91,184,173,.08)}}.idx{{font-size:9px;color:#60736f}}.body b{{display:block;font-size:11px}}.body span{{display:block;font-size:8px;color:#778985;margin-top:3px}}.chips{{display:flex;gap:5px}}.chips i{{font-style:normal;font-size:8px;color:#a5b3af;border:1px solid #334548;border-radius:99px;padding:4px 6px}}</style><div class="tl"><div class="head">Decision Timeline · histórico desta sessão</div>{''.join(items)}</div>'''
    components.html(doc,height=height,scrolling=False)
