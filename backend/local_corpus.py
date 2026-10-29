"""Local immutable restoration wrapper; production uses AgentCorpus directly."""
import json
import os
from pathlib import Path
from .agent_corpus import AgentCorpus, readonly
STATE=Path(os.getenv('ACTFORGOA_DEV_STATE', str(Path.home()/'.local/share/actforgoa-research-dev')))
class LocalCorpus(AgentCorpus):
    def __init__(self,root=None):
        root=Path(root or STATE/'corpus/20261027T065155-law-5bc5619b')
        self.ready=json.loads((root/'READY.json').read_text())
        generation=self.ready['generation']
        super().__init__(root,generation,root/'.research-index/generations'/generation,root/'agent-search.sqlite')
    def original(self,doc_id):
        doc=self.document(doc_id);path=(self.root/self.documents[doc_id]['raw_path']).resolve()
        if not path.is_relative_to((self.root/'corpus/raw').resolve()):raise ValueError('Unsafe original path')
        return path,doc
