# -*- coding: utf-8 -*-
"""
casy — výsledky jízd z libovolného podkladu do Eskyma (bez Canoe123).

Vstup: CSV (`;` nebo `,`, UTF-8 nebo cp1250) s hlavičkou. Povinné sloupce kat, stc, jizda
a buď `cas` (+ volitelně `pen`), nebo `start` a `cil`; volitelně `stav`.
  kat   k1m / K1W / C1Ž …          stc   startovní číslo       jizda  1 | 2
  cas   čistý čas: 95.23 | 95,23 | 1:35.23 | 1:35,23       pen    0 / 2 / 50 … (slalom)
  start, cil   denní čas 10:02:15,32 (cíl < start = přes hodinu)
  stav  DNS | DNS-A | DNS-B | DNF | DSQ-R | DSQ-C  (má přednost před časem)

Režimy:
  python casy.py zapis casy.csv zavod.ods vystup.ods [--dns-chybejici]
      zapíše přímo do výsledkových listů `<kat>`: slalom L/M (1. jízda), O/P (2. jízda) —
      čas v sekundách a trestné body, stav jako text + 999; sjezd/sprint N (1.) a Q (2.)
      jako hodnota času, stav jako text. Řádek hledá přes stč → id ve `<kat>_sl` → id
      ve výsledkovém listu (funguje i po seřazení v Eskymu).
  python casy.py eskymo casy.csv casy_eskymo.txt
      vyrobí soubor pro Eskymo „Natažení časů ze souboru“ (kat;stc;jizda;start;cil, jen řádky
      se startem a cílem). Trestné body a stavy pak člověk zadá v Eskymu (formulář Výsledek).

Invariant: každá jízda zapsaného závodníka má čas, nebo stav. Chybějící jízdy skript vypíše;
s --dns-chybejici je doplní jako DNS (jen když to pořadatel potvrdil).
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys

from domena import kategorie_eskymo, stav_jizdy
from eskymo_ods import Workbook
from inspect_workbook import read_param

SLALOM_SL = {1: (11, 12), 2: (14, 15)}   # L/M, O/P
SJEZD_SL = {1: 13, 2: 16}                 # N, Q


def parse_cas(s) -> float | None:
    """'95.23' | '95,23' | '1:35.23' | '1:35,23' | '0:01:35,23' → sekundy."""
    if s is None:
        return None
    t = str(s).strip().replace(',', '.')
    if not t:
        return None
    parts = t.split(':')
    try:
        sec = float(parts[-1])
        mult = 60
        for p in reversed(parts[:-1]):
            sec += int(p) * mult
            mult *= 60
        return round(sec, 3)
    except ValueError:
        return None


def parse_denni(s) -> float | None:
    """'10:02:15,32' → sekundy od půlnoci."""
    return parse_cas(s)


def nacti(path: str) -> list[dict]:
    raw = open(path, 'rb').read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1250')
    delim = ';' if text.count(';') >= text.count(',') else ','
    rows = list(csv.DictReader(io.StringIO(text), delimiter=delim))
    out = []
    for i, r in enumerate(rows, start=2):
        r = {(k or '').strip().lower(): (v or '').strip() for k, v in r.items()}
        kat = kategorie_eskymo(r.get('kat') or r.get('kategorie') or '')
        stc = r.get('stc') or r.get('stč') or r.get('bib')
        jizda = int(r.get('jizda') or r.get('jízda') or 1)
        stav = stav_jizdy(r.get('stav') or r.get('cas') or '')
        cas = None if stav else parse_cas(r.get('cas') or r.get('čas'))
        start, cil = parse_denni(r.get('start')), parse_denni(r.get('cil') or r.get('cíl'))
        if cas is None and not stav and start is not None and cil is not None:
            d = cil - start
            cas = round(d + 3600 if d < 0 else d, 2)
        pen = r.get('pen') or r.get('penalizace') or ''
        out.append({'radek': i, 'kat': kat, 'stc': int(float(stc)) if stc else None, 'jizda': jizda,
                    'cas': cas, 'pen': int(float(pen)) if pen.strip() else None, 'stav': stav,
                    'start': r.get('start'), 'cil': r.get('cil') or r.get('cíl')})
    return out


def zapis(zaznamy: list[dict], wb: Workbook, dns_chybejici=False) -> dict:
    pole = {k: v['hodnota'] for k, v in read_param(wb)['pole'].items()}
    disc = str(pole.get('Disciplína') or 'slalom').strip().lower()
    slalom = disc.startswith('slalom')
    jizd = int(float(pole.get('Počet jízd') or 2))
    problemy, zapsano = [], 0
    mapy = {}

    def mapa(kat):
        if kat not in mapy:
            sl = wb.sheet(f'{kat}_sl').values(max_cols=16)
            # obsazený řádek: rgc v C (individuál) nebo H-RGC v P (hlídky, C je tam vzorec)
            stc2id = {int(r[1]): int(r[0]) for r in (x + [None] * 16 for x in sl[2:])
                      if isinstance(r[0], float) and isinstance(r[1], float)
                      and (r[2] not in (None, '', ' ', 0.0) or r[15] not in (None, ''))}
            res = wb.sheet(kat).values(max_cols=1)
            id2row = {int(r[0]): i for i, r in enumerate(res) if i >= 2 and r and isinstance(r[0], float)}
            mapy[kat] = (stc2id, id2row)
        return mapy[kat]

    for z in zaznamy:
        ozn = f"ř.{z['radek']} {z['kat']} stč {z['stc']} {z['jizda']}. jízda"
        if not z['kat'] or not wb.has(z['kat']):
            problemy.append(f'{ozn}: neznámá kategorie nebo chybí list')
            continue
        if z['jizda'] not in (1, 2) or z['jizda'] > jizd:
            problemy.append(f'{ozn}: sešit má {jizd} jízd(y)')
            continue
        stc2id, id2row = mapa(z['kat'])
        if z['stc'] not in stc2id:
            problemy.append(f'{ozn}: stč není ve startovce')
            continue
        row = id2row.get(stc2id[z['stc']])
        if row is None:
            problemy.append(f'{ozn}: id {stc2id[z["stc"]]} chybí ve výsledkovém listu')
            continue
        sh = wb.sheet(z['kat'])
        if z['stav'] is None and z['cas'] is None:
            problemy.append(f'{ozn}: ani čas, ani stav')
            continue
        if slalom:
            tc, pc = SLALOM_SL[z['jizda']]
            if z['stav']:
                sh.set_input(row, tc, z['stav'])
                sh.set_input(row, pc, 999)
            else:
                sh.set_input(row, tc, round(z['cas'], 2))
                sh.set_input(row, pc, z['pen'] if z['pen'] is not None else 0)
        else:
            c = SJEZD_SL[z['jizda']]
            if z['stav']:
                sh.set(row, c, z['stav'])
            else:
                sh.set(row, c, round(z['cas'], 2) / 86400.0)   # hodnota času (zlomek dne)
        zapsano += 1

    # invariant: každá jízda zapsaného závodníka má čas nebo stav
    chybi = []
    for kat, (stc2id, id2row) in mapy.items():
        sh = wb.sheet(kat)
        for stc, i in stc2id.items():
            r = id2row.get(i)
            if r is None:
                continue
            behy = [1, 2][:jizd] if (slalom or disc.startswith('sprint')) else [1]
            for j in behy:
                c = SLALOM_SL[j][0] if slalom else SJEZD_SL[j]
                v = sh.get(r, c)
                if v in (None, '') or (not slalom and isinstance(v, float) and v >= 0.0416):
                    if dns_chybejici:
                        sh.set(r, c, 'DNS')
                        if slalom:
                            sh.set_input(r, SLALOM_SL[j][1], 999)
                    else:
                        chybi.append(f'{kat} stč {stc} {j}. jízda')
    return {'zapsano': zapsano, 'problemy': problemy, 'chybi': chybi}


def eskymo_soubor(zaznamy: list[dict], out: str) -> int:
    n = 0
    with open(out, 'w', encoding='cp1250', newline='\r\n') as f:
        for z in zaznamy:
            if z['kat'] and z['stc'] and z['start'] and z['cil'] and not z['stav']:
                f.write(f"{z['kat']};{z['stc']};{z['jizda']};{_hms(z['start'])};{_hms(z['cil'])}\n")
                n += 1
    return n


def _hms(s: str) -> str:
    """Eskymo čte HH:MM:SS,ccc a hodiny zahazuje — sjednotit tvar."""
    sec = parse_denni(s)
    h, rem = divmod(sec, 3600)
    m, rem = divmod(rem, 60)
    return f'{int(h):02d}:{int(m):02d}:{rem:06.3f}'.replace('.', ',')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('zapis'); a1.add_argument('csv'); a1.add_argument('sesit'); a1.add_argument('vystup')
    a1.add_argument('--dns-chybejici', action='store_true')
    a2 = sub.add_parser('eskymo'); a2.add_argument('csv'); a2.add_argument('vystup')
    a = ap.parse_args(argv)
    zaz = nacti(a.csv)
    if a.cmd == 'eskymo':
        n = eskymo_soubor(zaz, a.vystup)
        print(f'{n} řádků → {a.vystup}. V Eskymu: ikona „Natažení časů ze souboru“, pak zadej trestné body a stavy.')
        return 0
    wb = Workbook(a.sesit)
    res = zapis(zaz, wb, a.dns_chybejici)
    wb.save(a.vystup)
    print(f"Zapsáno {res['zapsano']} jízd → {a.vystup}")
    for p in res['problemy']:
        print(f'  ! {p}')
    if res['chybi']:
        print(f"Bez času i stavu ({len(res['chybi'])}) — doplň, nebo potvrď DNS a spusť s --dns-chybejici:")
        for c in res['chybi'][:50]:
            print(f'  - {c}')
    return 1 if res['problemy'] else 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
