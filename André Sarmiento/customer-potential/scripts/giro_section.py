#!/usr/bin/env python3
"""
giro_section.py — Adds "Brecha de Capitalización" section to a Customer Potential PPTX.

Usage:
    python giro_section.py \
        --pptx input.pptx \
        --giro-kpis kpis_giro.json \
        --output output.pptx \
        [--lang es|en|pt]          (default: es)
        [--start-image-idx 40]     (default: 40 — avoids overwriting original media)

Per category adds:
  Slide A  — Section divider (once)
  Slide B  — Tabla Distribución del Potencial por Giro/Business Type
  Slide C  — Brecha de Capitalización / Capitalization Gap (bar chart)
  Slide D  — Mapa de Priorización Comercial / Commercial Prioritization Map (scatter)

Chart generation notes:
  - Uses subplots_adjust with fixed margins to match image29.png proportions
  - xlim set to max_value * 1.22 so bars fill ~82% of chart area
  - Images saved as image{start_image_idx+}.png to avoid overwriting originals
"""
import argparse
import io
import json
import os
import sys
import tempfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker
import numpy as np
from PIL import Image

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Import translations ───────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from translations import T, get as TR

# ── Brand colors ──────────────────────────────────────────────────────────────
C_DARK      = RGBColor(0x1C, 0x1C, 0x1C)
C_LIME      = RGBColor(0xCC, 0xFF, 0x00)
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
C_GRAY      = RGBColor(0x3D, 0x3D, 0x3D)
C_LGRAY     = RGBColor(0xF2, 0xF2, 0xF2)
C_MGRAY     = RGBColor(0xAA, 0xAA, 0xAA)
C_LIME_TINT = RGBColor(0xF0, 0xFF, 0xCC)
C_EXPL      = RGBColor(0x55, 0x55, 0x55)
M_LIME      = '#CCFF00'
M_DARK      = '#1C1C1C'
M_GRAY      = '#3D3D3D'

# ── Layout constants (10" × 5.62") ────────────────────────────────────────────
TITLE_H   = 0.82
EXPL_H    = 0.40
INSIGHT_H = 1.18
FOOTER_H  = 0.28
SIDE_PAD  = 0.20

# Chart image target size (must match image29.png dimensions)
CHART_W, CHART_H = 1426, 580


# ── Helpers ───────────────────────────────────────────────────────────────────

def W(prs): return prs.slide_width  / 914400
def H(prs): return prs.slide_height / 914400

def add_rect(slide, l, t, w, h, fill, line=None):
    s = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line: s.line.color.rgb = line
    else: s.line.fill.background()
    return s

def add_text(slide, l, t, w, h, text, size=10, bold=False,
             color=C_DARK, align=PP_ALIGN.LEFT, font='Albert Sans',
             wrap=True, italic=False):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r.font.color.rgb = color; r.font.name = font
    return tb

def add_image_from_path(slide, path, l, t, w, h):
    slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))

def add_footer(slide, prs):
    y = H(prs) - FOOTER_H + 0.02; ww = W(prs)
    add_text(slide, 0.2,        y, 2.5, FOOTER_H - 0.05, 'Kin Analytics®', size=7, color=C_MGRAY)
    add_text(slide, ww/2 - 1.0, y, 2.0, FOOTER_H - 0.05, 'Let knowledge in.',
             size=7, color=C_MGRAY, align=PP_ALIGN.CENTER)
    add_text(slide, ww - 2.3,   y, 2.1, FOOTER_H - 0.05, 'KinAnalytics.com',
             size=7, color=C_MGRAY, align=PP_ALIGN.RIGHT)

def blank_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

def trunc(text, n=32):
    return text[:n] + '…' if len(text) > n else text

def fmt_uc(val):
    if abs(val) >= 500_000: return f"{val/1_000_000:.1f}M"
    if abs(val) >= 1_000:   return f"{val/1_000:.1f}k"
    return f"{val:.0f}"

def add_insight_box(slide, prs, bullets):
    ww = W(prs); hh = H(prs)
    box_y = hh - FOOTER_H - INSIGHT_H - 0.04
    add_rect(slide, SIDE_PAD, box_y, ww - 2*SIDE_PAD, INSIGHT_H, C_LIME_TINT)
    row_h = INSIGHT_H / len(bullets)
    for i, bullet in enumerate(bullets):
        add_text(slide, SIDE_PAD + 0.12, box_y + 0.03 + i * row_h,
                 ww - 2*SIDE_PAD - 0.2, row_h - 0.04,
                 f'• {bullet}', size=8.5, color=C_DARK)

def add_expl_strip(slide, prs, text):
    ww = W(prs)
    add_rect(slide, 0, TITLE_H, ww, EXPL_H, C_LGRAY)
    add_text(slide, SIDE_PAD, TITLE_H + 0.04, ww - 2*SIDE_PAD, EXPL_H - 0.06,
             text, size=8.5, color=C_EXPL, italic=True)

def chart_area(prs):
    hh = H(prs)
    top = TITLE_H + EXPL_H + 0.05
    bot = hh - FOOTER_H - INSIGHT_H - 0.10
    return top, bot - top


# ── Chart generation ──────────────────────────────────────────────────────────

def make_brecha_chart(top5, out_path, lang):
    """Generate horizontal bar chart matching image29.png proportions."""
    giros    = [trunc(r['giro'], 28) for r in reversed(top5)]
    ventas   = [r['avg_ventas_raw']    for r in reversed(top5)]
    potencial= [r['avg_potencial_raw'] for r in reversed(top5)]
    max_v    = max(max(ventas), 1)

    dpi = 100
    fig, ax = plt.subplots(figsize=(CHART_W/dpi, CHART_H/dpi),
                           facecolor='white', dpi=dpi)
    ax.set_facecolor('white')
    # Fixed margins calibrated to match image29.png visual proportions
    fig.subplots_adjust(left=0.22, right=0.89, top=0.97, bottom=0.14)

    y = np.arange(len(giros))
    h = 0.28
    ax.barh(y + h/2, ventas,    height=h, color=M_GRAY, zorder=3)
    ax.barh(y - h/2, potencial, height=h, color=M_LIME, zorder=3)
    ax.set_xlim(0, max_v * 1.22)

    for val, yi in zip(ventas, y):
        if val > 0:
            ax.text(val + max_v*0.015, yi + h/2,
                    f'{val:,.0f}', va='center', fontsize=9, color='#333333')
    for val, yi in zip(potencial, y):
        if val > 0:
            ax.text(val + max_v*0.015, yi - h/2,
                    f'+{val:,.0f}', va='center', fontsize=9,
                    color='#445500', fontweight='bold')

    ax.set_yticks(y)
    ax.set_yticklabels(giros, fontsize=9.5)
    ax.set_xlabel(TR(lang, 'brecha_xlabel'), fontsize=9, color='#555555')
    ax.tick_params(axis='x', labelcolor='#888888', labelsize=8.5)
    ax.xaxis.grid(True, color='#EEEEEE', linewidth=0.8); ax.set_axisbelow(True)
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD'); ax.spines['bottom'].set_color('#DDDDDD')
    ax.legend(
        handles=[mpatches.Patch(color=M_GRAY, label=TR(lang, 'brecha_legend_actual')),
                 mpatches.Patch(color=M_LIME, label=TR(lang, 'brecha_legend_potencial'))],
        fontsize=8, loc='lower right', framealpha=0.9, edgecolor='#DDDDDD')

    fig.savefig(out_path, dpi=dpi, facecolor='white')
    plt.close()


# ── Insight generators ────────────────────────────────────────────────────────

def insights_b(top5, cat_nombre, lang):
    top2_aporte = sum(r['aporte_pct'] for r in top5[:2])
    best_vhh    = max(top5, key=lambda r: r['pct_vh_high'])
    low_vhh     = sorted([r for r in top5 if r['pct_vh_high'] < 25],
                          key=lambda r: r['pos_n'], reverse=True)
    i1 = TR(lang, 'dist_i1', pct=top2_aporte, cat=cat_nombre)
    i2 = TR(lang, 'dist_i2', giro=trunc(best_vhh['giro'], 26), vhh=best_vhh['pct_vh_high'])
    if low_vhh:
        u = low_vhh[0]
        i3 = TR(lang, 'dist_i3_low', giro=trunc(u['giro'],26),
                pdv=u['pos_n'], vhh=u['pct_vh_high'])
    else:
        vm = max(top5, key=lambda r: r['avg_ventas_raw'])
        i3 = TR(lang, 'dist_i3_high', giro=trunc(vm['giro'],26), venta=vm['avg_ventas'])
    return [i1, i2, i3]


def insights_c(top5, lang):
    best_gap  = max(top5, key=lambda r: r['avg_potencial_raw'])
    eff_list  = [(r, r['avg_potencial_raw'] / max(r['avg_ventas_raw'], 1)) for r in top5]
    best_eff  = max(eff_list, key=lambda x: x[1])
    total_gap = sum(r['avg_potencial_raw'] * r['pos_n'] for r in top5)
    i1 = TR(lang, 'brecha_i1', giro=trunc(best_gap['giro'],26), val=best_gap['avg_potencial_raw'])
    i2 = TR(lang, 'brecha_i2', giro=trunc(best_eff[0]['giro'],26), pct=best_eff[1]*100)
    i3 = TR(lang, 'brecha_i3', total=fmt_uc(total_gap))
    return [i1, i2, i3]


def insights_d(scatter_data, x_med, y_med, lang):
    alta  = [r for r in scatter_data if r['pct_vh_high'] >= x_med and r['potencial_total'] >= y_med]
    desar = [r for r in scatter_data if r['pct_vh_high'] <  x_med and r['potencial_total'] >= y_med]
    alta_names  = ', '.join(trunc(r['giro'],18) for r in
                            sorted(alta, key=lambda r: r['potencial_total'], reverse=True)[:3])
    desar_names = ', '.join(trunc(r['giro'],18) for r in
                            sorted(desar, key=lambda r: r['potencial_total'], reverse=True)[:2])
    i1 = TR(lang, 'scatter_i1', n=len(alta),
            names=alta_names if alta_names else '—')
    if desar:
        i2 = TR(lang, 'scatter_i2_desar', n=len(desar), names=desar_names)
    else:
        mant = [r for r in scatter_data if r['pct_vh_high'] >= x_med and r['potencial_total'] < y_med]
        i2 = TR(lang, 'scatter_i2_mant', n=len(mant))
    i3 = TR(lang, 'scatter_i3')
    return [i1, i2, i3]


# ── Slide A — Section divider ─────────────────────────────────────────────────

def add_divider(prs, lang):
    slide = blank_slide(prs)
    ww = W(prs); hh = H(prs)
    add_rect(slide, 0, 0, ww, hh, C_DARK)
    add_rect(slide, 0, 0, 0.06, hh, C_LIME)
    add_text(slide, 1.0, hh*0.12, 1.5, 1.1, '3',
             size=72, bold=True, color=C_LIME, font='Space Grotesk')
    add_text(slide, 1.0, hh*0.55, ww - 2.0, 1.0,
             TR(lang, 'giro_divider_title'),
             size=26, bold=True, color=C_WHITE, font='Space Grotesk')
    add_text(slide, 1.0, hh*0.82, ww - 2.0, 0.5,
             TR(lang, 'giro_divider_subtitle'),
             size=9, color=C_MGRAY, italic=True)
    add_footer(slide, prs)


# ── Slide B — Distribution table ─────────────────────────────────────────────

def add_distribution_slide(prs, cat_nombre, top5, lang):
    slide = blank_slide(prs)
    ww = W(prs); hh = H(prs)
    add_rect(slide, 0, 0, ww, hh, C_WHITE)
    add_rect(slide, 0, 0, ww, TITLE_H, C_DARK)
    add_text(slide, 0.3, 0.12, ww - 0.5, 0.58,
             TR(lang, 'dist_title', cat=cat_nombre),
             size=15, bold=True, color=C_LIME, font='Space Grotesk')
    add_expl_strip(slide, prs, TR(lang, 'dist_expl'))

    chart_top, chart_h_avail = chart_area(prs)
    COLS  = [TR(lang,'dist_col_giro'), TR(lang,'dist_col_pdv'), TR(lang,'dist_col_vhh'),
             TR(lang,'dist_col_aporte'), TR(lang,'dist_col_venta')]
    COL_X = [SIDE_PAD + 0.05, 4.50, 5.45, 6.70, 8.25]
    COL_W = [4.1, 0.9, 1.2, 1.4, 1.5]
    HDR_Y = chart_top

    add_rect(slide, SIDE_PAD, HDR_Y - 0.02, ww - 2*SIDE_PAD, 0.37, C_GRAY)
    for col, x, w in zip(COLS, COL_X, COL_W):
        add_text(slide, x, HDR_Y + 0.02, w, 0.33, col, size=8.5, bold=True, color=C_WHITE)

    row_h = min((chart_h_avail - 0.37 - 0.05) / len(top5), 0.52)
    for i, row in enumerate(top5):
        ry = HDR_Y + 0.37 + i * row_h
        add_rect(slide, SIDE_PAD, ry, ww - 2*SIDE_PAD, row_h - 0.03,
                 C_LGRAY if i % 2 == 0 else C_WHITE)
        bar_w = min(row['pct_vh_high'] / 100 * 1.1, 1.08)
        bar_color = C_LIME if row['pct_vh_high'] >= 40 else RGBColor(0x88, 0xDD, 0x66)
        add_rect(slide, COL_X[2] - 0.02, ry + 0.06, bar_w, row_h * 0.58, bar_color)
        vals  = [trunc(row['giro'],40), f"{row['pos_n']:,}",
                 f"{row['pct_vh_high']:.1f}%", f"{row['aporte_pct']:.2f}%", row['avg_ventas']]
        bolds = [True, False, True, True, False]
        for val, x, w, bld in zip(vals, COL_X, COL_W, bolds):
            add_text(slide, x, ry + 0.06, w, row_h - 0.1, val, size=9 if bld else 8.5, bold=bld)

    add_insight_box(slide, prs, insights_b(top5, cat_nombre, lang))
    add_footer(slide, prs)


# ── Slide C — Brecha ─────────────────────────────────────────────────────────

def add_brecha_slide(prs, cat_nombre, top5, lang, chart_path):
    slide = blank_slide(prs)
    ww = W(prs); hh = H(prs)
    add_rect(slide, 0, 0, ww, hh, C_WHITE)
    add_rect(slide, 0, 0, ww, TITLE_H, C_DARK)
    add_text(slide, 0.3, 0.12, ww - 0.5, 0.58,
             TR(lang, 'brecha_title', cat=cat_nombre),
             size=15, bold=True, color=C_LIME, font='Space Grotesk')
    add_expl_strip(slide, prs, TR(lang, 'brecha_expl'))

    chart_top, chart_h = chart_area(prs)
    add_image_from_path(slide, chart_path,
                        SIDE_PAD, chart_top, ww - 2*SIDE_PAD, chart_h)
    add_insight_box(slide, prs, insights_c(top5, lang))
    add_footer(slide, prs)


# ── Slide D — Scatter ─────────────────────────────────────────────────────────

def add_scatter_slide(prs, cat_nombre, scatter_data, top5_names, lang):
    slide = blank_slide(prs)
    ww = W(prs); hh = H(prs)
    add_rect(slide, 0, 0, ww, hh, C_WHITE)
    add_rect(slide, 0, 0, ww, TITLE_H, C_DARK)
    add_text(slide, 0.3, 0.12, ww - 0.5, 0.58,
             TR(lang, 'scatter_title', cat=cat_nombre),
             size=15, bold=True, color=C_LIME, font='Space Grotesk')
    add_expl_strip(slide, prs, TR(lang, 'scatter_expl'))

    chart_top, chart_h = chart_area(prs)
    data = [r for r in scatter_data if r['pos_n'] >= 10]
    if not data:
        add_text(slide, 2, 2.5, 6, 1, 'Datos insuficientes.', size=14, color=C_GRAY)
        add_footer(slide, prs); return

    xs = [r['pct_vh_high']    for r in data]
    ys = [r['potencial_total'] for r in data]
    ss = [max(r['pos_n']/3.5, 30) for r in data]
    x_med = np.median(xs); y_med = np.median(ys)
    xlim = (0, max(xs)*1.25); ylim = (0, max(ys)*1.22)

    dpi = 100
    fig_w = (ww - 2*SIDE_PAD) * 96 / dpi  # approximate figure size
    fig, ax = plt.subplots(figsize=(fig_w, chart_h * 1.35), facecolor='white')
    ax.set_facecolor('white')
    ax.set_xlim(xlim); ax.set_ylim(ylim)

    ax.fill_betweenx([y_med, ylim[1]], xlim[0], x_med,  color='#FFF3E0', alpha=0.55, zorder=0)
    ax.fill_betweenx([y_med, ylim[1]], x_med,  xlim[1], color='#E8F5E9', alpha=0.55, zorder=0)
    ax.fill_betweenx([ylim[0], y_med], xlim[0], x_med,  color='#F5F5F5', alpha=0.55, zorder=0)
    ax.fill_betweenx([ylim[0], y_med], x_med,  xlim[1], color='#E3F2FD', alpha=0.55, zorder=0)

    qf = 7
    ax.text(xlim[0]+(x_med-xlim[0])*0.05, ylim[1]*0.93, TR(lang,'scatter_q_desar'),  fontsize=qf, color='#BF360C', style='italic')
    ax.text(x_med+(xlim[1]-x_med)*0.05,   ylim[1]*0.93, TR(lang,'scatter_q_alta'),   fontsize=qf, color='#1B5E20', style='italic')
    ax.text(xlim[0]+(x_med-xlim[0])*0.05, ylim[1]*0.06, TR(lang,'scatter_q_monit'),  fontsize=qf, color='#424242', style='italic')
    ax.text(x_med+(xlim[1]-x_med)*0.05,   ylim[1]*0.06, TR(lang,'scatter_q_mant'),   fontsize=qf, color='#0D47A1', style='italic')

    ax.axvline(x_med, color='#BBBBBB', linewidth=1.0, linestyle='--', zorder=1)
    ax.axhline(y_med, color='#BBBBBB', linewidth=1.0, linestyle='--', zorder=1)

    colors_s = []
    for x, y in zip(xs, ys):
        if   x >= x_med and y >= y_med: colors_s.append('#4CAF50')
        elif x <  x_med and y >= y_med: colors_s.append('#FF9800')
        elif x >= x_med and y <  y_med: colors_s.append('#2196F3')
        else:                            colors_s.append('#9E9E9E')
    ax.scatter(xs, ys, s=ss, c=colors_s, alpha=0.82, edgecolors='white', linewidths=0.5, zorder=3)

    top5_keys = [n[:8].upper() for n in top5_names]
    for x, y, row in zip(xs, ys, data):
        if any(t in row['giro'].upper() for t in top5_keys):
            ax.annotate(trunc(row['giro'].split('/')[0].strip(), 20), (x, y),
                        textcoords='offset points', xytext=(5, 3), fontsize=6.5,
                        color='#222222',
                        bbox=dict(boxstyle='round,pad=0.15', fc='white', alpha=0.75, lw=0))

    ax.set_xlabel(TR(lang,'scatter_xlabel'), fontsize=8.5, color='#555555')
    ax.set_ylabel(TR(lang,'scatter_ylabel'), fontsize=8.5, color='#555555')
    ax.tick_params(labelcolor='#888888', labelsize=7.5)
    yf = T[lang].get('scatter_yformat', T['es']['scatter_yformat'])
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: yf(v)))
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD'); ax.spines['bottom'].set_color('#DDDDDD')
    legend_h = [mpatches.Patch(color='#4CAF50', label=TR(lang,'scatter_q_alta')),
                mpatches.Patch(color='#FF9800', label=TR(lang,'scatter_q_desar')),
                mpatches.Patch(color='#2196F3', label=TR(lang,'scatter_q_mant')),
                mpatches.Patch(color='#9E9E9E', label=TR(lang,'scatter_q_monit'))]
    ax.legend(handles=legend_h, fontsize=7, loc='upper left', framealpha=0.85, edgecolor='#DDDDDD')
    plt.tight_layout(pad=0.4)

    tmp = tempfile.mktemp(suffix='.png')
    plt.savefig(tmp, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    add_image_from_path(slide, tmp, SIDE_PAD, chart_top, ww - 2*SIDE_PAD, chart_h)
    os.unlink(tmp)

    add_insight_box(slide, prs, insights_d(data, x_med, y_med, lang))
    add_footer(slide, prs)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pptx',            required=True)
    parser.add_argument('--giro-kpis',       required=True, dest='giro_kpis')
    parser.add_argument('--output',          required=True)
    parser.add_argument('--lang',            default='es',
                        choices=['es','en','pt'], help='Output language')
    parser.add_argument('--start-image-idx', default=40, type=int, dest='start_img',
                        help='Starting index for chart image files (avoid overwriting originals)')
    args = parser.parse_args()

    prs = Presentation(args.pptx)
    with open(args.giro_kpis) as f:
        giro = json.load(f)

    lang = args.lang
    img_idx = args.start_img

    # Temp dir for chart images
    tmp_dir = tempfile.mkdtemp()

    print(f"Base: {len(prs.slides)} slides | Lang: {lang} | Adding giro section ({len(giro)} categories)…")
    add_divider(prs, lang)

    for sufijo, cat_data in giro.items():
        nombre     = cat_data['nombre']
        top5       = cat_data['top5']
        scatter    = cat_data['scatter']
        top5_names = [r['giro'] for r in top5]

        # Generate chart image to temp file
        chart_path = os.path.join(tmp_dir, f'chart_{img_idx}.png')
        make_brecha_chart(top5, chart_path, lang)
        img_idx += 1

        add_distribution_slide(prs, nombre, top5, lang)
        add_brecha_slide(prs, nombre, top5, lang, chart_path)
        add_scatter_slide(prs, nombre, scatter, top5_names, lang)
        print(f"  ✓ {nombre}: B + C + D")

    # Cleanup temp charts
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    prs.save(args.output)
    print(f"\n✓ {args.output}  ({len(prs.slides)} slides total)")


if __name__ == '__main__':
    main()
