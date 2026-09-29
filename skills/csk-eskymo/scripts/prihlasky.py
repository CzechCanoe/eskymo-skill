# -*- coding: utf-8 -*-
"""
prihlasky — normalizace přihlášek na seznam lodí (lode.json) a kontrola proti registru.

Dva vstupy, jeden výstup:
  1) CSV export z přihlašovacího systému ČSK (prihlasky.kanoe.cz, formát „Eskymo“):
       python prihlasky.py csv export.csv --sablona zavod.ods [--zavod 135] -o lode.json
  2) JSON lodí, který sestavil agent z volných přihlášek (e-maily, docx, xlsx):
       python prihlasky.py over lode.json --sablona zavod.ods -o lode.json

Formát lode.json (seznam lodí; povinné jen `kat` a `rgc`):
  {"kat": "k1m", "rgc": ["9162"], "jmena": ["NOVÁK Jan"], "rocniky": [2008],
   "oddil": "USK Praha", "vt": "2", "vk": "DS", "zavody": ["135"], "poznamka": "",
   "poradi": 12, "kod": "…", "zdroj": "csv:ř.13"}
  C2: "rgc": ["57036", "57054"]. Cizinec: "rgc": ["A90001"] (musí být v listu cizi).

Kontrola (--sablona) doplní ke každé lodi blok `kontrola` (údaje z registru)
a vypíše PROBLÉMY (musí vyřešit člověk) a VAROVÁNÍ (ověřit). Nic nehádá:
nejednoznačnosti jen hlásí, s kandidáty z registru.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict

from domena import (KATEGORIE_NAZEV, je_debl, kategorie_eskymo, klic_jmena,
                    vk_pro_rocnik)
from eskymo_ods import Workbook, norm_rgc
from registr import Registr


# ---------- čtení CSV exportu ----------
def _dekoduj(raw: bytes) -> str:
    for enc in ('utf-8-sig', 'cp1250'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode('cp1250', errors='replace')


def nacti_csv(path: str) -> list[dict]:
    text = _dekoduj(open(path, 'rb').read())
    rows = list(csv.reader(io.StringIO(text), delimiter=';'))
    if not rows:
        return []
    hdr = [h.strip().lower() for h in rows[0]]
    need = {'kategorie', 'rgc'}
    if not need <= set(hdr):
        raise ValueError(f'{path}: čekám hlavičku exportu ČSK (kategorie;rgc;jmeno;nar;oddil;vt;vk;…), '
                         f'mám {rows[0]}')
    lode = []
    for i, r in enumerate(rows[1:], start=2):
        if not any(c.strip() for c in r):
            continue
        d = {h: (r[j].strip() if j < len(r) else '') for j, h in enumerate(hdr)}
        rgcs = [norm_rgc(x) for x in d.get('rgc', '').split()]
        lode.append({
            'kat': kategorie_eskymo(d.get('kategorie', '')),
            'kat_vstup': d.get('kategorie', ''),
            'rgc': rgcs,
            'jmena': [d.get('jmeno', '')] if d.get('jmeno') else [],
            'rocniky': [int(x) for x in d.get('nar', '').split() if x.isdigit()],
            'oddil': d.get('oddil', ''),
            'vt': d.get('vt', ''),
            'vk': d.get('vk', ''),
            'zavody': re.findall(r'\d+', d.get('zavody', '')),
            'poznamka': d.get('poznamky', ''),
            'poradi': int(d['poradi']) if d.get('poradi', '').isdigit() else None,
            'kod': d.get('kod', ''),
            'zeme': d.get('zeme', ''),
            'zdroj': f'csv:ř.{i}',
        })
    return lode


# ---------- kontrola ----------
def _sezona_ze_sesitu(wb: Workbook) -> int | None:
    try:
        from inspect_workbook import read_param
        d = read_param(wb)['pole'].get('Datum závodu', {}).get('hodnota')
        m = re.search(r'(\d{2})\s*$', str(d or ''))
        return 2000 + int(m.group(1)) if m else None
    except Exception:
        return None


def over(lode: list[dict], wb: Workbook, zavod: str | None = None, sezona: int | None = None) -> dict:
    """Doplní `kontrola` ke každé lodi, přeřadí předžáky, vrátí souhrn problémů."""
    reg = Registr.ze_sesitu(wb)
    names = set(wb.sheet_names())
    disciplina = 'slalom'
    try:
        from inspect_workbook import read_param
        disciplina = str(read_param(wb)['pole'].get('Disciplína', {}).get('hodnota') or 'slalom')
    except Exception:
        pass
    sezona = sezona or _sezona_ze_sesitu(wb)
    problemy, varovani, info = [], [], []
    vyrazene = []
    out = []

    for lod in lode:
        ref = lod.get('zdroj') or f"{lod.get('kat_vstup') or lod.get('kat')} {' '.join(lod.get('rgc', []))}"
        k = {'problemy': [], 'varovani': []}
        lod['kontrola'] = k

        if zavod and lod.get('zavody') and str(zavod) not in lod['zavody']:
            vyrazene.append(lod)
            continue

        kat = lod.get('kat') or kategorie_eskymo(lod.get('kat_vstup', ''))
        if not kat:
            k['problemy'].append(f"neznámá kategorie {lod.get('kat_vstup')!r}")
        lod['kat'] = kat
        rgcs = [norm_rgc(x) for x in lod.get('rgc', []) if norm_rgc(x)]
        lod['rgc'] = rgcs
        if not rgcs:
            k['problemy'].append('chybí RGC')
        if kat and je_debl(kat) and len(rgcs) != 2:
            k['problemy'].append(f'deblová kategorie, ale {len(rgcs)} RGC')
        if kat and not je_debl(kat) and len(rgcs) > 1:
            k['problemy'].append(f'singl, ale {len(rgcs)} RGC')

        osoby = []
        jmena_vstup = ' '.join(lod.get('jmena', []))
        for i, r in enumerate(rgcs):
            o = reg.get(r)
            if not o:
                kand = []
                if jmena_vstup:
                    for token in klic_jmena(jmena_vstup).split():
                        kand += reg.hledej(token)
                msg = f'RGC {r} není v {"cizi" if r.startswith("A") else "reg"}'
                if kand:
                    msg += '; kandidáti podle jména: ' + ', '.join(
                        f'{c.rgc} {c.cele_jmeno} {c.rok} {c.oddil}' for c in kand[:4])
                k['problemy'].append(msg)
                osoby.append(None)
                continue
            osoby.append(o)
            if jmena_vstup and klic_jmena(o.prijmeni) not in klic_jmena(jmena_vstup):
                k['varovani'].append(f'RGC {r} patří {o.cele_jmeno} ({o.rok}, {o.oddil}), '
                                     f'přihláška uvádí „{jmena_vstup}“ — překlep v RGC nebo ve jméně?')
            roky = lod.get('rocniky') or []
            if i < len(roky) and o.rok and roky[i] and int(roky[i]) != o.rok:
                k['varovani'].append(f'RGC {r}: ročník v přihlášce {roky[i]}, v registru {o.rok}')
            if o.prohlidka is False:
                k.setdefault('info', []).append(f'{o.cele_jmeno}: bez platné lékařské prohlídky (Eskymo ukáže #)')

        platne = [o for o in osoby if o]
        if platne and kat:
            k['jmena_reg'] = [o.cele_jmeno for o in platne]
            k['rocniky_reg'] = [o.rok for o in platne]
            k['oddil_reg'] = ' / '.join(dict.fromkeys(o.oddil for o in platne))
            k['vt_reg'] = reg.vt_lode(rgcs, kat, disciplina)
            if lod.get('vt') and k['vt_reg'] != str(lod['vt']).replace(' ', '').upper():
                k['varovani'].append(f"VT v přihlášce {lod['vt']!r}, v registru {k['vt_reg'] or 'bez VT'!r} "
                                     '(platí registr)')
            # předžáci přihlášení v běžné K1/C1
            if kat in ('k1m', 'k1z', 'c1m', 'c1z') and sezona:
                if all(o.rok and vk_pro_rocnik(o.rok, sezona) == 'PZ' for o in platne):
                    cil = 'pzk' if kat.startswith('k') else 'pzc'
                    if f'{cil}_sl' in names:
                        lod['kat_puvodni'] = kat
                        lod['kat'] = kat = cil
                        k['varovani'].append(f'předžák → přesunuto do {cil}')
                    else:
                        k['varovani'].append(f'předžák v {kat}, ale sešit nemá list {cil}_sl — rozhodne pořadatel')
            # pohlaví vs. kategorie (Eskymo: pohlaví 't' = muž)
            if kat in ('k1z', 'c1z', 'c2z') and any(o.pohlavi == 't' for o in platne if not o.cizinec):
                k['problemy'].append('muž v ženské kategorii')
            if kat in ('k1m', 'c1m') and any(o.pohlavi and o.pohlavi != 't' for o in platne if not o.cizinec):
                k['varovani'].append('žena v mužské kategorii — smí jen když se ženská kategorie nekoná (P 2.39.04)')

        if kat and f'{kat}_sl' not in names:
            k['problemy'].append(f'sešit nemá list {kat}_sl (kategorie nebyla zvolena v Nový závod)')

        for p in k['problemy']:
            problemy.append(f'{ref}: {p}')
        for v in k['varovani']:
            varovani.append(f'{ref}: {v}')
        for v in k.get('info', []):
            info.append(f'{ref}: {v}')
        out.append(lod)

    # duplicity a víc partnerů v C2
    by_kat = defaultdict(list)
    for lod in out:
        by_kat[lod['kat']].append(lod)
    for kat, ls in by_kat.items():
        c = Counter(tuple(sorted(l['rgc'])) for l in ls)
        for key, n in c.items():
            if n > 1 and key:
                problemy.append(f'{kat}: loď {" ".join(key)} je přihlášená {n}×')
        if kat and je_debl(kat):
            partneri = defaultdict(set)
            for l in ls:
                for r in l['rgc']:
                    partneri[r].add(tuple(sorted(l['rgc'])))
            for r, s in partneri.items():
                if len(s) > 1:
                    problemy.append(f'{kat}: {r} jede ve {len(s)} různých posádkách (P 2.39.05)')
    # počet individuálních startů na osobu
    starty = Counter(r for l in out for r in l['rgc'])
    for r, n in starty.items():
        if n > 3:
            o = reg.get(r)
            info.append(f'{r} {o.cele_jmeno if o else ""}: {n} startů (MČR/ČP/NKZ max. 3 individuální, P 2.39.03)')

    souhrn = {
        'sezona': sezona, 'disciplina': disciplina, 'lodi': len(out),
        'po_kategoriich': dict(Counter(l['kat'] for l in out)),
        'vyrazeno_jiny_zavod': len(vyrazene),
        'problemy': problemy, 'varovani': varovani, 'info': info,
    }
    return {'lode': out, 'souhrn': souhrn}


def report(s: dict) -> str:
    L = [f"Lodí: {s['lodi']}  (sezóna {s['sezona']}, disciplína {s['disciplina']})"]
    for k, n in sorted(s['po_kategoriich'].items(), key=lambda x: str(x[0])):
        L.append(f'  {k or "?":<4} {KATEGORIE_NAZEV.get(k, "?"):<14} {n}')
    if s['vyrazeno_jiny_zavod']:
        L.append(f"Vyřazeno (přihlášeni na jiný závod akce): {s['vyrazeno_jiny_zavod']}")
    for title, key in (('PROBLÉMY — vyřeší pořadatel', 'problemy'), ('VAROVÁNÍ — ověřit', 'varovani'),
                       ('INFO', 'info')):
        if s[key]:
            L += ['', f'{title} ({len(s[key])}):', *(f'  - {x}' for x in s[key])]
    if not s['problemy']:
        L += ['', 'Bez problémů, které by bránily zápisu.']
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('csv', help='načti CSV export z přihlašovacího systému')
    a1.add_argument('csv')
    a2 = sub.add_parser('over', help='zkontroluj lode.json proti registru')
    a2.add_argument('json')
    for a in (a1, a2):
        a.add_argument('--sablona', help='Eskymo sešit s naimportovaným registrem (reg)')
        a.add_argument('--zavod', help='číslo závodu — ponechá jen lodě přihlášené na tento závod')
        a.add_argument('--sezona', type=int, help='rok závodu (jinak z param Datum závodu)')
        a.add_argument('-o', '--out', help='výstupní lode.json')
    a = ap.parse_args(argv)

    lode = nacti_csv(a.csv) if a.cmd == 'csv' else json.load(open(a.json, encoding='utf-8'))
    if isinstance(lode, dict):
        lode = lode.get('lode', [])
    if a.sablona:
        res = over(lode, Workbook(a.sablona), a.zavod, a.sezona)
        print(report(res['souhrn']))
        data = res
        rc = 1 if res['souhrn']['problemy'] else 0
    else:
        data = {'lode': lode, 'souhrn': {'lodi': len(lode)}}
        print(f'Načteno {len(lode)} lodí (bez kontroly — přidej --sablona).')
        rc = 0
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    return rc


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
