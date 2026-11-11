"""The actual JS formatters must not turn a short positive horizon into zero."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

WEB = Path(__file__).resolve().parents[1] / 'atelier' / 'web'

@pytest.mark.parametrize('chart', [False, True])
def test_nonzero_small_value_visible_without_changing_ordinary_format(chart):
    node = shutil.which('node')
    if not node:
        pytest.skip('Node is required for the optional JavaScript formatter test.')
    if chart:
        source = (WEB / 'engineering_charts.js').read_text()
        snippet = source[source.index('const valid='):source.index('const fc=')]
        call = 'fnum'
    else:
        source = (WEB / 'app.js').read_text()
        snippet = source[source.index('const numericText ='):source.index('const h =')]
        call = 'numericText'
    js = snippet + f'console.log(JSON.stringify([0.001,16.9,1e-10].map(x=>{call}(x,2))))'
    values = json.loads(subprocess.check_output([node, '-e', js], text=True))
    assert values == ['0,001', '16,90', '1,000e-10']
