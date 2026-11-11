"""Static HTML report from saved update records: an index, one page per update, and an about page."""
import glob, html, json, os
from .diffing import word_diff

CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#6b6a66;--line:#e4e1da;--card:#fff;--acc:#2d5bd7;--del:#fbe3e1;--delfg:#8a1c12;
--ins:#dff3e4;--insfg:#14532d;--bar:#d9d6cf;--up:#14532d;--down:#8a1c12;--warn:#fff4d6}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe7;--mut:#a3a19b;--line:#2e2d2a;--card:#1e1e1c;--acc:#8fb0ff;
--del:#4a1f1b;--delfg:#ffb4ab;--ins:#173a24;--insfg:#a7e3b9;--bar:#3a3936;--up:#a7e3b9;--down:#ffb4ab;--warn:#3d3420}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}
main{max-width:920px;margin:0 auto;padding:28px 16px 80px}a{color:var(--acc)}h1{font-size:26px;margin:0 0 4px}
h2{font-size:18px;margin:32px 0 10px}.mut{color:var(--mut)}.sm{font-size:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:10px 0}
.row{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}.badge{font-size:12px;border:1px solid var(--line);
border-radius:99px;padding:1px 8px;color:var(--mut)}.badge.good{color:var(--up)}.badge.bad,.badge.blocker{color:var(--down)}
.q{margin:6px 0}.arrow.up{color:var(--up)}.arrow.down{color:var(--down)}
.bar{position:relative;height:8px;background:var(--bar);border-radius:4px;width:160px;display:inline-block;vertical-align:middle}
.bar i{position:absolute;top:-3px;width:3px;height:14px;border-radius:2px}.bar i.o{background:var(--mut)}.bar i.n{background:var(--fg)}
.diff{white-space:pre-wrap;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;font-size:14px}
del{background:var(--del);color:var(--delfg);text-decoration:line-through}ins{background:var(--ins);color:var(--insfg);text-decoration:none}
.ctx{color:var(--mut)}.note{background:var(--warn);border-radius:8px;padding:10px 12px;font-size:14px}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid var(--line);padding:6px 4px;text-align:left}
nav{margin-bottom:18px}nav a{margin-right:14px}
button{font:inherit;font-size:13px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:1px 8px;margin-left:4px;cursor:pointer}
button.on{background:var(--fg);color:var(--bg)}select{font:inherit;max-width:100%;margin:6px 0}
"""


def esc(s):
    return html.escape(str(s))


def page(title, body, key=''):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,'
            f'initial-scale=1"><title>{esc(title)}</title><style>{CSS}</style></head><body data-key="{esc(key)}"><main>'
            f'<nav class="sm"><a href="index.html">Updates</a><a href="about.html">How it works</a></nav>{body}</main></body></html>')


def wdiff(a, b):
    out = []
    for op, t in word_diff(a, b):
        out.append(f'<del>{esc(t)}</del>' if op == '-' else f'<ins>{esc(t)}</ins>' if op == '+' else esc(t))
    return ''.join(out)


def block_html(b):
    ctx = lambda ps: f'<span class="ctx">{esc(chr(10).join(ps))}</span>\n' if ps else ''
    return (f'<div class="diff">{ctx(b["before"])}{wdiff(chr(10).join(b["old"]), chr(10).join(b["new"]))}'
            f'{chr(10) + ctx(b["after"]) if b["after"] else ""}</div>')


def bar(po, pn):
    return f'<span class="bar"><i class="o" style="left:{po * 100:.0f}%"></i><i class="n" style="left:calc({pn * 100:.0f}% - 3px)"></i></span>'


def review_buttons(case):
    return (f'<span class="rv" data-case="{esc(case)}" hidden> · Human check: '
            + ''.join(f'<button data-v="{v}">{t}</button>' for v, t in (('changed', 'changed'), ('not_changed', 'not changed'), ('unsure', 'unsure')))
            + '</span>')


def qline(x):
    up = x['p_new'] > x['p_old']
    cls = x.get('classification') or ''
    return (f'<div class="q"><span class="arrow {"up" if up else "down"}">{"▲" if up else "▼"}</span> <b>{esc(x["title"])}</b> '
            f'{f"<span class=badge {esc(cls)}>{esc(cls)}</span>" if cls else ""}<br>'
            f'<span class="sm mut">{"now stated more clearly" if up else "now stated less clearly"} · '
            f'score {x["p_old"]:.2f} → {x["p_new"]:.2f}</span> {bar(x["p_old"], x["p_new"])}{review_buttons(x["case"])}</div>')


REVIEW_JS = """<script>
const KEY = document.body.dataset.key;
const mark = (el, v) => el.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.v === v));
async function post(body) {
  const r = await fetch('/api/verdict', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});
  if (!r.ok) throw new Error('save failed');
}
(async () => {
  let vs; try { const r = await fetch('/api/verdicts?key=' + encodeURIComponent(KEY)); if (!r.ok) return; vs = await r.json(); } catch (e) { return; }
  document.querySelectorAll('.rv, .missed').forEach(e => e.hidden = false);
  const by = {}; vs.forEach(v => by[String(v.case)] = v.verdict);
  document.querySelectorAll('.rv').forEach(el => {
    mark(el, by[el.dataset.case]);
    el.querySelectorAll('button').forEach(b => b.onclick = async () => {
      try { await post({key: KEY, case: el.dataset.case, verdict: b.dataset.v}); mark(el, b.dataset.v); } catch (e) { b.textContent += ' (not saved)'; }
    });
  });
  const m = document.querySelector('.missed');
  if (m) {
    const list = m.querySelector('.mlist');
    const show = () => { list.textContent = vs.filter(v => v.verdict === 'missed').map(v => '• ' + (m.querySelector(`option[value="${v.case}"]`) || {}).textContent).join('\\n'); };
    show();
    m.querySelector('button').onclick = async () => {
      const c = m.querySelector('select').value; if (!c) return;
      await post({key: KEY, case: c, verdict: 'missed'}); vs.push({case: c, verdict: 'missed'}); show();
    };
  }
})();
</script>"""


def missed_picker(rec, flagged):
    shown = {str(x['case']) for x in flagged}
    opts = ''.join(f'<option value="{esc(x["case"])}">{esc(x["title"])}</option>' for x in rec['questions'] if str(x['case']) not in shown)
    return (f'<div class="missed card" hidden><b>Did an answer change that is not flagged?</b><br><select><option value="">'
            f'Pick the question…</option>{opts}</select> <button>Record as missed</button><pre class="mlist sm"></pre></div>')


def source_link(rec, repo):
    return f'{repo}/commit/{rec["commit"]}' if repo else ''


def update_page(rec, repo):
    head = (f'<h1>{esc(rec["platform"])} · {esc(rec["doc"])}</h1><div class="mut">{esc(rec["date"])} · '
            f'{rec["n_changed"]} changed paragraphs · <a href="{esc(source_link(rec, repo))}">source commit</a></div>')
    body = [head]
    if rec['kind'] == 'rewrite':
        body.append('<p class="note">More than 80 paragraphs changed: treated as a rewrite. Every approved answer '
                    'for this document needs review; nothing was scored.</p>')
    elif rec['kind'] == 'formatting':
        body.append('<p class="note">Only formatting or link targets changed. No answer can have moved.</p>')
    elif rec['kind'] == 'revert':
        body.append(f'<p class="note">The new text is identical to the version recorded on {esc(rec["same_as"])}. Usually '
                    'this is the archive alternating between two captures of one page, not a policy change. Nothing '
                    'was scored.</p>')
    elif rec['kind'] == 'partial':
        side = 'new' if rec['short_side'] == 'new' else 'old'
        body.append(f'<p class="note">The {side} capture looks cut off: it has {rec["n_" + side]} paragraphs against '
                    f'{rec["n_new" if side == "old" else "n_old"]}, and almost all of them occur in the other version. '
                    'This is a capture problem, not a policy change. Nothing was scored.</p>')
    else:
        fl = [x for x in rec['questions'] if x['dp'] >= rec['tau']]
        body.append(f'<h2>Answers that probably changed ({len(fl)})</h2>')
        if not fl: body.append('<p class="mut">None moved past the threshold. Below are the largest movers.</p>')
        for x in fl:
            ev = block_html(rec['blocks'][x['block']]) if x.get('block') is not None else ''
            body.append(f'<div class="card">{qline(x)}{ev}</div>')
        more = [x for x in rec['questions'] if x not in fl][:5]
        if more:
            body.append('<h2>Next largest movements</h2><div class="card">' + ''.join(qline(x) for x in more) + '</div>')
        body.append(missed_picker(rec, fl + more))
    if rec['numeric']:
        body.append(f'<h2>Number and date changes ({len(rec["numeric"])})</h2><p class="sm mut">Listed by rule, not by the model.</p>')
        body += [f'<div class="diff">{wdiff(n["old"], n["new"])}</div>' for n in rec['numeric']]
    if rec['kind'] in ('scored', 'formatting', 'revert') and len(rec['blocks']) <= 40:
        body.append(f'<h2>All changed text ({len(rec["blocks"])} blocks)</h2>')
        body += [block_html(b) for b in rec['blocks']]
    return page(f'{rec["platform"]} {rec["doc"]} {rec["date"]}', ''.join(body) + (REVIEW_JS if rec['kind'] == 'scored' else ''), key=rec['key'])


def human_record(recs, verdicts):
    """Running precision of flags and audited misses from human verdicts (latest verdict per (update, case))."""
    by = {r['key']: r for r in recs}; fl_ok = fl_bad = fl_unsure = missed = 0; updates = set()
    for (key, case), v in verdicts.items():
        r = by.get(key)
        if not r or r['kind'] != 'scored': continue
        updates.add(key)
        q = next((x for x in r['questions'] if str(x['case']) == str(case)), None)
        flagged = q is not None and q['dp'] >= r['tau']
        if v['verdict'] == 'missed' or (v['verdict'] == 'changed' and not flagged): missed += 1
        elif flagged and v['verdict'] == 'changed': fl_ok += 1
        elif flagged and v['verdict'] == 'not_changed': fl_bad += 1
        elif flagged and v['verdict'] == 'unsure': fl_unsure += 1
    return {'updates_reviewed': len(updates), 'flags_confirmed': fl_ok, 'flags_wrong': fl_bad, 'flags_unsure': fl_unsure, 'misses': missed}


def index_page(recs, meta, hr=None):
    rows = []; noise = [r for r in recs if r['kind'] in ('revert', 'partial')]
    for r in [r for r in recs if r['kind'] not in ('revert', 'partial')]:
        if r['kind'] == 'scored':
            fl = [x for x in r['questions'] if x['dp'] >= r['tau']]
            summary = ''.join(f'<div class="sm">{"▲" if x["p_new"] > x["p_old"] else "▼"} {esc(x["title"])}</div>' for x in fl[:3])
            summary += f'<div class="sm mut">+{len(fl) - 3} more</div>' if len(fl) > 3 else ''
            summary = summary or '<div class="sm mut">No answer moved past the threshold.</div>'
        elif r['kind'] == 'rewrite':
            summary = '<div class="sm">Rewrite: review every answer.</div>'
        else:
            summary = '<div class="sm mut">Formatting only.</div>'
        nums = f'<span class="badge">{len(r["numeric"])} number/date</span>' if r['numeric'] else ''
        rows.append(f'<div class="card"><div class="row"><b><a href="{esc(r["key"])}.html">{esc(r["platform"])} · {esc(r["doc"])}</a></b>'
                    f'<span class="mut sm">{esc(r["date"])} · {r["n_changed"]} paragraphs</span>{nums}</div>{summary}</div>')
    head = (f'<h1>What changed in meaning</h1><p class="mut">{len(recs)} recorded updates to platform terms and privacy policies '
            f'({esc(meta.get("range", ""))}). For each update, {meta.get("n_questions", "")} approved yes/no answers are re-asked '
            f'of the old and the new text by a small local decision model; the ones whose score moved are listed first.</p>')
    if hr and hr['updates_reviewed']:
        judged = hr['flags_confirmed'] + hr['flags_wrong']
        unsure = f' ({hr["flags_unsure"]} unsure)' if hr['flags_unsure'] else ''
        head += (f'<div class="card sm"><b>Human check so far:</b> {hr["updates_reviewed"]} updates reviewed · '
                 f'{hr["flags_confirmed"]} of {judged} judged flags confirmed{unsure} · '
                 f'{hr["misses"]} changes the tool missed</div>')
    if noise:
        head += (f'<p class="mut sm">{len(noise)} of the {len(recs)} recorded updates are capture noise (the text returned to '
                 'an earlier version, or a capture was cut off); they are listed at the bottom and not scored.</p>')
        items = ''.join(f'<div class="sm"><a href="{esc(r["key"])}.html">{esc(r["date"])} {esc(r["platform"])} · {esc(r["doc"])}</a> '
                        f'<span class="mut">{"same as " + esc(r["same_as"]) if r["kind"] == "revert" else "cut-off capture"}</span></div>'
                        for r in noise)
        rows.append(f'<h2>Capture noise ({len(noise)})</h2><div class="card">{items}</div>')
    return page('policywatch', head + ''.join(rows))


def memo_html(mc):
    if not mc: return ''
    sm = mc['summary']
    rows = ''.join(f'<tr><td>{esc(r["platform"])} · {esc(r["doc"])}</td><td>{esc(r["memo"])}</td><td>{esc(r["result"])}</td></tr>' for r in mc['rows'])
    return (f'<h2>Does it catch the changes people wrote up?</h2><p>Open Terms Archive publishes memos: short write-ups of '
            f'notable changes by independent contributors. {sm["memos"]} memos concern a terms of service or privacy policy '
            f'recorded in this archive. Before any score existed, each memo was mapped to the questions a correct tool should '
            f'move (eval/memo_targets.json, hashed). A memo is caught when one of those questions is flagged or in the '
            f'update’s top 5.</p><p><b>{sm["caught"]} of {sm["judged"]}</b> judged memos caught; {sm["coverage_gaps"]} '
            f'changes no question in the bank covers; {sm["not_scored"]} not scored (rewrites or not yet scanned).</p>'
            + (lambda v: f'<p class="sm mut">Same check with the original 70-question bank: {v["v1"]["caught"]} of {v["v1"]["judged"]} caught '
               f'({v["v1"]["coverage_gaps"]} gaps). With a second, independent target mapping (Fable 5.2, also made before scoring): '
               f'{v["fable"]["caught"]} of {v["fable"]["judged"]}. Either mapping: {v["union"]["caught"]} of {v["union"]["judged"]}.</p>')(sm.get('variants', {'v1': sm, 'fable': sm, 'union': sm}))
            + f'<table><tr><th>Document</th><th>Memo</th><th>Result</th></tr>{rows}</table>')


def noise_html(recs):
    if not recs: return ''
    nz = sum(r['kind'] in ('revert', 'partial') for r in recs)
    return (f'<h2>Capture noise</h2><p>{nz} of the {len(recs)} recorded updates shown here are not policy changes: the text '
            'returned to an earlier version (for example TikTok’s UK-ads banner appearing and disappearing between captures), '
            'or a capture was cut off part-way (Reddit’s privacy policy, cut at a table about every other capture). Across the '
            'whole archive, 536 of 2,672 recorded changes are of this kind, and 304 of 835 in 2026.</p>')


def about_page(meta, ev, mc=None, recs=()):
    acc = ''
    if ev and ev.get('status') == 'ok':
        acc = '<h2>How accurate it is</h2>' + ev.get('html', '')
    acc += memo_html(mc) + noise_html(recs)
    body = f"""<h1>How it works</h1>
<p>Someone keeps a set of approved answers about a document ("Does this service sell your data?"). When the document
changes, which answers need another look?</p>
<p>The usual cheap rule re-checks every answer whose retrieved source paragraph changed. On real policy updates it
re-reads many answers that did not change and cannot see answers broken by an edit elsewhere in the document.</p>
<p>policywatch reads only the changed paragraphs (plus one paragraph of context on each side), once for the old version
and once for the new, and asks a decision model every question in the bank about each. A decision model answers many
yes/no questions about one text in a single pass and returns a probability for each. The answers whose probability
moved most are listed first; number and date edits are listed by rule. Nothing is decided automatically.</p>
<p class="sm mut">Model: {esc(meta.get('scorer', ''))}, running on a desktop CPU. Questions: {meta.get('n_questions', '')} case
titles from ToS;DR (tosdr.org), phrased as "Does the text state or clearly imply ...". Documents: Open Terms Archive,
{esc(meta.get('repo', ''))} (ODC-BY 1.0). The re-asking mechanic follows jev-why (github.com/Mahad-007/jev-why).
Threshold for "probably changed": |movement| ≥ {meta.get('tau', '')}.</p>{acc}"""
    return page('How policywatch works', body)


def _read(p):
    with open(p, encoding='utf-8') as f: return json.load(f)


def _write(p, text):
    with open(p, 'w', encoding='utf-8') as f: f.write(text)


def build(out_dir, repo='', n_questions=''):
    recs = [_read(p) for p in glob.glob(os.path.join(out_dir, 'updates', '*.json'))]
    recs.sort(key=lambda r: (r['date'], r['platform'], r['doc']), reverse=True)
    site = os.path.join(out_dir, 'site'); os.makedirs(site, exist_ok=True)
    dates = [r['date'] for r in recs]
    meta = {'range': f'{min(dates)} to {max(dates)}' if dates else '', 'n_questions': n_questions, 'repo': repo,
            'scorer': recs[0]['scorer'] if recs else '', 'tau': recs[0]['tau'] if recs else ''}
    for r in recs:
        _write(os.path.join(site, r['key'] + '.html'), update_page(r, repo))
    from .serve import load_verdicts
    hr = human_record(recs, load_verdicts(out_dir))
    _write(os.path.join(site, 'index.html'), index_page(recs, meta, hr))
    _write(os.path.join(out_dir, 'human_record.json'), json.dumps(hr, indent=1))
    evp = os.path.join(out_dir, 'eval.json')
    ev = _read(evp) if os.path.exists(evp) else None
    mcp = os.path.join(out_dir, 'memo_check.json')
    mc = _read(mcp) if os.path.exists(mcp) else None
    _write(os.path.join(site, 'about.html'), about_page(meta, ev, mc, recs))
    return site, len(recs)
