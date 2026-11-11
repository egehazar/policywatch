"""Read document updates from an Open Terms Archive versions repository (a git clone, e.g. pga-versions).

An update is a commit whose subject starts "Record new changes": the service changed its text (as opposed to a
change in OTA's extraction, recorded as "Apply technical or declaration upgrade" and the like).
"""
import hashlib, os, subprocess
from dataclasses import dataclass

DEFAULT_DOCS = ('Terms of Service', 'Privacy Policy')


@dataclass
class Update:
    platform: str
    doc: str
    path: str
    commit: str
    date: str

    @property
    def key(self):
        return f"{self.date}_{self.platform}_{self.doc.replace(' ', '-')}_{self.commit[:8]}"


def git(archive, *args):
    r = subprocess.run(['git', '-C', archive, *args], capture_output=True, encoding='utf-8', errors='replace')
    return r.stdout


def remote_url(archive):
    u = git(archive, 'remote', 'get-url', 'origin').strip()
    return u[:-4] if u.endswith('.git') else u


def updates(archive, docs=DEFAULT_DOCS, since=None, until=None, platforms=None):
    out = []
    for plat in sorted(os.listdir(archive)):
        if plat.startswith('.') or not os.path.isdir(os.path.join(archive, plat)): continue
        if platforms and plat not in platforms: continue
        for doc in docs:
            path = f'{plat}/{doc}.md'
            if not os.path.exists(os.path.join(archive, path)): continue
            # Date filtering is done here, NOT with git's --since/--until: this history is not in date order, and
            # git stops walking at the first old-enough commits, silently dropping later-dated ones (WhatsApp's
            # 2026-03-27 privacy change vanished from a --since=2026-03-17 query).
            for line in git(archive, 'log', '--format=%H%x09%ad%x09%s', '--date=short', '--', path).splitlines():
                h, date, subj = line.split('\t', 2)
                if since and date < since: continue
                if until and date > until: continue
                if subj.startswith('Record new changes'): out.append(Update(plat, doc, path, h, date))
    return sorted(out, key=lambda u: (u.date, u.platform, u.doc), reverse=True)


def texts(archive, u):
    return git(archive, 'show', f'{u.commit}^:{u.path}'), git(archive, 'show', f'{u.commit}:{u.path}')


def norm_hash(text):
    from .diffing import paras
    return hashlib.sha256('\n'.join(paras(text)).encode('utf-8')).hexdigest()


class History:
    """Every recorded version of one file, for telling capture noise from real edits.

    revert:  the new text (normalized) equals a version older than the parent. In practice this is a crawler
             alternating between two captures of one page (e.g. Reddit's privacy policy, cut off at a table every
             other capture), though a platform can also roll a change back.
    partial: one side is much shorter (< 90% of the paragraphs) and, apart from at most its last 2 paragraphs, is
             exactly the start of the longer side: a capture cut off part-way, not an edit. (A looser "its paragraphs
             all occur in the other side" rule also caught X adding its new terms above the old ones, a real change.)
    """
    LOOKBACK = 60

    def __init__(self, archive, path):
        self.archive, self.path = archive, path
        rows = git(archive, 'log', '--format=%H%x09%ad', '--date=short', '--', path).splitlines()
        self.commits = [tuple(r.split('\t')) for r in rows][::-1]     # oldest first
        self.pos = {h: i for i, (h, _) in enumerate(self.commits)}
        self._h = {}

    def hash_at(self, h):
        if h not in self._h: self._h[h] = norm_hash(git(self.archive, 'show', f'{h}:{self.path}'))
        return self._h[h]

    def classify(self, commit, old_text, new_text):
        from .diffing import paras
        O, N = paras(old_text), paras(new_text)
        short, long_ = (O, N) if len(O) < len(N) else (N, O)
        if len(short) > 2 and len(short) < .9 * len(long_) and any(short[:len(short) - k] == long_[:len(short) - k] for k in (0, 1, 2)):
            return {'noise': 'partial', 'short_side': 'old' if short is O else 'new', 'n_old': len(O), 'n_new': len(N)}
        i = self.pos.get(commit)
        if i is None or i < 2: return None
        hn, hp = norm_hash(new_text), norm_hash(old_text)
        if hn == hp: return None
        for h, d in reversed(self.commits[max(0, i - 1 - self.LOOKBACK):i - 1]):
            if self.hash_at(h) == hn: return {'noise': 'revert', 'same_as': d, 'same_as_commit': h}
        return None
