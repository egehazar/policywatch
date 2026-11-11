"""Paragraph diff of two document versions, and the changed REGION a decision model reads.

Paragraphs are non-empty lines, normalized (markdown link targets dropped, whitespace collapsed), so URL-only edits
vanish. A changed block is a run of non-equal difflib opcodes; its region text is the changed paragraphs plus one
unchanged paragraph on each side. Blocks are joined by SEP. This is byte-for-byte the region of the frozen r20 test
(decision-serving/play/reviewq/rq.py), so scores from that run are valid cache entries here.
"""
import difflib, re
from dataclasses import dataclass, field

SEP = '\n\n[...]\n\n'
LINK = re.compile(r'\]\([^)]*\)')
URL = re.compile(r'https?://\S+|mailto:\S+|www\.\S+')
NUM = re.compile(r'\d+(?:[.,:/]\d+)*|\b(?:january|february|march|april|june|july|august|september|october|november|december)\b', re.I)
LEAD = re.compile(r'^[\W_]*\d+(?:\\?\.\d+)*\\?\.?\s*')


def paras(text):
    return [' '.join(LINK.sub(']', l).split()) for l in text.replace('\r', '').split('\n') if l.strip()]


TARGET = re.compile(r'\]\(([^)]*)\)')


def link_targets(text):
    """Markdown link targets per paragraph, aligned with paras(text)."""
    return [TARGET.findall(l) for l in text.replace('\r', '').split('\n') if l.strip()]


def nums(ps):
    return sorted(m.lower() for p in ps for m in NUM.findall(URL.sub(' ', p)))


def pnums(p):
    """Number/date tokens of one paragraph, ignoring a leading list or section number."""
    return nums([LEAD.sub('', p)])


@dataclass
class Block:
    before: list            # 0 or 1 unchanged paragraph
    old: list               # changed old paragraphs
    new: list               # changed new paragraphs
    after: list             # 0 or 1 unchanged paragraph
    numeric: list = field(default_factory=list)   # [(old para, new para)] whose number/date tokens differ

    @property
    def old_text(self):
        return '\n\n'.join(self.before + self.old + self.after)

    @property
    def new_text(self):
        return '\n\n'.join(self.before + self.new + self.after)


@dataclass
class Change:
    blocks: list
    n_changed: int          # changed paragraphs, old + new

    @property
    def old_region(self):
        return SEP.join(b.old_text for b in self.blocks)

    @property
    def new_region(self):
        return SEP.join(b.new_text for b in self.blocks)

    links: list = field(default_factory=list)     # [(paragraph, old targets, new targets)] for unchanged paragraphs

    @property
    def numeric(self):
        return [x for b in self.blocks for x in b.numeric]


def diff(old_text, new_text):
    O, N = paras(old_text), paras(new_text)
    LO, LN = link_targets(old_text), link_targets(new_text)
    blocks, n, links = [], 0, []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, O, N, autojunk=False).get_opcodes():
        if tag == 'equal':
            # Text equal after normalization, but a link may now point elsewhere: listed by rule, never scored
            # (GPT r1: a changed URL can change obligations).
            for k in range(i2 - i1):
                if LO[i1 + k] != LN[j1 + k]: links.append((O[i1 + k], LO[i1 + k], LN[j1 + k]))
            continue
        numeric = []
        if j2 > j1:
            for i in range(i1, i2):
                r, j = max((difflib.SequenceMatcher(None, O[i], N[j]).ratio(), j) for j in range(j1, j2))
                if r >= .6 and pnums(O[i]) != pnums(N[j]): numeric.append((O[i], N[j]))
        before = O[i1 - 1:i1] if i1 > 0 else []
        blocks.append(Block(before, O[i1:i2], N[j1:j2], O[i2:i2 + 1], numeric))
        n += (i2 - i1) + (j2 - j1)
    return Change(blocks, n, links)


def chunks(change, cap):
    """Split a change into groups of blocks whose old and new regions each stay under `cap` characters.
    A single block longer than cap is its own chunk (the model reads it truncated by its own context)."""
    out, cur = [], []
    for b in change.blocks:
        trial = cur + [b]
        if cur and max(len(SEP.join(x.old_text for x in trial)), len(SEP.join(x.new_text for x in trial))) > cap:
            out.append(cur); cur = [b]
        else:
            cur = trial
    if cur: out.append(cur)
    return [Change(c, sum(len(x.old) + len(x.new) for x in c)) for c in out]


def word_diff(a, b):
    """[(op, text)] with op in '=', '-', '+' at word granularity, for display."""
    A, B = re.findall(r'\S+|\s+', a), re.findall(r'\S+|\s+', b)
    out = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, A, B, autojunk=False).get_opcodes():
        if tag == 'equal': out.append(('=', ''.join(A[i1:i2])))
        else:
            if i2 > i1: out.append(('-', ''.join(A[i1:i2])))
            if j2 > j1: out.append(('+', ''.join(B[j1:j2])))
    return out
