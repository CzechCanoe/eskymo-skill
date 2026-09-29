# -*- coding: utf-8 -*-
"""
build_skill_zip — zabalí skill pro nahrání do Claude (claude.ai / Claude desktop / Cowork)
nebo jiného harnessu podle standardu Agent Skills.

    python tools/build_skill_zip.py            # → dist/csk-eskymo.zip

Zip obsahuje složku `csk-eskymo/` (SKILL.md, scripts/, references/). Bez __pycache__
a bez čehokoli mimo skill (testy, fixtures, podklady).
"""
from __future__ import annotations

import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, 'skills', 'csk-eskymo')


def main():
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    out = os.path.join(ROOT, 'dist', 'csk-eskymo.zip')
    n = 0
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(SKILL):
            dirs[:] = [d for d in dirs if d != '__pycache__']
            for f in files:
                if f.endswith(('.pyc', '.ods', '.xlsx', '.csv')):
                    continue
                p = os.path.join(base, f)
                z.write(p, os.path.join('csk-eskymo', os.path.relpath(p, SKILL)))
                n += 1
    print(f'{out} ({n} souborů, {os.path.getsize(out) // 1024} kB)')


if __name__ == '__main__':
    sys.exit(main())
