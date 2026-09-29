# -*- coding: utf-8 -*-
"""
cisla — přidělení startovních čísel k hotovému startovnímu pořadí.

Číslování je záměrně samostatný krok nad uloženým nasazením: pořadatel často
dodatečně hlásí chybějící dresy nebo mění rozsah, a přečíslování pak musí být
jeden běh, ne ruční oprava.

Režimy (`rezim`):
  desitky      P 2.18.03 (výchozí): vzestupně, každá kategorie začíná číslem
               končícím jedničkou (1, 21, 41 …); `zarovnani` 10 lze změnit (100 → 101, 201 …)
  prubezne     vzestupně napříč závodem, mezi kategoriemi `mezera` rezervních čísel
  sestupne     sestupně napříč závodem od `start` (nejvyšší číslo má první startující),
               mezi kategoriemi `mezera` rezervních čísel (hlídky MČR 2026)
  sestupne-kat ČPw / KC individuál: v každé kategorii má poslední startující číslo 1
  pevne        čísla jsou už v datech (např. ČP slalom = umístění v loňském ČP)
Společné volby: `start` (první číslo), `vynechat` (čísla, která pořadatel nemá —
přeskakují se všude, i v rezervách), `max` (počet dresů, které pořadatel má).
"""
from __future__ import annotations


class ChybaCisel(ValueError):
    pass


def _gen(start: int, krok: int, vynechat: set):
    n = start
    while True:
        if n < 1:
            raise ChybaCisel('došla kladná čísla — zvyš `start` nebo zmenši mezery')
        if n not in vynechat:
            yield n
        n += krok


def prirad(kategorie: list[tuple[str, int]], rezim: str = 'desitky', start: int | None = None,
           mezera: int = 0, vynechat=(), zarovnani: int = 10, max_cislo: int | None = None,
           pevne: dict | None = None) -> dict:
    """kategorie = [(kat, pocet_lodi), …] v pořadí závodu.

    Vrací {'cisla': {kat: [stč v pořadí startu]}, 'rezervy': {kat: [rezervovaná za kategorií]}}.
    """
    vyn = {int(x) for x in vynechat}
    cisla, rezervy = {}, {}
    if rezim == 'pevne':
        for kat, n in kategorie:
            c = list((pevne or {}).get(kat, []))
            if len(c) != n or any(x is None for x in c):
                raise ChybaCisel(f'{kat}: režim „pevne“, ale čísla nejsou u všech {n} lodí')
            cisla[kat] = [int(x) for x in c]
        return _zkontroluj({'cisla': cisla, 'rezervy': rezervy}, rezim, max_cislo, vyn)

    if rezim == 'sestupne-kat':
        for kat, n in kategorie:
            g = _gen(1, 1, vyn)
            nums = [next(g) for _ in range(n)]
            cisla[kat] = list(reversed(nums))
        return _zkontroluj({'cisla': cisla, 'rezervy': rezervy}, rezim, max_cislo, vyn)

    if rezim == 'sestupne':
        if not start:
            celkem = sum(n for _, n in kategorie) + mezera * (len(kategorie) - 1) + len(vyn)
            raise ChybaCisel(f'režim „sestupne“ potřebuje `start` (nejvyšší číslo); '
                             f'potřeba je aspoň ~{celkem} čísel')
        g = _gen(int(start), -1, vyn)
        for i, (kat, n) in enumerate(kategorie):
            cisla[kat] = [next(g) for _ in range(n)]
            if i < len(kategorie) - 1:
                rezervy[kat] = [next(g) for _ in range(mezera)]
        return _zkontroluj({'cisla': cisla, 'rezervy': rezervy}, rezim, max_cislo, vyn)

    if rezim not in ('desitky', 'prubezne'):
        raise ChybaCisel(f'neznámý režim číslování {rezim!r}')
    n0 = int(start or 1)
    for i, (kat, n) in enumerate(kategorie):
        if rezim == 'desitky' and i > 0 and zarovnani > 1:
            # další číslo končící jedničkou (P 2.18.03), resp. 101, 201 … při zarovnání 100
            while n0 % zarovnani != 1 % zarovnani:
                n0 += 1
        g = _gen(n0, 1, vyn)
        cisla[kat] = [next(g) for _ in range(n)]
        last = cisla[kat][-1] if cisla[kat] else n0 - 1
        if i < len(kategorie) - 1 and mezera:
            g2 = _gen(last + 1, 1, vyn)
            rezervy[kat] = [next(g2) for _ in range(mezera)]
            last = rezervy[kat][-1]
        n0 = last + 1
    return _zkontroluj({'cisla': cisla, 'rezervy': rezervy}, rezim, max_cislo, vyn)


def _zkontroluj(res: dict, rezim: str, max_cislo, vyn: set) -> dict:
    """Povinné kontroly: unikátnost (kromě sestupne-kat), vynechaná čísla, rozsah."""
    vse = [c for cs in res['cisla'].values() for c in cs]
    if rezim != 'sestupne-kat' and len(set(vse)) != len(vse):
        raise ChybaCisel('startovní čísla nejsou unikátní napříč závodem')
    for kat, cs in res['cisla'].items():
        if len(set(cs)) != len(cs):
            raise ChybaCisel(f'{kat}: duplicitní startovní čísla')
    pouzita = set(vse) & vyn
    if pouzita:
        raise ChybaCisel(f'použita vynechaná čísla {sorted(pouzita)}')
    if vse and min(vse) < 1:
        raise ChybaCisel('číslo menší než 1')
    if max_cislo and vse and max(vse) > int(max_cislo):
        raise ChybaCisel(f'nejvyšší číslo {max(vse)} > počet dresů {max_cislo}')
    res['rozsah'] = (min(vse), max(vse)) if vse else None
    res['nevyuzita_vynechana'] = sorted(x for x in vyn if res['rozsah'] and not
                                        (res['rozsah'][0] <= x <= res['rozsah'][1]))
    return res


def popis(res: dict, poradi: list[str]) -> str:
    """Čitelný rozpis bloků — hodí se k nabídce variant pořadateli."""
    L = []
    for kat in poradi:
        cs = res['cisla'].get(kat, [])
        if not cs:
            continue
        s = f'{kat.upper():<4} {cs[0]:>4} → {cs[-1]:<4} ({len(cs)})'
        if res['rezervy'].get(kat):
            s += '   rezerva ' + ' '.join(map(str, res['rezervy'][kat]))
        L.append(s)
    if res.get('nevyuzita_vynechana'):
        L.append(f"! vynechaná čísla mimo rozsah (dotaz na zadání?): {res['nevyuzita_vynechana']}")
    return '\n'.join(L)
