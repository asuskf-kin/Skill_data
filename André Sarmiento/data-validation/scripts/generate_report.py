"""
generate_report.py
Genera el reporte Word editando la plantilla embebida en assets/template.docx.
Preserva 100% del diseño: logo, imágenes decorativas, tipografía Albert Sans, colores.

Índices de párrafos (basados en template manual v7):
  [18]  Nombre del cliente
  [28]  Mes/Año
  [54]  Bullet: clientes fuera del territorio
  [55]  Bullet: duplicados / pos_name
  [56]  Bullet: coordenadas en cero
  [57]  Bullet: pos_name / pos_address
  [58]  Bullet: ciudad/subcanal vacíos
  [59]  Bullet: POS finales (bold)
  [66]  Fecha de descarga
  [67]  File
  [70]  Total registros (Identificador)
  [73]  Texto Ubicación geográfica
  [83]  Puntos descartados
  [89]  Comentario Ciudad
  [102] Comentario Subchannel
  [107] Comentario Channel
  [113] Acción 1
  [114] Acción 2
  [115] Acción 3
  Table[0] Filtros (5 cols)
  Table[1] Ciudad/Zona
  Table[2] Subchannel
  Table[3] Channel
  Table[4] Canal Macro (si existe)
"""

import shutil, os, datetime
from copy import deepcopy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt(n, d=0):
    if isinstance(n, float): return f"{n:,.{d}f}"
    if isinstance(n, int):   return f"{n:,}"
    return str(n)


def set_para_text(para, text, bold=False):
    """Reemplaza texto de un párrafo preservando su estilo."""
    p = para._p
    for r in p.findall(qn('w:r')):
        p.remove(r)
    run = para.add_run(text)
    if bold:
        run.bold = True
    return run


def update_table(tbl_el, data_rows, alt_bg='F2F2F2'):
    """Reemplaza filas de datos (mantiene cabecera)."""
    all_rows = tbl_el.findall(qn('w:tr'))
    header_row = all_rows[0]
    for row in all_rows[1:]:
        tbl_el.remove(row)
    for idx, row_data in enumerate(data_rows):
        new_row = deepcopy(header_row)
        for rPr in new_row.findall('.//' + qn('w:rPr')):
            for b   in rPr.findall(qn('w:b')):     rPr.remove(b)
            for col in rPr.findall(qn('w:color')): rPr.remove(col)
        cells = new_row.findall('.//' + qn('w:tc'))
        bg = alt_bg if idx % 2 == 0 else 'FFFFFF'
        for i, val in enumerate(row_data):
            if i < len(cells):
                _set_cell_bg(cells[i], bg)
                for t in cells[i].findall('.//' + qn('w:t')):
                    t.text = str(val); break
        tbl_el.append(new_row)


def _set_cell_bg(tc_el, hex_color):
    tcPr = tc_el.find(qn('w:tcPr'))
    if tcPr is None:
        tcPr = OxmlElement('w:tcPr'); tc_el.insert(0, tcPr)
    for s in tcPr.findall(qn('w:shd')): tcPr.remove(s)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color); tcPr.append(shd)


# ── Función principal ─────────────────────────────────────────────────────────

def generate_report(
    skill_dir:        str,
    client_name:      str  = "Femsa",
    file_name:        str  = "",
    date_str:         str  = None,
    lang:             str  = "es",
    results_clients:  dict = None,
    results_products: dict = None,
    results_sales:    dict = None,
    output_path:      str  = "Validacion_Datos_Output.docx",
) -> str:

    if date_str is None:
        date_str = datetime.date.today().strftime("%d/%m/%Y")

    template_path = os.path.join(skill_dir, "assets", "template.docx")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"No se encontró la plantilla en {template_path}.")

    shutil.copy2(template_path, output_path)
    doc        = Document(output_path)
    paras      = doc.paragraphs
    body       = doc.element.body
    tables_xml = body.findall('.//' + qn('w:tbl'))

    rc = results_clients  or {}
    rp = results_products or {}
    rs = results_sales    or {}

    if not rc:
        raise ValueError(
            "El reporte Word solo se genera cuando hay base de clientes. "
            "Para ventas o productos solos, entregar solo el CSV y el resumen en el chat."
        )

    # Cargar traducciones según idioma seleccionado
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from translations import T
    t = T(lang)

    if rc:
        total     = rc.get('total_original', 0)
        geo       = rc.get('geo', {})
        dups_nc   = rc.get('duplicates_by_name_coords', {})
        coords    = rc.get('coordinates', {})
        nulls     = rc.get('nulls', {})
        fb        = rc.get('fecha_baja', {})
        dist      = rc.get('distributions', {})
        df_final  = rc.get('df_final')
        skipped   = dups_nc.get('skipped', False)

        fuera      = geo.get('fuera_territorio', 0)
        pct_fuera  = round(fuera / total * 100, 2) if total else 0
        dups       = dups_nc.get('dropped', 0)
        lat_int    = coords.get('lat_integer', 0)
        lat_zero   = coords.get('lat_zero', 0)
        city_null  = nulls.get('pos_city', 0)
        con_baja   = fb.get('con_baja', 0)
        fb_min     = fb.get('fecha_min', 'N/A')
        fb_max     = fb.get('fecha_max', 'N/A')
        pos_final  = len(df_final) if df_final is not None else 0
        total_desc = total - pos_final

        has_pos_name = not skipped

        # ── Portada ───────────────────────────────────────────────────────────
        set_para_text(paras[18], client_name)
        set_para_text(paras[28], _month_year(date_str))

        # ── Resumen ejecutivo — bullets ───────────────────────────────────────
        set_para_text(paras[54], t('bullet_outside_territory', total=fmt(total), fuera=fmt(fuera), pct=f'{pct_fuera:.2f}'))

        if skipped:
            set_para_text(paras[55],
                f'No fue posible verificar duplicados por nombre ya que la base '
                f'no contiene pos_name. Se recomienda obtener este dato.')
        else:
            set_para_text(paras[55], t('bullet_dups', dups=fmt(dups)))

        set_para_text(paras[56], t('bullet_zero_coords', zero=fmt(lat_zero)))

        addr_null = nulls.get('pos_address', 0)
        if not has_pos_name:
            set_para_text(paras[57], t('bullet_no_address'))
        elif addr_null > 0:
            set_para_text(paras[57], t('bullet_address_nulls', addr_null=fmt(addr_null), pct=round(addr_null/total*100,1)))
        else:
            set_para_text(paras[57], t('bullet_all_complete'))

        set_para_text(paras[58],
            t('bullet_city_nulls', city_null=fmt(city_null), pct=round(city_null/total*100,1) if total else 0)
            if city_null > 0 else
            t('bullet_all_city'))

        if con_baja > 0:
            set_para_text(paras[59],
                f'{fmt(con_baja)} clientes ({round(con_baja/total*100,1)}%) tienen fecha de baja '
                f'({fb_min} → {fb_max}). Se mantienen para prospección.')
            # POS finales en un párrafo adicional (se mantiene el siguiente en la plantilla)
        else:
            set_para_text(paras[59],
                t('bullet_pos_final', pos_final=fmt(pos_final)), bold=True)

        # ── Sección Maestra Clientes ──────────────────────────────────────────
        set_para_text(paras[66], f'Fecha de Descarga: {date_str} (Base de Datos)')
        set_para_text(paras[67], f'File: {file_name}')

        set_para_text(paras[70], t('text_total_clients', total=fmt(total)))

        set_para_text(paras[73], t('text_outside_geo', fuera=fmt(fuera), pct=f'{pct_fuera:.2f}', client=client_name))

        set_para_text(paras[83],
            f'En total se descartaron {fmt(total_desc)} clientes '
            f'({round(total_desc/total*100,2):.2f}%). '
            + (f'{fmt(lat_zero)} clientes con coordenadas en cero requieren corrección.'
               if lat_zero > 0 else '')
            + (f' {fmt(con_baja)} clientes con fecha de baja se mantienen para prospección.'
               if con_baja > 0 else ''))

        # Ciudad
        set_para_text(paras[89], t('text_city_distribution'))

        # Subchannel
        if 'pos_subchannel' in dist and dist['pos_subchannel']:
            top3n   = [r['pos_subchannel'] for r in dist['pos_subchannel'][:3]]
            top3pct = sum(r['pct'] for r in dist['pos_subchannel'][:3])
            set_para_text(paras[102],
                f'{", ".join(top3n)} representan el {top3pct:.1f}% '
                f'de todos los puntos de venta.')

        # Channel
        if 'pos_consumer_type' in dist and dist['pos_consumer_type']:
            top_ct = dist['pos_consumer_type'][0]
            set_para_text(paras[107],
                f'Canal predominante: {top_ct["pos_consumer_type"]} '
                f'con el {top_ct["pct"]:.1f}% de los clientes.')

        # Puntos de acción
        set_para_text(paras[113],
            t('action_no_pos_name')
            if not has_pos_name else
            f'Eliminar los {fmt(fuera)} POS fuera del territorio de la operación.')
        set_para_text(paras[114],
            t('action_outside_geo', fuera=fmt(fuera)))
        set_para_text(paras[115],
            t('action_zero_coords', zero=fmt(lat_zero))
            if lat_zero > 0 else
            f'{fmt(con_baja)} clientes con fecha de baja se mantienen para prospección. '
            f'Para segmentación se recomienda eliminarlos.')

        # ── Tablas ────────────────────────────────────────────────────────────
        # Tabla 0: Filtros (5 columnas: Filtro, Descripción, Afectados, Restantes, %)
        pct_geo  = round(geo.get('dentro_territorio', 0) / total * 100, 2) if total else 0
        pct_dups = round((geo.get('dentro_territorio', 0) - dups) / total * 100, 2) if total else 0
        pct_fin  = round(pos_final / total * 100, 2) if total else 0

        filter_rows = [
            [t('table_filter_outside'), t('filter_outside'),
             fmt(fuera), fmt(geo.get('dentro_territorio', 0)), f'{pct_geo:.2f}%'],
        ]
        if lat_zero > 0:
            filter_rows.append([
                'Coordenadas en Cero',
                'Clientes sin ubicación válida (lat=0, lon=0).',
                fmt(lat_zero), fmt(pos_final), f'{pct_fin:.2f}%'
            ])
        if not skipped and dups > 0:
            filter_rows.append([
                'Registros Duplicados',
                'Duplicados con nombre y coordenadas idénticos.',
                fmt(dups), fmt(geo.get('dentro_territorio', 0) - dups), f'{pct_dups:.2f}%'
            ])
        if not has_pos_name:
            filter_rows.append([
                'pos_name ausente',
                'No se realizó deduplicación (dato no disponible).',
                'N/A', fmt(pos_final), f'{pct_fin:.2f}%'
            ])
        if con_baja > 0:
            filter_rows.append([
                'Fecha Baja',
                'POS con fecha de baja (se mantienen para prospección).',
                fmt(con_baja), fmt(pos_final), f'{pct_fin:.2f}%'
            ])
        if len(tables_xml) >= 1:
            update_table(tables_xml[0], filter_rows)

        # Tabla 1: Ciudad / Zona
        city_col = 'pos_city' if 'pos_city' in dist else None
        if city_col and len(tables_xml) >= 2:
            city_d  = dist[city_col]
            top_n   = city_d[:7]
            others  = sum(r['count'] for r in city_d[7:])
            total_c = sum(r['count'] for r in city_d)
            rows = [[r[city_col], fmt(r['count']), f"{r['pct']:.2f}%"] for r in top_n]
            if others: rows.append([t('table_others'), fmt(others), f'{others/total_c*100:.2f}%'])
            rows.append([t('table_total'), fmt(total_c), '100%'])
            update_table(tables_xml[1], rows)

        # Tabla 2: Subchannel
        if 'pos_subchannel' in dist and len(tables_xml) >= 3:
            sub_d   = dist['pos_subchannel']
            top9    = sub_d[:9]
            others  = sum(r['count'] for r in sub_d[9:])
            total_s = sum(r['count'] for r in sub_d)
            rows = [[r['pos_subchannel'], fmt(r['count']), f"{r['pct']:.2f}%"] for r in top9]
            if others: rows.append([t('table_others'), fmt(others), f'{others/total_s*100:.2f}%'])
            rows.append([t('table_total'), fmt(total_s), '100%'])
            update_table(tables_xml[2], rows)

        # Tabla 3: Channel
        if 'pos_consumer_type' in dist and len(tables_xml) >= 4:
            ct_d    = dist['pos_consumer_type']
            total_ct = sum(r['count'] for r in ct_d)
            rows = [[r['pos_consumer_type'], fmt(r['count']), f"{r['pct']:.2f}%"] for r in ct_d]
            rows.append([t('table_total'), fmt(total_ct), '100%'])
            update_table(tables_xml[3], rows)

        # Tabla 4: Canal Macro — eliminado del reporte

    doc.save(output_path)
    return output_path


# ── Helpers adicionales ───────────────────────────────────────────────────────

def _month_year(date_str: str) -> str:
    months = {
        '01': 'Enero',   '02': 'Febrero', '03': 'Marzo',
        '04': 'Abril',   '05': 'Mayo',    '06': 'Junio',
        '07': 'Julio',   '08': 'Agosto',  '09': 'Septiembre',
        '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre',
    }
    try:
        parts = date_str.replace('-', '/').split('/')
        if len(parts[0]) == 4:           # YYYY/MM/DD
            year, month = parts[0], parts[1]
        else:                             # DD/MM/YYYY
            year, month = parts[2], parts[1]
        return f"{months.get(month.zfill(2), month)} {year}"
    except Exception:
        return date_str


def _append_macro_channel_table(doc, macro_data: list, fmt_fn):
    """Agrega tabla de Canal Macro al final del documento."""
    WNS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    body = doc.element.body

    heading = doc.add_paragraph('Canal Macro (Traditional / Modern):')
    heading.style = doc.styles['Heading 4']
    doc.add_paragraph(
        'La columna Canal Macro indica si el cliente pertenece a un canal '
        'Tradicional (tiendas independientes, abarrotes, mercados) o '
        'Moderno (supermercados, tiendas de conveniencia, autoservicio).'
    )

    headers  = ['Canal Macro', 'POS[n]', 'POS [%]']
    total_mc = sum(r['count'] for r in macro_data)
    n_cols   = len(headers)
    col_w    = 8500 // n_cols
    tbl      = OxmlElement('w:tbl')

    tblPr = OxmlElement('w:tblPr')
    tblW  = OxmlElement('w:tblW')
    tblW.set(qn('w:w'), '8500'); tblW.set(qn('w:type'), 'dxa')
    tblPr.append(tblW)
    tblBorders = OxmlElement('w:tblBorders')
    for side in ['top','left','bottom','right','insideH','insideV']:
        b = OxmlElement(f'w:{side}')
        b.set(qn('w:val'), 'single'); b.set(qn('w:sz'), '4')
        b.set(qn('w:space'), '0'); b.set(qn('w:color'), 'CCCCCC')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    tbl.append(tblPr)

    tblGrid = OxmlElement('w:tblGrid')
    for _ in headers:
        gc = OxmlElement('w:gridCol'); gc.set(qn('w:w'), str(col_w))
        tblGrid.append(gc)
    tbl.append(tblGrid)

    def make_cell(text, bg='FFFFFF', bold=False):
        tc = OxmlElement('w:tc')
        tcPr = OxmlElement('w:tcPr')
        tcW  = OxmlElement('w:tcW')
        tcW.set(qn('w:w'), str(col_w)); tcW.set(qn('w:type'), 'dxa')
        tcPr.append(tcW)
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), bg); tcPr.append(shd)
        tc.append(tcPr)
        p = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        jc = OxmlElement('w:jc'); jc.set(qn('w:val'), 'center')
        pPr.append(jc); p.append(pPr)
        r = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        rf = OxmlElement('w:rFonts')
        rf.set(qn('w:ascii'), 'Albert Sans'); rf.set(qn('w:hAnsi'), 'Albert Sans')
        rPr.append(rf)
        sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '18'); rPr.append(sz)
        if bold:
            rPr.append(OxmlElement('w:b'))
            clr = OxmlElement('w:color'); clr.set(qn('w:val'), 'FFFFFF'); rPr.append(clr)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = str(text); r.append(t); p.append(r); tc.append(p)
        return tc

    tr_hdr = OxmlElement('w:tr')
    for h in headers: tr_hdr.append(make_cell(h, bg='434343', bold=True))
    tbl.append(tr_hdr)
    rows = [[r['pos_macro_channel'], fmt_fn(r['count']), f"{r['pct']:.2f}%"] for r in macro_data]
    rows.append(['Total', fmt_fn(total_mc), '100%'])
    for idx, row in enumerate(rows):
        tr = OxmlElement('w:tr')
        bg = 'F2F2F2' if idx % 2 == 0 else 'FFFFFF'
        for val in row: tr.append(make_cell(val, bg=bg))
        tbl.append(tr)
    body.append(tbl)
    doc.add_paragraph()
