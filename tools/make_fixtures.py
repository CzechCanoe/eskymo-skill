# -*- coding: utf-8 -*-
"""
make_fixtures — vyrobí ANONYMNÍ testovací data do tests/fixtures z reálných Eskymo šablon.

    python tools/make_fixtures.py --slalom <prazdna_sablona_individual.ods> --hlidky <prazdna_hlidkova.ods>

Reálné šablony obsahují celý registr ČSK (jména, ročníky, nezletilí, zdravotní prohlídky),
funkcionáře a interní klíč registru — do veřejného repa nesmí. Z šablony se ponechají jen
listy a vzorce Eskyma; nahradí se:
  - `reg`  → syntetický registr (smyšlená jména, RGC s prefixem čísla oddílu, reálné
             zkratky oddílů z Přílohy 3 Směrnic — ty jsou veřejné), deterministicky (seed);
  - `cizi` → dva smyšlení cizinci;
  - `param` → smyšlený název, místo, činovníci, datum; adresa registru → REDACTED;
  - meta.xml autoři, náhled Thumbnails, text záhlaví/patičky ve styles.xml.
Na konci kontrola: v žádné části výstupu se nesmí objevit příjmení ani RGC z původního registru
(kromě těch, která jsou náhodou i v syntetickém seznamu jmen).

Vyrobí taky syntetické vstupy navázané na stejný registr: prihlasky.csv (export ČSK, cp1250),
canoe123.xml, loni_hlidky.xlsx, hlidky.json, rozpis.html, casy.csv.
"""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
import os
import random
import re
import sys
import zipfile

from lxml import etree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'skills', 'csk-eskymo', 'scripts'))
from eskymo_ods import CELL, COLS_REP, P, ROW, ROWS_REP, TNAME, VALUE, VTYPE, Workbook  # noqa: E402

OUT = os.path.join(ROOT, 'tests', 'fixtures')
SEZONA = 2026

# Veřejné: Příloha č. 3 Směrnic 2026 (oficiální zkratky oddílů) — výběr
ODDILY = [(1, 'Boh.Pha', 'Bohemians Praha', 'C'), (9, 'USK Pha', 'USK Praha', 'C'),
          (12, 'Dukla B.', 'Dukla Brandýs', 'C'), (23, 'SKVS ČB', 'SK Vodní slalom České Budějovice', 'C'),
          (24, 'Č.Kruml.', 'SK Vltava Č.Krumlov', 'C'), (39, 'Loko Plz', 'TJ Loko Plzeň', 'C'),
          (57, 'Pardub.', 'TJ Syntézia Pardub.', 'C'), (64, 'Vys.Mýto', 'SKK Vysoké Mýto', 'C'),
          (103, 'KK Brno', 'KK Spoj Brno', 'M'), (119, 'Olomouc', 'UP Olomouc', 'M'),
          (121, 'KK Opava', 'KK Opava', 'M'), (129, 'Šumperk', 'TJ Šumperk', 'M')]
PRIJMENI = ['Novák', 'Svoboda', 'Dvořák', 'Černý', 'Procházka', 'Kučera', 'Veselý', 'Horák', 'Němec',
            'Marek', 'Pospíšil', 'Hájek', 'Jelínek', 'Král', 'Růžička', 'Beneš', 'Fiala', 'Sedláček',
            'Doležal', 'Zeman', 'Kolář', 'Navrátil', 'Čermák', 'Urban', 'Vaněk', 'Blažek', 'Kříž',
            'Kovář', 'Bartoš', 'Vlček', 'Polák', 'Musil', 'Kopecký', 'Šimek', 'Konečný', 'Malý',
            'Holub', 'Štěpánek', 'Kadlec', 'Dostál']
MUZ = ['Jan', 'Petr', 'Tomáš', 'Jakub', 'Martin', 'Lukáš', 'Vojtěch', 'Ondřej', 'Adam', 'Matěj',
       'Filip', 'David', 'Šimon', 'Josef', 'Karel', 'Pavel', 'Jiří', 'Michal', 'Daniel', 'Vít']
ZENA = ['Anna', 'Tereza', 'Eliška', 'Karolína', 'Kateřina', 'Lucie', 'Barbora', 'Adéla', 'Natálie',
        'Klára', 'Veronika', 'Markéta', 'Hana', 'Jana', 'Petra', 'Zuzana', 'Julie', 'Nela', 'Ema', 'Marie']


def zensky(p: str) -> str:
    if p.endswith('ý'):
        return p[:-1] + 'á'
    if p.endswith('ek'):
        return p[:-2] + 'ková'
    if p.endswith('ec'):
        return p[:-2] + 'cová'
    if p.endswith(('a', 'e')):
        return p[:-1] + 'ová'
    return p + 'ová'


def vk(rok):
    vek = SEZONA - rok
    for kod, od, do in [('PZ', 6, 10), ('ZM', 11, 12), ('ZS', 13, 14), ('DM', 15, 16), ('DS', 17, 18),
                        ('U23', 19, 23), ('', 24, 34), ('VM', 35, 44), ('V ', 45, 54), ('VS', 55, 64),
                        ('SV', 65, 150)]:
        if od <= vek <= do:
            return kod
    return ''


def registr(seed=2026, n=420):
    rnd = random.Random(seed)
    lide, pouzita = [], set()
    per_club = {o[0]: 0 for o in ODDILY}
    vt_w = [('', 55), ('3', 15), ('3+', 8), ('2', 12), ('2+', 4), ('1', 4), ('MT', 2)]
    vts, vws = zip(*vt_w)
    for i in range(n):
        club = rnd.choice(ODDILY)
        per_club[club[0]] += 1
        rgc = club[0] * 1000 + per_club[club[0]]
        muz = rnd.random() < 0.62
        pr = rnd.choice(PRIJMENI)
        pr = pr if muz else zensky(pr)
        jm = rnd.choice(MUZ if muz else ZENA)
        rok = rnd.choice(list(range(1962, 2021)) + list(range(2004, 2016)) * 3)
        while (pr, jm, rok) in pouzita:
            rok += 1
        pouzita.add((pr, jm, rok))
        vt = {k: (rnd.choices(vts, vws)[0] if SEZONA - rok >= 11 else '') for k in
              ('KS', 'C1S', 'C2S', 'KW', 'C1W', 'C2W')}
        lide.append({'rgc': rgc, 'prijmeni': pr, 'jmeno': jm, 'rok': rok, 'pohlavi': 't' if muz else 'f',
                     'vk': vk(rok), **vt, 'oddil': club[1], 'odd_nazev': club[2], 'vek': SEZONA - rok,
                     'kmen': 500000 + i, 'prohl': 'A' if rnd.random() < 0.85 else '',
                     'datum_prohl': '2026-03-01' if rnd.random() < 0.85 else '', 'oblast': club[3]})
    # pevné postavy pro testy (stejné jméno, jiný ročník; diakritika)
    lide.append({**lide[0], 'rgc': 23901, 'prijmeni': 'Růžička', 'jmeno': 'Karel', 'rok': 1976, 'vk': vk(1976),
                 'pohlavi': 't', 'oddil': 'SKVS ČB', 'odd_nazev': ODDILY[3][2], 'kmen': 599001})
    lide.append({**lide[0], 'rgc': 23902, 'prijmeni': 'Růžička', 'jmeno': 'Karel', 'rok': 2004, 'vk': vk(2004),
                 'pohlavi': 't', 'oddil': 'SKVS ČB', 'odd_nazev': ODDILY[3][2], 'kmen': 599002})
    return lide


REG_COLS = ['rgc', 'prijmeni', 'jmeno', 'rok', 'pohlavi', 'vk', 'KS', 'C1S', 'C2S', 'KW', 'C1W', 'C2W',
            'oddil', 'odd_nazev', 'vek', 'kmen', 'prohl', 'datum_prohl', 'oblast']


def _cell(v):
    c = etree.Element(CELL)
    if v is None or v == '':
        return c
    if isinstance(v, (int, float)):
        c.set(VTYPE, 'float')
        c.set(VALUE, str(v))
    else:
        c.set(VTYPE, 'string')
    p = etree.SubElement(c, P)
    if isinstance(v, str) and v.startswith(' '):  # " MT" → <text:s/>MT
        s = etree.SubElement(p, '{urn:oasis:names:tc:opendocument:xmlns:text:1.0}s')
        s.tail = v.lstrip(' ')
    else:
        p.text = str(v)
    return c


def nahrad_list(wb: Workbook, name: str, rows: list[list], ncols: int):
    sh = wb.sheet(name)
    t = sh.el
    all_rows = [r for r in t.iter(ROW)]
    header = all_rows[0]
    for r in all_rows[1:]:
        r.getparent().remove(r)
    parent = header.getparent()
    pos = parent.index(header) + 1
    for vals in rows:
        row = etree.Element(ROW)
        for v in vals[:ncols]:
            row.append(_cell(v))
        parent.insert(pos, row)
        pos += 1
    tail = etree.Element(ROW)
    tail.set(ROWS_REP, '100')
    c = etree.SubElement(tail, CELL)
    c.set(COLS_REP, str(ncols))
    parent.insert(pos, tail)
    sh._index = None


def anonymizuj(src: str, dst: str, lide: list[dict], nazev: str, datum: str, cislo: int, disciplina_check=None):
    wb = Workbook(src)
    orig = wb.sheet('reg').values(max_cols=3)[1:]
    orig_prijmeni = {str(r[1]).strip() for r in orig if len(r) > 1 and r[1] and len(str(r[1]).strip()) >= 6}
    ncols = len(wb.sheet('reg').values(max_rows=1, max_cols=30)[0])
    rows = []
    for o in lide:
        vals = [o['rgc'], o['prijmeni'], o['jmeno'], str(o['rok']), o['pohlavi'], o['vk']]
        vals += [(' MT' if o[k] == 'MT' else o[k]) for k in ('KS', 'C1S', 'C2S', 'KW', 'C1W', 'C2W')]
        vals += [o['oddil'], o['odd_nazev'], o['vek'], o['kmen'], o['prohl'], o['datum_prohl'], o['oblast']]
        rows.append(vals)
    nahrad_list(wb, 'reg', rows, ncols)
    cizi = [['A90001', 'MÜLLER', 'Hanna', '2005', 'f', 'U23', '', '', '', '', '', '', 'GER', 'Kanu Test e.V.', 21, ''],
            ['A90002', 'SMITH', 'Tom', '1990', 't', '', '', '', '', '', '', '', 'GBR', 'Test Canoe Club', 36, '']]
    nahrad_list(wb, 'cizi', cizi, len(wb.sheet('cizi').values(max_rows=1, max_cols=30)[0]))
    p = wb.sheet('param')
    from inspect_workbook import read_param
    pole = read_param(wb)['pole']
    zmeny = {'Název závodu': nazev, 'Místo závodu': 'Testov, Horní jez', 'Pořadatel': 'Testovací oddíl',
             'Ředitel závodu': 'Ředitel Testovací', 'Vrchní rozhodčí': 'Rozhodčí Testovací',
             'Datum závodu': datum, 'Číslo závodu': cislo, 'Adresa registru': 'https://csk.kanoe.cz/exp.php?k=REDACTED',
             'Výsledky zpracoval': '', 'Telefon': '', 'Mail': '', 'Pracovní adresář': ''}
    stare = {k: pole[k]['hodnota'] for k in ('Název závodu', 'Místo závodu', 'Číslo závodu') if k in pole}
    for k, v in zmeny.items():
        if k in pole:
            p.set_a1(pole[k]['bunka'], v)
    # meta, styles, thumbnail
    wb.parts['meta.xml'] = re.sub(rb'<(meta:initial-creator|dc:creator)>[^<]*</\1>', b'', wb.parts['meta.xml'])
    st = wb.parts['styles.xml'].decode('utf-8')
    # záhlaví/zápatí tisku nese název, místo a číslo závodu z param a pořadatele šablony
    for k, nove in (('Název závodu', nazev), ('Místo závodu', 'Testov, Horní jez')):
        if stare.get(k):
            st = st.replace(f'>{stare[k]}<', f'>{nove}<')
    if stare.get('Číslo závodu') is not None:
        st = re.sub(r'závod č\. \d+', f'závod č. {cislo}', st)
    st = re.sub(r'>\d{2}\.\d{2}\.\d{4}<', '>01.01.2026<', st)
    st = re.sub(r'>\d{2}:\d{2}:\d{2}<', '>00:00:00<', st)
    st = re.sub(r'(<text:p[^>]*>)(?!ESKYMO|Stránka|Testov|závod č)([^<]{3,})(</text:p>)', r'\1Testovací oddíl\3', st)
    wb.parts['styles.xml'] = st.encode('utf-8')
    wb.parts.pop('Thumbnails/thumbnail.png', None)
    wb._order = [n for n in wb._order if not n.startswith('Thumbnails/')]
    wb.parts['META-INF/manifest.xml'] = re.sub(rb'<manifest:file-entry[^>]*Thumbnails[^>]*/>', b'',
                                               wb.parts['META-INF/manifest.xml'])
    wb.save(dst)
    # kontrola: žádné původní příjmení ani klíč registru
    synt = {x.lower() for x in PRIJMENI + [zensky(x) for x in PRIJMENI] + MUZ + ZENA +
            ['Müller', 'Smith', 'Hanna', 'Tom', 'Testovací']}
    hledat = [x for x in orig_prijmeni if x.lower() not in synt]
    z = zipfile.ZipFile(dst)
    text = ''.join(z.read(n).decode('utf-8', 'replace') for n in z.namelist() if n.endswith('.xml'))
    low = text.lower()
    nalez = [x for x in hledat if re.search(r'' + re.escape(x.lower()) + r'', low)]
    klic = re.findall(r'exp\.php\?k=([0-9a-f]{16,})', text)
    if nalez or klic:
        raise SystemExit(f'ANONYMIZACE SELHALA v {dst}: {nalez[:10]} klic={bool(klic)}')
    print(f'{os.path.basename(dst)}: reg {len(lide)} syntetických osob, kontrola OK '
          f'({len(hledat)} původních příjmení nenalezeno)')


# ---------- syntetické vstupy ----------
def vyber(lide, rnd, n, pohlavi=None, od=1960, do=2012, vt=None):
    kand = [o for o in lide if (pohlavi is None or o['pohlavi'] == pohlavi) and od <= o['rok'] <= do
            and (vt is None or o[vt])]
    return rnd.sample(kand, n)


def prihlasky_csv(lide, path):
    rnd = random.Random(7)
    hdr = ['kategorie', 'rgc', 'jmeno', 'nar', 'oddil', 'vt', 'vk', 'zavody', 'poznamky', 'poradi',
           'poradi nkz', 'startovne', 'zeme', 'vedouci', 'kod', 'disciplina']
    rows, n = [], 0

    def add(kat, os_, zavody='', vt=None):
        nonlocal n
        n += 1
        rows.append([kat, ' '.join(str(o['rgc']) for o in os_), ' '.join(f"{o['prijmeni']} {o['jmeno']}" for o in os_),
                     ' '.join(str(o['rok']) for o in os_), ' '.join(o['odd_nazev'] for o in os_),
                     vt if vt is not None else (os_[0]['KS'] or ''), os_[0]['vk'].strip(), zavody, '', str(n), '',
                     '200', '', 'Vedoucí Testovací', f'{abs(hash(os_[0]["oddil"])) % 16**8:08x}', 'slalom'])
    for o in vyber(lide, rnd, 18, 't', vt='KS'):
        add('K1M', [o])
    for o in vyber(lide, rnd, 9, 'f'):
        add('K1W', [o])
    for o in vyber(lide, rnd, 8, 't'):
        add('C1M', [o])
    for o in vyber(lide, rnd, 4, 'f'):
        add('C1W', [o])
    for _ in range(3):
        add('C2M', vyber(lide, rnd, 2, 't'))
    for o in vyber(lide, rnd, 3, None, 2016, 2020):
        add('K1M' if o['pohlavi'] == 't' else 'K1W', [o])
    add('K1M', vyber(lide, rnd, 1, 't', vt='KS'), zavody='136')   # jede jen v neděli
    rows.append(['K1W', 'A90001', 'MÜLLER Hanna', '2005', 'Kanu Test e.V.', '', 'U23', '', '', str(n + 1), '',
                 '200', 'GER', 'Vedoucí Testovací', 'ffffffff', 'slalom'])
    rows.append(['K1M', '999999', 'Neexistující Karel', '2000', 'Testovací oddíl', '3', '', '', '', str(n + 2), '',
                 '200', '', 'Vedoucí Testovací', 'eeeeeeee', 'slalom'])
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=';', lineterminator='\r\n')
    w.writerow(hdr)
    w.writerows(rows)
    open(path, 'wb').write(buf.getvalue().encode('cp1250'))
    return rows


def canoe123_xml(lide, path):
    rnd = random.Random(11)
    NS = 'http://siwidata.com/Canoe123/Data.xsd'
    root = etree.Element(f'{{{NS}}}Canoe123Data', nsmap={None: NS})

    def el(parent, tag, text=None):
        e = etree.SubElement(parent, f'{{{NS}}}{tag}')
        if text is not None:
            e.text = str(text)
        return e

    ucast = []
    bib = 0
    for cls, n, poh in (('K1M', 10, 't'), ('K1Z', 6, 'f'), ('C1M', 5, 't')):
        for o in vyber(lide, rnd, n, poh):
            bib += 1
            ucast.append((cls, bib, [o], None))
    for i, pair in enumerate([vyber(lide, rnd, 2, 't') for _ in range(2)]):
        bib += 1
        ucast.append(('C2M', bib, pair, 'nový' if i == 0 else 'slepený'))
    bib += 1
    ucast.append(('C1M', bib, [{'rgc': '', 'prijmeni': 'SMITH', 'jmeno': 'Tom', 'rok': 1990, 'oddil': 'GBR'}], 'cizinec'))
    bib += 1
    ucast.append(('XYZ', bib, vyber(lide, rnd, 1, 't'), 'neznámá třída'))
    for cls, b, os_, pozn in ucast:
        p = el(root, 'Participants')
        o = os_[0]
        pid = f"{o['rgc']}.{cls}" if o['rgc'] else f'6391990000000{b:05d}'
        if pozn == 'slepený':
            pid = f"{os_[0]['rgc']}{os_[1]['rgc']}.{cls}"
        el(p, 'Id', pid)
        el(p, 'ClassId', cls)
        el(p, 'EventBib', b)
        if pozn == 'slepený':
            el(p, 'ICFId', f"{os_[0]['rgc']}{os_[1]['rgc']}")
        elif o['rgc']:
            el(p, 'ICFId', o['rgc'])
        else:
            el(p, 'ICFId')
        if len(os_) > 1 and pozn == 'nový':
            el(p, 'ICFId2', os_[1]['rgc'])
        el(p, 'FamilyName', o['prijmeni'].upper())
        el(p, 'GivenName', o['jmeno'])
        if len(os_) > 1:
            el(p, 'FamilyName2', os_[1]['prijmeni'].upper())
            el(p, 'GivenName2', os_[1]['jmeno'])
        el(p, 'Club', o.get('odd_nazev', o['oddil']))
        el(p, 'Birthdate', f"{o['rok']}-01-01T11:00:00+01:00")
        if len(os_) > 1:
            el(p, 'Birthdate2', f"{os_[1]['rok']}-01-01T11:00:00+01:00")
        el(p, 'IsTeam', 'false')
    for i, (cls, b, os_, pozn) in enumerate(ucast):
        o = os_[0]
        pid = f"{o['rgc']}.{cls}" if o['rgc'] else f'6391990000000{b:05d}'
        if pozn == 'slepený':
            pid = f"{os_[0]['rgc']}{os_[1]['rgc']}.{cls}"
        for run in (1, 2):
            r = el(root, 'Results')
            el(r, 'RaceId', f'{cls}_BR{run}_15')
            el(r, 'Id', pid)
            el(r, 'Bib', f'{b:4d}')
            if i == 2 and run == 2:
                el(r, 'Status', 'DNS'); el(r, 'Time'); el(r, 'Pen')
            elif i == 3 and run == 1:
                el(r, 'Status', 'DNF'); el(r, 'Time'); el(r, 'Pen')
            elif i == 4 and run == 2:
                el(r, 'Status'); el(r, 'Time'); el(r, 'Pen')          # skrytý DNS
            else:
                t = rnd.randint(85000, 130000)
                el(r, 'Status')
                el(r, 'Time', t)
                if not (i == 5 and run == 1):                          # Time bez Pen
                    el(r, 'Pen', rnd.choice([0, 0, 2, 4, 50]))
    etree.ElementTree(root).write(path, xml_declaration=True, encoding='utf-8', standalone=True, pretty_print=True)
    return ucast


def loni_xlsx(lide, path):
    import openpyxl
    rnd = random.Random(13)
    wb = openpyxl.Workbook()
    wb.active.title = 'param'
    wb['param']['A1'] = 'Eskymo verze: 1.7.12'
    hlidky = {}
    for kat, poh, n in (('c1m', 't', 4), ('k1z', 'f', 3), ('k1m', 't', 5)):
        ws = wb.create_sheet(kat)
        ws.append([kat.upper(), None, None, 'VÝSLEDKOVÁ LISTINA'])
        ws.append(['poř.', 'pvk', 'vk', 'stč', 'rgc', 'jméno', 'nar.', 'vt', 'oddíl'])
        kluby = rnd.sample(ODDILY, n - 1) + [ODDILY[0]]
        teams = []
        for i, club in enumerate(kluby):
            cl = [o for o in lide if o['oddil'] == club[1] and o['pohlavi'] == poh and 1980 < o['rok'] < 2010]
            members = rnd.sample(cl, 3)
            pism = ' A' if club == ODDILY[0] else ''
            if club == ODDILY[0] and i == n - 1:
                pism = ' B'
            teams.append(members)
            ws.append([f'{i + 1}.' if i < n - 1 else None, None, None, 60 - i,
                       '\n'.join(str(m['rgc']) for m in members),
                       '\n'.join(f"{m['prijmeni'].upper()} {m['jmeno']}" for m in members),
                       '\n'.join(str(m['rok']) for m in members), '\n'.join('3' for _ in members),
                       '\n'.join([club[1]] * 2 + [club[1] + pism])])
        hlidky[kat] = teams
    wb.save(path)
    return hlidky


def rozpis_html(path):
    html = '''<html><body><h1>Testovací slalomy <small>03.10.2026 - 04.10.2026</small></h1>
<h3>Propozice závodu č. 135</h3><h2>Testovací slalom</h2>
<table>
<tr><td>Pořadatel:</td><td>Testovací oddíl</td></tr>
<tr><td>Druh závodu:</td><td>slalom  OČ, BHZ: 4 <br>propozice schváleny 17.08.2026</td></tr>
<tr><td>Datum závodu:</td><td>03.10.2026</td></tr>
<tr><td>Centrum, trať:</td><td>řeka Testová, Testov</td></tr>
<tr><td>Ředitel závodu:</td><td>Ředitel Testovací</td></tr>
<tr><td>Vrchní rozhodčí:</td><td>Rozhodčí Testovací</td></tr>
<tr><td>Stavitel trati:</td><td>Stavitel Testovací</td></tr>
</table>
<div><h4>Pořad závodu:</h4>8.30 start závodu<br>pořadí kategorií: 1.skupina K1m, C1ž, C2m, předžáci K1<br>2.skupina C1m, předžáci C1, K1ž, C2mix</div>
<div><h4>Startovné:</h4></div><div>mládež - 100 Kč, dospělí - 200 Kč</div>
<div><span class="font-weight-bold">muži:</span> K1, C1, C2 slalom</div>
<div><span class="font-weight-bold">ženy:</span> K1, C1 slalom</div>
<div><span class="font-weight-bold">mix:</span> C2mi slalom</div>
</body></html>'''
    open(path, 'w', encoding='utf-8').write(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--slalom', required=True, help='prázdná individuální šablona (reálná, lokální)')
    ap.add_argument('--hlidky', required=True, help='prázdná hlídková šablona (reálná, lokální)')
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    lide = registr()
    anonymizuj(a.slalom, os.path.join(OUT, 'slalom.ods'), lide, 'Testovací slalom', '15.08.26', 135)
    anonymizuj(a.hlidky, os.path.join(OUT, 'hlidky_sprint.ods'), lide, 'Testovací MČR družstev ve sprintu',
               '30.08.26', 113)
    prihlasky_csv(lide, os.path.join(OUT, 'prihlasky.csv'))
    canoe123_xml(lide, os.path.join(OUT, 'canoe123.xml'))
    loni = loni_xlsx(lide, os.path.join(OUT, 'loni_hlidky.xlsx'))
    # letošní hlídky: dva kluby z loňska (jedna osoba navazuje), jeden nový, jedno písmeno deklarované
    hl = []
    for kat, teams in loni.items():
        for t in teams[:2]:
            hl.append({'kat': kat, 'lode': [str(t[0]['rgc'])], 'zdroj': 'test'})
        cl = [o for o in lide if o['oddil'] == 'KK Opava' and 1980 < o['rok'] < 2010]
        hl.append({'kat': kat, 'lode': [str(cl[0]['rgc'])], 'zdroj': 'test-nova'})
    json.dump(hl, open(os.path.join(OUT, 'hlidky.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rozpis_html(os.path.join(OUT, 'rozpis.html'))
    print('Hotovo →', OUT)


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
