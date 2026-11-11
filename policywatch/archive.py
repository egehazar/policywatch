"""Read document updates from an Open Terms Archive versions repository (a git clone, e.g. pga-versions).

An update is a commit whose subject starts "Record new changes": the service changed its text (as opposed to a
change in OTA's extraction, recorded as "Apply technical or declaration upgrade" and the like).
"""
import os, subprocess
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
            args = ['log', '--format=%H%x09%ad%x09%s', '--date=short']
            if since: args.append(f'--since={since}')
            if until: args.append(f'--until={until}')
            for line in git(archive, *args, '--', path).splitlines():
                h, date, subj = line.split('\t', 2)
                if subj.startswith('Record new changes'): out.append(Update(plat, doc, path, h, date))
    return sorted(out, key=lambda u: (u.date, u.platform, u.doc), reverse=True)


def texts(archive, u):
    return git(archive, 'show', f'{u.commit}^:{u.path}'), git(archive, 'show', f'{u.commit}:{u.path}')
