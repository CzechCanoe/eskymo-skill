# Anatomie Eskymo sešitu (.ods)

Ověřeno na Eskymu 1.7.1–1.7.12 (layout je napříč verzemi stejný). Zdroje: rozbor rozšíření
1.7.11 a desítek reálných sešitů. Adresy jsou jako v Calcu (A1), indexy ve skriptech 0-based.

**Obsah:** 1 Typy sešitů · 2 Listy a pravidla pojmenování · 3 `param` · 4 `reg` a `cizi` ·
5 Startovka `<kat>_sl` · 6 Výsledky `<kat>` · 7 `hlidky` · 8 `id` a kapacita · 9 Pravidla pro zápis ·
10 Verze

## 1. Typy sešitů

| Typ | Poznáš podle | Vstupy (kam se píše) |
|---|---|---|
| A individuál slalom | `param` Disciplína = slalom, Hlídky = ne | `_sl` B stč, C rgc; výsledky L/M, O/P |
| A' individuál sjezd / sprint | Disciplína = sjezd / sprint | `_sl` B, C; výsledky N (a Q u sprintu) jako čas |
| B hlídky slalom | Hlídky = ano, slalom | `hlidky` A–F; `_sl` B stč, P H-RGC; výsledky L/M |
| C hlídky sprint / sjezd | Hlídky = ano, sprint/sjezd | `hlidky` A–F; `_sl` B, P; výsledky N (Q) |
| D kros | **bez listu `param`** (listy `MX1-indiv.`, `WX1-F`…) | není to Eskymo sešit, viz `vysledky.md` |
| E export XLS | `.xlsx` z Eskymo → Export XLS (hodnoty bez vzorců) | jen čtení (loňské výsledky) |

Eskymo nezná kros (disciplíny jen `slalom`, `sjezd`, `sprint`).

## 2. Listy a pravidla pojmenování

Pořadí záložek: `param`, `reg`, `cizi`, [`hlidky`], výsledkové listy `<kat>`, pak startovky `<kat>_sl`.
Kódy kategorií jsou **přesně 3 malé znaky**: `k1m k1z c1m c1z c2m c2z c2x pzk pzc for`
(`z` = ženy, `c2x` = mix, `pz*` = předžáci, `for` = předjezdci).

- Každý list, který není `param*`, `reg*`, `cizi*`, `pen*`, `hlidky*`, `x*` a nekončí `_sl`,
  bere Eskymo jako kategorii → **nepřidávej vlastní listy** (pomocný list musí začínat `x`).
- Pořadí listů generuje Eskymo podle disciplíny: slalom `for pzk pzc c1z c1m c2m k1z k1m c2z c2x`,
  sjezd/sprint `for pzk pzc c1m k1z k1m c1z c2m c2z c2x`. Pořadí kategorií **na startu** je věc
  rozpisu, ne listů.
- Všechny listy kromě `cizi` jsou zamčené prázdným heslem. Zápis přes XML zamčení neřeší.

## 3. `param` (hodnoty v B a D, popisky v A a C)

| Buňka | Popisek | Poznámka |
|---|---|---|
| A1 | „Eskymo verze: …“ | **nespolehlivé** (1.7.11 píše 1.7.10); skutečná verze je v patičce tisku |
| B3 | Název závodu | záhlaví tisků |
| B4 | Místo závodu | |
| B5 | Pořadatel | patička |
| B6 / B7 | Ředitel / Vrchní rozhodčí | |
| B8 | Datum závodu | **text `DD.MM.YY`** (Eskymo z něj bere rok) |
| B9 | Číslo závodu | číslo z kalendáře ČSK |
| B10 | BHZ | celé číslo (bodová hodnota závodu) |
| B11 | Disciplína | `slalom` / `sjezd` / `sprint` — zamčené, nejde změnit |
| B12–B14 | Body1–3 | `nic čp čpž nkz bhz-č bhz-m oč om` |
| B15–B18 | Hlídky / Penalty / Startovní časy / Počet jízd | `ano`/`ne` přesně malými písmeny; jízd 1/2 |
| B19 / B20 | Prohlídka-zobrazit / -znak | S26 §7b vyžaduje `ano` a `#` |
| B21 | Jazyk | `česky` / `anglicky` (jen texty záhlaví) |
| D3/D4, D6–D9, D11 | začátek/konec, teploty, průtok, vodočet, počet branek | jdou do XML exportu a tisků |
| A30:C30 → A31… | tabulka kategorií: kód, název, barva čísel | kódy zamčené; název a barvu lze psát |
| G4… (jen st. časy) | časový rozpis startů po kategoriích | viz `eskymo-gui.md` |
| B52 | Řádek/list (#řádek) | kapacita každé startovky/výsledků — zamčené |
| B57 / B58 / B59 | Import registru z webu / Adresa registru / Pracovní adresář | adresa má globální klíč — neopisuj ji do výstupů |

Parametry hledej **podle popisku** (`inspect_workbook.read_param`), ne podle adresy — řádky pod
tabulkou kategorií se posouvají podle počtu kategorií.

## 4. `reg` a `cizi`

`reg` (A–S) plní Eskymo → Import registru (CSV z ČSK, max. 4000 řádků, přepíše celý list):

| A RGC | B Prijmeni | C Jmeno | D Datum Narozeni | E Pohlavi | F VK | G KS | H C1S | I C2S | J KW | K C1W | L C2W | M Oddil | N Odd_nazev | O Vek | P #Kmen | Q zdr.prohl. | R datum | S oblast |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

- RGC je **číslo** (VLOOKUP páruje číslo s číslem). Prefix RGC = oddíl původní registrace, ne aktuální.
- D je ročník (text). E: `t` = muž, `f` = žena. F: `PZ ZM ZS DM DS U23 V␣ VM VS SV`, prázdné = dospělí.
- VT: **S = slalom, W = divoká voda (sjezd a sprint)**, ne „women“. Hodnoty `MT` (uložené s mezerou
  `" MT"`), `1 2+ 2 3+ 3`, prázdné = bez VT.
- M = zkratka oddílu (tiskne se; oficiální zkratky v Příloze 3 Směrnic), N = celý název.
- Q = `A` platná prohlídka (jinak Eskymo tiskne `#` před ročníkem), S = oblast `C`/`M` (body OČ/OM).
- Sešity 1.7.1 nemají sloupce Q–S.

`cizi` má sloupce A–P jako `reg`; RGC cizince **musí začínat `A`** (`A90001`). Plní se ručně nebo
skriptem (Canoe123 převod doplňuje chybějící cizince sám). Bez sloupce Q dostane cizinec `#`,
pokud je zapnuté zobrazení prohlídek — lze doplnit `A` do Q.

## 5. Startovka `<kat>_sl`

Řádek 1 titulek, řádek 2 hlavička, data od řádku 3 do 2+#řádek.

| Sl. | Hlavička | Typ | Obsah |
|---|---|---|---|
| A | id | předgenerované číslo | spojka na výsledkový list — **neměnit** |
| B | stč | **vstup** (číslo) | startovní číslo |
| C | rgc | **vstup** (individuál) / vzorec (hlídky) | RGC jako číslo; C2 text `"rgc1 rgc2"` (jedna mezera); cizinec `A…` |
| D–H | jméno, nar., vk, vt, oddíl | vzorce (VLOOKUP do `reg`/`cizi`) | C2 dvouřádkově; `#` před ročníkem = bez prohlídky |
| I, J | 1. / 2. jízda | vstup, nebo vzorec startovních časů | |
| K | poznámka | vstup | |
| L–O | nar1, nar2, vk1, vk2 | skryté pomocné (C2) | |
| P | H-RGC | **vstup u hlídek** | klíč hlídky `KAT-NN` do listu `hlidky` |
| R, S (st. časy) | `-` = závodník nezabere startovní interval v 1./2. jízdě | vstup | |

- **Fyzické pořadí řádků = pořadí startu** (startovní časy se počítají po řádcích).
- VT ve sloupci G: `"9"` = prázdné RGC nebo cizinec (bílé písmo). C2 = lepší VT posádky.
- Vyřazení závodníka: smazat rgc a stč, **řádek nemazat**.

## 6. Výsledkový list `<kat>`

Řádek ↔ závodník přes **id ve sloupci A** (VLOOKUP do `_sl`). Po Setřídit v Eskymu jsou řádky
přeházené — zapisuj podle id, ne podle pozice.

| Sl. | Slalom | Sjezd | Sprint |
|---|---|---|---|
| A id | spojka | | |
| B součet | vzorec (skrytý) | | |
| C poř. | `RANK` jako text `1.` | | |
| D | pořadí ve VK (`1/`, píše Eskymo při tisku/řazení) | | |
| E–K | vk, stč, rgc, jméno, nar., vt, oddíl (ze `_sl`) | | |
| L / M | **čas 1. jízdy (s, číslo) / trestné body** | — | — |
| N | výsl. 1 = L+M (vzorec) | **čas (hodnota času)** | **1. jízda (čas)** |
| O / P | **čas / tr. body 2. jízdy** | — | — |
| Q | výsl. 2 | — | **2. jízda (čas)** |
| R celk. | MIN(N;Q) — lepší jízda | = N | lepší jízda |
| S–U | body1–3 (píše tlačítko Body) | | |
| V–Y | start/cíl 1. a 2. jízdy `MM:SS,cc` (pro Přepočet časů) | | |

- Stav jízdy: slalom = text `DNS`/`DNS-A`/`DNS-B`/`DNF`/`DSQ-R`/`DSQ-C` v L (O) **a 999 v M (P)**
  → DNF/DSQ jízda se počítá jako 999 s; z pořadí vypadne jen DNS v obou jízdách.
  Sjezd/sprint = text stavu v N (Q).
- „Nezadáno“: slalom prázdná buňka (= 10000), sjezd/sprint `=TIMEVALUE("59:59,99")`.
  **Prázdné N/Q ve sjezdu = čas 0 → první místo.** Nikdy nenechávej prázdné.
- Body se nepočítají vzorcem, ale tlačítkem Body (tabulka T-4 75…1, nebo BHZ algoritmus).

## 7. `hlidky` (jen Hlídky = ano)

Řádek 1 hlavička, data od řádku 2. Vstupy **A–F**, zbytek vzorce (M:AU skryté).

| A H-RGC | B lodní katg. | C/D/E RGC1–3 | F oddíl A/B/C | G–L REG, jméno, nar, vk, vt, oddíl |
|---|---|---|---|---|
| `K1M-01` (text) | `K1`/`C1`/`C2` | číslo; C2 člen `"a b"`; cizinec `A…` | písmeno nebo prázdné | trojřádkové vzorce |

- `_sl` hlídek: C–H jsou VLOOKUP do `hlidky` přes P; píše se jen B (stč) a P (H-RGC).
- VT hlídky podle B a disciplíny: slalom KS/C1S/C2S, jinak KW/C1W/C2W.
- **Překlep `uuper(`** ve sloupci AU (každá hlídková šablona 1.7.1–1.7.10): u C2 hlídek → `#NAME?`
  ve VT. Oprav na kopii `patch_formulas('uuper(', 'UPPER(')` (dělá `hlidky.py zapis`) a řekni to.
- Neúplná hlídka (oddíl zatím nahlásil jen první loď) je v pořádku — oddíl pak vypadá `SKK VM\n\n B`.

## 8. `id` a kapacita

- `id` v `_sl` je statické číslo; ve výsledkovém listu je tatáž množina id (po řazení v jiném pořadí).
  Každé id musí být ve výsledkovém listu právě jednou — duplicita = Eskymo zdvojí závodníka
  (`inspect_workbook.py` hlásí). Canoe123 převod id přečísluje sám.
- Kapacita = `param` #řádek (B52; výchozí 150, u hlídek pořadatelé volí méně, např. 60). Víc lodí se nevejde — sešit je potřeba
  založit znovu s vyšším #řádek (vzorce jsou natvrdo na rozsah).

## 9. Pravidla pro zápis (shrnutí)

1. Piš jen do vstupních buněk (`Sheet.set_input` odmítne vzorec). Nikdy neměň `id`, nevkládej ani
   nemaž řádky a sloupce, nepřidávej listy.
2. RGC Čecha jako číslo bez vodicích nul; C2 a cizinec jako text. Stč jako číslo.
3. `ano`/`ne` malými písmeny, datum `DD.MM.YY` jako text.
4. Po zápisu jsou nacachované výsledky vzorců zastaralé → kontrola přes přepočet (`verify_workbook.py`),
   člověk v Eskymu Ctrl+Shift+F9.
5. ODS je ZIP: `mimetype` první a nekomprimovaný (řeší `eskymo_ods.Workbook.save`). Nepoužívej
   odfpy pro nový zápis (padá při dělení opakovaných buněk).

## 10. Verze

| Verze | Kde | Pozn. |
|---|---|---|
| 1.7.1 | sešity 2025 | bez `param` ř. 21 a 57–59, `reg` bez Q–S |
| 1.7.6 | Benátky 2026 | neveřejný build |
| 1.7.10 / 1.7.11 | 2026 | 1.7.11 = poslední veřejná (results.cz/eskymo/Eskymo.oxt, 4. 8. 2023) |
| 1.7.12 | exporty 2024/2025 | neveřejný build |

Vzorce jsou napříč verzemi stejné; liší se jen rozsahy podle #řádek a pár řádků `param`.
Eskymo oficiálně podporuje Apache OpenOffice (od 1.6.1); LibreOffice pro makra Eskyma ne,
pro přepočet vzorců při kontrole ano.
