"""Self-contained executive export built exclusively from a signed analysis."""
from html import escape as h
from datetime import datetime, timezone
from simulation.nexus_ai import brl,fmt


def executive_html(data,action=None):
    leader=action or data.get('leader');n=data['normal'];i=data['incident']
    rows=''.join('<tr>'+''.join('<td>'+h(str(v))+'</td>' for v in [r['action'],r.get('verdict',''),brl(r['investment']),brl(r['decision_cost']) if r['decision_cost'] is not None else 'Não calculado',
         brl(r['savings']) if r['savings'] is not None else 'Não calculado',fmt(r['sla_pct'])+'%',fmt(r['makespan_h'])+' h'])+'</tr>' for r in data['rows'])
    choice=(f"{leader['action']} · investimento {brl(leader['investment'])} · custo final {brl(leader['decision_cost'])} · economia líquida vs incidente {brl(leader['savings'])}. "
            f"SLA {fmt(leader['sla_pct'])}% · prazo {fmt(leader['makespan_h'])} h. Veredito: {leader.get('verdict','')}. {leader.get('verdict_reason','')}" if leader else 'Nenhuma resposta selecionada. '+data['policy_explanation'])
    assumptions=''.join('<li>'+h(str(a))+'</li>' for a in data.get('assumptions',[])+data.get('evaluation_assumptions',[]))
    p=data['incident_parameters']
    return f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Anti-Murphy · Evidência de decisão</title>
<style>body{{font:15px/1.65 system-ui,sans-serif;color:#1D292D;max-width:1200px;margin:45px auto;padding:0 25px}}header{{border-bottom:3px solid #FF681B;padding-bottom:18px}}small{{color:#536066}}h1{{font-size:36px;letter-spacing:-1px}}.callout{{background:#f2f3ed;border-left:4px solid #FF681B;padding:20px;margin:25px 0}}table{{border-collapse:collapse;width:100%;font-size:12px}}th,td{{border-bottom:1px solid #d4dad7;padding:10px;text-align:left}}th{{background:#1D292D;color:#F7F7F3}}@media print{{body{{margin:15px}}tr{{break-inside:avoid}}}}</style>
<header><small>ANTI-MURPHY V30 / NEXUS · RESULTADOS DO MODELO</small><h1>Evidência de decisão</h1><div>Experimento {h(data['run_id'])} · modelo {h(data['baseline_signature'])}</div></header>
<p><b>Incidente:</b> {h(p['station'])}, início {fmt(p['start_h'])} h, duração {fmt(p['duration_h'])} h.</p>
<p><b>Nominal:</b> {brl(n['total_cost'])} · SLA {fmt(n['sla_pct'])}% · {fmt(n['makespan_h'])} h.<br><b>Sem intervenção:</b> {brl(i['total_cost'])} · SLA {fmt(i['sla_pct'])}% · {fmt(i['makespan_h'])} h.</p>
<div class="callout"><b>{h("ALTERNATIVA EXAMINADA" if action else data["policy_status"])}</b><p>{h(choice)}</p></div>
<h2>Alternativas calculadas</h2><table><thead><tr><th>Ação</th><th>Veredito</th><th>Investimento</th><th>Custo total + implantação</th><th>Economia líquida</th><th>SLA</th><th>Conclusão</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Premissas e limites</h2><ul>{assumptions}</ul><p>Simulação sintética ou alimentada por dados do usuário. Validação com dados reais: PENDENTE. Nenhuma decisão física foi executada. Não é otimização global.</p>
<small>Gerado em {datetime.now(timezone.utc).isoformat()} · Valores por carteira; economia já desconta a implantação.</small></html>'''.encode('utf-8')
