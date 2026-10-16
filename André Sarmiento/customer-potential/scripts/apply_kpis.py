#!/usr/bin/env python3
"""
apply_kpis.py — Apply KPIs from kpis.json to an unpacked Nayar-based template.

Base template: Nayar Mexico (Traditional, Jun 2026)
Supports both Traditional (4 cats: TP, CC, SF, SS) and Custom (N custom cats) runs.

Usage:
    python apply_kpis.py \
        --kpis kpis.json \
        --unpacked /path/to/unpacked/ \
        --pais Nicaragua \
        --embotelladora Femsa \
        --mes Junio \
        --anio 2026 \
        --fuente-clientes "Embotelladora – Jun 2026" \
        --fuente-ventas "Sistema NSR – Jun 2026" \
        --email andre.sarmiento@kinanalytics.com

Nayar old values encoded in each function — replace1() warns if a pattern is missing.
After this script: run apply_custom_tables.py (Custom only), then clean.py + pack.py.
"""
import argparse
import json
import re
import sys
import tempfile
import os
from pathlib import Path


# ── I/O helpers ──────────────────────────────────────────────────────────────

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def t(val):
    return f"<a:t>{val}</a:t>"

def tp(val):
    return f'<a:t xml:space="preserve">{val} </a:t>'

def replace1(content, old, new, label=""):
    result = content.replace(old, new, 1)
    if result == content:
        print(f"  ⚠ NOT FOUND: {label or repr(old[:70])}")
    return result

def replace_all(content, old, new):
    return content.replace(old, new)


# ── Slide 1: Portada ─────────────────────────────────────────────────────────
# Nayar template values: "Femsa Nicaragua" (company+country), "Junio " (month), "2026" (year)

def apply_slide1(unpacked, meta):
    path = unpacked / "ppt/slides/slide1.xml"
    c = read(path)
    c = replace1(c, t("Femsa Nicaragua"), t(f'{meta["embotelladora"]} {meta["pais"]}'), "s1 company")
    c = replace1(c, t("Junio "),          t(f'{meta["mes"]} '),                          "s1 mes")
    if meta["anio"] != "2026":
        c = c.replace(t("2026"), t(meta["anio"]), 1)
    write(path, c)
    print(f"  ✓ Slide 1: {meta['embotelladora']} {meta['pais']}, {meta['mes']} {meta['anio']}")


# ── Slide 4: Resumen proceso (fuentes) ───────────────────────────────────────
# Nayar: "Nayar México" ×2, "(Embotelladora – Jun 2026)", "Sistema NSR – Jun 2026"

def apply_slide4(unpacked, meta):
    path = unpacked / "ppt/slides/slide4.xml"
    c = read(path)
    bot = f'{meta["embotelladora"]} {meta["pais"]}'
    c = replace1(c, t("Nayar México"), t(bot), "s4 clientes botname")
    c = replace1(c, t("Nayar México"), t(bot), "s4 ventas botname")
    c = replace1(c, t("(Embotelladora – Jun 2026)"),
                 t(f'({meta["fuente_clientes"]})'), "s4 fuente_clientes")
    c = replace1(c, t("Sistema NSR – Jun 2026"),
                 t(meta["fuente_ventas"]), "s4 fuente_ventas")
    write(path, c)
    print(f"  ✓ Slide 4: {bot} | clientes=({meta['fuente_clientes']}) | ventas={meta['fuente_ventas']}")


# ── Slide 7: Total Portafolio table + chart ───────────────────────────────────
# Nayar narrative: 20% → k=4 → 79% → VH=45.3% → 95.4k → 210.6k
# Nayar rows: VH 926/334.9k/45.3 | High 2,775/0.6M/33.7 | Moderate 5,551/361.0k/16.95
#             Low 9,253/1.1M/4.04 | Total 18,505/2.4 M/100%

def apply_slide7(unpacked, s7):
    path = unpacked / "ppt/slides/slide7.xml"
    c = read(path)
    rows = s7["rows"]

    # Narrative (order matters — replace in appearance order)
    c = replace1(c, t("20"),      t(s7["nar_pct_clientes"]),        "s7 nar pct_clientes")
    c = replace1(c, t(s7["nar_k_clientes_orig"]),
                    t(s7["nar_k_clientes"]),                          "s7 nar k_clientes")
    c = replace1(c, t(s7["nar_pct_vol_total_orig"]),
                    t(s7["nar_pct_vol_total"]),                       "s7 nar pct_vol_total")
    c = replace1(c, t(s7["nar_vh_pct_orig"]),
                    t(s7["nar_vh_pct"]),                              "s7 nar vh_pct")
    c = replace1(c, t(s7["nar_vh_vol_num_orig"]),
                    t(s7["nar_vh_vol_num"]),                          "s7 nar vh_vol_num")
    old_suf = f'{s7["nar_vh_vol_suf_orig"]}) del total del potencial de crecimiento del portafolio ('
    new_suf = f'{s7["nar_vh_vol_suf"]}) del total del potencial de crecimiento del portafolio ('
    c = replace1(c, t(old_suf), t(new_suf), "s7 nar vh_vol_suf")
    c = replace1(c, t(s7["nar_total_vol_orig"]),
                    t(s7["nar_total_vol"]),                           "s7 nar total_vol")

    # Table rows (VH, High, Moderate, Low)
    for i, nivel in enumerate(["VH", "High", "Moderate", "Low"]):
        r = rows[i]
        c = replace1(c, t(r["pos_n_orig"]),  t(r["pos_n"]),         f"s7 {nivel} pos_n")
        c = replace1(c, t(r["ventas_orig"]), t(r["prom_ventas"]),    f"s7 {nivel} ventas")
        c = replace1(c, t(r["aporte_orig"]), t(r["aporte_pct"]),     f"s7 {nivel} aporte")

    # Total row (ventas split: num + " M")
    r_tot = rows[4]
    c = replace1(c, t(r_tot["pos_n_orig"]),      t(r_tot["pos_n"]),           "s7 Total pos_n")
    c = replace1(c, t(r_tot["ventas_num_orig"]),  t(r_tot["prom_ventas_num"]), "s7 Total ventas_num")

    write(path, c)
    generate_slide7_chart(unpacked, s7)
    print(f"  ✓ Slide 7: {r_tot['pos_n']} POS | VH={rows[0]['aporte_pct']}% aporte")


# ── Slide 7 chart ─────────────────────────────────────────────────────────────

def generate_slide7_chart(unpacked, s7):
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
        from PIL import Image
    except ImportError:
        print("  ⚠ Chart: install matplotlib + Pillow")
        return

    rows    = [r for r in s7["rows"] if r["nivel"] != "Total"]
    labels  = [r["nivel"] for r in rows]
    pos_n   = [int(r["pos_n"].replace(",", "")) for r in rows]
    aporte  = [float(r["aporte_pct"]) for r in rows]

    fig, ax1 = plt.subplots(figsize=(12, 8.14), facecolor='#FFFFFF')
    ax1.set_facecolor('#FFFFFF')
    x = range(len(labels))
    bars = ax1.bar(x, pos_n, color='#3D3D3D', width=0.6, zorder=3)
    for bar, val in zip(bars, pos_n):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()*0.5,
                 f'{val:,}', ha='center', va='center', color='white', fontsize=14, fontweight='bold')
    ax2 = ax1.twinx()
    ax2.plot(x, aporte, color='#CCFF00', linewidth=2.5, zorder=4, marker='o', markersize=5)
    offsets = [(-0.28, 4.0), (0.08, 4.0), (0.08, 3.5), (0.08, 3.0)]
    for xi, (pct, (xo, yo)) in enumerate(zip(aporte, offsets)):
        ax2.text(xi+xo, pct+yo, f'{pct:.2f}%', color='#555555', fontsize=12)
    ax1.set_xticks(list(x)); ax1.set_xticklabels(labels, fontsize=13, color='#555555')
    ax1.set_ylim(0, max(pos_n)*1.18)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{int(v):,}'))
    ax1.tick_params(axis='y', labelcolor='#888888', labelsize=11)
    ax1.tick_params(axis='x', length=0)
    for sp in ['top','right']: ax1.spines[sp].set_visible(False)
    ax1.spines['left'].set_color('#DDDDDD'); ax1.spines['bottom'].set_color('#DDDDDD')
    ax1.yaxis.grid(True, color='#DDDDDD', linewidth=0.8, zorder=0); ax1.set_axisbelow(True)
    ax2.set_ylim(0, 70)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'{v:.2f}%'))
    ax2.tick_params(axis='y', labelcolor='#888888', labelsize=11)
    for sp in ['top','left','bottom']: ax2.spines[sp].set_visible(False)
    ax2.spines['right'].set_color('#DDDDDD')
    fig.suptitle('Portafolio Total', fontsize=16, color='#888888', y=0.97, ha='center')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name
    plt.savefig(tmp_path, dpi=150, bbox_inches='tight', facecolor='#FFFFFF'); plt.close()
    from PIL import Image as Img
    Img.open(tmp_path).resize((1200, 814), Img.LANCZOS).save(
        unpacked / "ppt/media/image26.png")
    os.unlink(tmp_path)
    print(f"  ✓ Slide 7 chart updated")


# ── Slide 8: Multi-category table ─────────────────────────────────────────────
# Nayar: 3 cats — CC(cols 1-3), SF(cols 4-6), SS(cols 7-9)
# Custom: 1+ custom cats replacing CC, SF, SS; surgery removes unused cols

def apply_slide8(unpacked, s8, run_type):
    path = unpacked / "ppt/slides/slide8.xml"
    c = read(path)
    cats_orig = s8["cats_orig"]
    cats      = s8["categorias"]

    for i, (orig, cat) in enumerate(zip(cats_orig, cats)):
        # Category header (row 0): Nayar has "Coca Cola", "Sparkling Flavors", "Single Serve"
        nayar_headers = ["Coca Cola", "Sparkling Flavors", "Single Serve"]
        if i < len(nayar_headers):
            c = replace1(c, t(nayar_headers[i]), t(cat["nombre"]), f"s8 cat{i} header")
        # VH row
        c = replace1(c, t(orig["vh_pos"]),          t(cat["rows"][0]["pos_n"]),       f"s8 cat{i} VH pos")
        c = replace1(c, t(orig["vh_ventas"]),        t(cat["rows"][0]["prom_ventas"]), f"s8 cat{i} VH ventas")
        c = replace1(c, t(f'{orig["vh_pct"]}%'),     t(f'{cat["rows"][0]["aporte_pct"]}%'), f"s8 cat{i} VH pct")
        # High row
        c = replace1(c, t(orig["hi_pos"]),           t(cat["rows"][1]["pos_n"]),       f"s8 cat{i} Hi pos")
        c = replace1(c, t(orig["hi_ventas"]),        t(cat["rows"][1]["prom_ventas"]), f"s8 cat{i} Hi ventas")
        c = replace1(c, t(f'{orig["hi_pct"]}%'),     t(f'{cat["rows"][1]["aporte_pct"]}%'), f"s8 cat{i} Hi pct")
        # Total row
        c = replace1(c, t(orig["tot_pos"]),          t(cat["rows"][2]["pos_n"]),       f"s8 cat{i} Tot pos")
        c = replace1(c, t(orig["tot_ventas"]),
                     t(f'{cat["rows"][2]["prom_ventas_num"]} {cat["rows"][2]["prom_ventas_suf"]}'),
                     f"s8 cat{i} Tot ventas")
        c = replace1(c, t(orig["tot_pct_num"]),      t(cat["rows"][2]["aporte_pct_num"]), f"s8 cat{i} Tot pct")

    # Narrative: "con X% en Very High, seguido por Single Serve con Y%."
    c = replace1(c, t(s8["nar_best_pct_orig"] + "%"),
                 t(s8["nar_best_pct"] + "%"), "s8 nar best_pct")

    if run_type == "custom" and len(cats) == 1:
        # Single custom cat — replace "seguido por Single Serve..." with "única categoría"
        c = c.replace(
            f', seguido por Single Serve con {s8["nar_second_pct_orig"]}%.',
            ', categoría única analizada en esta corrida.', 1)
    elif s8["nar_second_cat"]:
        c = c.replace(
            f', seguido por Single Serve con {s8["nar_second_pct_orig"]}%.',
            f', seguido por {s8["nar_second_cat"]} con {s8["nar_second_pct"]}%.', 1)

    write(path, c)
    print(f"  ✓ Slide 8: {len(cats)} cat(s) | best={s8['nar_best_cat']} {s8['nar_best_pct']}%")


# ── Slides 9 & 10: Top 5 subchannel / city ───────────────────────────────────
# Nayar subchannel names: ABARROTES, OTROS ABARROTES LOCALES O TRADICIONALES,
#   HOGAR CON VENTA, OTROS LICOR/CERVEZA/VINO/REFRESCO, FRUTAS Y VERDURAS, OTROS, TOTAL
# Traditional aporte: TP + CC + SF + SS cols
# Custom aporte: CustomCat only (in TP col position), —  in remaining cols

NAYAR_NAMES_9 = [
    "ABARROTES", "OTROS ABARROTES LOCALES O TRADICIONALES",
    "HOGAR CON VENTA", "OTROS LICOR/CERVEZA/VINO/REFRESCO",
    "FRUTAS Y VERDURAS", "OTROS", "TOTAL",
]
NAYAR_PDV_9 = ["3,357", "1,658", "4,397", "1,019", "459", "7,615", "18,505"]
NAYAR_AP_TP9 = ["44.24%","13.7%","12.77%","5.37%","3.82%","20.1%","100%"]
NAYAR_AP_CC9 = ["43.82%","13.73%","15.1%","5.74%","4.26%","17.35%","100%"]
NAYAR_AP_SF9 = ["42.35%","11.13%","13.43%","5.09%","2.77%","25.22%","100%"]
NAYAR_AP_SS9 = ["40.64%","11.53%","11.69%","6.44%","3.73%","25.97%","100%"]

NAYAR_NAMES_10 = [
    "TEPIC", "BAHIA DE BANDERAS", "PUERTO VALLARTA",
    "SANTIAGO IXCUINTLA", "COMPOSTELA", "OTROS", "TOTAL",
]
NAYAR_PDV_10 = ["5,742", "2,108", "2,949", "1,493", "1,125", "5,088", "18,505"]
NAYAR_AP_TP10 = ["29.32%","20.15%","19.47%","6.48%","6.21%","18.37%","100%"]
NAYAR_AP_CC10 = ["27.25%","18.96%","21.21%","7.02%","5.79%","19.77%","100%"]
NAYAR_AP_SF10 = ["26.63%","18.23%","19.28%","8.09%","7.09%","20.68%","100%"]
NAYAR_AP_SS10 = ["27.38%","18.1%","22.09%","7.19%","6.83%","18.42%","100%"]


def _apply_top5_slide(content, data, old_names, old_pdvs, old_tp, old_cc, old_sf, old_ss, run_type):
    new_rows  = data["rows"]
    top5_rows = [r for r in new_rows if r["nombre"] not in ("OTROS", "TOTAL")]
    new_names = [r["nombre"] for r in top5_rows]

    # Names — placeholder approach to avoid conflicts (same name in narrative + table)
    for i, old in enumerate(old_names):
        content = content.replace(t(old), t(f"§N{i}§"), 1)
    for i, new in enumerate([r["nombre"] for r in new_rows]):
        content = content.replace(t(f"§N{i}§"), t(new), 1)

    # PDVs
    for old, new in zip(old_pdvs, [r["pos_n"] for r in new_rows]):
        content = replace1(content, t(old), t(new), f"top5 pdv {old}")

    if run_type == "traditional":
        # 4 aporte columns per row: TP, CC, SF, SS
        new_ap = []
        for r in new_rows:
            new_ap += [r.get("aporte_0","—"), r.get("aporte_1","—"),
                       r.get("aporte_2","—"), r.get("aporte_3","—")]
        for old_list, start in [(old_tp, 0),(old_cc, 1),(old_sf, 2),(old_ss, 3)]:
            old_flat = old_list
            new_flat = [new_ap[i*4 + (start)] for i in range(len(new_rows))]
            for old, new in zip(old_flat, new_flat):
                content = replace1(content, t(old), t(new), f"top5 ap {old}")
    else:
        # Custom: aporte_0 → TP col position; remaining cols → "—"
        new_ap_0 = [r.get("aporte_0","—") for r in new_rows]
        for old, new in zip(old_tp, new_ap_0):
            content = replace1(content, t(old), t(new), f"top5 custom ap_0 {old}")
        for ap_list in [old_cc, old_sf, old_ss]:
            for old in ap_list:
                content = content.replace(t(old), t("—"), 1)

    # Fix remaining §Ni§ placeholders (narrative occurrences)
    top2 = data.get("top2_nombres", new_names[:2])
    content = content.replace(t("§N0§"), t(top2[0] if top2 else ""), 1)
    content = content.replace(t("§N1§"), t(top2[1] if len(top2)>1 else ""), 1)
    for i in range(2, len(old_names)):
        content = content.replace(t(f"§N{i}§"), t(""), 1)

    return content


def apply_top5(unpacked, s9, s10, run_type):
    path9 = unpacked / "ppt/slides/slide9.xml"
    c9 = _apply_top5_slide(read(path9), s9,
                           NAYAR_NAMES_9, NAYAR_PDV_9,
                           NAYAR_AP_TP9, NAYAR_AP_CC9, NAYAR_AP_SF9, NAYAR_AP_SS9,
                           run_type)
    # Fix Stills/custom narrative category reference
    if run_type == "custom":
        cats = [c["nombre"] for c in s9.get("columnas", [])]
        cat0 = cats[0] if cats else "Stills"
        c9 = c9.replace("<a:t>Sparkling</a:t>", f"<a:t>{cat0}</a:t>", 1)
        c9 = c9.replace("<a:t> Flavors y Coca Cola.</a:t>", "<a:t>.</a:t>", 1)
    write(path9, c9)

    path10 = unpacked / "ppt/slides/slide10.xml"
    c10 = _apply_top5_slide(read(path10), s10,
                            NAYAR_NAMES_10, NAYAR_PDV_10,
                            NAYAR_AP_TP10, NAYAR_AP_CC10, NAYAR_AP_SF10, NAYAR_AP_SS10,
                            run_type)
    if run_type == "custom":
        top2_10 = s10.get("top2_nombres", [])
        city1 = top2_10[0].title() if top2_10 else ""
        city2 = top2_10[1].title() if len(top2_10)>1 else ""
        c10 = c10.replace("principalmente en Single Serve y Coca Cola",
                          f"principalmente en Stills", 1)
    write(path10, c10)
    print(f"  ✓ Slide 9:  top={s9['rows'][0]['nombre']}, {s9['rows'][1]['nombre']}")
    print(f"  ✓ Slide 10: top={s10['rows'][0]['nombre']}, {s10['rows'][1]['nombre']}")
    if run_type == "custom":
        print(f"  ⚠ Slides 9/10: run apply_custom_tables.py to remove TP/CC/SF/SS cols")


# ── Slide 11: Mapa ────────────────────────────────────────────────────────────
# Nayar: Tepic / Bahia De Banderas

def apply_slide11(unpacked, s11):
    path = unpacked / "ppt/slides/slide11.xml"
    c = read(path)
    c1, c2 = s11["city1"], s11["city2"]

    c = replace1(c, "Departamento de Tepic y Bahia De Banderas:",
                 f'Departamento de {c1["ciudad"]} y {c2["ciudad"]}:', "s11 title")
    c = replace1(c, t("5,742"),            t(c1["pos_n"]),             "s11 c1 pos_n")
    c = replace1(c, t("Tepic "),           t(c1["ciudad"] + " "),      "s11 c1 name")
    c = replace1(c, t("9%"),               t(c1["pct_crecimiento"]+"%"),"s11 c1 pct")
    c = replace1(c, t("Bahia De Banderas se encuentran 2,108 POS"),
                 t(f'{c2["ciudad"]} se encuentran {c2["pos_n"]} POS'), "s11 c2 block")
    c = replace1(c, t("10%."),             t(c2["pct_crecimiento"]+"%."), "s11 c2 pct")
    # Map labels (standalone)
    c = replace1(c, t("Tepic"),            t(c1["ciudad"]),             "s11 map label 1")
    c = replace1(c, t("Bahia De Banderas"),t(c2["ciudad"]),             "s11 map label 2")

    write(path, c)
    print(f"  ✓ Slide 11: {c1['ciudad']} ({c1['pos_n']}, {c1['pct_crecimiento']}%) / "
          f"{c2['ciudad']} ({c2['pos_n']}, {c2['pct_crecimiento']}%)")
    print(f"  ⚠ Slide 11: map IMAGE must be updated manually in Kepler.gl")


# ── Slides 13-16: Embudos ─────────────────────────────────────────────────────
# All orig values from Nayar Mexico template

EMBUDO_ORIG = {
    "slide13.xml": {
        "titulo": "Total Portafolio",
        "nar_pct": "79",  "total_cli": "18.5",  "cat_label": "Total Portafolio",
        "total_vol": "210.6k",
        "n1_detail": "166.4k UC/mes - 3.7K clientes",
        "n2_labels": "ABARROTES y OTROS ABARROTES LOCALES O TRADICIONALES ",
        "n2_detail": "114.3k UC/mes - 2.4K clientes",
        "n2_pct_split": True,
        "n2_pct_tens_text": " concentra el 5",
        "n2_pct_units_digit": "4",
        "n2_com_units_digit": "3",
        "n3_pct_vol": "29",  "n3_pct_pos": "7",
        "n3_labels": "Tepic y Puerto Vallarta ",
        "n3_detail": "61.1k UC/mes - 1.3K clientes",
        "n3_vol_combined": True,
        "n3_vol_full": "61.1 k UC/mes",
        "n3_pos_combined": True,
        "n3_pos_full": "1300 Clientes segmentados",
    },
    "slide14.xml": {
        "titulo": "Colas",
        "nar_pct": "79",  "total_cli": "18.0",  "cat_label": "Colas",
        "total_vol": "132.0k",
        "n1_detail": "103.9k UC/mes - 3.6K clientes",
        "n2_labels": "ABARROTES y OTROS ABARROTES LOCALES O TRADICIONALES ",
        "n2_detail": "70.4k UC/mes - 2.3K clientes",
        "n2_pct_split": True,
        "n2_pct_tens_text": "anal concentra el 5",
        "n2_pct_units_digit": "3",
        "n2_com_units_digit": "3",
        "n3_pct_vol": "29",  "n3_pct_pos": "7",
        "n3_labels": "Tepic y Puerto Vallarta ",
        "n3_detail": "37.6k UC/mes - 1.3K clientes",
        "n3_vol_num": "37.6",  "n3_vol_suf_text": " k UC/mes ",
        "n3_pos": "1500 ",  "n3_pos_preserve": True,
    },
    "slide15.xml": {
        "titulo": "Flavors",
        "nar_pct": "74",  "total_cli": "18.2",  "cat_label": "Flavors",
        "total_vol": "15.2k",
        "n1_detail": "11.3k UC/mes - 3.6K clientes",
        "n2_labels": "ABARROTES y OTROS ABARROTES LOCALES O TRADICIONALES ",
        "n2_detail": "7.4k UC/mes - 2.2K clientes",
        "n2_pct_split": False,
        "n2_pct_combined_text": "Este subcanal concentra el 49% del volumen y el 1",
        "n2_com_units_digit": "2",
        "n3_pct_vol": "23",  "n3_pct_pos": "6",
        "n3_labels": "Tepic y Puerto Vallarta ",
        "n3_detail": "3.5k UC/mes - 1.1K clientes",
        "n3_vol_num": "3.5",  "n3_vol_suf_text": " k UC/mes",
        "n3_pos": "1100",
    },
    "slide16.xml": {
        "titulo": "Single Serve",
        "nar_pct": "76",  "total_cli": "18.4",  "cat_label": "Single Serve",
        "total_vol": "75.2k",
        "n1_detail": "57.3k UC/mes - 3.7K clientes",
        "n2_labels": "ABARROTES y OTROS ABARROTES LOCALES O TRADICIONALES ",
        "n2_detail": "35.8k UC/mes - 2.2K clientes",
        "n2_pct_split": False,
        "n2_pct_combined_text": " concentra el 48% del volumen y el 1",
        "n2_com_units_digit": "2",
        "n3_pct_vol": "24",
        "n3_pct_pos_embedded": True,
        "n3_pct_pos_text": "% del volumen y 6% de los POS",
        "n3_labels": "Tepic y Puerto Vallarta ",
        "n3_detail": "18.1k UC/mes - 1.2K clientes",
        "n3_vol_num": "18.1",  "n3_vol_suf_text": " k UC/mes",
        "n3_pos": "1200",
    },
}


def apply_embudos(unpacked, embudos, run_type):
    # Map: embudo index → slide file (always starts at slide13.xml)
    slide_files = ["slide13.xml", "slide14.xml", "slide15.xml", "slide16.xml"]
    for slide_file, emb in zip(slide_files, embudos):
        if slide_file not in EMBUDO_ORIG:
            print(f"  ⚠ {slide_file}: no EMBUDO_ORIG defined, skip")
            continue
        _apply_embudo(unpacked, slide_file, emb)


def _apply_embudo(unpacked, slide_file, emb):
    orig = EMBUDO_ORIG[slide_file]
    path = unpacked / f"ppt/slides/{slide_file}"
    c = read(path)
    n = emb["nombre"]

    c = replace1(c, t(f'Ultrasegmentación {orig["titulo"]} '),
                 t(f'Ultrasegmentación {n} '), f"{slide_file} titulo")
    c = replace1(c, t(orig["nar_pct"]),    t(emb["nar_pct_vol"]),         f"{slide_file} nar_pct")
    c = replace1(c, t(orig["total_cli"]),  t(emb["total_clientes_num"]),   f"{slide_file} total_cli")
    c = replace1(c, t(f' K Clientes Actuales {orig["cat_label"]}'),
                 t(f' K Clientes Actuales {n}'),                           f"{slide_file} cat_label")
    c = replace1(c, t(orig["total_vol"]),  t(emb["total_vol_fmt"]),        f"{slide_file} total_vol")
    c = replace1(c, t(orig["n1_detail"]), t(emb["n1_detail"]),             f"{slide_file} n1_detail")
    c = replace_all(c, t(orig["n2_labels"]), t(emb["n2_labels"] + " "))
    c = replace1(c, t(orig["n2_detail"]), t(emb["n2_detail"]),             f"{slide_file} n2_detail")
    c = _fix_embudo_n2_pct(c, orig, emb, slide_file)
    c = replace_all(c, t(orig["n3_labels"]), t(emb["n3_labels"] + " "))
    c = replace1(c, t(orig["n3_detail"]), t(emb["n3_detail"]),             f"{slide_file} n3_detail")
    c = replace1(c, t(orig["n3_pct_vol"]), t(emb["n3_pct_vol"]),          f"{slide_file} n3_pct_vol")

    # n3_pct_pos
    if orig.get("n3_pct_pos_embedded"):
        old_txt = orig["n3_pct_pos_text"]
        new_txt = f'% del volumen y {emb["n3_pct_pos"]}% de los POS'
        c = replace1(c, t(old_txt), t(new_txt), f"{slide_file} n3_pct_pos embedded")
    else:
        c = replace1(c, t(orig["n3_pct_pos"]), t(emb["n3_pct_pos"]),     f"{slide_file} n3_pct_pos")

    # Narrative clientes%
    c = re.sub(
        r'% del volumen estimado se concentra en el [\d.]+% de los clientes',
        f'% del volumen estimado se concentra en el {emb["nar_pct_cli"]}% de los clientes',
        c, count=1)

    # n3_vol — either combined or split
    if orig.get("n3_vol_combined"):
        new_vol = f'{emb["n3_vol_num"]} {emb["n3_vol_suf"]} UC/mes'
        c = replace1(c, t(orig["n3_vol_full"]), t(new_vol),               f"{slide_file} n3_vol combined")
    else:
        c = replace1(c, t(orig["n3_vol_num"]), t(emb["n3_vol_num"]),     f"{slide_file} n3_vol_num")
        c = replace1(c, t(orig["n3_vol_suf_text"]),
                     t(f' {emb["n3_vol_suf"]} UC/mes'),                   f"{slide_file} n3_vol_suf")

    # n3_pos — either combined, preserve (trailing space), or plain
    if orig.get("n3_pos_combined"):
        new_pos = f'{emb["n3_pos_fmt"]} Clientes segmentados'
        c = replace1(c, t(orig["n3_pos_full"]), t(new_pos),               f"{slide_file} n3_pos combined")
    elif orig.get("n3_pos_preserve"):
        c = replace1(c, tp(orig["n3_pos"].strip()), tp(emb["n3_pos_fmt"]),f"{slide_file} n3_pos preserve")
    else:
        c = replace1(c, t(orig["n3_pos"]), t(emb["n3_pos_fmt"]),         f"{slide_file} n3_pos")

    write(path, c)
    print(f"  ✓ {slide_file}: {n} | VH+H={emb['n1_vol_fmt']} | N2={emb['n2_pct_vol']}% | N3={emb['n3_vol_fmt']}")


def _fix_embudo_n2_pct(c, orig, emb, slide_file):
    n2pv = emb["n2_pct_vol"]       # "54"
    n2pc = emb["n2_pct_comercios"]  # "13"

    if orig["n2_pct_split"]:
        tens_text = orig["n2_pct_tens_text"]
        new_text  = tens_text[:-1] + n2pv[0]
        c = replace1(c, t(tens_text), t(new_text), f"{slide_file} n2pv tens")
        c = replace1(c, t(orig["n2_pct_units_digit"]),
                     t(n2pv[1] if len(n2pv) > 1 else ""), f"{slide_file} n2pv units")
    else:
        old_comb = orig["n2_pct_combined_text"]
        new_comb = re.sub(r'concentra el \d+%', f'concentra el {n2pv}%', old_comb)
        new_comb = re.sub(r'y el \d+$', f'y el {n2pc[0]}', new_comb)
        c = replace1(c, t(old_comb), t(new_comb), f"{slide_file} n2pv combined")

    c = replace1(c, t(orig["n2_com_units_digit"]),
                 t(n2pc[1] if len(n2pc) > 1 else n2pc[0]), f"{slide_file} n2pc units")
    return c


# ── Slides 18-21: Brecha de Capitalización ────────────────────────────────────
# Nayar: slide18=TP, 19=CC, 20=SF, 21=SS (all with image29/30/31/32 charts)
# Traditional: update all 4 | Custom: update only slide18 (for the 1st custom cat)

BRECHA_ORIG = {
    "slide18.xml": {
        "titulo":  "Total Portafolio",
        "insight": ("La mayor brecha de crecimiento la encontramos en ABARROTES que tiene "
                    "un crecimiento de +28 potencial adicional mensual. ABARROTES muestra "
                    "la mejor relación potencial/base (9%), alta eficiencia de conversión."),
        "chart_image": "image29.png",
    },
    "slide19.xml": {
        "titulo":  "Coca Cola",
        "insight": ("La mayor brecha de crecimiento la encontramos en ABARROTES que tiene "
                    "un crecimiento de +17 potencial adicional mensual. HOGAR CON VENTA "
                    "muestra la mejor relación potencial/base (10%), alta eficiencia de conversión."),
        "chart_image": "image30.png",  # Nayar CC brecha chart
    },
    "slide20.xml": {
        "titulo":  "Sparkling Flavors",
        "insight": ("La mayor brecha de crecimiento la encontramos en ABARROTES que tiene "
                    "un crecimiento de +2 potencial adicional mensual. OTROS LICOR/CERVEZA/ "
                    "muestra la mejor relación potencial/base (11%), alta eficiencia de conversión."),
        "chart_image": "image31.png",
    },
    "slide21.xml": {
        "titulo":  "Single Serve",
        "insight": ("La mayor brecha de crecimiento la encontramos en ABARROTES que tiene "
                    "un crecimiento de +9 potencial adicional mensual. HOGAR CON VENTA "
                    "muestra la mejor relación potencial/base (10%), alta eficiencia de conversión."),
        "chart_image": "image32.png",
    },
}


def _brecha_insight(top5, cat_name):
    def trunc(s, n=22): return s[:n]+"…" if len(s)>n else s
    best = max(top5, key=lambda r: r["avg_potencial_raw"])
    eff  = max(top5, key=lambda r: r["avg_potencial_raw"]/max(r["avg_ventas_raw"],1))
    eff_pct = round(100*eff["avg_potencial_raw"]/max(eff["avg_ventas_raw"],1))
    return (f'La mayor brecha de crecimiento la encontramos en {trunc(best["giro"])} '
            f'que tiene un crecimiento de +{best["avg_potencial_raw"]:.0f} potencial adicional mensual. '
            f'{trunc(eff["giro"])} muestra la mejor relación potencial/base ({eff_pct}%), '
            f'alta eficiencia de conversión.')


def _generate_brecha_chart(top5, out_path):
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        import numpy as np
    except ImportError:
        print(f"  ⚠ Chart: install matplotlib"); return

    def trunc(s, n=28): return s[:n]+"…" if len(s)>n else s
    giros    = [trunc(r["giro"]) for r in reversed(top5)]
    ventas   = [r["avg_ventas_raw"]    for r in reversed(top5)]
    potencial= [r["avg_potencial_raw"] for r in reversed(top5)]
    max_v    = max(max(ventas), 1)

    dpi = 100
    fig, ax = plt.subplots(figsize=(1426/dpi, 580/dpi), facecolor='white', dpi=dpi)
    ax.set_facecolor('white')
    fig.subplots_adjust(left=0.22, right=0.89, top=0.97, bottom=0.14)
    y = np.arange(len(giros)); h = 0.28
    ax.barh(y+h/2, ventas,    height=h, color='#3D3D3D', zorder=3)
    ax.barh(y-h/2, potencial, height=h, color='#CCFF00', zorder=3)
    ax.set_xlim(0, max_v*1.22)
    for val,yi in zip(ventas,y):
        if val>0: ax.text(val+max_v*0.015, yi+h/2, f'{val:,.0f}', va='center', fontsize=9, color='#333333')
    for val,yi in zip(potencial,y):
        if val>0: ax.text(val+max_v*0.015, yi-h/2, f'+{val:,.0f}', va='center', fontsize=9, color='#445500', fontweight='bold')
    ax.set_yticks(y); ax.set_yticklabels(giros, fontsize=9.5)
    ax.set_xlabel('UC/mes por PDV (promedio)', fontsize=9, color='#555555')
    ax.tick_params(axis='x', labelcolor='#888888', labelsize=8.5)
    ax.xaxis.grid(True, color='#EEEEEE', linewidth=0.8); ax.set_axisbelow(True)
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD'); ax.spines['bottom'].set_color('#DDDDDD')
    ax.legend(handles=[
        mpatches.Patch(color='#3D3D3D', label='Venta Actual Prom. UC'),
        mpatches.Patch(color='#CCFF00', label='Potencial Adicional Prom. UC')],
        fontsize=8, loc='lower right', framealpha=0.9, edgecolor='#DDDDDD')
    fig.savefig(out_path, dpi=dpi, facecolor='white')
    plt.close()


def apply_brecha(unpacked, brecha_kpis, run_type):
    """Update brecha slides 18-21 and regenerate bar charts."""
    # Map: embudo sufijo → slide file
    if run_type == "traditional":
        slide_map = [
            ("TotalPortafolio",            "slide18.xml"),
            ("GlobalCat_CocaCola",         "slide19.xml"),
            ("GlobalCat_SparklingFlavors", "slide20.xml"),
            ("ServingType_SingleServe",    "slide21.xml"),
        ]
    else:
        # Custom: only the custom cats, all mapped to slide18 onwards
        slide_files_custom = ["slide18.xml", "slide19.xml", "slide20.xml", "slide21.xml"]
        slide_map = list(zip(list(brecha_kpis.keys()), slide_files_custom))

    for sufijo, slide_file in slide_map:
        if sufijo not in brecha_kpis:
            continue
        cat_data = brecha_kpis[sufijo]
        cat_name = cat_data["nombre"]
        top5     = cat_data["top5"]
        orig     = BRECHA_ORIG.get(slide_file, BRECHA_ORIG["slide18.xml"])

        path = unpacked / f"ppt/slides/{slide_file}"
        if not path.exists():
            print(f"  ⚠ {slide_file} not found, skip")
            continue
        c = read(path)

        # Title
        c = replace1(c, t(f'Brecha de Capitalización – {orig["titulo"]}'),
                     t(f'Brecha de Capitalización – {cat_name}'),
                     f"{slide_file} brecha titulo")

        # Insight text
        new_insight = _brecha_insight(top5, cat_name)
        c = replace1(c, t(orig["insight"]), t(new_insight), f"{slide_file} brecha insight")

        write(path, c)

        # Regenerate chart
        chart_path = unpacked / f"ppt/media/{orig['chart_image']}"
        _generate_brecha_chart(top5, str(chart_path))
        print(f"  ✓ {slide_file}: Brecha {cat_name} — chart updated")


# ── Slide 23: Contactos (add presenter email) ─────────────────────────────────
# Nayar contacts are on slide23.xml

def apply_contactos(unpacked, email):
    path = unpacked / "ppt/slides/slide23.xml"
    c = read(path)

    # Anchor: last <a:t> in nicolas paragraph ends with 'm' → append new email paragraph
    anchor = (
        '              <a:t>m</a:t>\n'
        '            </a:r>\n'
        '            <a:endParaRPr sz="1400" b="0" i="0" u="none" strike="noStrike" cap="none">\n'
        '              <a:solidFill>\n'
        '                <a:srgbClr val="222326"/>\n'
        '              </a:solidFill>\n'
        '              <a:latin typeface="Albert Sans"/>\n'
        '              <a:ea typeface="Albert Sans"/>\n'
        '              <a:cs typeface="Albert Sans"/>\n'
        '              <a:sym typeface="Albert Sans"/>\n'
        '            </a:endParaRPr>\n'
        '          </a:p>'
    )
    new_para = f"""
          <a:p>
            <a:pPr marL="0" marR="0" lvl="0" indent="0" algn="l" rtl="0">
              <a:lnSpc><a:spcPct val="80000"/></a:lnSpc>
              <a:spcBef><a:spcPts val="0"/></a:spcBef>
              <a:spcAft><a:spcPts val="0"/></a:spcAft>
              <a:buClr><a:schemeClr val="dk1"/></a:buClr>
              <a:buSzPts val="1400"/><a:buFont typeface="Arial"/><a:buNone/>
            </a:pPr>
            <a:r>
              <a:rPr lang="es-ES" sz="1400" b="0" i="0" u="sng" strike="noStrike" cap="none">
                <a:solidFill><a:schemeClr val="hlink"/></a:solidFill>
                <a:latin typeface="Albert Sans"/>
              </a:rPr>
              <a:t>{email}</a:t>
            </a:r>
          </a:p>"""

    if anchor in c:
        c = c.replace(anchor, anchor + new_para, 1)
        print(f"  ✓ Slide 23: added {email}")
    else:
        print(f"  ⚠ Slide 23: anchor not found — add email manually: {email}")
    write(path, c)


# ── Remove unused slides (Custom mode) ────────────────────────────────────────

def remove_slides(unpacked, slide_files):
    """Remove slides from presentation.xml sldIdLst (clean.py will delete XML files)."""
    pres_path = unpacked / "ppt/presentation.xml"
    rels_path = unpacked / "ppt/_rels/presentation.xml.rels"
    pres = read(pres_path)
    rels = read(rels_path)

    for fname in slide_files:
        rid_m = re.search(rf'Id="(rId\d+)"[^>]*Target="slides/{fname}"', rels)
        if rid_m:
            rid = rid_m.group(1)
            pres = re.sub(rf'\s*<p:sldId[^>]*r:id="{rid}"[^/]*/>', '', pres)
            print(f"  ✓ Removed {fname} from sldIdLst")
        else:
            print(f"  ⚠ {fname} not found in rels")

    write(pres_path, pres)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Apply KPIs to unpacked Nayar-based template")
    parser.add_argument("--kpis",            required=True)
    parser.add_argument("--unpacked",        required=True)
    parser.add_argument("--pais",            required=True)
    parser.add_argument("--embotelladora",   required=True)
    parser.add_argument("--mes",             required=True)
    parser.add_argument("--anio",            required=True)
    parser.add_argument("--fuente-clientes", required=True, dest="fuente_clientes")
    parser.add_argument("--fuente-ventas",   required=True, dest="fuente_ventas")
    parser.add_argument("--email",           required=True)
    args = parser.parse_args()

    unpacked = Path(args.unpacked)
    if not (unpacked / "ppt/slides/slide1.xml").exists():
        print(f"ERROR: {unpacked} is not an unpacked PPTX directory"); sys.exit(1)

    with open(args.kpis, encoding="utf-8") as f:
        kpis = json.load(f)

    run_type = kpis.get("run_type", "traditional")
    meta = {
        "pais":           args.pais,
        "embotelladora":  args.embotelladora,
        "mes":            args.mes,
        "anio":           args.anio,
        "fuente_clientes":args.fuente_clientes,
        "fuente_ventas":  args.fuente_ventas,
    }

    print(f"\n── Applying KPIs [{run_type.upper()}] ──────────────────────────────────")

    print("\n[Slide 1] Cover")
    apply_slide1(unpacked, meta)

    print("\n[Slide 4] Fuentes de datos")
    apply_slide4(unpacked, meta)

    print("\n[Slide 7] TotalPortafolio")
    apply_slide7(unpacked, kpis["s7"])

    print("\n[Slide 8] Multi-categoría")
    apply_slide8(unpacked, kpis["s8"], run_type)

    print("\n[Slides 9-10] Top 5")
    apply_top5(unpacked, kpis["s9"], kpis["s10"], run_type)

    print("\n[Slide 11] Mapa")
    apply_slide11(unpacked, kpis["s11"])

    print("\n[Slides 13+] Embudos")
    apply_embudos(unpacked, kpis["embudos"], run_type)

    print("\n[Slides 18+] Brecha de Capitalización")
    apply_brecha(unpacked, kpis.get("brecha", {}), run_type)

    print("\n[Slide 23] Contactos")
    apply_contactos(unpacked, args.email)

    # Custom mode: remove unused embudos (14-16) and brecha (19-21)
    if run_type == "custom":
        n_cats  = len(kpis["categorias_embudo"])
        # Embudos: slide13=cat0, slide14=cat1, slide15=cat2, slide16=cat3
        unused_embudos  = [f"slide{13+i}.xml" for i in range(n_cats, 4)]
        # Brecha: slide18=cat0, slide19=cat1, slide20=cat2, slide21=cat3
        unused_brecha   = [f"slide{18+i}.xml" for i in range(n_cats, 4)]
        all_unused = unused_embudos + unused_brecha
        if all_unused:
            print(f"\n[Custom] Removing {len(all_unused)} unused slides: {all_unused}")
            remove_slides(unpacked, all_unused)
        print("\n[Custom] Run apply_custom_tables.py next (slides 8/9/10 column surgery)")

    print("\n✓ Done. Next: [apply_custom_tables.py if custom] → clean.py → pack.py")


if __name__ == "__main__":
    main()
