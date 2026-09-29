# Pravidla ČSK DV + Směrnice 2026 — výtah pro startovky a výsledky v Eskymu

Stav k **29. 9. 2026**. Výtah je pracovní pomůcka skillu, **ne náhrada** Pravidel ani Směrnic.
U všeho, co ovlivňuje pořadí, čísla nebo body, je citace (`P` = Pravidla 2022, `S26` = Směrnice 2026);
krátký doslovný úryvek tam, kde záleží na formulaci. Zdroje, URL a kontrolní součty jsou
v `pravidla-manifest.json`.

**Platnost:** Směrnice se vydávají na každý rok (obvykle prosinec–únor), Pravidla zhruba po 4 letech.
Před prací na závodě spusť `python scripts/check_rules.py --sesit zavod.ods`. Když hlásí novou sezónu
nebo změněný dokument, stáhni aktuální znění (`--stahnout DIR`), přečti dotčené části (§1 soutěže,
§2 přihlášky a čísla, §6 výsledky, přílohy) a řiď se jimi — tento výtah pak ber jen jako mapu,
kde hledat. Rozdíly řekni pořadateli. Při ročním updatu skillu se výtah přepíše
(viz AGENTS.md v repu).

**Obsah:** 0. Zdroje, hierarchie, zkratky citací · 1. Systém soutěží 2026 (S26 §1) · 2. Kategorie · 3. Výkonnostní třídy (VT) · 4. Právo startu · 5. Startovní listina – obecná pravidla · 6. Startovní listina podle typu soutěže (nasazení) · 7. Závod družstev (hlídky) · 8. Časový pořad, intervaly, pořadí kategorií · 9. Přihlášky, dohlášky, omluvy, pokuty, startovné · 10. Průběh a výpočet výsledků · 11. Výsledková listina – povinné náležitosti, zveřejnění, odeslání · 12. Bodování · 13. Kombinace (S26 §1 › KOMBINACE, P 2.06.04) · 14. Kayak cross (S26 §1, KC24) · 15. Přílohy Směrnic 2026 · 16. Co z toho plyne pro tvorbu startovky / výsledků v Eskymu (checklist) · 17. Nejasnosti / co je věcí pořadatele (rozpis závodu) · 18. Detekce nové sezóny (podrobně v manifestu)

## 0. Zdroje, hierarchie, zkratky citací

| zkratka v digestu | dokument | platnost |
|---|---|---|
| **P** | Pravidla sekce kanoistiky na divokých vodách (ČSK DV), vydání 2022 | schválena VV 8. 3. 2022, „Platnost od 8. 3. 2022“. **K 29. 9. 2026 je to stále poslední vydání** (žádné novější na kanoe.cz). |
| **S26** | Směrnice pro závodění v České republice pro rok 2026 | schváleno ZK 17. 12. 2025, VV 20. 1. 2026, zveřejněno 21. 1. 2026 |
| **S26-P1…P5** | Přílohy č. 1–5 Směrnic 2026 | P1 nahrazena opravou 28. 1. 2026 (viz §15) |
| **KC24** | Pravidla Kayak Cross 2024 (samostatné PDF, nahrazuje Část 4 „Extreme Canoe Slalom“ v P) | zveřejněno 14. 4. 2024, stále aktuální |
| **SČR22** | Směrnice pro činnost rozhodčích 2022 | okrajově (zpráva VR, body rozhodčích) |

Citace: `P 2.17.01` = článek Pravidel; `S26 §1 › ČP` = Směrnice 2026, paragraf 1, oddíl „ČP (Český pohár ve slalomu)“
(Směrnice nemají číslované odstavce, cituje se paragraf + nadpis oddílu).

**Hierarchie:** Pravidla → Směrnice pro daný rok („prováděcí nařízení k Pravidlům… nesmí být v rozporu s Pravidly“, `P 1.03.01`;
Pravidla na mnoha místech výslovně delegují na Směrnice, např. `P 2.17.01` „Pokud Směrnice pro závodění nestanovují jinak“)
→ **rozpis závodu** (`P 2.13`, závazný pro konkrétní závod) → rozhodnutí vrchního rozhodčího (VR) u věcí, které Pravidla neřeší (`P 2.27.01 f`).
Odchylku od rozpisu může VR povolit jen v souladu s Pravidly a při jednomyslném souhlasu pořadatele a vedoucích družstev (`P 2.27.01 a`).

---

## 1. Systém soutěží 2026 (S26 §1)

| disciplína | soutěž | rozsah 2026 | lodní kategorie |
|---|---|---|---|
| slalom | **ČP** Český pohár | 6 závodů vč. MČR (ČP 5 = MČR dospělých, ČP 6 = MČR U23) | C1Ž, C1M, K1Ž, K1M |
| slalom | **NKZ** národní kvalifikační závody | 6 závodů, postup do ČP 2027 | K1M, K1Ž, C1M, C1Ž |
| slalom | **ČPJ** ČP juniorů | 7 = 6 NKZ + MČR dorostu | (jen hodnocení mládeže) |
| slalom | **ČPŽ** ČP žáků | 7 = 6 ČPŽ + MČR žáků | C1Ž, C1M, K1Ž, K1M |
| slalom | **ČPV** ČP veteránů | 6 závodů v rámci vybraných VPZ („pouze s licencí“) | dle VPZ |
| slalom | **VPZ** veřejné postupové závody | dle kalendáře, BHZ 4–6 | C1Ž, C1M, K1Ž, K1M, C2M, C2MIX |
| sjezd | **ČPw** | 5 klas. sjezdů + 5 sprintů vč. MČR v obou | C1M, K1Ž, K1M, C1Ž, C2M |
| sjezd | **ČPJw** | 4 klasik + 4 sprint vč. MČR dorostu | totéž |
| sjezd | **ČPŽw** | 3 klasik + 2 sprint vč. MČR žáků | totéž |
| sjezd | **VPZw** | dle kalendáře, BHZ 4–6 | totéž + lze vypsat C2 MIX |
| kayak cross | **ČP KC** | 7 závodů vč. MČR (ČP 4 = MČR dospělých, ČP 7 = MČR U23) | K1M, K1Ž |
| kayak cross | **ČPJ KC** | 8 závodů vč. MČR (ČPJ 4 = MČR dorostu) | K1M, K1Ž |
| kombinace | **MČRkž** žactvo | slalom + sprint (kanoe) / slalom + sprint + KC (kajak) | ročníky 2012–2015 dohromady |
| kombinace | **MČRkd** dorost | slalom + KC | K1 i C1 (viz §13) |

Klíčové věty:
- `S26 §1`: „Závody ČP, ČPJ, ČPŽ, včetně MČR všech věkových kategorií ve slalomu se vypisují pouze pro kategorie C1Ž, C1M, K1Ž, K1M.“ → **C2 ve slalomu jen na VPZ.**
- `S26 §1`: ve sjezdu „V kategorii C2M mohou startovat i ženy.“; ve VPZ slalomu „V kategorii C2MIX mohou startovat i pouze ženské posádky.“
- `S26 §1`: v žákovských sjezdových soutěžích max. **2 individuální + 2 družstva** na závodníka.
- `S26 §1`: na sjezdových závodech lze startovat i na slalomových lodích (váha, zabezpečení proti potopení).
- Mistři ČR se vyhlašují: dospělí, U23, DS, DM, ŽS, ŽM, veteráni (slalom i oba sjezdy).
- Raft **není** součástí Pravidel ČSK DV ani S26 (raftové závody mají vlastní „Pravidla raftových závodů“ SVoČR na `/rafting/pravidla`).

---

## 2. Kategorie

### 2.1 Lodní kategorie (P 1.05, T-2)

| kód | název | kde | pozn. / aliasy |
|---|---|---|---|
| K1M | K1 muži | slalom, sjezd, KC | |
| K1Ž | K1 ženy | slalom, sjezd, KC | přihlašovací systém exportuje **K1W**, Eskymo list **k1z** |
| C1M | C1 muži | slalom, sjezd | |
| C1Ž | C1 ženy | slalom, sjezd | export **C1W**, Eskymo **c1z** |
| C2M | C2 muži | slalom (jen VPZ), sjezd | ve sjezdu mohou jet i ženy |
| C2MIX (C2X) | C2 mix | „jen slalom“ (`P 1.05`); S26 dovoluje i VPZw | ve slalomu smí i čistě ženská posádka |
| C2Ž | C2 ženy | „jen sjezd“ (`P 1.05`) | ve S26 zmíněna jen v §6 (když se nekoná, jedou v C2M) |

Družstva (`P 1.05.02`): 3×K1Ž, 3×K1M, 3×C1Ž, 3×C1M, 3×C2Ž (jen sjezd), 3×C2M, 3×C2mix (jen slalom). T-2: „Závody družstev je možné vypsat ve stejném rozsahu.“

### 2.2 Věkové kategorie pro rok 2026 (P T-3, P 2.33.02, S26 §1)

Rozhoduje **věk dovršený v kalendářním roce**; do vyšší skupiny se přechází vždy k 1. lednu (`P 2.33.02`).

| věková kategorie | zkratka (výsledky / Eskymo) | věk v r. 2026 | **ročníky 2026** | zdroj |
|---|---|---|---|---|
| Předžáci | pž / PZ (listy PZK, PZC) | 6–10 | **2016–2020** | S26 §1 › Závody předžáků |
| Žáci mladší | žm / ZM | 11–12 | **2014–2015** | P T-3 |
| Žáci starší | žs / ZS | 13–14 | **2012–2013** | P T-3 |
| Dorost mladší | dm / DM | 15–16 | **2010–2011** | P T-3 |
| Dorost starší | ds / DS | 17–18 | **2008–2009** | P T-3 |
| U23 | U23 | „11 - 23 let“ | **2003–2015** (jako samostatná VK v Eskymu 19–23 = 2003–2007) | P T-3, S26 §1 |
| Dospělí | (bez označení) | všichni | — (19–34 let = 1992–2007 bez VK) | P 2.15, P 2.21.01 |
| Veteráni mladší | VM | 35–44 | **1982–1991** | S26 §1 › MČR veteránů |
| Veteráni | V | 45–54 | **1972–1981** | tamtéž |
| Veteráni starší | VS | 55–64 | **1962–1971** | tamtéž |
| Super veteráni | SV | 65+ | **1961 a starší** | tamtéž |

Poznámky:
- „Junioři“ (ČPJ, „pořadí juniorů“ v NKZ/ČPw) = mládež do dorostu staršího včetně, tj. ročník **2008 a mladší** (ICF junior = U18). Explicitní definice v S26 chybí.
- ČPŽ a MČRkž pracují s „ročníky 2012–2015“ = ŽS + ŽM.
- Ukázková jízda NKZ se losuje jen z ročníků **2007 a starších** (`S26 §1 › NKZ`).
- KC: právo startu „kategorie DM a starší“ = ročník **2011 a starší** (`S26 §1 › ČP KAJAK KROS`).
- Mimořádné výjimky pro MSJ 2027 pro ročník 2012 (`S26 §1 › ČP KAJAK KROS`).
- Žák smí začít výkonnostně závodit v roce, kdy dovrší 11 let (`P 2.33.01`). Mládež smí startovat s dospělými, pokud je závod přístupný její věkové skupině a má předepsanou VT (`P 2.33.03`).
- Věková kategorie posádky C2 / družstva: Pravidla ji **neurčují**. Eskymo „určí společnou věkovou kategorii“ (v datech z 2025: družstvo 2009/2009/2006 → U23, tj. podle nejstaršího člena). Viz Nejasnosti.

### 2.3 Předžáci (S26 §1 › Závody předžáků)
- Jen na **postupové závody s BHZ 4 ve slalomu**; ročníky 2016–2020; o startu rozhoduje pořadatel s VR.
- Samostatně **vložený závod**, max. 2 kategorie; při ≥3 děvčatech samostatná kategorie; výsledky samostatně; označení „pž“; **závod se neboduje**.
- Musí být člen ČSK DV, v registru s RGC a lékařskou prohlídkou. Předžáci body nepřinášejí ani nezískávají (`S26 §6`).
- Pořadí skupin: ČPŽ „K1M, C1Ž a předžáci K1 – obě jízdy a C1M, K1Ž, předžáci C1 – obě jízdy“ (`S26 §1 › ČPŽ`); VPZ doporučení analogicky (§8 tohoto digestu).

### 2.4 Minimální počet lodí a slučování (S26 §1, P 2.04.03, P 2.42.05)
- `S26 §1`: „Aby mohla být věková a lodní kategorie hodnocena a vyhlášena, musí odstartovat minimálně 3 lodě nebo družstva.“ (odkaz na `P 2.04.03`, `P 2.09.01`).
- Mládež – příklady S26: (A) 2 lodě DS + ≥3 DM → vyhlašuje se jen DM; (B) ≥3 DS + ≤2 DM → všichni v DS; (C) ≤2 DS + ≤2 DM, celkem ≥3 → „dorost celkově“.
- Veteráni – obdobně (A) 2 VM + ≥3 VS → jen VS; (B) ≥3 V + ≤2 VS → všichni ve V; (C) po ≤2 v SV/VS/V, celkem ≥3 → veteráni celkově. „V případě, že není naplněna starší věková kategorie, je tato starší věková kategorie přiřazena k mladší věkové kategorii.“
- Do oblastních žebříčků se nezapočítávají kategorie, „ve kterých nebyly **klasifikovány** nejméně tři lodě“ (`P 2.42.05 a`) – pozor, S26 mluví o „odstartovaly“.
- C2MIX na VPZ: samostatně jen při ≥3 odstartovaných lodích, jinak hodnoceny v C2M; nevypsaná C2MIX → v C2M (`S26 §1 › VPZ`).
- Družstva mladšího dorostu a žactva lze při malém počtu přiřadit ke staršímu (`P 2.06.03`).

### 2.5 Ženy v mužských kategoriích
- `P 2.39.04`: ženy mohou jet v kategorii mužů (K1, C1, C2), „pouze v případě, kdy se individuální závod některé z ženských kategorií neuskuteční“.
- `S26 §6`: neuskuteční-li se K1Ž, C1Ž, C2MIX nebo (sjezd) C2Ž, mohou tyto závodnice/posádky jet závod mužů a získat umístění i body do oblastního žebříčku.
- Družstva: viz §7.

---

## 3. Výkonnostní třídy (VT)

### 3.1 Stupně, značení, pořadí (P 2.34, 2.17.01)
- Stupně: **M (MT)**, **1**, **2+**, **2**, **3+**, **3**, bez VT (`P 2.34.01`). Ve startovkách/výsledcích se značí „M, 1, 2, 3“ (`P 2.17.01`); Eskymo/registr používá MT, 1, 2+, 2, 3+, 3, prázdné/0.
- Získávají se **zvlášť** pro slalom (S) a sjezd (W) (KC upravují Směrnice) a zvlášť K / C1 / C2 (`P 2.34.02`) → v registru sloupce KS, C1S, C2S, KW, C1W, C2W.
- `S26 §4`: VT získané v 2026 v C1 resp. C2M „jsou mezi těmito dvěma kategoriemi nepřenosné“.
- Platnost: od potvrzení do **31. 12. následujícího roku** (`P 2.35.01`). Potvrzuje počtář žebříčku v registru (`P 2.36.01`); registr aktualizuje VT „neprodleně“ po zveřejnění oficiálních výsledků (`S26 §7`).
- C2 s různými VT: „určuje vždy jen vyšší VT“ (`P 2.37.02`).
- Start v nesprávné VT → ztráta nároku na umístění a vyloučení (`P 2.37.01`); zjištěno až po závodě → umístění se ruší (`P 2.15.05`).

### 3.2 Jak se VT získávají pro další rok (S26 §1, §4)

| VT | slalom | sjezd (ČPw) | kayak cross |
|---|---|---|---|
| **MT** | 1.–3. místo v konečném pořadí ČP | 1.–3. v ČPw (C1M, K1Ž, K1M, C2M, C1Ž) | 1.–3. v ČP KC |
| **1. VT** | ČP 4.–20. (K1M, C1M, K1Ž), 4.–16. (C1Ž) | K1M 4.–20., C1M 4.–18., K1Ž a C2M 4.–15., C1Ž „první polovina klasifikovaných lodí (po odečtení závodnic s MT VT)“ | 4.–10. v ČP KC |
| **2+** | postupující z NKZ do ČP (K1M, C1M, K1Ž, C1Ž) (`S26 §1 › NKZ`, §4) | — | — |
| **2** | všichni zařazení do žebříčku ČP (bodovali ≥2×); MT/1 neobhájené; během sezóny splněním limitu (§3); po sezóně z oblastního žebříčku limitem nebo v prvních 33 % (po odečtení MT/1 a druhé oblasti); první polovina celkového žebříčku ČPŽ | MT/1 neobhájené; limit; prvních 33 % oblastního žebříčku (stejná metoda) | další zařazení v žebříčku ČP KC (bodovali ≥2×) |
| **3+** | (mimo C2 a C2mix) body min. ve 2 závodech v součtu ≥ 50 % limitu 2. VT | — | — |
| **3** | body min. ve 2 závodech (zařazení do žebříčku) | totéž | — |

MT a 1. VT z ČP 2026 platí „až pro rok 2027“ (`S26 §4`). V žebříčcích NKZ se neuvádějí lodě, které v ČP 2026 získaly MT/1. VT (`S26 §1 › NKZ`).

### 3.3 Limity pro zisk 2. VT (S26 §3, tabulka nadepsaná „pro rok 2025“)

Body v oblastním žebříčku (součet max. 5 nejlepších výsledků, `P 2.42.04`).

| oblast | slalom K1M | slalom C2M/C2mix | slalom K1Ž | slalom C1M | slalom C1Ž | sjezd K1M | sjezd C2M | sjezd K1Ž | sjezd C1M | sjezd C1Ž |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Čechy | 500 | 40 | 210 | 260 | 160 | 310 | 70 | 50 | 270 | 50 |
| Morava | 200 | 40 | 130 | 130 | 60 | 120 | 50 | 70 | 100 | 40 |

⚠ Nadpis říká „pro rok 2025“ (zřejmě nepřepsaný) a pořadí sloupců sjezdu (K1Ž 50 vs C1M 270 v Čechách) působí podezřele – převzato doslova z docx. Viz Nejasnosti.

### 3.4 Bodová hodnota závodu – oblastní žebříčky (P 2.42.04–07)
- Oblastní žebříčky (Čechy / Morava) ze všech postupových závodů oblasti; ve sjezdu i z ČPw (počítáno zvlášť pro obě oblasti). Každé lodi max. **5 nejlepších** výsledků (`P 2.42.04`). Do žebříčku se loď/dvojice (v nezměněné sestavě) zařadí až po bodech ze **dvou** závodů (`P 2.42.01`).
- Moravští závodníci bodují i na českých závodech a naopak (`P 2.42.04 b`). Kombinovaná česko-moravská C2M v ČPw přináší i získává body do obou oblastí (`S26 §1 › ČPw`).
- Nezapočítávají se: kategorie s <3 klasifikovanými loděmi; nepostupové závody (akademické MČR, maraton, nominační); MČRd, MČRž, MČRv, nejsou-li v rámci VPZ (`P 2.42.05`).
- **BHZ** 6/5/4 = počet bodů do oblastního žebříčku „za jednu odstartovanou loď 2. VT“; za MT a 1. VT dvojnásobek (12/10/8); 1 bod za loď 3. VT a 1 bod za **dvě** lodě bez VT (`P 2.42.07 b`). VR je povinen BHZ změnit, pokud trať neodpovídá (`P 2.42.07 a`).
- Do celkového počtu bodů se zahrnují všechny **odstartované** lodě včetně DNF a DSQ (s uvedením důvodu); cizinci neregistrovaní v ČSK DV a předžáci body nepřinášejí ani nezískávají (`S26 §6`, `P 2.21.02`, `P 2.11.02`).
- Jak se bodová „banka“ rozdělí mezi umístěné lodě, Pravidla 2022 **neuvádějí** – implementuje to Eskymo (volby bhz-č/bhz-m/oč/om). Viz §12.4.

---

## 4. Právo startu

### 4.1 Obecně (P 2.37–2.40)
- Přihlásit lze jen tam, kde závodník splňuje věkovou skupinu, VT a další podmínky; výjimky jen rozhodnutím ZK (`P 2.39.02`, `P 2.40`).
- Start za oddíl, v němž je registrován; povolena „závodní společenství“ ze dvou oddílů (`P 2.39.01`).
- **Víc kategorií:** na MČR, MČRd, MČRž, ČP a NKZ max. **3 individuální + 3 družstva**; jinde neomezeno, pokud neomezí rozpis; „jen tam, kde se dostaví na start včas ve vylosovaném pořadí“ (`P 2.39.03`). Žákovské sjezdové soutěže: max. 2 + 2 (`S26 §1`).
- Jeden závodník nesmí v jednom závodě jet C2 s více partnery v téže kategorii (`P 2.39.05`).
- Podmínky: registrační poplatek zaplacen do 31. 3. (S26-P5: 200 Kč/člen), platná lékařská prohlídka ne starší 1 roku v registru (`P 2.38.03`, `S26 §7`).

### 4.2 Podle soutěže (S26 §1)

| soutěž | právo startu |
|---|---|
| ČP slalom 2026 | lodě MT a 1. VT v kategorii + závodníci uvedení v **Příloze č. 1** (postup z NKZ 2025, oblastní žebříčky, vítěz ČPŽ, schválené výjimky) |
| MČR slalom dospělí / U23 | „Právo startu mají pouze účastníci ČP.“ |
| NKZ | nositelé 2. VT v K1M, K1Ž, C1M, C1Ž (MT a 1. VT startují také – první ve startovce) |
| MČR dorostu slalom | min. 2. VT (všechny kategorie) + individuální medailisté MČR žáků (ŽS, ŽM) a celkového pořadí ČPŽ; žáci jsou hodnoceni v DM |
| MČR žáků slalom | min. 2. VT + všichni zařazení v průběžném žebříčku ČPŽ 2026 (i ŽM) |
| ČPŽ slalom / sjezd | „určeny pouze pro žáky“; start předžáků upřesní rozpis |
| ČPw | min. **3. VT sjezd** nebo min. **2. VT slalom** v příslušné kategorii (u C2 stejná posádka); ČPw Vyšší Brod, Roudnice, České Vrbné bez VT; ČP Lipno podmínkou 2. VT; pořadatel může rozpisem zpřísnit; vedení RD juniorů může doplnit |
| MČR dospělí sjezd/sprint | všichni účastníci ČPw |
| MČR dorostu sjezd/sprint | bez omezení VT; žáci hodnoceni v DM |
| MČR žáků sjezd/sprint | bez omezení VT |
| VPZ / VPZw | dle rozpisu (pořadatel může omezit dle T-5) |
| ČPV / MČR veteránů | jako na VPZ |
| ČP / ČPJ KC | všichni členové ČSK DV kategorie DM a starší; ČP 4 (MČR) jen registrovaní v ČSK DV |

---

## 5. Startovní listina – obecná pravidla

### 5.1 Základní způsob (P 2.17.01) – platí, „pokud Směrnice pro závodění nestanovují jinak“
Startovní čísla se přidělují podle výkonnostních skupin v pořadí: (1) MT a 1. VT, (2) 2+, (3) 2, (4) 3+, (5) 3, (6) bez VT.
„Startovní listina může být sestavena i v obráceném pořadí.“ VR před závodem kontroluje startovní listinu, „zda se losovalo podle výkonnostních tříd“ (`P 2.27.01 i`) → uvnitř VT skupiny se **losuje**.
Střídání lodí ohlášené v přihlášce „by nemělo narušit start podle výkonnostních skupin“ (`P 2.17.02`).

Eskymo: tlačítko losování „přidělí startovní čísla od 1 po skupinách od nejhorších po nejlepší (0, 3, 3+, 2, 2+, 1, MT)“ – tj. obrácené pořadí. Pro opačný směr se čísla musí přečíslovat ručně (Eskymo příručka 1.7.3).

### 5.2 Startovní čísla (P 2.18)
- Dodává pořadatel, oboustranná (hrudník + záda), číslice ≥ 15 cm vysoké a 1,5 cm široké; v C2 má číslo přední závodník (příp. oba) (`P 2.18.01`).
- `P 2.18.03`: „Pro každou kategorii se přidělují čísla od nejnižších k nejvyšším, pokud možno v nepřetržité řadě. Každá kategorie musí začínat číslem, které končí jedničkou (např. 1, 11, 21, 101, atd.).“ Výjimku mohou tvořit závody ČP (dle Směrnic).
- **Družstva:** „buď stejná různobarevná čísla (např. 1,1,1), nebo čísla se stejnou poslední číslicí (23, 33, 43)“ (`P 2.18.03`).
- Ztráta/poškození čísla: 250 Kč (`P 2.18.02`); ČP slalom: náhradní číslo za 100 Kč/závod (`S26 §2`).
- **Výjimky ze Směrnic:**
  - ČP slalom: čísla „budou odpovídat umístění v ČP v roce 2025, lodě 2.VT budou seřazeny podle pořadí v NKZ a v oblastních žebříčcích a výjimek“; čísla jsou na celý seriál, vrací se po posledním ČP (Lipno) (`S26 §2 › Startovní čísla pro ČP`).
  - ČPw: „Startovní čísla budou přidělena od nejvyššího po nejnižší (poslední v kategorii ve startovní listině má číslo 1).“ (`S26 §1 › ČPw`)
  - KC individuál: startovka „v pořadí od nejvyššího čísla k nejnižšímu“, čísla z ČP 2025 (`S26 §1 › ČP KAJAK KROS`); `KC24 4.13` naopak čísla podle pořadí v time trialu (nejrychlejší = 1).

### 5.3 Další povinnosti ke startovce
- Rozpis musí uvést **datum sestavování startovní listiny**, vypsané lodní a věkové kategorie a VT, první start a **pořadí kategorií nebo skupin** (`P 2.13.02` body 8, 11, 12d).
- Startovní listinu dostanou vedoucí nejpozději na úvodní poradě (`P 2.19`). Ředitel závodu dohlíží na sestavení a vydání startovky (`P 2.24.01`).
- **Lékařské prohlídky:** „Ve startovní listině zhotovené v Eskymu je závodník bez platné lékařské prohlídky indikován znakem „#“ před ročníkem narození.“ Pořadatel **musí** zapnout zobrazení příznaku v parametrech sešitu (`S26 §7 b`; v Eskymu `param`: Prohlídka-zobrazit = ano, Prohlídka-znak = #).
- Přihlášky: uzávěrka **nejvýše 10 dní** před závodem, elektronicky (výjimka ČP slalom) (`P 2.15`). V přihlášce kategorie (u mládeže např. „C1 ds, C1 dm, C1 žs nebo C1 žm – dospělí se neoznačují“), RGC, jméno, VT, rok narození; střídání lodí jmenovitě (`P 2.15`). Přihláška bez správného RGC je neplatná (`P 2.15.05`). Při překročení rozsahu může pořadatel přijmout jen část, musí to oznámit e-mailem (`P 2.15.06`). E-mailovou přihlášku musí pořadatel potvrdit, jinak není přijata (`S26 §7`).
- Odvolání přihlášky je konečné; vklad se vrací, pokud byla odvolána před sestavením startovky (`P 2.16.03`). Změna v C2 jen písemně s ověřením VT (`P 2.16.01`).

---

## 6. Startovní listina podle typu soutěže (nasazení)

### 6.1 Přehledová tabulka

| soutěž | nasazení (kdo startuje první → poslední) | nezařazení v žebříčku | čísla | citace |
|---|---|---|---|---|
| **ČP slalom – kvalifikace** | žebříčky ČP 2025 + NKZ 2025 „v pořadí od nejhorších k nejlepším“ vč. postupujících z oblastí a výjimek; **jedna startovka pro celý seriál**, pevné startovní časy | (dle P1) | = umístění ČP 2025, 2. VT dle NKZ/oblastí/výjimek | S26 §1 › ČP, §2 |
| **ČP slalom – finále A** | prvních 10 z kvalifikace v **obráceném pořadí výsledků kvalifikace** (10. první, vítěz kvalifikace poslední) | — | stejné | S26 §1 › ČP |
| **ČP slalom – finále B** | 11. a další z kvalifikace, „podle startovních čísel od nejnižšího po nejvyšší“ | — | stejné | S26 §1 › ČP |
| **NKZ** | 1) MT a 1. VT; 2) ostatní VT dle průběžného pořadí NKZ (pro 1. a 2. NKZ dle loňského žebříčku; pro 3.+ dodá počtářka); 3) 2. VT dosud nezařazení | na konec (skupina 3) | dle P 2.18 | S26 §1 › NKZ |
| **ČPŽ slalom** | „dle obráceného průběžného absolutního žebříčku“ (dodá počtářka); 1. a 2. závod dle obráceného pořadí loňského ČPŽ | losují se podle VT **na začátek** („od nejlepší VT po nejhorší“) | dle P 2.18 | S26 §1 › ČPŽ |
| **ČPŽ sjezd** | „dle obráceného průběžného žebříčku této soutěže“ (dodá počtářka) | neuvedeno | dle ČPw? neuvedeno | S26 §1 › ČPŽ |
| **MČR dorostu slalom** (součást ČPJ) | obrácené pořadí průběžného žebříčku ČPJ slalom (dodá počtářka) | losem dle VT na začátek (od nejlepší VT po nejhorší) | dle P 2.18 | S26 §1 › MČR dorostu ve slalomu |
| **MČR žáků slalom** | (implicitně obrácený průběžný ČPŽ 2026) | losem dle VT na začátek (od nejlepší VT po nejhorší) | dle P 2.18 | S26 §1 › MČR žáků |
| **MČR dorostu klas. sjezd** | obrácené pořadí průběžného ČPJw (bez žáků); **kategorie žáků** v obráceném pořadí ČPžw **2025** | losem dle VT na začátek | ČPw styl? | S26 §1 › MČR dorostu ve sjezdu |
| **MČR žáků sprint** | obrácené pořadí průběžného žebříčku „ČPŽ pro rok 2026“ | losem dle VT na začátek | | S26 §1 › MČR žáků |
| **MČR žáků klas. sjezd** | obrácené pořadí ČPžw **2025**; „Po závodnících v kategorii žáků následují dorostenci.“ | losem dle VT na začátek | | S26 §1 › MČR žáků |
| **ČPw klasik i sprint** | „z průběžného pořadí od nejhorších k nejlepším a to pouze v klasických sjezdech“; 1. a 2. ČPw v obráceném pořadí loňského žebříčku; podklady dodá počtářka | neuvedeno | **od nejvyššího po nejnižší, poslední v kategorii = 1** | S26 §1 › ČPw |
| **ČPw sprint – finále B** | lodě 7.+ (K1M 9.+) z kvalifikace „dle startovních čísel (od nejnižšího po nejvyšší)“ | — | | S26 §1 › ČPw |
| **ČPw sprint – finále A** | nejprve postupující z FB v opačném pořadí, pak postupující z kvalifikace (také v opačném pořadí) | — | | S26 §1 › ČPw |
| **KC individuál (ČP)** | podle pořadí ČP 2025; startovka od nejvyššího čísla k nejnižšímu; pevné startovní časy | rozlosováni na začátek | z ČP 2025 | S26 §1 › ČP KAJAK KROS |
| **KC – vyřazovací část** | viz §14 | | | S26, KC24 |
| **VPZ / VPZw / ČPV** | Směrnice neupravují → základní způsob `P 2.17.01` (VT skupiny + los), rozpis | | P 2.18.03 | P 2.17, 2.18 |
| **Družstva MČR** (všechna uvedená) | „v obráceném pořadí loňských výsledků“ | — | P 2.18.03 (družstva) | S26 §1, viz §7 |

### 6.2 Důležité doslovné formulace
- ČP: „Startovní listina pro kvalifikace pro celý seriál ČP se sestavuje na základě žebříčků ČP 2025 a NKZ 2025 v pořadí od nejhorších k nejlepším… Do startovní listiny pořadatel uvádí pevné startovní časy.“ (`S26 §1 › ČP`)
- ČP: „Startovní pořadí ve finále A je obráceným pořadím výsledků kvalifikace, startovní pořadí ve finále B je podle startovních čísel od nejnižšího po nejvyšší.“ (`S26 §1 › ČP`)
- Nezařazení: „Závodníci v něm nezařazení budou losováni podle VT na začátek startovní listiny (od nejlepší VT po nejhorší).“ (`S26 §1 › MČR dorostu ve slalomu`, obdobně ČPŽ, MČR žáků, MČR dorostu sjezd)
- **ČP slalom – kdo startovku dělá:** předseda ZK pošle všem pořadatelům ČP a výpočetnímu středisku startovní listinu „platnou na základě přihlášek se všemi omluvami“ (`S26 §2 › Přihlášky na ČP`); pořadatel na základě odhlášek do pátku 18:00 upraví podklady a oficiální časoměřiči „vydají časově upravenou startovní listinu“ (`S26 §1 › ČP`). → U ČP pořadatel startovku **nesestavuje od nuly**.
- Podklady pro nasazení (průběžné žebříčky) dodává **počtářka žebříčku** – ČPJ, ČPŽ, ČPžw, NKZ od 3. závodu, ČPw.

### 6.3 Předjezdci / ukázková jízda (P 3.03, S26)
- Před první jízdou „ukázková jízda, a to na všech třech typech lodí (pokud možno na C1 levák a pravák). V každé kategorii mohou startovat nejvýše dvě lodě.“ (`P 3.03.01`). Na mistrovských závodech určí předjezdce Směrnice, jinde pořadatel se souhlasem VR, zveřejní nejpozději na poradě; nedostaví-li se, ukázková jízda odpadá.
- První start nejdříve 20 min po schválení trati (`P 3.03.02`).
- ČP: ukázkovou jízdu koordinuje pověřený člen ZK; ČP 1–4 mají navíc „Měřená předjízda“ v 9:20 (`S26 §1 › ČP`).
- NKZ: předjezdci losováni jen z ročníků 2007 a starších, jména zveřejnit nejpozději hodinu před poradou.
- MČR dorostu slalom: předjezdci z dospělých; MČR žáků slalom: z dospělých a dorostenců (zajistí pořadatel s VR).
- Ve výsledkové listině: začátek slalomového závodu = začátek ukázkové jízdy (`P 2.21.01`, T-5).

---

## 7. Závod družstev (hlídky)

| téma | pravidlo | citace |
|---|---|---|
| složení | družstvo = 3 lodě téže kategorie (3×K1, 3×C1, 3×C2) | P 1.05.02 |
| oddílová družstva | na mistrovských závodech jen oddílová; jen v C2 smí být jedna dvojice kombinovaná (se závodníkem jiného oddílu) | P 2.09.01 |
| právo startu | družstvo má právo startu v lodní kategorii, kde v individuálním závodě odstartoval **alespoň jeden** člen; lze doplnit až **dvěma loděmi bez práva startu**; na VPZ může sestavování určit rozpis | P 2.09.01 |
| jmenovité složení | rozpis stanoví, zda se sestava uvádí už v přihlášce, nebo se hlásí na místě dle pokynu VR | P 2.09.02 |
| ženy v mužských | 1–2 závodnice mohou jet v družstvu 3×K1M/3×C1M/3×C2M, pokud v tomtéž závodě nejedou v ženském družstvu téže kategorie; C2M i C2Ž mohou jet v 3×C2mix | P 2.09.02 |
| málo družstev | ženské kategorie s <3 přihlášenými družstvy lze klasifikovat v mužské; 3×C2mix s <3 v 3×C2M; mladší dorost/žactvo lze přiřadit ke staršímu | P 2.09.02, P 2.06.03 |
| počet jízd | „Závod družstev (ve slalomu i sprintu) se jede v jedné jízdě.“ | P 2.09.03, P 3.05, P 3.11.04 |
| nasazení MČR | „v obráceném pořadí loňských výsledků“ – MČR dospělých sjezd+sprint, MČR dorostu slalom i sjezd+sprint, MČR žáků slalom i sjezd+sprint | S26 §1 |
| interval MČR | **slalom 90 s** (dorost, žáci); **sjezd a sprint 60 s** (dospělí, dorost, žáci); minimum dle P: slalom 90 s, sjezd 60 s; mezi kategoriemi družstev ≥ 5 min | S26 §1, P 2.29.02 |
| MČR družstev dospělých slalom | pátek 21. 8. odpoledne; časový program i nasazení upřesní rozpis (S26 nasazení neuvádí) | S26 §1 › Pořad ČP 5, 6 |
| čísla | stejná různobarevná (1,1,1) nebo stejná poslední číslice (23, 33, 43) | P 2.18.03 |
| start slalom | 2. a 3. loď připraveny nad startem (pod ním při startu proti proudu), v klidu; na povel vyjíždí 1. loď, další dvě za ní dle pokynů startéra; pořadí lodí libovolné, smí si pomáhat | P 2.29.08 a |
| čas slalom | od startu 1. lodě do protnutí cíle tělem závodníka **třetí** lodě; v cíli se měří i čas první lodě | P 2.29.07, 2.29.08 a |
| 15 s pravidlo (slalom) | „Neprojede-li celé družstvo cílem v rozmezí 15 sekund, znamená to ve slalomu 50 trestných bodů.“ | P 2.29.08 a, 3.07.04 |
| penalizace slalom | průjezd branky se hodnotí u každé lodě zvlášť, trestné body se sčítají | P 3.07.08 |
| odvolání z trati | brankový rozhodčí musí odvolat družstvo, jehož člen zvrhl a opustil loď nebo použil cizí pomoc | P 2.27.07 |
| start/cíl sjezd a sprint | lodě v libovolném pořadí, startovní linii musí protnout do 10 s; „Neprojede-li celé družstvo startem, respektive cílem, v rozmezí 10 sekund, znamená to ve sjezdu i sprintu diskvalifikaci družstva.“ | P 2.29.08 b |
| pomoc | ve sjezdu si členové smí pomáhat, jízda na vlně/v srku povolena; tažná zařízení zakázána | P 3.13.02, 3.13.04 |
| víc družstev | max. 3 družstva na závodníka na MČR/ČP/NKZ; žákovské sjezdové soutěže max. 2 | P 2.39.03, S26 §1 |

Hlídky v Eskymu: sešit se vytváří s parametrem „hlídky = ano“; výsledková řádka obsahuje 3 RGC/jména/ročníky/VT. Rozlišení více družstev oddílu písmeny (A/B) Pravidla **neupravují**.

---

## 8. Časový pořad, intervaly, pořadí kategorií

### 8.1 Minimální intervaly (P 2.29.02)
Stanovuje je VR; na **MČR, MČRd, MČRž, ČP a NKZ**: slalom ≥ **40 s** (individuálně) / ≥ **90 s** (družstva); sjezd ≥ **30 s** / ≥ **60 s**; přestávka mezi lodními kategoriemi ≥ **3 min**, u družstev ≥ **5 min**.

### 8.2 Konkrétní pořady podle S26

| soutěž | pořadí kategorií / skupin | intervaly |
|---|---|---|
| ČP slalom 1–4 | kvalifikace i obě finále: **C1Ž, C1M, K1Ž, K1M** | kval. 60 s, FA 100 s, FB 60 s; mezi kategoriemi 3 intervaly. Den předem 17–18 tuning, 18:00 předjízda ve třetinách; 7:45 porada; 9:20 měřená předjízda; 9:30 kval.; 13:00 FA; 14:30 FB |
| ČP 5 (MČR dospělí) a 6 (MČR U23), 21.–23. 8. | totéž | pá 21. 8. odpoledne MČR družstev dospělých (program dle rozpisu); so 22. 8. program dle rozpisu (pravděpodobně TV); ne 23. 8.: 8:15 ukázková jízda, 9:15 kval. 60 s, 12:30 FA 120 s, 14:00 FB 50 s |
| NKZ | 1. skupina **K1M, C1Ž – obě jízdy**; 2. skupina **C1M, K1Ž** | 7:45 porada vedoucích, 8:00 rozhodčích, 8:30 ukázková jízda, 9:15 start; 4. NKZ (Veltrusy, ne) účastníci LODM mimo pořadí v samostatných skupinách |
| ČPŽ slalom | **K1M, C1Ž, předžáci K1 – obě jízdy**; **C1M, K1Ž, předžáci C1 – obě jízdy** | dle P 2.29.02 |
| VPZ slalom (doporučení) | **K1M, C1Ž, C2M, předžáci K1 – obě jízdy**; **C1M, K1Ž, C2MIX, předžáci C1 – obě jízdy** | dle VR |
| všechny sjezdové (ČPw, VPZw…) | **C1M, K1Ž, K1M, C1Ž, C2M** | ČPw: kval. sprintu 30 s, FB 30 s, FA 60 s; ČP Kamenice až 60 s |
| družstva MČR | dle rozpisu | slalom 90 s, sjezd/sprint 60 s |

### 8.3 Časový rozsah (P T-5, P 2.02.03)
Postupové závody 1. 3.–31. 10.

| | III | IV | V | VI | VII | VIII | IX | X |
|---|---|---|---|---|---|---|---|---|
| start první lodě – sjezd | 10:00 | 9:30 | 9:30 | 9:00 | 9:00 | 9:00 | 9:00 | 9:30 |
| start první lodě – slalom | – | 8:30 | 8:30 | 8:00 | 8:00 | 8:00 | 8:30 | 8:30 |
| dojezd poslední lodě | 17:00 | 18:00 | 19:00 | 19:00 | 19:00 | 19:00 | 18:00 | 17:30 |

Slalom: start = začátek ukázkové jízdy. Sjezd: dojezd = start poslední lodě + předpokládaný čas vítěze poslední kategorie + 50 %. Dva závody v jednom dni s přestávkou ≥ 1 h. Pořadatel musí rozsah dodržet (časová úprava, redukce kategorií) (`P 2.02.04`) a může omezit přihlášky (`S26 §1 › VPZ`).

### 8.4 Start (P 2.29)
- Jen pevný start, po proudu nebo proti proudu (`P 2.29.01`); signál odpočítává ≥ 5 s (`P 2.29.03`).
- Nepřipravený na start podle čísla: **slalom a sprint** – „diskvalifikován z jízdy bez dalšího upozornění“; **sjezd** – může odstartovat do startu poslední lodě své kategorie, čas se počítá od doby, kdy měl startovat (`P 2.29.04`).

---

## 9. Přihlášky, dohlášky, omluvy, pokuty, startovné

### 9.1 Omluvy a pokuta 500 Kč (S26 §1 – shodně v oddílech ČP slalom, ČP KC, ČPw)
Vedoucí oddílu nahlásí nestartující lodě e-mailem/telefonem/SMS nejpozději **v pátek do 18:00**; ředitel zajistí, aby řádně omluvené lodě nebyly ve startovce; časomíra vydá časově upravenou startovku. Závažné zdravotní/technické důvody se omlouvají do porady u VR. „Vrchní rozhodčí zajistí, aby všechny omluvy byly uvedeny ve výsledcích“:

| stav | ve startovce? | pokuta | návrh kódu v Eskymu (ověřit) |
|---|---|---|---|
| omluven do pátku 18:00 | ne | ne | DNS-A |
| omluven do porady (zdravotní/technické důvody) | ano | ne | DNS-B |
| neomluven – nestartoval | ano | **500 Kč** (odečteno oddílu z dotace ve prospěch pořadatele „na základě oficiálních výsledků“) | DNS |

Eskymo zná stavy DNS, DNS-A, DNS-B („byl omluven“), DNF, DSQ-R (z jízdy), DSQ-C (ze závodu). Přesné přiřazení A/B k lhůtám S26 neuvádí.

VPZ: „Závodníky, kteří neodstartovali ani do jedné jízdy, nemusí pořadatel veřejných závodů uvádět ve výsledcích závodu.“ (`S26 §6`)

### 9.2 Přihlášky a dohlášky
- ČP slalom: přihláška na celý seriál předsedovi ZK do **15. 3. 2026**, startovné (300 Kč/loď/závod) do 31. 3. 2026; dohláška na jednotlivý ČP nejpozději **5 dní** před závodem pořadateli (na místě max. 500 Kč/loď); písemná přihláška na standardním formuláři nejpozději před poradou za max. 500 Kč (`S26 §2`).
- ČP juniorů a seniorů ve slalomu, sjezdu a NKZ: dodatečná přihláška nejpozději před poradou za 500 Kč (`S26 §2`).
- VPZ: dohlášení na místě až za dvojnásobné startovné (`S26 §2`).
- Dodatečné přihlášky nesmí překročit povolený časový rozsah a musí být písemné (`P 2.15`).
- Vedoucí družstva potvrdí elektronickou přihlášku podpisem nejpozději do porady (`P 2.15.04`, `P 2.28.01`).
- Online přihlašování: bude možné nastavit max. počet lodí (`S26 §7`).

### 9.3 Startovné 2026 (S26 §2), loď i družstvo
ČP slalom vč. MČR 300 Kč; ČPw klasik vč. MČR 250 Kč; ČPw sprint vč. MČR 200 Kč; NKZ vč. MČR dorostu slalom 250 Kč; KC 200 Kč; MČR dorostu sjezd/sprint 150 Kč; MČR žáků slalom 200 Kč; MČR žáků sjezd/sprint 150 Kč. Maximum pro postupové závody: slalom dospělí 200, sjezd dospělí 160, mládež 100 Kč. Jen v Kč, pro obě oblasti stejné; doklad o zaplacení s IČ/DIČ (`S26 §7`). NKZ a ČP sjezd platí oddíly na účet ČSK DV do 7 dnů po závodě.

---

## 10. Průběh a výpočet výsledků

### 10.1 Měření času (P 2.29.06–07)
- „Časy se měří s přesností na jednu desetinu sekundy. Při elektronickém měření se zaznamenávají časy na setiny sekund.“ Na setiny se měří minimálně všechny ČP ve slalomu a ČP ve sprintu, pokud se start i cíl zaznamenávají automaticky.
- Vždy **dvěma nezávislými systémy** (`P 2.29.07`, `P 2.12.02`).
- Konec jízdy: protnutí cílové linie tělem (C2: tělo závodníka, který projel dříve; družstvo: tělo závodníka třetí lodě). „Zvrhnutá loď nebo loď v eskymáckém obratu na cílové linii znamená diskvalifikaci ze závodu.“ Návrat přes cílovou linii = diskvalifikace; protnutí cíle pádlem dříve než tělem = diskvalifikace (`P 2.29.05`, `2.29.07 b`).

### 10.2 Slalom – penalizace a výpočet (P 3.05–3.10)
- Trestné body: **0** správný průjezd bez dotyku; **2** dotyk (opakovaný dotyk jen jednou); **50** dotyk bez správného průjezdu, úmyslné odhození, zvrhnutí v brance, průjezd z nesprávné strany, vynechání branky, družstvo mimo 15 s. Max. 50 na brance; ve sporných případech ve prospěch závodníka (`P 3.07`).
- Výsledek jízdy = čas v sekundách + trestné body; příklad: 1'50"82 = 110,82 + (2+50+2) = **164,82** (`P 3.10.01`).
- „Závod ve slalomu se skládá ze dvou jízd, které je nutno jet v jednom dni. Konečné pořadí je dáno výsledkem lepší jízdy.“ (`P 3.05`) Výjimky: družstva (1 jízda), ČP (kvalifikace + finále).
- Shoda: rozhoduje „další lepší jízda“; je-li i ta shodná, stejné umístění (`P 3.10.02`). Shoda na postupovém místě → postupují všichni (`P 3.10.03`).
- Medaile při shodě: 2× zlato → bez stříbra; ≥3× zlato → bez stříbra i bronzu; ≥2× stříbro → bez bronzu; více bronzů → všichni bronz (`P 3.10.04`).
- Opuštění lodi → vyřazení z jízdy (`P 3.09.03`); pokračování v projíždění branek po vzdání/diskvalifikaci → diskvalifikace z celého závodu (`P 3.09.04`); selhání bezpečnostní výstroje → diskvalifikace z jízdy (`P 1.07.06`).
- Opravná jízda: jen při prokazatelném poškození jiným závodníkem a bez 50 do té doby; nutně při selhání časomíry, poškození trati (`P 3.09.02`).
- Průběžné výsledky slalomu se vyvěšují **úplné** (časy a trestné body obou jízd) (`P 2.30.04`).

### 10.3 ČP slalom – formát a konečné pořadí (S26 §1 › ČP)
- Kvalifikace 1 jízda → FA (10 nejlepších, obrácené pořadí) → FB (11.+, dle čísel vzestupně).
- Shoda na 10. místě kvalifikace → do FA postupují všichni shodní (`P 3.10.03`).
- „Konečné pořadí na 1. až 10. místě je určeno výsledkem finálové jízdy.“ Shoda → stejné místo a stejné body. Nenastoupí-li / nedokončí-li FA → hodnocen na **10. místě** s příslušnými body.
- 11. a další místa: „lepší z obou výsledků (kvalifikace a finále „B“), při shodě pak lepší výsledek horší jízdy.“
- Bodování T-4; konečné pořadí ČP bez nejhoršího výsledku; shoda bodů v žebříčku → lepší výsledek na MČR (`S26 §4`).

### 10.4 NKZ, VPZ – dvě jízdy (S26 §1)
- NKZ: „Závod sestává ze dvou jízd, o konečném pořadí rozhoduje lepší jízda, při shodném výsledku několika závodníků pak další jízda.“ Povinnost vyhlásit celkové pořadí a pořadí juniorů.
- VPZ slalom: dvě jízdy, lepší jízda, při rovnosti další jízda; BHZ 4–6 dle rozpisu.

### 10.5 Sjezd a sprint (P 3.11, S26 §1 › ČPw)
- Sprint: trať 200–600 m; **dvě jízdy, započítává se lepší**; kdo 1. jízdu nedokončil, může startovat ve 2.; družstva 1 jízda; ČP dle Směrnic (`P 3.11.03–04`).
- Klasický sjezd: 1 jízda, trať projetelná do 30 min; delší = maraton (nebodovaný, nepostupový) (`P 3.11.05`). Opustit loď a pokračovat bez cizí pomoci je dovoleno (`P 3.13.03`).
- Trať musí schválit porada vedoucích prostou většinou, jinak náhradní trať nebo zrušení postupovosti (`P 3.11.07`).
- **ČPw sprint:** kvalifikace 1 jízda (interval 30 s) → přímo do FA 8 lodí K1M, 6 lodí ostatních; FB (7.+ resp. K1M 9.+) dle čísel vzestupně, interval 30 s, z FB do FA další **2**; FA interval 60 s. Pořadí: nejprve výsledek FA; nenastoupil/nedokončil FA → poslední místo FA s body; shoda ve FA → shodné pořadí, body, medaile; další místa = lepší z kvalifikace a FB, při shodě lepší horší jízda; kdo nestartoval v kvalifikaci, nesmí do FB. Vyhlásit celkové pořadí a pořadí juniorů.
- Ve výsledcích: sjezd = výsledný čas + body; sprint = čas každé jízdy, celkový výsledek, body (`P 2.21.01`). Eskymo: sprint = lepší jízda; formát času MM:SS,DS.
- Vedoucí družstva hlásí VR co nejdříve závodníky, kteří sjezd nedokončili (`P 2.28.04`).

### 10.6 Stavy nestartoval / nedokončil / diskvalifikace
- Pravidla používají: DNF „Do Not Finish“, DQB „Diskvalifikace“, FLT „Fault“, RAL „Rank As Lowest“ (seznam zkratek P; FLT/RAL jen KC); DNS v KC24 4.14.
- Výsledky musí obsahovat jména klasifikovaných, diskvalifikovaných **s důvodem** a nedokončivších (`P 2.21.01`).
- KC: DNF a DNS na konci v abecedním pořadí (nejprve DNF, pak DNS); DQB za všemi v abecedním pořadí (`KC24 4.14.02`, `4.15.06`).
- Eskymo: zadání DNS/DNF/DSQ uloží do času zkratku a do výsledku 999 (seřadí se na konec).

---

## 11. Výsledková listina – povinné náležitosti, zveřejnění, odeslání

### 11.1 Záhlaví a obsah (P 2.21.01, P 1.04.01)
Záhlaví: **pořadatel** (oddíl/klub); **název a pořadové číslo závodu dle celostátního kalendáře** (+ zařazení podle obtížnosti – `P 1.04.01` to vyžaduje „v záhlaví všech tiskovin“); **datum**; **vrchní rozhodčí, ředitel závodu, stavitel trati**, případně zástupce svazu.
Pro každý samostatný závod (na novou stránku): datum a **čas začátku** (bez porad; sjezd první start, slalom ukázková jízda) a **čas ukončení** (dojezd posledního); název a charakter závodu, **přesné určení a délka trati**, u slalomu **počet branek**; **stav vody** (vodočet nebo m³/s); **BHZ**; nenadálé okolnosti (povodeň…).
Řádky: celkové pořadí + pořadí ve věkových skupinách (ds, dm, žs, žm, v); **RGC, příjmení, jméno, VT, rok narození, oddíl**; slalom: čas, trestné body a výsledek **každé jízdy**, celkový výsledek, body; sprint: čas každé jízdy, celkový výsledek, body; sjezd: čas, body. Jména DSQ (s důvodem) a DNF.
RGC se do výsledků uvádí povinně (`P P-6 1.05.02`).
Eskymo `param` pole, která to pokrývají: název, místo, pořadatel, ředitel, VR, datum, číslo závodu, BHZ, disciplína, počet branek, začátek/konec, průtok, místo vodočtu, teploty, „Výsledky zpracoval“ (stavitel trati v `param` vzorového sešitu **není** – ověřit).

### 11.2 Zveřejňování na místě, dotazy, námitky
- Při průběžném vyvěšování uvádět **čas zveřejnění** posledních výsledků kategorie a **čas konce lhůty pro námitky**, potvrzeno podpisem VR (`P 2.30.04`).
- Dotaz (jen slalom, rozhodnutí brankového rozhodčího): vedoucí písemně do **10 min** po zveřejnění neoficiálních výsledků kategorie; formulář = S26-P4 (`P 2.30.01`, S26-P4).
- Námitka: do **20 min** po zveřejnění podkladů; vklad ČP/MČR 250, NKZ 200, VPZ 100 Kč (`P 2.30.04`, P-1.02). Nevyřízená námitka → v kategorii nelze udělit tituly a ceny (`P 2.31.03`).
- Zjevná početní chyba: bez vkladu u ředitele/počtáře (`P 2.30.05`). Reklamace výsledků do **10 dnů** po obdržení konečných výsledků; pořadatel vydá opravené výsledky kategorie a opravený výpočet bodů (`P 2.30.08`).

### 11.3 Odeslání a oficiální zveřejnění
- `S26 §6`: „Výsledky musí být v Eskymu, nebo ve formátu XML, pořadatel je vloží se na adresu http://csk.kanoe.cz do **24 hodin** po skončení závodu (veřejné postupové závody)“; po odsouhlasení předsedkyní ZK jsou oficiální na www.kanoe.cz/zavody/slalom-sjezd. Závody v péči ČSK DV: **do pondělí 8:00**. Závody zpracovávané firmou Results s.r.o.: věcnou i formální správnost garantuje VR, po kontrole počtářkou zveřejněno do **8:00 následujícího dne**.
- „Podmínkou jsou výsledky zpracované v programu Eskymo, který je ke stažení na eskymo.results.cz.“ (`S26 §6`)
- Pravidla obecně: „ve formátu požadovaném ČSK DV… nejdéle do tří dnů počtáři“, pokuta za zmeškání (`P 2.21.04–05`) → **Směrnice 2026 (24 h) jsou přísnější a platí.**
- Ředitel závodu odpovídá za správnost výsledků včetně žebříčkových bodů a jejich rozeslání (`P 2.24.01`).
- Mimořádné události / námitky → zpráva VV; ovlivní-li námitka výsledek, informovat počtáře (`P 2.21.06`).
- Uschovat přihlášky, startovku, startovní a cílový protokol, brankové záznamy, hlášení změn… nejméně **4 měsíce** (`P 2.21.07`).
- VR posílá „Zprávu vrchního rozhodčího“ do 10 dnů předsedovi komise rozhodčích (`SČR22 6.2.2`, `7.3`).
- Souhrnné pořadí více závodů pod společným názvem: prostý součet umístění, jen účastníci všech závodů; shoda → součet sekund nebo bodů (`P 2.21.03`).

---

## 12. Bodování

### 12.1 Tabulka T-4 (P T-4) – ČP, NKZ, ČPJ, ČPŽ, ČPw, kombinace

| místo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| body | 75 | 68 | 62 | 57 | 53 | 49 | 46 | 43 | 40 | 37 | 35 | 33 | 31 | 29 | 27 | 25 | 23 | 21 |

| místo | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| body | 19 | 17 | 15 | 14 | 13 | 12 | 11 | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |

(Eskymo 1.6.5: „bodování dle tabulky T4 se používá pouze stupnice začínající body 75“.)

### 12.2 Tabulka pro Kayak cross (S26 §1 › ČP KAJAK KROS)

| místo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| body | 32 | 30 | 28 | 26 | 24 | 22 | 20 | 18 | 16 | 14 | 12 | 10 | 8 | 6 | 4 | 2 |

### 12.3 Započítávání do seriálů (S26 §1, §4)

| seriál | body | započítává se | shoda bodů |
|---|---|---|---|
| ČP slalom | T-4 | všechny kromě nejhoršího z uskutečněných | lepší výsledek na MČR |
| NKZ | T-4 jen v rámci pořadí 2. VT; MT a 1. VT dostanou body jako bodovaná loď 2. VT za nimi | 4 nejlepší z 6 (neuskuteční-li se ≥2, škrtá se 1 nejhorší) | — |
| ČPJ slalom | T-4 jen mládež (MČR dorostu + 6 NKZ) | 5 nejlepších ze 7 (≥2 neuskutečněné → škrt 1) | lepší výsledek na MČR dorostu |
| ČPJw | T-4 | 6 nejlepších z 8; při neuskutečnění škrt 2 nejhorších | (MČR, §4) |
| ČPŽ slalom | T-4, žáci roč. 2012–2015, absolutní + žebříčky ŽM | 5 nejlepších | MČR žáků |
| ČPŽw | T-4 | škrtá se 1 nejhorší z 5 | MČR žáků ve sprintu |
| ČPw | T-4 (+ oblastní BHZ 6) | 4 nejlepší klasiky + 4 nejlepší sprinty | lepší výsledek na MČR |
| ČP / ČPJ KC | tabulka 32…2 | 5 ze 7 (ČPJ 6 z 8); ≥2 neuskutečněné → škrt 1 nejhorší | — |
| ČPV | — | 4 nejlepší ze 6; do žebříčku jen s ≥2 starty v lodní kategorii | — |
| VPZ / VPZw | oblastní BHZ 4–6 | max. 5 nejlepších do oblastního žebříčku | — |

Další: ČPŽ slalom i sjezd se boduje i do oblastních žebříčků dle oblastní příslušnosti; ČPw do oblastních sjezdových žebříčků dle BHZ 6, zvlášť Čechy a Morava (`S26 §1 › ČPw, VPZw`).

### 12.4 Volba bodování v Eskymu (inference – ověřit)
Eskymo nabízí `nic`, `čp` (T-4 slalom i sjezd), `čpž`, `nkz`, `bhz-č`, `bhz-m` (BHZ, body všichni), `oč`, `om` (BHZ, body jen závodníci dané oblasti); tři sloupce Body1–3.

| závod | doporučené Body1 / Body2 / Body3 | opora |
|---|---|---|
| ČP slalom, MČR dospělí/U23 slalom | čp | S26 §1 › ČP |
| NKZ, MČR dorostu slalom | nkz (a pro ČPJ body počítá počtářka) | S26 §1 › NKZ, ČPJ |
| ČPŽ slalom, MČR žáků | čpž / oč / om | S26 §1 › ČPŽ |
| ČPw (klasik i sprint) | čp / oč / om | „Závodníci české a moravské oblasti jsou v závodech ČPw bodováni odděleně“ (`S26 §1 › VPZw`) |
| VPZ v Čechách / na Moravě | bhz-č resp. bhz-m (BHZ z rozpisu) | P 2.42.04 b (bodují i závodníci druhé oblasti) |
| MČR družstev, předžáci, maraton | nic | P 2.42.05; S26 §1 |

---

## 13. Kombinace (S26 §1 › KOMBINACE, P 2.06.04)
- **MČRkž (žactvo):** součet výsledků MČR ve slalomu, ve sprintu a (kajakáři) v KC; kanoisté slalom + sprint; ročníky 2012–2015 dohromady; zahrnují se jen závodníci s umístěním ve všech 3 (resp. 2) disciplínách. Pořadatel odpovídá za vydání kompletních výsledků kombinace.
- Metoda (`P 2.06.04`): prvních **25 míst** v každé disciplíně dostane body jako v ČP (T-4), pořadí dle součtu; při rovnosti rozhoduje „prostý součet výsledků“; výsledky kombinace počítá VR s delegátem při druhém ze závodů.
- **MČRkd (dorost):** součet MČR slalom + KC; „K1 slalom + kajak kros (kajakářská kombinace) a C1 slalom + kajak kros (kanoistická kombinace)“.

---

## 14. Kayak cross (S26 §1, KC24)
- Kategorie jen **K1 ženy, K1 muži**; lodě ze seznamu ICF (KC Boat Index), max. délka 2,75 m, min. 18 kg (`KC24 4.03–4.04`).
- **Time trial** (kvalifikace) určuje nasazení do rozjížděk (`KC24 4.05`). Počet postupujících z TT a pavouk:

| dokončilo TT | postupuje | první fáze | lodí v rozjížďce | pavouk |
|---|---|---|---|---|
| 32+ | 32 | rozjížďky | 4 | A |
| 24–31 | 24 | rozjížďky | 3 | B |
| 16–23 | 16 | čtvrtfinále | 4 | C |
| 12–15 | 12 | čtvrtfinále | 3 | D |
| 8–11 | 8 | semifinále | 4 | E |
| 6–7 | 6 | semifinále | 3 | F |
| 4–5 | 4 | finále | 4 | G |
| 3 | 3 | finále | 3 | H |
| <3 | závod se nekoná | | | |

- Pavouk A (T-6): rozjížďka 1 = TT 1, 16, 17, 32; R2 = 8, 9, 24, 25; R3 = 5, 12, 21, 28; R4 = 4, 13, 20, 29; R5 = 3, 14, 19, 30; R6 = 6, 11, 22, 27; R7 = 7, 10, 23, 26; R8 = 2, 15, 18, 31. Z každé jízdy postupují první 2: QF1 = R1+R2, QF2 = R3+R4, QF3 = R5+R6, QF4 = R7+R8; SF1 = QF1+QF2, SF2 = QF3+QF4; finále = 1.–2. z SF1 a SF2.
- **ČP 2026 (S26) mění formát:** „Do vyřazovacího závodu bude postupovat vždy 8 nejlepších závodníků.“ Semifinále 1: **1., 4., 5., 8.**; semifinále 2: **2., 3., 6., 7.** loď z „Kajak krosu individuál“; první dvě z každého SF → **finále A (1.–4.)**, ostatní → **finále B (5.–8.)**; 9.+ podle vyřazovací části o 9.–16. místo (pokud se jede), dále podle pořadí v individuálním závodě. ČP 4 (MČR): pořadí/nasazení podle ICF canoe slalom world ranking (Praha).
- Start: všichni současně (rampa); předčasný start = FLT (`KC24 4.10`).
- Hodnocení: FLT (špatný start, neprojetí/špatný směr brány, eskymák mimo zónu či ne 360°), RAL (porušení bezpečnosti), DNF (zvrhnutí, cíl hlavou dolů); dotyk brány se netrestá (`KC24 4.12`). Dotazy v KC nelze podávat (`KC24 4.15.07`).
- Výsledky TT: bez penalizace podle času před FLT; FLT řazeni podle místa penalizace (kdo dojel bez penalizace dál, je výš); DNF, DNS na konec abecedně; shoda → aktuální žebříček KC, pak los; bez KC žebříčku → pozice v ČP (NKZ) slalom K1M/K1Ž (`KC24 4.14`).
- Vyřazení v kterékoli fázi: pořadí podle TT, ale všichni třetí před čtvrtými; v jízdách pořadí podle pozice v cíli; čistí před FLT, RAL, DNF, DNS (v tomto pořadí); DQB mimo pořadí na konci abecedně (`KC24 4.15`).
- Startovní čísla: `KC24 4.13` = pořadí v TT (nejrychlejší 1) × S26 = čísla z ČP 2025, startovka KC individuál od nejvyššího čísla (viz Nejasnosti).
- Eskymo KC nepodporuje (disciplíny slalom/sjezd/sprint); TT lze případně zpracovat jako sprint/sjezd s 1 jízdou (inference).

---

## 15. Přílohy Směrnic 2026

| příloha | soubor | obsah | význam pro startovky/výsledky |
|---|---|---|---|
| **č. 1** | `Priloha_c_1_Smernic_2026_-_postup_cp_slalom-oprava.xls` (listy „Postup ČP K1m,K1ž“, „Postup ČP C1m,C1ž“) | „Závodníci s právem startu na ČP ve slalomu v roce 2026“ nad rámec MT/1. VT. Sekce: *z oblasti Čechy / Morava* (vítěz oblastního žebříčku), *z NKZ*, *Vítěz ČPŽ*, *Výjimky*. Sloupce: RGC, PŘÍJMENÍ Jméno, ročník (2 číslice), zkratka oddílu. Počty: K1M 2+18+1+12, K1Ž 2+18+1+3, C1M 2+19+0+2, C1Ž 2+11+0+3. | vstup pro kontrolu práva startu a nasazení ČP; data jsou nečistá (RGC a ročníky jako float „10.0“, nejednotné zkratky „KKBrand“, „KK Brand.“, „Horš..Týn“, „TJ Dukla“). Oprava z 28. 1. 2026 přidala jednu výjimku v K1M; původní soubor (bez „-oprava“) je stále online. |
| **č. 2** | `Priloha_c.2_Smernic_2026.docx` | Klíč na rozdělování dotací (dotace za pořádání VPZ: slalom 4 000 Kč/den, sjezd 2 000, oba 5 000; všední den 600/300/1 000; body za rozhodčí, trenéry, VT mládeže ŽM–ŽS a DM–U23; předžáci s 2 závodními dny 4 body) | nepřímý (motivace kompletních výsledků, VT) |
| **č. 3** | `Priloha_c._3_Smernic_2026.xls` (list mylně „Příloha 4“) | „jediné platné zkratky všech oddílů… maximálně osmiznakové“ – číslo oddílu, název, 3znakový kód, 8znaková zkratka | **sloupec „oddíl“ v Eskymu** (např. „Pardub.“, „Č.Kruml.“, „Boh.Pha“); tabulka níže |
| **č. 4** | `Priloha_c_4_Smernic_2026.docx` | Podávání dotazu (text shodný s P 2.30.01) + formulář „Dotaz Český pohár 2026“ (číslo a místo, kategorie C1M/C1Ž/K1M/K1Ž, jízda Kvalifikace/Finále A/B, branka, penalizace 0/2/50, st. č., důvod, přezkoumání video/formuláře, výsledek) | lhůta 10 min po neoficiálních výsledcích |
| **č. 5** | `Priloha_c.5_Smernic_2026.docx` | Doplněk registračního řádu: registrační poplatek 200 Kč/člen k 31. 3. (noví členové do 30. 11.); nezaplacení → nelze startovat na závodech v péči ČSK DV, blokace přihlašovacího portálu | kontrola práva startu |
| (č. 6) | není přiložena | S26 §7 odkazuje na „přílohu č. 6“ (Registrační řád), ta ve 2026 nezveřejněna | — |

Pozn.: RGC dle `P P-6 1.05.02` „šestimístné, první číslice vyjadřuje příslušnost k oblasti“ – v praxi (Příloha 1 a 3) je prefix RGC **číslo oddílu** (např. 119xxx = UP Olomouc č. 119, 9xxx = USK Praha č. 9) a udává oddíl původní registrace, ne aktuální.

### 15.1 Příloha č. 3 – oficiální zkratky oddílů

| č. oddílu | název oddílu | kód (3 zn.) | zkratka (max 8 zn.) |
|---:|---|---|---|
| 1 | Bohemians Praha | BOH | Boh.Pha |
| 4 | Extreme kayak club | — | Ex.kayak |
| 7 | Technika Praha | TEP | Tech.Pha |
| 8 | Sokol Žižkov | SOZ | S.Žižkov |
| 9 | USK Praha | USK | USK Pha |
| 10 | SK VS Karbo Benátky | KAB | Benátky |
| 11 | KK Brandýs nad Labem | KKB | KK Brand |
| 12 | Dukla Brandýs | DUB | Dukla B. |
| 14 | TJ Kralupy z.s. | KKV | Kralupy |
| 17 | KK Rakovník | KKR | Rakovník |
| 19 | BS Vlašim | VLA | Vlašim |
| 20 | TJ VS Chomutov | CHO | Chomutov |
| 23 | SK Vodní slalom České Budějovice | VSB | SKVS ČB |
| 24 | SK Vltava Č.Krumlov | VCK | Č.Kruml. |
| 25 | TJ Kaplice | KAP | Kaplice |
| 26 | SK Domeček Soběslav | SOB | Soběslav |
| 27 | Otava Strakonice | OTS | Ot.Strak |
| 30 | VS Tábor | VST | VS Tábor |
| 33 | VS Blovice | BLO | Blovice |
| 34 | TJ SK Hubertus KV | HUB | Hubertus |
| 35 | SK Slavie K.Vary | SKV | Sláv.KV |
| 36 | TJ Klatovy | KLA | Klatovy |
| 38 | TJ ČSAD Plzeň | CPL | ČSAD Plz |
| 39 | TJ Loko Plzeň | LOP | Loko Plz |
| 42 | TJ KVS Sušice | SUS | Sušice |
| 43 | TJ Česká Lípa | CLI | Č.Lípa |
| 45 | KVS Hradec Králové | KHK | KVS HK |
| 46 | Delfín Jablonec | JAB | Jablonec |
| 47 | TJ DNT VS Kadaň | DNT | Kadaň |
| 48 | TJ Ohře Klášterec | KLO | Klášter. |
| 49 | KK Roudnice | RNL | Roudnice |
| 50 | SK Mondi Pack.Štětí | STE | Štětí |
| 52 | TJ Loko Žatec | ZAT | L.Žatec |
| 53 | TJ Dvůr Králové | DKL | Dv.Král. |
| 55 | SK VS Slávia Hradec Kr. | SHK | Sláv.HK |
| 57 | TJ Syntézia Pardub. | PAR | Pardub. |
| 59 | TJ Semily | SEM | Semily |
| 60 | Loko Trutnov | TRU | Trutnov |
| 61 | TJ Třebechovice | TRE | Třebech. |
| 62 | TJ Turnov | TUR | Turnov |
| 63 | SK Týniště nad Orlicí | TNO | Týniště |
| 64 | SKK Vysoké Mýto | SKK | Vys.Mýto |
| 65 | TJ Roztoky | PER | Roztoky |
| 66 | Vod.odd."7" Horš.Týn | VHT | Horš.Týn |
| 70 | KK Železný Brod | ZBR | Žel.Brod |
| 76 | TJ Jiskra Bechyně | BCH | Bechyně |
| 77 | Kotva Bráník | KOB | Kotva B. |
| 78 | Lužnice Tábor | LTA | L.Tábor |
| 80 | TJ Sokol Písek | SOP | So Písek |
| 81 | SK Jihlava | JIH | Jihlava |
| 86 | Sokol Trója | — | SoTrója |
| 88 | C.K. Rožátov | CKR | Rožátov |
| 89 | KV Viking Ml.Boleslav | — | VikingMB |
| 90 | WWCC FROL | — | Frol |
| 91 | Klub Larse Heletága | — | Heletag |
| 95 | Sport Zbraslav | ZBV | Zbraslav |
| 97 | Raft klub Troja | RKT | RK Troja |
| 103 | KK Spoj Brno | KSB | KK Brno |
| 105 | Tesla Brno | TES | Tesla Bo |
| 106 | VS Litovel | LIT | Litovel |
| 108 | VS Dolní Kounice | DOK | VSDK |
| 112 | VK Kroměříž | VKK | Kroměříž |
| 118 | Tzunami Ostrava | — | Ostrava |
| 119 | UP Olomouc | UPO | Olomouc |
| 120 | VS Ostrava | — | VS Ostr. |
| 121 | KK Opava | KKO | KK Opava |
| 123 | OP Prostějov | OPP | Prostěj. |
| 125 | VSK Rájec-Jestřebí | RAJ | VSKRájec |
| 128 | VS Desná | SUM | Desná |
| 129 | TJ Šumperk | — | Šumperk |
| 132 | TJ Valašské Meziříčí | VAM | Val.Mez. |
| 133 | SK Veselí nad Mor. | VNM | SKVeselí |
| 135 | TJ Zábřeh | ZAB | Zábřeh |
| 184 | Regent Team | — | Regent |
| 185 | KK Postřelmov | — | Postřelm |
| 188 | Raft team H2O Jeseník | — | Jeseník |

_76 oddílů._

---

## 16. Co z toho plyne pro tvorbu startovky / výsledků v Eskymu (checklist)

**A. Před startovkou – zjistit typ závodu a zdroj pravidel**
1. Urči soutěž (ČP / NKZ / ČPJ / ČPŽ / ČPw / ČPJw / ČPŽw / MČR* / VPZ / VPZw / ČPV / KC) a disciplínu (slalom / sjezd / sprint / KC); načti **rozpis závodu** (BHZ, vypsané kategorie a VT, pořadí kategorií/skupin, počet jízd, datum sestavení startovky, omezení počtu startů, pravidla pro družstva).
2. Ověř, že platí Směrnice **aktuálního roku** (manifest, detekce nové sezóny); pro 2026 = S26 + přílohy (P1 v opravené verzi).
3. U ČP slalom: startovku posílá předseda ZK → jen odstranit omluvené do pátku 18:00, převzít pevné časy; čísla jsou dána (ČP 2025).

**B. Oprávněnost a kategorie**
4. Kategorie mapuj K1W→K1Ž (k1z), C1W→C1Ž (c1z), C2X/C2MIX. Ve slalomu ČP/ČPJ/ČPŽ/MČR jen C1Ž, C1M, K1Ž, K1M.
5. Věkové kategorie dle ročníku (tabulka §2.2); veteráni VM/V/VS/SV – ověř, že Eskymo zná **SV**.
6. Právo startu dle §4.2 (VT ve správné disciplíně S/W a lodi K/C1/C2; C1↔C2M nepřenosné; C2 = vyšší VT); max. 3 + 3 starty (MČR/ČP/NKZ), žákovský sjezd 2 + 2; jeden C2 partner.
7. Předžáci (2016–2020) jen BHZ 4 slalom, samostatně, bez bodů; ženy v mužských jen když se ženská kategorie nekoná.
8. Zapni v Eskymu příznak „#“ pro chybějící prohlídku (S26 §7 b) a zkontroluj registrační poplatek oddílu (S26-P5).

**C. Nasazení a čísla**
9. Najdi pravidlo nasazení v tabulce §6.1; chybí-li (VPZ), použij `P 2.17.01`: skupiny MT+1 / 2+ / 2 / 3+ / 3 / bez VT, uvnitř skupin **los**; směr (nejlepší první vs. obrácené) je volba pořadatele → zeptat se.
10. „Obrácené pořadí žebříčku / loňských výsledků“ = vítěz startuje poslední. Podklady žebříčků dodává počtářka – vyžádat, nevymýšlet.
11. Nezařazení v žebříčku: dle S26 „losováni podle VT na začátek startovní listiny (od nejlepší VT po nejhorší)“ – Eskymo losuje opačně (0 → MT) → přeřadit ručně a nechat potvrdit.
12. Čísla: default `P 2.18.03` (vzestupně, každá kategorie od čísla končícího 1, např. 1, 21, 41…); ČPw a KC individuál **sestupně, poslední v kategorii = 1**; ČP slalom = umístění ČP 2025. Družstva: 1,1,1 barevně nebo 23/33/43. Rezervy na dohlášky a chybějící dresy jsou věc pořadatele.
13. Kontroly: unikátnost čísel, monotónnost ve zvoleném směru, pořadí kategorií dle rozpisu/§8.2, žádný závodník v kategorii dvakrát, C2 bez duplicitního partnera.

**D. Časy a intervaly**
14. Intervaly ≥ minima `P 2.29.02` (slalom 40/90 s, sjezd 30/60 s, mezery 3/5 min) a konkrétní S26 (ČP 60/100/60 s; MČR 60/120/50 s; ČPw sprint 30/30/60 s; družstva slalom 90 s, sjezd/sprint 60 s).
15. Pevné startovní časy do startovky u ČP slalom a KC individuál; celkový rozsah dle T-5.

**E. Výsledky**
16. Slalom: výsledek jízdy = čas (s, setiny při elektronice) + trestné body (0/2/50); konečný = lepší jízda; shoda → druhá jízda → stejné místo. ČP: FA určuje 1.–10., DNS/DNF ve FA = 10.; 11.+ lepší z kval./FB, shoda → lepší horší jízda.
17. Sprint: lepší ze 2 jízd; ČPw formát kval/FB/FA; klasik: 1 jízda; družstva 1 jízda.
18. Družstva: slalom 50 tr. b. za >15 s mezi 1. a 3. lodí v cíli, penalizace všech lodí sečíst; sjezd/sprint >10 s na startu nebo v cíli = DSQ.
19. Stavy: DNS / DNS-A / DNS-B (omluvy), DNF, DSQ-R (jízda), DSQ-C (závod); DSQ vždy s důvodem. U ČP/ČPw/KC uvést všechny omluvy; na VPZ lze nestartující vynechat.
20. Kategorie s < 3 odstartovanými loděmi nehodnotit/nevyhlašovat samostatně → sloučit dle příkladů A/B/C; C2MIX < 3 → C2M.
21. Body: nastav volbu bodování (§12.4) a BHZ z rozpisu (VR ji může změnit); body jen registrovaným (ne cizinci A-kód, ne předžáci); do banky se počítají i DNF/DSQ.
22. Záhlaví výsledků: pořadatel, název + číslo závodu z kalendáře, datum, VR, ředitel, **stavitel trati**, začátek/konec, trať a délka, počet branek, stav vody, BHZ, mimořádnosti; ve výsledcích RGC, jméno, VT, ročník, oddíl (zkratka dle Přílohy 3), pořadí ve VK, časy/tr. body po jízdách, body.
23. Při vyvěšování výsledků uvést čas zveřejnění a konec lhůty námitek (20 min; dotaz 10 min).
24. Odeslat Eskymo/XML na csk.kanoe.cz do **24 h** (VPZ); závody ČSK DV do pondělí 8:00; archivovat podklady 4 měsíce.

---

## 17. Nejasnosti / co je věcí pořadatele (rozpis závodu)

**Věcí pořadatele / rozpisu (musí se zeptat, nehádat):**
- Nasazení na VPZ/VPZw/ČPV (Směrnice mlčí) – jen rámec `P 2.17.01`; směr (nejlepší první/poslední) a zda losovat.
- Směr a rozsah startovních čísel, rezervy mezi kategoriemi, chybějící čísla, barevná čísla u družstev.
- Pořadí kategorií a skupin (S26 u VPZ jen „doporučuje“), počet jízd, časový program, startovní intervaly nad minimum.
- Složení družstev na VPZ, termín a forma hlášení sestav (`P 2.09.01–02`), písmena A/B pro víc družstev oddílu (Pravidla neřeší).
- MČR družstev dospělých ve slalomu – nasazení S26 neuvádí (u dorostu/žáků je „obrácené pořadí loňských výsledků“).
- Pořadí ve druhé jízdě (Pravidla neřeší; obvykle stejné jako v první).
- BHZ (4–6), omezení počtu startujících, dohlášky na místě (až 2× startovné), start předžáků.
- Předjezdci na nemistrovských závodech.

**Nejasnosti v textech:**
1. **Nezařazení „na začátek… od nejlepší VT po nejhorší“** – doslovně první startuje nejlepší VT z nezařazených; působí to opačně než logika obráceného žebříčku a než losování Eskyma. Potvrdit s pořadatelem/počtářkou.
2. **ČPw:** „z průběžného pořadí od nejhorších k nejlepším a to pouze v klasických sjezdech“ – buď se pro klasik i sprint nasazuje podle průběžného pořadí jen z klasiků, nebo pravidlo platí jen pro klasiky. Nasazení kvalifikace sprintu jinak neuvedeno.
3. **MČR žáků sprint** podle „průběžného žebříčku ČPŽ pro rok 2026“ (slalomového? sjezdového ČPŽw?) a **klasik podle ČPžw 2025** (loňský); obdobně MČR dorostu sjezd – kategorie žáků podle ČPžw 2025.
4. **Minimum 3 lodě:** S26 „odstartovat“ × `P 2.42.05 a` „klasifikovány“ (pro oblastní žebříček).
5. **§3 Limity 2. VT** nadepsány „pro rok 2025“; sloupce sjezdu (K1Ž 50 vs C1M 270 v Čechách) vypadají prohozeně – ověřit u ZK.
6. **ČP: více lodí DNS/DNF ve finále A** – všechny „na 10. místě“? Text řeší jen jednoho.
7. **Kayak cross:** S26 zavádí „Kajak kros individuál“ (časovka) a vyřazovací část jen pro 8 nejlepších, zatímco KC24 popisuje time trial s až 32 postupujícími a čísla podle pořadí v TT; formát „individuál“ není v pravidlech popsán (vychází z ICF).
8. **Věková kategorie posádky C2 a družstva** – Pravidla neurčují; Eskymo počítá sám (v datech dle nejstaršího člena). Pro vyhlášení U23 platí „11–23 let“ (i mládež).
9. **Omluvy DNS-A/DNS-B** – S26 rozlišuje „do pátku 18:00“ a „do porady“, Eskymo má DNS-A/DNS-B; přiřazení není nikde definováno.
10. **Rozdělení bodů BHZ mezi umístěné** – Pravidla 2022 uvádějí jen velikost „banky“ (`P 2.42.07`), algoritmus je v Eskymu.
11. **ČPV „pouze s licencí“** – co je licence, S26 nedefinuje.
12. **Odkazy s chybou:** `P 3.05` odkazuje na neexistující 2.09.04 (správně 2.09.03); S26 u MČRkž odkazuje na „Pravidla článek 2.21.04“ (správně 2.06.04); Příloha 3 má list pojmenovaný „Příloha 4“; S26 §7 zmiňuje přílohu č. 6, která není zveřejněna.
13. **Zvrhnutí na cílové linii** = „diskvalifikace ze závodu“ (`P 2.29.07 b`) – přísnější než běžná praxe „z jízdy“; u dvoujízdových závodů ověřit s VR.
14. **Směrnice vs. Pravidla u lhůty výsledků** – 24 h (S26) vs. 3 dny (P 2.21.05); platí přísnější S26.
15. **„Po závodnících v kategorii žáků následují dorostenci“** (MČR žáků sjezd) – naznačuje společný závod žáků a dorostu; pořadí kategorií potvrdit rozpisem.
16. **Stavitel trati** je povinný údaj záhlaví výsledků, ale v `param` vzorového Eskyma chybí – doplnit ručně (ověřit).

---

## 18. Detekce nové sezóny (podrobně v manifestu)
- Seznam: `https://www.kanoe.cz/cskdv/rozhodci/pravidla` (nejnovější článek nahoře), zrcadla `https://www.kanoe.cz/slalom/smernice-pro-zavodeni` a `https://www.kanoe.cz/sjezd/smernice-pro-zavodeni` (vždy aktuální rok).
- Článek: `/cskdv/rozhodci/pravidla/smernice-pro-zavodeni-csk-dv-{YYYY}` (historicky i s příponou `-konecna-verze`; `…-navrh` = návrh, ignorovat).
- Soubory: `/img/CSKDV/{YYYY}/Smernice{YYYY}/Smernice_pro_zavodeni_pro_rok_{YYYY}.docx`, přílohy `Priloha_c*{n}*Smernic_{YYYY}*.(docx|xls)` – názvy jsou nekonzistentní (`c_1`, `c.2`, `c._3`), opravy mají příponu `-oprava`.
- Neexistující slug vrací **HTTP 200** s textem „Chyba 404 Stránka nenalezena“ (redirect na `index.php?option=com_content&view=article&id=8334`) → testovat obsah, ne status.
- Tiché opravy příloh: hlídat Last-Modified / Content-Length / sha256 a slova „aktualizovan“, „oprava“ v titulku článku.
- Pravidla: `/cskdv/rozhodci/pravidla/pravidla-sekce-csk-dv`, soubory `/img/CSKDV/{YYYY}/Pravidla_{YYYY}_CSK_DV.(docx|pdf)`; nové vydání typicky po změně pravidel ICF (cca 4leté období, `P 1.01.01`).
