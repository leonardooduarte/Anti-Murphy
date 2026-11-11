"""Unified V29.1 high-contrast dark theme; appended once after legacy component styles.

Legacy components still use their original class names. This compatibility layer
makes them adhere to the official brand tokens without modifying the SVG assets.
No custom fonts and no externally loaded assets.
"""
from __future__ import annotations
from pathlib import Path

CSS = r"""
:root {
  --am-bg: #0C1518; --am-panel: #142227; --am-raised: #1D292D;
  --am-stroke: #334A4D; --am-orange: #FF681B; --am-text: #F7F7F3;
  --am-muted: #B9CBC7; --am-muted-2: #99B0AB;
  --ai-paper: var(--am-panel); --ai-line: var(--am-stroke);
  --v24-paper: var(--am-panel); --v24-ink: var(--am-text);
  --v24-line: var(--am-stroke); --v24-muted: var(--am-muted);
}
html, body, .stApp, [data-testid="stAppViewContainer"] { background:var(--am-bg)!important; color:var(--am-text)!important; }
[data-testid="stHeader"] {background:var(--am-bg)!important;}
/* Chat: fix V22's white-background + light-text contradiction */
[data-testid="stChatMessage"] {
  background:var(--am-panel)!important; border:1px solid var(--am-stroke)!important;
  border-radius:14px!important; padding:13px 16px!important; margin:9px 0!important;
  color:var(--am-text)!important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] a,
[data-testid="stChatMessage"] code {
  color:var(--am-text)!important; font-size:0.92rem!important; line-height:1.65!important;
}
[data-testid="stChatMessage"] a { text-decoration:underline!important; text-decoration-color:var(--am-orange)!important; }
[data-testid="stChatMessage"] code,
[data-testid="stChatMessage"] pre {background:#0D1B20!important; border:1px solid #345055!important;}
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] textarea {
  background:#1A2A2F!important; color:var(--am-text)!important; border-color:var(--am-stroke)!important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stTextInput"] input::placeholder {color:var(--am-muted-2)!important; opacity:1!important;}
[data-testid="stChatInput"] button {color:var(--am-orange)!important;}
/* Legacy AI cards and explanations */
.am-ai-stat, .am-ai-context>div, .am-ai-mode, .am-ai-note {
  background:var(--am-panel)!important; border-color:var(--am-stroke)!important;
  color:var(--am-text)!important;
}
.am-ai-stat .v, .am-ai-context .v {color:var(--am-text)!important; font-size:0.94rem!important;}
.am-ai-stat .k,.am-ai-context .k,.am-ai-stat .s,.am-ai-mode,.am-ai-note {color:var(--am-muted)!important;font-size:0.79rem!important;}
.am-ai-copy,.am-ai-action .s{font-size:.87rem!important;line-height:1.6!important;}
.am-ai-ey,.am-ai-action .k {font-size:.68rem!important;}
.am-ai-title {font-size:1.8rem!important;}
.am-ai-pill {font-size:.73rem!important;}
/* Formerly white legacy component families */
.v24-section:not(.dark), .v24-kpi,.v24-trust-grid>div:not(.lead),
.v24-agent>div,.v24-rule>div:not(.lead),.v24-maint>div:not(.lead),
.am26-strip,.am26-card,.am26-trustdims>div,.am26-ai,
.v23-thread-card, .v25-leader, .v25-digest, .v26-card,
.am16-metric, .am16-review-card, .v20-panel, .v21-confidence {
  background:var(--am-panel)!important; border-color:var(--am-stroke)!important;
  color:var(--am-text)!important;
}
.v24-section .v24-title,.v24-trust-grid .v,.v24-kpi .v,.v24-agent .t,
.v24-rule .v,.v24-maint .v,.am26-card h4,.am26-card .metrics b,
.am26-strip .v,.am26-trustdims b, .am26-ai b,
.v23-thread-card .v,.v25-leader .v {color:var(--am-text)!important;}
.v24-copy,.v24-agent .s,.v24-rule .k,.v24-maint .k,.v24-trust-grid .s,
.v24-kpi .k,.v24-kpi .s,.am26-card .metrics span,.am26-tag,.am26-ai span,
.am26-strip .s {color:var(--am-muted)!important;}
.v24-agent .t,.v24-rule .v,.v24-maint .v,.v24-trust-grid .v{font-size:0.85rem!important;}
.v24-agent .s,.v24-trust-grid .s,.v24-kpi .s,.v24-copy{font-size:0.78rem!important;}
.am26-tag{border-color:var(--am-stroke)!important;}
/* Evidence dashboard: no misleading composite "100/100 trust" */
.am26-trust-intro{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 14px;background:var(--am-panel);border:1px solid var(--am-stroke);border-radius:10px 10px 0 0;color:var(--am-text)}
.am26-trust-intro small{color:var(--am-muted)}
.am26-trust-hint{display:block;color:var(--am-muted);font-size:.74rem;margin-top:8px;line-height:1.5}
.am26-trust-dims-only .am26-trustdims{grid-template-columns:repeat(4,minmax(0,1fr));}
.am26-trust-dims-only .am26-trustdims>div{min-height:125px;}
/* Native inputs/data presentation */
[data-testid="stDataFrame"], [data-testid="stDataEditor"],
[data-testid="stExpander"],[data-testid="stForm"] {
  background:var(--am-panel)!important; border:1px solid var(--am-stroke)!important;
}
[data-testid="stDataFrame"] *,[data-testid="stDataEditor"] *{color-scheme:dark;}
[data-baseweb="popover"]>div,[data-baseweb="menu"],
[role="listbox"], [role="option"],
[data-baseweb="select"]>div,[data-baseweb="input"]>div,
[data-baseweb="textarea"]>div, input, textarea {
  background:#1B2D31!important; color:var(--am-text)!important;
  border-color:var(--am-stroke)!important;
}
[role="option"]:hover,[aria-selected="true"][role="option"]{background:#314347!important;}
[data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] p {
  color:var(--am-muted)!important; font-size:0.82rem!important;
}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
  font-size:0.9rem!important; line-height:1.6!important;
}
[data-testid="stAlert"]{border:1px solid var(--am-stroke)!important;color:var(--am-text)!important;}
[data-testid="stAlert"] p {color:var(--am-text)!important;}
/* sidebar readability / consistency */
.st-key-am16_navrail .stButton>button {color:var(--am-text)!important;font-size:.82rem!important;}
.st-key-am16_navrail .am16-side-sec {color:var(--am-muted)!important;font-size:.68rem!important;}
/* Focus visibility */
button:focus-visible,input:focus-visible,textarea:focus-visible {
  outline:2px solid var(--am-orange)!important; outline-offset:2px!important;
}
@media (max-width:1000px) {
  .am26-trust,.v24-maint,.v24-agent,.am26-cardgrid {grid-template-columns:repeat(2,minmax(0,1fr))!important;}
}
@media (max-width:640px) {
  .am26-trust,.v24-maint,.v24-agent,.am26-cardgrid {grid-template-columns:1fr!important;}
  [data-testid="stChatMessage"] {padding:10px 12px!important;}
  .block-container{padding:1rem .7rem 3rem!important;}
}
"""


def inject_design_system():
    import streamlit as st
    compatibility=Path(__file__).with_name('legacy_dark.css').read_text(encoding='utf-8')
    st.markdown('<style id="anti-murphy-design-system-v291">' + CSS + compatibility + '</style>', unsafe_allow_html=True)
