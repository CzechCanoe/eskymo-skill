# -*- coding: utf-8 -*-
"""
domena — číselníky a pravidla ČSK DV, která potřebují ostatní skripty.

Kategorie, výkonnostní třídy (VT) a věkové kategorie (VK). Věkové hranice jsou
dané věkem dovršeným v kalendářním roce (Pravidla T-3, S26 §1), takže funkce
fungují pro libovolnou sezónu — ročníky se dopočítají z roku závodu.

Kde se pravidla mění po sezónách, platí references/pravidla-<rok>.md.
"""
from __future__ import annotations

import re
import unicodedata

# ---------- kategorie ----------
# Kód z přihlášek / Canoe123 / textu → kód listu v Eskymu (3 malé znaky).
KATEGORIE_ALIASY = {
    'K1M': 'k1m', 'K1W': 'k1z', 'K1Z': 'k1z', 'K1Ž': 'k1z',
    'C1M': 'c1m', 'C1W': 'c1z', 'C1Z': 'c1z', 'C1Ž': 'c1z',
    'C2M': 'c2m', 'C2W': 'c2z', 'C2Z': 'c2z', 'C2Ž': 'c2z',
    'C2X': 'c2x', 'C2MIX': 'c2x', 'C2MI': 'c2x', 'C2MX': 'c2x',
    'PZK': 'pzk', 'PŽK': 'pzk', 'PZC': 'pzc', 'PŽC': 'pzc',
    'FOR': 'for',  # předjezdci
}
# Lidský název listu (pro výpisy)
KATEGORIE_NAZEV = {
    'k1m': 'K1 muži', 'k1z': 'K1 ženy', 'c1m': 'C1 muži', 'c1z': 'C1 ženy',
    'c2m': 'C2 muži', 'c2z': 'C2 ženy', 'c2x': 'C2 mix', 'pzk': 'předžáci K1',
    'pzc': 'předžáci C1', 'for': 'předjezdci',
}
# Pořadí listů, které Eskymo vygeneruje (Eskymo.makeParamsDialog / newRace)
PORADI_LISTU = {
    'slalom': ['for', 'pzk', 'pzc', 'c1z', 'c1m', 'c2m', 'k1z', 'k1m', 'c2z', 'c2x'],
    'sjezd': ['for', 'pzk', 'pzc', 'c1m', 'k1z', 'k1m', 'c1z', 'c2m', 'c2z', 'c2x'],
    'sprint': ['for', 'pzk', 'pzc', 'c1m', 'k1z', 'k1m', 'c1z', 'c2m', 'c2z', 'c2x'],
}


def kategorie_eskymo(kod: str) -> str | None:
    """'K1W' → 'k1z', 'c2miX' → 'c2x'. Neznámý kód → None (nikdy tiše nezahazovat!)."""
    if not kod:
        return None
    k = re.sub(r'[\s_-]', '', str(kod)).upper()
    if k.lower() in KATEGORIE_NAZEV:
        return k.lower()
    return KATEGORIE_ALIASY.get(k)


def lod(kat: str) -> str:
    """Typ lodě pro výběr sloupce VT: 'k1m' → 'K1', 'c2x' → 'C2', předžáci/předjezdci → 'K1'."""
    k = kat.lower()
    if k.startswith('c1') or k == 'pzc':
        return 'C1'
    if k.startswith('c2'):
        return 'C2'
    return 'K1'


def je_debl(kat: str) -> bool:
    return kat.lower().startswith('c2')


# ---------- výkonnostní třídy ----------
# Od nejlepší. Prázdná / '0' = bez VT.
VT_PORADI = ['MT', '1', '2+', '2', '3+', '3', '']
# Skupiny podle Pravidel 2.17.01: (1) MT a 1, (2) 2+, (3) 2, (4) 3+, (5) 3, (6) bez VT
VT_SKUPINY_PRAVIDLA = [['MT', '1'], ['2+'], ['2'], ['3+'], ['3'], ['']]
# Starší čtení P 2.17.01 (v docx Pravidel 2022 je číslování seznamu pomíchané: 4 skupiny)
VT_SKUPINY_PRAVIDLA4 = [['MT', '1'], ['2+', '2'], ['3+', '3'], ['']]
# Skupiny losování v Eskymu (SpreadsheetUtils.losovani), od nejhorší: 0/'', 3, 3+, 2, 2+, 1, MT
VT_SKUPINY_ESKYMO = [['MT'], ['1'], ['2+'], ['2'], ['3+'], ['3'], ['']]

# Sloupce VT v listu reg podle disciplíny a lodě
VT_SLOUPEC = {
    ('slalom', 'K1'): 'KS', ('slalom', 'C1'): 'C1S', ('slalom', 'C2'): 'C2S',
    ('sjezd', 'K1'): 'KW', ('sjezd', 'C1'): 'C1W', ('sjezd', 'C2'): 'C2W',
}


def norm_vt(v) -> str:
    """' MT' → 'MT', '2.0' → '2', '0'/None → ''."""
    if v is None:
        return ''
    if isinstance(v, float):
        v = int(v) if v.is_integer() else v
    s = str(v).strip().upper().replace(' ', '')
    if s in ('0', '9', 'M'):
        return 'MT' if s == 'M' else ''
    return s if s in VT_PORADI else ''


def vt_rank(v) -> int:
    """0 = MT (nejlepší) … 6 = bez VT."""
    return VT_PORADI.index(norm_vt(v))


def lepsi_vt(*vts) -> str:
    """C2 s různými VT: platí vyšší VT (Pravidla 2.37.02)."""
    vs = [norm_vt(v) for v in vts]
    return min(vs, key=VT_PORADI.index) if vs else ''


def vt_skupina(v, skupiny=VT_SKUPINY_PRAVIDLA) -> int:
    n = norm_vt(v)
    for i, g in enumerate(skupiny):
        if n in g:
            return i
    return len(skupiny) - 1


def disciplina_vt(disciplina: str) -> str:
    """Sprint i sjezd používají sjezdové VT (KW/C1W/C2W)."""
    d = (disciplina or '').strip().lower()
    return 'slalom' if d.startswith('slalom') else 'sjezd'


# ---------- věkové kategorie ----------
# (kód, věk od, věk do) — věk dovršený v roce sezóny. Pravidla T-3, S26 §1.
VK_VEK = [
    ('PZ', 6, 10), ('ZM', 11, 12), ('ZS', 13, 14), ('DM', 15, 16), ('DS', 17, 18),
    ('U23', 19, 23), ('', 24, 34), ('VM', 35, 44), ('V', 45, 54), ('VS', 55, 64), ('SV', 65, 150),
]


def vk_pro_rocnik(rocnik: int, sezona: int) -> str:
    """Věková kategorie tak, jak ji zobrazuje Eskymo (dospělí = '')."""
    vek = sezona - int(rocnik)
    for kod, od, do in VK_VEK:
        if od <= vek <= do:
            return kod
    return '?'


def rocniky_vk(sezona: int) -> dict:
    """{'ZM': (2014, 2015), …} pro danou sezónu — pro výpisy a kontroly."""
    return {k: (sezona - do, sezona - od) for k, od, do in VK_VEK if k}


def je_predzak(rocnik, sezona: int) -> bool:
    try:
        return vk_pro_rocnik(int(rocnik), sezona) == 'PZ'
    except (TypeError, ValueError):
        return False


# ---------- texty a jména ----------
def bez_diakritiky(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', s or '') if not unicodedata.combining(c))


def klic_jmena(s: str) -> str:
    """Klíč pro porovnání jmen: bez diakritiky, velká písmena, bez interpunkce."""
    return re.sub(r'[^A-Z ]', '', bez_diakritiky(s).upper()).strip()


def stav_jizdy(v) -> str | None:
    """Rozpozná kód stavu jízdy (DNS, DNS-A, DNS-B, DNF, DSQ-R, DSQ-C). Jinak None."""
    if not isinstance(v, str):
        return None
    s = v.strip().upper().replace(' ', '')
    if s in ('DNS', 'DNS-A', 'DNS-B', 'DNF', 'DSQ-R', 'DSQ-C'):
        return s
    if s in ('DSQ', 'DQB', 'DIS'):
        return 'DSQ-R'
    return None
