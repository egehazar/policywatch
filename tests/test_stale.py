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
        self.assertIn('<ins>A &lt;b&gt; &amp; &quot;c&quot; passage.</ins>', h); self.assertNotIn('A <b>', h)          # the clear / close label has its own <b>
        s = {'n_pieces': 2, 'top': [{'piece': 0, 'score': .8, 'text': 'Plain.'}]}
        self.assertNotIn('Suggested quote', report.suggestion(s, 'bm25', None))


class TestClearLabel(unittest.TestCase):
    """The clear / close label: kev only, after LABEL ADOPTED; cascade suggestions say the check came after the test."""
    def s(self, a, b, **kw):
        return {'n_pieces': 9, 'top': [{'piece': 0, 'score': a, 'text': 'x'}, {'piece': 1, 'score': b, 'text': 'y'}], **kw}

    def test_label(self):
        from unittest import mock
        with mock.patch.object(report, 'label_adopted', return_value=True):
            full = report.confidence(self.s(.9, .6), 'kev')                    # a lead of exactly .30 is clear
            self.assertIn('Clear:', full); self.assertNotIn('after the test', full)
            self.assertIn('Close:', report.confidence(self.s(.9, .61), 'kev'))
            casc = report.confidence(self.s(.95, .2, cascade='rerank top 10'), 'kev')
            self.assertIn('Clear:', casc); self.assertIn('checked after the test', casc)
            card = report.suggestion(self.s(.95, .2, cascade='rerank top 10'), 'kev')
            self.assertIn('among the reranker', card); self.assertIn('1. passage 1', card)
            self.assertNotIn('among the reranker', report.suggestion(self.s(.95, .2), 'kev'))
            self.assertEqual(report.confidence(self.s(.9, .1), 'bm25'), '')
        with mock.patch.object(report, 'label_adopted', return_value=False):
            self.assertEqual(report.confidence(self.s(.9, .1), 'kev'), '')


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


class TestPartDEval(unittest.TestCase):
    """stale.relocate_d.evaluate on synthetic scores: readings, the cascade's share, and the archive check."""
    def setUp(self):
        import subprocess, random
        from stale import relocate_d
        from stale.relocate import psha
        self.D = relocate_d
        self.tmp = tempfile.mkdtemp(); arch = os.path.join(self.tmp, 'contrib-versions'); os.makedirs(arch)
        g = lambda *a: subprocess.run(['git', '-C', arch, *a], capture_output=True, encoding='utf-8')
        g('init', '-q'); g('config', 'user.email', 't@t'); g('config', 'user.name', 't')
        open(os.path.join(arch, 'f.md'), 'w').write('x'); g('add', '-A'); g('commit', '-q', '-m', 'c')
        self.g, head = g, g('rev-parse', 'HEAD').stdout.strip()
        rng = random.Random(3); docs, K, B = [], {}, {'BGE': {}, 'BM25': {}, 'RERANK': {}, 'pieces_sha': {}, 'rerank_sec': 1.0, 'rerank_truncated': 0}
        for sv in range(12):
            P = [f'piece {sv} {i}' for i in range(30)]; qs = [f'q{sv}a', f'q{sv}b']; gold = {qs[0]: [rng.randrange(30)], qs[1]: [rng.randrange(30)]}
            d = {'doc': f'S{sv}/T.md', 'service': 1000 + sv, 'pieces': P, 'questions': qs, 'cases': qs,
                 'items': [{'point': sv * 10 + k, 'question': q, 'gold': gold[q]} for k, q in enumerate(qs)]}
            docs.append(d); B['pieces_sha'][d['doc']] = psha(P)
            # Kev: right everywhere; reranker: gold in its top 10 (so the cascade keeps it); BM25/BGE: random
            K[d['doc']] = {'pieces_sha': psha(P), 'sec': 30.0, 'scores': [{q: (.95 if i in gold[q] else rng.random() * .5) for q in qs} for i in range(30)]}
            B['RERANK'][d['doc']] = {q: [(5.0 if i in gold[q] else rng.random() + (1 if i < 12 else 0)) for i in range(30)] for q in qs}
            for a in ('BM25', 'BGE'): B[a][d['doc']] = {q: [rng.random() for _ in range(30)] for q in qs}
        self.old = (relocate_d.DOCS, relocate_d.F, relocate_d.OUT, wide.DATA_ROOT)
        relocate_d.DOCS = os.path.join(self.tmp, 'docs.json'); relocate_d.F = {a: os.path.join(self.tmp, f'{a}.json') for a in ('kev', 'base')}
        relocate_d.OUT = self.tmp; wide.DATA_ROOT = self.tmp
        json.dump({'archive_head': head, 'order': [], 'docs': docs}, open(relocate_d.DOCS, 'w'))
        json.dump(K, open(relocate_d.F['kev'], 'w')); json.dump(B, open(relocate_d.F['base'], 'w'))

    def tearDown(self):
        self.D.DOCS, self.D.F, self.D.OUT, wide.DATA_ROOT = self.old; shutil.rmtree(self.tmp, ignore_errors=True)

    def test_readings_and_cascade(self):
        self.D.evaluate()
        R = json.load(open(os.path.join(self.tmp, 'contrib_result.json')))['result']
        self.assertEqual(R['hit_at']['KEV']['1'], 1.0)
        self.assertEqual(R['reading']['D0_replication'], 'REPLICATED')
        self.assertEqual(R['reading']['D1_cascade'], 'CASCADE ADOPTED')          # the gold piece is always in the top 10
        self.assertEqual(R['reading']['D2_reranker'], 'NO DIFFERENCE SHOWN')    # the reranker ranks gold first too
        self.assertAlmostEqual(R['cost']['cascade_kev_share'], 10 / 30, places=2)
        self.assertEqual(R['services'], 12)

    def test_refuses_a_moved_archive(self):
        open(os.path.join(self.tmp, 'contrib-versions', 'f.md'), 'w').write('y')
        self.g('commit', '-qam', 'moved')
        with self.assertRaises(AssertionError): self.D.evaluate()


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



class TestDailyDigest(unittest.TestCase):
    def test_suggestions_only_on_stale_events_and_section_anchors(self):
        from stale import daily
        tmp = tempfile.mkdtemp(); old = daily.OUT; daily.OUT = tmp
        ev = lambda kind, pid, st: {'kind': kind, 'before': 'present', 'platform': 'Pinterest', 'case_title': f'Case {pid}',
                                    'classification': 'bad', 'point': pid, 'status': st}
        run = {'run_at': '2026-11-15T01:22:41Z', 'compared_with': 'the previous run', 'archive': {'head': 'ab', 'fetched': True, 'new_commits': 1},
               'tosdr_point_fetches': 0, 'tosdr_failed': [], 'counts': {'gone': 1}, 'events_by_kind': {'new drop': 1, 'recovered': 1},
               'events': [ev('new drop', 1, 'gone'), ev('recovered', 2, 'present')]}
        top = lambda pid: {'point': pid, 'n_pieces': 5, 'top': [{'piece': 2, 'score': 3.1, 'text': f'Passage for {pid}.'}]}
        try:
            daily.digest([run], 'https://example.org/repo', sug={1: top(1), 2: top(2)}, prop={}, arm='bm25')
            h = open(os.path.join(tmp, 'digest.html'), encoding='utf-8').read()
            self.assertEqual(h.count('Where the case may be stated now'), 1)
            self.assertIn('Passage for 1.', h); self.assertNotIn('Passage for 2.', h)
            daily.digest([run], 'https://example.org/repo')          # without suggestions: the page as before
            self.assertNotIn('Where the case may be', open(os.path.join(tmp, 'digest.html'), encoding='utf-8').read())
        finally:
            daily.OUT = old; shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(report.sid('Proton Mail'), 'proton-mail'); self.assertEqual(report.sid('???'), 'x')



class TestDropAudit(unittest.TestCase):
    def test_plain_window_wilson(self):
        from stale import drop_audit as A
        self.assertEqual(A.plain('li>\n<li>Information you <b>shared</b> stays.\n</p>\n<'), 'Information you shared stays.')
        ps = ['Intro.', 'We sell data to brokers for profit.', 'x' * 2000]
        i, share = A.best(ps, 'We sell data to brokers')
        self.assertEqual(i, 1); self.assertEqual(share, 1.0)
        self.assertEqual(A.window(ps, 1, 'We sell'), 'Intro.\n\nWe sell data to brokers for profit.')   # the long neighbour stays out
        self.assertLessEqual(len(A.window(ps, 2, '')), A.CAP + 6)
        lo, hi = A.wilson(27, 30); self.assertAlmostEqual(lo, .744, places=3); self.assertAlmostEqual(hi, .965, places=3)
        self.assertEqual(A.wilson(0, 0), [None, None])

    def test_draw_is_fixed_and_blind(self):
        from stale import drop_audit as A
        if not os.path.exists(os.path.join(ROOT, 'stale', 'wide', 'contrib', 'out', 'points.jsonl')): self.skipTest('no contrib run')
        c1, n1 = A.draw(); c2, _ = A.draw()
        self.assertEqual([(k, r['point']) for k, r in c1], [(k, r['point']) for k, r in c2])
        self.assertEqual(sorted(k for k, _ in c1).count('L'), 30)


class TestStatesCase(unittest.TestCase):
    def test_top_breaks_ties_to_the_earliest_passage(self):
        from stale.states_case import top
        self.assertEqual(top([.2, .9, .9, .1]), 1); self.assertEqual(top([0, 0, 0]), 0)

    def test_rows_reuse_one_verdict_per_shared_passage(self):
        from stale.states_case_ext import rows_of, summary
        K = {'cards': {'T1': {'part': 'A', 'point': 1, 'piece': 3, 'arms': ['KEV', 'RERANK']},
                       'T2': {'part': 'A', 'point': 1, 'piece': 5, 'arms': ['BM25']},
                       'T3': {'part': 'A', 'point': 1, 'piece': 7, 'arms': ['RANDOM']},
                       'T4': {'part': 'B', 'point': 2, 'piece': 0, 'arms': ['KEV', 'RERANK', 'BM25']}},
             'points': [{'part': 'A', 'point': 1, 'doc': 'd1', 'tops': {'KEV': 3, 'RERANK': 3, 'BM25': 5}, 'hit1': {'KEV': 1, 'RERANK': 1, 'BM25': 0}},
                        {'part': 'B', 'point': 2, 'doc': 'd2', 'tops': {'KEV': 0, 'RERANK': 0, 'BM25': 0}, 'hit1': {'KEV': 0, 'RERANK': 0, 'BM25': 0}}]}
        V = {'T1': {'verdict': 'YES'}, 'T2': {'verdict': 'PARTLY'}, 'T3': {'verdict': 'YES'}, 'T4': {'verdict': 'NO'}}
        rows = rows_of(K, V)
        self.assertEqual([r['KEV']['yes'] for r in rows], [1, 0]); self.assertEqual(rows[0]['BM25'], {'yes': 0, 'yes_or_partly': 1, 'hit1': 0})
        s = summary(rows)
        self.assertEqual(s['states_at1'], {'KEV': .5, 'RERANK': .5, 'BM25': 0.0}); self.assertEqual(s['KEV_minus_BM25']['point'], .5)


class TestCostCurve(unittest.TestCase):
    """bench.cost_curve.result on synthetic timings: Kev = 6 + 1 s per question; instruct 6 s per question."""
    def test_result(self):
        from bench import cost_curve as C
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        F0 = C.F; C.F = {k: os.path.join(tmp, k) for k in F0}; self.addCleanup(setattr, C, 'F', F0)
        with open(C.F['kev.jsonl'], 'w') as f, open(C.F['qwen.jsonl'], 'w') as g:
            for n, q in enumerate(C.LEVELS * 2):
                f.write(json.dumps({'key': f'c{n}', 'q': q, 'chars': 1400, 'sec': 6 + q}) + '\n')
                for k in range(q):
                    g.write(json.dumps({'key': f'c{n}|{k}', 'item': f'c{n}', 'k': k, 'q': q, 'chars': 1400, 'sec': 6.0, 'lo': 0}) + '\n')
        C.result(); R = json.load(open(C.F['result.json']))
        self.assertEqual(R['kev_fit'], {'s_per_passage': 6.0, 's_per_question': 1.0})
        self.assertEqual(R['qwen_later_over_first'], 1.0); self.assertEqual(R['ceiling_ratio'], 6.0)
        self.assertEqual(R['break_even_questions'], 1.2)                          # 6 / (6 - 1)
        self.assertEqual(R['levels']['4']['qwen_over_kev'] if '4' in R['levels'] else R['levels'][4]['qwen_over_kev'], 2.4)


class TestRecrawl(unittest.TestCase):
    """stale.recrawl: listed points only, grouped by ToS;DR document, split by what the stored copy holds."""
    def test_rows(self):
        from unittest import mock
        from stale import recrawl
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        P = lambda pt, doc, q, kind='platform edit', ver='2020-01-01': {
            'point': pt, 'platform': 'S' + str(doc), 'doc': f'S{doc}/Terms.md', 'drop_kind': kind, 'dropped': '2024-05-0' + str(pt % 9 + 1),
            'phoenix_doc': doc, 'phoenix_doc_updated_at': '2021-01-01', 'quote_in_phoenix': q, 'phoenix_closest_version': ver}
        f = os.path.join(tmp, 'p.jsonl')
        with open(f, 'w', encoding='utf-8') as fh:
            for r in (P(1, 7, 1.0), P(2, 7, .8), P(3, 7, .2), P(4, 9, .95, ver='2019-01-01'), P(5, 9, None), P(6, 7, 1.0, 'archive change'),
                      P(8, 5, .9, ver='2022-01-01'), P(9, 5, .9, ver='2022-01-01')):
                fh.write(json.dumps(r) + '\n')
        with mock.patch.object(recrawl, 'sources', return_value=[('c', f)]):
            R = recrawl.rows()
        self.assertEqual([r['tosdr_document_id'] for r in R], [7, 5, 9])        # 2 break, then 2 vs 1
        a = R[0]; self.assertEqual((a['points_break_on_recrawl'], a['points_already_lost'], a['point_ids']), (2, 1, '1 2 3'))
        self.assertEqual((R[2]['points_break_on_recrawl'], R[2]['points_no_stored_text']), (1, 1))


class TestMissing(unittest.TestCase):
    """stale.missing (the missing points pilot): the tie rules, the interval and the fixed readings of score()."""
    def test_ties_and_interval(self):
        from stale import missing as M
        self.assertEqual(M.best([{'a': .2}, {'a': .7}, {'a': .7}], 'a'), (.7, 1))          # ties go to the earliest piece
        self.assertEqual(M.auroc([.5, .9], [.5, .1]), .875)                                 # a tie counts half
        self.assertEqual(M.reading([.01, .2], 'b', 'w', 'n'), 'b'); self.assertEqual(M.reading([-.2, -.01], 'b', 'w', 'n'), 'w')
        self.assertEqual(M.reading([0.0, .2], 'b', 'w', 'n'), 'n')                          # a bound at 0 is not shown
        self.assertEqual(M.wilson(14, 40), [0.221, 0.505]); self.assertEqual(M.wilson(12, 40)[0], 0.181)

    def run_score(self, yes, rnd_yes, vs_rerank='KEV better', vs_bm25='KEV better'):
        from stale import missing as M
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        for k, v in (('KEY', os.path.join(tmp, 'key.json')), ('AUD', tmp), ('OUT', tmp)):
            self.addCleanup(setattr, M, k, getattr(M, k)); setattr(M, k, v)
        K, V = {}, {}
        for arm, n, y in [(a, 40, yes[a]) for a in M.ARMS] + [('RANDOM', 10, rnd_yes)]:
            for i in range(n):
                cid = f'{arm}{i:02d}'; K[cid] = {'doc': 'd', 'case': cid, 'piece': 0, 'arms': [arm]}
                V[cid] = {'verdict': 'YES' if i < y else 'PARTLY' if i == y else 'NO', 'why': ''}
        json.dump(K, open(M.KEY, 'w')); json.dump(V, open(os.path.join(tmp, 'verdicts.json'), 'w'))
        json.dump({'auroc': {}, 'recall_at_20': {}, 'KEV_minus_RERANK_auroc': {'reading': vs_rerank},
                   'KEV_minus_BM25_auroc': {'reading': vs_bm25}}, open(os.path.join(tmp, 'missing_measures.json'), 'w'))
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()): M.score()
        return json.load(open(os.path.join(tmp, 'missing_result.json')))

    def test_readings(self):
        r = self.run_score({'KEV': 14, 'RERANK': 10, 'BM25': 5}, 1)
        self.assertEqual((r['reading'], r['method']), ('WORTH BUILDING', 'Kev'))
        self.assertEqual(r['precision_at_10']['KEV']['yes_or_partly_share'], .375)
        self.assertEqual(self.run_score({'KEV': 14, 'RERANK': 10, 'BM25': 5}, 3)['reading'], 'NOT VALID (random controls)')
        r = self.run_score({'KEV': 12, 'RERANK': 10, 'BM25': 5}, 2, vs_rerank='no difference shown')   # .30 exactly passes
        self.assertEqual((r['reading'], r['method']), ('WORTH BUILDING', 'the reranker (Kev ahead not shown)'))
        self.assertEqual(self.run_score({'KEV': 11, 'RERANK': 10, 'BM25': 5}, 0)['reading'], 'NOT WORTH BUILDING AS IS')
        self.assertEqual(self.run_score({'KEV': 20, 'RERANK': 10, 'BM25': 5}, 0, vs_bm25='no difference shown')['reading'],
                         'NOT WORTH BUILDING AS IS')
        self.assertEqual(self.run_score({'KEV': 10, 'RERANK': 12, 'BM25': 5}, 0)['method'], 'the reranker (Kev ahead not shown)')

    def test_report_keeps_the_prose(self):
        from stale import missing_report as R
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        r = self.run_score({'KEV': 14, 'RERANK': 10, 'BM25': 5}, 1)
        json.dump(r, open(os.path.join(tmp, 'missing_result.json'), 'w'))
        dest = os.path.join(tmp, 'RESULT.md'); import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            R.build(out=tmp, dest=dest)
            with open(dest, 'a', encoding='utf-8') as f: f.write('Hand-written reading.\n')
            R.build(out=tmp, dest=dest)
        s = open(dest, encoding='utf-8').read()
        self.assertIn('**Pilot: WORTH BUILDING.**', s); self.assertEqual(s.count(R.MARK), 1)
        self.assertTrue(s.endswith(R.MARK + '\n\nHand-written reading.\n'))



class TestMissing2(unittest.TestCase):
    """stale.missing2: the reranker shortlist and the cascade arms' case scores on the same pieces."""
    def test_shortlist_and_cascade(self):
        from stale import missing2 as M
        rr = [{'a': .1}, {'a': .9}, {'a': .5}, {'a': .9}, {'a': .2}]
        self.assertEqual(M.shortlist(rr, 'a'), [1, 2, 3])                    # top 3 by score, ties to the earliest
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        F0 = M.F; M.F = {k: os.path.join(tmp, k + '.json') for k in F0}; self.addCleanup(setattr, M, 'F', F0)
        D = [{'doc': 'd', 'cases': ['a'], 'positives': ['a'], 'negatives': []}]
        json.dump({'d': rr}, open(M.F['RERANK'], 'w'))
        json.dump({'d': [{'a': .99}, {'a': .2}, {'a': .7}, {'a': .7}, {'a': .1}]}, open(M.F['KEV'], 'w'))   # piece 0 is not shortlisted
        json.dump({'d': [{'a': 0}] * 5}, open(M.F['BM25'], 'w'))
        json.dump({'d': {'1': {'a': -2.0}, '2': {'a': 3.0}, '3': {'a': 3.0}}}, open(M.F['QWEN'], 'w'))
        cs = M.case_scores(D)
        self.assertEqual(cs['KEV']['d']['a'], (.99, 0))                      # the full arm sees every piece
        self.assertEqual(cs['CASCADE_KEV']['d']['a'], (.7, 2))               # only the shortlist; tie to the earliest
        self.assertEqual(cs['CASCADE_QWEN']['d']['a'], (3.0, 2))

    def test_report_keeps_the_prose(self):
        from stale import missing2 as M, missing2_report as R
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        diff = lambda r: {'point': .05, 'ci95': [.01, .09], 'reading': r}
        row = {'doc': 'P/Terms.md', 'positives': 12, 'negatives': 40, **{f'{a}_{m}': .7 for a in M.ARMS for m in ('auroc', 'recall20')}}
        meas = {'docs': [row], 'auroc': {a: .7 for a in M.ARMS}, 'recall_at_20': {a: .4 for a in M.ARMS},
                'KEV_minus_RERANK_auroc': diff('KEV better'), 'KEV_minus_BM25_auroc': diff('KEV better'),
                'CASCADE_KEV_minus_CASCADE_QWEN_auroc': diff('no difference shown'),
                'cards': {'total': 30, 'random': 2, 'per_arm': {a: 10 for a in M.CARD_ARMS}},
                'timing': {'KEV': {'P/Terms.md': {'seconds': 100.0, 'pieces': 10, 'questions': 5, 'asked_cells': 50, 'cached_cells': 0}},
                           'RERANK': {'P/Terms.md': 20.0}, 'QWEN': {'P/Terms.md': {'seconds': 60.0, 'cells': 10, 'pieces': 4, 'no_yes_no': 0}}}}
        prec = {a: {'cards': 10, 'yes': 4, 'yes_share': .4, 'wilson95': [.17, .69], 'yes_or_partly_share': .6} for a in M.CARD_ARMS}
        res = {'random_yes': 0, 'random_n': 2, 'valid': True, 'precision_at_10': prec,
               'precision_diff': {'KEV_minus_RERANK': {'point': 0, 'ci95': [-.1, .1]}, 'CASCADE_KEV_minus_CASCADE_QWEN': {'point': 0, 'ci95': [-.1, .1]}},
               'reading_replication': 'REPLICATED', 'reading_reranker': 'KEV better', 'reading_base_family': 'no difference shown',
               'measures': {k: meas[k] for k in ('auroc', 'recall_at_20', 'KEV_minus_RERANK_auroc', 'KEV_minus_BM25_auroc', 'CASCADE_KEV_minus_CASCADE_QWEN_auroc')}}
        json.dump(meas, open(os.path.join(tmp, 'missing2_measures.json'), 'w')); json.dump(res, open(os.path.join(tmp, 'missing2_result.json'), 'w'))
        dest = os.path.join(tmp, 'RESULT.md'); import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            R.build(out=tmp, dest=dest)
            with open(dest, 'a', encoding='utf-8') as f: f.write('Hand-written reading.\n')
            R.build(out=tmp, dest=dest)
        s = open(dest, encoding='utf-8').read()
        self.assertIn('**Replication: REPLICATED.**', s); self.assertIn('6.00 s per cell measured here', s)
        self.assertEqual(s.count(R.MARK), 1); self.assertTrue(s.endswith(R.MARK + '\n\nHand-written reading.\n'))


class TestMissingWide(unittest.TestCase):
    def test_report_reads_the_check_against_the_plan(self):
        from stale import missing_wide_report as R
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp)
        docs = {'docs': [{'doc': 'P/Privacy Policy.md', 'type': 'privacy', 'pieces': ['a', 'b'], 'positives': ['x'] * 12,
                          'excluded': ['e'], 'negatives': ['n%d' % i for i in range(14)], 'cases': ['x', 'n']}]}
        meas = {'docs': [{'doc': 'P/Privacy Policy.md', 'positives': 12, 'negatives': 14, 'CASCADE_KEV_auroc': .8, 'RERANK_auroc': .6}],
                'auroc': {'CASCADE_KEV': .8, 'RERANK': .6},
                'CASCADE_KEV_minus_RERANK_auroc': {'point': .2, 'ci95': [.1, .3], 'reading': 'CASCADE_KEV better'},
                'timing': {'KEV': {'P/Privacy Policy.md': {'seconds': 20.0, 'pieces': 2, 'cells': 6, 'asked_cells': 5, 'cached_cells': 1}},
                           'RERANK': {'P/Privacy Policy.md': 4.0}}}
        json.dump(docs, open(os.path.join(tmp, 'missing_wide_docs.json'), 'w')); json.dump(meas, open(os.path.join(tmp, 'missing_wide_measures.json'), 'w'))
        dest = os.path.join(tmp, 'RESULT.md')
        R.build(out=tmp, dest=dest)
        with open(dest, 'a', encoding='utf-8') as f: f.write('Hand-written reading.\n')
        R.build(out=tmp, dest=dest); s = open(dest, encoding='utf-8').read()
        self.assertIn('**CASCADE_KEV better**', s); self.assertIn('**0.800**, predicted .66-.76: above the range', s)
        self.assertIn('**0.600**, predicted .58-.68: inside the range', s); self.assertIn('4.00 s per asked cell', s)
        self.assertIn('10 suggestions', s); self.assertTrue(s.endswith(R.MARK + '\n\nHand-written reading.\n'))


class TestMissingWatch(unittest.TestCase):
    """A changed document is found from the archive's HEAD, re-scored reusing the reranker scores of unchanged passages,
    Kev asked only on the shortlist, and skipped on the next run unless its text changes again."""

    def test_check_rerank_kev(self):
        import subprocess
        from stale import missing_watch as W
        from policywatch.scorer import qid
        tmp = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, tmp, True); arch = os.path.join(tmp, 'arch'); os.makedirs(os.path.join(arch, 'P'))
        g = lambda *a: subprocess.run(['git', '-C', arch, *a], capture_output=True, check=True)
        g('init', '-q'); g('config', 'user.email', 't@t'); g('config', 'user.name', 't')
        open(os.path.join(arch, 'P', 'Terms.md'), 'w', encoding='utf-8').write('Old words. ' * 80 + '\n\n' + 'Kept words here. ' * 60 + '\n')
        open(os.path.join(arch, 'P', 'Same.md'), 'w', encoding='utf-8').write('Unchanged text.\n')
        g('add', '.'); g('commit', '-qm', 'v1')
        old = {'Terms': W.current_pieces(arch, 'P/Terms.md'), 'Same': W.current_pieces(arch, 'P/Same.md')}
        open(os.path.join(arch, 'P', 'Terms.md'), 'w', encoding='utf-8').write('Data words. ' * 80 + '\n\n' + 'Kept words here. ' * 60 + '\n')
        g('add', '.'); g('commit', '-qm', 'v2')
        cases = ['data case', 'other case']
        doc = lambda n: {'doc': f'P/{n}.md', 'type': 'terms', 'pieces': old[n], 'positives': [], 'excluded': [], 'negatives': cases, 'cases': cases}
        src = os.path.join(tmp, 'docs.json'); json.dump({'docs': [doc('Terms'), doc('Same')]}, open(src, 'w'))
        json.dump({'P/Terms.md': [{c: 1.0 for c in cases} for _ in old['Terms']]}, open(os.path.join(tmp, 'rr_old.json'), 'w'))
        saved = (W.DOCS, W.F, W.SOURCES, W.OUT)
        self.addCleanup(lambda: setattr(W, 'DOCS', saved[0]) or setattr(W, 'F', saved[1]) or setattr(W, 'SOURCES', saved[2]) or setattr(W, 'OUT', saved[3]))
        W.DOCS = os.path.join(tmp, 'w_docs.json'); W.F = {a: os.path.join(tmp, f'w_{a}.json') for a in ('KEV', 'RERANK')}
        W.SOURCES = ((src, 'rr_old.json', True),); W.OUT = tmp
        import contextlib, io

        class Model:
            calls = 0
            def predict(self, pairs, batch_size=16):
                Model.calls += 1; return [.9 if 'data' in c and 'data' in p else .1 for c, p in pairs]

        class Scorer:
            asked = hits = 0
            def score(self, piece, qs):
                Scorer.asked += len(qs); return {qid(q): .8 for q in qs}
        with contextlib.redirect_stdout(io.StringIO()):
            W.check(arch)
            D = json.load(open(W.DOCS, encoding='utf-8'))['docs']
            self.assertEqual([d['doc'] for d in D], ['P/Terms.md']); self.assertTrue(D[0]['rated'])
            self.assertEqual(len(D[0]['pieces']), 2); self.assertEqual(D[0]['pieces'][1], old['Terms'][1])
            W.rerank(Model()); self.assertEqual(Model.calls, 1)       # only the new paragraph; the kept one reused
            W.kev(scorer=Scorer())
            R, K = json.load(open(W.F['RERANK'])), json.load(open(W.F['KEV']))
            self.assertEqual(len(R['P/Terms.md']), len(D[0]['pieces'])); self.assertEqual(Scorer.asked, 2 * min(3, len(D[0]['pieces'])))
            self.assertIn('P/Terms.md', W.current('KEV')); self.assertEqual(W.current('BM25'), {})
            W.rerank(Model()); W.kev(scorer=Scorer())                 # nothing changed: nothing re-run
        self.assertEqual(Model.calls, 1); self.assertEqual(Scorer.asked, 2 * min(3, len(D[0]['pieces'])))


if __name__ == '__main__':
    unittest.main()
