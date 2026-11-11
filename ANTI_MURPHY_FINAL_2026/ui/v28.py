"""V28.1 War Room presentation — uses the official Anti-Murphy palette.

Only visual presentation lives here. It does not change any operational KPI.
"""
from __future__ import annotations

from html import escape


def war_room_hero(title: str, subtitle: str, detail: str) -> None:
    import streamlit as st

    title, subtitle, detail = (escape(str(x), quote=True) for x in (title, subtitle, detail))
    st.markdown(
        f"""
        <style>
        .am281-hero {{
            position:relative; overflow:hidden; border:1px solid #34454A;
            background:#1D292D; border-radius:17px; padding:28px 32px;
            color:#F7F7F3; box-shadow:none; margin:6px 0 22px;
        }}
        .am281-hero:before {{
            content:''; position:absolute; right:0; top:0; width:6px; height:100%;
            background:#FF681B;
        }}
        .am281-eyebrow {{font-size:11px;letter-spacing:.18em;font-weight:800;color:#FF681B;margin-bottom:9px;}}
        .am281-hero h2 {{font-size:29px;line-height:1.2;letter-spacing:-.04em;margin:0 0 8px;color:#F7F7F3!important;}}
        .am281-subtitle {{color:#F7F7F3;font-size:15px;font-weight:700;margin-bottom:9px;}}
        .am281-detail {{color:#CBD4D1;font-size:13px;line-height:1.65;max-width:880px;}}
        .am281-flow {{display:flex;gap:9px;align-items:center;margin-top:20px;flex-wrap:wrap;}}
        .am281-flow span {{font-size:11px;font-weight:750;letter-spacing:.05em;color:#F7F7F3;
           padding:8px 11px;border:1px solid #46585B;border-radius:7px;background:#26363A;}}
        .am281-flow i {{font-style:normal;color:#FF681B;font-weight:900;}}
        @media (max-width:900px) {{
          .am281-hero{{padding:21px 19px;}} .am281-hero h2{{font-size:23px;}}
        }}
        </style>
        <section class="am281-hero">
          <div class="am281-eyebrow">ANTI-MURPHY / OPERATIONAL DECISION TWIN / V28.1</div>
          <h2>{title}</h2>
          <div class="am281-subtitle">{subtitle}</div>
          <div class="am281-detail">{detail}</div>
          <div class="am281-flow">
            <span>01 · OPERAÇÃO</span><i>→</i>
            <span>02 · INCIDENTE</span><i>→</i>
            <span>03 · RECUPERAÇÃO</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
