"""The one-page summary (out/site/ledger.html, published privately): the template plus two charts drawn to scale.
Usage  py stale/ledger/build.py
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
arms = [('Kev-4B (decision model)', .625, .725), ('Qwen3.5-4B (its base family)', .600, .733),
        ('bge-reranker-v2-m3', .542, .608), ('BM25 (keywords)', .373, .417)]
X0, X1 = 210, 620
sx = lambda v: X0 + v * (X1 - X0)
dots = []
for k, (name, h, s) in enumerate(arms):
    y = 40 + k * 44
    dots.append(f'<text x="{X0-12}" y="{y+4}" class="lab" text-anchor="end">{name}</text>'
                f'<line x1="{sx(h):.1f}" y1="{y}" x2="{sx(s):.1f}" y2="{y}" class="link"/>'
                f'<circle cx="{sx(h):.1f}" cy="{y}" r="6" class="hit"/><circle cx="{sx(s):.1f}" cy="{y}" r="6" class="states"/>'
                f'<text x="{sx(s)+11:.1f}" y="{y+4}" class="val">{round(s*100)}%</text>'
                f'<text x="{sx(h)-11:.1f}" y="{y+4}" class="val mute" text-anchor="end">{round(h*100)}%</text>')
ticks = ''.join(f'<line x1="{sx(t):.1f}" y1="18" x2="{sx(t):.1f}" y2="196" class="grid"/>'
                f'<text x="{sx(t):.1f}" y="214" class="tick" text-anchor="middle">{int(t*100)}%</text>' for t in (0, .25, .5, .75, 1))
chart1 = f'<svg viewBox="0 0 680 228" role="img" aria-label="Share of 120 points whose top passage is the curator\'s (hollow) and states the case (filled), per method">{ticks}{"".join(dots)}</svg>'

kev = [7.96, 4.54, 3.25, 2.76, 2.45]; qwen = [6.62, 6.59, 6.51, 6.49, 6.55]; rr = 0.98
PX0, PX1, PY0, PY1, YMAX = 70, 640, 24, 236, 8
px = lambda q: PX0 + (q - 1) * (PX1 - PX0) / 4
py = lambda v: PY1 - v / YMAX * (PY1 - PY0)
g = ''.join(f'<line x1="{PX0}" y1="{py(v):.1f}" x2="{PX1}" y2="{py(v):.1f}" class="grid"/><text x="{PX0-10}" y="{py(v)+4:.1f}" class="tick" text-anchor="end">{v} s</text>' for v in (0, 2, 4, 6, 8))
g += ''.join(f'<text x="{px(q):.1f}" y="{PY1+20}" class="tick" text-anchor="middle">{q}</text>' for q in range(1, 6))
line = lambda vals, cls: (f'<polyline points="{" ".join(f"{px(q+1):.1f},{py(v):.1f}" for q, v in enumerate(vals))}" class="{cls}"/>'
                          + ''.join(f'<circle cx="{px(q+1):.1f}" cy="{py(v):.1f}" r="4.5" class="{cls}-dot"/>' for q, v in enumerate(vals)))
c2 = (g + line(qwen, 'qw') + line(kev, 'kv') +
      f'<line x1="{PX0}" y1="{py(rr):.1f}" x2="{PX1}" y2="{py(rr):.1f}" class="rr"/>'
      f'<text x="{PX0+6}" y="{py(rr)-8:.1f}" class="lab small">reranker, 0.98 s (part B average)</text>'
      f'<text x="{px(5)+8:.1f}" y="{py(qwen[-1])-10:.1f}" class="lab small" text-anchor="end">instruct model, re-reads the passage per question</text>'
      f'<text x="{px(5)-4:.1f}" y="{py(kev[-1])+22:.1f}" class="lab small" text-anchor="end">Kev, reads the passage once</text>'
      f'<text x="{(PX0+PX1)/2:.1f}" y="{PY1+40}" class="tick" text-anchor="middle">questions asked of each document</text>')
chart2 = f'<svg viewBox="0 0 680 286" role="img" aria-label="Seconds per passage-question against questions per document, for Kev, the instruct model and the reranker">{c2}</svg>'

page = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
page = page.replace('<!--CHART1-->', chart1).replace('<!--CHART2-->', chart2)
open(os.path.join(HERE, '..', '..', 'out', 'site', 'ledger.html'), 'w', encoding='utf-8').write(page)
print('ok', len(page))
