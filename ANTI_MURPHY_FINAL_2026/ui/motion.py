"""Isolated, dependency-free motion component with deterministic trace data."""
from pathlib import Path
import json
import streamlit as st
import streamlit.components.v1 as components
from simulation.replay import replay_payload
ROOT=Path(__file__).resolve().parent/'motion'


def twin_html(normal, data=None, action=None, *, pitch=False, reduced=False):
    payload={'normal':replay_payload(normal),'pitch':pitch,'reduced':reduced}
    if data:
        payload['incident']=replay_payload(data['incident'])
        payload['action_count']=len([r for r in data['rows'] if r['action']!='Não intervir'])
        if action:
            payload['response']=replay_payload(action['result'])
            payload['action']={k:action[k] for k in ('action','investment','savings','makespan_h','sla_pct')}
    safe=json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return (ROOT/'twin.html').read_text().replace('__CORE__',(ROOT/'replay-core.js').read_text()).replace('__PAYLOAD__',safe)


def render_twin(normal, data=None, action=None, *, pitch=False, reduced=False):
    html=twin_html(normal,data,action,pitch=pitch,reduced=reduced)
    if hasattr(st,'iframe'):
        st.iframe(html,height='content',alt='Murphy Motion: replay interativo dos eventos da simulação')
    else:
        components.html(html,height=840 if pitch else 670,scrolling=True)
