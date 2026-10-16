# KPI Computation Logic

## Source file

The input CSV is the segmentation output (e.g. `cp_stills_bepensa_rd_20260615.csv`).  
Key columns:

| Column | Description |
|--------|-------------|
| `pos_id` | POS identifier (use `nunique()` for client counts) |
| `pos_subchannel` | Subchannel label |
| `pos_city` | City / territory name |
| `PotentialQualitative_<sufijo>` | Qualitative segment: Very High / High / Moderate / Low |
| `PotentialQuantitative_<sufijo>` | Current avg monthly UC (base volume) |
| `PotentialQuantitativeFinal_<sufijo>` | Estimated growth potential (delta UC/month) |

**Always filter first:** `df = df[df["PotentialQuantitative_TotalPortafolio"] > 0]`

---

## Suffixes by run type

### Traditional
```
TotalPortafolio
GlobalCat_CocaCola          → display as "Coca Cola"
GlobalCat_SparklingFlavors  → display as "Sparkling Flavors"
ServingType_SingleServe     → display as "Single Serve"
```

### Custom
```
TotalPortafolio                (always)
CustomCat_<Nombre>             → display as "<Nombre>"
```
*Example: if user says categories are "Stills" and "Sparkling":*
```
CustomCat_Stills
CustomCat_Sparkling
```

---

## Slide 7 — TotalPortafolio table

```python
grp = df.groupby("PotentialQualitative_TotalPortafolio").agg(
    pos_id=("pos_id", "nunique"),
    ventas=("PotentialQuantitative_TotalPortafolio", "sum"),
    crecimiento=("PotentialQuantitativeFinal_TotalPortafolio", "sum"),
).reset_index()

total_crec = grp["crecimiento"].sum()
total_pos = grp["pos_id"].sum()
total_ventas = grp["ventas"].sum()
```

Table rows (order: Very High → High → Moderate → Low → Total):
- `POS[n]` = `pos_id` nunique per segment
- `Promedio de ventas actuales [UC]` = sum of `PotentialQuantitative` / scale (auto: k or M)
- `Aporte al Crecimiento` = segment `PotentialQuantitativeFinal` / `total_crec`

**Narrative (bold text at top):**
```python
vh_h = grp[grp["PotentialQualitative_TotalPortafolio"].isin(["Very High", "High"])]
pct_clientes = round(100 * vh_h["pos_id"].sum() / total_pos)  → e.g. "20"
k_clientes   = round(vh_h["pos_id"].sum() / 1000)             → e.g. "3"
pct_vol      = round(100 * vh_h["crecimiento"].sum() / total_crec) → e.g. "81"
```

Very High detail line:
```python
vh = grp[grp["PotentialQualitative_TotalPortafolio"] == "Very High"]
vh_pct  = round(100 * vh["crecimiento"].sum() / total_crec, 2)   → "55.44"
vh_vol  = vh["crecimiento"].sum() / scale                         → "141" (k)
total   = total_crec / scale                                       → "255k"
```

---

## Slide 8 — Multi-category table

For each category suffix (3 max, shown side-by-side):
- Same groupby as slide 7 but for each suffix
- Shows only **Very High**, **High**, **Total (VH+H)**
- Aporte % = row crecimiento / total_crec for that suffix

**Narrative:** identify which category has highest Very High aporte %, then second.

---

## Slides 9 & 10 — Top 5 subchannel / city

```python
agrupador = "pos_subchannel"   # or "pos_city"

top5_vals = (
    df.groupby(agrupador)["PotentialQuantitativeFinal_TotalPortafolio"]
    .sum().sort_values(ascending=False).head(5).index
)
df["_group"] = np.where(df[agrupador].isin(top5_vals), df[agrupador].str.upper(), "OTROS")
```

For each suffix, compute: `aporte = group_crec / total_crec` (as %)
Columns: PDV [n] (only for TotalPortafolio), then aporte % per suffix.

Order: top5 alphabetically by rank (TotalPortafolio growth desc), then OTROS, then TOTAL.

---

## Slide 11 — Map city text

Top 2 cities by TotalPortafolio growth:
```python
city_stats = df.groupby("pos_city").agg(
    pos_id=("pos_id", "nunique"),
    crecimiento=("PotentialQuantitativeFinal_TotalPortafolio", "sum"),
    ventas=("PotentialQuantitative_TotalPortafolio", "sum"),
).sort_values("crecimiento", ascending=False).head(2)

pct_growth = round(100 * city_stats["crecimiento"] / city_stats["ventas"])
```

Output per city: `nombre`, `pos_n`, `pct_crecimiento`.

---

## Embudos (Slides 13–N) — One per category

```python
df_c = df[df[f"PotentialQuantitative_{sufijo}"] > 0]

# N1 — Very High + High
mask_n1 = df_c[f"PotentialQualitative_{sufijo}"].isin(["Very High", "High"])

# N2 — Top 2 subcanales within N1 (sort by PotentialQuantitativeFinal desc)
seg_n2 = df_c[mask_n1].groupby("pos_subchannel").agg(
    vol=(f"PotentialQuantitativeFinal_{sufijo}", "sum")
).sort_values("vol", ascending=False).head(2).index
mask_n2 = df_c["pos_subchannel"].isin(seg_n2)

# N3 — Top 2 cities within N1 & N2 (sort by PotentialQuantitativeFinal desc)
seg_n3 = df_c[mask_n1 & mask_n2].groupby("pos_city").agg(
    vol=(f"PotentialQuantitativeFinal_{sufijo}", "sum")
).sort_values("vol", ascending=False).head(2).index
mask_n3 = df_c["pos_city"].isin(seg_n3)
```

Values needed per embudo:
| Key | Description |
|-----|-------------|
| `total_clientes_num` | Total POS count ("15.9") |
| `total_vol_fmt` | Total growth volume ("255k") |
| `nar_pct_vol` | % of vol in VH+H ("81") |
| `n1_labels` | "Very High y high" |
| `n1_detail` | "207.29k UC/mes - 3.2K clientes" |
| `n2_labels` | "ALMACENES y AUTOSERVICIOS" |
| `n2_detail` | "173.69k UC/mes - 2.4K clientes" |
| `n2_pct_vol` | % vol N2 / total ("68") |
| `n2_pct_comercios` | % pos N2 / total ("15") |
| `n3_labels` | "Montevideo y Canelones" |
| `n3_detail` | "116.01k UC/mes - 1.5K clientes" |
| `n3_pct_vol` | % vol N3 / total ("45") |
| `n3_pct_pos` | % pos N3 / total ("9") |
| `n3_vol_num` | N3 vol number ("116") |
| `n3_vol_suf` | N3 vol suffix ("K") |
| `n3_pos_fmt` | N3 pos count rounded to hundreds ("1500") |

---

## Scale factor selection

```python
def auto_scale(val):
    if val >= 500_000:
        return 1_000_000, "M"
    return 1_000, "k"
```

Apply per value. The same scale should be used consistently within an embudo.
