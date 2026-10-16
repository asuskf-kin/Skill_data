"""
derive_consumer_type.py
Construye pos_consumer_type_internal a partir de pos_subchannel
cuando no existe la columna pos_consumer_type oficial.

Lógica basada en la clasificación estándar Femsa/Coca-Cola:
  - ON PREMISE  → establecimientos donde se consume en el lugar
  - OFF PREMISE → establecimientos donde se lleva el producto
  - MODERNO     → canales modernos (supermercados, tiendas de conveniencia)
  - INDIRECTOS  → distribuidores, mayoristas
"""

import pandas as pd
import re


# ── Mapa de subcanal → consumer type ─────────────────────────────────────────
# Clave: fragmento (lowercase, sin tildes) que aparece en el subcanal
# Valor: categoría asignada

ON_PREMISE_KEYWORDS = [
    "bar", "taberna", "cantina", "restaurant", "restaurante",
    "fonda", "loncheria", "lonchería", "merendero", "comida rapida",
    "comida rápida", "cafeteria", "cafetería", "hotel", "motel",
    "estadio", "cine", "teatro", "club", "discoteca", "antro",
    "taqueria", "taquería", "cocina", "marisqueria", "marisquería",
    "pizzeria", "pizzería", "hamburgueseria", "sushi", "buffet",
    "on premise", "on-premise", "consume", "otros on",
]

OFF_PREMISE_KEYWORDS = [
    "abarrote", "miscelanea", "miscelánea", "tienda", "expendio",
    "hogar con venta", "hogar", "papeleria", "papelería",
    "farmacia", "ferreteria", "ferretería", "carniceria", "carnicería",
    "tortilleria", "tortillería", "panaderia", "panadería",
    "dulceria", "dulcería", "verduleria", "verdulería",
    "frutas", "verduras", "flores", "botanero", "botana",
    "auto chico", "autogrande", "auto grande", "autocine",
    "deposito", "depósito", "licorera", "licoreria", "licorería",
    "vulcanizadora", "gasolinera", "lavanderia", "lavandería",
    "otros off", "off premise", "off-premise", "peluqueria",
    "peluquería", "salon", "salón", "spa",
]

MODERNO_KEYWORDS = [
    "supermercado", "super mercado", "hipermercado", "minisuper",
    "mini super", "bodega", "warehouse", "costco", "walmart",
    "soriana", "chedraui", "oxxo", "seven", "7-eleven",
    "circle k", "extra", "kiosko", "farmacias", "farmacia",
    "moderno", "canal moderno", "autoservicio",
]

INDIRECTOS_KEYWORDS = [
    "mayorista", "mayoreo", "distribuidor", "subdistribuidor",
    "indirecto", "indirectos", "ruta", "deposito mayorista",
]


def normalize_text(s: str) -> str:
    """Minúsculas sin tildes."""
    import unicodedata
    s = str(s).lower().strip()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def classify_subchannel(subchannel_value: str) -> str:
    """
    Clasifica un valor de subcanal en consumer type.
    Retorna: 'ON PREMISE' | 'OFF PREMISE' | 'MODERNO' | 'INDIRECTOS' | 'OTROS'
    """
    if pd.isna(subchannel_value):
        return "OTROS"

    val = normalize_text(subchannel_value)

    for kw in ON_PREMISE_KEYWORDS:
        if kw in val:
            return "ON PREMISE"

    for kw in MODERNO_KEYWORDS:
        if kw in val:
            return "MODERNO"

    for kw in INDIRECTOS_KEYWORDS:
        if kw in val:
            return "INDIRECTOS"

    for kw in OFF_PREMISE_KEYWORDS:
        if kw in val:
            return "OFF PREMISE"

    return "OTROS"


def derive_consumer_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega la columna pos_consumer_type_internal al DataFrame
    basándose en pos_subchannel.

    También imprime un resumen de la clasificación para que el usuario
    pueda revisar y corregir si algún subcanal quedó mal clasificado.
    """
    if "pos_subchannel" not in df.columns:
        raise ValueError("No existe la columna pos_subchannel en el DataFrame.")

    df = df.copy()
    df["pos_consumer_type_internal"] = df["pos_subchannel"].apply(classify_subchannel)

    # Resumen por subcanal → tipo asignado (para revisión del usuario)
    resumen = (
        df.groupby(["pos_subchannel", "pos_consumer_type_internal"])["pos_id"]
        .count()
        .reset_index()
    )
    resumen.columns = ["Subcanal", "Consumer Type (Derivado)", "POS"]
    resumen = resumen.sort_values("POS", ascending=False)

    print("\n📋 Clasificación derivada pos_consumer_type_internal:")
    print(resumen.to_string(index=False))

    # Alerta si hay muchos "OTROS"
    otros = (df["pos_consumer_type_internal"] == "OTROS").sum()
    if otros > 0:
        pct = otros / len(df) * 100
        print(
            f"\n⚠️  {otros:,} registros ({pct:.1f}%) quedaron clasificados como 'OTROS' "
            f"porque su subcanal no coincidió con ningún patrón conocido. "
            f"Revisa la tabla anterior y avísame si necesitas reclasificar alguno."
        )

    return df, resumen


# ── Distribución final ────────────────────────────────────────────────────────

def summarize_consumer_type_internal(df: pd.DataFrame) -> pd.DataFrame:
    """Genera tabla de distribución de pos_consumer_type_internal."""
    col = "pos_consumer_type_internal"
    if col not in df.columns:
        return pd.DataFrame()

    vc = df.groupby(col)["pos_id"].count().reset_index()
    vc.columns = [col, "count"]
    total = vc["count"].sum()
    vc["pct"] = (vc["count"] / total * 100).round(2)
    vc = vc.sort_values("count", ascending=False)
    return vc
