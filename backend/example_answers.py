"""Reviewed, public starter answers only. No user-message or conversation cache."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

EXAMPLES = (
    'How can we protect a wetland near our village?',
    'What can a village panchayat do about waste?',
    'How do khazans manage fresh and salt water?',
)

def normalize(question):
    return ' '.join(question.split()).casefold()

def eligible(request):
    return (not request.history and not request.document_id and request.domain == 'all'
            and request.include_outside_context and normalize(request.question) in {normalize(q) for q in EXAMPLES})

def runtime_digest():
    root = Path(__file__).parent
    files = sorted(root.glob('*.py')) + sorted(root.rglob('*.json')) + [root/'agent-prompt.txt']
    return hashlib.sha256(b''.join(str(p.relative_to(root)).encode()+p.read_bytes() for p in files)).hexdigest()

class ExampleAnswers:
    def __init__(self, state, runtime, crm_digest):
        self.folder = Path(state)/'example-answers'
        self.runtime = runtime
        self.crm_digest = crm_digest

    def fingerprint(self, corpus):
        return hashlib.sha256(json.dumps([self.runtime, self.crm_digest, corpus.generation, corpus.source_digest]).encode()).hexdigest()

    def path(self, request, corpus):
        key = hashlib.sha256((self.fingerprint(corpus)+normalize(request.question)).encode()).hexdigest()
        return self.folder/(key+'.json')

    def validate(self, answer, corpus):
        if answer.get('status') != 'answered' or answer.get('domain') != 'all' or answer.get('outside_context'):
            raise ValueError('Only complete library answers can be approved')
        ids = set()
        for citation in answer['citations']:
            # Starter records use original corpus evidence, not mutable directory records.
            if citation.get('format') == 'crm' or citation.get('origin') == 'official_guidance_summary': raise ValueError('Only original corpus answers are cached')
            source = corpus.evidence(citation['document_id'], citation['page'], citation['start'], citation['end'])
            if (source['answer_excluded'] or any(source.get(k) != citation.get(k) for k in ('id','text','sha256','generation','reader_url'))):
                raise ValueError('Cached citation differs from its original source')
            ids.add(citation['id'])
        if not answer['paragraphs'] or any(not p['text'].strip() or not p['citations'] or not set(p['citations']) <= ids for p in answer['paragraphs']):
            raise ValueError('Every cached paragraph must retain its citations')

    def approve(self, request, answer, corpus, *, review_note, now=None):
        if not eligible(request) or not review_note.strip(): raise ValueError('Only reviewed public starters can be cached')
        self.validate(answer, corpus)
        now = now or datetime.now(timezone.utc)
        clean = {k:v for k,v in answer.items() if k not in ('_dev','cache','timings')}
        record = {'fingerprint':self.fingerprint(corpus),'question':request.question,'reviewed_at':now.isoformat(),
                  'expires_at':(now+timedelta(days=7)).isoformat(),'review_note':review_note,'answer':clean,
                  'answer_sha256':hashlib.sha256(json.dumps(clean,sort_keys=True).encode()).hexdigest()}
        self.folder.mkdir(mode=0o700,parents=True,exist_ok=True)
        path = self.path(request,corpus);temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps(record,ensure_ascii=False));temporary.chmod(0o600);temporary.replace(path)
        return path

    def get(self, request, corpus, now=None):
        if not eligible(request): return None
        try:
            record = json.loads(self.path(request,corpus).read_text())
            if record['fingerprint'] != self.fingerprint(corpus): return None
            if datetime.fromisoformat(record['expires_at']) <= (now or datetime.now(timezone.utc)): return None
            if normalize(record['question']) != normalize(request.question): return None
            answer = record['answer']
            if record['answer_sha256'] != hashlib.sha256(json.dumps(answer,sort_keys=True).encode()).hexdigest(): return None
            self.validate(answer,corpus)
            answer = deepcopy(answer)
            answer['agent'] = {'engine':'claude-agent-sdk','model_calls':0,'tools':[],'source_run_id':answer.get('agent',{}).get('run_id')}
            answer['cache'] = {'hit':True,'kind':'reviewed_example','reviewed_at':record['reviewed_at'],'generation':corpus.generation}
            return answer
        except (OSError,ValueError,KeyError,TypeError):
            return None
