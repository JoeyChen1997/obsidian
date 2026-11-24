"""Optional local dense document retrieval using MiniLM (title + abstract or first-page text)."""

import argparse
from contextlib import closing
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
import time

import corpus_rag
import paperlist

DEFAULT_DB = corpus_rag.DEFAULT_DB.with_name('research-vectors.sqlite3')
MODEL_DIR = DEFAULT_DB.parent / 'minilm-v1'
WIDTH = 384
MAX_TOKENS = 160


class Encoder:
    def __init__(self, threads=8):
        import os
        os.environ.setdefault('TOKENIZERS_PARALLELISM','false')
        import onnxruntime as ort
        from tokenizers import Tokenizer

        model = MODEL_DIR / 'model_quantized.onnx'
        tokenizer = MODEL_DIR / 'tokenizer.json'
        if not model.is_file() or not tokenizer.is_file():
            raise ValueError(f'Local MiniLM model not installed at {MODEL_DIR}')
        self.version = ':'.join(sha256(p.read_bytes()).hexdigest() for p in (model, tokenizer)) + f':mean-{MAX_TOKENS}'
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = threads
        opts.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(model), sess_options=opts, providers=['CPUExecutionProvider'])
        self.inputs = {x.name for x in self.session.get_inputs()}
        self.tokenizer = Tokenizer.from_file(str(tokenizer))
        self.tokenizer.enable_truncation(max_length=MAX_TOKENS)
        self.tokenizer.enable_padding(pad_id=0, pad_token='[PAD]')

    def encode(self, texts):
        import numpy as np

        batch = self.tokenizer.encode_batch(texts)
        mask = np.asarray([x.attention_mask for x in batch], dtype=np.int64)
        inputs = {'input_ids':np.asarray([x.ids for x in batch], dtype=np.int64),
                  'attention_mask':mask,
                  'token_type_ids':np.asarray([x.type_ids for x in batch], dtype=np.int64)}
        hidden = self.session.run(None, {k:v for k,v in inputs.items() if k in self.inputs})[0]
        v = np.einsum('bld,bl->bd', hidden, mask.astype(np.float32))
        v /= np.maximum(np.linalg.norm(v,axis=1,keepdims=True),1e-9)
        if v.shape[1] != WIDTH:
            raise ValueError('Unexpected MiniLM embedding dimension.')
        return v


def vectors(path, writable=False):
    if writable:
        path.parent.mkdir(parents=True,exist_ok=True)
        con = sqlite3.connect(path,timeout=20)
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA synchronous=NORMAL')
        con.executescript('''CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS vectors(id INTEGER PRIMARY KEY, stamp TEXT NOT NULL, value BLOB NOT NULL);''')
    else:
        if not path.is_file():
            raise ValueError('Dense index has not been built yet.')
        con = sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True,timeout=10)
    return con


def build(args):
    start = time.monotonic()
    encoder = Encoder(args.threads)
    with paperlist.build_lock(args.db), closing(corpus_rag.connect(args.corpus)) as src, closing(vectors(args.db, True)) as dest:
        binding = {'source':str(args.corpus.resolve()), 'encoder':encoder.version}
        saved = dict(dest.execute('SELECT key,value FROM settings'))
        if saved and saved != binding:
            raise ValueError('Dense index is tied to a different corpus or model; use another --db.')
        docs = src.execute("SELECT id,stamp,title,abstract FROM docs WHERE page_count>0 ORDER BY id").fetchall()
        old = dict(dest.execute('SELECT id,stamp FROM vectors'))
        current = {r['id'] for r in docs}
        with dest:
            dest.executemany('INSERT OR IGNORE INTO settings VALUES (?,?)', binding.items())
            dest.executemany('DELETE FROM vectors WHERE id=?',((k,) for k in old.keys()-current))
        candidates = [r for r in docs if old.get(r['id']) != r['stamp']]
        if args.limit:
            candidates = candidates[:args.limit]
        print(f'Dense: {len(docs):,} eligible; {len(candidates):,} queued',flush=True)
        last = start
        for offset in range(0,len(candidates),256):
            batch = candidates[offset:offset+256]
            # Group similar lengths to avoid padding short abstracts to the longest in each batch.
            batch.sort(key=lambda r:len(r['abstract'] or ''))
            with dest:
                for i in range(0,len(batch),32):
                    group = batch[i:i+32]
                    emb = encoder.encode([r['title'] + '. ' + (r['abstract'] or '') for r in group])
                    dest.executemany('INSERT OR REPLACE INTO vectors VALUES (?,?,?)',
                                     ((r['id'],r['stamp'],row.astype('<f2').tobytes()) for r,row in zip(group,emb)))
            now = time.monotonic()
            if now-last >= 12 or offset+len(batch)==len(candidates):
                print(f'{offset+len(batch):,}/{len(candidates):,} vectors; {now-start:.0f}s',flush=True)
                last = now


def search(con, corpus, db, terms, journals=(), limit=10, from_year=None, to_year=None):
    import numpy as np

    encoder = Encoder(6)
    clauses = []
    params = []
    if journals:
        clauses.append('upper(journal) IN (' + ','.join('?' for _ in journals) + ')')
        params.extend(j.upper() for j in journals)
    for op,year in [('>=',from_year),('<=',to_year)]:
        if year is not None:
            clauses.append(f'year{op}?')
            params.append(year)
    filters = ''.join(' AND '+f for f in clauses)
    docs = {r['id']: dict(r) for r in con.execute('SELECT id,title,author,year,journal,relpath,stamp,has_abstract FROM docs WHERE page_count>0'+filters,
                                               params)}
    with closing(vectors(db)) as store:
        saved = dict(store.execute('SELECT key,value FROM settings'))
        if saved != {'source':str(corpus.resolve()), 'encoder':encoder.version}:
            raise ValueError('Dense index not compatible with this corpus or local model.')
        rows = [(key, blob) for key, version, blob in store.execute('SELECT id,stamp,value FROM vectors')
                if key in docs and docs[key]['stamp'] == version]
    if not rows:
        return {'papers':[], 'vectors_searched':0}
    arr = np.frombuffer(b''.join(r[1] for r in rows),dtype='<f2').reshape(-1,WIDTH).astype(np.float32)
    query = encoder.encode(terms)
    scores = arr @ query.T
    best = scores.max(axis=1)
    order = np.argsort(-best,kind='stable')[:limit]
    result = []
    for i in order:
        doc = docs[rows[i][0]].copy()
        doc.pop('stamp')
        doc['basis'] = 'title_and_recognized_abstract' if doc.pop('has_abstract') else 'title_and_opening_text'
        result.append(doc | {'similarity':round(float(best[i]),5),'query':terms[int(scores[i].argmax())]})
    return {'papers':result, 'vectors_searched':len(rows), 'eligible_papers':len(docs),
            'note':'Dense retrieval ranks papers, not evidence passages. Open the source before using a claim.'}


def main():
    paperlist.configure_output()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',type=Path,default=DEFAULT_DB)
    p.add_argument('--corpus',type=Path,default=corpus_rag.DEFAULT_DB)
    sub = p.add_subparsers(dest='cmd',required=True)
    b = sub.add_parser('build')
    b.add_argument('--threads',type=int,choices=range(1,25),default=10)
    b.add_argument('--limit',type=paperlist.positive)
    sub.add_parser('status')
    s = sub.add_parser('search')
    s.add_argument('query',nargs='+')
    s.add_argument('--journal',action='append',default=[])
    try:
        args = p.parse_args()
        if args.cmd == 'build':
            build(args)
        elif args.cmd == 'status':
            with closing(vectors(args.db)) as con:
                print(json.dumps({'vectors':con.execute('SELECT COUNT(*) FROM vectors').fetchone()[0]}))
        else:
            with closing(corpus_rag.connect(args.corpus)) as con:
                print(json.dumps(search(con,args.corpus,args.db,args.query[:8],args.journal),ensure_ascii=False,indent=2))
    except (sqlite3.Error, OSError, ValueError, ImportError) as exc:
        print(f'corpus_vectors: {exc}',file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
