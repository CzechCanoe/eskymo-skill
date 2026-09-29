# -*- coding: utf-8 -*-
"""
inspect_workbook — první krok před jakoukoli prací s Eskymo sešitem.

    python inspect_workbook.py zavod.ods [--json]

Vypíše verzi Eskyma, parametry závodu z listu `param` (s adresami buněk),
tabulku kategorií, typy listů, stav registru a cizinců, zaplnění startovek
a výsledků, a VAROVÁNÍ na známé problémy šablon:
  * prázdný `reg` (neproběhl Import registru),
  * kategorie v `param` bez listů / listy bez kategorie,
  * překlep `uuper(` ve vzorcích (list `hlidky`),
  * duplicitní `id` ve výsledkovém listu (zbytek šablony → zdvojení závodníka),
  * sešit, který není z Eskyma (např. cross šablony bez `param`).
Nic nezapisuje.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter

from eskymo_ods import Workbook, col_letter

SPECIAL = {'param', 'reg', 'cizi', 'hlidky'}


def read_param(wb: Workbook) -> dict:
    """Páry popisek→hodnota z listu param (sloupce A/B a C/D) + tabulka kategorií."""
    p = wb.sheet('param')
    grid = p.values(max_rows=80, max_cols=6)
    out = {'verze_text': grid[0][0] if grid and grid[0] else None, 'pole': {}, 'kategorie': []}
    m = re.search(r'(\d+\.\d+(?:\.\d+)?)', str(out['verze_text'] or ''))
    out['verze'] = m.group(1) if m else None
    hdr, v_tabulce = None, False
    for r, row in enumerate(grid):
        if hdr is None and row and isinstance(row[0], str) and row[0].strip().lower() == 'kategorie':
            hdr, v_tabulce = row, True
            continue
        if v_tabulce:
            if row and row[0]:
                out['kategorie'].append({
                    'kod': str(row[0]).strip(),
                    'nazev': row[1] if len(row) > 1 else None,
                    'radek': r + 1,
                    'dalsi': {str(hdr[i]): row[i] for i in range(2, min(len(hdr), len(row))) if hdr[i]},
                })
                continue
            v_tabulce = False
        for a, b in ((0, 1), (2, 3)):
            if len(row) > a and isinstance(row[a], str) and row[a].strip().endswith(':'):
                label = row[a].strip().rstrip(':').strip()
                val = row[b] if len(row) > b else None
                out['pole'].setdefault(label, {'hodnota': val, 'bunka': f'{col_letter(b)}{r + 1}'})
    return out


def _count_filled(values, col, start_row):
    return sum(1 for row in values[start_row:] if len(row) > col and row[col] not in (None, '', ' '))


def inspect(path: str) -> dict:
    wb = Workbook(path)
    names = wb.sheet_names()
    rep = {'soubor': path, 'listy': names, 'varovani': [], 'info': []}
    if 'param' not in names:
        rep['typ'] = 'neeskymovsky'
        rep['varovani'].append('Sešit nemá list `param` — není to sešit vygenerovaný Eskymem '
                               '(např. cross šablona). Pracuj podle references/vysledky-cross.md.')
        return rep
    rep['typ'] = 'eskymo'
    param = read_param(wb)
    rep['param'] = param
    pole = {k: v['hodnota'] for k, v in param['pole'].items()}
    rep['hlidky'] = str(pole.get('Hlídky', '')).strip().lower() == 'ano'
    rep['disciplina'] = pole.get('Disciplína')
    rep['pocet_jizd'] = pole.get('Počet jízd')

    # registr a cizinci
    for sh in ('reg', 'cizi'):
        if sh in names:
            n = max(0, len([r for r in wb.sheet(sh).values(max_cols=2) if r and r[0] not in (None, '')]) - 1)
            rep[f'{sh}_zaznamu'] = n
    if rep.get('reg_zaznamu', 0) < 100:
        rep['varovani'].append(f"List `reg` má jen {rep.get('reg_zaznamu', 0)} záznamů — v Eskymu nejdřív "
                               'proveď Eskymo → Import registru a sešit ulož.')

    # kategorie vs listy
    kat = [k['kod'].lower() for k in param['kategorie']]
    rep['kategorie'] = []
    data_sheets = [n for n in names if n not in SPECIAL and not n.endswith('_sl')]
    for k in kat:
        info = {'kod': k, 'vysledky': k in names, 'startovka': f'{k}_sl' in names}
        if f'{k}_sl' in names:
            v = wb.sheet(f'{k}_sl').values(max_cols=16)
            info['startovka_radku'] = sum(1 for row in v[2:] if row and isinstance(row[0], float))
            info['startovka_vyplneno'] = _count_filled(v, 2, 2) if not rep['hlidky'] else _count_filled(v, 15, 2)
            info['stc_vyplneno'] = _count_filled(v, 1, 2)
        if k in names:
            v = wb.sheet(k).values(max_cols=20)
            ids = [row[0] for row in v[2:] if row and isinstance(row[0], float)]
            info['vysledky_radku'] = len(ids)
            dup = [i for i, c in Counter(ids).items() if c > 1]
            if dup:
                rep['varovani'].append(f'List `{k}`: duplicitní id {sorted(int(d) for d in dup)[:10]} '
                                       '— Eskymo by zdvojilo závodníka (zbytek šablony). Před plněním přečísluj.')
        if not info['vysledky'] or not info['startovka']:
            rep['varovani'].append(f'Kategorie `{k}` je v param, ale chybí list '
                                   f"{'`' + k + '`' if not info['vysledky'] else ''} "
                                   f"{'`' + k + '_sl`' if not info['startovka'] else ''}".rstrip())
        rep['kategorie'].append(info)
    for n in data_sheets:
        if n.lower() not in kat:
            rep['info'].append(f'List `{n}` nemá řádek v tabulce kategorií na `param`.')

    # známé chyby vzorců
    uuper = 0
    for n in names:
        for row in wb.sheet(n).values(max_rows=400, max_cols=60, formulas=True):
            uuper += sum(1 for v in row if isinstance(v, str) and 'uuper(' in v)
    if uuper:
        rep['varovani'].append(f'Šablona obsahuje {uuper}× překlep `uuper(` ve vzorcích (VT u C2 hlídek → #NAME?). '
                               'Oprav na kopii přes Workbook.patch_formulas("uuper(", "UPPER(") a řekni to pořadateli.')
    return rep


def format_report(rep: dict) -> str:
    L = [f"Soubor: {rep['soubor']}", f"Listy: {', '.join(rep['listy'])}"]
    if rep['typ'] != 'eskymo':
        L += ['', *('! ' + v for v in rep['varovani'])]
        return '\n'.join(L)
    p = rep['param']
    L.append(f"Eskymo verze: {p['verze'] or '?'}   hlídky: {'ano' if rep['hlidky'] else 'ne'}   "
             f"disciplína: {rep['disciplina']}   jízd: {rep['pocet_jizd']}")
    L.append(f"reg: {rep.get('reg_zaznamu', '—')} záznamů   cizi: {rep.get('cizi_zaznamu', '—')} záznamů")
    L.append('')
    L.append('Parametry (param):')
    for k, v in p['pole'].items():
        if v['hodnota'] not in (None, '', ' '):
            L.append(f"  {v['bunka']:>4}  {k}: {v['hodnota']}")
    L.append('')
    L.append('Kategorie (pořadí dle param):')
    for k in rep['kategorie']:
        s = f"  {k['kod']:<5} listy: {'V' if k['vysledky'] else '-'}{'S' if k['startovka'] else '-'}"
        if 'startovka_vyplneno' in k:
            s += f"   startovka: {k['startovka_vyplneno']}/{k['startovka_radku']} vyplněno, stč u {k['stc_vyplneno']}"
        L.append(s)
    if rep['info']:
        L += ['', *('i ' + v for v in rep['info'])]
    if rep['varovani']:
        L += ['', 'VAROVÁNÍ:', *('! ' + v for v in rep['varovani'])]
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ods')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    rep = inspect(a.ods)
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_report(rep))
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
