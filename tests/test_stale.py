"""Tests for the stale-evidence page's newer parts: the proposed quote, its highlight, the artifact page and the wider
OTA-collection pipeline's mapping and dedupe. No real model and no network: a fake /v1/systemone server stands in."""
import json, os, shutil, sys, tempfile, threading, unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from stale import propose, report, wide, publish_page
from stale.relocate2 import units


class FakeKev(BaseHTTPRequestHandler):
    """Reports the Kev model name; p(yes) = .9 when the text holds the question's case title, else a value that falls
    with the text's length (so ties are rare and the earliest-unit rule is still exercised by equal texts)."""
    calls = 0

    def do_GET(self):
        raw = json.dumps({'data': [{'id': 'Kev-4B-Q8_0.gguf'}]}).encode()
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        FakeKev.calls += 1; text = body['state'].lower(); ans = {}
        for k, q in body['questions'].items():
            title = q['instructions'].split('imply the following: ', 1)[-1].rsplit('?', 1)[0].lower()
            ans[k] = {'noul': .9 if title in text else .5 / (1 + len(text) / 100)}
        raw = json.dumps({'answers': ans}).encode()
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)

    def log_message(self, *a): pass


PIECE = ('Section 4. Your data.\nWe keep your messages for ninety days after you delete them, for safety reviews.\n'
         'We may share usage statistics with advertisers in aggregate form only.\nYou can export your data at any time.')


class TestPropose(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.srv = HTTPServer(('127.0.0.1', 0), FakeKev); threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        pts = [{'point': 1, 'case_title': 'usage statistics with advertisers', 'status': 'gone', 'drop_kind': 'platform edit'},
               {'point': 2, 'case_title': 'export your data', 'status': 'partly', 'drop_kind': 'platform edit'},
               {'point': 3, 'case_title': 'export your data', 'status': 'gone', 'drop_kind': 'platform edit'}]
        sug = [{'point': p['point'], 'doc': 'Demo/Privacy Policy.md', 'n_pieces': 5,
                'top': [{'piece': 2, 'score': .9, 'text': PIECE}]} for p in pts]
        with open(os.path.join(self.d, 'points.jsonl'), 'w', encoding='utf-8') as f:
            for p in pts: f.write(json.dumps(p) + '\n')
        with open(os.path.join(self.d, 'suggest_kev.jsonl'), 'w', encoding='utf-8') as f:
            for s in sug: f.write(json.dumps(s) + '\n')

    def tearDown(self):
        self.srv.shutdown(); shutil.rmtree(self.d, ignore_errors=True)

    def run_propose(self):
        propose.run(str(self.srv.server_port), self.d, os.path.join(self.d, 'cache.sqlite'))
        return {r['point']: r for r in map(json.loads, open(os.path.join(self.d, 'propose_kev.jsonl'), encoding='utf-8'))}

    def test_picks_the_unit_stating_the_case_and_shares_one_request_per_unit(self):
        FakeKev.calls = 0
        R = self.run_propose()
        self.assertEqual(sorted(R), [1, 2, 3])
        self.assertIn('advertisers', R[1]['quote']); self.assertIn('export your data', R[2]['quote'])
        self.assertEqual(R[2]['quote'], R[3]['quote'])
        self.assertEqual(R[1]['units'], len(units(PIECE)))
        self.assertEqual(FakeKev.calls, len(units(PIECE)))      # three points, one shared piece: one request per unit

    def test_resumes_without_asking_again(self):
        self.run_propose(); FakeKev.calls = 0
        R = self.run_propose()
        self.assertEqual(FakeKev.calls, 0); self.assertEqual(len(R), 3)


class TestSuggestionHighlight(unittest.TestCase):
    def card(self, text, quote):
        s = {'n_pieces': 9, 'top': [{'piece': 0, 'score': .8, 'text': text}, {'piece': 3, 'score': .5, 'text': 'Other.'}]}
        return report.suggestion(s, 'kev', {'piece': 0, 'quote': quote})

    def test_quote_past_900_characters_is_shown_and_highlighted(self):
        text = 'x ' * 600 + 'We sell your data to brokers.' + ' tail' * 50
        h = self.card(text, 'We sell your data to brokers.')
        passage1 = h.split('<details', 1)[1].split('2. passage')[0]
        self.assertIn('<ins>We sell your data to brokers.</ins>', passage1)

    def test_quote_across_joined_lines_is_highlighted(self):
        text = 'Intro line.\nShort.\nWe keep logs\nfor a year.\nEnd.'
        h = self.card(text, 'We keep logs for a year.')
        self.assertIn('<ins>We keep logs\nfor a year.</ins>', h.split('<details', 1)[1])

    def test_escaping_and_no_proposal(self):
        h = self.card('A <b> & "c" passage.', 'A <b> & "c" passage.')
        self.assertIn('<ins>A &lt;b&gt; &amp; &quot;c&quot; passage.</ins>', h); self.assertNotIn('<b>', h)
        s = {'n_pieces': 2, 'top': [{'piece': 0, 'score': .8, 'text': 'Plain.'}]}
        self.assertNotIn('Suggested quote', report.suggestion(s, 'bm25', None))


class TestWide(unittest.TestCase):
    def test_site(self):
        self.assertEqual(wide.site('www.google.com'), 'google.com')
        self.assertEqual(wide.site('policies.google.com'), 'google.com')
        self.assertEqual(wide.site('www.bbc.co.uk'), 'bbc.co.uk')
        self.assertEqual(wide.site('help.example.com.au:443'), 'example.com.au')

    def test_dedupe_keeps_each_points_best_home(self):
        tmp = tempfile.mkdtemp(); old = wide.WIDE; wide.WIDE = tmp
        try:
            os.makedirs(os.path.join(tmp, 'c', 'raw'))
            json.dump({'mapped': {'Google': {'tosdr_name': 'Google'}, 'Gmail': {'tosdr_name': 'Google'}}},
                      open(os.path.join(tmp, 'c', 'map.json'), 'w'))
            rows = [{'platform': 'Google', 'point': 7, 'status': 'not in archive', 'max_coverage': .1},
                    {'platform': 'Gmail', 'point': 7, 'status': 'gone', 'current_coverage': .1, 'max_coverage': 1.0, 'drop_kind': 'platform edit'},
                    {'platform': 'Google', 'point': 8, 'status': 'present', 'current_coverage': 1.0, 'max_coverage': 1.0},
                    {'platform': 'Gmail', 'point': 8, 'status': 'present', 'current_coverage': .9, 'max_coverage': 1.0},
                    {'platform': 'Gmail', 'point': 9, 'status': 'not in archive', 'max_coverage': .2},
                    {'platform': 'Google', 'point': 9, 'status': 'not in archive', 'max_coverage': .2}]
            with open(os.path.join(tmp, 'c', 'raw', 'points.jsonl'), 'w') as f:
                for r in rows: f.write(json.dumps(r) + '\n')
            wide.dedupe('c')
            out = {r['point']: r for r in map(json.loads, open(os.path.join(tmp, 'c', 'out', 'points.jsonl')))}
            self.assertEqual((out[7]['platform'], out[7]['status']), ('Gmail', 'gone'))
            self.assertEqual(out[8]['platform'], 'Google')
            self.assertEqual(out[9]['platform'], 'Google')            # no home anywhere: the folder named like the service
            S = json.load(open(os.path.join(tmp, 'c', 'out', 'summary.json')))
            self.assertEqual(S['total'], {'approved_with_quote': 3, 'gone': 1, 'present': 1, 'not in archive': 1})
        finally:
            wide.WIDE = old; shutil.rmtree(tmp, ignore_errors=True)


class TestBrokenCaptureGuard(unittest.TestCase):
    """A tiny archive: a real edit, a capture that collapsed to a title, and a login wall filed under two documents."""
    def setUp(self):
        import subprocess
        self.tmp = tempfile.mkdtemp(); self.arch = os.path.join(self.tmp, 'demo-versions'); os.makedirs(os.path.join(self.arch, 'S'))
        g = lambda *a: subprocess.run(['git', '-C', self.arch, *a], capture_output=True, encoding='utf-8')
        g('init', '-q'); g('config', 'user.email', 't@t'); g('config', 'user.name', 't')
        body = lambda k: '\n\n'.join(f'Paragraph {k} {i} with enough words to count as a long section of text.' for i in range(40))
        files = {'S/Edited.md': body('a'), 'S/Collapsed.md': body('b'), 'S/Walled.md': body('c'), 'S/Other.md': body('d')}
        self.commit(g, files, 'Record new changes of S')
        files['S/Edited.md'] = body('a2'); files['S/Collapsed.md'] = 'Terms\n====='
        files['S/Walled.md'] = files['S/Other.md'] = 'Log in or sign up\n\n' + body('w')[:1500]
        self.commit(g, files, 'Record new changes of S')
        self.c1, self.c2 = g('rev-list', '--reverse', 'HEAD').stdout.split()
        self.old = wide.DATA_ROOT; wide.DATA_ROOT = self.tmp

    def commit(self, g, files, msg):
        for p, t in files.items():
            with open(os.path.join(self.arch, p), 'w', encoding='utf-8') as f: f.write(t)
        g('add', '-A'); g('commit', '-q', '-m', msg)

    def tearDown(self):
        wide.DATA_ROOT = self.old; shutil.rmtree(self.tmp, ignore_errors=True)

    def test_only_the_real_edit_stays_a_platform_edit(self):
        rows = [{'point': i, 'doc': f'S/{d}.md', 'status': 'gone', 'drop_kind': 'platform edit',
                 'last_present': {'commit': self.c1}, 'dropped_at': {'commit': self.c2}}
                for i, d in enumerate(('Edited', 'Collapsed', 'Walled'))]
        self.assertEqual(wide.guard('demo', rows), 2)
        self.assertEqual([r['drop_kind'] for r in rows], ['platform edit', 'broken capture', 'broken capture'])
        self.assertEqual(rows[2]['capture_twin_of'], ['S/Other.md'])


class TestCascade(unittest.TestCase):
    """stale.cascade.kev on a throwaway collection: Kev is asked only about each case's reranker top 10."""
    def setUp(self):
        import subprocess
        from stale.relocate import PIECE
        from policywatch.watch import pieces
        from policywatch.diffing import paras
        self.tmp = tempfile.mkdtemp(); arch = os.path.join(self.tmp, 'demo-versions'); os.makedirs(os.path.join(arch, 'S'))
        g = lambda *a: subprocess.run(['git', '-C', arch, *a], capture_output=True, encoding='utf-8')
        g('init', '-q'); g('config', 'user.email', 't@t'); g('config', 'user.name', 't')
        paras_ = [f'Section {i}. ' + ('Filler words about nothing in particular. ' * 30) for i in range(40)]
        paras_[33] = 'Section 33. We sell your data to advertisers. ' + 'More words to fill the piece. ' * 30
        text = '\n\n'.join(paras_)
        with open(os.path.join(arch, 'S', 'Terms.md'), 'w', encoding='utf-8') as f: f.write(text)
        g('add', '-A'); g('commit', '-q', '-m', 'Record new changes of S')
        self.P = [p for p in pieces('\n\n'.join(paras(text)), PIECE) if p.strip()]
        self.target = next(i for i, p in enumerate(self.P) if 'sell your data' in p)
        out = os.path.join(self.tmp, 'wide', 'demo', 'out'); os.makedirs(out)
        with open(os.path.join(out, 'points.jsonl'), 'w') as f:
            f.write(json.dumps({'platform': 'S', 'point': 1, 'case_title': 'sell your data', 'doc': 'S/Terms.md', 'status': 'gone',
                                'drop_kind': 'platform edit', 'classification': 'bad', 'quote': 'We sell your data.',
                                'current_coverage': 0.1, 'point_updated_at': '2025-01-01', 'drop_after_point_update': True,
                                'dropped_at': {'commit': 'abc123', 'date': '2026-01-01', 'subject': 'Record new changes of S'}}) + '\n')
        json.dump({'total': {'approved_with_quote': 1, 'gone': 1}, 'platforms': {'S': {'approved_with_quote': 1, 'gone': 1}}},
                  open(os.path.join(out, 'summary.json'), 'w'))
        head = g('rev-parse', 'HEAD').stdout.strip()
        from stale.relocate import psha
        # the reranker likes the first 10 pieces and the target: Kev must only be asked about those 11
        rs = [1.0 if i < 10 or i == self.target else 0.0 for i in range(len(self.P))]
        json.dump({'archive_head': head, 'docs': {'S/Terms.md': {'pieces_sha': psha(self.P), 'scores': {'sell your data': rs}}}},
                  open(os.path.join(out, 'rerank_scores.json'), 'w'))
        self.out = out; self.old = (wide.DATA_ROOT, wide.WIDE); wide.DATA_ROOT = self.tmp; wide.WIDE = os.path.join(self.tmp, 'wide')
        self.srv = HTTPServer(('127.0.0.1', 0), FakeKev); threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown(); wide.DATA_ROOT, wide.WIDE = self.old; shutil.rmtree(self.tmp, ignore_errors=True)
        for f in ('stale_demo.html',):
            p = os.path.join(ROOT, 'out', 'site', f)
            if os.path.exists(p): os.remove(p)

    def test_asks_only_the_top_ten_and_finds_the_case(self):
        from stale import cascade
        self.assertGreater(len(self.P), 11)
        FakeKev.calls = 0
        cascade.kev('demo', str(self.srv.server_port), os.path.join(self.tmp, 'cache.sqlite'))
        s = json.loads(open(os.path.join(self.out, 'suggest_kev.jsonl')).readline())
        self.assertEqual(s['top'][0]['piece'], self.target)
        self.assertTrue(all(t['score'] >= 0 for t in s['top']))
        p = json.loads(open(os.path.join(self.out, 'propose_kev.jsonl')).readline())
        self.assertIn('sell your data', p['quote'])
        self.assertTrue(os.path.exists(os.path.join(ROOT, 'out', 'site', 'stale_demo.html')))


class TestPublishPage(unittest.TestCase):
    def test_theme_guards_and_no_local_nav(self):
        tmp = tempfile.mkdtemp(); old = publish_page.SITE; publish_page.SITE = tmp
        try:
            from policywatch.report import page
            with open(os.path.join(tmp, 'stale.html'), 'w', encoding='utf-8') as f: f.write(page('Stale evidence', '<h1>T</h1><p>x</p>'))
            publish_page.build()
            h = open(os.path.join(tmp, 'stale_artifact.html'), encoding='utf-8').read()
            self.assertTrue(h.startswith('<title>')); self.assertNotIn('<html', h); self.assertNotIn('index.html', h)
            self.assertIn(':root:not([data-theme="light"])', h); self.assertIn(':root[data-theme="dark"]', h)
            self.assertIn('Snapshot built', h)
        finally:
            publish_page.SITE = old; shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
