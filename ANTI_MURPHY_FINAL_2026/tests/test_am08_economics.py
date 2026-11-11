from tempfile import TemporaryDirectory
from pathlib import Path
from copy import deepcopy
import json
import pytest
from atelier.service import Studio
from atelier.experiment_economics import normalize,compare
from simulation.numeric import metric
from simulation.nexus import current_analysis,selected_action


def archives(s):
    rows=s.info()['alternatives'];ref=next(x for x in rows if x['action']=='Não intervir');action=next(x for x in rows if x['action'].startswith('Manutenção expressa'))
    s.select(ref['signature']);a=s.save_experiment('Referência sem ação');s.select(action['signature']);b=s.save_experiment('Manutenção expressa');return a,b


def test_persist_components_exact_and_compare_without_double_investment(tmp_path):
    s=Studio(tmp_path);a,b=archives(s);e=b['economics'];analysis=current_analysis(s.state);row=selected_action(s.state,analysis)
    assert e['investment']==1800
    assert e['scenario_cost']==metric(row['result'],'total_cost')
    assert e['decision_cost']==pytest.approx(e['scenario_cost']+1800)
    assert e['savings']==pytest.approx(e['reference_cost']-e['decision_cost'])
    assert round(e['savings'],2)==4103.68
    c=s.compare_experiments(a['id'],b['id']);assert c['economics']['same_reference']
    assert c['economics']['delta']['decision_cost']==pytest.approx(-e['savings'])
    assert c['economics']['delta']['scenario_cost']==pytest.approx(-e['savings']-1800)
    assert c['delta']['total_cost']==c['economics']['delta']['scenario_cost']
    assert Studio(tmp_path).experiment_list()[0]['economics']['status']=='complete'


def test_zero_investment_is_explicit_and_negative_savings_supported(tmp_path):
    s=Studio(tmp_path);a,b=archives(s);assert a['economics']['investment']==0;assert a['economics']['savings']==0
    a['economics']['savings']=-123.456
    assert normalize(a)['savings']==-123.456
    assert compare(b,a)['delta']['savings']==pytest.approx(-123.456-b['economics']['savings'])


def test_legacy_comparison_never_rewrites_or_infers_investment(tmp_path):
    s=Studio(tmp_path);a,b=archives(s)
    for doc in [a,b]:
        doc.pop('economics');p=s.experiments_dir/(doc['id']+'.json');p.write_text(json.dumps(doc))
    originals={p:p.read_bytes() for p in s.experiments_dir.glob('*.json')}
    c=s.compare_experiments(a['id'],b['id']);e=c['economics']
    assert e['first']['scenario_cost']>0;assert not e['same_reference']
    for key in ['investment','decision_cost','savings']:assert e['first'][key] is None;assert e['delta'][key] is None
    for entry in s.experiment_list():assert entry['economics']['status']=='partial'
    assert all(p.read_bytes()==v for p,v in originals.items())


@pytest.mark.parametrize('value',[None,'bad',True,float('inf'),float('nan')])
def test_unknown_or_invalid_component_not_zero(value):
    doc={'economics':{'schema':'1.0','investment':value,'scenario_cost':10,'decision_cost':None,'savings':None,'reference_cost':20}}
    e=normalize(doc);assert e['investment'] is None;assert 'investment' in e['missing']


def test_partial_new_mixed_with_old_and_different_reference():
    old={'metrics':{'response':{'total_cost':5,'feasible':True},'incident':{'total_cost':10}}}
    new={'economics':{'schema':'1.0','scenario_cost':5,'reference_cost':10,'investment':0,'decision_cost':5,'savings':5,'reference_signature':'A'}}
    c=compare(old,new);assert c['delta']['scenario_cost']==0;assert c['delta']['investment'] is None
    other=deepcopy(new);other['economics']['reference_signature']='B';assert not compare(new,other)['same_reference']


def test_infeasible_does_not_appear_free():
    assert normalize({'metrics':{'response':{'total_cost':0,'feasible':False}}})['scenario_cost'] is None


def test_legacy_precision_and_missing_response():
    e=normalize({'metrics':{'incident':{'total_cost':10,'precise':{'total_cost':10.004}}}})
    assert e['scenario_cost']==10.004;assert e['investment'] is None


def test_different_models_warning_retained(tmp_path):
    s=Studio(tmp_path);a=s.save_experiment('Modelo anterior');m={'stations':deepcopy(s.info()['stations']),'orders':deepcopy(s.info()['orders'])};m['orders'][0]['quantidade']+=1;s.set_model(m);b=s.save_experiment('Modelo alterado')
    c=s.compare_experiments(a['id'],b['id']);assert not c['same_model'];assert not c['economics']['same_reference']


def test_real_capacity_action_archives_negative_net_saving(tmp_path):
    s=Studio(tmp_path)
    row=next(x for x in s.info()['alternatives'] if x['action']=='+1 máquina · CNC')
    s.select(row['signature']);saved=s.save_experiment('Capacidade adicional')
    assert saved['economics']['investment']==6500
    assert saved['economics']['savings']<0
    assert saved['economics']['decision_cost']==pytest.approx(saved['economics']['scenario_cost']+6500)
