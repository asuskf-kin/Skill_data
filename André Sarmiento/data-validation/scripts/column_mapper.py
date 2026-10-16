"""
column_mapper.py
Mapea automáticamente las columnas del archivo del cliente
a los nombres internos del skill usando fuzzy matching.
"""

import unicodedata
import re

# ─── Catálogo de columnas esperadas ──────────────────────────────────────────

CLIENTS_REQUIRED = {
    "pos_id":        ["cliente", "cod_cliente", "client_id", "id_cliente",
                      "cliente_id_key", "cod_cliente", "codigo_cliente"],
    "pos_name":      ["nombre del cliente", "nombre_cliente", "pos_nombre",
                      "razon_social", "nombre"],
    "pos_latitude":  ["coordenada y", "latitud", "lat", "latitude", "y",
                      "coord_y"],
    "pos_longitude": ["coordenada x", "longitud", "lon", "long", "longitude",
                      "x", "coord_x"],
    "pos_city":      ["nombre municipio", "municipio", "ciudad", "city"],
    "pos_subchannel":["descr. canal", "subcanal", "sub_canal", "subchannel"],
    "pos_channel":   ["descr. canal pais", "canal", "channel",
                      "descr. canal país"],
}

CLIENTS_OPTIONAL = {
    "pos_address":          ["calle", "direccion", "address", "pos_addres",
                             "dirección"],
    "pos_consumer_type":    ["descr. tipo de canal de cliente",
                             "tipo_consumidor", "consumer_type", "tipo_canal"],
    "pos_size_classification": ["descr. gec", "size", "tamano",
                                "clasificacion", "gec"],
    "pos_fecha_alta":       ["fecha de alta", "fecha_alta", "alta",
                             "date_open"],
    "pos_fecha_baja":       ["fecha de baja", "fecha_baja", "baja",
                             "date_close", "inactivo"],
    "pos_neighborhood":     ["colonia", "barrio", "neighborhood"],
    "pos_region":           ["region", "zona", "zone"],
    "segmentacion":         ["segmento", "segment"],
}

PRODUCTS_REQUIRED = {
    "product_id":       ["src_prod_cd", "cod_producto", "product_code",
                         "producto_id_key", "sku"],
    "product_name":     ["bpp_name", "nombre_producto", "descripcion_producto",
                         "product_description"],
    "product_brand":    ["brand_group", "marca_producto", "brand", "marca"],
    "global_category":  ["category_group", "categoria_global", "global_cat"],
    "serving_type":     ["serving_type", "tipo_envase", "presentacion",
                         "serving"],
    "refillability":    ["lt1_4_refillability", "retornable", "refillable"],
}

PRODUCTS_OPTIONAL = {
    "product_subcategory": ["sub_category", "subcategoria", "sub_cat"],
    "product_category":    ["category", "categoria", "cat"],
}

SALES_REQUIRED = {
    "pos_id":      ["cliente_id_key", "cod_cliente", "client_id"],
    "product_id":  ["producto_id_key", "cod_producto", "sku"],
    "unit_cases":  ["cajas", "units", "cases", "cantidad", "volumen"],
    "fecha":       ["fecha_entrega", "week_445", "date", "semana",
                    "fecha"],
}

SALES_OPTIONAL = {
    "month":           ["month_445", "mes"],
    "n_active_months": ["meses_activos", "active_months"],
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    """Minúsculas, sin tildes, sin espacios extra."""
    s = s.strip().lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s)
    return s


def similarity(a: str, b: str) -> float:
    """Similitud de Jaccard sobre bigramas."""
    def bigrams(s):
        return set(s[i:i+2] for i in range(len(s) - 1))
    ba, bb = bigrams(a), bigrams(b)
    if not ba or not bb:
        return 1.0 if a == b else 0.0
    return len(ba & bb) / len(ba | bb)


def find_best_match(col_norm: str, aliases: list[str]) -> float:
    """Devuelve la similitud máxima entre col_norm y los aliases."""
    return max(similarity(col_norm, normalize(a)) for a in aliases)


# ─── Función principal ───────────────────────────────────────────────────────

def map_columns(
    file_columns: list[str],
    base_type: str,  # "clients" | "products" | "sales"
    threshold_auto: float = 0.85,
    threshold_suggest: float = 0.55,
) -> dict:
    """
    Retorna un dict con:
    {
      "exact":    {internal_name: original_col, ...},   # mapeo automático
      "suggest":  {internal_name: (original_col, score), ...},  # requiere confirmación
      "missing":  [internal_name, ...],   # obligatorias no encontradas
      "unmapped": [original_col, ...],    # columnas del archivo sin mapear
    }
    """
    catalogs = {
        "clients":  {**CLIENTS_REQUIRED,  **CLIENTS_OPTIONAL},
        "products": {**PRODUCTS_REQUIRED, **PRODUCTS_OPTIONAL},
        "sales":    {**SALES_REQUIRED,    **SALES_OPTIONAL},
    }
    required_keys = {
        "clients":  set(CLIENTS_REQUIRED),
        "products": set(PRODUCTS_REQUIRED),
        "sales":    set(SALES_REQUIRED),
    }

    catalog = catalogs[base_type]
    required = required_keys[base_type]

    col_norm_map = {normalize(c): c for c in file_columns}
    used_cols = set()
    result = {"exact": {}, "suggest": {}, "missing": [], "unmapped": []}

    for internal, aliases in catalog.items():
        best_col, best_score = None, 0.0

        for col_norm, col_orig in col_norm_map.items():
            if col_orig in used_cols:
                continue
            # Coincidencia exacta contra aliases
            if col_norm in [normalize(a) for a in aliases]:
                best_col, best_score = col_orig, 1.0
                break
            # Fuzzy
            score = find_best_match(col_norm, aliases)
            if score > best_score:
                best_score = score
                best_col = col_orig

        if best_score >= threshold_auto:
            result["exact"][internal] = best_col
            used_cols.add(best_col)
        elif best_score >= threshold_suggest:
            result["suggest"][internal] = (best_col, round(best_score, 2))
            used_cols.add(best_col)
        elif internal in required:
            result["missing"].append(internal)

    result["unmapped"] = [c for c in file_columns if c not in used_cols]
    return result


def format_mapping_summary(mapping: dict, base_type: str) -> str:
    """Genera el texto legible para mostrarle al usuario."""
    lines = [f"**Mapeo detectado — {base_type.capitalize()}:**\n"]

    for internal, col in mapping["exact"].items():
        lines.append(f"✅  `{col}` → `{internal}`")

    for internal, (col, score) in mapping["suggest"].items():
        lines.append(f"⚠️  `{col}` → `{internal}`  ← ¿Correcto? (similitud: {score:.0%})")

    for internal in mapping["missing"]:
        lines.append(f"❓  No encontré columna para `{internal}` — ¿cuál columna tiene este dato?")

    if mapping["unmapped"]:
        unmapped_str = ", ".join(f"`{c}`" for c in mapping["unmapped"][:10])
        lines.append(f"\n📋  Columnas sin mapear (se ignorarán): {unmapped_str}")

    return "\n".join(lines)
