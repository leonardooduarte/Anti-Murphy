/* Optional local browser QA. Install: npm install --no-save playwright */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const out=process.env.AM_QA_DIR||path.join(require('os').tmpdir(),'anti-murphy-qa');fs.mkdirSync(out,{recursive:true});
let qaPage;
// Check rendered colors, including labels inside the cards, rather than CSS text.
async function assertLegacyContrast(page,surfaces,labels){
 const findings=await page.evaluate(({surfaces,labels})=>{
  const rgb=s=>(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);
  const light=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
  const opaque=el=>{for(let n=el;n;n=n.parentElement){const c=getComputedStyle(n).backgroundColor;if(c!=='transparent'&&!c.endsWith(', 0)'))return rgb(c);}return [0,0,0];};
  const cards=[...document.querySelectorAll(surfaces)],text=[...document.querySelectorAll(labels)];
  return {cards:cards.length,labels:text.length,lightCards:cards.filter(el=>light(opaque(el))>.2).length,
   unreadable:text.filter(el=>{const bg=light(opaque(el)),fg=light(rgb(getComputedStyle(el).color));return (Math.max(bg,fg)+.05)/(Math.min(bg,fg)+.05)<4.5||parseFloat(getComputedStyle(el).fontSize)<11;}).map(el=>el.textContent.slice(0,75))};
 },{surfaces,labels});
 assert(findings.cards>0&&findings.labels>0,'Missing legacy cards: '+JSON.stringify(findings));
 assert.equal(findings.lightCards,0,'Unexpected light legacy surfaces');
 assert.deepEqual(findings.unreadable,[],'Legacy labels need readable contrast and size');
 return findings;
}
(async()=>{
 const b=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||undefined,headless:true,
  args:['--no-sandbox','--disable-dev-shm-usage','--no-zygote','--single-process','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:1440,height:1050}}),errors=[];
 qaPage=p;
 p.on('pageerror',e=>errors.push(e.message)); p.on('console',m=>{if(m.type()==='error')console.log('CONSOLE',m.text());});p.on('crash',()=>console.log('PAGE_CRASH'));b.on('disconnected',()=>console.log('BROWSER_DISCONNECTED'));
 await p.goto(process.env.AM_QA_URL||'http://127.0.0.1:8501');
 console.log('GOTO_OK',await p.title()); await p.screenshot({path:path.join(out,'00_loading.png')});
 await p.getByRole('button',{name:'▶ Preparar demonstração CNC',exact:true}).waitFor({timeout:20000});
 await p.screenshot({path:path.join(out,'01_initial.png'),fullPage:true});
 console.log('INITIAL',await p.title());
 await p.getByRole('button',{name:'▶ Preparar demonstração CNC',exact:true}).click();
 await p.getByText('RESPOSTA PROMISSORA',{exact:true}).waitFor();
 const f=p.frameLocator('iframe[title="Murphy Motion: replay interativo dos eventos da simulação"]');
 await f.getByRole('button',{name:'Reproduzir',exact:true}).waitFor();
 await f.getByRole('slider',{name:'Tempo do replay',exact:true}).evaluate(el=>{el.value='230';el.dispatchEvent(new Event('input',{bubbles:true}));});
 await f.getByText('EVENTO MURPHY',{exact:true}).waitFor();
 await p.screenshot({path:path.join(out,'02_incident.png'),fullPage:true});
 const queues=await f.locator('#queue').innerText();assert(Number(queues)>0);
 await f.getByRole('button',{name:'⇄ Antes / depois',exact:true}).click();
 assert((await f.locator('#scene').textContent()).includes('DEPOIS / RESPOSTA SIMULADA'));
 await f.getByRole('button',{name:'Reproduzir',exact:true}).click();
 await f.getByRole('button',{name:'Reproduzir',exact:true}).click();
 await p.getByTestId('stPlotlyChart').first().scrollIntoViewIfNeeded();
 await p.screenshot({path:path.join(out,'09_economics.png'),fullPage:true});
 await p.getByRole('button',{name:'✦ Murphy AI',exact:true}).click();
 await p.getByText('Modo de IA e conexão opcional',{exact:true}).click();
 assert.equal(await p.getByTestId('stTextInput').count(),0,'Local mode must not ask for API credentials');
 await p.getByRole('combobox',{name:'Modo de análise',exact:true}).fill('Generativo');
 await p.getByRole('combobox',{name:'Modo de análise',exact:true}).press('ArrowDown');
 await p.getByRole('combobox',{name:'Modo de análise',exact:true}).press('Enter');
 await p.getByLabel('Chave da API (somente nesta sessão)',{exact:true}).waitFor();
 await p.getByRole('combobox',{name:'Modo de análise',exact:true}).fill('Local');
 await p.getByRole('combobox',{name:'Modo de análise',exact:true}).press('ArrowDown');
 await p.getByRole('combobox',{name:'Modo de análise',exact:true}).press('Enter');
 await p.getByLabel('Chave da API (somente nesta sessão)',{exact:true}).waitFor({state:'detached'});
 await p.getByText('Modo de IA e conexão opcional',{exact:true}).click();
 await p.getByRole('button',{name:'Tenho apenas R$ 3.000 para resolver o problema.',exact:true}).click();
 await p.getByRole('button',{name:'✓ Autorizar e executar experimento',exact:true}).waitFor();
 await p.screenshot({path:path.join(out,'03_ai_authorization.png'),fullPage:true});
 await p.getByRole('button',{name:'✓ Autorizar e executar experimento',exact:true}).click();
 await p.getByRole('button',{name:'✓ Autorizar e executar experimento',exact:true}).waitFor({state:'detached'});
 await p.getByRole('button',{name:'Compare realocar operadores com manutenção expressa.',exact:true}).click();
 await p.getByTestId('stDataFrame').waitFor();
 assert.equal(await p.locator('[data-testid="stChatMessage"] .katex').count(),0,'Currency was interpreted as math');
 await p.screenshot({path:path.join(out,'04_ai_evidence.png'),fullPage:true});
 await p.getByRole('button',{name:'◇ Revisar decisão',exact:true}).click();
 await p.getByRole('button',{name:'Preparar teste com 8 sementes',exact:true}).click();
 await p.getByText('Teste pareado de sensibilidade',{exact:true}).waitFor();
 await p.getByRole('button',{name:'✓ Autorizar e executar experimento',exact:true}).click();
 await p.getByText('ECONOMIA LÍQUIDA MÉDIA',{exact:true}).waitFor();
 await p.screenshot({path:path.join(out,'05_review.png'),fullPage:true});
 await p.getByRole('button',{name:'▶ Pitch · 2 minutos',exact:true}).click();
 await p.getByRole('button',{name:'Preparar / reiniciar carteira sintética',exact:true}).click();
 await p.getByText('O palco está usando seu experimento atual.',{exact:false}).waitFor({state:'detached'});
 const pitch=p.frameLocator('iframe[title="Murphy Motion: replay interativo dos eventos da simulação"]');
 await pitch.getByRole('button',{name:'06 / RECUPERAÇÃO',exact:true}).click();
 assert((await pitch.locator('#story-title').innerText()).includes('Recuperação estimada'));
 await p.screenshot({path:path.join(out,'06_pitch.png'),fullPage:true});
 await pitch.getByRole('button',{name:'Reiniciar',exact:true}).click();
 assert((await pitch.locator('#clock').innerText()).includes('00:00'));
 await p.getByText('Ferramentas V29 preservadas',{exact:true}).click();
 await p.getByRole('button',{name:'Abrir ferramentas anteriores',exact:true}).click();
 await p.getByRole('button',{name:'← Voltar para NEXUS V30',exact:true}).waitFor();
 const legacyChecks=[];
 for(const [name,title,slug,surfaces,labels] of [
  ['◎  Visão operacional','Centro de decisão','operations','.v18-pulse>div,.am16-signal,.v18-econ>div,.v23-stat,.v25-root>div','.v18-pulse .ey,.v18-pulse .big,.v18-pulse .sub,.am16-signal b,.am16-signal p,.v23-stat .k,.v23-stat .s'],
  ['▣  Sala executiva','Executive Room','executive','.v23-stat,.v23-exec-grid>div,.v23-callout,[data-testid="stMetric"]','.v23-stat .k,.v23-stat .v,.v23-stat .s,.v23-exec-grid .k,.v23-exec-grid .s'],
  ['✦  Murphy AI','Murphy AI','ai','.v23-ai-plan>div,.am-ai-stat,.am-ai-context>div','.v23-ai-plan .n,.v23-ai-plan .t,.v23-ai-plan .s']
 ]){
  await p.getByRole('button',{name,exact:true}).click();
  await p.locator('h1').filter({hasText:title}).waitFor();
  legacyChecks.push({page:slug,...await assertLegacyContrast(p,surfaces,labels)});
  await p.screenshot({path:path.join(out,'legacy_'+slug+'.png'),fullPage:true});
 }
 await p.getByRole('button',{name:'← Voltar para NEXUS V30',exact:true}).click();
 await p.getByRole('button',{name:'◉ War Room',exact:true}).click();
 await p.getByRole('button',{name:'▶ Preparar demonstração CNC',exact:true}).click();
 await p.getByText('RESPOSTA PROMISSORA',{exact:true}).waitFor();
 await p.setViewportSize({width:1050,height:900});
 await p.getByRole('button',{name:'◉ War Room',exact:true}).click();
 await p.screenshot({path:path.join(out,'07_laptop.png'),fullPage:true});
 await p.setViewportSize({width:600,height:900});
 await p.screenshot({path:path.join(out,'08_narrow.png'),fullPage:true});
 assert.equal(errors.length,0,'Browser JS errors: '+errors.join('; '));
 console.log('BROWSER_QA_PASS',JSON.stringify({errors,queue_at_incident:queues,screens:12,viewport:[1440,1050,600],legacyChecks}));
 await b.close();
})().catch(async e=>{if(qaPage)await qaPage.screenshot({path:path.join(out,'failure.png'),fullPage:true}).catch(()=>{});console.error(e);process.exit(1);});
