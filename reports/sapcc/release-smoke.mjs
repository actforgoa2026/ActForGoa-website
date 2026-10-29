// Read-only release acceptance. Template exports stay inside the isolated browser.
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const { chromium } = await import(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.SAPCC_BASE_URL || 'http://127.0.0.1:4196';
const out = process.env.SAPCC_SMOKE_DIR || '.reports/sapcc-release/retained';
await fs.mkdir(out, {recursive: true});
const browser = await chromium.launch({channel: 'chrome', headless: true});
let context = await browser.newContext({reducedMotion: 'reduce', acceptDownloads: true});
let page = await context.newPage();
const errors = [], checks = [];
page.on('pageerror', error => errors.push(error.message));
page.on('dialog', dialog => dialog.accept());
await page.route('**/api/chat', route => { throw new Error('No AI requests are allowed in this smoke check.'); });
const read = async path => {const r = await context.request.get(base + path); assert.equal(r.status(), 200, path); return r.json();};
const status = await read('/api/status');
assert(status.search_ready && status.chat_ready);
const search = await read('/api/search?' + new URLSearchParams({q: 'Goa mangroves', domain: 'ecology'}));
assert(search.results?.length);
const documentPath = search.results[0].reader_url;
assert(documentPath.startsWith('/documents/'));
const admin = await read('/api/admin/config');
assert.equal(admin.available, true);
assert(Array.isArray((await read('/api/blog')).posts));
const routes = ['/', '/explore', '/topics/waste', '/directory', '/directory/archive', '/emergency', '/report', '/read/guide-farming', '/templates/18-service-enquiry', '/ask', '/ask/legal', '/ask/ecology', '/admin', '/blog', '/blog/archive', documentPath, '/library', '/newsletters', '/climate-plan', '/climate-plan/water'];
async function visit(route) {
  await page.goto(base + route);
  await page.locator('main h1').first().waitFor();
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => !/^(Loading|Opening this page)/.test(document.querySelector('main')?.innerText || ''));
  if (route.startsWith('/ask')) await page.waitForFunction(() => {
    const starter = document.querySelector('.research-starters button');
    return starter && !starter.disabled;
  });
}
for (const [name, width, height] of [['desktop', 1440, 1000], ['mobile', 390, 844]]) {
  // Give each device a fresh draft store and download permission state.
  if (name === 'mobile') {
    await context.close();
    context = await browser.newContext({reducedMotion: 'reduce', acceptDownloads: true});
    page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    page.on('dialog', dialog => dialog.accept());
    await page.route('**/api/chat', route => { throw new Error('No AI requests are allowed in this smoke check.'); });
  }
  await page.setViewportSize({width, height});
  await fs.mkdir(`${out}/${name}`, {recursive: true});
  for (const route of routes) {
    await visit(route);
    const heading = await page.locator('main h1').first().innerText();
    assert(!/could not open|not found|isn.t here|could not load/i.test(heading), `${route}: ${heading}`);
    if (route.startsWith('/documents/')) {await page.locator('.document-text').waitFor(); assert((await page.locator('.document-text').innerText()).length > 30);}
    if (route === '/directory') {await page.locator('.crm-card, .crm-row, [data-record-id]').first().waitFor();}
    const geometry = await page.evaluate(() => ({width: innerWidth, scroll: document.documentElement.scrollWidth, italicCount: [...document.querySelectorAll('main *')].filter(el => getComputedStyle(el).fontStyle !== 'normal').length}));
    assert(geometry.scroll <= geometry.width + 1, `${route}: horizontal overflow`);
    assert.equal(geometry.italicCount, 0, route);
    const capture = ['/', '/explore', '/directory', '/report', '/read/guide-farming', '/templates/18-service-enquiry', '/ask/ecology', '/blog', '/admin'].includes(route) || route.startsWith('/documents/');
    if (capture) await page.screenshot({path: `${out}/${name}/${route.startsWith('/documents/') ? 'document' : route.replaceAll('/', '-') || 'home'}.png`});
    checks.push({viewport: name, route, heading, ...geometry});
  }
  await visit('/templates/18-service-enquiry');
  for (const input of await page.locator('.template-fields input, .template-fields textarea').all()) {
    await input.fill(await input.getAttribute('type') === 'date' ? '2026-10-30' : 'Release smoke test');
  }
  if (name === 'mobile') await page.getByRole('group', {name: 'Template view'}).getByRole('button', {name: 'Review & save', exact: true}).click();
  const downloading = page.waitForEvent('download', {timeout: 30000}).catch(async error => {
    await page.screenshot({path: `${out}/${name}/export-failure.png`});
    await fs.writeFile(`${out}/${name}/export-failure.txt`, await page.locator('main').innerText());
    throw error;
  });
  await page.getByRole('button', {name: 'Save PDF', exact: true}).click();
  const download = await downloading;
  const saved = `${out}/${name}/template.pdf`;
  await download.saveAs(saved);
  assert.equal((await fs.readFile(saved)).subarray(0, 5).toString(), '%PDF-');
}
assert.equal(errors.length, 0, errors.join('\n'));
await fs.writeFile(`${out}/checks.json`, JSON.stringify({base, routes, checks, errors, templatePdf: true, researchReady: status.search_ready && status.chat_ready, adminReady: admin.available, paidRequests: 0, passed: true}, null, 2) + '\n');
await browser.close();
console.log('Retained-route desktop/phone checks passed.');
