# -*- coding: utf-8 -*-
"""
Testy skillu csk-eskymo nad anonymními fixtures (tests/fixtures, vyrábí tools/make_fixtures.py).

    python tests/run_tests.py            # vše, co jde spustit (bez sítě)
    python tests/run_tests.py -k cisla   # jen testy, jejichž jméno obsahuje „cisla“
    python tests/run_tests.py --online   # i kontrola pravidel proti kanoe.cz

Testy s přepočtem potřebují LibreOffice (soffice v PATH nebo ESKYMO_SOFFICE); bez něj se přeskočí.
Převod Canoe123 potřebuje odfpy.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, 'skills', 'csk-eskymo', 'scripts')
FIX = os.path.join(ROOT, 'tests', 'fixtures')
sys.path.insert(0, SCRIPTS)

import cisla  # noqa: E402
import domena  # noqa: E402
from eskymo_ods import Workbook, norm_rgc, rgc_cell_value  # noqa: E402

TMP = tempfile.mkdtemp(prefix='eskymo-tests-')
TESTS = []


def test(fn):
    TESTS.append(fn)
    return fn


def run(script, *args, ok=(0,)):
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *map(str, args)],
                       capture_output=True, text=True, encoding='utf-8', env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    if r.returncode not in ok:
        raise AssertionError(f'{script} {args} → rc {r.returncode}\n{r.stdout}\n{r.stderr}')
    return r.stdout


def t(name):
    return os.path.join(TMP, name)


def have_lo():
    from recalc import find_soffice
    return find_soffice() is not None


class Skip(Exception):
    pass


# ---------- jednotky ----------
@test
def test_domena_kategorie():
    assert domena.kategorie_eskymo('K1W') == 'k1z'
    assert domena.kategorie_eskymo('K1Z') == 'k1z'
    assert domena.kategorie_eskymo('C1Ž') == 'c1z'
    assert domena.kategorie_eskymo('C2miX') == 'c2x'
    assert domena.kategorie_eskymo('XYZ') is None
    assert domena.lod('pzc') == 'C1' and domena.lod('c2x') == 'C2' and domena.lod('k1z') == 'K1'


@test
def test_domena_vk_vt():
    assert domena.vk_pro_rocnik(2014, 2026) == 'ZM'
    assert domena.vk_pro_rocnik(2016, 2026) == 'PZ'
    assert domena.vk_pro_rocnik(2003, 2026) == 'U23'
    assert domena.vk_pro_rocnik(1961, 2026) == 'SV'
    assert domena.vk_pro_rocnik(2015, 2027) == 'ZM'
    assert domena.lepsi_vt('3', ' MT') == 'MT'
    assert domena.lepsi_vt('2+', '2') == '2+'
    assert domena.stav_jizdy('dsq') == 'DSQ-R' and domena.stav_jizdy('95.3') is None


@test
def test_norm_rgc():
    assert norm_rgc('009162') == '9162' and norm_rgc(9162.0) == '9162'
    assert norm_rgc('057036  057054') == '57036 57054' and norm_rgc('a90001') == 'A90001'
    assert rgc_cell_value('9162') == 9162 and rgc_cell_value('1 2') == '1 2'


@test
def test_cisla_mcr_druzstev_2026():
    """Referenční startovka MČR družstev sprint 2026 (jela se)."""
    r = cisla.prirad([('c1m', 12), ('k1z', 6), ('k1m', 16), ('c1z', 4), ('c2m', 7)], 'sestupne',
                     start=70, mezera=5, vynechat=[41, 66])
    assert r['cisla']['c1m'][0] == 70 and r['cisla']['c1m'][-1] == 58
    assert r['rezervy']['c1m'] == [57, 56, 55, 54, 53]
    assert r['cisla']['k1m'] == [40] + list(range(39, 24, -1)) and 41 not in r['cisla']['k1m']
    assert r['cisla']['c2m'] == list(range(10, 3, -1))


@test
def test_cisla_rezimy():
    r = cisla.prirad([('k1m', 17), ('c1z', 5)], 'desitky')
    assert r['cisla']['c1z'][0] == 21
    r = cisla.prirad([('k1m', 3), ('c1z', 2)], 'sestupne-kat')
    assert r['cisla'] == {'k1m': [3, 2, 1], 'c1z': [2, 1]}
    r = cisla.prirad([('a', 3), ('b', 3)], 'prubezne', mezera=2, vynechat=[4])
    assert r['cisla'] == {'a': [1, 2, 3], 'b': [7, 8, 9]} and r['rezervy']['a'] == [5, 6]   # 4 chybí
    try:
        cisla.prirad([('a', 5)], 'desitky', max_cislo=3)
        raise AssertionError('čekám chybu max')
    except cisla.ChybaCisel:
        pass


# ---------- ODS vrstva ----------
@test
def test_ods_roundtrip():
    wb = Workbook(os.path.join(FIX, 'slalom.ods'))
    sl = wb.sheet('k1m_sl')
    sl.set_input(2, 1, 17)
    sl.set_input(2, 2, 23001)
    sl.set_input(3, 2, '23001 23002')
    reg = wb.sheet('reg')
    n = reg.nrows
    reg.set(n + 3, 0, 'x')                 # za koncem listu
    reg.set(n - 50, 20, 'y')               # uvnitř opakovaného bloku (pokud tam je)
    try:
        sl.set_input(2, 3, 'jméno')
        raise AssertionError('zápis do vzorce musí selhat')
    except ValueError:
        pass
    out = t('rt.ods')
    wb.save(out)
    z = zipfile.ZipFile(out)
    first = z.infolist()[0]
    assert first.filename == 'mimetype' and first.compress_type == zipfile.ZIP_STORED
    wb2 = Workbook(out)
    s2 = wb2.sheet('k1m_sl')
    assert s2.get(2, 1) == 17.0 and s2.get(2, 2) == 23001.0 and s2.get(3, 2) == '23001 23002'
    assert s2.formula(2, 3), 'vzorec ve sloupci D musí zůstat'
    assert wb2.sheet('reg').get(n + 3, 0) == 'x'
    try:
        wb.save(os.path.join(FIX, 'slalom.ods'))
        raise AssertionError('přepsání vstupu musí selhat')
    except ValueError:
        pass


@test
def test_inspect():
    out = run('inspect_workbook.py', os.path.join(FIX, 'hlidky_sprint.ods'))
    assert 'uuper(' in out and 'hlídky: ano' in out
    out = run('inspect_workbook.py', os.path.join(FIX, 'slalom.ods'), '--json')
    d = json.loads(out)
    assert d['param']['pole']['Řádek/list']['hodnota'] == 200.0
    assert {k['kod'] for k in d['kategorie']} >= {'k1m', 'k1z', 'pzk', 'c2x'}


# ---------- přihlášky a startovka ----------
@test
def test_prihlasky():
    out = run('prihlasky.py', 'csv', os.path.join(FIX, 'prihlasky.csv'), '--sablona', os.path.join(FIX, 'slalom.ods'),
              '--zavod', '135', '-o', t('lode.json'), ok=(1,))
    d = json.load(open(t('lode.json'), encoding='utf-8'))
    s = d['souhrn']
    assert any('999999' in p for p in s['problemy']), s['problemy']
    assert s['vyrazeno_jiny_zavod'] == 1
    assert s['po_kategoriich'].get('pzk', 0) + s['po_kategoriich'].get('pzc', 0) >= 1, s['po_kategoriich']
    assert s['po_kategoriich']['k1z'] >= 9            # K1W → k1z, i cizinka
    ok = [l for l in d['lode'] if not l['kontrola']['problemy']]
    json.dump({'lode': ok, 'souhrn': {'problemy': []}}, open(t('lode_ok.json'), 'w', encoding='utf-8'), ensure_ascii=False)


@test
def test_startovka():
    if not os.path.exists(t('lode_ok.json')):
        test_prihlasky()
    nast = {'poradi_kategorii': ['k1m', 'c1z', 'c2m', 'pzk', 'c1m', 'pzc', 'k1z', 'c2x'],
            'nasazeni': {'metoda': 'vt-los', 'smer': 'nejslabsi-prvni', 'seed': 42},
            'cisla': {'rezim': 'desitky', 'vynechat': [13]}}
    json.dump(nast, open(t('nast.json'), 'w', encoding='utf-8'))
    run('startovka.py', 'nasad', t('lode_ok.json'), os.path.join(FIX, 'slalom.ods'), '-c', t('nast.json'),
        '-o', t('plan.json'))
    plan1 = json.load(open(t('plan.json'), encoding='utf-8'))
    run('startovka.py', 'zapis', t('plan.json'), os.path.join(FIX, 'slalom.ods'), t('startovka.ods'))
    plan = json.load(open(t('plan.json'), encoding='utf-8'))
    k1m = next(k for k in plan['kategorie'] if k['kat'] == 'k1m')
    stc = [p['stc'] for p in k1m['lode']]
    assert stc[0] == 1 and 13 not in stc
    # VT skupiny: nejslabší první → rank neklesá
    ranks = [domena.vt_skupina(p['vt']) for p in k1m['lode']]
    assert ranks == sorted(ranks, reverse=True), ranks
    wb = Workbook(t('startovka.ods'))
    sl = wb.sheet('k1m_sl')
    assert sl.get(2, 1) == stc[0] and norm_rgc(sl.get(2, 2)) == k1m['lode'][0]['rgc'][0]
    # stejný seed → stejné pořadí
    run('startovka.py', 'nasad', t('lode_ok.json'), os.path.join(FIX, 'slalom.ods'), '-c', t('nast.json'),
        '-o', t('plan2.json'))
    plan2 = json.load(open(t('plan2.json'), encoding='utf-8'))
    assert [p['rgc'] for k in plan2['kategorie'] for p in k['lode']] == \
           [p['rgc'] for k in plan1['kategorie'] for p in k['lode']]
    # obsazený list bez --prepsat odmítne
    run('startovka.py', 'zapis', t('plan.json'), t('startovka.ods'), t('startovka2.ods'), ok=(1,))


@test
def test_startovka_verify():
    if not have_lo():
        raise Skip('LibreOffice není')
    if not os.path.exists(t('startovka.ods')):
        test_startovka()
    out = run('verify_workbook.py', t('startovka.ods'), '--plan', t('plan.json'))
    assert 'OK — žádné problémy' in out, out


# ---------- hlídky ----------
@test
def test_hlidky():
    run('hlidky.py', 'loni', os.path.join(FIX, 'loni_hlidky.xlsx'), '-o', t('loni.json'))
    loni = json.load(open(t('loni.json'), encoding='utf-8'))
    assert loni['k1m'][-1]['umisteni'] == 'DNF/DSQ' and loni['k1m'][0]['poradi'] == 1
    nast = {'poradi_kategorii': ['c1m', 'k1z', 'k1m'], 'nasazeni': {'pismena': 'podle-nasazeni'},
            'cisla': {'rezim': 'sestupne', 'start': 40, 'mezera': 3, 'vynechat': [33]}}
    json.dump(nast, open(t('hnast.json'), 'w', encoding='utf-8'))
    run('hlidky.py', 'nasad', os.path.join(FIX, 'hlidky.json'), os.path.join(FIX, 'hlidky_sprint.ods'),
        '--loni', t('loni.json'), '-c', t('hnast.json'), '-o', t('hplan.json'))
    plan = json.load(open(t('hplan.json'), encoding='utf-8'))
    for k in plan['kategorie']:
        vazby = [h['vazba'] for h in k['hlidky']]
        assert vazby[0].startswith('nová'), vazby          # nová hlídka jde na začátek
        assert all(v.startswith('osoba') for v in vazby[1:]), vazby
        loni_por = [h['loni'] for h in k['hlidky'][1:]]
        assert loni_por == sorted(loni_por, reverse=True)  # vítěz poslední
    out = run('hlidky.py', 'zapis', t('hplan.json'), os.path.join(FIX, 'hlidky_sprint.ods'), t('hlidky_out.ods'))
    assert 'uuper' in out
    wb = Workbook(t('hlidky_out.ods'))
    assert wb.sheet('hlidky').get(1, 0) == 'C1M-01'
    assert wb.sheet('c1m_sl').get(2, 15) == 'C1M-01' and wb.sheet('c1m_sl').get(2, 1) == 40.0
    assert not any('uuper(' in (v or '') for row in wb.sheet('hlidky').values(max_rows=5, max_cols=48, formulas=True)
                   for v in row if isinstance(v, str))


# ---------- výsledky ----------
@test
def test_casy():
    if not os.path.exists(t('startovka.ods')):
        test_startovka()
    plan = json.load(open(t('plan.json'), encoding='utf-8'))
    k1m = next(k for k in plan['kategorie'] if k['kat'] == 'k1m')
    s1, s2 = k1m['lode'][0]['stc'], k1m['lode'][1]['stc']
    open(t('casy.csv'), 'w', encoding='utf-8').write(
        'kat;stc;jizda;cas;pen;stav\n'
        f'K1M;{s1};1;95,23;2;\nK1M;{s1};2;1:33.10;0;\nK1M;{s2};1;;;DNF\nK1M;{s2};2;101.5;50;\n'
        'K1M;999;1;90;0;\n')
    run('casy.py', 'zapis', t('casy.csv'), t('startovka.ods'), t('vysledky.ods'), ok=(1,))
    wb = Workbook(t('vysledky.ods'))
    sl = {int(r[1]): int(r[0]) for r in wb.sheet('k1m_sl').values(max_cols=3)[2:] if len(r) > 2 and isinstance(r[1], float)}
    rows = {int(r[0]): r for r in wb.sheet('k1m').values(max_cols=16)[2:] if r and isinstance(r[0], float)}
    r1, r2 = rows[sl[s1]] + [None] * 16, rows[sl[s2]] + [None] * 16
    assert r1[11] == 95.23 and r1[12] == 2.0 and r1[14] == 93.1
    assert r2[11] == 'DNF' and r2[12] == 999.0
    open(t('casy2.csv'), 'w', encoding='utf-8').write('kat;stc;jizda;start;cil\nk1m;5;1;10:59:50,00;11:01:35,27\n')
    run('casy.py', 'eskymo', t('casy2.csv'), t('casy.txt'))
    assert open(t('casy.txt'), encoding='cp1250').read().strip() == 'k1m;5;1;10:59:50,000;11:01:35,270'


@test
def test_canoe123():
    try:
        import odf  # noqa: F401
    except ImportError:
        raise Skip('odfpy není')
    out = run('canoe123.py', 'prehled', os.path.join(FIX, 'canoe123.xml'), '--sablona', os.path.join(FIX, 'slalom.ods'),
              ok=(1,))
    assert 'NEZNÁMÉ TŘÍDY' in out and 'XYZ' in out and 'debl ve starém slepeném formátu: 1' in out
    out = run('canoe123.py', 'slalom', os.path.join(FIX, 'canoe123.xml'), os.path.join(FIX, 'slalom.ods'),
              t('c123.ods'), '--day', '15', '--race', '135', '--date', '15.08.26', ok=(0, 1))
    assert 'K1Z → k1z_sl: 6 startovka' in out, out
    assert 'VAROVÁNÍ: třídu XYZ' in out
    wb = Workbook(t('c123.ods'))
    c1m = [r[2] for r in wb.sheet('c1m_sl').values(max_cols=3)[2:] if len(r) > 2 and r[2]]
    assert 'A90002' in c1m, c1m          # cizinec bez ICFId spárován jménem na existující A-kód v cizi
    if have_lo():
        v = run('verify_workbook.py', t('c123.ods'), '--vysledky', ok=(0, 1))
        assert 'bez času i stavu' not in v, v


@test
def test_kalendar():
    out = run('kalendar.py', os.path.join(FIX, 'rozpis.html'), '-o', t('zavod.json'))
    d = json.load(open(t('zavod.json'), encoding='utf-8'))
    e = d['zavody'][0]['eskymo']
    assert d['zavody'][0]['cislo'] == '135' and e['bhz']['hodnota'] == 4
    assert e['body']['hodnota'][0] == 'bhz-č'
    assert set(e['kategorie']['hodnota']) == {'k1m', 'c1m', 'c2m', 'k1z', 'c1z', 'c2x', 'pzk', 'pzc'}
    assert e['poradi_startu']['hodnota'][:4] == ['k1m', 'c1z', 'c2m', 'pzk']
    assert e['datum']['hodnota'] == '03.10.26' and 'disciplína' in out


@test
def test_check_rules_online():
    if '--online' not in sys.argv:
        raise Skip('bez --online')
    out = run('check_rules.py', '--sezona', '2026', ok=(0, 3))
    assert 'VERDIKT' in out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-k')
    ap.add_argument('--online', action='store_true')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    ok = fail = skip = 0
    for fn in TESTS:
        if a.k and a.k not in fn.__name__:
            continue
        try:
            fn()
            ok += 1
            print(f'  ✓ {fn.__name__}')
        except Skip as e:
            skip += 1
            print(f'  - {fn.__name__} (přeskočeno: {e})')
        except Exception:
            fail += 1
            print(f'  ✗ {fn.__name__}')
            traceback.print_exc()
    print(f'\n{ok} prošlo, {fail} selhalo, {skip} přeskočeno')
    shutil.rmtree(TMP, ignore_errors=True)
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
