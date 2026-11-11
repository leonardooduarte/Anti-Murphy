"""Editorial and integration smoke tests for the production view."""
from pathlib import Path
import ast
import json
from simulation_contract import ComparisonBundle

ROOT = Path(__file__).resolve().parents[1]


def test_editorial_copy_without_promo_headlines():
    html=(ROOT/'ui'/'factory_studio.html').read_text(encoding='utf8')
    for banned in (
        'Uma falha. Dois futuros.',
        'O futuro da sua produção',
        'Transforme problemas em oportunidades',
        'INTELIGÊNCIA DE DECISÃO',
    ):
        assert banned not in html
    for required in ('Análise de impacto', 'Carteira de pedidos', 'Linha do tempo'):
        assert required.lower() in html.lower()


def test_only_one_root_launcher():
    assert [x.name for x in ROOT.glob('*.bat')]==['INICIAR_ANTI_MURPHY.bat']
    assert 'tools\\start_nexus.py' in (ROOT/'INICIAR_ANTI_MURPHY.bat').read_text()


def test_offline_demo_uses_exact_contract_and_has_separated_futures():
    bundle=ComparisonBundle.model_validate_json((ROOT/'factory_command_demo.json').read_text(encoding='utf8'))
    assert bundle.schema_version=='1.1.0'
    assert bundle.branch_a.summary.late_orders > bundle.branch_b.summary.late_orders
    assert bundle.branch_a.summary.makespan_us > bundle.branch_b.summary.makespan_us


def test_preview_has_no_external_script_dependency():
    html=(ROOT/'PREVIEW_OPERACAO.html').read_text(encoding='utf8')
    assert 'id="payload"' in html
    assert '__BUNDLE_JSON__' not in html
    assert 'http://cdn' not in html and 'https://cdn' not in html
    assert 'Análise de impacto' in html


def test_application_files_parse():
    ast.parse((ROOT/'app.py').read_text(encoding='utf8'))
    ast.parse((ROOT/'ui/studio_runner.py').read_text(encoding='utf8'))
