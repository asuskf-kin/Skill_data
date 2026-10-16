#!/usr/bin/env python3
"""
compute_kpis.py — Compute all KPIs needed for the Customer Potential presentation.

Usage:
    python compute_kpis.py \
        --csv PATH_TO_FILE.csv \
        --run-type traditional|custom \
        [--custom-cats "Stills" "Sparkling" ...] \
        [--output kpis.json]

Traditional suffixes:
    TotalPortafolio, GlobalCat_CocaCola, GlobalCat_SparklingFlavors, ServingType_SingleServe

Custom suffixes:
    CustomCat_<name> for each name in --custom-cats
"""
import argparse
import json
import sys
import numpy as np
import pandas as pd
from functools import reduce


# ── Helpers ──────────────────────────────────────────────────────────────────

def auto_scale(val):
    """Return (divisor, suffix_str) best fitting for val."""
    if val >= 500_000:
        return 1_000_000, "M"
    return 1_000, "k"


def fmt_num(val, scale=None, scale_str=None, decimals=1):
    if scale is None:
        scale, scale_str = auto_scale(val)
    v = np.round(val / scale, decimals)
    return f"{v}", scale_str   # returns two parts so caller can split if needed


def fmt_pct(ratio, decimals=2):
    return f"{np.round(ratio * 100, decimals)}"


def comma_int(val):
    return f"{int(val):,}"


# ── Core computations ─────────────────────────────────────────────────────────

def compute_slide7(df):
    """Slide 7: TotalPortafolio full breakdown table + narrative."""
    suf = "TotalPortafolio"
    order = ["Very High", "High", "Moderate", "Low"]

    grp = (
        df.groupby(f"PotentialQualitative_{suf}")
        .agg(pos_id=("pos_id", "nunique"),
             ventas=(f"PotentialQuantitative_{suf}", "sum"),
             crecimiento=(f"PotentialQuantitativeFinal_{suf}", "sum"))
        .reset_index()
    )
    total_crecimiento = grp["crecimiento"].sum()
    total_pos = grp["pos_id"].sum()
    total_ventas = grp["ventas"].sum()

    rows = []
    for nivel in order:
        r = grp[grp[f"PotentialQualitative_{suf}"] == nivel]
        if r.empty:
            continue
        pos_n = int(r["pos_id"].values[0])
        ventas_v = r["ventas"].values[0]
        aporte = r["crecimiento"].values[0] / total_crecimiento
        scale, scale_str = auto_scale(ventas_v)
        v_num, v_suf = fmt_num(ventas_v, scale, scale_str)
        rows.append({
            "nivel": nivel,
            "pos_n": comma_int(pos_n),
            "prom_ventas": v_num + v_suf,          # e.g. "516k"
            "aporte_pct": fmt_pct(aporte),          # e.g. "55.44"
            # _orig fields: Nayar Mexico template values (for apply_kpis.py replacements)
            "pos_n_orig":    ["926", "2,775", "5,551", "9,253"][order.index(nivel)],
            "ventas_orig":   ["334.9k", "0.6M", "361.0k", "1.1M"][order.index(nivel)],
            "aporte_orig":   ["45.3", "33.7", "16.95", "4.04"][order.index(nivel)],
        })

    # Total row
    scale_t, scale_str_t = auto_scale(total_ventas)
    v_num_t, v_suf_t = fmt_num(total_ventas, scale_t, scale_str_t)
    rows.append({
        "nivel": "Total",
        "pos_n": comma_int(total_pos),
        "prom_ventas_num": v_num_t,                 # "2.7" (number part)
        "prom_ventas_suf": " " + v_suf_t,           # " M" (suffix, note the space)
        "aporte_pct": "100%",
        # _orig fields
        "pos_n_orig":       "18,505",
        "ventas_num_orig":  "2.4",
    })

    # Narrative values (for the bold text at the top of slide 7)
    vh = grp[grp[f"PotentialQualitative_{suf}"] == "Very High"]
    hi = grp[grp[f"PotentialQualitative_{suf}"] == "High"]

    vh_h_pos = (vh["pos_id"].sum() if not vh.empty else 0) + (hi["pos_id"].sum() if not hi.empty else 0)
    vh_h_vol = (vh["crecimiento"].sum() if not vh.empty else 0) + (hi["crecimiento"].sum() if not hi.empty else 0)
    pct_clientes = int(np.round(100 * vh_h_pos / total_pos))
    k_clientes = int(np.round(vh_h_pos / 1000))
    pct_vol_total = int(np.round(100 * vh_h_vol / total_crecimiento))

    vh_vol = vh["crecimiento"].sum() if not vh.empty else 0
    vh_pct = np.round(100 * vh_vol / total_crecimiento, 2)
    scale_vh, scale_str_vh = auto_scale(vh_vol)
    vh_vol_fmt_num, vh_vol_fmt_suf = fmt_num(vh_vol, scale_vh, scale_str_vh)

    scale_total, scale_str_total = auto_scale(total_crecimiento)
    total_vol_num, total_vol_suf = fmt_num(total_crecimiento, scale_total, scale_str_total)

    return {
        "rows": rows,
        # Narrative fragments (map to specific <a:t> elements in the XML)
        "nar_pct_clientes": str(pct_clientes),          # "20"
        "nar_k_clientes": str(k_clientes),               # "4"
        "nar_pct_vol_total": str(pct_vol_total),         # "79"
        "nar_vh_pct": str(vh_pct),                       # "45.3"
        "nar_vh_vol_num": vh_vol_fmt_num,                 # "95.4"
        "nar_vh_vol_suf": vh_vol_fmt_suf,                 # "k" or "M"
        "nar_total_vol": total_vol_num + total_vol_suf,   # "210.6k"
        # _orig fields: Nayar template values matched in apply_kpis.py
        "nar_k_clientes_orig":    "4",
        "nar_pct_vol_total_orig": "79",
        "nar_vh_pct_orig":        "45.3",
        "nar_vh_vol_num_orig":    "95.4",
        "nar_vh_vol_suf_orig":    "k",      # suffix in template text (e.g. "95.4k) del total...")
        "nar_total_vol_orig":     "210.6k",
    }


def compute_slide8(df, sufijos_display):
    """Slide 8: Multi-category summary table (Very High / High / Total).
    sufijos_display: list of (sufijo, display_name) tuples, max 3.
    """
    order = ["Very High", "High"]
    cats = []

    for sufijo, nombre in sufijos_display[:3]:
        grp = (
            df.groupby(f"PotentialQualitative_{sufijo}")
            .agg(pos_id=("pos_id", "nunique"),
                 ventas=(f"PotentialQuantitative_{sufijo}", "sum"),
                 crecimiento=(f"PotentialQuantitativeFinal_{sufijo}", "sum"))
            .reset_index()
        )
        total_crec = grp["crecimiento"].sum()
        total_pos_cat = grp[grp[f"PotentialQualitative_{sufijo}"].isin(order)]["pos_id"].sum()
        total_ventas_cat = grp[grp[f"PotentialQualitative_{sufijo}"].isin(order)]["ventas"].sum()
        total_crec_vh_h = grp[grp[f"PotentialQualitative_{sufijo}"].isin(order)]["crecimiento"].sum()

        rows_cat = []
        for nivel in order:
            r = grp[grp[f"PotentialQualitative_{sufijo}"] == nivel]
            if r.empty:
                continue
            pos_n = int(r["pos_id"].values[0])
            ventas_v = r["ventas"].values[0]
            aporte = r["crecimiento"].values[0] / total_crec
            scale, scale_str = auto_scale(ventas_v)
            v_num, v_suf = fmt_num(ventas_v, scale, scale_str)
            rows_cat.append({
                "nivel": nivel,
                "pos_n": comma_int(pos_n),
                "prom_ventas": v_num + " " + v_suf,
                "aporte_pct": fmt_pct(aporte),
            })

        # Total row
        scale_t, scale_str_t = auto_scale(total_ventas_cat)
        v_t_num, v_t_suf = fmt_num(total_ventas_cat, scale_t, scale_str_t)
        aporte_total = total_crec_vh_h / total_crec
        rows_cat.append({
            "nivel": "Total",
            "pos_n": comma_int(total_pos_cat),
            "prom_ventas_num": v_t_num,              # split for XML (e.g. "560")
            "prom_ventas_suf": v_t_suf,              # "k"
            "aporte_pct_num": fmt_pct(aporte_total), # "81.89"
            "aporte_pct_sign": "%",
        })

        # Top contributing category for narrative
        vh = grp[grp[f"PotentialQualitative_{sufijo}"] == "Very High"]
        vh_pct = np.round(100 * (vh["crecimiento"].sum() if not vh.empty else 0) / total_crec, 2)

        cats.append({
            "sufijo": sufijo,
            "nombre": nombre,
            "rows": rows_cat,
            "vh_pct": str(vh_pct),
        })

    # Find best and second-best for narrative
    cats_sorted = sorted(cats, key=lambda x: float(x["vh_pct"]), reverse=True)
    nar_best = cats_sorted[0]["nombre"] if cats_sorted else ""
    nar_best_pct = cats_sorted[0]["vh_pct"] if cats_sorted else ""
    nar_second = cats_sorted[1]["nombre"] if len(cats_sorted) > 1 else ""
    nar_second_pct = cats_sorted[1]["vh_pct"] if len(cats_sorted) > 1 else ""

    return {
        "categorias": cats,
        "nar_best_cat": nar_best,
        "nar_best_pct": nar_best_pct,
        "nar_best_pct_orig": "44.2",        # Nayar template value: CC VH% (for replacement)
        "nar_second_cat": nar_second,
        "nar_second_pct": nar_second_pct,
        "nar_second_pct_orig": "42.71",     # Nayar template value: SS VH% (for replacement)
        # Original Nayar cell values per category position (CC, SF, SS)
        "cats_orig": [
            # Col 1 — Coca Cola (Nayar)
            {"vh_pos": "901",   "vh_ventas": "198.3 k", "vh_pct": "44.2",
             "hi_pos": "2,703", "hi_ventas": "352.3 k", "hi_pct": "34.52",
             "tot_pos": "3,604","tot_ventas": "0.6 M",  "tot_pct_num": "78.73"},
            # Col 2 — Sparkling Flavors (Nayar)
            {"vh_pos": "911",   "vh_ventas": "23.3 k",  "vh_pct": "40.73",
             "hi_pos": "2,731", "hi_ventas": "34.5 k",  "hi_pct": "33.21",
             "tot_pos": "3,642","tot_ventas": "57.7 k", "tot_pct_num": "73.94"},
            # Col 3 — Single Serve (Nayar)
            {"vh_pos": "922",   "vh_ventas": "110.4 k", "vh_pct": "42.71",
             "hi_pos": "2,765", "hi_ventas": "180.7 k", "hi_pct": "33.42",
             "tot_pos": "3,687","tot_ventas": "291.0 k","tot_pct_num": "76.13"},
        ],
    }


def compute_brecha_top5(df, sufijos_list):
    """Brecha de Capitalización data: avg_ventas vs avg_potencial per top-5 subchannels.
    Used for generating bar charts in the Brecha slides.
    """
    results = {}
    for sufijo, nombre in sufijos_list:
        col_crecimiento = f"PotentialQuantitativeFinal_{sufijo}"
        col_ventas      = f"PotentialQuantitative_{sufijo}"
        if col_crecimiento not in df.columns:
            continue
        grp = (
            df.groupby("pos_subchannel")
            .agg(pos_n=("pos_id", "nunique"),
                 avg_ventas=(col_ventas, "mean"),
                 avg_potencial=(col_crecimiento, "mean"))
            .reset_index()
            .sort_values("avg_potencial", ascending=False)
            .head(5)
        )
        top5 = []
        for _, row in grp.iterrows():
            top5.append({
                "giro":              row["pos_subchannel"],
                "pos_n":             int(row["pos_n"]),
                "avg_ventas_raw":    float(row["avg_ventas"]),
                "avg_potencial_raw": float(row["avg_potencial"]),
            })
        results[sufijo] = {"nombre": nombre, "top5": top5}
    return results


def compute_top5(df, agrupador, sufijos_list, label):
    """Slides 9 & 10: Top 5 subchannel or city table.
    sufijos_list: list of (sufijo, display_name) tuples
    """
    col_suf_total = "TotalPortafolio"

    df[agrupador] = df[agrupador].str.strip()
    top5_vals = (
        df.groupby(agrupador)[f"PotentialQuantitativeFinal_{col_suf_total}"]
        .sum().reset_index()
        .sort_values(f"PotentialQuantitativeFinal_{col_suf_total}", ascending=False)
        .head(5)[agrupador].unique()
    )
    df["_group"] = np.where(df[agrupador].isin(top5_vals), df[agrupador].str.upper(), "OTROS")

    total_crec = {}
    for sufijo, _ in sufijos_list:
        total_crec[sufijo] = df[f"PotentialQuantitativeFinal_{sufijo}"].sum()

    rows = []
    order_groups = [v.upper() for v in top5_vals] + ["OTROS"]
    for grp_name in order_groups:
        mask = df["_group"] == grp_name
        entry = {"nombre": grp_name}
        entry["pos_n"] = comma_int(df[mask]["pos_id"].nunique())  # always include PDV count
        for i, (sufijo, _) in enumerate(sufijos_list):
            val = df[mask][f"PotentialQuantitativeFinal_{sufijo}"].sum()
            aporte = np.round(100 * val / total_crec[sufijo], 2)
            entry[f"aporte_{i}"] = f"{aporte}%"
        rows.append(entry)

    # Total row
    total_entry = {"nombre": "TOTAL"}
    total_entry["pos_n"] = comma_int(df["pos_id"].nunique())
    for i, (sufijo, _) in enumerate(sufijos_list):
        total_entry[f"aporte_{i}"] = "100%"
    rows.append(total_entry)

    return {
        "label": label,
        "agrupador": agrupador,
        "columnas": [d for _, d in sufijos_list],
        "rows": rows,
        "top2_nombres": [v.upper() for v in top5_vals[:2]],
    }


def compute_embudo(df, sufijo, nombre_display, scale=None, scale_str=None):
    """Slides 13-16: funnel (Potencial → Subcanal → Ciudad)."""
    df_c = df[df[f"PotentialQuantitative_{sufijo}"] > 0].copy()

    if scale is None:
        total_crec_val = df_c[f"PotentialQuantitativeFinal_{sufijo}"].sum()
        scale, scale_str = auto_scale(total_crec_val)

    total_clientes = df_c["pos_id"].nunique()
    total_crecimiento = df_c[f"PotentialQuantitativeFinal_{sufijo}"].sum()

    # N1 — Very High + High
    seg_n1 = ["Very High", "High"]
    mask_n1 = df_c[f"PotentialQualitative_{sufijo}"].isin(seg_n1)
    n1_pos = int(df_c[mask_n1]["pos_id"].count())
    n1_vol = df_c[mask_n1][f"PotentialQuantitativeFinal_{sufijo}"].sum()
    n1_pct_vol = int(np.round(100 * n1_vol / total_crecimiento))
    n1_pct_cli = int(np.round(100 * n1_pos / total_clientes))

    # N2 — Top 2 subcanales dentro de N1
    seg_n2 = (
        df_c[mask_n1]
        .groupby("pos_subchannel")
        .agg(pos_id=("pos_id", "count"), vol=(f"PotentialQuantitativeFinal_{sufijo}", "sum"))
        .sort_values("vol", ascending=False)
        .head(2).index.unique()
    )
    mask_n2 = df_c["pos_subchannel"].isin(seg_n2)
    n2_pos = int(df_c[mask_n1 & mask_n2]["pos_id"].count())
    n2_vol = df_c[mask_n1 & mask_n2][f"PotentialQuantitativeFinal_{sufijo}"].sum()
    n2_pct_vol = int(np.round(100 * n2_vol / total_crecimiento))
    n2_pct_comercios = int(np.round(100 * n2_pos / total_clientes))

    # N3 — Top 2 ciudades dentro de N1+N2
    seg_n3 = (
        df_c[mask_n1 & mask_n2]
        .groupby("pos_city")
        .agg(pos_id=("pos_id", "count"), vol=(f"PotentialQuantitativeFinal_{sufijo}", "sum"))
        .sort_values("vol", ascending=False)
        .head(2).index.unique()
    )
    mask_n3 = df_c["pos_city"].isin(seg_n3)
    n3_pos = int(df_c[mask_n1 & mask_n2 & mask_n3]["pos_id"].count())
    n3_vol = df_c[mask_n1 & mask_n2 & mask_n3][f"PotentialQuantitativeFinal_{sufijo}"].sum()
    n3_pct_vol = int(np.round(100 * n3_vol / total_crecimiento))
    n3_pct_pos = int(np.round(100 * n3_pos / total_clientes))

    def fv(val):
        num, suf = fmt_num(val, scale, scale_str)
        return f"{num}{suf}"

    total_clientes_fmt = f"{np.round(total_clientes / 1000, 1)}"
    total_vol_fmt = fv(total_crecimiento)

    return {
        "sufijo": sufijo,
        "nombre": nombre_display,
        # Header numbers (top-right area of slide)
        "total_clientes_num": total_clientes_fmt,        # "15.9"
        "total_vol_fmt": total_vol_fmt,                   # "255k"
        "n3_vol_num": fmt_num(n3_vol, scale, scale_str)[0],  # "116"
        "n3_vol_suf": fmt_num(n3_vol, scale, scale_str)[1],  # "K"
        "n3_pos_fmt": str(int(np.round(n3_pos / 100) * 100)),  # "1500"
        # Narrative % (the "X% del volumen estimado se concentra en el Y% de los clientes")
        "nar_pct_vol": str(n1_pct_vol),                   # "81" — Vol% in VH+H
        "nar_pct_cli": str(round(n1_pct_cli, 1)),          # "20.0" — Clientes% in VH+H
        # N1 level
        "n1_labels": "Very High y high",                   # fixed casing to match template
        "n1_detail": f"{fv(n1_vol)} UC/mes - {round(n1_pos / 1000, 1)}K clientes",
        "n1_vol_fmt": fv(n1_vol),
        "n1_pos_k": f"{round(n1_pos / 1000, 1)}K",
        # N2 level
        "n2_labels": " y ".join([s.upper() for s in seg_n2]),   # "ALMACENES y AUTOSERVICIOS"
        "n2_detail": f"{fv(n2_vol)} UC/mes - {round(n2_pos / 1000, 1)}K clientes",
        "n2_vol_fmt": fv(n2_vol),
        "n2_pos_k": f"{round(n2_pos / 1000, 1)}K",
        "n2_pct_vol": str(n2_pct_vol),                    # "68"
        "n2_pct_comercios": str(n2_pct_comercios),         # "15"
        # N3 level
        "n3_labels": " y ".join([s.title() for s in seg_n3]),   # "Montevideo y Canelones"
        "n3_detail": f"{fv(n3_vol)} UC/mes - {round(n3_pos / 1000, 1)}K clientes",
        "n3_vol_fmt": fv(n3_vol),
        "n3_pos_k": f"{np.round(n3_pos / 1000, 1)}K",
        "n3_pct_vol": str(n3_pct_vol),                    # "45"
        "n3_pct_pos": str(n3_pct_pos),                    # "9"
    }


def compute_slide11(df):
    """Slide 11: Map slide text — top 2 cities by TotalPortafolio growth."""
    suf = "TotalPortafolio"
    df["pos_city"] = df["pos_city"].str.strip()
    city_stats = (
        df.groupby("pos_city")
        .agg(pos_id=("pos_id", "nunique"),
             crecimiento=(f"PotentialQuantitativeFinal_{suf}", "sum"),
             ventas=(f"PotentialQuantitative_{suf}", "sum"))
        .reset_index()
        .sort_values("crecimiento", ascending=False)
        .head(2)
    )
    results = []
    for _, row in city_stats.iterrows():
        pct_growth = np.round(100 * row["crecimiento"] / row["ventas"]) if row["ventas"] > 0 else 0
        results.append({
            "ciudad": row["pos_city"].title(),
            "pos_n": comma_int(row["pos_id"]),
            "pct_crecimiento": str(int(pct_growth)),
        })
    return {
        "city1": results[0] if len(results) > 0 else {},
        "city2": results[1] if len(results) > 1 else {},
    }


# ── Main ──────────────────────────────────────────────────────────────────────

TRADITIONAL_SUFIJOS = [
    ("GlobalCat_CocaCola",        "Coca Cola"),
    ("GlobalCat_SparklingFlavors", "Sparkling Flavors"),
    ("ServingType_SingleServe",    "Single Serve"),
]

TRADITIONAL_EMBUDO_MAP = [
    ("TotalPortafolio",            "Total Portafolio"),
    ("GlobalCat_CocaCola",        "Colas"),
    ("GlobalCat_SparklingFlavors", "Flavors"),
    ("ServingType_SingleServe",    "Single Serve"),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to the segmentation CSV")
    parser.add_argument("--run-type", default="traditional", choices=["traditional", "custom"])
    parser.add_argument("--custom-cats", nargs="*", default=[],
                        help="Custom category names, e.g. Stills Sparkling")
    parser.add_argument("--output", default="kpis.json")
    args = parser.parse_args()

    print(f"[1/6] Loading {args.csv}...")
    df = pd.read_csv(args.csv)
    df = df[df["PotentialQuantitative_TotalPortafolio"] > 0].copy()
    print(f"      {len(df):,} rows after filter (PotentialQuantitative_TotalPortafolio > 0)")

    # Determine sufijos
    if args.run_type == "traditional":
        sufijos_cat = TRADITIONAL_SUFIJOS
        sufijos_embudo = TRADITIONAL_EMBUDO_MAP
    else:
        sufijos_cat = [(f"CustomCat_{c}", c) for c in args.custom_cats]
        sufijos_embudo = sufijos_cat   # Custom: only the custom categories, no TP

    # Traditional: slides 9/10 show TP + all cats
    # Custom: slides 9/10 show ONLY the custom cats (no TP) — TP removed in table surgery
    if args.run_type == "custom":
        sufijos_top5 = sufijos_cat
    else:
        sufijos_top5 = [("TotalPortafolio", "Total Portafolio")] + sufijos_cat

    print("[2/6] Computing slide 7 (TotalPortafolio)...")
    s7 = compute_slide7(df)

    print("[3/6] Computing slide 8 (multi-category)...")
    s8 = compute_slide8(df, sufijos_cat)

    print("[4/6] Computing slides 9 & 10 (Top 5 subchannel / city)...")
    s9 = compute_top5(df, "pos_subchannel", sufijos_top5, "Subchannel - Top 5")
    s10 = compute_top5(df, "pos_city", sufijos_top5, "City - Top 5")

    print("[5/6] Computing slide 11 (map city text)...")
    s11 = compute_slide11(df)

    print("[6/6] Computing embudos (slides 13+)...")
    embudos = [compute_embudo(df, suf, nombre) for suf, nombre in sufijos_embudo]

    print("[7/7] Computing brecha top5 (bar charts)...")
    # Traditional: brecha for TP + CC + SF + SS (matching TRADITIONAL_EMBUDO_MAP)
    # Custom:      brecha for custom cats only
    brecha = compute_brecha_top5(df, sufijos_embudo)

    output = {
        "run_type": args.run_type,
        "categorias_cat": [{"sufijo": s, "nombre": n} for s, n in sufijos_cat],
        "categorias_embudo": [{"sufijo": s, "nombre": n} for s, n in sufijos_embudo],
        "s7": s7,
        "s8": s8,
        "s9": s9,
        "s10": s10,
        "s11": s11,
        "embudos": embudos,
        "brecha": brecha,
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ KPIs written to {args.output}")
    print(f"  Embudos: {len(embudos)} categories")
    print(f"  Slide 7 rows: {len(s7['rows'])}")
    print(f"  Slide 8 categories: {len(s8['categorias'])}")
    print(f"  Top5 subchannel rows: {len(s9['rows'])}")
    print(f"  Top5 city rows: {len(s10['rows'])}")


if __name__ == "__main__":
    main()
