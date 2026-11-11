"""Isolated Factory Command integration test entry (does not replace V30.2 pages)."""
from pathlib import Path
import streamlit as st
from bridge.factory_command_component import read_validated_bundle, factory_command_view
ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Anti-Murphy · Factory Command', layout='wide')
st.title('Factory Command · Futuros Paralelos')
st.caption('Reprodução de dados sintéticos calculados pela V30.2. Sem ligação com chão de fábrica real.')
if st.button('Regerar comparação no motor V30.2'):
    from tools.export_factory_command import demo_scenario
    from simulation.trace_export import export_comparison_json
    cfg, action = demo_scenario()
    export_comparison_json(cfg, action, ROOT / "simulation_snapshot.json",
                           keyframe_every=20, experiment_id="FC-V302-THREE-STATIONS")
    st.rerun()
try:
    bundle=read_validated_bundle(ROOT/'simulation_snapshot.json')
except (OSError,ValueError) as exc:
    st.error(f'Não foi possível abrir o snapshot: {exc}')
    st.stop()
result=factory_command_view(bundle,key='fc_split_futures')
if result is not None and getattr(result,'selected_station',None):
    st.caption(f'Posto selecionado no Canvas: {result.selected_station}')
st.warning('Viabilidade industrial não verificada: buffers e setup por sequência ainda não são impostos pelo motor.')
