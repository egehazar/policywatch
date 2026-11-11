"""Local review server: the report site plus a human verdict store (out/verdicts.jsonl).

A reviewer marks each flagged answer "changed" / "not changed" / "unsure", and can add a change the tool missed.
Verdicts are append-only JSON lines (the last verdict per (update, case) wins); `report` turns them into running
precision and audited misses. Listens on 127.0.0.1 only.
"""
import json, os, re, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

VERDICTS = ('changed', 'not_changed', 'unsure', 'missed', 'retract')
KEY_RE = re.compile(r'[\w.-]{1,200}')


def load_verdicts(out_dir):
    p = os.path.join(out_dir, 'verdicts.jsonl'); latest = {}
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            for l in f:
                try:
                    v = json.loads(l); v['case'] = str(int(v['case'])); assert v['verdict'] in VERDICTS; latest[(str(v['key']), v['case'])] = v
                except (ValueError, TypeError, KeyError, AssertionError):
                    continue    # a malformed line is skipped, never fatal
    return {k: v for k, v in latest.items() if v['verdict'] != 'retract'}


def make_handler(out_dir):
    site = os.path.join(out_dir, 'site')

    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=site, **kw)

        def _json(self, code, obj):
            raw = json.dumps(obj).encode(); self.send_response(code)
            self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(raw)))
            self.end_headers(); self.wfile.write(raw)

        def do_GET(self):
            if self.path.startswith('/api/verdicts'):
                key = self.path.split('key=', 1)[1] if 'key=' in self.path else None
                vs = [v for (k, _), v in load_verdicts(out_dir).items() if key is None or k == key]
                return self._json(200, vs)
            return super().do_GET()

        def do_POST(self):
            if self.path != '/api/verdict': return self._json(404, {'error': 'not found'})
            # Only same-origin JSON: a text/plain POST from another page in the reviewer's browser is refused.
            origin = self.headers.get('Origin')
            if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):
                return self._json(403, {'error': 'cross-origin'})
            if not (self.headers.get('Content-Type') or '').startswith('application/json'):
                return self._json(415, {'error': 'json only'})
            try:
                v = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
                assert isinstance(v, dict) and v.get('verdict') in VERDICTS
                assert isinstance(v.get('key'), str) and KEY_RE.fullmatch(v['key'])
                assert os.path.exists(os.path.join(out_dir, 'updates', v['key'] + '.json'))
                case = v.get('case')
                assert (isinstance(case, int) and not isinstance(case, bool)) or (isinstance(case, str) and case.isdigit())
            except Exception:
                return self._json(400, {'error': 'bad verdict'})
            rec = {'key': v['key'], 'case': str(int(case)), 'verdict': v['verdict'], 'note': str(v.get('note', ''))[:500],
                   'at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
            with open(os.path.join(out_dir, 'verdicts.jsonl'), 'a', encoding='utf-8') as f: f.write(json.dumps(rec) + '\n')
            return self._json(200, {'ok': True})

        def log_message(self, *a): pass
    return H


def serve(out_dir, port):
    httpd = ThreadingHTTPServer(('127.0.0.1', port), make_handler(out_dir))
    print(f'review at http://127.0.0.1:{port}/  (verdicts -> {os.path.join(out_dir, "verdicts.jsonl")})', flush=True)
    httpd.serve_forever()
