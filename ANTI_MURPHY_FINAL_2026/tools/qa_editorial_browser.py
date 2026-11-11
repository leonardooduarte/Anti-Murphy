
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for width,height in [(1366,768),(1920,1080)]:
   page=await browser.new_page(viewport={'width':width,'height':height})
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   await page.set_content(Path('/mnt/data/ANTI_MURPHY_V31_OPERACAO/PREVIEW_OPERACAO.html').read_text(), wait_until='domcontentloaded')
   await page.wait_for_timeout(400)
   assert await page.locator('h1').inner_text() == 'Análise de impacto'
   statuses=await page.evaluate('''() => {
     const qa=window.__ANTI_MURPHY_QA__; const h=3600000000;
     const a=qa.stateAt('A',9.1*h),b=qa.stateAt('B',9.1*h);
     return [a.stations.CNC.status,b.stations.CNC.status];
   }''')
   print('statuses at 9.1h',statuses)
   assert statuses[0] == 'down'
   assert statuses[1] != 'down'
   await page.locator('#rewind').click()
   assert (await page.locator('#clock').inner_text()).startswith('0.00')
   await page.locator('#markIncident').click()
   assert (await page.locator('#clock').inner_text()).startswith('3.00')
   await page.locator('[data-mode="A"]').click()
   assert 'active' in str(await page.locator('[data-mode="A"]').get_attribute('class'))
   await page.locator('[data-mode="S"]').click()
   await page.locator('#dragHandle').press('ArrowRight')
   assert await page.locator('#dragHandle').get_attribute('aria-valuenow') == '52'
   scrollwidth=await page.evaluate('document.documentElement.scrollWidth')
   assert scrollwidth <= width
   assert not errors, errors
   print('PASS',width,height,'errors',len(errors),'overflow',scrollwidth)
   await page.close()
  await browser.close()
asyncio.run(main())
