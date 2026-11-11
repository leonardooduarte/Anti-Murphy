"""Regressions for read-only dashboards projected from cached simulation results."""
from pathlib import Path
from tempfile import TemporaryDirectory
from atelier.service import Studio
from simulation.nexus import current_analysis, selected_action


def test_dashboards_are_live_and_read_only():
    with TemporaryDirectory() as root:
        studio=Studio(Path(root))
        before=studio.info()
        d=studio.dashboards()
        after=studio.info()
        assert d['run_id']==before['run_id']==after['run_id']
        assert d['model_hash'] and len(d['model_hash'])==64
        assert before['selected']==after['selected']
        assert {'normal','incident','response'}<=set(d['scenarios'])
        analysis=current_analysis(studio.state)
        for key in ('normal','incident'):
            scenario=d['scenarios'][key]
            assert scenario['stations']==analysis[key]['stations']
            assert scenario['orders']==analysis[key]['orders']
            assert scenario['metrics']['total_cost']==analysis[key]['total_cost']
            assert scenario['metrics']['late_orders']==analysis[key]['late_orders']
            assert scenario['cost_breakdown']==analysis[key]['cost_breakdown']
        selected=selected_action(studio.state,analysis)
        assert d['scenarios']['response']['metrics']['sla_pct']==selected['result']['sla_pct']
        assert d['selected']==selected['signature']


def test_dashboard_updates_on_new_decision():
    with TemporaryDirectory() as root:
        studio=Studio(Path(root))
        before=studio.dashboards()
        choices=[a for a in studio.info()['alternatives'] if a['signature']!=before['selected']]
        assert choices
        studio.select(choices[0]['signature'])
        after=studio.dashboards()
        assert after['selected']==choices[0]['signature']
        assert after['selected']!=before['selected']
        assert after['run_id']==before['run_id']
        assert after['scenarios']['response']['metrics']==studio.info()['metrics']['response']


def test_dashboard_after_switching_model_changes_reference():
    with TemporaryDirectory() as root:
        studio=Studio(Path(root))
        before=studio.dashboards()
        clone=studio.create_project('Projeto auxiliar',duplicate=True)
        after=studio.dashboards()
        assert before['project_id']!=after['project_id']
        assert after['project_id']==clone['active_project_id']
        assert after['scenarios']['normal']['metrics']['feasible'] is True
        assert len(after['scenarios']['normal']['orders'])==len(clone['orders'])
