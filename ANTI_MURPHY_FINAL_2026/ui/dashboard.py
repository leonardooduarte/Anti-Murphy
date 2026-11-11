from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from simulation.metrics import compare_results, fingerprint, murphy_score

PAPER = "rgba(0,0,0,0)"
TEXT = "#66736E"
GRID = "#DDE3DF"
NAVY = "#102025"
ORANGE = "#F5662C"
TEAL = "#3D9D92"


def utilization_chart(result):
    df = pd.DataFrame(result["stations"])
    fig = go.Figure()
    fig.add_bar(x=df["Posto"], y=df["Utilização máquina (%)"], name="Máquina", marker_color="#A7B0AD")
    fig.add_bar(x=df["Posto"], y=df["Utilização mão de obra (%)"], name="Mão de obra", marker_color=TEAL)
    fig.update_layout(
        barmode="group", height=330, margin=dict(l=18,r=18,t=35,b=20),
        paper_bgcolor=PAPER, plot_bgcolor=PAPER,
        font=dict(color=TEXT, family="Aptos, Segoe UI, sans-serif", size=11), legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        yaxis=dict(range=[0,105], gridcolor=GRID, zeroline=False, title="Utilização (%)"),
        xaxis=dict(gridcolor=GRID, linecolor=GRID),
        bargap=.28,
    )
    return fig


def compare_bar(base, alt):
    """Comparação indexada (Base=100) para não misturar escalas incompatíveis."""
    metrics = ["Throughput", "SLA", "Custo/un", "Makespan"]
    b_raw = [float(base["throughput_h"]), float(base["sla_pct"]), float(base["unit_cost"]), float(base["makespan_h"])]
    a_raw = [float(alt["throughput_h"]), float(alt["sla_pct"]), float(alt["unit_cost"]), float(alt["makespan_h"])]
    b = [100.0] * 4
    a = [(av / bv * 100.0) if abs(bv) > 1e-9 else 100.0 for av, bv in zip(a_raw, b_raw)]
    fig = go.Figure()
    fig.add_bar(name="Base · índice 100", x=metrics, y=b, marker_color="#B6BFBC", customdata=b_raw, hovertemplate="%{x}<br>Base: %{customdata:.2f}<br>Índice: 100<extra></extra>")
    fig.add_bar(name=alt["name"], x=metrics, y=a, marker_color=NAVY, customdata=a_raw, text=[f"{v:.0f}" for v in a], textposition="outside", hovertemplate="%{x}<br>Cenário: %{customdata:.2f}<br>Índice: %{y:.1f}<extra></extra>")
    fig.add_hline(y=100, line_dash="dot", line_color="#AFA89D")
    fig.update_layout(
        title="Comparação normalizada · Base = 100", barmode="group", height=350, margin=dict(l=18,r=18,t=55,b=20),
        paper_bgcolor=PAPER, plot_bgcolor=PAPER, font=dict(color=TEXT, family="Aptos, Segoe UI, sans-serif", size=11),
        yaxis=dict(gridcolor=GRID, zeroline=False, title="Índice relativo"), xaxis=dict(linecolor=GRID), bargap=.30,
        legend=dict(orientation="h", y=1.15, x=0),
    )
    return fig


def radar(base, alt):
    fb = fingerprint(base, base)
    fa = fingerprint(alt, base)
    cats = list(fb.keys())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=list(fb.values())+[list(fb.values())[0]], theta=cats+[cats[0]], fill="toself", name="Base", line=dict(color="#AAB2B0"), fillcolor="rgba(170,178,176,.16)"))
    fig.add_trace(go.Scatterpolar(r=list(fa.values())+[list(fa.values())[0]], theta=cats+[cats[0]], fill="toself", name=alt["name"], line=dict(color=NAVY), fillcolor="rgba(29,41,45,.14)"))
    fig.update_layout(height=370, margin=dict(l=35,r=35,t=40,b=35), paper_bgcolor=PAPER, font=dict(color=TEXT, family="Aptos, Segoe UI, sans-serif", size=11), polar=dict(bgcolor=PAPER, radialaxis=dict(range=[0,100], gridcolor=GRID, showticklabels=False), angularaxis=dict(gridcolor=GRID)))
    return fig


def render_delta(base, alt):
    d = compare_results(base, alt)
    st.markdown(f"""
    <div class="insight"><b>Leitura do cenário:</b> throughput <b>{d['throughput_pct']:+.1f}%</b>, SLA <b>{d['sla_pp']:+.1f} p.p.</b>, custo unitário <b>{d['unit_cost_pct']:+.1f}%</b> e makespan <b>{d['makespan_pct']:+.1f}%</b>. O gargalo passa a ser <b>{alt['bottleneck']}</b>.</div>
    """, unsafe_allow_html=True)


def score_label(result):
    return murphy_score(result)
