"""
validate_products.py
Validaciones sobre la maestra de productos.
"""

import pandas as pd


def validate_products(df: pd.DataFrame) -> dict:
    """
    Retorna dict con resultados de validación de productos.
    """
    results = {}
    insights = []
    df = df.copy()

    results["total"] = len(df)
    results["unique_ids"] = df["product_id"].nunique()

    # Duplicados
    dup_exact = df.duplicated().sum()
    dup_id    = df["product_id"].duplicated().sum()
    results["duplicates"] = {"exact": int(dup_exact), "by_id": int(dup_id)}
    if dup_id > 0:
        insights.append(f"⚠️ Hay {dup_id:,} product_id duplicados.")

    # Vacíos en columnas clave
    null_checks = {}
    for col in ["product_name", "product_brand", "serving_type",
                "global_category", "refillability"]:
        if col in df.columns:
            n = df[col].isna().sum()
            null_checks[col] = int(n)
            if n > 0:
                insights.append(f"⚠️ `{col}` tiene {n:,} valores vacíos.")
    results["nulls"] = null_checks

    # Distribuciones
    distributions = {}
    for col in ["product_brand", "global_category", "serving_type", "refillability"]:
        if col in df.columns:
            vc = df[col].value_counts().reset_index()
            vc.columns = [col, "count"]
            total = vc["count"].sum()
            vc["pct"] = (vc["count"] / total * 100).round(2)
            distributions[col] = vc.to_dict("records")
    results["distributions"] = distributions

    # Refillability: detectar valores desconocidos
    if "refillability" in df.columns:
        valid_vals = {"returnable", "nonreturnable", "non-returnable",
                      "retornable", "no retornable"}
        unknown = df["refillability"].dropna().apply(
            lambda x: str(x).lower().strip() not in valid_vals
        ).sum()
        if unknown > 0:
            insights.append(
                f"🔍 {unknown:,} productos tienen refillability desconocido. "
                f"Revisar si corresponde a 'NonReturnable'."
            )
        results["refillability_unknown"] = int(unknown)

    # Categorías de alto nivel
    if "global_category" in df.columns:
        emerging = (df["global_category"].str.lower().str.strip() == "emerging beverages").sum()
        if emerging > 0:
            insights.append(
                f"📌 {emerging:,} productos son 'Emerging Beverages' — "
                f"estos se excluirán de las ventas en el procesamiento."
            )
        results["emerging_beverages"] = int(emerging)

    results["insights"] = insights
    results["df_final"] = df

    return results
