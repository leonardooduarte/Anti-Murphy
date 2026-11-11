"""Contract tests for restored specialist analyses in the main workspace."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from atelier.service import Studio, StudioError


class SpecialistWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.studio=Studio(Path(self.temp.name))
    def tearDown(self):
        self.temp.cleanup()

    def test_six_specialist_modes_stay_in_same_experiment(self):
        initial=self.studio.info()
        scenarios={
            'diagnostic':{'mode':'diagnostic'},
            'opportunities':{'mode':'opportunities'},
            'sensitivity':{'mode':'sensitivity','station':'CNC','resource':'operadores'},
            'demand':{'mode':'demand','min_sla':80},
            'uncertainty':{'mode':'uncertainty'},
            'recovery':{'mode':'recovery'},
        }
        for mode,params in scenarios.items():
            with self.subTest(mode=mode):
                r=self.studio.advanced(params)
                self.assertEqual(r['mode'],mode)
                self.assertEqual(r['experiment_id'],initial['run_id'])
                self.assertIn('notes',r)
                if mode=='diagnostic':
                    self.assertEqual(len(r['stations']),5)
                    self.assertEqual(r['quality']['calibration'],'NÃO COMPROVADA')
                else:
                    self.assertGreater(len(r['rows']),0)
                current=self.studio.info()
                self.assertEqual(current['run_id'],initial['run_id'])
                self.assertEqual(current['selected'],initial['selected'])

    def test_unknown_tool_and_invalid_station_are_rejected(self):
        for payload in ({'mode':'made-up'},{'mode':'sensitivity','station':'NONE'},
                        {'mode':'sensitivity','station':'CNC','resource':'money'},
                        {'mode':'demand','min_sla':120}):
            with self.subTest(payload=payload), self.assertRaises(StudioError):
                self.studio.advanced(payload)

    def test_evidence_requires_a_written_reason(self):
        selected=self.studio.info()['selected']
        with self.assertRaises(StudioError):
            self.studio.decision({'signature':selected,'note':' '})
        self.assertEqual(self.studio.history(),[])
        outcome=self.studio.decision({'signature':selected,
            'note':'Verificar disponibilidade e custo total antes da intervenção.'})
        self.assertEqual(len(self.studio.history()),1)
        self.assertEqual(self.studio.read_history(outcome['filename'])['record']['note'],
            'Verificar disponibilidade e custo total antes da intervenção.')

    def test_no_unverified_zero_cost_assumptions_in_recovery_notes(self):
        r=self.studio.advanced({'mode':'recovery'})
        self.assertTrue(any('investimento' in note.lower() for note in r['notes']))

if __name__=='__main__':unittest.main()
