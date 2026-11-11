"""UI smoke test with a Streamlit double, no GUI dependency."""
from __future__ import annotations
import ast
from pathlib import Path
from contextlib import nullcontext
from data.scenarios import STATIONS_BASE, ORDERS_BASE
from simulation.factory import build_scenario
from simulation.engine import run_simulation
from simulation.atlas import analyze_incident
from simulation.ai_orchestrator import diagnose_operation,response_playbook
from simulation.decision_council import blocked_station_fixes
from simulation.decision_lab import config_signature

ROOT=Path(__file__).resolve().parents[1]
class Col:
    def __enter__(self):return self
    def __exit__(self,*args):return False
class State(dict):
    def __getattr__(self,k):return self[k]
    def __setattr__(self,k,v):self[k]=v
class Fake:
    def __init__(self,**kwargs):
        self.session_state=State(stations=STATIONS_BASE,orders=ORDERS_BASE,scenario_result=None,audit_log=[],**kwargs)
        self.calls=[]
    def columns(self,n,**kw):return [Col() for _ in range(n if isinstance(n,int) else len(n))]
    def container(self,**kw):return Col()
    def expander(self,*args,**kw):return Col()
    def slider(self,*a,**kw):return kw.get('value',80)
    def selectbox(self,lab,opts,**kw):return opts[kw.get('index',0)]
    def number_input(self,*a,**kw):return kw.get('value',0.)
    def button(self,*a,**kw):return False
    def markdown(self,*a,**kw):self.calls.append(('markdown',a))
    def caption(self,*a,**kw):self.calls.append(('caption',a))
    def dataframe(self,*a,**kw):self.calls.append(('dataframe',a))
    def plotly_chart(self,*a,**kw):self.calls.append(('chart',a))
    def download_button(self,*a,**kw):self.calls.append(('download',a))
    def info(self,*a,**kw):self.calls.append(('info',a))
    def warning(self,*a,**kw):self.calls.append(('warning',a))
    def success(self,*a,**kw):self.calls.append(('success',a))
    def error(self,*a,**kw):self.calls.append(('error',a))
    def rerun(self):raise AssertionError('Unexpected rerun')


def _war_block():
    tree=ast.parse((ROOT/'legacy_app.py').read_text(encoding='utf-8'))
    blocks=[node for node in ast.walk(tree) if isinstance(node,ast.If) and ast.unparse(node.test)=="page == 'War Room'"]
    assert len(blocks)==1
    code=ast.Module(body=blocks[0].body,type_ignores=[])
    return compile(ast.fix_missing_locations(code),'app.py','exec')


def run_smoke(analysis=None):
    import pandas as pd
    st=Fake(v29_analysis=analysis)
    cfg=build_scenario('Base',STATIONS_BASE,ORDERS_BASE)
    b=run_simulation(cfg)
    visuals=[]
    def vis(name,arity):
        def _render(*args,**kw):
            assert len(args)==arity,(name,len(args),arity)
            visuals.append(name)
        return _render
    ns={'st':st,'ensure_base':lambda:b, 'current_atlas_analysis':lambda:analysis,
        'diagnose_operation':diagnose_operation,'blocked_station_fixes':blocked_station_fixes,
        'response_playbook':response_playbook,'atlas_hero':lambda *a,**kw:visuals.append('hero'),
        'atlas_kpi_strip':vis('kpi',1),'atlas_stage':vis('stage',3),
        'atlas_plant_flow':vis('plant',3),'atlas_signal':vis('signal',2),
        'atlas_comparison_chart':lambda *a,**kw:'chart','atlas_frontier_chart':lambda *a,**kw:'chart',
        'decision_memo':lambda a:b'{}','pd':pd, 'run_atlas':lambda *a:None}
    exec(_war_block(),ns)
    assert 'hero' in visuals and 'plant' in visuals and visuals.count('stage')==3
    if analysis:
        assert 'signal' in visuals and any(k=='chart' for k,_ in st.calls)
    return st


def test_war_room_initial_ui_renders_without_typeerror():run_smoke()
def test_war_room_after_simulation_ui_renders():
    cfg=build_scenario('Base',STATIONS_BASE,ORDERS_BASE)
    data=analyze_incident(cfg,'CNC',4,5)
    run_smoke(data)


def test_model_signature_changed_invalidates_old_view():
    cfg=build_scenario('Base',STATIONS_BASE,ORDERS_BASE)
    a=analyze_incident(cfg,'CNC',4,5)
    cfg.stations['CNC']['operadores']+=1
    assert a['baseline_signature']!=config_signature(cfg)
