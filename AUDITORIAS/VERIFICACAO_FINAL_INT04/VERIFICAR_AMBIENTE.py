"""Diagnóstico portátil em cópia temporária; não homologa BAT/GUI/projetor."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,queue,re,shutil,subprocess,sys,tempfile,threading,time,uuid
from urllib.request import Request,urlopen


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app',type=Path,required=True,help='Pasta ANTI_MURPHY_FINAL_2026 recém-extraída')
    parser.add_argument('--saida',type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parent
    output=args.saida or root/('resultado_ambiente_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]+'.json')
    if output.exists():parser.error('A saída já existe. Escolha outro nome; nada foi sobrescrito.')
    result={'executado_em':datetime.datetime.now().astimezone().isoformat(),'sistema':platform.system(),
            'python':sys.version,'verificacoes':{},'windows_automatizado_aprovado':None,
            'bat_executado':False,'interface_visual_homologada':False,'projetor_homologado':False}
    def check(name,condition):
        result['verificacoes'][name]=bool(condition)
        if not condition:raise RuntimeError('Verificação falhou: '+name)
    try:
        check('python_310_ou_superior',sys.version_info>=(3,10))
        manifest=json.loads((root/'base-manifest.json').read_text('utf-8'))
        app=args.app.resolve();bad=[name for name,digest in manifest['files'].items()
            if not (app/name).is_file() or hashlib.sha256((app/name).read_bytes()).hexdigest()!=digest]
        result['arquivos_diferentes']=bad
        check('748_arquivos_da_INT04_conferem',not bad and len(manifest['files'])==748)
        with tempfile.TemporaryDirectory(prefix='anti_murphy_diagnostico_') as tmp:
            copy=Path(tmp)/'app'
            shutil.copytree(app,copy,ignore=shutil.ignore_patterns('workspace','__pycache__','.pytest_cache','.git'))
            env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
            process=None;reader=None
            def start():
                nonlocal process,reader
                process=subprocess.Popen([sys.executable,'-S','start.py','--no-browser','--port','0'],cwd=copy,
                    env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace')
                messages=queue.Queue();lines=[]
                def collect():
                    for line in process.stdout:messages.put(line)
                reader=threading.Thread(target=collect,daemon=True);reader.start();deadline=time.monotonic()+30
                while time.monotonic()<deadline:
                    try:line=messages.get(timeout=.2);lines.append(line)
                    except queue.Empty:
                        if process.poll() is not None:break
                        continue
                    found=re.search(r'http://127\.0\.0\.1:\d+',line)
                    if found:return found.group()
                raise RuntimeError('Servidor não iniciou. '+''.join(lines[-8:]))
            def stop():
                nonlocal process
                if process is not None:
                    if process.poll() is None:
                        process.terminate()
                        try:process.wait(timeout=5)
                        except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
                    if reader:reader.join(timeout=1)
                    process.stdout.close();process=None
            def request(url,path,payload=None):
                headers={}
                if payload is not None:headers={'Content-Type':'application/json','Origin':url}
                req=Request(url+path,data=json.dumps(payload).encode('utf-8') if payload is not None else None,headers=headers)
                with urlopen(req,timeout=30) as response:
                    raw=response.read()
                    return json.loads(raw) if response.headers.get_content_type()=='application/json' else raw
            try:
                url=start();state=request(url,'/api/state')
                check('inicio_sem_dependencias_extras',state['rule']=='EDD')
                check('referencia_oficial_SLA',state['metrics']['incident']['sla_pct']==40)
                for asset in ['/','/app.js','/styles.css','/experience_v01.css']:
                    check('recurso_'+asset,bool(request(url,asset)))
                request(url,'/api/run',{'rule':'SPT'});model=request(url,'/api/model/export')
                request(url,'/api/run',{'rule':'EDD'});changed=request(url,'/api/model',model)
                check('INT01_regra_restaurada',changed['rule']=='SPT')
                request(url,'/api/experiment/save',{'name':'Diagnóstico válido'})
                invalid=copy/'workspace/experimentos/invalid.json';invalid.write_text('[]',encoding='utf-8')
                library=request(url,'/api/experiment-library')
                check('INT03_validos_e_aviso',len(library['items'])==1 and len(library['issues'])==1)
                request(url,'/api/experiment/save',{'name':'Diagnóstico com aviso'})
                stop();url=start();reopened=request(url,'/api/state')
                check('reabertura_sem_perda',reopened['rule']=='SPT' and reopened['experiment_count']==2 and invalid.read_text('utf-8')=='[]')
                short=json.loads((root/'MODELO_CICLO_CURTO.json').read_text('utf-8'))
                request(url,'/api/model',short)
                request(url,'/api/run',{'station':'P','start_h':10,'duration_h':1,'delay_h':0})
                timing=request(url,'/api/technical-audit')['orders']['normal'][0]
                check('INT02_horarios_precisos',timing['finish_h']>0 and timing['slack_h']==timing['due_h']-timing['finish_h'] and timing['is_late'] is True)
                stop()
                official=subprocess.run([sys.executable,'-S','-m','atelier.tests.validacao_experimentos_banca'],cwd=copy,env=env,
                    capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=60)
                result['experimentos_saida']=official.stdout+official.stderr
                check('tres_experimentos_oficiais',official.returncode==0 and '3 EXPERIMENTOS APROVADOS' in official.stdout)
            finally:stop()
        result['automaticos_aprovados']=True
    except Exception as exc:
        result['automaticos_aprovados']=False;result['erro']=str(exc)
    if platform.system()=='Windows':result['windows_automatizado_aprovado']=result['automaticos_aprovados']
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
    print('Resultado:',output)
    print('Verificações automáticas:', 'APROVADAS' if result['automaticos_aprovados'] else 'FALHARAM')
    print('BAT, interface visual e projetor continuam exigindo ensaio manual.')
    if platform.system()!='Windows':print('Este resultado NÃO é validação nativa no Windows.')
    return 0 if result['automaticos_aprovados'] else 1

if __name__=='__main__':raise SystemExit(main())
