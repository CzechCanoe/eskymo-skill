# -*- coding: utf-8 -*-
"""
startovka — individuální startovní listiny: nasazení → plán → čísla → zápis do Eskyma.

Dva kroky, aby šlo nasazení zkontrolovat/upravit a čísla měnit bez nového losu:

  1) python startovka.py nasad lode.json zavod.ods -c nastaveni.json -o plan.json
       spočítá startovní pořadí v každé kategorii a u každé lodi uvede, PROČ je tam,
       kde je (sloupec „nasazeno podle“) — to pořadatel kontroluje.
  2) python startovka.py zapis plan.json zavod.ods vystup.ods [-c nastaveni.json]
       přidělí startovní čísla (cisla.py) a zapíše do `<kat>_sl` stč (B) a rgc (C)
       ve fyzickém pořadí startu. Nic jiného v sešitu nemění.

nastaveni.json (vše volitelné):
{
  "poradi_kategorii": ["k1m","c1z","c2m","pzk","c1m","pzc","k1z","c2x"],   // jinak pořadí listů
  "nasazeni": {
     "metoda": "vt-los",            // vt-los | zebricek | pevne | prihlaska | eskymo-los
     "smer": "nejslabsi-prvni",     // nejslabsi-prvni (Eskymo, obrácené žebříčky) | nejlepsi-prvni (P 2.17.01)
     "skupiny": "pravidla",         // pravidla: MT+1 | 2+ | 2 | 3+ | 3 | bez;  eskymo: MT | 1 | 2+ | …
     "seed": 20261003,              // los je reprodukovatelný; bez seedu se vygeneruje a uloží do plánu
     "zebricek": "zebricek.csv",    // kat;rgc;poradi  (C2: "rgc1 rgc2")
     "nezarazeni": "zacatek-vt-nejlepsi-prvni"   // | zacatek-vt-nejslabsi-prvni | konec
  },
  "kategorie": {"c2x": {"nasazeni": {"metoda": "prihlaska"}}},             // výjimky po kategoriích
  "cisla": {"rezim": "desitky", "start": 1, "mezera": 0, "vynechat": [], "max": null}
}
Metoda `eskymo-los` jen zapíše rgc (seřazené podle VT) bez čísel — losovat pak člověk
v Eskymu tlačítkem „Losování startovních čísel“ na každém listu `_sl`.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import random
import sys
from collections import Counter

import cisla as C
from domena import (KATEGORIE_NAZEV, VT_SKUPINY_ESKYMO, VT_SKUPINY_PRAVIDLA, VT_SKUPINY_PRAVIDLA4,
                    kategorie_eskymo, vt_rank, vt_skupina)
from eskymo_ods import Workbook, norm_rgc, rgc_cell_value
from inspect_workbook import read_param
from registr import Registr

VYCHOZI = {
    'nasazeni': {'metoda': 'vt-los', 'smer': 'nejslabsi-prvni', 'skupiny': 'pravidla',
                 'nezarazeni': 'zacatek-vt-nejlepsi-prvni'},
    'cisla': {'rezim': 'desitky', 'start': 1, 'mezera': 0, 'vynechat': [], 'max': None},
}


def _merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _klic(rgcs) -> str:
    return ' '.join(sorted(norm_rgc(r) for r in rgcs))


def nacti_zebricek(path: str) -> tuple[dict, list[str]]:
    """CSV kat;rgc;poradi (hlavička volitelná) → ({kat: {klic_lodi: poradi}}, varování).

    Řádky s neznámou kategorií nebo bez čísla pořadí se nezahazují potichu — jdou do varování.
    """
    raw = open(path, 'rb').read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1250')
    out: dict = {}
    varovani = []
    for i, row in enumerate(csv.reader(io.StringIO(text), delimiter=';'), start=1):
        if not any(c.strip() for c in row):
            continue
        if len(row) < 3 or not row[2].strip().rstrip('.').isdigit():
            if i > 1:  # 1. řádek bývá hlavička
                varovani.append(f'žebříček ř.{i}: bez čísla pořadí, vynechán: {";".join(row)[:60]}')
            continue
        kat = kategorie_eskymo(row[0])
        if not kat:
            varovani.append(f'žebříček ř.{i}: neznámá kategorie {row[0]!r} — řádek NEPOUŽIT')
            continue
        out.setdefault(kat, {})[_klic(row[1].split())] = int(row[2].strip().rstrip('.'))
    return out, varovani


def _poradi_kategorii(wb: Workbook, nast: dict, lode: list) -> list[str]:
    if nast.get('poradi_kategorii'):
        por = [kategorie_eskymo(k) or k for k in nast['poradi_kategorii']]
    else:
        por = [k['kod'].lower() for k in read_param(wb)['kategorie']]
    chybi = sorted({l['kat'] for l in lode} - set(por))
    if chybi:
        raise SystemExit(f'Kategorie {chybi} mají přihlášené lodě, ale nejsou v pořadí kategorií — doplň je.')
    return por


def nasad(lode: list[dict], wb: Workbook, nast: dict, i_s_problemy: bool = False) -> dict:
    reg = Registr.ze_sesitu(wb)
    param = read_param(wb)
    pole = {k: v['hodnota'] for k, v in param['pole'].items()}
    if str(pole.get('Hlídky', '')).strip().lower() == 'ano':
        raise SystemExit('Sešit je hlídkový (param Hlídky = ano) — startovku hlídek dělá hlidky.py.')
    for l in lode:
        if not l.get('rgc') or not l.get('kat'):
            raise SystemExit(f"Loď {l.get('zdroj') or l} nemá `kat` nebo `rgc` — lode.json musí být seznam lodí "
                             '(prihlasky.py); hlídky patří do hlidky.py.')
    disciplina = str(pole.get('Disciplína') or 'slalom')
    nast = _merge(VYCHOZI, nast)
    seed = nast['nasazeni'].get('seed')
    if seed is None:
        seed = random.SystemRandom().randrange(1, 10 ** 9)
    rnd = random.Random(seed)
    varovani = []
    _zeb_cache = {}

    def zebricek_pro(path):   # žebříček může být globální i jen pro jednu kategorii
        if path not in _zeb_cache:
            data, var = nacti_zebricek(path)
            _zeb_cache[path] = data
            varovani.extend(var)
        return _zeb_cache[path]

    # lodě s nevyřešenými problémy z kontroly přihlášek se nezapisují (prázdné jméno v Eskymu)
    nezapsano = []
    if not i_s_problemy:
        ok = []
        for l in lode:
            pr = (l.get('kontrola') or {}).get('problemy') or []
            if pr:
                nezapsano.append({'zdroj': l.get('zdroj'), 'kat': l['kat'], 'rgc': l['rgc'],
                                  'jmena': l.get('jmena', []), 'duvod': '; '.join(pr)})
            else:
                ok.append(l)
        lode = ok

    metody = {_merge(nast, nast.get('kategorie', {}).get(k, {}))['nasazeni']['metoda']
              for k in {l['kat'] for l in lode}}
    if 'eskymo-los' in metody and len(metody) > 1:
        raise SystemExit('Metodu eskymo-los nejde kombinovat s jinými: Eskymo čísluje každou kategorii od 1 '
                         'a čísla by kolidovala. Použij eskymo-los pro všechny kategorie, nebo vt-los.')

    plan = {'vytvoreno': dt.datetime.now().isoformat(timespec='seconds'),
            'zavod': {k: pole.get(k) for k in ('Název závodu', 'Datum závodu', 'Číslo závodu', 'Disciplína')},
            'nastaveni': nast, 'seed': seed, 'kategorie': [], 'varovani': varovani, 'nezapsano': nezapsano}

    for kat in _poradi_kategorii(wb, nast, lode):
        ls = [l for l in lode if l['kat'] == kat]
        if not ls:
            continue
        kn = _merge(nast, nast.get('kategorie', {}).get(kat, {}))['nasazeni']
        metoda, smer = kn['metoda'], kn['smer']
        skupiny = {'eskymo': VT_SKUPINY_ESKYMO, 'pravidla-4': VT_SKUPINY_PRAVIDLA4}.get(
            kn.get('skupiny'), VT_SKUPINY_PRAVIDLA)
        polozky = []
        for l in ls:
            osoby = [reg.get(r) for r in l['rgc']]
            vt = reg.vt_lode(l['rgc'], kat, disciplina)
            polozky.append({
                'rgc': l['rgc'],
                'jmeno': ' / '.join(o.cele_jmeno for o in osoby if o) or ' '.join(l.get('jmena', [])),
                'rok': ' / '.join(str(o.rok) for o in osoby if o and o.rok),
                'oddil': ' / '.join(dict.fromkeys(o.oddil for o in osoby if o)) or l.get('oddil', ''),
                'vt': vt, 'poradi_prihlasky': l.get('poradi'), 'poradi_start': l.get('poradi_start'),
                'stc': l.get('stc'), 'zdroj': l.get('zdroj'),
            })

        def vt_los(items, nejlepsi_prvni):
            gidx = sorted({vt_skupina(p['vt'], skupiny) for p in items}, reverse=not nejlepsi_prvni)
            out = []
            for g in gidx:
                grp = [p for p in items if vt_skupina(p['vt'], skupiny) == g]
                rnd.shuffle(grp)
                for p in grp:
                    p['duvod'] = f"VT {'/'.join(x or 'bez' for x in skupiny[g])} (los)"
                out += grp
            return out

        if metoda in ('vt-los', 'eskymo-los'):
            poradi = vt_los(polozky, smer == 'nejlepsi-prvni')
            if metoda == 'eskymo-los':
                for p in poradi:
                    p['duvod'] = 'los v Eskymu (tlačítko Losování)'
        elif metoda == 'zebricek':
            if not kn.get('zebricek'):
                raise SystemExit(f'{kat}: metoda „zebricek“ potřebuje soubor žebříčku (nasazeni.zebricek)')
            z = zebricek_pro(kn['zebricek']).get(kat, {})
            ranked = [p for p in polozky if _klic(p['rgc']) in z]
            unranked = [p for p in polozky if _klic(p['rgc']) not in z]
            if not ranked:
                raise SystemExit(f'{kat}: metoda „zebricek“, ale žádná přihlášená loď není v žebříčku '
                                 f'(v CSV pro {kat}: {len(z)} řádků) — zkontroluj kódy kategorií a RGC v žebříčku.')
            prihlaseni = {_klic(p['rgc']) for p in polozky}
            chybi = [k for k in z if k not in prihlaseni]
            if chybi:
                plan['varovani'].append(f'{kat}: {len(chybi)} lodí ze žebříčku není přihlášeno (např. {chybi[:5]}) '
                                        '— jen pro kontrolu úplnosti přihlášek.')
            plan['varovani'].append(f'{kat}: v žebříčku {len(ranked)} lodí, nezařazených {len(unranked)}.')
            ranked.sort(key=lambda p: z[_klic(p['rgc'])], reverse=(smer == 'nejslabsi-prvni'))
            for p in ranked:
                p['duvod'] = f"žebříček {z[_klic(p['rgc'])]}."
            nz = kn.get('nezarazeni', 'zacatek-vt-nejlepsi-prvni')
            if nz == 'konec':
                un = vt_los(unranked, True)
                for p in un:
                    p['duvod'] = 'nezařazen v žebříčku → ' + p['duvod']
                poradi = ranked + un
            else:
                un = vt_los(unranked, nz == 'zacatek-vt-nejlepsi-prvni')
                for p in un:
                    p['duvod'] = 'nezařazen v žebříčku → ' + p['duvod']
                poradi = un + ranked
        elif metoda == 'pevne':
            if any(p['poradi_start'] is None for p in polozky):
                raise SystemExit(f'{kat}: metoda „pevne“ potřebuje u každé lodi poradi_start')
            poradi = sorted(polozky, key=lambda p: p['poradi_start'])
            for p in poradi:
                p['duvod'] = f"zadané pořadí {p['poradi_start']}"
        elif metoda == 'prihlaska':
            poradi = sorted(polozky, key=lambda p: (p['poradi_prihlasky'] is None, p['poradi_prihlasky'] or 0))
            for p in poradi:
                p['duvod'] = 'pořadí v přihláškách'
        else:
            raise SystemExit(f'neznámá metoda nasazení {metoda!r}')
        plan['kategorie'].append({'kat': kat, 'metoda': metoda, 'smer': smer, 'lode': poradi})
    return plan


def dohlas(plan: dict, wb: Workbook, kat: str, rgc: list[str], stc: int, pozice: str = 'konec') -> dict:
    """Dohláška po zápisu: přidá loď s pevným číslem do uloženého plánu; ostatní čísla zůstanou.

    Pak znovu `zapis … --prepsat` s čísly v režimu `pevne`.
    """
    kat = kategorie_eskymo(kat) or kat
    reg = Registr.ze_sesitu(wb)
    osoby = [reg.get(r) for r in rgc]
    if not all(osoby):
        raise SystemExit(f'RGC {[r for r, o in zip(rgc, osoby) if not o]} není v reg/cizi — nejdřív Import registru '
                         'nebo doplnit cizince.')
    if any(p.get('stc') is None for kk in plan['kategorie'] for p in kk['lode']):
        raise SystemExit('V plánu chybí čísla — dohláška jde až po prvním `zapis` (ten čísla do plánu uloží).')
    k = next((x for x in plan['kategorie'] if x['kat'] == kat), None)
    if k is None:
        k = {'kat': kat, 'metoda': 'pevne', 'smer': '', 'lode': []}
        plan['kategorie'].append(k)
    if any(p.get('stc') == stc for p in k['lode']):
        raise SystemExit(f'Číslo {stc} už v kategorii {kat} je.')
    disc = str(plan['zavod'].get('Disciplína') or 'slalom')
    pol = {'rgc': [str(r) for r in rgc], 'jmeno': ' / '.join(o.cele_jmeno for o in osoby),
           'rok': ' / '.join(str(o.rok) for o in osoby if o.rok),
           'oddil': ' / '.join(dict.fromkeys(o.oddil for o in osoby)),
           'vt': reg.vt_lode(rgc, kat, disc), 'stc': stc, 'duvod': 'dohláška'}
    if pozice == 'zacatek':
        k['lode'].insert(0, pol)
    elif pozice.isdigit():
        k['lode'].insert(int(pozice) - 1, pol)
    else:
        k['lode'].append(pol)
    return plan


def _data_rows(sheet) -> list[int]:
    """Indexy řádků startovky s předgenerovaným id (řádek 3 = index 2 …)."""
    vals = sheet.values(max_cols=3)
    return [r for r in range(2, len(vals)) if vals[r] and isinstance(vals[r][0], float)]


def zapis(plan: dict, wb: Workbook, nast: dict, prepsat: bool = False) -> dict:
    nast = _merge(VYCHOZI, _merge(plan.get('nastaveni', {}), nast or {}))
    kats = [k for k in plan['kategorie'] if k['lode']]
    cn = nast['cisla']
    bez_cisel = all(k['metoda'] == 'eskymo-los' for k in kats)
    res = None
    if not bez_cisel:
        pevne = {k['kat']: [p.get('stc') for p in k['lode']] for k in kats} if cn['rezim'] == 'pevne' else None
        res = C.prirad([(k['kat'], len(k['lode'])) for k in kats], cn['rezim'], cn.get('start'),
                       int(cn.get('mezera') or 0), cn.get('vynechat') or [], int(cn.get('zarovnani') or 10),
                       cn.get('max'), pevne)
    upozorneni = []
    for k in kats:
        sh = wb.sheet(f"{k['kat']}_sl")
        rows = _data_rows(sh)
        if len(k['lode']) > len(rows):
            raise SystemExit(f"{k['kat']}_sl má jen {len(rows)} řádků (param #řádek) a lodí je {len(k['lode'])} "
                             '— v Eskymu založ sešit s vyšším #řádek.')
        obsazeno = [r for r in rows if sh.get(r, 1) not in (None, '') or sh.get(r, 2) not in (None, '', ' ')]
        if obsazeno and not prepsat:
            raise SystemExit(f"{k['kat']}_sl už obsahuje data ({len(obsazeno)} řádků). "
                             'Použij čistou šablonu, nebo --prepsat (smaže stč a rgc v celém listu).')
        if prepsat:
            for r in rows:
                for c in (1, 2):
                    if sh.get(r, c) not in (None, ''):
                        sh.set_input(r, c, None)
            pozn = [r + 1 for r in rows if sh.get(r, 10) not in (None, '')]
            if pozn:
                upozorneni.append(f"{k['kat']}_sl: poznámky (sl. K) na řádcích {pozn[:10]} zůstaly na místě — "
                                  'po přeřazení lodí je zkontroluj')
        for i, p in enumerate(k['lode']):
            r = rows[i]
            if res is not None and k['metoda'] != 'eskymo-los':
                p['stc'] = res['cisla'][k['kat']][i]
                sh.set_input(r, 1, p['stc'])
            sh.set_input(r, 2, rgc_cell_value(' '.join(p['rgc'])))
    return {'plan': plan, 'cisla': res, 'upozorneni': upozorneni}


def prehled(plan: dict) -> str:
    L = [f"# Startovka — {plan['zavod'].get('Název závodu')} ({plan['zavod'].get('Datum závodu')})",
         f"Seed losu: {plan['seed']}", '']
    for k in plan['kategorie']:
        L.append(f"## {k['kat'].upper()} — {KATEGORIE_NAZEV.get(k['kat'], '')} "
                 f"({len(k['lode'])} lodí; {k['metoda']}, {k['smer']})")
        L.append('| # | stč | jméno | ročník | oddíl | VT | nasazeno podle |')
        L.append('|---:|---:|---|---|---|---|---|')
        for i, p in enumerate(k['lode'], 1):
            L.append(f"| {i} | {p.get('stc') or ''} | {p['jmeno']} | {p['rok']} | {p['oddil']} | "
                     f"{p['vt'] or '—'} | {p.get('duvod', '')} |")
        L.append('')
    if plan.get('nezapsano'):
        L += ['## Nezapsáno (nevyřešené problémy z kontroly přihlášek)',
              *(f"- {x['kat']} {' '.join(x['rgc'])} {' '.join(x.get('jmena', []))} ({x.get('zdroj')}): {x['duvod']}"
                for x in plan['nezapsano']), '']
    if plan.get('varovani'):
        L += ['## Poznámky k nasazení', *(f'- {x}' for x in plan['varovani']), '']
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a1 = sub.add_parser('nasad')
    a1.add_argument('lode')
    a1.add_argument('sesit')
    a1.add_argument('-c', '--nastaveni')
    a1.add_argument('-o', '--out', required=True)
    a1.add_argument('--prehled', help='kam uložit přehled (Markdown)')
    a1.add_argument('--i-s-problemy', action='store_true',
                    help='nasadit i lodě s nevyřešenými PROBLÉMY z kontroly přihlášek (jinak se vynechají a vypíšou)')
    a3 = sub.add_parser('dohlas', help='dohláška po zápisu: přidá loď s pevným číslem do plánu')
    a3.add_argument('plan')
    a3.add_argument('sesit')
    a3.add_argument('--kat', required=True)
    a3.add_argument('--rgc', required=True, nargs='+', help='RGC (C2: dvě)')
    a3.add_argument('--stc', required=True, type=int)
    a3.add_argument('--pozice', default='konec', help='zacatek | konec | pořadí (1 = první startující)')
    a2 = sub.add_parser('zapis')
    a2.add_argument('plan')
    a2.add_argument('sesit')
    a2.add_argument('vystup')
    a2.add_argument('-c', '--nastaveni')
    a2.add_argument('--prepsat', action='store_true')
    a2.add_argument('--prehled')
    a = ap.parse_args(argv)
    nast = json.load(open(a.nastaveni, encoding='utf-8')) if getattr(a, 'nastaveni', None) else {}

    if a.cmd == 'dohlas':
        plan = dohlas(json.load(open(a.plan, encoding='utf-8')), Workbook(a.sesit), a.kat, a.rgc, a.stc, a.pozice)
        json.dump(plan, open(a.plan, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'Dohláška přidána do {a.plan}. Zapiš znovu: startovka.py zapis {a.plan} <sablona.ods> <vystup.ods> '
              '--prepsat -c <nastaveni.json s "cisla": {"rezim": "pevne"}>')
        return 0

    if a.cmd == 'nasad':
        data = json.load(open(a.lode, encoding='utf-8'))
        if isinstance(data, dict):
            data = data['lode']
        plan = nasad(data, Workbook(a.sesit), nast, a.i_s_problemy)
        for x in plan['nezapsano']:
            print(f"! NEZAPSÁNO {x['kat']} {' '.join(x['rgc'])} ({x.get('zdroj')}): {x['duvod']}", file=sys.stderr)
        for x in plan['varovani']:
            print(f'! {x}', file=sys.stderr)
        json.dump(plan, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        txt = prehled(plan)
        if a.prehled:
            open(a.prehled, 'w', encoding='utf-8').write(txt)
        print('\n'.join(f"{k['kat']}: {len(k['lode'])} lodí ({k['metoda']}) — "
                        + ', '.join(f'{d} {n}×' for d, n in Counter(
                            p['duvod'].split(' (')[0] for p in k['lode']).most_common(4))
                        for k in plan['kategorie']))
        print(f"seed {plan['seed']} → {a.out}")
        return 0

    plan = json.load(open(a.plan, encoding='utf-8'))
    wb = Workbook(a.sesit)
    try:
        res = zapis(plan, wb, nast, a.prepsat)
    except C.ChybaCisel as e:
        print(f'ČÍSLOVÁNÍ: {e}', file=sys.stderr)
        return 1
    wb.save(a.vystup)
    json.dump(res['plan'], open(a.plan, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if res['cisla']:
        print(C.popis(res['cisla'], [k['kat'] for k in plan['kategorie']]))
    for u in res['upozorneni']:
        print(f'! {u}')
    if a.prehled:
        open(a.prehled, 'w', encoding='utf-8').write(prehled(res['plan']))
    print(f'Zapsáno → {a.vystup}. Výsledky vzorců jsou zastaralé: ověř přes verify_workbook.py '
          '(přepočet LibreOffice), v Eskymu Ctrl+Shift+F9.')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
