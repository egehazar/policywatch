"""Turns out/site/stale.html into a single private-artifact page (out/site/stale_artifact.html).

The artifact host wraps the page in its own document skeleton and sets data-theme on the root for an explicit light or
dark choice, so: the skeleton tags are dropped, the dark palette is guarded and repeated for [data-theme="dark"], the
links to the local site's other pages are removed, and long words wrap inside passages.
Usage  py -m stale.publish_page [src page] [dst page] [title]   (default stale.html -> stale_artifact.html)
"""
import datetime, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'out', 'site')


def build(src='stale.html', dst='stale_artifact.html', title='Stale Evidence Finder'):
    h = open(os.path.join(SITE, src), encoding='utf-8').read()
    css = re.search(r'<style>(.*?)</style>', h, re.S).group(1)
    m = re.search(r'@media \(prefers-color-scheme:dark\)\{:root\{(.*?)\}\}', css, re.S)
    assert m, 'dark palette not found'
    dark = m.group(1).rstrip(';') + ';color-scheme:dark'
    css = (css[:m.start()] + '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){' + dark + '}}\n'
           ':root[data-theme="dark"]{' + dark + '}' + css[m.end():])
    css += '\n.diff{overflow-wrap:anywhere}table{display:block;overflow-x:auto}'
    body = re.search(r'<main>(.*)</main>', h, re.S).group(1)
    body = re.sub(r'<nav class="sm">.*?</nav>', '', body, count=1, flags=re.S)
    built = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(SITE, src)), datetime.timezone.utc)
    m2 = re.fullmatch(r'stale_(.+)\.html', src)          # stale_<collection>.html, built by stale/wide.py
    source = f'{m2.group(1)} collection ({m2.group(1)}-versions)' if m2 else 'platform archive (pga-versions)'
    stamp = (f'<p class="sm mut">Snapshot built {built:%Y-%m-%d %H:%M} UTC by policywatch from the Open Terms Archive '
             f'{source} and ToS;DR&rsquo;s public points.</p>')
    body = body.replace('</h1>', '</h1>' + stamp, 1)
    out = os.path.join(SITE, dst)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f'<title>{title}</title><style>{css}</style><main>{body}</main>')
    print(out, os.path.getsize(out), 'bytes')


if __name__ == '__main__':
    build(*sys.argv[1:])
