"""Finite set diagnostics: do not confuse Pareto with industrial validation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from atelier.decision_quality import review_alternatives
from atelier.service import Studio


def row(name, cost, h, sla, *, eligible=True):
    return dict(signature=name, action=name, decision_cost=cost, makespan_h=h, sla_pct=sla,
                feasible=eligible, within_budget=eligible, meets_sla=eligible)


def test_dominance_detected_across_three_objectives():
    out=review_alternatives([row('express', 11983,21.30,100),row('worker',10193,17.85,100)],'express')
    assert out['status']=='dominated'
    assert out['dominated_by'][0]['signature']=='worker'
    assert out['physical_feasibility_verified'] is False


def test_tradeoff_does_not_claim_dominance():
    out=review_alternatives([row('express', 11983,21.30,100),row('fast',10900,19.00,80)],'express')
    assert out['status']=='non_dominated'


def test_unverified_or_outside_criteria_rival_not_used():
    out=review_alternatives([row('a', 11000,22,100),row('b',9500,19,100,eligible=False)],'a')
    assert out['status']=='non_dominated'
    out=review_alternatives([row('a', 11000,22,100,eligible=False)],'a')
    assert out['status']=='outside_criteria'


def test_missing_or_nonfinite_data_safe():
    out=review_alternatives([row('a',11000,22,100),row('b',float('nan'),19,100)],'a')
    assert out['status']=='non_dominated'
    assert review_alternatives([],None)['status']=='unknown'


def test_service_model_integration_and_record_snapshot():
    with TemporaryDirectory() as tmp:
        app=Studio(Path(tmp))
        state=app.info()
        assert state['decision_review']['status'] in {'dominated','non_dominated','outside_criteria','unknown'}
        assert state['decision_review']['evaluated_count']==len(state['alternatives'])
        recorded=app.decision({'signature':state['selected'],'note':'Critérios comparados; verificar restrições operacionais.',
                              'risks':'Habilitação e custos evitáveis pendentes.','constraints_ack':True})
        assert recorded['record']['decision_review']==state['decision_review']
        archive=app.read_history(recorded['filename'])
        assert archive['record']['decision_review']['physical_feasibility_verified'] is False
