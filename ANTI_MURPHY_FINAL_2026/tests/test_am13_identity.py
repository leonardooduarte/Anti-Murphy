import pytest
from atelier.decision_explainer import explain

def selected(ids):
 return {'order_impacts':[{'id':x,'due_h':i+1,'before_h':i+2,'after_h':i+1} for i,x in enumerate(ids)]}

@pytest.mark.parametrize('question,wanted', [('Quando termina o pedido OP-10?','OP-10'),('Prazo op-1.','OP-1'),('Pedido (OP-10)','OP-10'),('Pedido OP-10/A','OP-10/A'),('Pedido X.2','X.2')])
def test_exact_identifiers(question,wanted):
 ids=['OP-1','OP-10','OP-10/A','X.2']
 assert explain(question,{'incident':{}},selected(ids),ids)['text'].startswith('Pedido '+wanted+' ·')

def test_multiple_ids_require_disambiguation():
 ids=['OP-1','OP-10'];text=explain('Compare pedido OP-1 e OP-10',{'incident':{}},selected(ids),ids)['text']
 assert 'mais de um' in text

def test_unknown_longer_id_is_not_prefix_match():
 assert 'não existe' in explain('Prazo do pedido OP-100?',{'incident':{}},selected(['OP-1','OP-10']),['OP-1','OP-10'])['text']

@pytest.mark.parametrize('objective',['cost','delivery','critical'])
def test_choice_reuses_engine_leader_without_reranking(objective):
 cheap={'signature':'C','action':'Barata','decision_cost':1,'sla_pct':80,'feasible':True,'within_budget':True,'meets_sla':True}
 fast={**cheap,'signature':'F','action':'Rápida','decision_cost':100,'sla_pct':100}
 a={'incident':{},'rows':[cheap,fast],'leader':fast,'objective':objective,'selection_reason':'Critério registrado pelo motor.'}
 text=explain('Qual escolher?',a,cheap,[])['text']
 assert '"Rápida"' in text and 'Critério registrado pelo motor' in text

def test_no_delivery_leader_does_not_invent_cost_recommendation():
 row={'action':'Barata','decision_cost':1,'feasible':True,'within_budget':True,'meets_sla':True}
 text=explain('Qual escolher?',{'incident':{},'rows':[row],'objective':'delivery'},row,[])['text']
 assert 'não apontou' in text
