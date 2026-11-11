from __future__ import annotations

import html
import json
from ui.stat_values import stat_value
import streamlit.components.v1 as components


def _esc(x):
    return html.escape(str(x))


def render_replay(result, height: int = 440):
    events = result.get("events", [])[:80]
    stations = result.get("stations", [])
    station_names = {str(x.get("Posto")): str(x.get("Nome")) for x in stations}
    payload = []
    for e in events:
        msg = str(e.get("message", ""))
        payload.append({"t": round(float(e.get("time", 0)), 2), "type": str(e.get("type", "flow")), "message": msg})
    data = json.dumps(payload, ensure_ascii=False)
    names = json.dumps(station_names, ensure_ascii=False)
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#111A1D;color:#F7F7F3;font-family:Inter,system-ui,sans-serif}}
    .wrap{{height:{height}px;border:1px solid #2C393D;border-radius:22px;overflow:hidden;background:radial-gradient(circle at 10% 0,rgba(255,104,27,.09),transparent 32%),#111A1D}}
    .top{{display:flex;justify-content:space-between;align-items:center;padding:18px 20px;border-bottom:1px solid #29363A}}
    .ey{{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#FF8A4C;font-weight:800}}.title{{font-size:21px;font-weight:800;margin-top:4px}}.time{{font-variant-numeric:tabular-nums;font-size:26px;font-weight:800;color:#F7F7F3}}
    .grid{{display:grid;grid-template-columns:1.45fr .85fr;height:calc(100% - 76px)}}.stage{{position:relative;padding:22px;overflow:hidden}}.stage:before{{content:"";position:absolute;left:8%;right:8%;top:50%;height:2px;background:#314044}}
    .stations{{position:absolute;left:6%;right:6%;top:42%;display:flex;justify-content:space-between;align-items:center}}.s{{width:88px;text-align:center;position:relative}}.dot{{width:17px;height:17px;border-radius:50%;background:#5B7273;border:4px solid #111A1D;margin:auto;box-shadow:0 0 0 1px #526467}}.s.on .dot{{background:#43AAA4;box-shadow:0 0 22px rgba(67,170,164,.65)}}.sn{{font-size:10px;color:#9DB0AE;margin-top:9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
    .pulse{{position:absolute;width:12px;height:12px;border-radius:50%;background:#FF681B;top:calc(50% - 5px);left:8%;box-shadow:0 0 20px rgba(255,104,27,.8);transition:left .65s cubic-bezier(.2,.8,.2,1),opacity .2s}}
    .side{{border-left:1px solid #29363A;padding:18px;background:#0E171A;overflow:hidden}}.event{{border:1px solid #2B383C;border-left:3px solid #43AAA4;background:#142024;border-radius:0 13px 13px 0;padding:13px 14px;margin-top:12px;min-height:118px}}.event strong{{display:block;font-size:12px;color:#FF9B67;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}}.event p{{font-size:13px;line-height:1.5;color:#DDE7E4;margin:0}}
    .controls{{display:flex;gap:8px;margin-top:14px}}button{{border:1px solid #3A484B;background:#172428;color:#EAF2EF;border-radius:10px;padding:8px 12px;font-weight:700;cursor:pointer}}button:hover{{border-color:#FF681B}}.progress{{height:4px;background:#273438;border-radius:999px;margin-top:16px;overflow:hidden}}.progress i{{display:block;height:100%;width:0;background:#FF681B;transition:width .35s}}
    .empty{{color:#849592;font-size:13px;padding:30px}}
    </style></head><body><div class="wrap"><div class="top"><div><div class="ey">Black Box Replay · Event Timeline</div><div class="title">Replay operacional</div></div><div class="time" id="clock">T+0.0h</div></div><div class="grid"><div class="stage"><div class="stations" id="stations"></div><i class="pulse" id="pulse"></i></div><div class="side"><div class="ey">Evento em foco</div><div class="event" id="event"><strong>Pronto</strong><p>Pressione reproduzir para percorrer os eventos registrados pela simulação.</p></div><div class="controls"><button onclick="toggle()" id="play">▶ Reproduzir</button><button onclick="step()">⏭ Próximo</button><button onclick="resetReplay()">↺ Reiniciar</button></div><div class="progress"><i id="prog"></i></div></div></div></div><script>
    const events={data}; const stationNames={names}; const ids=Object.keys(stationNames); let idx=-1, timer=null;
    const stations=document.getElementById('stations'); ids.forEach((id,i)=>{{const d=document.createElement('div');d.className='s';d.dataset.id=id;d.innerHTML=`<div class="dot"></div><div class="sn">${{stationNames[id]}}</div>`;stations.appendChild(d)}});
    function focusEvent(e){{document.getElementById('clock').textContent='T+'+Number(e.t).toFixed(1)+'h';document.getElementById('event').innerHTML='<strong>'+e.type+'</strong><p>'+e.message+'</p>';document.getElementById('prog').style.width=((idx+1)/Math.max(events.length,1)*100)+'%';let found=-1;ids.forEach((id,i)=>{{if(e.message.toUpperCase().includes(id.toUpperCase())||e.message.toUpperCase().includes(stationNames[id].toUpperCase())) found=i;}});document.querySelectorAll('.s').forEach((x,i)=>x.classList.toggle('on',i===found));if(found>=0) document.getElementById('pulse').style.left=(8+(84*found/Math.max(ids.length-1,1)))+'%';}}
    function step(){{if(!events.length)return;idx=(idx+1)%events.length;focusEvent(events[idx]);}}
    function toggle(){{const b=document.getElementById('play');if(timer){{clearInterval(timer);timer=null;b.textContent='▶ Reproduzir'}}else{{step();timer=setInterval(step,1150);b.textContent='⏸ Pausar'}}}}
    function resetReplay(){{if(timer){{clearInterval(timer);timer=null}}idx=-1;document.getElementById('play').textContent='▶ Reproduzir';document.getElementById('clock').textContent='T+0.0h';document.getElementById('event').innerHTML='<strong>Pronto</strong><p>Replay reiniciado.</p>';document.getElementById('prog').style.width='0';document.querySelectorAll('.s').forEach(x=>x.classList.remove('on'));document.getElementById('pulse').style.left='8%';}}
    </script></body></html>'''
    components.html(doc, height=height, scrolling=False)


def render_fragility_map(fragility):
    cards=[]
    max_score=max([float(x['Índice de fragilidade']) for x in fragility if x.get('Índice de fragilidade') is not None] or [1])
    for x in fragility:
        score=x.get('Índice de fragilidade'); pct=min(100,100*score/max_score) if score is not None and max_score>0 else 0
        cards.append(f'''<div class="fcard"><div class="fid">{_esc(x.get('Posto'))}</div><div class="fscore">{stat_value(score)}</div><div class="bar"><i style="width:{pct:.1f}%"></i></div><div class="meta">SLA médio <b>{stat_value(x.get('SLA médio'),0,'%')}</b> · makespan <b>{stat_value(x.get('Makespan médio'),1,'h')}</b></div></div>''')
    doc=f'''<style>.fgrid{{display:grid;grid-template-columns:repeat({min(5,max(1,len(cards)))},1fr);gap:10px}}.fcard{{background:#162124;border:1px solid #314044;border-radius:16px;padding:15px;color:#F7F7F3}}.fid{{font-size:10px;letter-spacing:.15em;color:#9EAEAB;font-weight:800}}.fscore{{font-size:27px;font-weight:850;margin:8px 0 7px}}.bar{{height:5px;background:#29383B;border-radius:99px;overflow:hidden}}.bar i{{display:block;height:100%;background:linear-gradient(90deg,#4AA49E,#FF681B);border-radius:99px}}.meta{{font-size:10px;color:#92A19E;margin-top:9px}}.meta b{{color:#EAF1EF}}@media(max-width:900px){{.fgrid{{grid-template-columns:1fr 1fr}}}}</style><div class="fgrid">{''.join(cards)}</div>'''
    components.html(doc,height=135 if len(cards)<=5 else 270,scrolling=False)


def render_goal_path(rows, target_tp, target_sla):
    top=rows[:5]
    items=[]
    for i,x in enumerate(top):
        ok=x.get('Atinge meta')=='Sim'
        items.append(f'''<div class="gitem {'ok' if ok else ''}"><div class="rank">0{i+1}</div><div><b>{_esc(x.get('Cenário'))}</b><span>{float(x.get('Throughput',0)):.2f} un/h · SLA {float(x.get('SLA',0)):.0f}% · custo/un R$ {float(x.get('Custo/un',0)):.2f}</span></div><div class="status">{'META' if ok else 'QUASE'}</div></div>''')
    doc=f'''<style>.goal{{background:#111A1D;border-radius:20px;padding:18px;color:#F7F7F3}}.head{{display:flex;justify-content:space-between;align-items:end;margin-bottom:12px}}.ey{{font-size:10px;letter-spacing:.16em;color:#FF8A4C;text-transform:uppercase;font-weight:800}}.tar{{font-size:12px;color:#91A29F}}.gitem{{display:grid;grid-template-columns:42px 1fr auto;align-items:center;gap:10px;border-top:1px solid #2A383B;padding:12px 4px}}.rank{{color:#617573;font-size:12px}}.gitem b{{display:block;font-size:13px}}.gitem span{{display:block;color:#93A39F;font-size:11px;margin-top:4px}}.status{{font-size:9px;letter-spacing:.12em;padding:4px 7px;border:1px solid #46575A;border-radius:99px;color:#A8B6B3}}.gitem.ok .status{{border-color:#3C8E69;color:#6FD09C;background:rgba(43,122,90,.12)}}</style><div class="goal"><div class="head"><div><div class="ey">Mission Control · Goal Seek</div><div style="font-size:20px;font-weight:800;margin-top:4px">Rotas para a meta</div></div><div class="tar">alvo: {target_tp:.2f} un/h · SLA {target_sla:.0f}%</div></div>{''.join(items)}</div>'''
    components.html(doc,height=100+len(items)*66,scrolling=False)
