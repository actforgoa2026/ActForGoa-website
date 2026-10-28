"""Desktop/phone UI acceptance with real local auth and synthetic provider data.

Run with the system Python that provides Playwright; the service uses .venv.
This never calls either image provider. Screenshots carry a fixture label.
"""
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def fixture_service():
    import httpx
    import uvicorn
    from satellite.app import create_app
    from satellite.domain import Interpretation
    from satellite.service import SatelliteService
    from test_service import transport
    calls = []
    base = transport(calls)

    def handler(request):
        if str(request.url) == 'https://api.openai.com/v1/decisions':
            questions = json.loads(request.content)['questions']
            choices = {'before_canopy': 'yes', 'after_canopy': 'no', 'canopy_change': 'possible_loss'}
            return httpx.Response(200, json={'model': 'gpt-6-luna', 'answers': [
                {'name': q['name'], 'type': 'choice', 'choice': choices.get(q['name'], 'uncertain')} for q in questions]})
        return base.handle_request(request)

    service = SatelliteService(Path(os.environ['SATELLITE_DATA_DIR'])/'jobs.sqlite', httpx.Client(transport=httpx.MockTransport(handler)))
    service.planner.interpret = lambda query: Interpretation(intent='canopy_loss', scope='selected_area', place_name='',
        time_mode='absolute_dates', days=1, start_date='2025-10-18', end_date='2025-10-28', individual_tree=False)
    uvicorn.run(create_app(service), host='127.0.0.1', port=8094, access_log=False)


def main():
    from playwright.sync_api import sync_playwright
    work = Path(tempfile.mkdtemp(prefix='satellite-decisions-ui-', dir=ROOT/'.reports'))
    output = ROOT/'reports/satellite-decisions-2026-10-28'
    output.mkdir(parents=True, exist_ok=True)
    password = secrets.token_urlsafe(24)
    env = {**os.environ, 'NODE_ENV': 'development', 'NODE_USE_ENV_PROXY': '1',
        'ADMIN_DATA_DIR': str(work/'admin'), 'ADMIN_PORT': '4198', 'ADMIN_PUBLIC_ORIGIN': 'http://127.0.0.1:4178',
        'ADMIN_API_ORIGIN': 'http://127.0.0.1:4198', 'SATELLITE_API_ORIGIN': 'http://127.0.0.1:8094',
        'SATELLITE_DATA_DIR': str(work/'satellite'), 'SATELLITE_SERVICE_TOKEN': secrets.token_urlsafe(32),
        'SATELLITE_MCP_TOKEN': secrets.token_urlsafe(32), 'SATELLITE_CLASSIFIER': 'openai-decisions',
        'CDSE_CLIENT_ID': 'synthetic-only', 'CDSE_CLIENT_SECRET': 'synthetic-only',
        'OPENAI_API_KEY': 'synthetic-only', 'ANTHROPIC_API_KEY': 'synthetic-only'}
    subprocess.run(['node', '--import', 'tsx', 'server/admin-accounts.ts', 'add', 'satellite-ui@example.test', 'Satellite UI Test', 'editor'],
        cwd=ROOT, env=env, input=password+'\n', text=True, check=True, stdout=subprocess.DEVNULL)
    commands = [[str(ROOT/'.venv/bin/python'), str(Path(__file__).resolve()), '--service'],
                ['node', '--import', 'tsx', 'server/admin.ts'],
                ['node', 'node_modules/vite/bin/vite.js', '--host', '127.0.0.1', '--port', '4178']]
    processes, logs, results = [], [], []
    try:
        for i, command in enumerate(commands):
            log = (work/f'service-{i}.log').open('w'); logs.append(log)
            processes.append(subprocess.Popen(command, cwd=ROOT, env=env, stdout=log, stderr=log))
        for url in ['http://127.0.0.1:8094/healthz', 'http://127.0.0.1:4198/api/admin/session', 'http://127.0.0.1:4178/map']:
            for _ in range(100):
                try:
                    with urlopen(url, timeout=1): break
                except HTTPError as error:
                    if error.code == 401: break
                    raise
                except (URLError, TimeoutError): time.sleep(.1)
            else: raise RuntimeError('Local test service did not become ready')
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=shutil.which('chromium'), args=['--no-sandbox'])
            for name, width in [('desktop', 1440), ('phone', 390), ('small-phone', 320)]:
                context = browser.new_context(viewport={'width': width, 'height': 1000 if width > 500 else 844})
                page = context.new_page(); errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto('http://127.0.0.1:4178/map')
                page.get_by_text('Sign in to the team workspace', exact=True).wait_for()
                page.goto('http://127.0.0.1:4178/admin')
                page.get_by_label('Email address').fill('satellite-ui@example.test')
                page.get_by_label('Password', exact=True).fill(password)
                page.get_by_role('button', name='Sign in', exact=True).click()
                page.get_by_role('button', name='Sign out').wait_for()
                page.goto('http://127.0.0.1:4178/map')
                page.get_by_role('button', name='Use these coordinates').click()
                page.get_by_label('Ask about this area').fill('Was canopy lost here between 18 and 28 October 2025?')
                page.get_by_role('button', name='Prepare investigation').click()
                page.get_by_text('Requested period:', exact=False).wait_for()
                page.get_by_role('button', name='Find observations').click()
                page.get_by_label('Before observation').select_option('scene-0')
                page.get_by_label('After observation').select_option('scene-1')
                page.get_by_role('button', name='Compare selected observations').click()
                presence = page.locator('.satellite-presence')
                presence.wait_for(timeout=20000)
                assert presence.locator('dd').all_text_contents() == ['Yes', 'No']
                answer = page.get_by_label('Evidence-based interpretation').inner_text()
                assert 'possible canopy loss' in answer and 'before that period' in answer
                assert 'does not establish cutting' in answer
                assert page.locator('.satellite-pair img').evaluate_all('(nodes)=>nodes.every(n=>n.complete&&n.naturalWidth>0)')
                assert page.locator('.satellite-answer a').evaluate_all('(links)=>links.every(a=>document.querySelector(a.getAttribute("href")))')
                assert page.locator('.satellite-results').inner_text().count('OpenAI Decisions') == 1
                assert presence.bounding_box()['y'] < page.get_by_label('Evidence-based interpretation').bounding_box()['y']
                overflow = page.evaluate('document.documentElement.scrollWidth>innerWidth')
                assert not overflow
                assert not page.locator('.satellite-results').evaluate('(root)=>[root,...root.querySelectorAll("*")].some(n=>getComputedStyle(n).fontStyle!=="normal")')
                assert not errors
                page.locator('.satellite-results').evaluate('''root=>{const label=document.createElement('p'); label.textContent='UI TEST — synthetic imagery and Decisions answers. Not a real finding.'; label.style.cssText='font-weight:750;padding:16px;background:#fff1cf;color:#193e32';root.prepend(label)}''')
                page.locator('.nav').evaluate_all('(nodes)=>nodes.forEach(n=>n.style.visibility="hidden")')
                page.locator('.satellite-results').screenshot(path=str(output/f'{name}-synthetic-decisions.png'))
                page.get_by_label('Search from').fill('2025-10-02')
                assert page.locator('.satellite-results').count() == 0
                results.append({'viewport': name, 'width': width, 'real_named_account_login': True,
                    'synthetic_provider_flow': True, 'yes_no_pair': True, 'grounded_interpretation': True,
                    'overlapping_window_caveat': True, 'working_evidence_links': True, 'decoded_images': True,
                    'result_cleared_on_date_change': True, 'horizontal_overflow': overflow, 'page_errors': errors})
                context.close()
            browser.close()
    finally:
        for process in processes: process.terminate()
        for process in processes:
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
        for log in logs: log.close()
        (output/'browser.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps({'passed': len(results), 'evidence': str(output/'browser.json')}))


if __name__ == '__main__':
    if '--service' in sys.argv: fixture_service()
    else: main()
