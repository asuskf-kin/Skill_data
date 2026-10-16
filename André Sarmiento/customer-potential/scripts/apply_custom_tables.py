#!/usr/bin/env python3
"""
apply_custom_tables.py — XML surgery for slides 8, 9, 10 in Custom mode.

Called AFTER apply_kpis.py has filled in data values.
Removes unused category columns and resizes/centers tables.

Slide 8  — Multi-category table
  Traditional:  10 cols = label + (POS,Ventas,Aporte)×3 cats (CC, SF, SS)
  Custom 1cat:   4 cols = label + (POS,Ventas,Aporte)×1 cat, centered
  Custom N cats: 1+3N cols, centered

Slides 9/10 — Subchannel/City Top5 table
  Traditional:  6 cols = name + PDV + TP + CC + SF + SS
  Custom 1cat:  3 cols = name + PDV + Cat1, expanded to full original width
  Custom N cats: 2+N cols, expanded to full original width
"""

import re
from pathlib import Path
from lxml import etree

SLIDE_W = 9_144_000  # 10" in EMU

NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = lambda t: f'{{{NS_A}}}{t}'
P = lambda t: f'{{{NS_P}}}{t}'

# ── Parsing ───────────────────────────────────────────────────────────────────

def parse(xml_str):
    return etree.fromstring(xml_str.encode('utf-8'))

def serialize(root):
    return etree.tostring(root, encoding='unicode', xml_declaration=False)

def find_table(root):
    """Return (graphicFrame, table_element) or (None, None)."""
    for frame in root.iter(P('graphicFrame')):
        tbl = frame.find(f'.//{A("tbl")}')
        if tbl is not None:
            return frame, tbl
    return None, None

def get_rows(tbl):
    return tbl.findall(A('tr'))

def get_cells(tr):
    return tr.findall(A('tc'))

def cell_span(tc):
    gs = tc.get('gridSpan')
    return int(gs) if gs else 1

def is_vmerge(tc):
    return tc.get('vMerge') is not None or tc.find(f'.//{A("vMerge")}') is not None

def get_col_widths(tbl):
    grid = tbl.find(A('tblGrid'))
    return [int(gc.get('w', 0)) for gc in grid.findall(A('gridCol'))] if grid else []

def set_col_widths(tbl, widths):
    grid = tbl.find(A('tblGrid'))
    if grid is None: return
    for gc, w in zip(grid.findall(A('gridCol')), widths):
        gc.set('w', str(int(w)))

def set_frame_geom(frame, x=None, cx=None):
    xfrm = frame.find(f'.//{A("xfrm")}')
    if xfrm is None: return
    if x  is not None:
        off = xfrm.find(A('off'))
        if off is not None: off.set('x', str(int(x)))
    if cx is not None:
        ext = xfrm.find(A('ext'))
        if ext is not None: ext.set('cx', str(int(cx)))

def get_cell_text(tc):
    return ''.join(t.text or '' for t in tc.iter(A('t')))

def set_cell_text(tc, new_text):
    """Replace ALL text content in a cell with new_text, preserving first rPr for styling."""
    paras = tc.findall(f'.//{A("p")}')
    if not paras:
        return

    first_p = paras[0]

    # Collect rPr from first existing run for styling
    rpr_copy = None
    for r in first_p.findall(A('r')):
        rpr = r.find(A('rPr'))
        if rpr is not None:
            import copy
            rpr_copy = copy.deepcopy(rpr)
        break

    # Clear ALL runs from ALL paragraphs
    for p in paras:
        for r in p.findall(A('r')):
            p.remove(r)

    # Remove extra paragraphs (keep only first)
    parent = first_p.getparent()
    for extra_p in paras[1:]:
        if extra_p.getparent() is not None:
            extra_p.getparent().remove(extra_p)

    # Add single run to first paragraph
    r_el = etree.SubElement(first_p, A('r'))
    if rpr_copy is not None:
        r_el.insert(0, rpr_copy)
    t_el = etree.SubElement(r_el, A('t'))
    t_el.text = new_text


# ── Column removal ────────────────────────────────────────────────────────────

def remove_columns(tbl, cols_to_remove):
    """
    Remove columns by index from a table.
    Handles gridSpan cells (merged headers).
    """
    if not cols_to_remove:
        return
    col_set = set(cols_to_remove)

    # 1. Remove from tblGrid
    grid = tbl.find(A('tblGrid'))
    if grid is not None:
        gridcols = grid.findall(A('gridCol'))
        for idx in sorted(col_set, reverse=True):
            if idx < len(gridcols):
                grid.remove(gridcols[idx])

    # 2. Remove/shrink cells in each row
    for tr in tbl.findall(A('tr')):
        cells = tr.findall(A('tc'))

        # Map effective column index → (cell, span)
        eff = 0
        col_map = []  # list of (eff_start, span, cell)
        for tc in cells:
            span = cell_span(tc)
            col_map.append((eff, span, tc))
            eff += span

        to_remove = []
        for eff_start, span, tc in col_map:
            covered = set(range(eff_start, eff_start + span))
            removed  = covered & col_set
            kept     = covered - col_set
            if not removed:
                continue
            if not kept:
                to_remove.append(tc)
            else:
                # Partial span reduction
                new_span = len(kept)
                if new_span == 1:
                    tc.attrib.pop('gridSpan', None)
                else:
                    tc.set('gridSpan', str(new_span))

        for tc in to_remove:
            tr.remove(tc)


# ── Slide 8 ───────────────────────────────────────────────────────────────────

# Original 10-column widths from Nayar template (EMU)
SLIDE8_ORIG_WIDTHS = [837000, 710275, 788925, 1023650,
                      900650, 900650, 906650, 819125, 819125, 904900]

def apply_slide8_custom(xml_str, custom_cats, s8_data):
    """
    Remove unused category columns from slide 8 and center the table.
    Renames the category header to the custom cat name.
    custom_cats: e.g. ['Stills']
    s8_data: kpis['s8']
    """
    root   = parse(xml_str)
    frame, tbl = find_table(root)
    if tbl is None:
        return xml_str

    n_cats      = len(custom_cats)
    n_keep_cols = 1 + 3 * n_cats          # label + 3 cols per cat
    total_cols  = len(get_col_widths(tbl))
    to_remove   = list(range(n_keep_cols, total_cols))

    remove_columns(tbl, to_remove)

    # Rename category header(s) in row 0
    rows = get_rows(tbl)
    if rows:
        row0_cells = get_cells(rows[0])
        # Cat headers start at cell index 1 in row 0 (cell 0 = "Potencial" with rowSpan)
        cat_header_cells = [tc for tc in row0_cells if tc.get('gridSpan')]
        for i, (tc, cat_name) in enumerate(zip(cat_header_cells, custom_cats)):
            set_cell_text(tc, cat_name)

    # Recalculate widths (keep first n_keep_cols original widths)
    new_widths = SLIDE8_ORIG_WIDTHS[:n_keep_cols]
    set_col_widths(tbl, new_widths)
    total_w = sum(new_widths)

    # Center horizontally on slide
    new_x = (SLIDE_W - total_w) // 2
    set_frame_geom(frame, x=new_x, cx=total_w)

    # Fix narrative: replace "Coca Cola" with first custom cat name in all text runs
    first_cat = custom_cats[0]
    for t_el in root.iter(A('t')):
        if t_el.text and 'Coca Cola' in t_el.text:
            t_el.text = t_el.text.replace('Coca Cola', first_cat)

    return serialize(root)

# Slide 9 original 6-col widths (Nayar template)
SLIDE9_ORIG_WIDTHS = [3_639_450, 1_014_975, 840_600, 1_032_750, 1_087_800, 1_024_425]
SLIDE9_ORIG_CX = sum(SLIDE9_ORIG_WIDTHS)   # 8_640_000
SLIDE9_ORIG_X  = 213_975

# Slide 10 original 6-col widths
SLIDE10_ORIG_WIDTHS = [2_367_600, 904_575, 1_133_850, 1_124_550, 1_279_800, 1_279_800]
SLIDE10_ORIG_CX = sum(SLIDE10_ORIG_WIDTHS)  # 8_090_175
SLIDE10_ORIG_X  = 532_050

def apply_slide910_custom(xml_str, custom_cats, orig_widths, orig_cx, orig_x):
    """
    Remove traditional category columns (TP, CC, SF, SS) from slides 9/10.
    Keeps: name + PDV + custom cat columns.
    Expands remaining columns proportionally to fill original total width.
    Renames aporte column headers to custom cat names.
    """
    root   = parse(xml_str)
    frame, tbl = find_table(root)
    if tbl is None:
        return xml_str

    n_cats     = len(custom_cats)
    keep_cols  = 2 + n_cats               # name + PDV + n custom cats
    total_cols = len(get_col_widths(tbl))  # 6
    to_remove  = list(range(keep_cols, total_cols))

    remove_columns(tbl, to_remove)

    # Rename aporte column headers (row 0, cols 2..2+n_cats-1)
    rows = get_rows(tbl)
    if rows:
        row0_cells = get_cells(rows[0])
        for cat_idx, cat_name in enumerate(custom_cats):
            col_idx = 2 + cat_idx
            if col_idx < len(row0_cells):
                set_cell_text(row0_cells[col_idx],
                              f'Aporte al crecimiento\n({cat_name})')

    # Expand remaining columns proportionally to fill original total width
    kept_orig = orig_widths[:keep_cols]
    scale     = orig_cx / sum(kept_orig)
    new_widths = [int(w * scale) for w in kept_orig]
    diff = orig_cx - sum(new_widths)
    new_widths[0] += diff   # absorb rounding in the name column
    set_col_widths(tbl, new_widths)

    # Keep frame at original position/size
    set_frame_geom(frame, x=orig_x, cx=orig_cx)

    return serialize(root)


# ── Public entrypoint ─────────────────────────────────────────────────────────

def apply_all(unpacked_dir, kpis, metadata):
    """
    Apply all custom table fixes.
    Call AFTER apply_kpis.py has filled in data.
    """
    if metadata.get('run_type') != 'custom':
        return

    custom_cats = metadata.get('custom_cats', [])
    if not custom_cats:
        return

    unpacked = Path(unpacked_dir)

    p8  = unpacked / 'ppt/slides/slide8.xml'
    p9  = unpacked / 'ppt/slides/slide9.xml'
    p10 = unpacked / 'ppt/slides/slide10.xml'

    if p8.exists():
        xml = apply_slide8_custom(
            p8.read_text('utf-8'), custom_cats, kpis.get('s8', {}))
        p8.write_text(xml, 'utf-8')
        print(f'  ✓ Slide 8:  {n_cols_str(custom_cats)} cats — centered')

    if p9.exists():
        xml = apply_slide910_custom(
            p9.read_text('utf-8'), custom_cats,
            SLIDE9_ORIG_WIDTHS, SLIDE9_ORIG_CX, SLIDE9_ORIG_X)
        p9.write_text(xml, 'utf-8')
        print(f'  ✓ Slide 9:  only {cats_str(custom_cats)} — full width')

    if p10.exists():
        xml = apply_slide910_custom(
            p10.read_text('utf-8'), custom_cats,
            SLIDE10_ORIG_WIDTHS, SLIDE10_ORIG_CX, SLIDE10_ORIG_X)
        p10.write_text(xml, 'utf-8')
        print(f'  ✓ Slide 10: only {cats_str(custom_cats)} — full width')


def n_cols_str(cats): return str(len(cats))
def cats_str(cats): return ' + '.join(cats)


if __name__ == '__main__':
    print('apply_custom_tables.py — import and call apply_all()')
