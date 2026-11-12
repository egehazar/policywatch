"""Pull ToS;DR's approved points, with their quoted evidence, for the platforms in Open Terms Archive's pga-versions.

Public API (api.tosdr.org), one request about every 0.6 s. Writes stale/data/<platform>.json:
  {platform, service_id, service, documents: [{id, name, url}], points: [{id, case_id, case_title, classification,
   status, document_id, quote_text, quote_start, quote_end, created_at, updated_at, source}]}
Resumable: a platform whose file exists is skipped.  Usage  py -m stale.pull
"""
import json, os, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'data')
API = 'https://api.tosdr.org'; UA = {'User-Agent': 'policywatch-research (local, low-rate)'}

# pga-versions platform -> ToS;DR service id (matched by name 2026-11-12; X and Twitter share one service)
SERVICES = {'BeReal': 6742, 'Bluesky': 10752, 'Facebook': 182, 'Instagram': 219, 'LINE': 2895, 'LinkedIn': 193,
            'Mastodon': 639, 'Parler': 3206, 'Pinterest': 175, 'Quora': 314, 'Reddit': 194, 'Snapchat': 311,
            'Spotify': 225, 'Telegram': 1946, 'Threads': 11718, 'TikTok': 1448, 'Tumblr': 280, 'Twitch': 200,
            'X': 195, 'WeChat': 9563, 'WhatsApp': 198, 'YouTube': 274}


def get(path, tries=4):
    for i in range(tries):
        try:
            req = urllib.request.Request(API + path, headers=UA)
            r = json.loads(urllib.request.urlopen(req, timeout=60).read()); time.sleep(0.6); return r
        except Exception:
            if i == tries - 1: raise
            time.sleep(5 * (i + 1))


def main():
    os.makedirs(OUT, exist_ok=True)
    for plat, sid in SERVICES.items():
        path = os.path.join(OUT, plat + '.json')
        if os.path.exists(path): continue
        s = get(f'/service/v3/?id={sid}')
        pts = []
        for p in s.get('points', []):
            d = get(f"/point/v1/?id={p['id']}"); c = d.get('case') or {}
            pts.append({'id': d['id'], 'case_id': c.get('id'), 'case_title': c.get('title'), 'classification': c.get('classification'),
                        'status': d.get('status'), 'document_id': d.get('document_id'), 'quote_text': d.get('quote_text'),
                        'quote_start': d.get('quote_start'), 'quote_end': d.get('quote_end'), 'created_at': d.get('created_at'),
                        'updated_at': d.get('updated_at'), 'source': d.get('source'), 'title': d.get('title')})
        rec = {'platform': plat, 'service_id': sid, 'service': s.get('name'), 'pulled_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
               'documents': [{'id': x['id'], 'name': x['name'], 'url': x.get('url'), 'updated_at': x.get('updated_at')} for x in s.get('documents', [])],
               'points': pts}
        with open(path + '.tmp', 'w', encoding='utf-8') as f: json.dump(rec, f, ensure_ascii=False, indent=1)
        os.replace(path + '.tmp', path)
        print(plat, sid, s.get('name'), len(pts), 'points', sum(1 for p in pts if p['quote_text']), 'with quotes', flush=True)


if __name__ == '__main__':
    main()
