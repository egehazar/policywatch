import json, os, shutil, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from policywatch import archive, diffing, report, watch
from policywatch.scorer import Cache, Scorer, Server

FROZEN = os.path.join(ROOT, '..', 'decision-serving', 'play', 'reviewq', 'out')
PGA = os.path.join(ROOT, '..', 'decision-serving', 'data', 'pga-versions')


class Fake(BaseHTTPRequestHandler):
    """Stands in for llama.cpp /v1/systemone: p = .9 if the question's last word occurs in the text, else .1."""
    calls = 0

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        Fake.calls += 1; text = body['state'].lower(); ans = {}
        for k, q in body['questions'].items():
            word = q['instructions'].rsplit(' ', 1)[-1].strip('?').lower()
            ans[k] = {'noul': .9 if word in text else .1}
        raw = json.dumps({'answers': ans}).encode()
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)

    def log_message(self, *a): pass


BANK = [{'case': 1, 'title': 'Arbitration', 'classification': 'bad', 'q': 'Does the text mention arbitration?'},
        {'case': 2, 'title': 'Cookies', 'classification': 'neutral', 'q': 'Does the text mention cookies?'},
        {'case': 3, 'title': 'Deletion', 'classification': 'good', 'q': 'Does the text mention deletion?'}]
OLD = 'Intro.\n\nWe use cookies.\n\nMiddle one.\n\nMiddle two.\n\nMiddle three.\n\nYou may request deletion within 30 days.\n\nEnd.'
NEW = 'Intro.\n\nWe use cookies.\n\nMiddle one.\n\nMiddle two.\n\nMiddle three.\n\nYou may request account removal within 14 days.\n\nDisputes go to arbitration.\n\nEnd.'


class U:
    platform, doc, path, commit, date, key = 'Demo', 'Terms of Service', 'Demo/Terms of Service.md', 'abc123', '2026-11-01', '2026-11-01_Demo_Terms-of-Service_abc123'


class Pipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(('127.0.0.1', 0), Fake); threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()
        cls.url = f'http://127.0.0.1:{cls.httpd.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close()

    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.caches = []

    def tearDown(self):
        for c in self.caches: c.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cache(self):
        c = Cache(os.path.join(self.tmp, 'c.sqlite')); self.caches.append(c); return c

    def test_flags_localizes_and_caches(self):
        sc = Scorer(Server(self.url, 'fake'), self.cache())
        rec = watch.analyze(U, OLD, NEW, sc, BANK, tau=.3)
        self.assertEqual(rec['kind'], 'scored')
        by = {x['title']: x for x in rec['questions']}
        self.assertAlmostEqual(by['Arbitration']['dp'], .8); self.assertAlmostEqual(by['Deletion']['dp'], .8)
        self.assertEqual(by['Cookies']['dp'], 0)
        self.assertEqual(rec['n_flagged'], 2)
        self.assertEqual(rec['numeric'][0], {'old': 'You may request deletion within 30 days.', 'new': 'You may request account removal within 14 days.'})
        self.assertEqual(len(rec['blocks']), 1)            # one changed block -> evidence is that block
        self.assertEqual(by['Arbitration']['block'], 0)
        calls = Fake.calls; asked = sc.asked
        rec2 = watch.analyze(U, OLD, NEW, sc, BANK, tau=.3)
        self.assertEqual(Fake.calls, calls); self.assertEqual(sc.asked, asked)   # second run: all from cache
        self.assertEqual(rec2['questions'], rec['questions'])

    def test_localization_across_blocks(self):
        old = 'A.\n\nWe use cookies.\n\nB.\n\nC.\n\nD.\n\nNothing here.\n\nE.'
        new = 'A.\n\nWe use tracking pixels.\n\nB.\n\nC.\n\nD.\n\nNothing here, see arbitration.\n\nE.'
        sc = Scorer(Server(self.url, 'fake'), self.cache())
        rec = watch.analyze(U, old, new, sc, BANK, tau=.3)
        by = {x['title']: x for x in rec['questions']}
        self.assertEqual(len(rec['blocks']), 2)
        self.assertEqual(by['Cookies']['block'], 0); self.assertEqual(by['Arbitration']['block'], 1)

    def test_formatting_and_rewrite(self):
        sc = Scorer(Server(self.url, 'fake'), self.cache())
        same = watch.analyze(U, 'See [here](http://a.com/1).\n\nB.', 'See [here](http://b.com/2).\n\n  B.  ', sc, BANK, .3)
        self.assertEqual(same['kind'], 'formatting')
        big_new = '\n\n'.join(f'New paragraph {i}.' for i in range(90))
        self.assertEqual(watch.analyze(U, 'Old.', big_new, sc, BANK, .3)['kind'], 'rewrite')

    def test_chunking_keeps_max(self):
        ch = diffing.diff('\n\n'.join(f'p{i} same' for i in range(40)),
                          '\n\n'.join(f'p{i} same' if i % 10 else f'p{i} changed text' for i in range(40)))
        parts = diffing.chunks(ch, 60)
        self.assertGreater(len(parts), 1)
        self.assertEqual(sum(len(p.blocks) for p in parts), len(ch.blocks))

    def test_report_builds(self):
        sc = Scorer(Server(self.url, 'fake'), self.cache())
        watch.save(watch.analyze(U, OLD, NEW, sc, BANK, .3), self.tmp)
        site, n = report.build(self.tmp, 'https://github.com/x/y', 3)
        self.assertEqual(n, 1)
        with open(os.path.join(site, U.key + '.html'), encoding='utf-8') as f: page = f.read()
        self.assertIn('Arbitration', page); self.assertIn('<ins>', page); self.assertIn('https://github.com/x/y/commit/abc123', page)
        self.assertIn('Number and date changes (1)', page)


@unittest.skipUnless(os.path.exists(os.path.join(FROZEN, 'pairs.jsonl')) and os.path.isdir(PGA), 'frozen r20 test not on disk')
class FrozenRegions(unittest.TestCase):
    def test_regions_match_frozen_test(self):
        """The tool's region text must equal the r20 test's byte for byte, or seeded scores would be wrong."""
        pairs = [json.loads(l) for l in open(os.path.join(FROZEN, 'pairs.jsonl'), encoding='utf-8')]
        for p in pairs:
            u = archive.Update(p['platform'], p['doc'][:-3], p['doc'] if '/' in p['doc'] else f"{p['platform']}/{p['doc']}", p['commit'], p['date'])
            old, new = archive.texts(PGA, u)
            ch = diffing.diff(old, new)
            self.assertEqual(ch.old_region, p['old_region'], p['id']); self.assertEqual(ch.new_region, p['new_region'], p['id'])
            self.assertEqual(ch.n_changed, p['n_changed'], p['id'])
            self.assertEqual(bool(ch.numeric), p['rule'], p['id'])


if __name__ == '__main__':
    unittest.main()
