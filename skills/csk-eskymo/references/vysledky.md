# Výsledky: Canoe123, časomíra, ruční protokoly, kros

**Obsah:** 1 Zásady a stavy jízd · 2 Canoe123 XML (slalom) · 3 Časy z CSV / protokolů · 4 Kros ·
5 Po zápisu (body, tisk, odeslání) · 6 Kategorie pod 3 lodě, omluvy

## 1. Zásady a stavy jízd

- **Každá jízda zařazeného závodníka má čas, nebo stav.** Nikdy prázdná buňka — ve sjezdu/sprintu
  se prázdná buňka počítá jako čas 0 a skončí první.
- Stavy: `DNS` (nestartoval, neomluven), `DNS-A`, `DNS-B` (omluven — přiřazení k lhůtám S26 „do pátku
  18:00“ / „do porady“ není nikde definované, ověř s VR), `DNF`, `DSQ-R` (z jízdy), `DSQ-C` (ze závodu).
  Slalom: text stavu do času + **999** do trestných bodů. Sjezd/sprint: text stavu do času.
- Slalom: výsledek jízdy = čas (s) + trestné body (0/2/50), konečný = lepší jízda; shoda → druhá
  jízda → stejné místo (P 3.10). Sprint = lepší ze dvou jízd; sjezd klasik = 1 jízda; hlídky 1 jízda.
- Vstupní soubory pořadatele nepřepisuj; výstup = nový soubor. Každý den závodu = samostatný sešit.

## 2. Canoe123 XML → Eskymo (slalom)

Canoe123 (siwidata) exportuje XML (`Participants` + `Results`, časy v ms) za celý víkend nebo po
dnech. Převod dělá vendorovaný `canoe2eskymo.py` z repa
[canoe123-2-eskymo](https://github.com/CzechCanoe/canoe123-2-eskymo) (startovka i časy obou jízd,
doplní chybějící cizince do `cizi`). Obal `canoe123.py` přidává kontroly před a po.

```bash
python scripts/canoe123.py prehled export.xml --sablona zavod.ods     # dny, třídy, neznámé třídy, kapacita
python scripts/canoe123.py slalom export.xml zavod.ods zavod_vysledky.ods --day 15 --race 102 --date 15.08.26
python scripts/verify_workbook.py zavod_vysledky.ods --vysledky
```

- `--day` = poslední číslo `RaceId` (`K1M_BR1_15` → 15, den v měsíci). `--race/--date/--name`
  přepíší `param` B9/B8/B3; **BHZ ani nic dalšího** skript nepíše — u 2. dne se zeptej na číslo
  závodu, datum a BHZ a případně oprav `param` (Sheet.set_a1).
- Kdo je ve výstupu: kdo má aspoň jeden `Results` záznam pro den (DNS+DNS zařadit); jen v
  `Participants` = odhlášen → vynechán. Skrytý DNS (bez Status i Time) → DNS + 999, chybějící Pen → 0.
- **Neznámá třída** (není v mapě skriptu) → `prehled` ji hlasitě vypíše; nikdy ji tiše nevynechávej.
  Ženy jako K1W/C1W **i** K1Z/C1Z. Kapacita listu < počet závodníků → převod skončí chybou (nic
  neuloží) → nový sešit s vyšším #řádek. Víc lidí stejného jména, které ročník nerozliší → převod
  použije prvního a vypíše „! Nejednoznačná jména … OVĚŘ“ — to předej pořadateli.
- Známé zrady XML (skript řeší, ty jen kontroluj výpis): deble ve starém slepeném formátu
  (`ICFId` = RGC1‖RGC2, dělí se proti registru), `Id` ≠ `ICFId` (věří se ICFId), cizinci bez ICFId
  (vygeneruje `A` + 5 číslic navazující na `cizi`) nebo s vlastním A-kódem (zachová a doplní do `cizi`),
  diakritický překlep proti `reg` (Ú/Ů — fallback bez diakritiky), dva lidé stejného jména (ročník).
- Po převodu projdi **nově doplněné cizince** (výpis `cizi: doplněno …`): překlep jména cizince
  založí novou osobu; Čech, který nebyl nalezen v registru, by skončil jako falešný cizinec.
- Vícedenní závod: každý den z **čisté** šablony. Aby měli cizinci oba dny stejné A-kódy, zkopíruj
  řádky `cizi` z výstupu 1. dne do šablony 2. dne (Workbook + Sheet.set) a pak převáděj 2. den.
- Pořadí ve startovce je podle startovního čísla (bib), ne podle `StartOrder` z Canoe123.

## 3. Časy z CSV, časomíry nebo ručních protokolů

`casy.py` bere CSV s hlavičkou (`;` nebo `,`, UTF-8/cp1250):

```
kat;stc;jizda;cas;pen;stav
K1M;12;1;95,23;2;
K1M;12;2;1:33.10;0;
K1W;31;1;;;DNF
```

nebo se startem a cílem (denní čas; cíl < start = jízda přes celou hodinu):

```
kat;stc;jizda;start;cil;pen
c1m;41;1;10:02:15,32;10:03:58,07;4
```

Dvě cesty:
1. **Přímý zápis** do výsledkových listů: `python scripts/casy.py zapis casy.csv zavod.ods zavod_vysledky.ods`
   (řádek najde přes stč → id, funguje i po seřazení v Eskymu). Vypíše jízdy bez času i stavu;
   `--dns-chybejici` je doplní jako DNS — jen když to pořadatel potvrdí.
2. **Soubor pro Eskymo** „Natažení časů ze souboru“: `python scripts/casy.py eskymo casy.csv casy.txt`
   (`kat;stc;jizda;start;cil`, jen řádky se startem a cílem). Člověk ho načte ikonou v Eskymu a trestné
   body/stavy zadá formulářem. Hodí se, když pořadatel chce mít zadávání pod kontrolou v Eskymu.

Ručně psané protokoly (fotka, papír): přepiš do CSV, u nečitelných hodnot nic nedomýšlej — seznam
nejasností dej pořadateli. Trestné body ve slalomu musí být součtem 0/2/50 po brankách.

## 4. Kros (kayak cross)

Eskymo kros nepodporuje. Pro ČP KC se používají samostatné šablony (listy `<třída>-Q`/`-indiv.`
pro časovku a `<třída>-F` pro vyřazovací část) — nejsou to Eskymo sešity (bez `param`, bez vzorců).
Převod z Canoe123 (XT = time trial, XER = celkové pořadí):

```bash
python scripts/canoe123.py cross export.xml kros_sablona.ods kros_vysledky.ods --day 26 [--day-final 27]
```

Pravidla (KC 2024 + S26): kvalifikace časovkou, do vyřazování 8 nejlepších (SF 1-4-5-8 a 2-3-6-7,
finále A/B), body 32…2; FLT/RAL/DNF/DNS pořadí viz `pravidla-2026.md` §14. Sloupec „celk.“ nechává
skript prázdný (ověř s pořadatelem, jestli ho vyplnit ručně).

## 5. Po zápisu výsledků

1. `verify_workbook.py zavod_vysledky.ods --vysledky` (přepočet, úplnost jízd, 999 u stavů).
2. Člověk v Eskymu: otevřít, Ctrl+Shift+F9, Setřídit list (výsledek) — dopočte pořadí ve VK.
3. **Body** tlačítkem na každém výsledkovém listu (metoda z `param` Body1–3; skript body nepočítá).
4. Tisk všech VL (PDF), vyvěsit s časem zveřejnění a koncem lhůty pro námitky (20 min; dotaz 10 min).
5. Nahrát celý sešit přes odkaz z e-mailu **do 24 h** (VPZ; závody ČSK DV do pondělí 8:00).
   Záhlaví: pořadatel, název + číslo závodu, datum, VR, ředitel, stavitel trati, začátek/konec,
   trať, počet branek, stav vody, BHZ (P 2.21.01) — doplň, co v `param` chybí.

## 6. Kategorie pod 3 lodě, omluvy, předžáci

- Kategorie se hodnotí a vyhlašuje, jen když **odstartovaly aspoň 3 lodě** (S26 §1); jinak slučování
  podle příkladů A/B/C (mládež i veteráni). C2MIX < 3 → hodnotí se v C2M. Rozhoduje VR/pořadatel.
- Všechny omluvy mají být ve výsledcích (ČP, ČPw, KC); na VPZ lze nestartující v obou jízdách vynechat
  (S26 §6).
- Předžáci: samostatně, bez bodů. Cizinci (RGC `A…`) body nedostávají.
