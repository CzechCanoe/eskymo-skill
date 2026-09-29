# -*- coding: utf-8 -*-
"""
eskymo_ods — čtení a zápis Eskymo sešitů (.ods) přímo přes content.xml (lxml).

Proč ne odfpy: odfpy padá při dělení opakovaných buněk
(`remove_from_caches: x not in list`). Přímá práce s XML zachová vzorce,
styly i namespacy a nic dalšího v souboru nemění.

Co vrstva řeší za tebe:
  * logické adresování řádek/sloupec (0-based) přes `number-rows-repeated`
    i `number-columns-repeated` — opakované řádky/buňky se při zápisu
    rozdělí a kopie si ponechají obsah i styl;
  * typované hodnoty (číslo / text / prázdno), víceřádkový text (`\\n`),
    čtení vzorců a nacachovaných výsledků vzorců (včetně chyb `#N/A`);
  * uložení s `mimetype` jako první nekomprimovanou položkou ZIPu
    (jinak Calc/Eskymo soubor odmítne).

Co vrstva NEDĚLÁ: nepřepočítává vzorce. Po zápisu jsou výsledky vzorců
v souboru zastaralé — pro kontrolu použij `recalc.py`, člověk v Eskymu
Ctrl+Shift+F9.

Příklad:
    from eskymo_ods import Workbook
    wb = Workbook('sablona.ods')
    sl = wb.sheet('k1m_sl')
    sl.set(2, 1, 17)            # řádek 3, sloupec B (stč) = 17
    sl.set(2, 2, '9162')        # text; pro čísla předej int/float
    print(sl.get(2, 3))         # nacachovaná hodnota vzorce (jméno)
    wb.save('vystup.ods')
"""
from __future__ import annotations

import copy
import os
import re
import zipfile

from lxml import etree

NS = {
    'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'calcext': 'urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0',
}
_T, _O, _X, _C = NS['table'], NS['office'], NS['text'], NS['calcext']

TABLE = f'{{{_T}}}table'
ROW = f'{{{_T}}}table-row'
CELL = f'{{{_T}}}table-cell'
COVERED = f'{{{_T}}}covered-table-cell'
ROWS_REP = f'{{{_T}}}number-rows-repeated'
COLS_REP = f'{{{_T}}}number-columns-repeated'
FORMULA = f'{{{_T}}}formula'
TNAME = f'{{{_T}}}name'
VTYPE = f'{{{_O}}}value-type'
VALUE = f'{{{_O}}}value'
CVTYPE = f'{{{_C}}}value-type'
P = f'{{{_X}}}p'
_VALUE_ATTRS = [VTYPE, VALUE, CVTYPE, f'{{{_O}}}date-value', f'{{{_O}}}time-value',
                f'{{{_O}}}boolean-value', f'{{{_O}}}string-value', f'{{{_O}}}currency']

# Skryté/pomocné entity, které nejsou řádky listu (vnořené tabulky apod.)
_ROW_CONTAINERS = {f'{{{_T}}}{n}' for n in
                   ('table-header-rows', 'table-row-group', 'table-rows')}


def col_letter(idx: int) -> str:
    """0 → 'A', 25 → 'Z', 26 → 'AA'."""
    s = ''
    idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def col_index(letters: str) -> int:
    """'A' → 0, 'AA' → 26."""
    n = 0
    for ch in letters.upper():
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def parse_addr(addr: str) -> tuple[int, int]:
    """'B8' → (7, 1) — (řádek, sloupec), 0-based."""
    m = re.fullmatch(r'\$?([A-Za-z]+)\$?(\d+)', addr.strip())
    if not m:
        raise ValueError(f'neplatná adresa buňky: {addr!r}')
    return int(m.group(2)) - 1, col_index(m.group(1))


def iso_duration_days(s):
    """ODF time-value 'PT01H02M03.45S' → zlomek dne (jak čas ukládá Calc); None když nejde."""
    m = re.fullmatch(r'-?P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:([\d.]+)S)?', (s or '').strip())
    if not m:
        return None
    d, h, mi, sec = (float(x) if x else 0.0 for x in m.groups())
    val = (d * 86400 + h * 3600 + mi * 60 + sec) / 86400
    return -val if s.strip().startswith('-') else val


def _cell_text(cell) -> str:
    """Text buňky jako v Calcu: odstavce spojené \\n, text:s → mezery."""
    parts = []
    for p in cell.iter(P):
        buf = []

        def walk(el):
            if el.text:
                buf.append(el.text)
            for ch in el:
                tag = etree.QName(ch).localname
                if tag == 's':
                    buf.append(' ' * int(ch.get(f'{{{_X}}}c') or 1))
                elif tag == 'tab':
                    buf.append('\t')
                elif tag == 'line-break':
                    buf.append('\n')
                else:
                    walk(ch)
                if ch.tail:
                    buf.append(ch.tail)
        walk(p)
        parts.append(''.join(buf))
    return '\n'.join(parts)


def _cell_value(cell):
    """Hodnota buňky: float / str / None. U vzorců nacachovaný výsledek."""
    vt = cell.get(VTYPE)
    if vt in ('float', 'percentage', 'currency'):
        v = cell.get(VALUE)
        return float(v) if v is not None else None
    if vt == 'date':
        return cell.get(f'{{{_O}}}date-value')
    if vt == 'time':
        return iso_duration_days(cell.get(f'{{{_O}}}time-value'))
    if vt == 'boolean':
        return cell.get(f'{{{_O}}}boolean-value') == 'true'
    txt = _cell_text(cell)
    if vt == 'string' or cell.get(CVTYPE) == 'error' or txt:
        return txt
    return None


class Sheet:
    """Jeden list sešitu s logickým (0-based) adresováním."""

    def __init__(self, wb: 'Workbook', el):
        self.wb = wb
        self.el = el
        self.name = el.get(TNAME)
        self._index = None

    # ---------- indexace řádků ----------
    def _rows_in_order(self):
        out = []

        def walk(parent):
            for ch in parent:
                if ch.tag == ROW:
                    out.append(ch)
                elif ch.tag in _ROW_CONTAINERS:
                    walk(ch)
        walk(self.el)
        return out

    def _build_index(self):
        idx, r = [], 0
        for el in self._rows_in_order():
            rep = int(el.get(ROWS_REP) or 1)
            idx.append((r, rep, el))
            r += rep
        self._index = idx
        return idx

    @property
    def nrows(self) -> int:
        idx = self._index or self._build_index()
        return idx[-1][0] + idx[-1][1] if idx else 0

    def _row_el(self, r: int, split: bool):
        idx = self._index or self._build_index()
        for start, rep, el in idx:
            if start <= r < start + rep:
                if rep == 1 or not split:
                    return el
                return self._split_row(el, start, rep, r)
        if not split:
            return None
        # za koncem listu — dopiš prázdné řádky
        parent = idx[-1][2].getparent() if idx else self.el
        missing = r - self.nrows
        if missing > 0:
            pad = etree.SubElement(parent, ROW)
            etree.SubElement(pad, CELL)
            if missing > 1:
                pad.set(ROWS_REP, str(missing))
        new = etree.SubElement(parent, ROW)
        etree.SubElement(new, CELL)
        self._index = None
        return new

    def _split_row(self, el, start, rep, r):
        parent = el.getparent()
        pos = parent.index(el)
        before, after = r - start, start + rep - r - 1
        pieces = []
        for n in (before, 1, after):
            if n <= 0:
                pieces.append(None)
                continue
            c = copy.deepcopy(el)
            if n > 1:
                c.set(ROWS_REP, str(n))
            else:
                c.attrib.pop(ROWS_REP, None)
            pieces.append(c)
        parent.remove(el)
        for off, c in enumerate([p for p in pieces if p is not None]):
            parent.insert(pos + off, c)
        self._index = None
        return pieces[1]

    # ---------- indexace buněk ----------
    @staticmethod
    def _cells(row_el):
        return [c for c in row_el if c.tag in (CELL, COVERED)]

    def _cell_el(self, r: int, c: int, split: bool):
        row = self._row_el(r, split)
        if row is None:
            return None
        col = 0
        for cell in self._cells(row):
            rep = int(cell.get(COLS_REP) or 1)
            if col <= c < col + rep:
                if rep == 1 or not split:
                    return cell
                return self._split_cell(row, cell, col, rep, c)
            col += rep
        if not split:
            return None
        if c - col > 0:
            pad = etree.SubElement(row, CELL)
            if c - col > 1:
                pad.set(COLS_REP, str(c - col))
        return etree.SubElement(row, CELL)

    @staticmethod
    def _split_cell(row, cell, col, rep, c):
        pos = row.index(cell)
        before, after = c - col, col + rep - c - 1
        pieces = []
        for n in (before, 1, after):
            if n <= 0:
                pieces.append(None)
                continue
            k = copy.deepcopy(cell)
            if n > 1:
                k.set(COLS_REP, str(n))
            else:
                k.attrib.pop(COLS_REP, None)
            pieces.append(k)
        row.remove(cell)
        for off, k in enumerate([p for p in pieces if p is not None]):
            row.insert(pos + off, k)
        return pieces[1]

    # ---------- veřejné API ----------
    def get(self, r: int, c: int):
        """Hodnota (float/str/None). U vzorce jeho poslední nacachovaný výsledek."""
        cell = self._cell_el(r, c, split=False)
        return None if cell is None or cell.tag == COVERED else _cell_value(cell)

    def formula(self, r: int, c: int):
        cell = self._cell_el(r, c, split=False)
        return None if cell is None else cell.get(FORMULA)

    def get_a1(self, addr: str):
        return self.get(*parse_addr(addr))

    def set(self, r: int, c: int, value, keep_formula: bool = False):
        """Zapíše hodnotu. int/float → číslo, str → text, None → prázdná buňka.

        Vzorec v cílové buňce se odstraní (pokud nechceš jinak), styl zůstane.
        Zápis do vzorcové buňky je obvykle chyba — `set_input` to hlídá.
        """
        cell = self._cell_el(r, c, split=True)
        if cell.tag == COVERED:
            raise ValueError(f'{self.name}!{col_letter(c)}{r + 1} je sloučená (covered) buňka')
        for a in _VALUE_ATTRS:
            cell.attrib.pop(a, None)
        if not keep_formula:
            cell.attrib.pop(FORMULA, None)
        for ch in list(cell):
            if ch.tag == P:
                cell.remove(ch)
        if value is None or value == '':
            return cell
        if isinstance(value, bool):
            raise TypeError('boolean do Eskyma nepíšeme — použij 0/1 nebo text')
        if isinstance(value, (int, float)):
            cell.set(VTYPE, 'float')
            cell.set(VALUE, repr(float(value)) if isinstance(value, float) else str(value))
            if self.wb.has_calcext:
                cell.set(CVTYPE, 'float')
            p = etree.SubElement(cell, P)
            p.text = (str(int(value)) if float(value).is_integer() else str(value)).replace('.', ',')
        else:
            cell.set(VTYPE, 'string')
            if self.wb.has_calcext:
                cell.set(CVTYPE, 'string')
            for line in str(value).split('\n'):
                p = etree.SubElement(cell, P)
                p.text = line
        self.wb.dirty = True
        return cell

    def set_input(self, r: int, c: int, value):
        """Jako `set`, ale odmítne přepsat buňku se vzorcem (ochrana šablony)."""
        f = self.formula(r, c)
        if f:
            raise ValueError(f'{self.name}!{col_letter(c)}{r + 1} obsahuje vzorec {f!r} — '
                             'do vzorcových buněk Eskyma se nepíše')
        return self.set(r, c, value)

    def set_a1(self, addr: str, value):
        return self.set(*parse_addr(addr), value)

    def values(self, max_rows: int | None = None, max_cols: int = 64, formulas: bool = False):
        """Mřížka hodnot (nebo vzorců) jako list listů; opakované řádky se rozbalí.

        Dlouhé prázdné opakované konce (1M řádků) se ořežou.
        """
        out = []
        for el in self._rows_in_order():
            rep = int(el.get(ROWS_REP) or 1)
            row, col = [], 0
            for cell in self._cells(el):
                crep = int(cell.get(COLS_REP) or 1)
                if cell.tag == COVERED:
                    v = None
                elif formulas and cell.get(FORMULA):
                    v = cell.get(FORMULA)
                else:
                    v = _cell_value(cell)
                for _ in range(min(crep, max_cols - col)):
                    row.append(v)
                col += crep
                if col >= max_cols:
                    break
            while row and row[-1] in (None, ''):
                row.pop()
            if not row and rep > 10000:
                break  # obří prázdný opakovaný blok = konec listu
            for _ in range(rep):
                out.append(list(row))
                if max_rows is not None and len(out) >= max_rows:
                    return out
        while out and not out[-1]:
            out.pop()
        return out

    def find(self, text: str, max_rows: int = 200, max_cols: int = 30):
        """Najde první buňku, jejíž text se (bez ohledu na velikost) rovná `text`."""
        t = text.strip().lower()
        for r, row in enumerate(self.values(max_rows=max_rows, max_cols=max_cols)):
            for c, v in enumerate(row):
                if isinstance(v, str) and v.strip().lower() == t:
                    return r, c
        return None


class Workbook:
    def __init__(self, path: str):
        self.path = path
        with zipfile.ZipFile(path) as z:
            self._order = z.namelist()
            self.parts = {n: z.read(n) for n in self._order}
        if 'content.xml' not in self.parts:
            raise ValueError(f'{path}: není to ODS (chybí content.xml)')
        self.tree = etree.fromstring(self.parts['content.xml'])
        self.has_calcext = _C in (self.tree.nsmap or {}).values()
        self.dirty = False

    def sheet_names(self) -> list[str]:
        return [t.get(TNAME) for t in self.tree.iter(TABLE)]

    def has(self, name: str) -> bool:
        return name in self.sheet_names()

    def sheet(self, name: str) -> Sheet:
        for t in self.tree.iter(TABLE):
            if t.get(TNAME) == name:
                return Sheet(self, t)
        raise KeyError(f'list {name!r} v sešitu není; jsou tam: {", ".join(self.sheet_names())}')

    def patch_formulas(self, old: str, new: str, sheets=None) -> int:
        """Náhrada textu ve vzorcích (např. překlep `uuper(` → `UPPER(`). Vrací počet buněk."""
        n = 0
        for t in self.tree.iter(TABLE):
            if sheets and t.get(TNAME) not in sheets:
                continue
            for c in t.iter(CELL):
                f = c.get(FORMULA)
                if f and old in f:
                    c.set(FORMULA, f.replace(old, new))
                    n += 1
        if n:
            self.dirty = True
        return n

    def save(self, out: str):
        if os.path.abspath(out) == os.path.abspath(self.path):
            raise ValueError('výstup se nesmí jmenovat stejně jako vstup — vstupy pořadatele nepřepisujeme')
        data = dict(self.parts)
        data['content.xml'] = etree.tostring(self.tree, xml_declaration=True,
                                             encoding='UTF-8', standalone=True)
        tmp = out + '.tmp'
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
            if 'mimetype' in data:
                z.writestr(zipfile.ZipInfo('mimetype'), data.pop('mimetype'),
                           compress_type=zipfile.ZIP_STORED)
            for name in self._order:
                if name in data:
                    z.writestr(name, data.pop(name))
            for name, blob in data.items():
                z.writestr(name, blob)
        os.replace(tmp, out)


# ---------- pomocníci pro doménu ----------
def norm_rgc(x) -> str:
    """'009162' → '9162', 9162.0 → '9162'. Cizinci ('A90001') a C2 dvojice
    ('57036 57054') se normalizují po částech, jinak beze změny."""
    if x is None:
        return ''
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    s = str(x).strip()
    if ' ' in s:
        return ' '.join(norm_rgc(p) for p in s.split())
    if s.isdigit():
        return str(int(s))
    return s.upper() if re.fullmatch(r'[aA]\d+', s) else s


def rgc_cell_value(rgc):
    """Hodnota pro zápis RGC do buňky: číselné RGC jako číslo (VLOOKUP do `reg`
    páruje na čísla), cizinec `A…` a C2 dvojice jako text."""
    s = norm_rgc(rgc)
    return int(s) if s.isdigit() else s
