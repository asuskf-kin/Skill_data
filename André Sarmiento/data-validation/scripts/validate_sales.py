"""
validate_sales.py
Validaciones sobre la base de ventas.
"""

import pandas as pd


def validate_sales(df_ventas: pd.DataFrame,
                   df_clientes: pd.DataFrame = None,
                   df_productos: pd.DataFrame = None) -> dict:
    """
    Valida la base de ventas.
    Opcionalmente cruza con clientes y productos si se proporcionan.
    """
    results = {}
    insights = []
    df = df_ventas.copy()

    results["total_rows"] = len(df)
    results["unique_pos"] = df["pos_id"].nunique()
    results["unique_products"] = df["product_id"].nunique() if "product_id" in df.columns else None

    # Vacíos
    null_checks = {}
    for col in ["pos_id", "product_id", "unit_cases"]:
        if col in df.columns:
            n = df[col].isna().sum()
            null_checks[col] = int(n)
            if n > 0:
                insights.append(f"⚠️ `{col}` tiene {n:,} valores vacíos en ventas.")
    results["nulls"] = null_checks

    # Totales de ventas
    if "unit_cases" in df.columns:
        total_cases = df["unit_cases"].sum()
        neg_cases   = (df["unit_cases"] < 0).sum()
        results["total_unit_cases"] = float(total_cases)
        results["negative_cases"]   = int(neg_cases)
        if neg_cases > 0:
            insights.append(
                f"⚠️ {neg_cases:,} registros tienen unit_cases negativos. "
                f"Pueden ser devoluciones o notas de crédito legítimas — se mantienen tal cual. "
                f"Confirmar con el embotellador si deben excluirse del análisis."
            )

    # Rango de fechas
    date_col = "fecha" if "fecha" in df.columns else None
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        fecha_min = df[date_col].min()
        fecha_max = df[date_col].max()
        results["fecha_min"] = str(fecha_min.date()) if pd.notna(fecha_min) else "N/A"
        results["fecha_max"] = str(fecha_max.date()) if pd.notna(fecha_max) else "N/A"
        insights.append(f"📅 Rango de ventas: {results['fecha_min']} → {results['fecha_max']}")

        # Buckets de actividad (24 meses)
        if pd.notna(fecha_max):
            df["mes"] = df[date_col].dt.to_period("M")
            end_month   = fecha_max.to_period("M")
            start_month = end_month - 23

            df_24 = df[(df["mes"] >= start_month) & (df["mes"] <= end_month)].copy()
            meses_por_pos = (
                df_24.groupby("pos_id")["mes"]
                .nunique()
                .rename("n_meses_24")
                .reset_index()
            )
            total_pos = meses_por_pos["pos_id"].nunique()

            buckets = {
                "24 meses":  int((meses_por_pos["n_meses_24"] == 24).sum()),
                "21-23":     int(((meses_por_pos["n_meses_24"] >= 21) & (meses_por_pos["n_meses_24"] <= 23)).sum()),
                "18-20":     int(((meses_por_pos["n_meses_24"] >= 18) & (meses_por_pos["n_meses_24"] <= 20)).sum()),
                "15-17":     int(((meses_por_pos["n_meses_24"] >= 15) & (meses_por_pos["n_meses_24"] <= 17)).sum()),
                "12-14":     int(((meses_por_pos["n_meses_24"] >= 12) & (meses_por_pos["n_meses_24"] <= 14)).sum()),
                "<12 meses": int((meses_por_pos["n_meses_24"] < 12).sum()),
            }
            results["activity_buckets"] = buckets
            results["activity_window"] = f"{start_month} a {end_month}"

            pct_full_24 = buckets["24 meses"] / total_pos * 100 if total_pos else 0
            insights.append(
                f"📊 {buckets['24 meses']:,} POS ({pct_full_24:.1f}%) tienen ventas "
                f"en los 24 meses completos del período analizado."
            )

    # Cruce con clientes
    if df_clientes is not None and "pos_id" in df_clientes.columns:
        clientes_ids = set(pd.to_numeric(df_clientes["pos_id"], errors="coerce").dropna().unique())
        ventas_ids   = set(pd.to_numeric(df["pos_id"],          errors="coerce").dropna().unique())
        en_ventas    = clientes_ids & ventas_ids
        solo_ventas  = ventas_ids - clientes_ids  # en ventas pero no en maestra
        pct_match    = len(en_ventas) / len(clientes_ids) * 100 if clientes_ids else 0

        results["cross_clients"] = {
            "clientes_en_maestra":  len(clientes_ids),
            "clientes_en_ventas":   len(en_ventas),
            "pct_match":            round(pct_match, 2),
            "pos_solo_en_ventas":   len(solo_ventas),
        }
        insights.append(
            f"🔗 {len(en_ventas):,} de {len(clientes_ids):,} clientes ({pct_match:.1f}%) "
            f"tienen al menos una venta registrada."
        )
        if len(solo_ventas) > 0:
            insights.append(
                f"⚠️ {len(solo_ventas):,} pos_id en ventas no existen en la maestra de clientes."
            )

    # Cruce con productos
    if df_productos is not None and "product_id" in df_productos.columns:
        prod_ids = set(df_productos["product_id"].dropna().unique())
        venta_prod_ids = set(df["product_id"].dropna().unique()) if "product_id" in df.columns else set()
        sin_producto = venta_prod_ids - prod_ids
        results["cross_products"] = {
            "productos_en_maestra": len(prod_ids),
            "productos_en_ventas":  len(venta_prod_ids),
            "sin_match":            len(sin_producto),
        }
        if len(sin_producto) > 0:
            insights.append(
                f"⚠️ {len(sin_producto):,} product_id en ventas no existen en la maestra de productos."
            )

    results["insights"] = insights
    results["df_final"] = df

    return results
