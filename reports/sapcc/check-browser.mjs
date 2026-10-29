const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const base=process.env.SAPCC_BASE_URL || 'http://127.0.0.1:4196';
const out=process.env.SAPCC_CAPTURE_DIR || '.impeccable/review/sapcc-release';
const resultPath=process.env.SAPCC_RESULT_PATH || '.reports/sapcc-release/browser-checks.json';
await fs.mkdir(out,{recursive:true});
await fs.mkdir(new URL('.',new URL(resultPath,`file://${process.cwd()}/`)),{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
const context=await browser.newContext({viewport:{width:1440,height:1000},permissions:['clipboard-read','clipboard-write'],reducedMotion:'reduce'});
const page=await context.newPage();const errors=[];const checks=[];
page.on('pageerror',error=>errors.push(error.message));
async function visit(path){await page.goto(base+path);await page.locator('main h1').waitFor();await page.evaluate(()=>document.fonts.ready);}
async function count(selector, n){await page.waitForFunction(({selector,n})=>document.querySelectorAll(selector).length===n,{selector,n});assert.equal(await page.locator(selector).count(),n);}
async function capture(name){await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:`${out}/${name}.png`,fullPage:true});if(['desktop','mobile'].includes(name)) await page.screenshot({path:`${out}/${name}-viewport.png`});}
async function geometry(label){const data=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,italics:[...document.querySelectorAll('main *')].filter(el=>{const s=getComputedStyle(el);return s.display!=='none'&&s.fontStyle!=='normal';}).map(el=>el.tagName),sideflags:[...document.querySelectorAll('main *')].filter(el=>{const s=getComputedStyle(el);return parseFloat(s.borderLeftWidth)>1||parseFloat(s.borderRightWidth)>1;}).map(el=>el.tagName)}));assert(data.scroll<=data.width+1,`${label} overflow ${JSON.stringify(data)}`);assert.equal(data.italics.length,0);assert.equal(data.sideflags.length,0);checks.push({label,...data});}
await visit('/climate-plan');await count('.plan-topic-row',13);await capture('desktop');await geometry('desktop overview');
const input=page.getByRole('searchbox',{name:'Search topics and selected actions'});
await input.fill('solar');assert(await page.getByRole('link',{name:/Energy & solar power/}).isVisible());assert.match(page.url(),/q=solar/);
await page.getByRole('link',{name:/Energy & solar power/}).click();await page.getByRole('heading',{name:'Energy & solar power',level:1}).waitFor();
await page.getByRole('button',{name:'Copy question & reference'}).click();assert.match(await page.evaluate(()=>navigator.clipboard.readText()),/Goa SAPCC/);
await page.goBack();await page.getByRole('searchbox').waitFor();assert.equal(await page.getByRole('searchbox').inputValue(),'solar');
await page.getByRole('button',{name:'Clear search',exact:true}).click();await count('.plan-topic-row',13);
await page.getByRole('searchbox').fill('unfindable-climate-zzzz');await page.getByRole('heading',{name:/No topics match/}).waitFor();await capture('desktop-empty');
await page.getByRole('button',{name:'Clear search',exact:true}).last().click();await count('.plan-topic-row',13);
await page.getByRole('link',{name:'Chapter index',exact:true}).click();await count('.plan-chapter',19);
await page.getByRole('searchbox').fill('health');await count('.plan-chapter',1);await page.getByText('Browse sector sections',{exact:true}).click();
assert.equal(await page.getByRole('link',{name:/7.6 Human health, printed/}).getAttribute('href'),'https://www.nitiforstates.gov.in/public-assets/Policy/policy_files/GSSNAD000283.pdf#page=71');
await page.getByRole('button',{name:'Clear search',exact:true}).click();await capture('desktop-chapters');await geometry('desktop chapters');
await visit('/climate-plan/water');await capture('desktop-water');await geometry('desktop detail');
await page.getByRole('link',{name:'Prepare a records request',exact:true}).click();await page.getByRole('heading',{level:1}).waitFor();assert.match(page.url(),/templates\/03-rti-records-request/);assert(!/not found|isn.t here/i.test(await page.locator('main h1').innerText()));
await visit('/climate-plan?view=source');await capture('desktop-source');await geometry('source details');
const guideResponse=await context.request.get(base+'/guides/goa-climate-plan.md');assert.equal(guideResponse.status(),200);assert.match(await guideResponse.text(),/26 measures/);
await visit('/library');await page.getByRole('link',{name:'Explore Goa’s climate action plan',exact:true}).click();assert.match(page.url(),/climate-plan$/);
await visit('/search?q=SAPCC');assert(await page.locator('[data-record-id="goa-sapcc"]').count()>0);
await page.locator('[data-record-id="goa-sapcc"] h3 a').click();await page.getByRole('heading',{name:'Goa’s climate action plan',exact:true}).waitFor();
await visit('/climate-plan/missing');assert(await page.getByRole('heading',{name:'That climate topic isn’t here.'}).isVisible());
for(const width of [390,320,768]){
 await page.setViewportSize({width,height:844});await visit('/climate-plan');await geometry(`${width} overview`);await capture(width===390?'mobile':`overview-${width}`);
 await visit('/climate-plan/water');await geometry(`${width} detail`);if(width===390){await capture('mobile-water');await page.getByText('Choose another topic',{exact:true}).click();await page.locator('.plan-mobile-topics').getByRole('link',{name:'Heat & health',exact:true}).click();await page.getByRole('heading',{name:'Heat & health',exact:true}).waitFor();await geometry('mobile health');}
}
await page.setViewportSize({width:390,height:844});await visit('/climate-plan?view=chapters');await capture('mobile-chapters');await geometry('mobile chapters');
await visit('/climate-plan?view=source');await capture('mobile-source');await geometry('mobile source');
await visit('/climate-plan');await page.getByRole('searchbox').focus();await page.keyboard.type('solar');assert.equal(await page.getByRole('searchbox').inputValue(),'solar');await page.waitForURL('**q=solar');await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('aria-label')),'Clear search');await page.keyboard.press('Enter');await page.waitForFunction(()=>document.querySelector('input[type=search]').value==='');assert.equal(await page.getByRole('searchbox').inputValue(),'');
await page.route('**/data/catalog.json',route=>route.abort());await visit('/climate-plan/funding');assert(await page.getByRole('heading',{name:'Funding & progress',level:1}).isVisible());
assert.equal(errors.length,0,errors.join('\n'));
await fs.writeFile(resultPath,JSON.stringify({checks,errors,journeys:['topic search and clear','shared query URL','back restores search','clipboard copies question and source','chapter search and expansion','exact source page anchor','records template opens','library entry','catalogue SAPCC search','unavailable topic','mobile topic navigation','keyboard search clear','PDF-independent route with failed catalogue'],passed:true},null,2)+'\n');
await browser.close();console.log('Browser checks passed.');
