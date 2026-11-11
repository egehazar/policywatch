"""Decision-model client plus a score cache.

A decision model answers many yes/no questions about one text in a single request (llama.cpp's /v1/systemone with a
Kev model, or TypeSafe's hosted endpoint). It returns a probability per question. Scores are cached in SQLite keyed by
(scorer id, sha256 of the exact text, question id), so a text is read once per bank, however many reports need it.
"""
import hashlib, json, os, random, sqlite3, threading, time, urllib.error, urllib.request

# The wrapper and its id must stay identical to the r20 harness (decision-serving/play/outward/sweep.py q_obj),
# or seeded scores would be mixed with scores of a different prompt.
WRAPPER_ID = 'systemone-noul-q_obj-v1'


def q_obj(q):
    return {'type': 'noul', 'instructions': f'Answer this question about the text: {q}',
            'criteria': {'true': 'Yes, this is true of the text.', 'false': 'No, this is not true of the text.'}}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def qid(question):
    return sha(question)[:16]


class Server:
    """llama.cpp /v1/systemone. `url` like http://127.0.0.1:9995. `name` names the model for the cache key."""

    def __init__(self, url, name='kev-4b-q8', timeout=3600):
        self.url, self.timeout = url.rstrip('/'), timeout
        self.served = self.served_model()
        # The cache key names the model the server actually reports, so swapping the model behind the port can
        # never reuse old scores. (Review 11-11: the key used to be only the --model-name label.)
        self.id = f'{name}|{self.served or "unknown-model"}|{WRAPPER_ID}'

    def served_model(self):
        try:
            with urllib.request.urlopen(self.url + '/v1/models', timeout=15) as r:
                d = json.loads(r.read())
            mid = (d.get('data') or d.get('models') or [{}])[0]
            return os.path.basename(str(mid.get('id') or mid.get('model') or mid.get('name') or '')) or None
        except Exception:
            return None

    def health(self):
        try:
            with urllib.request.urlopen(self.url + '/health', timeout=15) as r: return r.status == 200
        except Exception:
            return False

    def ask(self, text, questions):
        """questions: {key: question text} -> {key: p(yes)}"""
        body = json.dumps({'state': text, 'questions': {k: q_obj(v) for k, v in questions.items()}}).encode()
        req = urllib.request.Request(self.url + '/v1/systemone', body, {'Content-Type': 'application/json'})
        for attempt in range(8):
            try:
                r = json.loads(urllib.request.urlopen(req, timeout=self.timeout).read())
                return {k: round(float(v['noul']), 4) for k, v in r['answers'].items()}
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503) and attempt < 7: time.sleep(min(60, 2 ** attempt) + random.random()); continue
                raise
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt < 7: time.sleep(min(60, 2 ** attempt)); continue
                raise


class Cache:
    def __init__(self, path):
        d = os.path.dirname(os.path.abspath(path)); os.makedirs(d, exist_ok=True)
        self.db = sqlite3.connect(path, check_same_thread=False); self.lock = threading.Lock()
        self.db.execute('CREATE TABLE IF NOT EXISTS scores (scorer TEXT, text_sha TEXT, qid TEXT, p REAL, '
                        'PRIMARY KEY (scorer, text_sha, qid))')
        self.db.commit()

    def get(self, scorer, text, qids):
        h = sha(text)
        with self.lock:
            rows = self.db.execute(f"SELECT qid, p FROM scores WHERE scorer=? AND text_sha=? AND qid IN ({','.join('?' * len(qids))})",
                                   [scorer, h, *qids]).fetchall()
        return dict(rows)

    def put(self, scorer, text, ps):
        h = sha(text)
        with self.lock:
            self.db.executemany('INSERT OR REPLACE INTO scores VALUES (?,?,?,?)', [(scorer, h, q, p) for q, p in ps.items()])
            self.db.commit()

    def close(self):
        with self.lock: self.db.close()

    def count(self):
        with self.lock:
            return self.db.execute('SELECT COUNT(*) FROM scores').fetchone()[0]


class Scorer:
    """Cache in front of a server. score(text, bank) -> {qid: p}, asking the server only for missing questions."""

    def __init__(self, server, cache):
        self.server, self.cache = server, cache; self.asked = 0; self.hits = 0

    def score(self, text, bank):
        want = {qid(q): q for q in bank}
        have = self.cache.get(self.server.id, text, list(want))
        missing = {k: v for k, v in want.items() if k not in have}
        self.hits += len(have)
        if missing:
            got = self.server.ask(text, missing); self.asked += len(missing)
            self.cache.put(self.server.id, text, got); have.update(got)
        return have
