"""Browser acceptance for answer-first presentation using explicit API fixtures.

Run against a built frontend preview; no model calls or semantic acceptance.
python3 tests/research/answer_first_browser.py --base-url http://127.0.0.1:4193
"""
import argparse
import json
from pathlib import Path
import shutil

from playwright.sync_api import expect, sync_playwright


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:4193')
    parser.add_argument('--output-dir', default='.reports/answer-first')
    args = parser.parse_args()
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    source = {
        'id': 'passage-fixture', 'document_id': 'document-fixture', 'page': 17,
        'label': 'PDF page 17', 'title': 'Coastal survey fixture',
        'url': 'https://example.org/survey.pdf',
        'reader_url': '/documents/document-fixture?generation=fixture&page=17&passage=passage-fixture',
        'text': 'At Site A, mangroves sheltered juvenile fish. This does not establish conditions at Site B.',
        'origin': 'fixture', 'warning': '', 'retrieved_at': '2020-06-01',
        'format': 'pdf', 'matches': ['semantic'], 'generation': 'fixture',
    }
    answer = {
        'status': 'answered', 'coverage': 'partial', 'domain': 'all',
        'paragraphs': [{'text': 'The survey found juvenile fish sheltering among mangroves at Site A.',
                        'citations': [source['id']]}],
        'citations': [source], 'outside_context': None,
        'library_notice': 'The excerpt does not establish conditions at Site B.',
    }
    checks, errors = [], []
    with sync_playwright() as pw:
        executable = shutil.which('chromium')
        browser = pw.chromium.launch(**({'executable_path': executable} if executable else {}),
                                    args=['--no-sandbox'])
        for width in (1440, 390, 320):
            context = browser.new_context(viewport={'width': width, 'height': 1000}, reduced_motion='reduce')
            state = {'available': True, 'failure': False, 'requests': [], 'searches': 0}

            def api(route):
                path = route.request.url.split('/api/', 1)[-1]
                if path == 'status':
                    route.fulfill(json={'search_ready': True, 'chat_ready': state['available'],
                                        'provider': 'anthropic', 'stats': {'documents': 2},
                                        'domains': ['legal', 'ecology']})
                elif path.startswith('search?'):
                    state['searches'] += 1
                    route.fulfill(json={'results': [source], 'domain': 'all'})
                elif path == 'chat':
                    state['requests'].append(route.request.post_data_json)
                    if state['failure']:
                        route.fulfill(status=502, json={'detail': 'The answer could not be verified against its citations.'})
                    else:
                        route.fulfill(json=answer)
                elif path == 'curation':
                    route.fulfill(json={'starredIds': []})
                elif path.startswith('documents/document-fixture/pages?'):
                    route.fulfill(json={'pages': [{'page': 17, 'label': source['label'],
                                                   'text': source['text'], 'origin': 'fixture', 'warning': ''}]})
                elif path.startswith('documents/document-fixture/passages/'):
                    route.fulfill(json={'page': 17, 'start': 0, 'end': len(source['text'])})
                elif path.startswith('documents/document-fixture?'):
                    route.fulfill(json={**source, 'id': source['document_id'], 'page_count': 20,
                                        'sha256': 'fixture', 'quality': {'ocr_pages': 0, 'low_text_pages': 0},
                                        'original_url': source['url'], 'text_url': 'https://example.org/survey.txt'})
                else:
                    route.fulfill(status=404, json={'detail': 'No fixture for this endpoint'})

            context.route('**/api/**', api)
            context.route('**/data/crm.json', lambda route: route.fulfill(
                json={'version': 'fixture', 'records': [], 'opportunities': []}))
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))

            def open_page():
                page.goto(args.base_url + '/ask', wait_until='networkidle')
                expect(page.get_by_role('button', name='Answer', exact=True)).to_have_attribute('aria-pressed', 'true')

            def ask(text):
                page.locator('#research-question').fill(text)
                page.get_by_role('button', name='Ask', exact=True).click()

            open_page()
            ask('What did the survey find?')
            turn = page.locator('.research-turn').first
            expect(turn.locator('.answer-paragraph').first).to_have_text(answer['paragraphs'][0]['text'] + '[1]')
            sources = turn.locator('details.research-sources')
            assert not sources.evaluate('(element) => element.open')
            expect(sources.locator('.research-source')).not_to_be_visible()
            assert turn.locator('.research-answer').bounding_box()['y'] < sources.bounding_box()['y']
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            page.evaluate("document.activeElement?.blur(); window.scrollTo({top: 0, behavior: 'instant'})")
            page.screenshot(path=str(output / f'answer-first-{width}.png'), full_page=True)
            turn.get_by_role('link', name='Source 1:', exact=False).click()
            expect(page.locator('.document-text mark')).to_have_text(source['text'])
            page.get_by_role('link', name='Back to your research', exact=True).click()
            expect(page.locator('.research-turn')).to_have_count(1)
            expect(page.locator('details.research-sources .research-source')).not_to_be_visible()
            ask('What about Site B?')
            expect(page.locator('.research-turn')).to_have_count(2)
            history = state['requests'][-1]['history']
            assert history[0] == {'role': 'user', 'content': 'What did the survey find?'}
            assert history[1]['role'] == 'assistant' and 'juvenile fish' in history[1]['content']
            checks.append({'width': width, 'case': 'answer first, collapsed sources, citation and contextual follow-up', 'passed': True})

            state['failure'] = True
            open_page()
            ask('What did the survey find?')
            expect(page.get_by_role('alert')).to_contain_text('answer could not be verified')
            sources = page.locator('details.research-sources')
            expect(sources.locator(':scope > summary')).to_contain_text('View matching sources')
            assert not sources.evaluate('(element) => element.open')
            expect(page.locator('.research-answer')).to_have_count(0)
            expect(sources.locator('.research-source')).not_to_be_visible()
            sources.locator(':scope > summary').click()
            expect(sources.locator('.research-source')).to_be_visible()
            checks.append({'width': width, 'case': 'generation failure is explicit with opt-in sources', 'passed': True})

            state.update(available=False, failure=False)
            open_page()
            page.locator('#research-question').fill('What did the survey find?')
            expect(page.get_by_role('button', name='Ask', exact=True)).to_be_disabled()
            expect(page.get_by_text('Answers are unavailable right now.', exact=False)).to_be_visible()
            previous_requests, previous_searches = len(state['requests']), state['searches']
            page.locator('#research-question').press('Control+Enter')
            assert len(state['requests']) == previous_requests and state['searches'] == previous_searches
            page.get_by_role('button', name='Find sources', exact=True).click()
            page.locator('button.research-submit').click()
            sources = page.locator('details.research-sources')
            expect(sources.locator('.research-source')).to_be_visible()
            assert sources.evaluate('(element) => element.open')
            assert len(state['requests']) == previous_requests
            checks.append({'width': width, 'case': 'unavailable answers do not silently become search; explicit browsing works', 'passed': True})
            context.close()
        browser.close()
    assert not errors, errors
    report = {'checks': checks, 'pageErrors': errors,
              'scope': 'API fixtures; no live provider calls or semantic acceptance'}
    (output / 'browser.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
