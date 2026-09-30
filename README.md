# eskymo-skill

> Skill pro AI agenty (Claude a další): startovky a výsledky závodů ČSK ve vodním slalomu,
> sjezdu a sprintu v programu **Eskymo** — podle Pravidel ČSK DV a Směrnic pro závodění.

[![Tests](https://github.com/CzechCanoe/eskymo-skill/actions/workflows/test.yml/badge.svg)](https://github.com/CzechCanoe/eskymo-skill/actions/workflows/test.yml)

[Eskymo](https://eskymo.results.cz/) je rozšíření OpenOffice Calc, ve kterém pořadatelé závodů
ČSK DV zpracovávají startovní a výsledkové listiny a ve kterém se výsledky odevzdávají svazu.
Skill `csk-eskymo` pomáhá pořadateli připravit data z nesourodých podkladů, zapsat je do
sešitu Eskyma, všechno zkontrolovat a vede ho u kroků, které se dělají v Eskymu.

## Co umí

- **Založení závodu** z odkazu v kalendáři ČSK: hodnoty do dialogu Eskymo → Nový závod
  (číslo, BHZ, kategorie, bodování, pořadí kategorií…).
- **Přihlášky** z exportu prihlasky.kanoe.cz i z volných e-mailů a formulářů → kontrola proti
  registru (neznámá RGC, překlepy, předžáci, C2, cizinci, duplicity).
- **Individuální startovky**: nasazení podle Směrnic pro daný typ soutěže (los podle VT, žebříček,
  pevné pořadí), startovní čísla (P 2.18.03, průběžně, sestupně, rezervy, chybějící dresy),
  přehled „nasazeno podle“ ke kontrole pořadatelem.
- **Startovky hlídek** (MČR družstev): nasazení v obráceném pořadí loňských výsledků s párováním
  přes identitu oddílu a závodníky, písmena oddílů, číslování — ověřeno na MČR 2026.
- **Výsledky** z Canoe123 XML (slalom i kros, přes [canoe123-2-eskymo](https://github.com/CzechCanoe/canoe123-2-eskymo)),
  z CSV časomíry a ručních protokolů, nebo soubor pro Eskymo „Natažení časů ze souboru“.
- **Kontrola** sešitu přepočtem v LibreOffice: dotažená jména a oddíly, chyby vzorců, čísla,
  úplnost jízd.
- **Pravidla**: výtah Pravidel ČSK DV 2022 a Směrnic 2026 s citacemi a kontrola, jestli pro
  sezónu závodu nevyšly nové Směrnice.

Sešit závodu vytváří vždy Eskymo (Nový závod, Import registru). Skill píše jen do vstupních
buněk a kroky v Eskymu (tisk, body, odeslání) nechává člověku — s přesným návodem.

## Instalace

**Claude Code** (plugin z marketplace v tomto repu):

```
/plugin marketplace add CzechCanoe/eskymo-skill
/plugin install csk-eskymo@czechcanoe
```

**Claude desktop / claude.ai / Cowork**: stáhni `csk-eskymo.zip` z
[Releases](https://github.com/CzechCanoe/eskymo-skill/releases) nebo z artefaktu posledního běhu
[Actions](https://github.com/CzechCanoe/eskymo-skill/actions) (případně `python tools/build_skill_zip.py`)
a nahraj ho v Nastavení → Capabilities → Skills.

**Jiné harnessy** (standard [Agent Skills](https://agentskills.io)): zkopíruj složku
`skills/csk-eskymo` do adresáře skillů daného nástroje (např. `~/.claude/skills/`).

Požadavky: Python 3.10+ a `pip install -r skills/csk-eskymo/scripts/requirements.txt`.
Pro kontrolní přepočet LibreOffice (`soffice` v PATH, nebo proměnná `ESKYMO_SOFFICE`).
Eskymo samo běží u pořadatele v Apache OpenOffice.

## Příklady zadání

- „Tady je export přihlášek a prázdný sešit z Eskyma na OČ slalom ve Strakonicích. Udělej
  startovku, los podle VT, čísla po kategoriích, chybí nám dres 13.“
- „Převeď výsledky z Canoe123 (sobota i neděle) do Eskyma.“
- „MČR družstev ve sprintu: přihlášky, loňské výsledky a šablona jsou ve složce. Čísla klesající
  od 70, mezi kategoriemi pár volných.“
- „Co mám nastavit v Eskymu pro závod https://www.kanoe.cz/zavody/slalom-sjezd?link=7511?“
- „Jak se sestavuje startovka na MČR dorostu ve slalomu?“

## Struktura

```
skills/csk-eskymo/          ← samotný skill
  SKILL.md                  rozcestník a zásady
  references/               sešit Eskyma, GUI, přihlášky, startovky, hlídky, výsledky,
                            kontrola, úskalí, výtah pravidel + manifest zdrojů
  scripts/                  Python nástroje (lxml vrstva ODS, kontrola, přihlášky,
                            startovka, hlídky, časy, Canoe123, kalendář, pravidla)
    vendor/canoe123_2_eskymo/  připnutá kopie převodníku Canoe123 → Eskymo
tests/                      testy nad anonymními fixtures
tools/                      výroba fixtures, synchronizace vendoru, zip skillu
.claude-plugin/             plugin + marketplace pro Claude Code
```

## Vztah k canoe123-2-eskymo

Převod Canoe123 XML → Eskymo žije v repu
[CzechCanoe/canoe123-2-eskymo](https://github.com/CzechCanoe/canoe123-2-eskymo) (samostatně
použitelné skripty s vlastními testy). Skill má **připnutou kopii** (`scripts/vendor/`, commit ve
`VENDOR.md`), aby fungoval offline a v Cowork a aby se chování neměnilo během sezóny. Opravy jdou
upstream jako PR a sem se přenesou `python tools/sync_vendor.py --ref <commit>`.

## Pravidla a sezóny

Výtah pravidel je pro sezónu **2026** (Pravidla ČSK DV 2022 + Směrnice 2026). Skill si na začátku
práce ověří (`scripts/check_rules.py`), jestli pro sezónu závodu nevyšly nové Směrnice nebo opravy
příloh, a když ano, stáhne je a řídí se jimi. Jednou za sezónu se výtah aktualizuje — postup
v [AGENTS.md](AGENTS.md).

## Vývoj

```bash
python -m pip install -r skills/csk-eskymo/scripts/requirements.txt
python tests/run_tests.py                 # testy (s LibreOffice i přepočet)
python tools/build_skill_zip.py           # dist/csk-eskymo.zip
```

Pro AI agenty a přispěvatele: [AGENTS.md](AGENTS.md).

## Osobní údaje

Sešity Eskyma obsahují celý registr ČSK (včetně nezletilých a zdravotních prohlídek). Do repa
patří jen **anonymní** fixtures (`tools/make_fixtures.py` nahradí registr syntetickým a ověří,
že v souborech nezůstalo žádné původní příjmení ani klíč registru). Reálné podklady (`podklady/`)
jsou v `.gitignore`.

## Licence

MIT — viz [LICENSE](LICENSE). Vendorovaný převodník: MIT, CzechCanoe contributors.
Eskymo je software results.cz s.r.o.; tento projekt s ním jen spolupracuje přes formát souborů.
