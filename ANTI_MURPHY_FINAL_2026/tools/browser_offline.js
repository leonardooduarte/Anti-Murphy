const {chromium}=require('playwright');
const path=require('path'),fs=require('fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE,headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--no-zygote','--single-process','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1366,height:768}});page.setDefaultTimeout(15000);const errors=[];page.on('pageerror',e=>errors.push(e.message));let external=0;
 await page.route('**/*',r=>{const u=new URL(r.request().url());if(['file:','data:','blob:'].includes(u.protocol))return r.continue();external++;return r.abort();});
 await page.goto('file://'+path.resolve(__dirname,'../DEMO_NEXUS_V30.html'));await page.evaluate(()=>document.fonts.ready);
 await page.getByRole('button',{name:'Ensaiar esta resposta →',exact:true}).waitFor();
 assert(await page.locator('#open-record').isDisabled());
 await page.getByRole('button',{name:'Custo de esperar ↗',exact:true}).click();await page.locator('#timing-dialog').waitFor({state:'visible'});assert((await page.locator('#timing-content').innerText()).includes('4.582'));assert(await page.locator('[data-delay]').evaluateAll(nodes=>nodes.every(n=>n.disabled)));await page.getByRole('button',{name:'Fechar análise de tempo',exact:true}).click();
 await page.getByRole('button',{name:'Ver 18 ↗',exact:true}).click();const transfer=page.locator('#matrix-content tr').filter({hasText:'Realocar operador · MONTAGEM → CNC'});await transfer.getByRole('button',{name:'Ensaiar',exact:true}).click();assert((await page.locator('#response-content .response-option').first().innerText()).includes('MONTAGEM → CNC'));
 await page.getByRole('tab',{name:'Comparação',exact:true}).click();await page.locator('#seek').evaluate(el=>{el.value='6000';el.dispatchEvent(new Event('input',{bubbles:true}));});assert((await page.locator('#comparison-content').innerText()).includes('Mesmo instante'));
 await page.getByRole('button',{name:'Apresentar',exact:true}).click();await page.locator('[data-chapter="5"]').click();assert(await page.locator('#story-plant').isHidden());assert(await page.locator('#story-deliveries').isVisible());const box=await page.locator('.theater-controls').boundingBox();assert(box.y+box.height<=768);
 if(process.env.AM_QA_DIR){fs.mkdirSync(process.env.AM_QA_DIR,{recursive:true});await page.screenshot({path:path.join(process.env.AM_QA_DIR,'offline_presentation.png'),fullPage:true});}
 assert.deepEqual(errors,[]);assert.equal(external,0);console.log('OFFLINE_HTML_PASS',JSON.stringify({errors,external,fonts:await page.evaluate(()=>[...document.fonts].map(f=>({family:f.family,status:f.status})))}));await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1;});
