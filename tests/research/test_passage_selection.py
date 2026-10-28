"""Requested details should beat repeated headings without source-specific rules."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy

from backend.passage_selection import select_passages

STOP=set('what are the and for is who must about a to'.split())


def pool(texts, title='Beacon register'):
    return {f'p{i}':({'doc_id':'doc','text':text},{'title':title}) for i,text in enumerate(texts)}


def test_two_slots_cover_two_requested_details_instead_of_cover_and_intro():
    candidates=pool(['Beacon register handbook.', 'An introduction to the Beacon register.',
                     'The registration price is five units.', 'The required signature is that of the applicant.'])
    before=deepcopy(candidates)
    scores={'p0':.09,'p1':.08,'p2':.05,'p3':.05}
    selected=select_passages('What are the price and signature requirements for the Beacon register?',
                             candidates,['p0','p1'],scores,STOP)
    assert set(selected)=={'p2','p3'}
    assert candidates==before


def test_inflections_match_without_notify_notification_prefix_collision():
    candidates=pool(['Notifications publish the date of the amendment.',
                     'The farmer notifies the office about damage.'],title='Assistance scheme')
    result=select_passages('Who must notify the office about damage?',candidates,['p0'],
                           {'p0':.05,'p1':.04},STOP)
    assert result==['p1']


def test_concurrent_searches_do_not_share_mutable_stemming_state():
    candidates=pool(['An introduction to the Beacon register.',
                     'The registration price is five units.', 'The signature is provided by the applicant.'])
    scores={'p0':.08,'p1':.05,'p2':.05}
    questions=['What is the price for the Beacon register?', 'Who provides the signature for the Beacon register?']*12
    def select(q):return select_passages(q,candidates,['p0'],scores,STOP)
    expected=[select(q) for q in questions]
    with ThreadPoolExecutor(max_workers=4) as executor:
        assert list(executor.map(select,questions))==expected
