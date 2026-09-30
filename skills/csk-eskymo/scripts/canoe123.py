# -*- coding: utf-8 -*-
"""
canoe123 — výsledky z Canoe123 XML do Eskyma (obal nad vendorovaným canoe123-2-eskymo).

  python canoe123.py prehled export.xml [--sablona zavod.ods]
      PŘED převodem: dny (suffix RaceId), třídy a počty po dnech, NEZNÁMÉ třídy
      (nikdy tiše nezahazovat), rizikové záznamy (bez ICFId, ne-číselné ICFId,
      deble ve starém slepeném formátu, Id≠ICFId), a se šablonou i kapacitu listů
      (param #řádek) a chybějící listy.
  python canoe123.py slalom export.xml sablona.ods vystup.ods --day 15 [--race 102 --date 15.08.26 --name "…"]
      převod slalomu (vendor/canoe123_2_eskymo/canoe2eskymo.py) + kontrola RGC ∈ reg ∪ cizi
      a počtů proti XML. Každý den = samostatný soubor z ČISTÉ šablony.
  python canoe123.py cross export.xml sablona.ods vystup.ods --day 26 [--day-final 27] [--date …]
      kajak kros (vendor/.../cross.py) — šablona není Eskymo sešit (viz references/vysledky.md).

Po převodu vždy: verify_workbook.py vystup.ods --vysledky (přepočet + úplnost jízd).
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from xml.etree import ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, 'vendor', 'canoe123_2_eskymo')
NS = '{http://siwidata.com/Canoe123/Data.xsd}'


def _vendor_classes() -> dict:
    spec = importlib.util.spec_from_file_location('c2e', os.path.join(VENDOR, 'canoe2eskymo.py'))
    try:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return dict(m.CLASS_TO_SHEETS)
    except ImportError:  # odfpy chybí — stačí statická kopie mapy
        return {'K1M': ('k1m', 'k1m_sl'), 'K1W': ('k1z', 'k1z_sl'), 'K1Z': ('k1z', 'k1z_sl'),
                'C1M': ('c1m', 'c1m_sl'), 'C1W': ('c1z', 'c1z_sl'), 'C1Z': ('c1z', 'c1z_sl'),
                'C2M': ('c2m', 'c2m_sl'), 'C2W': ('c2z', 'c2z_sl'), 'C2Z': ('c2z', 'c2z_sl'),
                'C2X': ('c2x', 'c2x_sl'), 'PZK': ('pzk', 'pzk_sl'), 'PZC': ('pzc', 'pzc_sl')}


def _t(el, tag):
    x = el.find(NS + tag)
    return (x.text or '').strip() if x is not None and x.text else ''


def nacti(xml: str):
    root = ET.parse(xml).getroot()
    parts, res = [], defaultdict(set)
    for el in root:
        tag = el.tag.replace(NS, '')
        if tag == 'Participants':
            parts.append({k: _t(el, k) for k in ('Id', 'ClassId', 'EventBib', 'ICFId', 'ICFId2',
                                                   'FamilyName', 'FamilyName2', 'CatId')})
        elif tag == 'Results':
            rid = _t(el, 'RaceId')
            if rid and rid != '<unassigned>':
                res[rid].add(_t(el, 'Id'))
    return parts, res


def prehled(xml: str, sablona: str | None = None) -> tuple[str, int]:
    parts, res = nacti(xml)
    known = _vendor_classes()
    L, problemy = [], 0
    dny = sorted({r.rsplit('_', 1)[-1] for r in res}, key=lambda d: int(d) if d.isdigit() else 0)
    L.append(f'Dny (suffix RaceId): {", ".join(dny)}   závodů (RaceId): {len(res)}')
    tridy = Counter(p['ClassId'] for p in parts)
    cross = {c for c in tridy if re.match(r'^[MW]X1|^X1', c)}
    L.append('Třídy v XML: ' + ', '.join(f'{c} {n}' for c, n in sorted(tridy.items())))
    nezname = [c for c in tridy if c not in known and c not in cross]
    if nezname:
        problemy += 1
        L.append(f'! NEZNÁMÉ TŘÍDY (převod je vynechá): {", ".join(nezname)} — rozhodni s pořadatelem '
                 '(nový alias v upstream skriptu, nebo úmyslně vynechat)')
    if cross:
        L.append(f'i Kros třídy: {", ".join(sorted(cross))} → použij podpříkaz `cross`')
    dup = defaultdict(list)
    for c in tridy:
        if c in known:
            dup[known[c][1]].append(c)
    for sh, cs in dup.items():
        if len(cs) > 1:
            problemy += 1
            L.append(f'! {", ".join(cs)} míří do stejného listu {sh} — převod skončí chybou')

    L.append('\nÚčastníci s výsledkem po dnech (jen ti jdou do výstupu):')
    po_dnech = {}
    for d in dny:
        cnt = Counter()
        for p in parts:
            if any(p['Id'] in res.get(f"{p['ClassId']}_BR{n}_{d}", set()) for n in (1, 2)):
                cnt[p['ClassId']] += 1
        po_dnech[d] = cnt
        if cnt:
            L.append(f'  den {d}: ' + ', '.join(f'{c} {n}' for c, n in sorted(cnt.items())))

    rizika = Counter()
    for p in parts:
        if not p['ICFId']:
            rizika['bez ICFId (cizinec → A-kód)'] += 1
        elif not p['ICFId'].isdigit():
            rizika['ne-číselné ICFId (A-kód / slepenec s A)'] += 1
        if p['ClassId'].startswith('C2') and p['ICFId'] and not p['ICFId2']:
            rizika['debl ve starém slepeném formátu'] += 1
        idp = p['Id'].split('.')[0]
        if p['ICFId'].isdigit() and idp.isdigit() and idp != p['ICFId']:
            rizika['Id ≠ ICFId (věří se ICFId)'] += 1
    if rizika:
        L.append('\nRizikové záznamy (po převodu zkontroluj cizi a RGC):')
        L += [f'  - {k}: {n}' for k, n in rizika.items()]

    if sablona:
        sys.path.insert(0, HERE)
        from eskymo_ods import Workbook
        wb = Workbook(sablona)
        L.append(f'\nŠablona {os.path.basename(sablona)}:')
        for c in sorted(tridy):
            if c not in known:
                continue
            res_sh, sl_sh = known[c]
            mx = max((po_dnech[d][c] for d in dny), default=0)
            if not mx:
                continue
            if not wb.has(sl_sh):
                L.append(f'  ! {c}: list {sl_sh} chybí — {mx} závodníků se přeskočí (potvrď s pořadatelem)')
                problemy += 1
                continue
            vals = wb.sheet(sl_sh).values(max_cols=1)
            cap = sum(1 for r in vals[2:] if r and isinstance(r[0], float))
            if mx > cap:
                problemy += 1
                L.append(f'  ! {c}: {mx} závodníků, list má jen {cap} řádků (#řádek) — převod skončí chybou; '
                         'v Eskymu založ sešit s vyšším #řádek')
            else:
                L.append(f'  {c}: max {mx} závodníků / kapacita {cap}')
    return '\n'.join(L), problemy


def _run(script, args):
    cmd = [sys.executable, os.path.join(VENDOR, script)] + args
    return subprocess.run(cmd).returncode


def kontrola_po(xml, vystup, day):
    sys.path.insert(0, HERE)
    from eskymo_ods import Workbook
    from registr import Registr
    wb = Workbook(vystup)
    reg = Registr.ze_sesitu(wb)
    known = _vendor_classes()
    parts, res = nacti(xml)
    chyby = []
    for c, (res_sh, sl_sh) in known.items():
        exp = sum(1 for p in parts if p['ClassId'] == c and any(
            p['Id'] in res.get(f'{c}_BR{n}_{day}', set()) for n in (1, 2)))
        if not exp or not wb.has(sl_sh):
            continue
        rows = [r for r in wb.sheet(sl_sh).values(max_cols=3)[2:] if len(r) > 2 and r[2] not in (None, '', ' ')]
        got = len(rows)
        others = sum(1 for c2, v in known.items() if v[1] == sl_sh and c2 != c and any(
            p['ClassId'] == c2 for p in parts))
        if got != exp and not others:
            chyby.append(f'{sl_sh}: zapsáno {got}, v XML {exp}')
        for r in rows:
            for x in str(r[2] if not isinstance(r[2], float) else int(r[2])).split():
                if not reg.get(x):
                    chyby.append(f'{sl_sh}: RGC {x} (stč {r[1]}) není v reg ani cizi → prázdné jméno v Eskymu')
    return chyby


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a0 = sub.add_parser('prehled'); a0.add_argument('xml'); a0.add_argument('--sablona')
    for name in ('slalom', 'cross'):
        a = sub.add_parser(name)
        a.add_argument('xml'); a.add_argument('sablona'); a.add_argument('vystup')
        a.add_argument('--day', required=True)
        a.add_argument('--date'); a.add_argument('--race'); a.add_argument('--name')
        if name == 'cross':
            a.add_argument('--day-final'); a.add_argument('--no-body', action='store_true')
    a = ap.parse_args(argv)
    if a.cmd == 'prehled':
        txt, n = prehled(a.xml, a.sablona)
        print(txt)
        return 1 if n else 0
    if os.path.abspath(a.sablona) == os.path.abspath(a.vystup):
        print('Výstup nesmí přepsat šablonu pořadatele.', file=sys.stderr)
        return 2
    args = [a.xml, a.sablona, a.vystup, '--day', a.day]
    for k in ('race', 'date', 'name'):
        if getattr(a, k):
            args += [f'--{k}', getattr(a, k)]
    if a.cmd == 'cross':
        if a.day_final:
            args += ['--day-final', a.day_final]
        if a.no_body:
            args.append('--no-body')
        return _run('cross.py', args)
    rc = _run('canoe2eskymo.py', args)
    if rc:
        return rc
    chyby = kontrola_po(a.xml, a.vystup, a.day)
    print('\nKontrola po převodu:', 'OK' if not chyby else f'{len(chyby)} problémů')
    for c in chyby[:60]:
        print(f'  ! {c}')
    print(f'Dál: verify_workbook.py {a.vystup} --vysledky')
    return 1 if chyby else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
