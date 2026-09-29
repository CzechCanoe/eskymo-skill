# -*- coding: utf-8 -*-
"""
verify_workbook — povinná kontrola sešitu po každém zápisu.

    python verify_workbook.py vystup.ods [--plan plan.json | --lode lode.json] [--vysledky]
                              [--cisla-v-kategorii] [--bez-prepoctu]

1. Přepočítá kopii sešitu v headless LibreOffice (recalc.py). Bez přepočtu nejde
   poznat, jestli se VLOOKUPy do registru chytly. Když LibreOffice není, kontroluje
   uložené hodnoty — to má smysl jen u souboru, který člověk v Eskymu přepočítal
   (Ctrl+Shift+F9) a uložil.
2. Startovky: u každého zapsaného řádku jméno a oddíl z registru, žádné #N/A,
   #NAME?, #VALUE!; startovní čísla vyplněná a unikátní; fyzické pořadí monotónní.
3. Proti plánu / lode.json: počty lodí po kategoriích a všechna RGC na svém místě.
4. --vysledky: každá jízda zapsaného závodníka má čas nebo stav (DNS/DNF/DSQ…),
   stav má penalizaci 999, žádná prázdná buňka (prázdný čas ve sjezdu = čas 0 → 1. místo!).
Vrací 0 = bez problémů, 1 = problémy, 2 = sešit nejde zkontrolovat.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict

from domena import stav_jizdy
from eskymo_ods import Workbook, norm_rgc
from inspect_workbook import read_param

_ERR = re.compile(r'^(#N/A|#NAME\?|#VALUE!|#REF!|#DIV/0!|Err:\d+|#NUM!|#NULL!)')
_PROHLIDKA = re.compile(r'^#\s*\d{4}')


def _je_chyba(v) -> bool:
    return isinstance(v, str) and bool(_ERR.match(v.strip()))


def _prazdne(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def zkontroluj(path: str, plan=None, lode=None, vysledky=False, cisla_v_kategorii=False) -> dict:
    wb = Workbook(path)
    if not wb.has('param'):
        return {'problemy': ['sešit nemá list param — není z Eskyma'], 'varovani': [], 'info': [], 'pocty': {}}
    param = read_param(wb)
    pole = {k: v['hodnota'] for k, v in param['pole'].items()}
    hlidky = str(pole.get('Hlídky', '')).strip().lower() == 'ano'
    disciplina = str(pole.get('Disciplína') or 'slalom').strip().lower()
    jizd = int(float(pole.get('Počet jízd') or 2))
    kats = [k['kod'].lower() for k in param['kategorie']]
    P, V, I = [], [], []
    pocty, rgc_v_kat, vsechna_stc = {}, defaultdict(list), []

    if hlidky and wb.has('hlidky'):
        for r, row in enumerate(wb.sheet('hlidky').values(max_cols=12)[1:], start=2):
            if row and not _prazdne(row[0]):
                for c, v in enumerate(row):
                    if _je_chyba(v):
                        P.append(f'hlidky ř.{r} ({row[0]}): chyba vzorce ve sloupci {"ABCDEFGHIJKL"[c]} → {v}')

    for kat in kats:
        if not wb.has(f'{kat}_sl'):
            continue
        rows = wb.sheet(f'{kat}_sl').values(max_cols=16)
        n, stc_kat = 0, []
        for r, row in enumerate(rows[2:], start=3):
            row = list(row) + [None] * (16 - len(row))
            klic = row[15] if hlidky else row[2]
            if _prazdne(klic) or (isinstance(klic, float) and klic == 0):
                if not _prazdne(row[1]):
                    V.append(f'{kat}_sl ř.{r}: stč {row[1]} bez závodníka')
                continue
            n += 1
            ozn = f'{kat}_sl ř.{r} ({row[2] if not hlidky else row[15]})'
            rgc_v_kat[kat].append(norm_rgc(row[2]) if not hlidky else str(row[15]))
            for c in range(2, 8):
                if _je_chyba(row[c]):
                    P.append(f'{ozn}: chyba vzorce ve sloupci {"ABCDEFGH"[c]} → {row[c]}')
            if not _je_chyba(row[3]) and _prazdne(row[3]):
                P.append(f'{ozn}: prázdné jméno — RGC není v reg/cizi (nebo sešit není přepočítaný)')
            if not _je_chyba(row[7]) and _prazdne(row[7]):
                P.append(f'{ozn}: prázdný oddíl')
            if isinstance(row[4], str) and _PROHLIDKA.match(row[4].strip()):
                I.append(f'{ozn}: {str(row[3]).splitlines()[0]} — bez platné lékařské prohlídky (#)')
            if isinstance(row[1], float):
                stc_kat.append(int(row[1]))
            else:
                P.append(f'{ozn}: chybí startovní číslo')
        pocty[kat] = n
        vsechna_stc += stc_kat
        dup = [s for s, c in Counter(stc_kat).items() if c > 1]
        if dup:
            P.append(f'{kat}_sl: duplicitní stč {sorted(dup)}')
        if len(stc_kat) > 2 and stc_kat != sorted(stc_kat) and stc_kat != sorted(stc_kat, reverse=True):
            V.append(f'{kat}_sl: stč nejsou ve fyzickém pořadí monotónní — Eskymo počítá startovní časy '
                     'podle pořadí řádků; ověř, že pořadí řádků = pořadí startu')
    dup = [s for s, c in Counter(vsechna_stc).items() if c > 1]
    if dup and not cisla_v_kategorii:
        V.append(f'stč se opakují mezi kategoriemi: {sorted(dup)[:15]} — P 2.18.03 chce u nové startovky '
                 'čísla unikátní (kategorie od čísla končícího 1); je-li to záměr (ČPw, barevná čísla, převzaté '
                 'z časomíry), je to v pořádku (--cisla-v-kategorii)')

    # proti plánu / přihláškám
    ocekavano = {}
    if plan:
        for k in plan['kategorie']:
            ocekavano[k['kat']] = [norm_rgc(' '.join(p['rgc'])) for p in k['lode']]
    elif lode:
        for l in lode:
            ocekavano.setdefault(l['kat'], []).append(norm_rgc(' '.join(l['rgc'])))
    if ocekavano and not hlidky:
        for kat, exp in ocekavano.items():
            got = rgc_v_kat.get(kat, [])
            if Counter(got) != Counter(exp):
                chybi = list((Counter(exp) - Counter(got)).elements())
                navic = list((Counter(got) - Counter(exp)).elements())
                P.append(f'{kat}: ve startovce {len(got)}, čekáno {len(exp)}'
                         + (f'; chybí {chybi[:8]}' if chybi else '') + (f'; navíc {navic[:8]}' if navic else ''))

    if vysledky:
        _zkontroluj_vysledky(wb, kats, disciplina, jizd, hlidky, P, V)

    return {'problemy': P, 'varovani': V, 'info': I, 'pocty': pocty,
            'rozsah_stc': (min(vsechna_stc), max(vsechna_stc)) if vsechna_stc else None}


def _zkontroluj_vysledky(wb, kats, disciplina, jizd, hlidky, P, V):
    slalom = disciplina.startswith('slalom')
    for kat in kats:
        if not (wb.has(kat) and wb.has(f'{kat}_sl')):
            continue
        sl = wb.sheet(f'{kat}_sl').values(max_cols=16)
        by_id = {}
        for row in sl[2:]:
            row = list(row) + [None] * (16 - len(row))
            klic = row[15] if hlidky else row[2]
            if isinstance(row[0], float) and not _prazdne(klic) and klic != 0:
                by_id[int(row[0])] = row
        res = wb.sheet(kat).values(max_cols=18)
        ids = [int(r[0]) for r in res[2:] if r and isinstance(r[0], float)]
        dup = [i for i, c in Counter(ids).items() if c > 1]
        if dup:
            P.append(f'{kat}: duplicitní id ve výsledkovém listu {sorted(dup)[:10]} — Eskymo zdvojí závodníka')
        zadano = 0
        for r, row in enumerate(res[2:], start=3):
            row = list(row) + [None] * (18 - len(row))
            if not isinstance(row[0], float) or int(row[0]) not in by_id:
                continue
            stc = by_id[int(row[0])][1]
            ozn = f'{kat} ř.{r} (stč {int(stc) if isinstance(stc, float) else stc})'
            if slalom:
                behy = [(11, 12)] + ([(14, 15)] if jizd == 2 else [])
                for j, (tc, pc) in enumerate(behy, 1):
                    t, p = row[tc], row[pc]
                    if _prazdne(t):
                        P.append(f'{ozn}: {j}. jízda bez času i stavu (zapiš DNS)')
                        continue
                    zadano += 1
                    if stav_jizdy(t):
                        if p != 999:
                            V.append(f'{ozn}: {j}. jízda {t}, penalizace {p} (Eskymo čeká 999)')
                    elif isinstance(t, float):
                        if p is None or isinstance(p, str):
                            P.append(f'{ozn}: {j}. jízda čas {t} bez penalizace (zapiš 0)')
                        elif p not in (0, 999) and p % 2:
                            V.append(f'{ozn}: {j}. jízda penalizace {p} — lichý součet (0/2/50)?')
                    else:
                        P.append(f'{ozn}: {j}. jízda neznámá hodnota {t!r}')
            else:
                behy = [13] + ([16] if disciplina.startswith('sprint') and jizd == 2 else [])
                for j, c in enumerate(behy, 1):
                    t = row[c]
                    if _prazdne(t) or t == 0:
                        P.append(f'{ozn}: {j}. jízda prázdná — ve sjezdu/sprintu se prázdná buňka počítá '
                                 'jako čas 0 a skončí první')
                    elif isinstance(t, float) and t >= 0.0416:  # ≥ 59:59,99 = nezadáno
                        P.append(f'{ozn}: {j}. jízda nezadána (59:59,99)')
                    else:
                        zadano += 1
            if _je_chyba(row[2]):
                P.append(f'{ozn}: chyba v pořadí → {row[2]}')
        if by_id and not zadano:
            V.append(f'{kat}: žádný výsledek zatím není zadán')


def format_report(rep: dict, prepocet: str) -> str:
    L = [f'Přepočet: {prepocet}',
         'Počty ve startovkách: ' + ', '.join(f'{k} {n}' for k, n in rep['pocty'].items() if n)]
    if rep.get('rozsah_stc'):
        L.append(f"Startovní čísla: {rep['rozsah_stc'][0]}–{rep['rozsah_stc'][1]}")
    for title, key in (('PROBLÉMY', 'problemy'), ('VAROVÁNÍ', 'varovani'), ('INFO', 'info')):
        if rep[key]:
            L += ['', f'{title} ({len(rep[key])}):', *(f'  - {x}' for x in rep[key][:200])]
    if not rep['problemy']:
        L += ['', 'OK — žádné problémy.']
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ods')
    ap.add_argument('--plan')
    ap.add_argument('--lode')
    ap.add_argument('--vysledky', action='store_true')
    ap.add_argument('--cisla-v-kategorii', action='store_true')
    ap.add_argument('--bez-prepoctu', action='store_true', help='soubor už přepočítal člověk v Eskymu')
    a = ap.parse_args(argv)
    target, prepocet = a.ods, 'nepoužit (hodnoty uložené v souboru)'
    tmp = None
    if not a.bez_prepoctu:
        from recalc import recalc
        try:
            tmp = tempfile.mkdtemp(prefix='eskymo-verify-')
            target = recalc(a.ods, tmp)
            prepocet = 'LibreOffice headless (kopie)'
        except RuntimeError as e:
            prepocet = f'NEPROBĚHL ({e}) — kontroluji uložené hodnoty; platné jen pro soubor přepočítaný v Eskymu'
            target = a.ods
    plan = json.load(open(a.plan, encoding='utf-8')) if a.plan else None
    lode = None
    if a.lode:
        d = json.load(open(a.lode, encoding='utf-8'))
        lode = d['lode'] if isinstance(d, dict) else d
    rep = zkontroluj(target, plan, lode, a.vysledky, a.cisla_v_kategorii)
    print(format_report(rep, prepocet))
    if tmp:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return 1 if rep['problemy'] else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
