# Úskalí z praxe

Všechno níže se reálně stalo (závody 2025–2026). Seřazeno podle oblasti; u každého, jak se to řeší.

## Data a registr

1. **Ženy jako W i Z.** Přihlášky a Canoe123 píšou K1W/C1W, někdy K1Z/C1Z; Eskymo list `k1z`/`c1z`.
   Bez mapování kategorie tiše zmizí (Benátky 2026: 100 závodnic). → `domena.kategorie_eskymo`,
   neznámé vždy hlásit.
2. **RGC jako číslo.** `reg!A` je číslo; RGC zapsané jako text VLOOKUP nenajde. Vodicí nuly (`009162`)
   z PDF a formulářů odstranit. C2 dvojice a cizinci jsou text. → `rgc_cell_value`.
3. **Prefix RGC ≠ oddíl.** RGC nese oddíl původní registrace; aktuální oddíl je `reg` sloupec M.
   Přestupy mezi oddíly jsou běžné.
4. **W v registru = divoká voda.** Sloupce KW/C1W/C2W jsou VT pro sjezd a sprint, ne ženy.
5. **Zkratky oddílů se mění mezi ročníky** (`Vys.Mýto` → `SKK VM`) → párování na loňské výsledky tiše
   selže. → `oddil_alias` + výpis nespárovaných loňských hlídek.
6. **Diakritický překlep** mezi zdrojem a registrem (Ú/Ů) → hledat bez diakritiky; **stejná jména**
   (otec a syn) → rozlišit ročníkem a oddílem, jinak se zeptat.
7. **Jeden závodník ve víc kategoriích** je v pořádku (K1 i C1, C1 i C2) — duplicita RGC napříč
   kategoriemi není chyba. Chyba je stejná loď 2× v kategorii nebo jeden člověk ve dvou C2 posádkách.
8. **Předžáci v běžných kategoriích** (přihlašovací systém je nerozlišuje) → přesun do `pzk`/`pzc`.
9. **Registr je stará kopie** (stav při Import registru) → nový závodník = prázdné jméno; řešení:
   znovu Import registru v Eskymu, ne ruční zápis do `reg`.

## Sešit a zápis

10. **Vzorce se po zápisu nepřepočítají** → kontrola jen po přepočtu (`verify_workbook.py`).
11. **odfpy padá** při dělení opakovaných buněk (`remove_from_caches: x not in list`) a je pomalé →
    nový kód jen přes `eskymo_ods.py` (lxml). Vendorovaný Canoe123 převod odfpy používá (ověřený).
12. **ODS ZIP**: `mimetype` první a nekomprimovaný, jinak Calc soubor odmítne.
13. **Opakované řádky/buňky** (`number-rows-repeated`, `number-columns-repeated`, sloučené buňky) →
    index v XML ≠ sloupec; vrstva je rozbaluje.
14. **Překlep `uuper(`** v každé hlídkové šabloně (sloupec AU listu `hlidky`) → `#NAME?` u C2 hlídek.
    Opravit na kopii, říct pořadateli (a autorovi Eskyma).
15. **Duplicitní / permutovaná `id`** ve výsledkovém listu (šablona z minulého závodu) → Eskymo zdvojí
    závodníka. `inspect_workbook.py` hlásí duplicity; zápis výsledků páruje přes id.
16. **Po Setřídit v Eskymu** jsou řádky přeházené → nikdy nepárovat výsledky podle pozice řádku.
17. **Kapacita #řádek** (B52) je pevná → víc lodí se nevejde, sešit založit znovu.
18. **Vlastní list v sešitu** (např. „poznámky“) Eskymo vezme jako kategorii a rozbije tisk/exporty.
19. **Prázdný čas ve sjezdu/sprintu** = čas 0 = první místo. Vždy čas, stav, nebo nechat 59:59,99.
20. **param A1 neříká verzi** (1.7.11 píše 1.7.10). Parametry hledat podle popisků.

## Nasazení a čísla

21. **„Obrácené pořadí“** = vítěz startuje poslední. Loňské pořadí brát podle poř., DNF/DSQ na konci
    v pořadí řádků (DNF má prázdné poř.).
22. **Dvě letošní hlídky z jedné loňské** → umístění zdědí jen jedna (dohad, vypsat).
23. **Dělená místa** loni → pořadí rozhodne pořadatel.
24. **„Vynechat pár čísel“** je neurčité → 2–3 varianty s rozpisem bloků. Chybějící dresy chodí po
    dávkách → přečíslování musí být jeden běh nad uloženým plánem.
25. **Rezerva na dohlášky spotřebovává reálná čísla** → i v rezervě přeskakovat chybějící dresy.
26. **Eskymo losuje od nejhorší VT a čísluje od 1 v každé kategorii**; P 2.17.01 uvádí skupiny od
    nejlepší a čísla navazující (kategorie od čísla končícího 1). Směr je volba pořadatele.
27. **Nezařazení v žebříčku** (S26: „na začátek … od nejlepší VT po nejhorší“) — doslovné znění jde
    proti intuici; vždy ukázat pořadateli.
28. **Písmena hlídek** — deklarovaná oddílem jsou identita; přidělená jsou dohad a pořadatel je
    může zrušit (ČV 2026 nakonec bez písmen).

## Canoe123

29. Deble ve **starém slepeném ICFId** (`108112032` = `1081`+`12032`) → dělí se proti registru;
    víc možných dělení = nejistota.
30. **Skrytý DNS** (bez Status i Time), **Time bez Pen** (= 0), `RaceId <unassigned>`, XML jen za
    jeden den, `Id` ≠ `ICFId` → řeší převod; ty kontroluj výpis `prehled`.
31. Cizinec s **překlepem jména** proti `cizi` → skript založí novou osobu; sloučit ručně.

## Prostředí

32. **kanoe.cz vrací 403** bez prohlížečového User-Agentu (WebFetch) → curl/urllib s UA.
33. **LibreOffice na Windows** tiše nic nevyrobí s `--outdir` s lomítky/8.3 cestou → `recalc.py`
    kopíruje do pracovního adresáře a volá s relativními cestami.
34. **Apache OpenOffice** neumí headless převod → pro kontrolu LibreOffice; Eskymo samo zůstává v AOO.
35. **Cowork**: `/tmp` se recykluje, dlouhé příkazy mají timeout → výstupy ukládat do složky uživatele,
    kroky dělat po částech. Visící `.git/index.lock` po spadlém gitu smazat (jen když git neběží).
36. **OneDrive** soubory nemusí být stažené; NFC/NFD v názvech souborů → glob nebo ASCII kopie.
