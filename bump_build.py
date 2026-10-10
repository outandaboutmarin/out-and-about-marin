"""Bump the app build stamp in index.html AND version.json together. Run after ANY index.html change.
Open tabs compare their APP_BUILD with version.json and reload when they differ (see AUTO-UPDATE in index.html).
Usage: python bump_build.py"""
import datetime, json, os, re
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, 'index.html')
h = open(p, encoding='utf-8').read()
old = re.search(r"const APP_BUILD = '([^']+)';", h).group(1)
today = datetime.date.today().isoformat()
n = int(old.rsplit('.', 1)[1]) + 1 if old.startswith(today + '.') else 1
new = f"{today}.{n}"
h = h.replace(f"const APP_BUILD = '{old}';", f"const APP_BUILD = '{new}';", 1)
open(p, 'w', encoding='utf-8').write(h)
json.dump({"build": new}, open(os.path.join(here, 'version.json'), 'w', encoding='utf-8'))
print(old, '->', new)
