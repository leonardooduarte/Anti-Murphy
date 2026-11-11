"""Factory Command Streamlit v2 bridge. Streamlit >=1.66.

The *full* ComparisonBundle is validated by Pydantic before passing to the UI.
Only a station selection goes back to Streamlit; frames never trigger Python.
"""
from pathlib import Path
import json
from simulation_contract import ComparisonBundle, validate_reconstruction

HERE = Path(__file__).resolve().parent
FRONTEND_DIR = HERE.parent / 'frontend' / 'dist-component'


def read_validated_bundle(path: str | Path) -> dict:
    parsed = ComparisonBundle.model_validate_json(Path(path).read_text(encoding='utf-8'))
    validate_reconstruction(parsed)
    return parsed.model_dump(mode='json', by_alias=True)


def factory_command_view(bundle: dict, *, key: str = 'factory_command') -> object:
    import streamlit as st
    if not FRONTEND_DIR.joinpath('factory_command.js').is_file():
        st.error('Canvas React não compilado. Execute npm install e npm run build:component em frontend/.')
        return None
    script = (FRONTEND_DIR / 'factory_command.js').read_text(encoding='utf-8')
    css_files = list(FRONTEND_DIR.glob('*.css'))
    css = '\n'.join(p.read_text(encoding='utf-8') for p in css_files)
    component = st.components.v2.component(
        name='anti_murphy.factory_command',
        html='<div id="anti-murphy-factory-command"></div>',
        css=css,
        js=script,
        isolate_styles=True,
    )
    return component(data={'bundle':bundle}, key=key, on_selected_station_change=lambda:None)
