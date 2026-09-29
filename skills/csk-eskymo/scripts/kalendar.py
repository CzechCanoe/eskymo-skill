# -*- coding: utf-8 -*-
"""
kalendar — z odkazu na akci v kalendáři ČSK vyrobí zavod.json a tahák pro Eskymo „Nový závod“.

    python kalendar.py https://www.kanoe.cz/zavody/slalom-sjezd?link=7511 [-o zavod.json] [--tahak tahak.md]
    python kalendar.py 7511
    python kalendar.py rozpis.html          # uložená stránka (offline)

Zdroj: strukturovaný rozpis https://csk.kanoe.cz/extreq/kalendarcsk-show.php?s=2&a=<id>
(číslo závodu, druh + BHZ, datum, činovníci, startovné, pořad, vypsané kategorie).
Návrhy pro Eskymo (bodování, kategorie, pořadí startu) jsou ODVOZENÉ — pořadatel je
potvrzuje; skript označuje, co je jisté (`z rozpisu`) a co odhad (`odhad`).
Kontaktní údaje z rozpisu se neukládají.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36'
SHOW = 'https://csk.kanoe.cz/extreq/kalendarcsk-show.php?s=2&a={id}'
POLE = ['Pořadatel', 'Druh závodu', 'Datum závodu', 'Centrum, trať', 'Ředitel závodu', 'Delegát ČSK',
        'Vrchní rozhodčí', 'ZVR', 'Stavitel trati', 'Nejpozději do', 'On-line', 'Losování', 'Ceny']

# druh závodu → návrh bodování Body1..3 (odvozeno z dat a Směrnic — potvrdit)
BODOVANI = {'ČP': 'čp', 'NKZ': 'nkz', 'ČPž': 'čpž', 'ČPŽ': 'čpž', 'OČ': 'bhz-č', 'OM': 'bhz-m'}
VYPSANE = {  # (pohlaví, loď) z řádku „muži: K1, C1, C2 slalom“ → list Eskyma
    ('muži', 'K1'): 'k1m', ('muži', 'C1'): 'c1m', ('muži', 'C2'): 'c2m',
    ('ženy', 'K1'): 'k1z', ('ženy', 'C1'): 'c1z', ('ženy', 'C2'): 'c2z',
    ('mix', 'C2mi'): 'c2x', ('mix', 'C2'): 'c2x', ('mix', 'C2mix'): 'c2x',
}
KAT_TEXT = [(r'k1\s*m', 'k1m'), (r'k1\s*[žzw]', 'k1z'), (r'c1\s*m', 'c1m'), (r'c1\s*[žzw]', 'c1z'),
            (r'c2\s*mi', 'c2x'), (r'c2\s*m', 'c2m'), (r'c2\s*[žzw]', 'c2z'),
            (r'předžáci\s*k1|pž\s*k', 'pzk'), (r'předžáci\s*c1|pž\s*c', 'pzc')]


def akce_id(s: str) -> str:
    m = re.search(r'(?:[?&](?:link|a)=)(\d+)', s)
    if m:
        return m.group(1)
    if s.strip().isdigit():
        return s.strip()
    raise ValueError(f'nerozpoznám id akce v {s!r} (čekám odkaz ?link=… nebo a=…, nebo číslo)')


def stahni(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode('utf-8', errors='replace')


def _text(el) -> str:
    for br in el.xpath('.//br'):
        br.tail = '\n' + (br.tail or '')
    return re.sub(r'[ \t]+', ' ', el.text_content()).strip()


def parse(raw: str) -> dict:
    from lxml import html
    d = html.fromstring(raw)
    h1 = d.xpath('//h1')
    akce = (h1[0].text or '').strip() if h1 else ''
    small = h1[0].xpath('./small') if h1 else []
    termin = small[0].text_content().strip() if small else ''
    body = html.tostring(d, encoding='unicode')
    zavody = []
    for ch in re.split(r'<h3>\s*Propozice závodu č\.', body)[1:]:
        e = html.fromstring('<div>' + ch + '</div>')
        z = {'cislo': (re.match(r'\s*(\d*)', ch).group(1) or None)}
        h2 = e.xpath('.//h2')
        z['nazev'] = h2[0].text_content().strip() if h2 else ''
        for tr in e.xpath('.//tr'):
            tds = tr.xpath('./td')
            if len(tds) >= 2:
                lab = tds[0].text_content().strip().rstrip(':').strip()
                if lab in POLE and lab not in z:
                    z[lab] = _text(tds[1])
        for h4 in e.xpath('.//h4'):
            lab = h4.text_content().strip().rstrip(':')
            if lab == 'Pořad závodu':
                z['Pořad závodu'] = _text(h4.getparent()).replace('Pořad závodu:', '', 1).strip()
            elif lab == 'Startovné':
                sib = h4.getparent().getnext()
                z['Startovné'] = _text(sib) if sib is not None else ''
        z['vypsane'] = [re.sub(r'\s+', ' ', dv.text_content()).strip()
                        for dv in e.xpath('.//div[span[contains(@class,"font-weight-bold")]]')]
        m = re.match(r'(\S+)\s+(.*?),\s*BHZ:\s*(\d*)', z.get('Druh závodu', ''))
        if m:
            z['disciplina'], z['druh'], z['bhz'] = m.group(1), m.group(2).split(), (int(m.group(3)) if m.group(3) else None)
        m = re.search(r'propozice schváleny\s+([\d.]+)', ch)
        z['schvaleno'] = m.group(1) if m else None
        zavody.append(z)
    return {'akce': akce, 'termin': termin, 'zavody': zavody}


def navrh_eskymo(z: dict) -> dict:
    """Návrh parametrů pro dialog Nový závod. Každé pole má zdroj: rozpis / odhad."""
    disc = (z.get('disciplina') or '').lower()
    esk_disc = {'slalom': 'slalom', 'sjezd': 'sjezd', 'sprint': 'sprint'}.get(disc)
    body = [BODOVANI[d] for d in z.get('druh', []) if d in BODOVANI][:3]
    body += ['nic'] * (3 - len(body))
    kat = []
    for line in z.get('vypsane', []):
        m = re.match(r'(muži|ženy|mix)\s*:\s*(.*)', line)
        if not m:
            continue
        for tok in re.split(r'[,\s]+', m.group(2)):
            k = VYPSANE.get((m.group(1), tok))
            if k and k not in kat:
                kat.append(k)
    porad = (z.get('Pořad závodu') or '').lower()
    poradi = []
    m = re.search(r'pořadí kategorií\s*:?(.*)', porad, re.S)
    if m:
        for mm in re.finditer('|'.join(f'({p})' for p, _ in KAT_TEXT), m.group(1)):
            k = next(code for (p, code) in KAT_TEXT if re.fullmatch(p, mm.group(0)))
            if k not in poradi:
                poradi.append(k)
    for k in ('pzk', 'pzc'):
        if k in poradi and k not in kat:
            kat.append(k)
    jizd = 1 if re.search(r'jedn[aé] jízd|1 jízd', porad) else (2 if 'obě jízdy' in porad or esk_disc == 'slalom' else None)
    return {
        'nazev': {'hodnota': z.get('nazev'), 'zdroj': 'rozpis'},
        'misto': {'hodnota': z.get('Centrum, trať'), 'zdroj': 'rozpis (zkrátit na místo)'},
        'poradatel': {'hodnota': z.get('Pořadatel'), 'zdroj': 'rozpis'},
        'reditel': {'hodnota': z.get('Ředitel závodu'), 'zdroj': 'rozpis'},
        'vrchni_rozhodci': {'hodnota': z.get('Vrchní rozhodčí'), 'zdroj': 'rozpis'},
        'cislo': {'hodnota': z.get('cislo'), 'zdroj': 'rozpis'},
        'datum': {'hodnota': _ddmmyy(z.get('Datum závodu')), 'zdroj': 'rozpis'},
        'bhz': {'hodnota': z.get('bhz'), 'zdroj': 'rozpis'},
        'disciplina': {'hodnota': esk_disc or f'!! {disc} — Eskymo zná jen slalom/sjezd/sprint',
                       'zdroj': 'rozpis'},
        'body': {'hodnota': body, 'zdroj': 'odhad z druhu závodu — potvrdit (Směrnice, počtářka)'},
        'kategorie': {'hodnota': kat, 'zdroj': 'rozpis „vypsané disciplíny“ + předžáci z pořadu — potvrdit'},
        'poradi_startu': {'hodnota': poradi, 'zdroj': 'odhad z pořadu závodu — potvrdit'},
        'pocet_jizd': {'hodnota': jizd, 'zdroj': 'odhad z pořadu / disciplíny'},
        'hlidky': {'hodnota': 'ano' if re.search(r'hlídk|družstv', (z.get('nazev') or '').lower()) else 'ne',
                   'zdroj': 'odhad z názvu'},
        'st_casy': {'hodnota': 'ne', 'zdroj': 'výchozí — ano jen když se tisknou startovní časy'},
        'radek': {'hodnota': 150, 'zdroj': 'výchozí Eskyma; zvyš, čeká-li se v kategorii víc lodí'},
    }


def _ddmmyy(d):
    m = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})', d or '')
    return f'{int(m.group(1)):02d}.{int(m.group(2)):02d}.{m.group(3)[2:]}' if m else d


def tahak(data: dict) -> str:
    L = [f"# Nový závod v Eskymu — {data['akce']} ({data['termin']})", '',
         'Eskymo → Nový závod. Pole s * nejdou později změnit — zkontroluj je dvakrát.', '']
    for z in data['zavody']:
        e = z['eskymo']
        L.append(f"## Závod č. {z.get('cislo')} — {z.get('Datum závodu')} — {z.get('Druh závodu')}")
        L.append('| pole dialogu | hodnota | zdroj |')
        L.append('|---|---|---|')
        rows = [('název', 'nazev'), ('místo', 'misto'), ('pořadatel', 'poradatel'), ('ředitel', 'reditel'),
                ('vrchní rozhodčí', 'vrchni_rozhodci'), ('číslo', 'cislo'), ('disciplína *', 'disciplina'),
                ('datum', 'datum'), ('bhz', 'bhz'), ('st. časy', 'st_casy'), ('počet jízd', 'pocet_jizd'),
                ('bodování * (body1/2/3)', 'body'), ('kategorie *', 'kategorie'), ('#řádek *', 'radek'),
                ('hlídky *', 'hlidky')]
        for lab, key in rows:
            v = e[key]['hodnota']
            v = ', '.join(map(str, v)) if isinstance(v, list) else v
            L.append(f"| {lab} | {v if v not in (None, '') else '—'} | {e[key]['zdroj']} |")
        if e['poradi_startu']['hodnota']:
            L.append(f"\nPořadí kategorií na startu (pro startovku, ne pro dialog): "
                     f"{', '.join(e['poradi_startu']['hodnota'])}")
        L += ['', 'Po vytvoření: ulož sešit (např. `'
              f"{str(z.get('Datum závodu', ''))[-2:]}{int(z.get('cislo') or 0):03d}_nazev.ods`), "
              'Eskymo → Import registru, zkontroluj `param`: Prohlídka-zobrazit = ano (S26 §7b).', '']
    return '\n'.join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('zdroj', help='odkaz z kalendáře, id akce, nebo uložené HTML rozpisu')
    ap.add_argument('-o', '--out')
    ap.add_argument('--tahak')
    a = ap.parse_args(argv)
    if a.zdroj.lower().endswith(('.html', '.htm')):
        raw = open(a.zdroj, encoding='utf-8', errors='replace').read()
        src = a.zdroj
    else:
        src = SHOW.format(id=akce_id(a.zdroj))
        raw = stahni(src)
    data = parse(raw)
    data['zdroj'] = src
    if not data['zavody']:
        print(f'V rozpisu {src} jsem nenašel žádný závod (neplatné id?).', file=sys.stderr)
        return 1
    for z in data['zavody']:
        z['eskymo'] = navrh_eskymo(z)
    if a.out:
        json.dump(data, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    t = tahak(data)
    if a.tahak:
        open(a.tahak, 'w', encoding='utf-8').write(t)
    print(t)
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
