"""Each gold incident's blocks with both arms' scores (exploratory, written after the kill test's result).

  py -m aiwatch.incidents   -> one line per AI-vocabulary block of each eligible incident's change commit

Used in RESULT_aiwatch.md to explain why both arms missed the same four GRANT incidents. Reads the hashed outputs;
changes nothing.
"""
from aiwatch.backtest import kev_table, gold

if __name__ == '__main__':
    C = kev_table()
    for g in gold():
        rows = [c for c in C if c['coll'] == g['ota_collection'] and c['commit'].startswith(g['change_commit'][:8])]
        print(f"== {g['direction']:11} {g['service']} | {g['document']} | {g['change_date']} | {g['change_commit'][:9]} | "
              f"{len(rows)} blocks")
        for c in rows:
            k = c['kev']
            print(f"   grant {k['grant'][0]:.3f}->{k['grant'][1]:.3f}  promise {k['promise'][0]:.2f}->{k['promise'][1]:.2f}  "
                  f"ban {k['ban'][0]:.2f}->{k['ban'][1]:.2f}  keyword alert {c['regex_alert']}")
