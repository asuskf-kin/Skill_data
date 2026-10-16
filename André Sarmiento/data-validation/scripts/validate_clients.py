"""
validate_clients.py
Ejecuta todas las validaciones sobre la maestra de clientes.
Recibe un DataFrame ya renombrado con los nombres internos (pos_id, pos_name, etc.)
y un GeoDataFrame del territorio.
Retorna un dict con todos los resultados para el reporte y los DataFrames de salida.
"""

import pandas as pd
import numpy as np
import geopandas as gpd


def validate_clients(df: pd.DataFrame, geo: gpd.GeoDataFrame) -> dict:
    """
    Parámetros:
        df   : DataFrame con columnas renombradas a nombres internos
        geo  : GeoDataFrame del territorio (GeoJSON del país/zona)

    Retorna dict con:
        "total_original", "geo", "duplicates_by_id", "duplicates_by_name_coords",
        "coordinates", "nulls", "fecha_baja", "distributions",
        "filter_summary", "steps_log", "insights",
        "df_final"   → base limpia exportable,
        "df_issues"  → registros con problemas + columna validation_issues
    """
    results = {}
    insights = []
    steps_log = []
    df = df.copy()

    # Columna de issues por registro
    df["validation_issues"] = [[] for _ in range(len(df))]

    def add_issue(idx_list, issue: str):
        for i in idx_list:
            if i in df.index:
                df.at[i, "validation_issues"].append(issue)

    def log_step(label, before, after):
        steps_log.append({
            "label":         label,
            "before":        before,
            "after":         after,
            "removed":       before - after,
            "pct_remaining": round(after / results["total_original"] * 100, 2),
        })

    # ── 1. Total original ────────────────────────────────────────────────────
    results["total_original"] = len(df)

    # ── 2. IDs: faltantes y duplicados ──────────────────────────────────────
    missing_ids  = df[df["pos_id"].isna()].index.tolist()
    dup_ids_idx  = df[df["pos_id"].duplicated(keep=False)].index.tolist()
    add_issue(missing_ids, "missing_id")
    add_issue(dup_ids_idx, "duplicate_id")
    results["unique_ids"]   = int(df["pos_id"].nunique())
    results["missing_ids"]  = len(missing_ids)
    results["dup_ids"]      = len(dup_ids_idx)
    if dup_ids_idx:
        insights.append(f"⚠️ Hay {len(dup_ids_idx):,} registros con pos_id duplicado.")

    # ── 3. Coordenadas: parseo y correcciones ────────────────────────────────
    df["pos_latitude"]  = pd.to_numeric(df["pos_latitude"],  errors="coerce")
    df["pos_longitude"] = pd.to_numeric(df["pos_longitude"], errors="coerce")

    # Corregir longitudes positivas solo si el territorio está en el hemisferio occidental
    # (detectado por el centroide del GeoJSON — evita corregir países con longitud este como Kazajistán)
    geo_centroid_lon = geo.geometry.unary_union.centroid.x
    western_hemisphere = geo_centroid_lon < 0

    mask_pos_lon = df["pos_longitude"] > 4
    corrected_lon = int(mask_pos_lon.sum())
    if corrected_lon > 0 and western_hemisphere:
        df.loc[mask_pos_lon, "pos_longitude"] = -df.loc[mask_pos_lon, "pos_longitude"]
        insights.append(f"🔧 Se corrigieron {corrected_lon:,} longitudes positivas a negativas.")
    elif corrected_lon > 0 and not western_hemisphere:
        corrected_lon = 0  # no correction needed

    # Nulos
    lat_null = int(df["pos_latitude"].isna().sum())
    lon_null = int(df["pos_longitude"].isna().sum())
    add_issue(df[df["pos_latitude"].isna()].index.tolist(),  "missing_lat")
    add_issue(df[df["pos_longitude"].isna()].index.tolist(), "missing_lon")

    # Coordenadas enteras (1, 2, 3, 4… — inválidas)
    lat_int = int(df["pos_latitude"].dropna().apply(lambda x: x % 1 == 0).sum())
    lon_int = int(df["pos_longitude"].dropna().apply(lambda x: x % 1 == 0).sum())

    # Coordenadas exactamente en 0 — GPS sin señal / campo vacío exportado como cero
    lat_zero = int((df["pos_latitude"] == 0).sum())
    lon_zero = int((df["pos_longitude"] == 0).sum())
    zero_idx = df[(df["pos_latitude"] == 0) | (df["pos_longitude"] == 0)].index.tolist()
    add_issue(zero_idx, "zero_coord")
    if lat_zero > 0 or lon_zero > 0:
        insights.append(
            f"⚠️ {lat_zero:,} latitudes y {lon_zero:,} longitudes con valor exacto 0 "
            f"(posible GPS sin señal o campo vacío exportado como cero)."
        )

    # Fuera de rango válido (lat > 90 / < -90 ; lon > 180 / < -180)
    invalid_range_idx = df[
        (df["pos_latitude"]  >  90) | (df["pos_latitude"]  < -90) |
        (df["pos_longitude"] > 180) | (df["pos_longitude"] < -180)
    ].index.tolist()
    add_issue(invalid_range_idx, "invalid_coord_range")

    # ── 4. Detección de coordenadas INVERTIDAS (lat/lon swapped) ─────────────

    # Método 1 — por rango: lat fuera de [-90,90] pero lon dentro → probablemente swapped
    inverted_range_idx = df[
        ((df["pos_latitude"] < -90) | (df["pos_latitude"] > 90)) &
        (df["pos_longitude"].between(-90, 90))
    ].index.tolist()
    add_issue(inverted_range_idx, "possible_inverted_range")

    # Método 2 — estadístico: si el punto encaja mejor con lat/lon swapped
    inverted_dist_idx = _detect_inverted_by_distribution(df)
    add_issue(inverted_dist_idx, "possible_inverted_distribution")

    all_inverted = set(inverted_range_idx) | set(inverted_dist_idx)
    if all_inverted:
        insights.append(
            f"🔄 {len(all_inverted):,} registros parecen tener lat/lon invertidos "
            f"({len(inverted_range_idx)} detectados por rango, "
            f"{len(inverted_dist_idx)} por distribución estadística). "
            f"Revisar antes de usar las coordenadas."
        )

    results["coordinates"] = {
        "lat_null":            lat_null,
        "lon_null":            lon_null,
        "lat_integer":         lat_int,
        "lon_integer":         lon_int,
        "lat_zero":            lat_zero,
        "lon_zero":            lon_zero,
        "invalid_range":       len(invalid_range_idx),
        "inverted_range":      len(inverted_range_idx),
        "inverted_dist":       len(inverted_dist_idx),
        "corrected_longitude": corrected_lon,
    }

    # ── 5. Geo-validación ────────────────────────────────────────────────────
    if geo.crs is None:
        geo = geo.set_crs("EPSG:4326")
    else:
        geo = geo.to_crs("EPSG:4326")
    geo_union = geo.geometry.unary_union

    df_coords_validas = df.dropna(subset=["pos_latitude", "pos_longitude"]).copy()
    df_coords_validas = df_coords_validas[
        (df_coords_validas["pos_latitude"]  % 1 != 0) &
        (df_coords_validas["pos_longitude"] % 1 != 0)
    ]

    gdf = gpd.GeoDataFrame(
        df_coords_validas,
        geometry=gpd.points_from_xy(
            df_coords_validas["pos_longitude"],
            df_coords_validas["pos_latitude"]
        ),
        crs="EPSG:4326"
    )

    outside_idx = gdf[~gdf.geometry.within(geo_union)].index.tolist()
    add_issue(outside_idx, "outside_geojson")

    dentro = len(df_coords_validas) - len(outside_idx)
    fuera  = len(df) - dentro
    results["geo"] = {
        "total_con_coords_validas": len(df_coords_validas),
        "dentro_territorio":        dentro,
        "fuera_territorio":         fuera,
        "pct_dentro":               round(dentro / len(df) * 100, 2) if len(df) else 0,
    }

    before = len(df)
    df_geo = gdf[gdf.geometry.within(geo_union)].drop(columns=["geometry"]).copy()
    log_step("Fuera del territorio (GeoJSON)", before, len(df_geo))

    # ── 6. Duplicados por ID — conservar el registro más completo ────────────
    before = len(df_geo)
    dup_groups = df_geo[df_geo["pos_id"].duplicated(keep=False)]
    drop_by_id = []
    for _, group in dup_groups.groupby("pos_id"):
        completeness = group.drop(columns=["validation_issues"]).notna().sum(axis=1)
        keep_idx     = completeness.idxmax()
        drop_by_id.extend([i for i in group.index if i != keep_idx])

    add_issue(drop_by_id, "duplicate_id_drop")
    df_geo = df_geo.drop(index=drop_by_id)
    log_step("IDs duplicados (conservado el más completo)", before, len(df_geo))
    results["duplicates_by_id"] = {
        "groups":  int(dup_groups["pos_id"].nunique()),
        "dropped": len(drop_by_id),
    }
    if drop_by_id:
        insights.append(
            f"🗑️ {len(drop_by_id):,} duplicados de pos_id eliminados "
            f"(se conservó el registro con más campos completos en cada grupo)."
        )

    # ── 7. Duplicados por nombre + coordenadas ───────────────────────────────
    # Solo se ejecuta si pos_name existe — sin nombre no es posible distinguir
    # negocios distintos en la misma coordenada (edificios, centros comerciales, etc.)
    before = len(df_geo)
    drop_name_coords  = []
    name_coord_groups = 0
    has_pos_name = "pos_name" in df_geo.columns and df_geo["pos_name"].notna().any()

    if has_pos_name:
        df_geo["_name_norm"] = df_geo["pos_name"].astype(str).str.lower().str.strip()
        df_geo["_coord_key"] = (
            df_geo["pos_latitude"].round(6).astype(str) + "/" +
            df_geo["pos_longitude"].round(6).astype(str)
        )
        for _, group in df_geo.groupby(["_coord_key", "_name_norm"]):
            if len(group) > 1:
                name_coord_groups += 1
                completeness = group.drop(
                    columns=["validation_issues", "_name_norm", "_coord_key"]
                ).notna().sum(axis=1)
                keep_idx = completeness.idxmax()
                drop_name_coords.extend([i for i in group.index if i != keep_idx])
        add_issue(drop_name_coords, "duplicate_name_coord_drop")
        df_geo = df_geo.drop(index=drop_name_coords).drop(columns=["_name_norm", "_coord_key"])
        if drop_name_coords:
            insights.append(f"🗑️ {len(drop_name_coords):,} duplicados por nombre+coordenadas eliminados.")
    else:
        insights.append(
            "⚠️ No se encontró la columna pos_name — se omitió la deduplicación por "
            "nombre+coordenadas. Sin nombre no es posible distinguir negocios distintos "
            "en una misma ubicación."
        )

    log_step("Duplicados nombre+coordenadas (conservado el más completo)", before, len(df_geo))
    results["duplicates_by_name_coords"] = {
        "groups":  name_coord_groups,
        "dropped": len(drop_name_coords),
        "skipped": not has_pos_name,
    }

    # ── 8. Fecha de baja ─────────────────────────────────────────────────────
    fecha_baja_result = {}
    if "pos_fecha_baja" in df_geo.columns:
        con_baja = int(df_geo["pos_fecha_baja"].notna().sum())
        fechas   = pd.to_datetime(df_geo["pos_fecha_baja"], errors="coerce")
        fecha_baja_result = {
            "con_baja": con_baja,
            "sin_baja": int(df_geo["pos_fecha_baja"].isna().sum()),
            "fecha_min": str(fechas.min().date()) if pd.notna(fechas.min()) else "N/A",
            "fecha_max": str(fechas.max().date()) if pd.notna(fechas.max()) else "N/A",
        }
        if con_baja > 0:
            pct_baja = con_baja / len(df_geo) * 100
            insights.append(
                f"📅 {con_baja:,} registros ({pct_baja:.1f}%) tienen fecha de baja "
                f"({fecha_baja_result['fecha_min']} → {fecha_baja_result['fecha_max']}). "
                f"Se mantienen para prospección, se excluirán en segmentación."
            )
    results["fecha_baja"] = fecha_baja_result

    # ── 9. Vacíos en columnas clave ──────────────────────────────────────────
    null_checks = {}
    for col in ["pos_name", "pos_address", "pos_city", "pos_consumer_type",
                "pos_channel", "pos_subchannel", "pos_size_classification"]:
        if col in df_geo.columns:
            idx = df_geo[df_geo[col].isna()].index.tolist()
            n   = len(idx)
            null_checks[col] = n
            add_issue(idx, f"missing_{col}")
            if n > 0 and n / len(df_geo) * 100 > 5:
                insights.append(f"⚠️ `{col}` tiene {n:,} valores vacíos ({n/len(df_geo)*100:.1f}%).")
    results["nulls"] = null_checks

    # ── 10. Distribuciones ───────────────────────────────────────────────────
    distributions = {}
    for col in ["pos_city", "pos_subchannel", "pos_channel",
                "pos_consumer_type", "pos_macro_channel",
                "pos_consumer_type_internal", "pos_size_classification"]:
        if col in df_geo.columns:
            vc = df_geo.groupby(col)["pos_id"].count().reset_index()
            vc.columns = [col, "count"]
            total_d = vc["count"].sum()
            vc["pct"] = (vc["count"] / total_d * 100).round(2)
            distributions[col] = vc.sort_values("count", ascending=False).to_dict("records")
    results["distributions"] = distributions

    if "pos_subchannel" in distributions and distributions["pos_subchannel"]:
        top3_pct   = sum(r["pct"] for r in distributions["pos_subchannel"][:3])
        top3_names = [list(r.values())[0] for r in distributions["pos_subchannel"][:3]]
        if top3_pct > 60:
            insights.append(
                f"📊 Los 3 principales subcanales ({', '.join(str(n) for n in top3_names)}) "
                f"concentran el {top3_pct:.1f}% de los POS."
            )

    # ── 11. Tabla resumen de filtros ─────────────────────────────────────────
    filter_summary = []
    for step in steps_log:
        filter_summary.append({
            "filtro":    step["label"],
            "afectados": step["removed"],
            "restantes": step["after"],
            "pct":       step["pct_remaining"],
        })
    if fecha_baja_result.get("con_baja", 0) > 0:
        filter_summary.append({
            "filtro":    "Fecha Baja (mantenidos para prospección)",
            "afectados": fecha_baja_result["con_baja"],
            "restantes": len(df_geo),
            "pct":       round(len(df_geo) / results["total_original"] * 100, 2),
        })
    results["filter_summary"] = filter_summary
    results["steps_log"]      = steps_log

    # ── 12. DataFrames de salida ─────────────────────────────────────────────
    # Serializar issues en df original completo (incluye los eliminados por geo)
    df["validation_issues"] = df["validation_issues"].apply(
        lambda x: ";".join(x) if isinstance(x, list) else str(x)
    )

    # Razones legibles en español para cada código de issue
    ISSUE_LABELS = {
        "outside_geojson":                "Fuera del territorio de operación (GeoJSON)",
        "missing_id":                     "Sin identificador de cliente (pos_id vacío)",
        "duplicate_id":                   "pos_id duplicado en la base",
        "duplicate_id_drop":              "Eliminado por pos_id duplicado (se conservó el más completo)",
        "missing_lat":                    "Sin latitud",
        "missing_lon":                    "Sin longitud",
        "zero_coord":                     "Coordenadas en cero (GPS sin señal o campo vacío)",
        "invalid_coord_range":            "Coordenadas fuera del rango válido",
        "possible_inverted_range":        "Lat/Lon posiblemente invertidos (por rango)",
        "possible_inverted_distribution": "Lat/Lon posiblemente invertidos (estadístico)",
        "duplicate_name_coord_drop":      "Eliminado por duplicado de nombre+coordenadas",
        "missing_pos_name":               "Sin nombre del cliente",
        "missing_pos_address":            "Sin dirección",
        "missing_pos_city":               "Sin ciudad",
        "missing_pos_channel":            "Sin canal de venta",
        "missing_pos_subchannel":         "Sin subcanal",
        "missing_pos_consumer_type":      "Sin tipo de canal (On/Off Premise)",
        "missing_pos_size_classification":"Sin clasificación de tamaño",
    }

    def translate_issues(issues_str):
        if not issues_str:
            return ""
        codes = issues_str.split(";")
        labels = [ISSUE_LABELS.get(c.strip(), c.strip()) for c in codes if c.strip()]
        return " | ".join(labels)

    df["issue_description"] = df["validation_issues"].apply(translate_issues)

    # df_final  : registros en df_geo sin ningún issue — base limpia exportable
    df_geo["validation_issues"] = df_geo["validation_issues"].apply(
        lambda x: ";".join(x) if isinstance(x, list) else str(x)
    )
    df_geo["issue_description"] = df_geo["validation_issues"].apply(translate_issues)

    df_final = df_geo[df_geo["validation_issues"] == ""].drop(
        columns=["validation_issues", "issue_description"]
    )

    # df_issues : TODOS los registros con algún problema (del df original completo)
    df_issues = df[df["validation_issues"] != ""].copy()
    # Ordenar por tipo de issue para facilitar revisión
    df_issues = df_issues.sort_values("validation_issues")

    results["insights"]  = insights
    results["df_final"]  = df_final
    results["df_issues"] = df_issues

    return results


# ── Helper: detección estadística de coordenadas invertidas ──────────────────

def _detect_inverted_by_distribution(df: pd.DataFrame, threshold_ratio: float = 5.0) -> list:
    """
    Compara la distancia de cada punto al centroide de la nube normal vs. swapped.
    Si el punto encaja mucho mejor swapped, lo marca como posiblemente invertido.
    Vectorizado para performance en bases grandes.
    """
    lat = pd.to_numeric(df["pos_latitude"],  errors="coerce")
    lon = pd.to_numeric(df["pos_longitude"], errors="coerce")

    valid = lat.notna() & lon.notna()
    if valid.sum() == 0:
        return []

    lat_mean = lat[valid].mean()
    lon_mean = lon[valid].mean()

    d_normal  = np.sqrt((lat - lat_mean) ** 2 + (lon - lon_mean) ** 2)
    d_swapped = np.sqrt((lon - lat_mean) ** 2 + (lat - lon_mean) ** 2)

    mask = valid & (d_normal > 0) & (d_swapped < d_normal / threshold_ratio)
    return df.index[mask].tolist()
