# Startovka hlídek (závod družstev)

Hlídka = družstvo **tří lodí stejné kategorie** (3×K1, 3×C1, 3×C2); jede jednu jízdu, čas se měří
do dojezdu třetí lodi. Sešit se zakládá v Eskymu s **Hlídky: ano** (vlastní sešit, list `hlidky`).
Ověřeno na MČR družstev 2026 (sprint České Vrbné — výstup skriptu je buňka po buňce shodný se
startovkou, která se jela; slalom Lipno).

## 1. Pravidla (citace v `pravidla-2026.md` §7)

- **Nasazení MČR družstev** (dospělí sjezd+sprint, dorost, žáci): „v obráceném pořadí loňských
  výsledků“ — loňský vítěz startuje poslední. U MČR družstev dospělých ve slalomu S26 nasazení
  neuvádí → rozpis / pořadatel.
- Interval: slalom 90 s, sjezd/sprint 60 s; mezi kategoriemi ≥ 5 min.
- Čísla (P 2.18.03): buď stejná různobarevná (1, 1, 1), nebo se stejnou poslední číslicí (23, 33, 43).
  V praxi 2026: jedno číslo na hlídku (ČV: klesající napříč závodem s rezervami; Lipno: bloky
  po kategoriích).
- Mistrovské závody: jen oddílová družstva (jedna C2 smí být kombinovaná). Právo startu: aspoň
  jeden člen odstartoval v individuálním závodě kategorie; doplnit lze až dvěma loděmi bez práva
  startu. Smíšené pohlaví: 1–2 ženy smí jet v mužském družstvu (P 2.09.02).
- Víc hlídek oddílu v kategorii se rozlišuje písmenem (A/B/C) — Pravidla to neřeší, je to zvyklost.

## 2. Data

- **Letošní hlídky** (`hlidky.json`): z CSV exportu (oddíly často přihlásí jen **první loď**,
  zbytek doplní později; počet řádků oddílu v kategorii = počet hlídek):
  `python scripts/hlidky.py z-prihlasek lode.json -o hlidky.json`. Z volných přihlášek ho sestav
  sám — `lode` až tři RGC (C2 loď `"a b"`), `pismeno` jen když ho oddíl **deklaroval**.
- **Loňské výsledky**: nejlépe loňský sešit Eskyma `.ods` (v kalendáři u závodu, ikona XLS) — má
  i list `hlidky` s písmeny; nebo Export XLS `.xlsx`. PDF jen jako nouze.
  `python scripts/hlidky.py loni loni.ods -o loni.json` (pořadí podle poř., DNF/DSQ na konci).
  **Ověř, že je to stejná disciplína** (sprint ≠ slalom; křížem se hlídky nespárují).

## 3. Nasazení (`hlidky.py nasad`)

Návaznost letošní hlídky na loňskou, v tomto pořadí:
1. **identita oddíl + písmeno** — jen když má letos hlídka písmeno deklarované (USK A ↔ loni USK A);
2. **přes závodníka, ale jen v témže oddílu** (závodníci přestupují; bez podmínky by si přestupující
   odnesl umístění starého oddílu);
3. **zbylá loňská umístění oddílu** podle síly (lepší VT, pak pořadí v přihláškách);
4. jinak **nová** → na začátek, mezi sebou od nejslabší VT (`nove_razeni`).

Pak startovní pořadí: nové, potom navazující od loňského nejhoršího k vítězi.
Přehled ukáže u každé hlídky „nasazeno podle“ a na konci **loňské hlídky bez návaznosti** — to je
signál přejmenovaného oddílu (zkratky se mezi roky mění, např. `Vys.Mýto` → `SKK VM` →
`oddil_alias`) nebo přestupu. Sporné (dvě letošní hlídky z jedné loňské, dělená místa, přestup)
předlož pořadateli.

```bash
python scripts/hlidky.py nasad hlidky.json zavod.ods --loni loni.json -c nastaveni.json -o plan.json --prehled nasazeni.md
python scripts/hlidky.py zapis plan.json zavod.ods zavod_startovka.ods -c nastaveni.json --prehled nasazeni.md
python scripts/verify_workbook.py zavod_startovka.ods
```

`nastaveni.json` (MČR družstev sprint 2026):
```json
{"poradi_kategorii": ["C1M", "K1W", "K1M", "C1W", "C2M"],
 "nasazeni": {"nove": "zacatek", "nove_razeni": "vt-nejslabsi-prvni", "pismena": "podle-nasazeni"},
 "oddil_alias": {"Vys.Mýto": "SKK VM"},
 "cisla": {"rezim": "sestupne", "start": 70, "mezera": 5, "vynechat": [41, 66]}}
```

**Písmena** (`pismena`): `deklarovana` (ponech z přihlášek), `podle-nasazeni` (A = nejlépe nasazená,
tj. startuje nejpozději), `podle-prihlasky`, `zadna`. Pořadatel se může rozmyslet (ČV 2026: nakonec
bez písmen) — je to přepínač, ne zapečené chování. Změna písmen = jen znovu `zapis`.

**Pestrost** (aby nejely bloky jednoho oddílu za sebou) je lidský úsudek: vygeneruj čisté pořadí,
případné prohození udělej v `plan.json` s důvodem.

## 4. Zápis (co skript dělá)

- list `hlidky`: A H-RGC (`K1M-01`, pořadí na startu), B lodní kategorie, C–E RGC lodí (C2 `"a b"`),
  F písmeno; chybějící lodě prázdné (oddíl se pak zobrazí `SKK VM\n\n B` — v pořádku);
- `<kat>_sl`: B stč a P H-RGC ve **fyzickém pořadí startu**;
- na kopii opraví překlep šablony `uuper(` → `UPPER(` (jinak `#NAME?` u C2) a vypíše to.

Doplnění posádek později: uprav `lode` v `plan.json` a spusť `zapis --prepsat` (čísla i pořadí zůstanou),
nebo doplní pořadatel ručně v Eskymu do listu `hlidky`. Exporty → Formuláře hlídky vyrobí formuláře pro oddíly.

## 5. Co se zeptat

Pravidlo nasazení (pokud to není MČR s pravidlem ze Směrnic), pořadí kategorií (musí sedět s rozpisem),
číslování (směr, start, rezervy, chybějící dresy, max. dresů), písmena (tisknout?), nová hlídka bez
loňska (začátek/konec), sporné návaznosti. Otázky pokládej s hotovými variantami a rozpisem.
