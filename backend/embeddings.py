"""Offline MiniLM inference using the model already shipped with the field guide."""
from pathlib import Path
import hashlib
import os
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parents[1]

class Encoder:
    def __init__(self, model_dir=None):
        directory = Path(model_dir or ROOT / 'public/models/all-MiniLM-L6-v2')
        self.tokenizer = Tokenizer.from_file(str(directory / 'tokenizer.json'))
        self.tokenizer.enable_truncation(max_length=256)
        self.tokenizer.enable_padding(pad_id=0, pad_token='[PAD]')
        options = ort.SessionOptions()
        options.intra_op_num_threads = 2
        options.inter_op_num_threads = 1
        model = directory / 'onnx/model_quantized.onnx'
        self.fingerprint = hashlib.sha256(model.read_bytes()).hexdigest()
        self.session = ort.InferenceSession(str(model), sess_options=options, providers=['CPUExecutionProvider'])

    def encode(self, texts):
        encoded = self.tokenizer.encode_batch(texts)
        data = {
            'input_ids': np.array([e.ids for e in encoded], dtype=np.int64),
            'attention_mask': np.array([e.attention_mask for e in encoded], dtype=np.int64),
            'token_type_ids': np.array([e.type_ids for e in encoded], dtype=np.int64),
        }
        output = self.session.run(None, {i.name: data[i.name] for i in self.session.get_inputs()})[0]
        if output.ndim == 3:
            mask = data['attention_mask'][..., None]
            output = (output * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1)
        return (output / np.maximum(np.linalg.norm(output, axis=1, keepdims=True), 1e-12)).astype(np.float32)

    def chunks(self, text, size=190, overlap=30):
        # A separate untruncated tokenizer avoids dropping the end of a long page.
        tokens = self.chunk_tokenizer.encode(text, add_special_tokens=False).offsets
        for start in range(0, len(tokens), size-overlap):
            end = min(start+size, len(tokens))
            left, right = tokens[start][0], tokens[end-1][1]
            if right > left:
                yield left, right, text[left:right]
            if end == len(tokens):
                break

    @property
    def chunk_tokenizer(self):
        if not hasattr(self, '_chunk_tokenizer'):
            self._chunk_tokenizer = Tokenizer.from_str(self.tokenizer.to_str())
            self._chunk_tokenizer.no_truncation()
            self._chunk_tokenizer.no_padding()
        return self._chunk_tokenizer
