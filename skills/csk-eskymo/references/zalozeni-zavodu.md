# Založení závodu: kalendář → rozpis → Nový závod

Cíl: z odkazu na akci v kalendáři ČSK připravit hodnoty pro dialog Eskymo → Nový závod
a parametry, které budou potřeba pro startovku. Sešit pak vytvoří pořadatel v Eskymu.

## 1. Zdroj

- Kalendář: `https://www.kanoe.cz/zavody/slalom-sjezd?s=2&r=<rok>`, akce `?link=<id>`
  (slalom i sjezd v jedné tabulce, filtr disciplíny není).
- **Strukturovaný rozpis**: `https://csk.kanoe.cz/extreq/kalendarcsk-show.php?s=2&a=<id>`
  (PDF: `kalendarcsk.php`). Každý závod akce má blok „Propozice závodu č. N“: pořadatel, druh
  (`slalom OČ, BHZ: 4`), datum, trať, činovníci (ředitel, VR, stavitel trati…), uzávěrka přihlášek,
  losování, startovné, **pořad závodu** (volný text) a **vypsané disciplíny**.
- Přílohy „propozice“ (`csk-dokumenty/…pdf`) jsou nespolehlivé (často seznam rozhodčích) —
  jen doplněk, vždy ověř, co v nich je.

```bash
python scripts/kalendar.py "https://www.kanoe.cz/zavody/slalom-sjezd?link=7511" -o zavod.json --tahak tahak.md
```

## 2. Co z rozpisu plyne (a jak jistě)

| Údaj | Zdroj | Jistota |
|---|---|---|
| číslo závodu, název, datum, pořadatel, ředitel, VR, BHZ, disciplína | pevná pole rozpisu | vysoká |
| kategorie | „vypsané disciplíny“ (`muži: K1, C1, C2 slalom`) | střední — u ČP/MČR chybí, předžáci bývají jen v pořadu |
| pořadí kategorií na startu, skupiny, „obě jízdy“ | pořad (volný text) | odhad → potvrdit |
| bodování Body1–3 | druh závodu | odhad → potvrdit (tabulka níže) |
| startovní interval, pravidlo nasazení | skoro nikdy v rozpisu | Směrnice / pořadatel |

Druh závodu → návrh bodování (odvozené z dat, potvrdit u pořadatele / počtářky):

| Druh | Body1 | Pozn. |
|---|---|---|
| ČP | `čp` | u ČP slalom startovku posílá předseda ZK (S26 §2) |
| NKZ | `nkz` | |
| ČPž (ČPŽ) | `čpž` | často spolu s OČ/OM → Body2/3 `bhz-č`/`bhz-m` |
| OČ / OM (VPZ) | `bhz-č` / `bhz-m` | `oč`/`om` bodují jen závodníky dané oblasti |
| MČR, MČRd, MČRž, družstva, OST, maraton | `nic` | |
| ČPj, ČPv | Eskymo metodu nemá → `nic` | žebříček vede počtářka |

## 3. Tahák pro Nový závod

`kalendar.py` vypíše tabulku pole → hodnota → zdroj. Před předáním zkontroluj a doplň:
- **Kategorie *:** všechny, které se pojedou (i předžáci PŽK/PŽC, C2X/C2M dle rozpisu). Chybějící
  kategorii nejde doplnit (nový sešit). Když si nejsi jistý, vezmi raději víc — prázdný list nevadí.
- **#řádek *:** víc než očekávaný max. počet lodí v kategorii (přihlášky + dohlášky).
- **Hlídky *:** jen pro závod družstev (vlastní sešit).
- **st. časy:** `ano`, když se ve startovce mají tisknout časy startu (ČP, KC individuál: pevné časy).
- **Místo:** z „Centrum, trať“ jen místo (např. „Strakonice, Podskalí“).

Pak člověk: Eskymo → Nový závod → vyplnit → OK → Uložit (`rrccc_nazev.ods`) → Import registru →
`param`: Prohlídka-zobrazit = ano → uložit. Skill: `inspect_workbook.py` na uložený soubor.

## 4. Vícedenní akce

Rozpis mívá víc závodů (např. č. 135 sobota, 136 neděle) → **dva sešity**. Přihlášky jsou často
společné; sloupec `zavody` v CSV exportu (čísla závodů) a veřejný seznam („Neúč.“) říkají, kdo jede
jen jeden den → `prihlasky.py … --zavod 135`.

## 5. Parametry pro startovku (nastaveni.json)

Z rozpisu a Směrnic sestav (a nech potvrdit):
- `poradi_kategorii` — pořadí na startu (např. `k1m c1z c2m pzk | c1m pzc k1z c2x`),
- nasazení podle typu soutěže (`startovka.md`), čísla (od 1, bloky po kategoriích, rezervy),
- interval a první start (když st. časy = ano; minima P 2.29.02: slalom 40 s, sjezd 30 s,
  3 min mezi kategoriemi).
