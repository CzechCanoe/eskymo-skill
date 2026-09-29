# -*- coding: utf-8 -*-
"""
recalc — přepočítá vzorce Eskymo sešitu v headless LibreOffice a uloží KOPII.

    python recalc.py vystup.ods [--outdir DIR] [--format ods|xlsx]

Proč: skripty zapisují jen vstupní buňky; výsledky vzorců (jména, oddíly,
VT z registru, pořadí…) jsou v souboru zastaralé, dokud je Calc nepřepočítá.
Bez přepočtu nejde poznat, jestli se VLOOKUPy chytly.

Přepočtená kopie slouží KE KONTROLE (verify_workbook.py). Pořadateli se
předává původní výstup skriptu — Eskymo si ho po otevření přepočítá samo
(Ctrl+Shift+F9); kopii uloženou LibreOffice do Eskyma raději nevracej.

Hledání LibreOffice (první nalezené):
  1. proměnná prostředí ESKYMO_SOFFICE (cesta k soffice/soffice.com)
  2. `soffice` / `libreoffice` v PATH
  3. obvyklé instalační cesty (Windows, macOS, Linux)
Apache OpenOffice (v něm Eskymo běží) headless převod neumí — potřeba je
LibreOffice. Když není k dispozici, skript to řekne a skončí kódem 2;
kontrola se pak dělá ručně (viz references/kontrola.md).
"""
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

PROFILE_XCU = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry">
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""

_CANDIDATES = [
    r'C:\Program Files\LibreOffice\program\soffice.com',
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.com',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice',
    '/usr/bin/soffice', '/usr/bin/libreoffice', '/usr/local/bin/soffice',
    '/opt/libreoffice/program/soffice', '/snap/bin/libreoffice',
]


def _is_libreoffice(path: str) -> bool:
    try:
        r = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=60)
        return 'LibreOffice' in (r.stdout + r.stderr)
    except (OSError, subprocess.SubprocessError):
        return False


def find_soffice() -> str | None:
    env = os.environ.get('ESKYMO_SOFFICE')
    cands = [env] if env else []
    cands += [shutil.which('soffice'), shutil.which('libreoffice')]
    cands += _CANDIDATES
    for c in cands:
        if c and os.path.exists(c) and _is_libreoffice(c):
            return c
    return None


def recalc(src: str, outdir: str | None = None, fmt: str = 'ods', soffice: str | None = None) -> str:
    """Vrátí cestu k přepočtené kopii. Vyhodí RuntimeError, když to nejde."""
    soffice = soffice or find_soffice()
    if not soffice:
        raise RuntimeError('LibreOffice nenalezen (nastav ESKYMO_SOFFICE nebo nainstaluj LibreOffice)')
    src = os.path.abspath(src)
    base = os.path.splitext(os.path.basename(src))[0]
    work = tempfile.mkdtemp(prefix='eskymo-recalc-')
    try:
        prof = os.path.join(work, 'profile')
        os.makedirs(os.path.join(prof, 'user'))
        with open(os.path.join(prof, 'user', 'registrymodifications.xcu'), 'w', encoding='utf-8') as f:
            f.write(PROFILE_XCU)
        # Kopie do pracovního adresáře a relativní cesty: LibreOffice na Windows
        # občas tiše nic nevyrobí, když dostane --outdir s lomítky / 8.3 jmény.
        indir = os.path.join(work, 'in')
        os.makedirs(indir)
        shutil.copy2(src, os.path.join(indir, 'in.ods'))
        cmd = [soffice, '--headless', '--norestore', '--nolockcheck',
               f'-env:UserInstallation={pathlib.Path(prof).as_uri()}',
               '--convert-to', fmt, '--outdir', 'out', 'in.ods']
        r = subprocess.run(cmd, cwd=indir, capture_output=True, text=True, timeout=600)
        produced = os.path.join(indir, 'out', f'in.{fmt}')
        if not os.path.exists(produced):
            raise RuntimeError(f'LibreOffice nevyrobil výstup (rc={r.returncode}): {r.stdout} {r.stderr}')
        outdir = os.path.abspath(outdir or os.path.dirname(src))
        os.makedirs(outdir, exist_ok=True)
        dst = os.path.join(outdir, f'{base}.prepocet.{fmt}')
        shutil.move(produced, dst)
        return dst
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ods')
    ap.add_argument('--outdir')
    ap.add_argument('--format', default='ods', choices=['ods', 'xlsx'])
    a = ap.parse_args(argv)
    try:
        out = recalc(a.ods, a.outdir, a.format)
    except RuntimeError as e:
        print(f'PŘEPOČET NEPROBĚHL: {e}', file=sys.stderr)
        return 2
    print(out)
    return 0


if __name__ == '__main__':
    sys.exit(main())
