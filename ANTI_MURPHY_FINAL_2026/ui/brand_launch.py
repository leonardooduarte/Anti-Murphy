"""Original V8 launch mark, restored as a nonblocking entrance to the real app."""
from __future__ import annotations
import base64
from pathlib import Path
import streamlit as st

BRAND = Path(__file__).resolve().parents[1] / 'assets' / 'brand'

def reveal_once(force: bool = False) -> None:
    if st.session_state.get('am_intro_seen') and not force:
        return
    st.session_state.am_intro_seen = True
    icon = base64.b64encode((BRAND / 'icon-dark.svg').read_bytes()).decode('ascii')
    # The image is the original logo asset; not a redrawn version.
    st.markdown(f"""<style>
    @keyframes amBrandEnter {{ 0% {{ opacity:0; transform:translateY(21px) scale(.88) }} 42% {{opacity:1; transform:translateY(0) scale(1)}} 100% {{opacity:1}} }}
    @keyframes amBrandExit {{ 0%,73% {{opacity:1; visibility:visible}} 100% {{opacity:0; visibility:hidden}} }}
    @keyframes amBrandLine {{from {{transform:scaleX(0)}} to {{transform:scaleX(1)}}}}
    .am-original-intro{{position:fixed;inset:0;z-index:999999;display:flex;align-items:center;justify-content:center;background:#1D292D;animation:amBrandExit 2.3s ease both;pointer-events:none}}
    .am-intro-center{{display:flex;flex-direction:column;align-items:center;gap:15px;animation:amBrandEnter 1.1s cubic-bezier(.2,.8,.25,1) both}}
    .am-intro-center img{{width:112px;height:112px;object-fit:contain;filter:drop-shadow(0 12px 22px rgba(0,0,0,.2))}}
    .am-intro-center strong{{font-size:24px;letter-spacing:.13em;color:#F7F7F3;font-family:Segoe UI,Arial,sans-serif;font-weight:700}}
    .am-intro-line{{height:3px;width:138px;background:#FF681B;transform-origin:left;animation:amBrandLine 1.3s ease-out both}}
    @media(prefers-reduced-motion:reduce){{.am-original-intro{{animation:amBrandExit .01s linear both}}.am-intro-center,.am-intro-line{{animation:none}}}}
    </style><div class="am-original-intro" aria-hidden="true"><div class="am-intro-center"><img src="data:image/svg+xml;base64,{icon}" alt=""><strong>ANTI-MURPHY</strong><div class="am-intro-line"></div></div></div>""", unsafe_allow_html=True)
