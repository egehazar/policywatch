"""One update in, one record out: which approved answers probably changed, with the evidence.

For every question in the bank, the decision model scores the OLD changed region and the NEW changed region; the
movement |p_new - p_old| ranks the questions. The model is used as a comparator (the same question on two versions),
never as an oracle: the record holds scores and evidence, and a person decides. Number and date edits are listed
separately by rule, because a 4B model is not trusted to notice "30 days" becoming "14 days".
"""
import json, os
from concurrent.futures import ThreadPoolExecutor
from .diffing import diff
from .scorer import qid

MAX_CHANGED = 80        # more changed paragraphs than this = a wholesale rewrite: review everything, score nothing
REGION_CAP = 8000       # characters per state; a larger side is split at paragraphs (pieces) and the max over pieces is kept
MAX_LOCALIZE_BLOCKS = 12


def load_bank(path):
    with open(path, encoding='utf-8') as f: return json.load(f)


def pieces(text, cap):
    """Split one side's region into states of at most `cap` characters at paragraph boundaries; a text under the
    cap is returned unchanged (byte-identical to the frozen r20 regions). A single paragraph over the cap is cut at
    the cap, so no state can overflow a llama.cpp slot (-c 16384 -np 4 = 4,096 tokens, about 16k characters)."""
    if len(text) <= cap: return [text]
    out, cur = [], ''
    for p in text.split('\n\n'):
        while len(p) > cap:
            if cur: out.append(cur); cur = ''
            out.append(p[:cap]); p = p[cap:]
        if cur and len(cur) + 2 + len(p) > cap: out.append(cur); cur = p
        else: cur = cur + '\n\n' + p if cur else p
    if cur: out.append(cur)
    return out


def side_scores(scorer, regions, questions):
    """max over chunks of p(yes) per question ("does the text state X" holds if any chunk states it)."""
    best = {}
    for text in regions:
        if not text.strip(): ps = {qid(q): 0.0 for q in questions}
        else: ps = scorer.score(text, questions)
        for k, p in ps.items(): best[k] = max(best.get(k, 0.0), p)
    return best


def analyze(u, old_text, new_text, scorer, bank, tau, localize=True, noise=None):
    """noise: archive.History.classify() result; a revert or a partial capture is labelled and not scored."""
    ch = diff(old_text, new_text)
    rec = {'platform': u.platform, 'doc': u.doc, 'path': u.path, 'commit': u.commit, 'date': u.date, 'key': u.key,
           'n_changed': ch.n_changed, 'scorer': scorer.server.id, 'tau': tau,
           'numeric': [{'old': a, 'new': b} for a, b in ch.numeric],
           'links': [{'para': p, 'old': o, 'new': n} for p, o, n in ch.links],
           'blocks': [{'before': b.before, 'old': b.old, 'new': b.new, 'after': b.after} for b in ch.blocks]}
    if ch.n_changed == 0:
        return {**rec, 'kind': 'links' if ch.links else 'formatting', 'questions': []}
    if noise:
        return {**rec, **noise, 'kind': noise['noise'], 'questions': []}
    if ch.n_changed > MAX_CHANGED:
        return {**rec, 'kind': 'rewrite', 'questions': []}
    Q = [b['q'] for b in bank]
    with ThreadPoolExecutor(2) as ex:
        fo = ex.submit(side_scores, scorer, pieces(ch.old_region, REGION_CAP), Q)
        fn = ex.submit(side_scores, scorer, pieces(ch.new_region, REGION_CAP), Q)
        po, pn = fo.result(), fn.result()
    qs = []
    for b in bank:
        k = qid(b['q']); qs.append({'case': b.get('case'), 'title': b.get('title', b['q']), 'classification': b.get('classification'),
                                    'q': b['q'], 'p_old': po[k], 'p_new': pn[k], 'dp': round(abs(pn[k] - po[k]), 4), 'block': None})
    qs.sort(key=lambda x: -x['dp'])
    flagged = [x for x in qs if x['dp'] >= tau]
    if localize and flagged and 1 < len(ch.blocks) <= MAX_LOCALIZE_BLOCKS:
        fq = [x['q'] for x in flagged]
        for x in flagged: x['block_dp'] = []
        for bi, blk in enumerate(ch.blocks):
            o = side_scores(scorer, pieces(blk.old_text, REGION_CAP), fq)
            n = side_scores(scorer, pieces(blk.new_text, REGION_CAP), fq)
            for x in flagged: x['block_dp'].append(round(abs(n[qid(x['q'])] - o[qid(x['q'])]), 4))
        for x in flagged: x['block'] = max(range(len(ch.blocks)), key=lambda i: x['block_dp'][i])
    elif len(ch.blocks) == 1:
        for x in flagged: x['block'] = 0
    return {**rec, 'kind': 'scored', 'n_flagged': len(flagged), 'questions': qs}


def save(rec, out_dir):
    d = os.path.join(out_dir, 'updates'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, rec['key'] + '.json')
    tmp = p + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)      # atomic: a killed run never leaves a truncated record that counts as done
    return p
