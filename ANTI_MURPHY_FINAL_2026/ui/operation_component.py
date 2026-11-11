"""Local bidirectional frontend; no network asset or frontend build at installation."""
from pathlib import Path
import streamlit.components.v1 as components

_component=components.declare_component('anti_murphy_operation',path=str(Path(__file__).with_name('operation').resolve()))


def render_operation(data):
    return _component(data=data,key='operation_workspace',default=None)
