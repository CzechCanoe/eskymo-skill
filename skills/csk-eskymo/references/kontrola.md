# Kontrola sešitu

Nepřepočítaný sešit vypadá správně, i když je rozbitý: skripty zapisují jen vstupy a výsledky
vzorců (jména, oddíly, VT, pořadí) zůstávají ze šablony. Kontrola proto vždy znamená **přepočet**.

## 1. Automaticky

```bash
python scripts/verify_workbook.py vystup.ods --plan plan.json          # startovka
python scripts/verify_workbook.py vystup.ods --vysledky                 # výsledky
```

`verify_workbook.py` přepočítá kopii v headless LibreOffice (`recalc.py`, profil s vynuceným
přepočtem) a kontroluje:
- u každého zapsaného řádku startovky **jméno a oddíl** z registru (prázdné = RGC není v `reg`/`cizi`,
  nebo překlep), žádné `#N/A`, `#NAME?`, `#VALUE!`;
- startovní čísla: vyplněná, unikátní v kategorii (mezi kategoriemi varování), fyzické pořadí monotónní;
- počty a RGC proti `plan.json` / `lode.json` (nic nechybí, nic navíc);
- hlídky: chyby vzorců v listu `hlidky`;
- `--vysledky`: každá jízda má čas nebo stav, stav má 999, sjezd/sprint bez prázdných a nezadaných
  (59:59,99) časů, duplicitní id ve výsledkovém listu;
- INFO: závodníci bez platné prohlídky (`#` před ročníkem).

Návratový kód 0 = OK, 1 = problémy. **Bez LibreOffice** skript kontroluje uložené hodnoty — platné jen
u souboru, který člověk v Eskymu přepočítal (Ctrl+Shift+F9) a uložil (`--bez-prepoctu`).
Přepočtenou kopii (`*.prepocet.ods`) pořadateli nedávej — do Eskyma patří soubor ze skriptu.

## 2. Nezávislá druhá kontrola (u důležitých závodů)

U MČR, ČP a velkých převodů pusť **druhého agenta** (čerstvé oči, bez kontextu první práce):
přečte syrové vstupy (přihlášky, XML, loňské výsledky) a výstupní sešit vlastním kódem a porovná:
počty po kategoriích, 10–15 namátkových záznamů (první/poslední startující, C2, cizinci, DNS/DNF,
předžáci, ženy), nasazení proti pravidlu, rozsah a unikátnost čísel. Verdikt PROŠLO / NEPROŠLO
s konkrétními nálezy. V praxi takhle vyplavaly chyby, které autor přehlédl.

## 3. Co zkontroluje člověk v Eskymu

1. Otevřít výstup v OpenOffice s Eskymem → Ctrl+Shift+F9.
2. Projít startovky: jména, ročníky, oddíly, VT vyplněné; `#N/A` nikde; C2 dvouřádkově.
3. `param`: název, datum, číslo, BHZ, Body, Prohlídka-zobrazit = ano.
4. Výsledky: Setřídit list (výsledek), Body, náhled tisku.

## 4. Formát předávací zprávy

```
Hotovo: zavod_startovka.ods (… lodí: K1M 25, C1Ž 5, …; stč 1–72, vynecháno 13)
Ověřeno: přepočet LibreOffice — jména a oddíly dotažené u všech, žádné chyby vzorců.
K rozhodnutí:
  1. …  (konkrétně: kdo, co, návrh)
Opravy šablony: překlep uuper( → UPPER( (61 buněk, jen ve výstupu).
V Eskymu: otevřít, Ctrl+Shift+F9, zkontrolovat, Tisk všech SL.
```
