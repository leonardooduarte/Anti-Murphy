from pathlib import Path
import tempfile
import unittest
from copy import deepcopy
from atelier.service import Studio, StudioError
from simulation.replay import snapshot

class IntegratedWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.studio=Studio(Path(self.tmp.name))
    def tearDown(self):self.tmp.cleanup()

    def test_existing_motor_and_alternatives(self):
        d=self.studio.info()
        self.assertEqual(len(d['stations']),5)
        self.assertEqual(len(d['orders']),5)
        self.assertGreaterEqual(len(d['alternatives']),10)
        self.assertEqual(d['metrics']['incident']['late_orders'],3)
        self.assertEqual(d['metrics']['normal']['late_orders'],0)

    def test_replay_states_and_same_timeline(self):
        d=self.studio.info()
        a=d['replay']['incident'];b=d['replay']['response']
        self.assertEqual(list(x['id'] for x in a['stations']),list(x['id'] for x in b['stations']))
        self.assertEqual(snapshot(a,0)['stations'],snapshot(b,0)['stations'])
        self.assertGreater(a['horizon'],0)

    def test_action_selection_updates_response(self):
        d=self.studio.info()
        signature=next(a['signature'] for a in d['alternatives'] if a['action']=='Não intervir')
        updated=self.studio.select(signature)
        self.assertEqual(updated['selected'],signature)
        self.assertEqual(updated['metrics']['incident']['total_cost'],updated['metrics']['response']['total_cost'])

    def test_edit_persist_model_and_recalculate(self):
        d=self.studio.info();m={'stations':deepcopy(d['stations']),'orders':deepcopy(d['orders'])}
        m['orders'][0]['quantidade']=23
        x=self.studio.set_model(m)
        self.assertEqual(x['orders'][0]['quantidade'],23)
        self.assertIsNotNone(x['run_id'])
        reopened=Studio(Path(self.tmp.name)).info()
        self.assertEqual(reopened['orders'][0]['quantidade'],23)

    def test_bad_model_cannot_overwrite(self):
        old=self.studio.info()['orders']
        with self.assertRaises(StudioError):self.studio.set_model({'stations':{},'orders':old})
        self.assertEqual(self.studio.info()['orders'],old)

    def test_all_lab_modes(self):
        self.assertEqual(len(self.studio.lab({'mode':'duration'})['points']),7)
        self.assertEqual(len(self.studio.lab({'mode':'dispatch'})['points']),3)
        self.assertEqual(len(self.studio.lab({'mode':'robustness'})['pairs']),6)
        self.assertGreaterEqual(len(self.studio.lab({'mode':'goal','min_sla':80})['points']),1)
        self.assertEqual(len(self.studio.lab({'mode':'stress'})['points']),16)
        self.assertGreaterEqual(len(self.studio.lab({'mode':'capacity','min_sla':80,'target_throughput':5.5})['points']),1)

    def test_assistant_local_without_api(self):
        ans=self.studio.assistant('Quais pedidos estão em risco?')
        self.assertIn('OP-',ans['text'])

    def test_record_verifiable_and_persisted(self):
        signature=self.studio.info()['selected']
        saved=self.studio.decision({'signature':signature,'note':'Verificar custo e prazo antes de decidir.'})
        self.assertEqual(len(self.studio.history()),1)
        data=self.studio.read_history(saved['filename'])
        self.assertEqual(data['record']['note'],'Verificar custo e prazo antes de decidir.')
        self.assertTrue(data.get('sha256'))

    def test_reject_invalid_action(self):
        with self.assertRaises(StudioError):self.studio.select('inexistente')

    def test_reset_keeps_original_examples(self):
        d=self.studio.reset();self.assertEqual(d['stations']['CNC']['maquinas'],2)
        self.assertEqual(d['metrics']['incident']['late_orders'],3)

if __name__=='__main__':unittest.main()
