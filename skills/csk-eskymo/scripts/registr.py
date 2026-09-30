# -*- coding: utf-8 -*-
"""
registr — čtení listů `reg` a `cizi` z Eskymo sešitu a vyhledávání osob.

`reg` je jediný zdroj pravdy o závodnících (jméno, ročník, oddíl, VT, prohlídka).
Plní ho Eskymo (Eskymo → Import registru); skripty ho jen čtou.

    from registr import Registr
    r = Registr.ze_sesitu(Workbook('zavod.ods'))
    o = r.get('9162')
    kandidati = r.hledej('Novák', 'Jan', rok=2008, oddil='USK Pha')

Pozn.: prefix RGC odpovídá oddílu PŮVODNÍ registrace, ne aktuálnímu —
aktuální oddíl je vždy sloupec `Oddil` (M) v `reg`.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from domena import VT_SLOUPEC, disciplina_vt, klic_jmena, lepsi_vt, lod, norm_vt
from eskymo_ods import Workbook, norm_rgc

# Sloupce reg (A..S) podle Eskyma 1.7.x; cizi má stejné pořadí A..P
_SL = {'RGC': 0, 'Prijmeni': 1, 'Jmeno': 2, 'Nar': 3, 'Pohlavi': 4, 'VK': 5,
       'KS': 6, 'C1S': 7, 'C2S': 8, 'KW': 9, 'C1W': 10, 'C2W': 11,
       'Oddil': 12, 'Odd_nazev': 13, 'Vek': 14, 'Kmen': 15, 'Prohlidka': 16,
       'DatumProhlidky': 17, 'Oblast': 18}


@dataclass
class Osoba:
    rgc: str
    prijmeni: str
    jmeno: str
    rok: int | None
    pohlavi: str
    vk: str
    vt: dict = field(default_factory=dict)
    oddil: str = ''
    odd_nazev: str = ''
    prohlidka: bool | None = None
    oblast: str = ''
    cizinec: bool = False

    @property
    def cele_jmeno(self) -> str:
        return f'{self.prijmeni.upper()} {self.jmeno}'.strip()

    def vt_pro(self, kat_nebo_lod: str, disciplina: str) -> str:
        l = kat_nebo_lod.upper() if kat_nebo_lod.upper() in ('K1', 'C1', 'C2') else lod(kat_nebo_lod)
        return self.vt.get(VT_SLOUPEC[(disciplina_vt(disciplina), l)], '')


def _s(v) -> str:
    if v is None:
        return ''
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def _rok(v):
    s = _s(v).lstrip('#')
    return int(s[:4]) if s[:4].isdigit() else None


class Registr:
    def __init__(self, osoby: list[Osoba]):
        self.osoby = osoby
        self._by_rgc = {o.rgc: o for o in osoby}
        self._by_prijmeni: dict[str, list[Osoba]] = {}
        for o in osoby:
            self._by_prijmeni.setdefault(klic_jmena(o.prijmeni), []).append(o)

    @classmethod
    def ze_sesitu(cls, wb: Workbook) -> 'Registr':
        osoby = []
        for sheet, cizinec in (('reg', False), ('cizi', True)):
            if not wb.has(sheet):
                continue
            vals = wb.sheet(sheet).values(max_cols=19)
            hlav = [str(x or '').strip().lower() for x in (vals[0] if vals else [])]
            ma_prohlidky = len(hlav) > 16 and 'prohl' in hlav[16]
            for row in vals[1:]:
                if not row or row[0] in (None, ''):
                    continue
                row = list(row) + [None] * (19 - len(row))
                rgc = norm_rgc(row[0])
                if not rgc:
                    continue
                prijmeni, jmeno = _s(row[1]), _s(row[2])
                if cizinec and not jmeno and ' ' in prijmeni:
                    # cizi má někdy celé jméno ve sloupci B
                    prijmeni, jmeno = prijmeni.split(' ', 1)
                osoby.append(Osoba(
                    rgc=rgc, prijmeni=prijmeni, jmeno=jmeno, rok=_rok(row[3]),
                    pohlavi=_s(row[4]), vk=_s(row[5]),
                    vt={k: norm_vt(row[_SL[k]]) for k in ('KS', 'C1S', 'C2S', 'KW', 'C1W', 'C2W')},
                    oddil=_s(row[12]), odd_nazev=_s(row[13]),
                    prohlidka=(None if cizinec or not ma_prohlidky else _s(row[16]).upper() == 'A'),
                    oblast=_s(row[18]).upper(), cizinec=cizinec or rgc.startswith('A'),
                ))
        return cls(osoby)

    def __len__(self):
        return len(self.osoby)

    def get(self, rgc) -> Osoba | None:
        return self._by_rgc.get(norm_rgc(rgc))

    def hledej(self, prijmeni: str, jmeno: str | None = None, rok: int | None = None,
               oddil: str | None = None) -> list[Osoba]:
        """Kandidáti podle jména (bez diakritiky), zúžení ročníkem a oddílem.

        Vrací seznam — prázdný = nenalezeno, víc prvků = nejednoznačné (rozhodne člověk).
        """
        kand = list(self._by_prijmeni.get(klic_jmena(prijmeni), []))
        if jmeno:
            kj = klic_jmena(jmeno)
            k2 = [o for o in kand if klic_jmena(o.jmeno) == kj]
            if not k2:  # zkrácené jméno / překlep: prefix
                k2 = [o for o in kand if klic_jmena(o.jmeno).startswith(kj[:3])] if len(kj) >= 3 else []
            kand = k2
        if rok and len(kand) > 1:
            k2 = [o for o in kand if o.rok == int(rok)]
            kand = k2 or kand
        if oddil and len(kand) > 1:
            ko = klic_jmena(oddil)
            k2 = [o for o in kand if ko and (ko in klic_jmena(o.oddil) or ko in klic_jmena(o.odd_nazev)
                                              or klic_jmena(o.oddil) in ko)]
            kand = k2 or kand
        return kand

    def vt_lode(self, rgcs: list, kat: str, disciplina: str) -> str:
        """VT lodě: u C2 vyšší z obou (Pravidla 2.37.02)."""
        vts = []
        for r in rgcs:
            o = self.get(r)
            if o:
                vts.append(o.vt_pro(kat, disciplina))
        return lepsi_vt(*vts) if vts else ''
