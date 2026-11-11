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


def _days(a, b):
    import datetime
    f = lambda s: datetime.date.fromisoformat(s)
    return abs((f(b) - f(a)).days)


def norm_hash(text):
    from .diffing import paras
    return hashlib.sha256('\n'.join(paras(text)).encode('utf-8')).hexdigest()


class History:
    """Every recorded version of one file, for telling capture noise from real edits.

    partial: the NEW capture is much shorter (< 90% of the paragraphs) and, apart from at most its last 2
             paragraphs, is exactly the start of the old one: a capture cut off part-way. Only the new side counts:
             when the OLD side is the short one, the text grew, which is either a real addition (Telegram's DSA clause
             2024-02-18, TikTok appending its US children's policy 2024-04-17) or a recovery from a cut capture,
             which the revert rule or clean_parent() handles. A real deletion of the document's tail would also
             match; the page says "looks cut off" and shows the diff.
    revert:  the new text (normalized) equals one of the RECENT versions before the parent (at most REVERT_VERSIONS
             back and REVERT_DAYS old): a crawler alternating between captures (TikTok's UK-ads banner). Returning to
             an older version is treated as a real change (a rollback), since it cannot be told apart from flapping.
    (Review 11-11 by an independent subagent: the first rules labelled both additions above as noise, and hid
    rollbacks up to 59 captures back.)
    """
    LOOKBACK = 60
    REVERT_VERSIONS = 6
    REVERT_DAYS = 45
    CLEAN_STEPS = 5

    def __init__(self, archive, path):
        self.archive, self.path = archive, path
        rows = git(archive, 'log', '--format=%H%x09%ad', '--date=short', '--', path).splitlines()
        self.commits = [tuple(r.split('\t')) for r in rows][::-1]     # oldest first
        self.pos = {h: i for i, (h, _) in enumerate(self.commits)}
        self._h, self._t = {}, {}

    def text_at(self, h):
        if h not in self._t: self._t[h] = git(self.archive, 'show', f'{h}:{self.path}')
        return self._t[h]

    def hash_at(self, h):
        if h not in self._h: self._h[h] = norm_hash(self.text_at(h))
        return self._h[h]

    @staticmethod
    def cut_off(old_text, new_text):
        """True if the new capture looks like the old one cut off part-way."""
        from .diffing import paras
        O, N = paras(old_text), paras(new_text)
        return 2 < len(N) < .9 * len(O) and any(N[:len(N) - k] == O[:len(N) - k] for k in (0, 1, 2))

    def classify(self, commit, old_text, new_text):
        from .diffing import paras
        if self.cut_off(old_text, new_text):
            return {'noise': 'partial', 'short_side': 'new', 'n_old': len(paras(old_text)), 'n_new': len(paras(new_text))}
        i = self.pos.get(commit)
        if i is None or i < 2: return None
        hn, hp = norm_hash(new_text), norm_hash(old_text)
        if hn == hp: return None
        d0 = self.commits[i][1]
        for h, d in reversed(self.commits[max(0, i - 1 - self.REVERT_VERSIONS):i - 1]):
            if self.hash_at(h) == hn and _days(d, d0) <= self.REVERT_DAYS:
                return {'noise': 'revert', 'same_as': d, 'same_as_commit': h}
        return None

    def clean_parent(self, commit, old_text):
        """The text to diff against: the parent, unless the parent is itself a cut-off capture, in which case the
        last version before the cut (at most CLEAN_STEPS back). Returns (text, commit or None if the parent)."""
        i = self.pos.get(commit)
        if i is None or i < 2: return old_text, None
        j, text, via = i - 1, old_text, None
        for _ in range(self.CLEAN_STEPS):
            if j < 1: break
            prev = self.text_at(self.commits[j - 1][0])
            if not self.cut_off(prev, text): break
            j -= 1; text, via = prev, self.commits[j][0]
        return text, via
