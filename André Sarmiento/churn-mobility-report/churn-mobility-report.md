---
name: churn-mobility-report
description: >
  Genera un informe HTML interactivo y autocontenido de análisis Churn × Movilidad para
  embotelladores Femsa/KOF, con branding oficial Kin Analytics. Úsalo SIEMPRE que el usuario
  quiera crear o actualizar un reporte HTML a partir de una base de datos de clientes churned
  con datos de visitation/mobility H3. Activa cuando el usuario mencione "informe churn",
  "reporte movilidad", "HTML churn", "churn x mobility", "análisis de movilidad",
  "visitation data", "H3 mobility", o cuando suba un CSV con columnas como pos_h3_cell,
  pct_change_devices, churn_reason, avg_devices_pre, pos_zone, pos_subchannel.
author: Kin Analytics
version: "1.1"
markets: MEX, NIC, VEN, COL (cualquier mercado con datos H3 de movilidad)
brand: kin-brand (ver sección KIN ANALYTICS BRAND)
---

# Skill: Churn × Mobility HTML Report

## Descripción

Genera un reporte HTML **interactivo y autocontenido** (una sola página, sin backend)
que correlaciona datos de churn de clientes con señales de tráfico peatonal (H3 mobility),
aplicando la identidad visual oficial de **Kin Analytics** (fondo oscuro, KIN Yellow, Space Grotesk).
El reporte usa **Chart.js** vía CDN e inyecta todos los datos como JSON embebido.

## Flujo completo

```
CSV de análisis       →   Paso 1: Leer y validar columnas
(Churn_*_Analysis.csv)     Paso 2: Recomputar mob_drop / mob_drop_light
                           Paso 3: Calcular chart_data (7 estructuras)
                           Paso 4: Renderizar HTML con branding Kin + f-string
                           Paso 5: Guardar en /mnt/user-data/outputs/
```

---

## ═══════════════════════════════════════════
## KIN ANALYTICS BRAND — HTML REPORTS
## ═══════════════════════════════════════════

### Filosofía visual
Los reportes HTML de Kin Analytics son **dark, data-forward y premium**.
Fondo oscuro (`#141417`), texto blanco, y el acento KIN Yellow (`#E5FF01`).
Esto aplica a todos los dashboards interactivos. Para reportes impresos/PDF se
puede usar fondo claro (ver sección Light override).

### CSS Variables — siempre en `:root`

```css
:root {
  /* Paleta Kin Analytics */
  --kin-black:   #141417;
  --kin-gray4:   #222326;
  --kin-gray3:   #999EA6;
  --kin-gray2:   #D4D5D6;
  --kin-gray1:   #EFEFEE;
  --kin-white:   #FFFFFF;
  --kin-yellow:  #E5FF01;

  /* Roles semánticos */
  --bg-primary:   var(--kin-black);
  --bg-secondary: var(--kin-gray4);
  --bg-card:      #1a1a1e;
  --text-primary: var(--kin-white);
  --text-muted:   var(--kin-gray3);
  --accent:       var(--kin-yellow);
  --border:       rgba(255, 255, 255, 0.08);

  /* Colores semánticos del análisis (sobre fondo oscuro) */
  --danger:  #FF5555;   /* caída severa de movilidad */
  --warning: #FFC800;   /* caída moderada */
  --ok:      #E5FF01;   /* normal / KPIs positivos  — usar yellow */
  --info:    #999EA6;   /* datos secundarios        — usar gray3  */

  /* Tipografía */
  --font-title: 'Space Grotesk', Arial, Helvetica, sans-serif;
  --font-body:  'Albert Sans',   Arial, Calibri,   sans-serif;
}
```

### Fuentes — Google Fonts CDN (siempre incluir en `<head>`)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;700&family=Albert+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

```css
body {
  font-family: var(--font-body);
  background: var(--bg-primary);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, h4, .kpi-value, .stat-value {
  font-family: var(--font-title);
}
```

### Header Kin Analytics

```html
<header class="kin-header">
  <div class="kin-brand">
    <span class="kin-logo">Kin Analytics</span><span class="kin-hex">◆</span>
  </div>
  <div class="kin-report-title">Churn × Mobility — FEMSA Mexico</div>
  <div class="kin-meta">May 2024 → Feb 2026  ·  H3 Res. 9  ·  7 Zonas</div>
</header>
```

```css
.kin-header {
  background: var(--bg-secondary);
  border-bottom: 2px solid var(--accent);
  padding: 16px 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.kin-logo { font-family: var(--font-title); font-weight: 500; font-size: 18px; }
.kin-hex  { color: var(--accent); font-size: 14px; margin-left: -4px; }
.kin-report-title { font-family: var(--font-title); font-size: 15px; flex: 1; color: var(--text-primary); }
.kin-meta { font-size: 11px; color: var(--text-muted); }
```

### KPI Cards

```css
.kpi {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px;
}
/* Barra amarilla en la parte superior — marca Kin */
.kpi::before {
  content: '';
  display: block;
  width: 32px;
  height: 3px;
  background: var(--accent);
  margin-bottom: 16px;
  border-radius: 2px;
}
.kpi-value {
  font-family: var(--font-title);
  font-size: 2.4rem;
  font-weight: 700;
  line-height: 1;
  color: var(--kin-yellow);   /* siempre yellow como default */
}
.kpi-value.danger  { color: var(--danger); }
.kpi-value.warning { color: var(--warning); }
.kpi-label { font-size: .72rem; color: var(--text-muted); margin-top: 8px;
             text-transform: uppercase; letter-spacing: .06em; }
.kpi-sub   { font-size: .82rem; color: var(--text-muted); margin-top: 4px; }
```

### Tamaño de charts — patrón obligatorio con Chart.js responsive

Con `responsive: true`, Chart.js **ignora el atributo `height` del `<canvas>`** y toma
el tamaño del contenedor padre. El patrón correcto es envolver cada canvas en un div con
`position: relative` y altura CSS explícita:

```css
.chart-wrap       { position: relative; height: 185px; }  /* default */
.chart-wrap.tall  { height: 230px; }   /* barras horizontales con ≥7 items */
.chart-wrap.short { height: 135px; }   /* charts simples / poco datos */
```

```html
<!-- ✅ Correcto -->
<div class="chart-wrap"><canvas id="myChart"></canvas></div>
<div class="chart-wrap tall"><canvas id="bigChart"></canvas></div>

<!-- ❌ Incorrecto — height= en canvas se ignora con responsive:true -->
<canvas id="myChart" height="300"></canvas>
```

Guía de alturas por tipo de chart:

| Chart                         | Clase          | Altura |
|-------------------------------|----------------|--------|
| Histograma / Scatter          | (default)      | 185px  |
| Barras mensuales / Línea      | (default)      | 185px  |
| Barras horiz. ≥7 items (dual) | `.tall`        | 230px  |
| Chart simple / pocos datos    | `.short`       | 135px  |

### Chart.js — Defaults globales (poner ANTES de crear cualquier chart)

```javascript
Chart.defaults.color           = '#999EA6';
Chart.defaults.font.family     = "'Albert Sans', Arial, sans-serif";
Chart.defaults.font.size       = 11;
Chart.defaults.scale.grid.color       = 'rgba(255,255,255,0.06)';
Chart.defaults.scale.grid.borderColor = 'rgba(255,255,255,0.10)';
```

### Chart.js — Tooltip estándar Kin

```javascript
const KIN_TOOLTIP = {
  backgroundColor: '#222326',
  titleColor:      '#FFFFFF',
  bodyColor:       '#999EA6',
  borderColor:     '#E5FF01',
  borderWidth:     1,
};
// Usar en cada chart: plugins: { tooltip: KIN_TOOLTIP }
```

### Colores de datos en charts

| Rol                         | Color                     | CSS var      |
|-----------------------------|---------------------------|--------------|
| Serie principal / positiva  | `#E5FF01` KIN Yellow      | `--accent`   |
| Caída severa (>15%)         | `#FF5555`                 | `--danger`   |
| Caída moderada (>5%)        | `#FFC800`                 | `--warning`  |
| Volumen / referencia        | `rgba(255,255,255,0.15)`  | `--border`   |
| Segunda serie               | `#999EA6` Gray 3          | `--info`     |
| Fill bajo línea             | `rgba(229,255,1,0.08)`    | —            |

### Tabla de datos Kin

```css
.kin-table { width: 100%; border-collapse: collapse; font-size: .83rem; }
.kin-table thead tr { border-bottom: 2px solid var(--accent); }
.kin-table thead th {
  padding: 10px 14px; text-align: left;
  font-family: var(--font-title); font-size: .72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: .06em; color: var(--text-muted);
}
.kin-table tbody tr { border-bottom: 1px solid var(--border); }
.kin-table tbody tr:hover { background: rgba(229,255,1,0.04); }
.kin-table tbody td { padding: 10px 14px; }
```

### Badges / Pills Kin

```css
.badge { display:inline-block; padding:3px 10px; border-radius:12px;
         font-size:11px; font-weight:600; font-family: var(--font-body); }
.badge-danger  { background:rgba(255,85,85,0.15);   color:#FF5555; }
.badge-warning { background:rgba(255,200,0,0.15);   color:#FFC800; }
.badge-ok      { background:rgba(229,255,1,0.15);   color:#E5FF01; }
.badge-muted   { background:rgba(153,158,166,0.15); color:#999EA6; }
```

### Cards de contenido

```css
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 22px;
}
.card h3     { font-family: var(--font-title); font-size: .95rem; font-weight: 600;
               margin-bottom: 4px; color: var(--text-primary); }
.card-sub    { font-size: .8rem; color: var(--text-muted); margin-bottom: 16px; }
```

### Insight / Callout box

```css
.insight {
  background: rgba(229,255,1,0.06);
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  padding: 14px 18px;
  font-size: .88rem; line-height: 1.6; margin-bottom: 20px;
}
.insight strong { color: var(--accent); }
.insight.danger-bg {
  background: rgba(255,85,85,0.08);
  border-left-color: var(--danger);
}
.insight.danger-bg strong { color: var(--danger); }
.insight.warning-bg {
  background: rgba(255,200,0,0.08);
  border-left-color: var(--warning);
}
.insight.warning-bg strong { color: var(--warning); }
```

### Footer Kin

```html
<footer class="kin-footer">
  <span>Kin Analytics◆ &middot; Let knowledge in.</span>
  <span>{MARKET} · Churn × Mobility Analysis · {DATE}</span>
  <span>KinAnalytics.com</span>
</footer>
```

```css
.kin-footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border);
  padding: 12px 32px;
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
  font-size: 11px; color: var(--text-muted);
  font-family: var(--font-body);
}
```

### Override para tema claro (reportes para impresión/PDF)

```css
:root {
  --bg-primary:   #FFFFFF;
  --bg-secondary: #EFEFEE;
  --bg-card:      #FFFFFF;
  --text-primary: #141417;
  --text-muted:   #999EA6;
  --border:       #D4D5D6;
}
.kin-header { background: #141417; color: #FFFFFF; border-bottom: 3px solid #E5FF01; }
```

---

## Paso 1: Columnas requeridas del CSV de entrada

El CSV final tiene este esquema (generado por `Churn_Mobility_Dataframe.ipynb`):

| Columna                   | Tipo    | Descripción                                             |
|---------------------------|---------|---------------------------------------------------------|
| `pos_id`                  | int     | ID del punto de venta                                   |
| `pos_h3_cell`             | str     | Celda H3 del POS                                        |
| `pos_subchannel`          | str     | Sub-canal (e.g. Mom & Pop, House Sales)                 |
| `pos_zone`                | str     | Zona territorial                                        |
| `pos_size_classification` | str     | GRANDE / MUY GRANDE                                     |
| `pos_latitude`            | float   | Latitud GPS                                             |
| `pos_longitude`           | float   | Longitud GPS                                            |
| `pos_last_purchase_date`  | str/date| Fecha de última compra                                  |
| `pos_buyd_segment`        | str     | Segmento (e.g. Churned)                                 |
| `pos_churn_type`          | str     | Tipo de churn                                           |
| `churn_month`             | int     | Mes del churn (1–12)                                    |
| `avg_devices_pre`         | float   | Promedio dispositivos distintos pre-churn (NaN=sin dato)|
| `avg_dwell_pre`           | float   | Promedio dwell minutos pre-churn (NaN=sin dato)         |
| `pct_change_devices`      | float   | % cambio movilidad (NaN si sin dato)                    |
| `slope_devices`           | float   | Slope lineal de la tendencia de movilidad               |
| `n_months_obs`            | int     | Número de meses observados (0=sin dato)                 |
| `churn_reason`            | str     | `drop_in_mobility_XX%` / `no_mobility_signal` / `no_mobility_data` |

⚠️ **IMPORTANTE**: Las columnas usan prefijo `pos_` (`pos_subchannel`, `pos_zone`).
El código original del HTML usaba nombres sin prefijo (`subcanal`, `territorio`).
Este skill siempre usa los nombres con prefijo tal como salen del CSV.

---

## Paso 2: Parámetros de configuración

```python
DROP_THRESHOLD_HEAVY = 15   # % caída → "churn impulsado por movilidad"
DROP_THRESHOLD_LIGHT = 5    # % caída → etiquetado en churn_reason
H3_RESOLUTION        = 9    # resolución H3 usada en el pipeline
PRE_CHURN_MONTHS     = 6    # meses de ventana pre-churn
```

---

## Paso 3: Recomputar mob_drop (no está en el CSV final)

```python
df = pd.read_csv(csv_path)
df['pos_last_purchase_date'] = pd.to_datetime(df['pos_last_purchase_date'])

df_mob = df[df['avg_devices_pre'].notna()].copy()
df_mob['mob_drop']       = df_mob['pct_change_devices'] < -DROP_THRESHOLD_HEAVY
df_mob['mob_drop_light'] = df_mob['pct_change_devices'] < -DROP_THRESHOLD_LIGHT

total    = len(df)
with_mob = len(df_mob)
coverage = round(with_mob / total * 100, 1)
```

---

## Paso 4: Calcular chart_data

### 4a. Summary KPIs
```python
summary = {
    "total_churn"   : total,
    "with_mobility" : with_mob,
    "mob_drop_15"   : int(df_mob["mob_drop"].sum()),
    "mob_drop_5"    : int(df_mob["mob_drop_light"].sum()),
    "avg_change"    : round(float(df_mob["pct_change_devices"].mean()), 1),
    "median_change" : round(float(df_mob["pct_change_devices"].median()), 1),
    "pct_rising"    : round((df_mob["pct_change_devices"] > 0).mean() * 100, 1),
    "pct_drop_5"    : round(df_mob["mob_drop_light"].mean() * 100, 1),
    "pct_drop_15"   : round(df_mob["mob_drop"].mean() * 100, 1),
    "date_min"      : str(df['pos_last_purchase_date'].min())[:10],
    "date_max"      : str(df['pos_last_purchase_date'].max())[:10],
}
```

### 4b. Histograma
```python
hist_vals = df_mob["pct_change_devices"].clip(-100, 150)
hist_counts, hist_edges = np.histogram(hist_vals, bins=40)
hist_centers = [(hist_edges[i] + hist_edges[i+1]) / 2 for i in range(len(hist_edges)-1)]
# Colores Kin: rojo para caída, amarillo para estable/alza
hist_colors = ["#FF5555" if c < -DROP_THRESHOLD_LIGHT else "#E5FF01" for c in hist_centers]
```

### 4c. Mensual
```python
MONTH_LABEL = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
               7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
monthly = df.groupby("churn_month").agg(churn_count=("pos_id","count")).reset_index()
monthly_mob = (
    df_mob.groupby("churn_month")
    .agg(avg_mob_change=("pct_change_devices","mean"),
         pct_mob_drop  =("mob_drop","mean"))
    .reset_index()
)
monthly = monthly.merge(monthly_mob, on="churn_month", how="left")
monthly["month_label"] = monthly["churn_month"].map(MONTH_LABEL)
```

### 4d. Sub-canal (Top 10 por volumen)
```python
subcanal = (
    df_mob.groupby("pos_subchannel")
    .agg(n=("pos_id","count"),
         mob_drop_rate=("mob_drop","mean"),
         avg_change   =("pct_change_devices","mean"))
    .reset_index()
    .sort_values("n", ascending=False)
    .head(10)
    .rename(columns={"pos_subchannel":"subcanal"})
)
```

### 4e. Territorio
```python
territorio = (
    df_mob.groupby("pos_zone")
    .agg(n=("pos_id","count"),
         mob_drop_rate=("mob_drop","mean"),
         avg_change   =("pct_change_devices","mean"))
    .reset_index()
    .sort_values("n", ascending=False)
    .rename(columns={"pos_zone":"territorio"})
)
```

### 4f. Tipo de churn
```python
churn_type = (
    df_mob.groupby("pos_churn_type")
    .agg(n=("pos_id","count"),
         mob_drop_rate=("mob_drop","mean"),
         avg_change   =("pct_change_devices","mean"))
    .reset_index()
    .sort_values("n", ascending=False)
)
```

### 4g. Scatter + Top 5 casos
```python
scatter_sample = df_mob.sample(min(600, len(df_mob)), random_state=42)
scatter = scatter_sample[["pct_change_devices","slope_devices","avg_devices_pre",
    "mob_drop","pos_subchannel"]].rename(columns={"pos_subchannel":"subcanal"}).to_dict("records")

top_drops = df_mob.nsmallest(5, "pct_change_devices")
case_studies = [{
    "pos_id"     : str(row["pos_id"]),
    "subcanal"   : str(row["pos_subchannel"]),
    "territorio" : str(row["pos_zone"]),
    "churn_date" : str(row["pos_last_purchase_date"])[:7],
    "pct_change" : round(float(row["pct_change_devices"]), 1),
    "avg_devices": round(float(row["avg_devices_pre"]), 1),
    "churn_type" : str(row["pos_churn_type"]),
    "n_months"   : int(row["n_months_obs"]),
} for _, row in top_drops.iterrows()]
```

### Ensamblado final + escape seguro
```python
chart_data = {
    "hist": {"centers":[round(c,2) for c in hist_centers],
             "counts":hist_counts.tolist(),"colors":hist_colors},
    "monthly": monthly.to_dict("records"),
    "subcanal": subcanal.to_dict("records"),
    "territorio": territorio.to_dict("records"),
    "churn_type": churn_type.to_dict("records"),
    "scatter": scatter,
    "case_studies": case_studies,
    "summary": summary,
}
# ⚠️ CRÍTICO: escapar </script> para que no rompa el HTML
DATA_JSON = json.dumps(chart_data, default=str).replace("</", "<\\/")
```

---

## Paso 5: Estructura de secciones del HTML

| Sección      | Componentes                                                 |
|--------------|-------------------------------------------------------------|
| Header Kin   | Logo◆ + título report + metadata + border-bottom yellow     |
| KPI Row      | 5 cards: total, con movilidad, drop>15%, drop>5%, avg_change|
| Sección 1    | Histograma + Scatter (distribución cambio %)                |
| Sección 2    | Barra mensual + Línea mensual                               |
| Sección 3    | Dual-axis subcanal + dual-axis zona + barra churn_type      |
| Sección 4    | Top 5 casos (stat cards, sin mini-charts — CSV no tiene mob_monthly) |
| Sección 5    | Tabla territorial completa                                  |
| Sección 6    | Metodología (texto)                                         |
| Footer Kin   | Kin Analytics◆ · Let knowledge in · KinAnalytics.com        |

---

## Errores comunes y soluciones

### ❌ Columnas sin prefijo `pos_` (subcanal, territorio)
**Causa**: El código original usaba nombres sin prefijo.
**Solución**: Usar `.rename(columns={"pos_subchannel":"subcanal", "pos_zone":"territorio"})`.

### ❌ mob_drop / mob_drop_light no están en el CSV
**Causa**: Son columnas intermedias del pipeline que no se exportan.
**Solución**: Recomputar desde `pct_change_devices` (ver Paso 3).

### ❌ KPI de cobertura hardcodeado o incorrecto
**Solución**: `coverage = round(len(df_mob) / len(df) * 100, 1)` — siempre dinámico.

### ❌ Insight de movilidad invertido
**Causa**: Insight hardcodeado no refleja los datos reales.
**Solución**: Usar `summary["pct_rising"]` y `summary["pct_drop_15"]` dinámicos.

### ❌ `</script>` en DATA_JSON rompe el HTML
**Solución**: `DATA_JSON.replace("</", "<\\/")` antes de inyectar.

### ❌ Mercado incorrecto en header
**Causa**: Header puede decir "Colombia" para datos de México.
**Solución**: Inferir del config del notebook o pedir al usuario.

### ❌ Texto blanco sobre KIN Yellow
**Causa**: Violación de brand — el yellow es muy brillante para texto blanco.
**Solución**: Sobre fondos `#E5FF01` usar SIEMPRE texto `#141417` (negro).

---

## Variables que deben ajustarse por mercado

| Variable              | México                       | Nicaragua / Venezuela / Colombia |
|-----------------------|------------------------------|----------------------------------|
| Nombre en header      | "FEMSA Mexico"               | Ajustar por cliente              |
| `MONTH_LABEL`         | Español (Ene, Feb…)          | Mismo                            |
| `H3_RESOLUTION`       | 9                            | Verificar resolución del archivo |
| `PRE_CHURN_MONTHS`    | 6                            | Puede variar según cobertura     |
| `DROP_THRESHOLD_HEAVY`| 15%                          | Ajustar según distribución local |
| Zonas en header       | Bajio, Centro-Pacifico…      | Zonas del país                   |

---

## Salidas

| Archivo                                        | Descripción                  |
|------------------------------------------------|------------------------------|
| `Churn_Mobility_Report_{MARKET}_{DATE}.html`   | Informe HTML Kin autocontenido |

El HTML requiere solo Chart.js desde CDN y Google Fonts.
Para entornos sin internet: descargar ambos y embeber inline.
