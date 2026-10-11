"""Keep the sweep docs consistent across regions (added 2026-10-10, Alexandra: "no deviating").

One rulebook (CLAUDE.md) holds every rule and the one sweep procedure. Each region has a source list in
sources/<region>.md, all in the same fixed format. This script fails (exit 1) when:
  - a sources file is missing a header field, uses a section that is not allowed, or has no numbered sources;
  - a file's "Source count" does not match the numbered entries under "## Sources", or numbers repeat;
  - a region has a sources file but no row in CLAUDE.md's Regions table (or the reverse);
  - CLAUDE.md is missing the shared sweep / processing / regions sections.
A sources file may hold SOURCES ONLY: rules belong in CLAUDE.md, where they apply to every region.

Usage:
  python check_docs.py              # check the real files
  python check_docs.py --self-test  # prove the checks can fail
"""
import os, re, sys, tempfile, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ['Region key', '`county` value on records', 'Sweep window', 'Review workbook', 'Source count']
ALLOWED_H2 = {'Sources', 'Not yet verified', 'Retired or seasonal', 'Reference'}
CLAUDE_SECTIONS = ['## Regions (Marin, Napa, Telluride+)', '## Weekly sweep (one procedure for every region)',
                   '## Processing an approved sweep (every region)']


def check(root):
    errs = []
    src_dir = os.path.join(root, 'sources')
    claude = open(os.path.join(root, 'CLAUDE.md'), encoding='utf-8').read()
    for sec in CLAUDE_SECTIONS:
        if sec not in claude:
            errs.append(f'CLAUDE.md: missing section "{sec}"')
    reg = claude[claude.find('## Regions'):]
    reg = reg[:reg.find('\n## ', 5)] if '\n## ' in reg[5:] else reg
    table_files = set(re.findall(r'`sources/([a-z]+)\.md`', reg))
    files = sorted(f for f in os.listdir(src_dir) if f.endswith('.md')) if os.path.isdir(src_dir) else []
    if not files:
        errs.append('sources/: no region files')
    for f in files:
        key = f[:-3]
        t = open(os.path.join(src_dir, f), encoding='utf-8').read()
        tag = f'sources/{f}'
        if not t.startswith('# Sweep sources: '):
            errs.append(f'{tag}: first line must be "# Sweep sources: <Region>"')
        vals = {}
        for fld in FIELDS:
            m = re.search(r'^\| ' + re.escape(fld) + r' \| (.+?) \|\s*$', t, re.M)
            if not m:
                errs.append(f'{tag}: header field "{fld}" missing')
            else:
                vals[fld] = m.group(1).strip()
        if vals.get('Region key') and vals['Region key'].strip('`') != key:
            errs.append(f'{tag}: Region key {vals["Region key"]} does not match file name')
        for h in re.findall(r'^## (.+)$', t, re.M):
            if h.strip() not in ALLOWED_H2:
                errs.append(f'{tag}: section "## {h}" not allowed (allowed: {", ".join(sorted(ALLOWED_H2))}). Rules go in CLAUDE.md.')
        m = re.search(r'^## Sources\s*$(.*?)(?=^## |\Z)', t, re.M | re.S)
        if not m:
            errs.append(f'{tag}: no "## Sources" section')
            continue
        nums = [int(n) for n in re.findall(r'^(\d+)\. \*\*', m.group(1), re.M)]
        if not nums:
            errs.append(f'{tag}: no numbered sources ("N. **Name** — ...")')
        if len(nums) != len(set(nums)):
            errs.append(f'{tag}: repeated source numbers {sorted(n for n in set(nums) if nums.count(n) > 1)}')
        cnt = vals.get('Source count', '')
        if not cnt.isdigit():
            errs.append(f'{tag}: Source count must be a number, got "{cnt}"')
        elif int(cnt) != len(nums):
            errs.append(f'{tag}: Source count says {cnt} but {len(nums)} numbered sources found')
        if key not in table_files:
            errs.append(f'{tag}: no row for it in CLAUDE.md "Regions" table')
    for k in table_files - {f[:-3] for f in files}:
        errs.append(f'CLAUDE.md Regions table names sources/{k}.md, which does not exist')
    return errs


def self_test():
    ok = True
    tmp = tempfile.mkdtemp()
    try:
        shutil.copytree(os.path.join(HERE, 'sources'), os.path.join(tmp, 'sources'))
        shutil.copy(os.path.join(HERE, 'CLAUDE.md'), tmp)
        base = check(tmp)
        if base:
            print('self-test: real files are not clean, fix them first'); return False
        cases = [
            ('a rule section added to a region file', lambda t: t + '\n## Age categories\nTelluride uses different ages.\n'),
            ('a wrong Source count', lambda t: re.sub(r'(\| Source count \| )\d+', r'\g<1>999', t)),
            ('a missing header field', lambda t: re.sub(r'^\| Sweep window \|.*\n', '', t, flags=re.M)),
            ('a repeated source number', lambda t: t.replace('\n2. **', '\n1. **', 1)),
        ]
        target = os.path.join(tmp, 'sources', 'telluride.md')
        orig = open(target, encoding='utf-8').read()
        for name, mut in cases:
            open(target, 'w', encoding='utf-8').write(mut(orig))
            caught = bool(check(tmp))
            print(f'  {"PASS" if caught else "FAIL"}: catches {name}')
            ok &= caught
        open(target, 'w', encoding='utf-8').write(orig)
        os.remove(os.path.join(tmp, 'sources', 'napa.md'))
        caught = bool(check(tmp)); print(f'  {"PASS" if caught else "FAIL"}: catches a region in the table with no sources file'); ok &= caught
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('self-test:', 'all passed' if ok else 'FAILED')
    return ok


if __name__ == '__main__':
    if '--self-test' in sys.argv:
        sys.exit(0 if self_test() else 1)
    errs = check(HERE)
    for e in errs:
        print('  ✗', e)
    print(f'check_docs: {"clean" if not errs else f"{len(errs)} problem(s)"} ({len(os.listdir(os.path.join(HERE, "sources")))} region files)')
    sys.exit(1 if errs else 0)
