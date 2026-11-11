from __future__ import annotations

import html
import streamlit.components.v1 as components


def _safe(v):
    return html.escape(str(v))


def render_cinematic_twin(result, height: int = 500):
    """Immersive, animated live view of the current simulated production system."""
    stations = result.get("stations", [])
    bottleneck = result.get("bottleneck")
    total_units = result.get("total_units", 0)
    throughput = float(result.get("throughput_h", 0))
    sla = float(result.get("sla_pct", 0))
    makespan = float(result.get("makespan_h", 0))
    unit_cost = float(result.get("unit_cost", 0))
    flow_duration = max(3.8, min(9.0, 8.4 - throughput * 0.55))

    cards = []
    for i, r in enumerate(stations):
        sid = _safe(r.get("Posto", ""))
        name = _safe(r.get("Nome", sid))
        util = float(r.get("Utilização máquina (%)", 0))
        workers = r.get("Operadores", 0)
        machines = r.get("Máquinas", 0)
        queue = r.get("Fila máx.", 0)
        wait = float(r.get("Espera média (min)", 0))
        queue_dots = "".join('<i></i>' for _ in range(min(int(queue), 7))) or '<i class="empty"></i>'
        is_bn = str(r.get("Posto")) == str(bottleneck)
        state = "RESTRIÇÃO" if is_bn else ("ALTA CARGA" if util >= 75 else "ESTÁVEL")
        cards.append(f'''
          <div class="station {'critical' if is_bn else ''}" style="--delay:{i*90}ms">
            <div class="station-head"><span>{sid}</span><span class="state">{state}</span></div>
            <div class="station-name">{name}</div>
            <div class="station-util">{util:.1f}<small>%</small></div>
            <div class="station-bar"><i style="width:{max(4, min(100, util)):.1f}%"></i></div>
            <div class="station-meta"><span>{machines} maq.</span><span>{workers} op.</span><span>{queue} fila</span></div>
            <div class="queue-viz"><em>fila</em><div>{queue_dots}</div></div>
            <div class="station-wait">espera média <b>{wait:.1f} min</b></div>
            {('<div class="fault"><span></span><span></span><b>EVENTO MURPHY</b></div>' if is_bn else '')}
          </div>
        ''')

    count = max(1, len(stations))
    runners = "".join([f'<i class="packet p{j}"></i>' for j in range(1, 6)])
    html_doc = f'''
<!doctype html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}}html,body{{margin:0;background:transparent;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#edf2ef}}
.stage{{position:relative;height:470px;overflow:hidden;border-radius:26px;border:1px solid rgba(255,255,255,.09);background:
 radial-gradient(circle at 16% 0%,rgba(255,104,27,.12),transparent 28%),
 radial-gradient(circle at 82% 100%,rgba(63,142,137,.16),transparent 30%),
 linear-gradient(145deg,#101719 0%,#131c1f 45%,#0d1416 100%);box-shadow:0 28px 75px rgba(16,24,26,.22)}}
.stage:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.85),transparent);pointer-events:none}}
.orb{{position:absolute;border-radius:50%;filter:blur(10px);opacity:.55;pointer-events:none}}
.orb.o1{{width:220px;height:220px;left:-50px;bottom:-60px;background:radial-gradient(circle,rgba(255,104,27,.18),transparent 65%);animation:float1 7s ease-in-out infinite alternate}}
.orb.o2{{width:260px;height:260px;right:-80px;top:-80px;background:radial-gradient(circle,rgba(63,142,137,.18),transparent 65%);animation:float2 8s ease-in-out infinite alternate}}
@keyframes float1{{to{{transform:translate(30px,-12px) scale(1.08)}}}}@keyframes float2{{to{{transform:translate(-25px,18px) scale(1.06)}}}}
.scan{{position:absolute;left:-20%;right:-20%;top:-80px;height:90px;background:linear-gradient(to bottom,transparent,rgba(255,255,255,.035),transparent);transform:rotate(-4deg);animation:scan 8s linear infinite;pointer-events:none}}@keyframes scan{{to{{top:520px}}}}
.hud{{position:relative;z-index:3;display:flex;align-items:flex-start;justify-content:space-between;padding:22px 25px 0}}
.eyebrow{{font-size:10px;letter-spacing:.19em;font-weight:800;color:#ff8a50;text-transform:uppercase}}.title{{font-size:24px;font-weight:780;letter-spacing:-.035em;margin-top:5px}}.sub{{font-size:11px;color:#82918e;margin-top:5px}}
.live{{display:flex;gap:8px;align-items:center;font-size:10px;letter-spacing:.12em;color:#a8b7b3;text-transform:uppercase;border:1px solid rgba(255,255,255,.1);border-radius:999px;padding:8px 11px;background:rgba(255,255,255,.035)}}.live i{{width:7px;height:7px;border-radius:50%;background:#52b7aa;box-shadow:0 0 0 0 rgba(82,183,170,.45);animation:ping 1.8s infinite}}@keyframes ping{{70%{{box-shadow:0 0 0 9px rgba(82,183,170,0)}}}}
.metrics{{position:relative;z-index:3;display:grid;grid-template-columns:repeat(5,1fr);gap:8px;padding:16px 25px 0}}
.m{{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.07);border-radius:13px;padding:9px 11px;backdrop-filter:blur(8px);position:relative;overflow:hidden}}
.m:after{{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 0 42%,rgba(255,255,255,.06) 50%,transparent 58% 100%);transform:translateX(-120%);animation:sheen 4.8s ease-in-out infinite}}
.m label{{display:block;font-size:8px;color:#71807d;letter-spacing:.14em;text-transform:uppercase;font-weight:800}}
.m b{{display:block;font-size:15px;margin-top:4px;letter-spacing:-.02em}}
.m.hot b{{color:#ff7a38}}.m.teal b{{color:#5db3aa}}@keyframes sheen{{15%{{transform:translateX(130%)}}100%{{transform:translateX(130%)}}}}
.network{{position:absolute;left:25px;right:25px;top:178px;height:250px;overflow-x:auto;overflow-y:hidden;padding:23px 4px 20px;scrollbar-width:thin;scrollbar-color:#334347 transparent}}.network::-webkit-scrollbar{{height:5px}}.network::-webkit-scrollbar-thumb{{background:#334347;border-radius:99px}}
.track{{position:absolute;left:4%;right:4%;top:77px;height:2px;background:linear-gradient(90deg,rgba(79,102,100,.25),rgba(124,153,149,.72),rgba(79,102,100,.25));box-shadow:0 0 18px rgba(91,173,162,.12)}}
.track:after{{content:"";position:absolute;inset:-1px;background:linear-gradient(90deg,transparent 0 40%,rgba(91,195,181,.9) 50%,transparent 60%);background-size:220% 100%;animation:flowline 4.3s linear infinite}}@keyframes flowline{{from{{background-position:180% 0}}to{{background-position:-60% 0}}}}
.packet{{position:absolute;top:72px;width:10px;height:10px;border-radius:50%;background:#61c6b8;box-shadow:0 0 0 3px #152022,0 0 18px rgba(97,198,184,.8);left:3%;z-index:2;animation:packet {flow_duration:.2f}s cubic-bezier(.3,.05,.4,1) infinite}}
.packet.p2{{animation-delay:-1.4s}}.packet.p3{{animation-delay:-2.8s}}.packet.p4{{animation-delay:-4.2s}}.packet.p5{{animation-delay:-5.6s}}@keyframes packet{{0%{{left:3%;opacity:0}}5%{{opacity:1}}95%{{opacity:1}}100%{{left:96%;opacity:0}}}}
.stations{{position:relative;z-index:3;display:grid;grid-template-columns:repeat({count},minmax(190px,1fr));gap:12px;min-width:{max(1000, count*204)}px}}
.station{{position:relative;height:205px;background:linear-gradient(180deg,rgba(25,37,40,.96),rgba(18,28,30,.96));border:1px solid rgba(255,255,255,.09);border-radius:17px;padding:14px 14px 12px;box-shadow:0 9px 28px rgba(0,0,0,.14);opacity:0;transform:translateY(16px);animation:enter .6s cubic-bezier(.15,.8,.25,1) forwards;animation-delay:var(--delay);transition:.25s ease}}@keyframes enter{{to{{opacity:1;transform:none}}}}.station:hover{{transform:translateY(-6px);border-color:rgba(91,184,172,.35);box-shadow:0 20px 42px rgba(0,0,0,.26)}}
.station:before{{content:"";position:absolute;top:-6px;left:50%;width:12px;height:12px;transform:translateX(-50%);border-radius:50%;background:#4d6260;border:3px solid #121d1f;z-index:3}}.station.critical{{border-color:rgba(255,104,27,.7);box-shadow:0 0 0 1px rgba(255,104,27,.13),0 18px 38px rgba(255,104,27,.08)}}.station.critical:before{{background:#ff681b;box-shadow:0 0 0 0 rgba(255,104,27,.42);animation:orangePulse 1.6s infinite}}@keyframes orangePulse{{70%{{box-shadow:0 0 0 12px rgba(255,104,27,0)}}}}
.station-head{{display:flex;justify-content:space-between;align-items:center;font-size:8px;letter-spacing:.13em;color:#6d7d79;text-transform:uppercase;font-weight:800}}.state{{color:#81908d}}.critical .state{{color:#ff8042}}.station-name{{font-size:13px;font-weight:720;margin-top:7px;color:#f4f4ef;min-height:32px}}.station-util{{font-size:31px;font-weight:800;margin-top:7px;color:#5db3aa;letter-spacing:-.05em}}.station-util small{{font-size:13px;margin-left:2px}}.critical .station-util{{color:#ff7431}}
.station-bar{{height:4px;border-radius:999px;background:#263436;overflow:hidden;margin-top:5px}}.station-bar i{{display:block;height:100%;background:linear-gradient(90deg,#3f8e89,#6cc1b6);border-radius:999px;transform-origin:left;animation:grow 1.1s cubic-bezier(.2,.8,.2,1)}}.critical .station-bar i{{background:linear-gradient(90deg,#ff681b,#ff9e62)}}@keyframes grow{{from{{transform:scaleX(0)}}}}
.station-meta{{display:flex;gap:5px;margin-top:9px}}.station-meta span{{font-size:8px;color:#a1aeab;border:1px solid rgba(255,255,255,.08);border-radius:999px;padding:4px 6px;background:rgba(255,255,255,.025)}}.queue-viz{{display:flex;align-items:center;gap:6px;margin-top:7px}}.queue-viz em{{font-size:7px;color:#5f706d;font-style:normal;text-transform:uppercase;letter-spacing:.08em}}.queue-viz div{{display:flex;gap:3px}}.queue-viz i{{display:block;width:5px;height:5px;border-radius:2px;background:#617d79;animation:qPulse 1.7s ease-in-out infinite alternate}}.queue-viz i:nth-child(2n){{animation-delay:.35s}}.queue-viz i.empty{{background:#283638}}.critical .queue-viz i{{background:#ff681b}}@keyframes qPulse{{to{{opacity:.38;transform:translateY(-2px)}}}}.station-wait{{font-size:9px;color:#71817d;margin-top:7px}}.station-wait b{{color:#b6c3bf;font-weight:650}}
.fault{{position:absolute;left:14px;right:14px;bottom:9px;height:17px;display:flex;align-items:center;gap:3px;color:#ff884a;font-size:7px;letter-spacing:.09em;font-weight:850}}.fault span{{height:3px;background:#ff681b;border-radius:9px;flex:1}}.fault span:first-child{{transform:translateY(-2px) rotate(-1deg)}}.fault span:nth-child(2){{transform:translateY(2px) rotate(1deg)}}.fault b{{white-space:nowrap;padding:0 5px}}
@media(max-width:900px){{.metrics{{grid-template-columns:repeat(2,1fr)}}.stage{{height:580px}}.network{{top:250px}}}}
</style></head><body><div class="stage"><div class="orb o1"></div><div class="orb o2"></div><div class="scan"></div><div class="hud"><div><div class="eyebrow">Decision Twin · Live simulation theatre</div><div class="title">Operação em movimento</div><div class="sub">Cada pulso representa fluxo atravessando o sistema. O laranja marca onde Murphy pressiona a operação.</div></div><div class="live"><i></i> simulação ativa</div></div>
<div class="metrics"><div class="m teal"><label>Throughput</label><b>{throughput:.2f} un/h</b></div><div class="m"><label>Unidades</label><b>{total_units}</b></div><div class="m"><label>Makespan</label><b>{makespan:.1f} h</b></div><div class="m"><label>SLA</label><b>{sla:.0f}%</b></div><div class="m hot"><label>Custo / un.</label><b>R$ {unit_cost:.2f}</b></div></div>
<div class="network"><div class="track">{runners}</div><div class="stations">{''.join(cards)}</div></div></div></body></html>
'''
    components.html(html_doc, height=height, scrolling=False)


def render_decision_reveal(base, alt, height: int = 320):
    """Animated before/after reveal after a Murphy Lab experiment."""
    from simulation.metrics import compare_results
    d = compare_results(base, alt)
    old_bn = _safe(base.get("bottleneck", "—"))
    new_bn = _safe(alt.get("bottleneck", "—"))
    vals = [
        ("THROUGHPUT", f"{base['throughput_h']:.2f}", f"{alt['throughput_h']:.2f}", f"{d['throughput_pct']:+.1f}%"),
        ("SLA", f"{base['sla_pct']:.0f}%", f"{alt['sla_pct']:.0f}%", f"{d['sla_pp']:+.1f} p.p."),
        ("CUSTO / UN.", f"R$ {base['unit_cost']:.2f}", f"R$ {alt['unit_cost']:.2f}", f"{d['unit_cost_pct']:+.1f}%"),
        ("MAKESPAN", f"{base['makespan_h']:.1f}h", f"{alt['makespan_h']:.1f}h", f"{d['makespan_pct']:+.1f}%"),
    ]
    cards = ''.join([f'<div class="r"><label>{a}</label><div class="swap"><span>{b}</span><i>→</i><b>{c}</b></div><em>{e}</em></div>' for a,b,c,e in vals])
    html_doc = f'''<!doctype html><html><head><style>
*{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.reveal{{height:292px;border-radius:24px;overflow:hidden;position:relative;background:linear-gradient(135deg,#11191b,#182326);border:1px solid rgba(255,255,255,.08);color:#eef2ef;box-shadow:0 24px 60px rgba(29,41,45,.16)}}.reveal:before{{content:"";position:absolute;inset:0;background:radial-gradient(circle at 75% 20%,rgba(63,142,137,.17),transparent 28%),radial-gradient(circle at 15% 90%,rgba(255,104,27,.11),transparent 25%)}}.head{{position:relative;padding:20px 23px 12px;display:flex;justify-content:space-between;align-items:center}}.ey{{font-size:9px;letter-spacing:.17em;text-transform:uppercase;color:#ff8245;font-weight:800}}.ttl{{font-size:21px;font-weight:780;margin-top:4px}}.shift{{font-size:10px;color:#7d8f8b;border:1px solid rgba(255,255,255,.09);padding:7px 10px;border-radius:999px}}.shift b{{color:#ff8245}}.grid{{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:8px;padding:5px 23px}}.r{{background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.075);border-radius:14px;padding:12px;opacity:0;transform:translateY(10px);animation:in .55s ease forwards}}.r:nth-child(2){{animation-delay:.08s}}.r:nth-child(3){{animation-delay:.16s}}.r:nth-child(4){{animation-delay:.24s}}@keyframes in{{to{{opacity:1;transform:none}}}}.r label{{display:block;font-size:8px;letter-spacing:.14em;color:#70807d;font-weight:800}}.swap{{display:flex;align-items:center;gap:7px;margin-top:9px}}.swap span{{color:#80908d;font-size:12px}}.swap i{{color:#52615e;font-style:normal}}.swap b{{font-size:18px;color:#f2f4ef}}.r em{{display:inline-block;margin-top:8px;font-size:9px;color:#78c3b9;font-style:normal}}.foot{{position:relative;margin:12px 23px 0;padding-top:11px;border-top:1px solid rgba(255,255,255,.06);font-size:11px;color:#82918e}}.foot b{{color:#f1f3ef}}.beam{{position:absolute;top:0;bottom:0;width:80px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.035),transparent);transform:skewX(-20deg);animation:beam 3.8s linear infinite}}@keyframes beam{{from{{left:-15%}}to{{left:110%}}}}</style></head><body><div class="reveal"><div class="beam"></div><div class="head"><div><div class="ey">Decision shift detected</div><div class="ttl">O sistema respondeu à sua decisão.</div></div><div class="shift">gargalo <b>{old_bn}</b> → <b>{new_bn}</b></div></div><div class="grid">{cards}</div><div class="foot">Leitura sistêmica: a decisão altera recursos locais, mas o <b>efeito emerge no fluxo inteiro</b>. Compare antes de implementar.</div></div></body></html>'''
    components.html(html_doc, height=height, scrolling=False)


def render_opportunity_radar(opps, height: int = 300):
    """Visual top-opportunity scan after the engine finishes."""
    top = opps[:5]
    if not top:
        return
    max_score = max(1.0, max(float(x.get("Score de oportunidade", 0)) for x in top))
    bars = []
    for i, x in enumerate(top):
        name = _safe(x.get("Ação", "Cenário"))
        score = float(x.get("Score de oportunidade", 0))
        pct = max(2, min(100, 100 * score / max_score)) if score > 0 else 2
        bars.append(f'<div class="o" style="--d:{i*90}ms"><div class="ot"><span>{name}</span><b>{score:.1f}</b></div><div class="bar"><i style="width:{pct:.1f}%"></i></div></div>')
    html_doc=f'''<!doctype html><html><head><style>*{{box-sizing:border-box}}body{{margin:0;background:transparent;font-family:Inter,-apple-system,"Segoe UI",sans-serif}}.radar{{height:270px;border-radius:22px;background:linear-gradient(135deg,#121a1c,#172225);color:#edf2ef;border:1px solid rgba(255,255,255,.08);padding:20px 22px;overflow:hidden;position:relative}}.radar:after{{content:"";position:absolute;width:330px;height:330px;border-radius:50%;border:1px solid rgba(63,142,137,.12);right:-130px;top:-150px;box-shadow:0 0 0 45px rgba(63,142,137,.035),0 0 0 90px rgba(63,142,137,.018)}}.ey{{font-size:9px;letter-spacing:.16em;text-transform:uppercase;color:#ff8245;font-weight:800}}.t{{font-size:20px;font-weight:780;margin-top:4px;margin-bottom:13px}}.o{{position:relative;z-index:2;margin:8px 0;opacity:0;animation:show .45s ease forwards;animation-delay:var(--d)}}@keyframes show{{to{{opacity:1}}}}.ot{{display:flex;justify-content:space-between;gap:15px;font-size:10px;color:#9caaa7}}.ot b{{color:#e9eeeb}}.bar{{height:5px;border-radius:99px;background:#263437;margin-top:5px;overflow:hidden}}.bar i{{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#3f8e89,#78c7bc);transform-origin:left;animation:grow 1s cubic-bezier(.2,.8,.2,1)}}.o:first-of-type .bar i{{background:linear-gradient(90deg,#ff681b,#ff9a5e)}}@keyframes grow{{from{{transform:scaleX(0)}}}}</style></head><body><div class="radar"><div class="ey">Opportunity scan complete</div><div class="t">Mapa de oportunidades testadas</div>{''.join(bars)}</div></body></html>'''
    components.html(html_doc, height=height, scrolling=False)
