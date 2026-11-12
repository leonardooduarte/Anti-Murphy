from pathlib import Path
import json,subprocess
import pytest

@pytest.mark.parametrize('count',[1,3,4,5,6,9,16,50])
def test_all_workcell_halos_fit_without_intersection(count):
 src=Path(__file__).resolve().parents[1]/'atelier/web/app.js'
 js="const fs=require('fs'),vm=require('vm');const s=fs.readFileSync(process.argv[1],'utf8'),c={st:{focus:false}};vm.createContext(c);vm.runInContext(s.slice(s.indexOf('const positions ='),s.indexOf('function equipment('))+';globalThis.points=positions('+process.argv[2]+');globalThis.height=factoryLayoutHeight('+process.argv[2]+');',c);process.stdout.write(JSON.stringify({points:c.points,height:c.height}));"
 r=json.loads(subprocess.check_output(['node','-e',js,str(src),str(count)],text=True))
 points=r['points'];assert len(points)==count
 for i,a in enumerate(points):
  assert 0<=a['x']-155 and a['x']+155<=1200
  assert 0<=a['y']-116 and a['y']+108<=r['height']-30
  for b in points[i+1:]:assert abs(a['x']-b['x'])>=310 or abs(a['y']-b['y'])>=224
