import streamlit as st


def render_flow(result):
    rows = {r["Posto"]: r for r in result["stations"]}
    max_queue = max([max(1, float(r["Fila máx."])) for r in rows.values()] or [1])
    parts = []
    for sid, r in rows.items():
        util = r["Utilização máquina (%)"]
        is_bottleneck = sid == result.get("bottleneck")
        color = "#C94A0A" if is_bottleneck else ("#3F8E89" if util < 70 else "#78684B")
        extra = '<div class="bottleneck-tag">EVENTO MURPHY</div>' if is_bottleneck else ''
        cls = "flow-card bottleneck" if is_bottleneck else "flow-card"
        pressure = min(100.0, 14 + 86 * (float(r["Fila máx."]) / max_queue)) if float(r["Fila máx."]) > 0 else 4
        parts.append(
            f'<div class="flow-node"><div class="{cls}"><div class="flow-id">{sid}</div>'
            f'<div class="flow-name">{r["Nome"]}</div><div class="flow-util" style="color:{color}">{util:.1f}%</div>'
            f'<div class="flow-meta"><span class="pill">{r["Máquinas"]} maq.</span><span class="pill">{r["Operadores"]} op.</span></div>'
            f'{extra}<div class="pressure"><div class="pressure-top"><span>pressão</span><span>{r["Fila máx."]} fila</span></div><div class="pressure-bar"><div class="pressure-fill" style="width:{pressure:.0f}%"></div></div></div>'
            f'<div class="flow-note">espera {r["Espera média (min)"]:.1f} min</div></div></div>'
        )
    html = (
        '<div class="flow-shell"><div class="flow-topline"><div><span class="flow-label">Rede operacional</span>'
        '<span class="live-badge"><i></i> DIGITAL TWIN LIVE</span></div>'
        '<div class="flow-legend">laranja = <b>restrição / perturbação</b></div></div>'
        '<div class="flow-wrap"><div class="flow-runner"></div>' + ''.join(parts) + '</div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)
