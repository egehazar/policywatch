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

    def test_review_server_and_human_record(self):
        import urllib.request
        from policywatch import serve
        sc = Scorer(Server(self.url, 'fake'), self.cache())
        watch.save(watch.analyze(U, OLD, NEW, sc, BANK, .3), self.tmp); report.build(self.tmp, '', 3)
        httpd = serve.ThreadingHTTPServer(('127.0.0.1', 0), serve.make_handler(self.tmp))
        threading.Thread(target=httpd.serve_forever, daemon=True).start(); base = f'http://127.0.0.1:{httpd.server_port}'
        try:
            def post(body):
                req = urllib.request.Request(base + '/api/verdict', json.dumps(body).encode(), {'Content-Type': 'application/json'})
                with urllib.request.urlopen(req) as r: return json.loads(r.read())
            self.assertTrue(post({'key': U.key, 'case': 1, 'verdict': 'changed'})['ok'])        # Arbitration, flagged
            post({'key': U.key, 'case': 3, 'verdict': 'changed'}); post({'key': U.key, 'case': 3, 'verdict': 'not_changed'})  # last wins
            post({'key': U.key, 'case': 2, 'verdict': 'missed'})                                # Cookies, not flagged
            with self.assertRaises(urllib.error.HTTPError) as cm: post({'key': U.key, 'case': 2, 'verdict': 'whatever'})
            cm.exception.close()
            with urllib.request.urlopen(base + '/api/verdicts?key=' + U.key) as r: self.assertEqual(len(json.loads(r.read())), 3)
            with urllib.request.urlopen(base + '/' + U.key + '.html') as r: self.assertIn(b'class="rv"', r.read())
        finally:
            httpd.shutdown(); httpd.server_close()
        report.build(self.tmp, '', 3)
        with open(os.path.join(self.tmp, 'human_record.json')) as f: hr = json.load(f)
        self.assertEqual(hr, {'updates_reviewed': 1, 'flags_confirmed': 1, 'flags_wrong': 1, 'flags_unsure': 0, 'misses': 1})
        with open(os.path.join(self.tmp, 'site', 'index.html'), encoding='utf-8') as f: self.assertIn('1 of 2 judged flags confirmed', f.read())


class Noise(unittest.TestCase):
    def test_revert_and_partial(self):
        import subprocess
        d = tempfile.mkdtemp()
        try:
            run = lambda *a: subprocess.run(['git', '-C', d, *a], capture_output=True, check=True)
            run('init', '-q'); run('config', 'user.email', 't@t'); run('config', 'user.name', 't')
            os.makedirs(os.path.join(d, 'P'))
            A = '\n\n'.join(f'Para {i}.' for i in range(20)); B = A.replace('Para 3.', 'Para 3 changed.')
            C = '\n\n'.join(f'Para {i}.' for i in range(8))          # cut-off capture of A
            for i, t in enumerate((A, B, A, C)):
                with open(os.path.join(d, 'P', 'Terms of Service.md'), 'w') as f: f.write(t)
                run('add', '-A')
                run('commit', '-q', '-m', 'Record new changes of P Terms of Service' if i else 'First record', '--date', f'2026-01-0{i + 1}T00:00:00')
            us = archive.updates(d); self.assertEqual(len(us), 3)
            H = archive.History(d, 'P/Terms of Service.md')
            got = []
            for u in sorted(us, key=lambda u: H.pos[u.commit]):
                old, new = archive.texts(d, u); got.append((H.classify(u.commit, old, new) or {}).get('noise'))
            self.assertEqual(got, [None, 'revert', 'partial'])
            # dates are filtered in Python: git's --since stops early on histories that are not in date order
            self.assertEqual([u.date for u in archive.updates(d, since='2026-01-03')], ['2026-01-04', '2026-01-03'])
            self.assertEqual([u.date for u in archive.updates(d, until='2026-01-02')], ['2026-01-02'])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class MemoCheck(unittest.TestCase):
    def test_variants(self):
        from policywatch import memocheck
        bank = watch.load_bank(os.path.join(ROOT, 'data', 'bank.json'))
        T = memocheck._load('memo_targets.json')['memos']
        d = tempfile.mkdtemp(); os.makedirs(os.path.join(d, 'updates'))
        try:
            def rec(plat, doc, date, hot):
                qs = [{'case': b['case'], 'title': b['title'], 'q': b['q'], 'p_old': .1, 'p_new': .1 + (.8 if i in hot else .05 * (i % 7 == 0)),
                       'dp': .8 if i in hot else .05 * (i % 7 == 0)} for i, b in enumerate(bank)]
                qs.sort(key=lambda x: -x['dp'])
                r = {'platform': plat, 'doc': doc, 'date': date, 'kind': 'scored', 'tau': .3, 'questions': qs, 'key': f'{date}_{plat}'}
                with open(os.path.join(d, 'updates', r['key'] + '.json'), 'w', encoding='utf-8') as f: json.dump(r, f)
            rec('TikTok', 'Privacy Policy', '2025-12-14', {5})            # M5 target 5 -> caught everywhere
            rec('LinkedIn', 'Privacy Policy', '2025-11-04', {98, 1, 2, 3, 4, 6, 7})   # M6: only 98 moves among targets
            res = memocheck.check(d, T, bank)
            by = {r['id']: r for r in res['rows']}
            self.assertEqual(by['M5']['primary'], 'CAUGHT'); self.assertEqual(by['M5']['v1'], 'CAUGHT')
            self.assertEqual(by['M6']['primary'], 'CAUGHT'); self.assertEqual(by['M6']['v1'], 'missed')   # a v1 miss stays a miss
            self.assertEqual(by['M8']['primary'], 'coverage gap')
            self.assertTrue(by['M1']['primary'].startswith('not scored'))
            self.assertEqual(res['summary']['caught'], 2); self.assertEqual(res['summary']['variants']['v1']['caught'], 1)
        finally:
            shutil.rmtree(d, ignore_errors=True)


@unittest.skipUnless(os.path.exists(os.path.join(FROZEN, 'pairs.jsonl')) and os.path.isdir(PGA), 'frozen r20 test not on disk')
class FrozenRegions(unittest.TestCase):
    def test_regions_match_frozen_test(self):
        """The tool's region text must equal the r20 test's byte for byte, or seeded scores would be wrong."""
        with open(os.path.join(FROZEN, 'pairs.jsonl'), encoding='utf-8') as f: pairs = [json.loads(l) for l in f]
        for p in pairs:
            u = archive.Update(p['platform'], p['doc'][:-3], p['doc'] if '/' in p['doc'] else f"{p['platform']}/{p['doc']}", p['commit'], p['date'])
            old, new = archive.texts(PGA, u)
            ch = diffing.diff(old, new)
            self.assertEqual(ch.old_region, p['old_region'], p['id']); self.assertEqual(ch.new_region, p['new_region'], p['id'])
            self.assertEqual(ch.n_changed, p['n_changed'], p['id'])
            self.assertEqual(bool(ch.numeric), p['rule'], p['id'])


if __name__ == '__main__':
    unittest.main()
