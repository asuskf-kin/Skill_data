---
name: customer-potential
description: >
  Genera presentaciones de Customer Potential (Ultrasegmentación) para embotelladores
  de la red Coca-Cola. Úsalo SIEMPRE que el usuario quiera crear o actualizar una
  presentación de resultados de Customer Potential / Ultrasegmentación a partir de
  un CSV de segmentación. Activa cuando mencione "customer potential", "ultrasegmentación",
  "presentación de potencial", "resultados de segmentación", "kpi_presentaciones",
  o cuando suba un CSV con columnas como PotentialQualitative_, PotentialQuantitative_,
  PotentialQuantitativeFinal_, pos_subchannel, pos_city, junto a un PPTX template.
---

# Customer Potential Presentation Skill

Genera una presentación branded Kin Analytics de resultados de Customer Potential
(Ultrasegmentación), partiendo de la plantilla Uruguay y un CSV de segmentación.

**Before starting:** Read `references/kpi-logic.md` for computation details and
`references/slide-mapping.md` for per-slide XML replacement guide.

---

## Step 1 — Intake (preguntas obligatorias)

Haz estas preguntas antes de empezar. No asumas respuestas.

```
1. ¿Para qué País y Embotelladora es la presentación?
   (ej. "Uruguay - Femsa", "México - Bepensa")

2. ¿Mes y año de la presentación?
   (ej. "Junio 2026")

3. ¿Quién entregó la base de clientes y en qué fecha?
   → Ejemplo: "Embotelladora – Jun 2026" (se pone tal cual en el slide 4)

4. ¿La fuente de datos de ventas y en qué fecha?

   Usar el selector interactivo:
   ```
   ask_user_input_v0(questions=[{
     "question": "¿De dónde vienen los datos de ventas?",
     "options": ["Embotelladora", "Sistema NSR"],
     "type": "single_select"
   }])
   ```
   Luego preguntar la fecha: "¿En qué mes/año están los datos? (ej. Jun 2026)"
   El valor final se combina: `"Embotelladora – Jun 2026"` o `"Sistema NSR – Jun 2026"`

5. ¿Es una corrida Tradicional o Custom?

   Usar el selector interactivo:
   ```
   ask_user_input_v0(questions=[{
     "question": "¿Es una corrida Tradicional o Custom?",
     "options": ["Tradicional", "Custom"],
     "type": "single_select"
   }])
   ```
   - **Tradicional**: usa TotalPortafolio + GlobalCat_CocaCola + GlobalCat_SparklingFlavors
                  + ServingType_SingleServe
   - **Custom**: el usuario especifica categorías (ej. "Stills", "Sparkling") → se mapean
             como CustomCat_Stills, CustomCat_Sparkling, etc.

6. Si es Custom: ¿Cuáles son los nombres de las categorías custom?
   (Máximo 3 para que quepan en slide 8; si son más, acordar qué mostrar)
   Nota: TotalPortafolio SIEMPRE está en embudos (slide 13) y tablas top5 (slides 9/10),
   pero en slide 8 SOLO se muestran las categorías custom.

7. ¿En qué idioma quieres los resultados?

   Usar el selector interactivo:
   ```
   ask_user_input_v0(questions=[{
     "question": "¿En qué idioma quieres los resultados de la presentación?",
     "options": ["Español", "English", "Português"],
     "type": "single_select"
   }])
   ```
   Mapeo de respuesta → código:
   - "Español"   → `lang = "es"`
   - "English"   → `lang = "en"`
   - "Português" → `lang = "pt"`

   El idioma afecta todo el texto generado: narrativas de slides, títulos y explicaciones
   de la sección de Giro, insights, labels de gráficas, y textos de los embudos.
   Los slides base del template (texto fijo en XML) no cambian.
```

Store responses as:
```
metadata = {
  "pais": ..., "embotelladora": ..., "mes": ..., "anio": ...,
  "fuente_clientes": "Embotelladora – Jun 2026",
  "fuente_ventas":   "Sistema NSR – Jun 2026",
  "run_type": "traditional" | "custom",
  "custom_cats": [...] if custom else [],
  "email_presentador": "nombre@kinanalytics.com",
  "lang": "es" | "en" | "pt"
}
```

---

## Step 2 — Load files

1. **Template PPTX:** `Femsa_Uruguay_Resultados_Ultrasegmentación_202605__1_.pptx`
   (or the file the user uploads — always use the provided template)

2. **CSV:** ask the user for the path or wait for upload.
   Typical name pattern: `cp_<operation>_<date>.csv`

Confirm both files are available before proceeding.

---

## Step 3 — Compute KPIs

```bash
pip install pandas numpy --quiet 2>/dev/null

python customer-potential/scripts/compute_kpis.py \
    --csv <path_to_csv> \
    --run-type <traditional|custom> \
    [--custom-cats Cat1 Cat2 Cat3] \
    --output /home/claude/kpis.json
```

Verify output:
```bash
python3 -c "import json; d=json.load(open('/home/claude/kpis.json')); print('Embudos:', len(d['embudos'])); print('S7 rows:', len(d['s7']['rows']))"
```

If errors, read `references/kpi-logic.md` and debug the relevant computation.

---

## Step 4 — Build presentation

### 4a. Unpack template
```bash
cp <template_path> /home/claude/work_template.pptx
python /mnt/skills/public/pptx/scripts/office/unpack.py /home/claude/work_template.pptx /home/claude/unpacked/
```

### 4b. Handle embudo slides (Custom mode only)
If custom mode has more or fewer categories than 4 total embudos (TotalPortafolio + custom cats):

**More than 4 embudos:** Duplicate slide13.xml for each extra category:
```bash
python /mnt/skills/public/pptx/scripts/add_slide.py /home/claude/unpacked/ slide13.xml
# → Returns <p:sldId> — insert it into ppt/presentation.xml after slide16's entry
```

**Fewer than 4 embudos:** Remove excess slides from `<p:sldIdLst>` in `ppt/presentation.xml`.

### 4c. Apply all KPI replacements (automated)

Use `apply_kpis.py` — encodes all slide patterns learned from the Uruguay template:

```bash
python customer-potential/scripts/apply_kpis.py \
    --kpis /home/claude/kpis.json \
    --unpacked /home/claude/unpacked/ \
    --pais "{pais}" \
    --embotelladora "{embotelladora}" \
    --mes "{mes}" \
    --anio "{anio}" \
    --fuente-clientes "{fuente_clientes}" \
    --fuente-ventas "{fuente_ventas}" \
    --email "{email_presentador}"
```

The script applies slides 1, 4, 7, 8, 9, 10, 11, 13–16, 18 automatically.
Warnings (`⚠`) indicate values not found — investigate and fix manually if any appear.

**Slide 4 — formato de fecha por fuente:**
Las fuentes de clientes y ventas incluyen la fecha en el mismo campo. El formato exacto es:
- Fuente clientes → entre paréntesis: `(Embotelladora – Jun 2026)`
- Fuente ventas → sin paréntesis: `Sistema NSR – Jun 2026`

Ejemplo de intake: preguntar "¿fuente y fecha?" → respuesta "Embotelladora – Jun 2026"
El valor se inserta tal cual reemplazando `(Embotelladora)` y `Embotelladora` en slide4.xml.

**Key patterns encoded in apply_kpis.py:**
- Slide 7: volume suffix is embedded in text `"k) del total del potencial..."` (not a separate element)
- Slide 8: VH/High aporte includes `%` in same `<a:t>` (`55.84%`); Total CocaCola ventas is `"560 k"` (combined)
- Slides 9/10: subchannel/city names replaced with `replace()` — ALL occurrences — because same name appears in both narrative and table
- Slides 13–16: n2_pct split pattern varies by slide (split digits vs combined string); documented in `EMBUDO_ORIG` dict inside script
- Slide 14 "Clientes segmentados": uses `xml:space="preserve"` with trailing space

#### Slide 11 — Map image ⚠️
The **text** (city names, POS counts, growth %) se actualiza automáticamente desde `s11`.
La **imagen del mapa** (el heat map de territorios coloreados) NO se puede actualizar
programáticamente — requiere generación manual con Kepler.gl o herramienta similar.

**Avisar siempre al usuario al entregar:**
> "⚠️ El mapa del slide 11 requiere actualización manual. Hay que generar la imagen en
> Kepler.gl con los datos de {ciudad1} y {ciudad2} y reemplazarla en la diapositiva."

#### Slide 18 (`slide18.xml`) — Contactos
Agregar el email del presentador después de `nicolas.ayala@@kinanalytics.com`.
Insertar un nuevo `<a:p>` con el mismo formato que los emails existentes:

```xml
<a:p>
  <a:pPr marL="0" marR="0" lvl="0" indent="0" algn="l" rtl="0">
    <a:lnSpc><a:spcPct val="80000"/></a:lnSpc>
    <a:spcBef><a:spcPts val="0"/></a:spcBef>
    <a:spcAft><a:spcPts val="0"/></a:spcAft>
    <a:buClr><a:schemeClr val="dk1"/></a:buClr>
    <a:buSzPts val="1400"/>
    <a:buFont typeface="Arial"/>
    <a:buNone/>
  </a:pPr>
  <a:r>
    <a:rPr lang="es-ES" sz="1400" b="0" i="0" u="sng" strike="noStrike" cap="none">
      <a:solidFill><a:schemeClr val="hlink"/></a:solidFill>
      <a:latin typeface="Albert Sans"/>
      <a:ea typeface="Albert Sans"/>
      <a:cs typeface="Albert Sans"/>
      <a:sym typeface="Albert Sans"/>
    </a:rPr>
    <a:t>{email_presentador}</a:t>
  </a:r>
  <a:endParaRPr sz="1400" b="0" i="0" u="none" strike="noStrike" cap="none">
    <a:solidFill><a:schemeClr val="dk1"/></a:solidFill>
    <a:latin typeface="Albert Sans"/>
    <a:ea typeface="Albert Sans"/>
    <a:cs typeface="Albert Sans"/>
    <a:sym typeface="Albert Sans"/>
  </a:endParaRPr>
</a:p>
```

Usar `str_replace` para insertar este bloque inmediatamente después del `</a:p>` que cierra
el párrafo de nicolas.ayala (el que termina con `<a:t>m</a:t>`).
Locate anchor: `<a:t>m</a:t>\n            </a:r>\n            <a:endParaRPr`

### 4d. Clean and pack
```bash
python /mnt/skills/public/pptx/scripts/clean.py /home/claude/unpacked/

python /mnt/skills/public/pptx/scripts/office/pack.py \
    /home/claude/unpacked/ \
    /home/claude/standard.pptx \
    --original /home/claude/work_template.pptx
```

### 4e. Add Giro de Negocio section

First compute giro KPIs, then append the section to the packed PPTX:

```bash
# Compute giro KPIs (separate from standard KPIs)
python customer-potential/scripts/compute_kpis.py \
    --csv <path_to_csv> \
    --run-type <traditional|custom> \
    --output /home/claude/kpis_giro.json
# (same CSV, output a separate file for giro)

# Note: giro KPIs need pos_subchannel grouping — this is computed separately
# Run the inline Python giro computation (see kpi-logic.md §Giro section)

# Add section slides
python customer-potential/scripts/giro_section.py \
    --pptx /home/claude/standard.pptx \
    --giro-kpis /home/claude/kpis_giro.json \
    --output /home/claude/output.pptx \
    --lang {lang} \
    --start-image-idx 40
```

**`--lang`**: `es` | `en` | `pt` — translates ALL generated text:
titles, column headers, insight bullets, explanation strips, chart axis labels, quadrant labels.

**`--start-image-idx 40`**: critical — uses image40.png, image41.png... for new charts.
⚠️ Never use indices < 40 as they may conflict with the template's original media files.

**Translations**: `scripts/translations.py` — add new languages by adding a new key block.
The section divider in this template uses "Brecha de Capitalización" (ES), "Capitalization Gap" (EN),
"Brecha de Capitalização" (PT) — update `giro_divider_title` in translations.py if needed.

---

## Step 5 — QA

### Content QA
```bash
extract-text /home/claude/output.pptx
```

Check that:
- Old values (Femsa, Uruguay, Mayo 2026, 15,932, 797) are replaced
- New values from kpis.json appear correctly
- No leftover placeholder text

```bash
extract-text /home/claude/output.pptx | grep -iE "Femsa|Uruguay|15,932|797"
```

### Visual QA
```bash
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless --convert-to pdf /home/claude/output.pptx
rm -f /home/claude/slide-*.jpg
pdftoppm -jpeg -r 150 /home/claude/output.pdf /home/claude/slide
ls -1 "$PWD"/home/claude/slide-*.jpg
```

Visually inspect key slides: 1, 4, 7, 8, 13, 14.

---

## Slide inventory

| Slide | Content | Dynamic? | Source |
|-------|---------|----------|--------|
| 1 | Cover | ✅ | metadata |
| 2 | Objetivo del proyecto | ❌ static | — |
| 3 | De Clustering a Segmentación | ❌ static | — |
| 4 | Resumen del proceso | ✅ | metadata |
| 5 | Resumen proceso (detalle) | ❌ static | — |
| 6 | Section: Resultados | ❌ static | — |
| 7 | TotalPortafolio table | ✅ | s7 |
| 8 | Multi-cat table | ✅ | s8 |
| 9 | Top 5 subchannel | ✅ | s9 |
| 10 | Top 5 city | ✅ | s10 |
| 11 | Map + city text (texto auto, imagen manual) | ⚠️ parcial | s11 |
| 12 | Section: Prioridades | ❌ static | — |
| 13 | Embudo TotalPortafolio | ✅ | embudos[0] |
| 14 | Embudo Cat2 (Colas / Custom1) | ✅ | embudos[1] |
| 15 | Embudo Cat3 (Flavors / Custom2) | ✅ | embudos[2] |
| 16 | Embudo Cat4 (SingleServe / Custom3) | ✅ | embudos[3] |
| 17 | Siguientes pasos | ❌ static | — |
| 18 | Contactos (añadir email presentador) | ✅ | metadata |

---

## Custom mode specifics

When `run_type == "custom"`:

1. **Column names:** `CustomCat_<Nombre>` (exactamente como lo especificó el usuario, case-sensitive)

2. **Slide 8 — SOLO custom categories** (sin TotalPortafolio):
   - Reemplazar "Coca Cola", "Sparkling Flavors", "Single Serve" con los nombres custom
   - `compute_kpis.py` ya pasa `sufijos_cat` (solo custom) a `compute_slide8`, así que `kpis.json` ya tiene los valores correctos

3. **Slides 9/10 columnas:** TotalPortafolio + custom cats (slide top5 siempre incluye Total como primera columna)
   - Reemplazar headers: `(Coca Cola)`, `(Sparkling Flavors)`, `(Single Serve)` con custom category names

4. **Embudo slide titles:** `Ultrasegmentación <nombre_custom>` (ej. "Ultrasegmentación Stills")
   - Slide 13 siempre = TotalPortafolio
   - Slides 14+ = una por cada custom category

5. **Slide count:** Ajustar embudos 14–N al número de custom categories

Si `custom_cats` tiene 1–2 items: eliminar slides de embudo sobrantes y columnas en slide 8.
Si `custom_cats` tiene 4+ items:
- Slide 8 solo puede mostrar 3 → confirmar con usuario cuáles 3 mostrar
- Agregar slides extra de embudo con `add_slide.py`

---

## Naming the output file

```
{Embotelladora}_{Pais}_Resultados_Ultrasegmentacion_{YYYYMM}.pptx
```

Example: `Femsa_Uruguay_Resultados_Ultrasegmentacion_202605.pptx`

```bash
cp /home/claude/output.pptx "/mnt/user-data/outputs/Femsa_Uruguay_Resultados_Ultrasegmentacion_202605.pptx"
```
