"""Delayed API fixtures verify early feedback; no paid model requests."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in (1440, 390):
            page = await browser.new_page(viewport={'width':width,'height':950})
            started = {}
            source = {'id':'p1','title':'Building rules fixture','label':'Page 122','format':'pdf','text':'The owner must follow approved plans.','reader_url':'/documents/fixture?page=122','url':'https://example.org/rules.pdf','retrieved_at':'2026-10-29','warning':''}
            answer = {'status':'answered','summary_first':True,'paragraphs':[{'text':'The owner must follow approved plans.','citations':['p1']},{'text':'The affidavit records the owner’s responsibilities.','citations':['p1']}],'citations':[source]}
            async def api(route):
                path = route.request.url.split('/api/')[-1]
                if path=='status':
                    await route.fulfill(json={'search_ready':True,'chat_ready':True,'provider':'anthropic','domains':['legal','ecology'],'stats':{}})
                elif path.startswith('search?'):
                    started['search']=asyncio.get_running_loop().time()
                    await asyncio.sleep(.6)
                    await route.fulfill(json={'results':[source],'domain':'legal'})
                elif path=='chat':
                    started['chat']=asyncio.get_running_loop().time()
                    await asyncio.sleep(2)
                    await route.fulfill(json=answer)
                elif path=='curation': await route.fulfill(json={'starredIds':[]})
                else: await route.fulfill(status=404,json={'detail':'No fixture'})
            await page.route('**/api/**',api)
            await page.route('**/data/crm.json',lambda route:route.fulfill(json={'version':'fixture','records':[],'opportunities':[]}))
            await page.goto('http://127.0.0.1:4198/ask/legal', wait_until='networkidle')
            await page.locator('#research-question').fill('What must the owner do?')
            await expect(page.get_by_role('button',name='Ask',exact=True)).to_be_enabled()
            await page.locator('#research-question').press('Enter')
            turn=page.locator('.research-turn')
            await expect(turn.get_by_role('heading',name='What must the owner do?')).to_be_visible()
            await expect(turn.get_by_role('status')).to_be_visible()
            await expect(turn.locator('details.research-sources')).to_be_visible()
            assert not await turn.locator('.research-answer').count()
            assert abs(started['chat']-started['search']) < .5
            await expect(turn.get_by_label('Key takeaway')).to_contain_text('The owner must follow approved plans.')
            await expect(turn.get_by_role('heading',name='More detail')).to_be_visible()
            await expect(turn.get_by_label('Key takeaway').get_by_role('link')).to_have_attribute('href','/documents/fixture?page=122')
            assert not await page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            Path('.reports/clarity').mkdir(parents=True,exist_ok=True)
            await page.evaluate("document.activeElement?.blur(); window.scrollTo({top:0,behavior:'instant'})")
            await page.screenshot(path=f'.reports/clarity/answer-{width}.png',full_page=True)
            await page.close()
        await browser.close()
    print('Desktop and phone: immediate question, concurrent requests, early sources, cited takeaway and detail passed.')

asyncio.run(main())
