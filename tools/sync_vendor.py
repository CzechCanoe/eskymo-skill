# -*- coding: utf-8 -*-
"""
sync_vendor — přenese canoe2eskymo.py a cross.py z repa canoe123-2-eskymo do skillu.

    python tools/sync_vendor.py --ref main [--repo ../c1232eskymo]
    python tools/sync_vendor.py --ref v1.2.0 --repo https://github.com/CzechCanoe/canoe123-2-eskymo.git

Soubory se berou z daného commitu/větve/tagu (ne z pracovní kopie), přepíše se tabulka
ve VENDOR.md. Potom spusť `python tests/run_tests.py`. Ručně vendorované soubory neupravuj —
oprava patří upstream (PR) a sem se dostane dalším syncem.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, 'skills', 'csk-eskymo', 'scripts', 'vendor', 'canoe123_2_eskymo')
FILES = ['canoe2eskymo.py', 'cross.py', 'LICENSE']


def git(repo, *args) -> str:
    return subprocess.run(['git', '-C', repo, *args], check=True, capture_output=True, text=True).stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ref', required=True)
    ap.add_argument('--repo', default=os.path.join(os.path.dirname(ROOT), 'c1232eskymo'),
                    help='lokální klon nebo URL repa canoe123-2-eskymo')
    ap.add_argument('--popis', default='', help='stav (např. „main po sloučení PR #1“)')
    a = ap.parse_args()
    repo, tmp = a.repo, None
    if re.match(r'https?://', repo):
        tmp = tempfile.mkdtemp()
        subprocess.run(['git', 'clone', '--quiet', repo, tmp], check=True)
        repo = tmp
    else:
        subprocess.run(['git', '-C', repo, 'fetch', '--quiet', '--all'], check=False)
    sha = git(repo, 'rev-parse', a.ref).strip()
    datum = git(repo, 'show', '-s', '--format=%cs', sha).strip()
    for f in FILES:
        data = subprocess.run(['git', '-C', repo, 'show', f'{sha}:{f}'], check=True, capture_output=True).stdout
        open(os.path.join(VENDOR, f), 'wb').write(data)
    vm = os.path.join(VENDOR, 'VENDOR.md')
    s = open(vm, encoding='utf-8').read()
    s = re.sub(r'\| commit \|.*\|', f'| commit | `{sha}` ({datum}) |', s)
    if a.popis:
        s = re.sub(r'\| stav \|.*\|', f'| stav | {a.popis} |', s)
    open(vm, 'w', encoding='utf-8').write(s)
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'Vendor aktualizován na {sha[:10]} ({datum}). Spusť: python tests/run_tests.py')


if __name__ == '__main__':
    sys.exit(main())
