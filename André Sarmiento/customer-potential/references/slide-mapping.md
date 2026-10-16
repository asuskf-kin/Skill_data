# Slide Mapping — Customer Potential Presentation

This guide documents exactly which `<a:t>` text elements to replace in each dynamic slide.
Use `str_replace` on each slide's XML file after unpacking.

> **Key principle:** Many numeric values are split across multiple `<a:t>` elements
> (e.g., `<a:t>81</a:t>` followed by `<a:t>% del volumen...</a:t>`).
> Always search for the surrounding context to locate the right element.

---

## Slides that are STATIC (do not modify)

- **Slide 2** — Objetivo / Impacto esperado
- **Slide 3** — De Clustering a Segmentación de Potencial
- **Slide 5** — Resumen del proceso (detalle)
- **Slide 6** — Section divider "Resultados de potencial por categoría"
- **Slide 12** — Section divider "Prioridades"
- **Slide 17** — Siguientes pasos

---

## Slide 1 — Cover

Dynamic elements in `slide1.xml`:

| Target `<a:t>` value | Replace with | From |
|---------------------|-------------|------|
| `Femsa` | `{embotelladora}` | metadata |
| `Uruguay` | `{pais}` | metadata |
| `Mayo ` | `{mes} ` (keep trailing space) | metadata |
| `2026` (in "Mayo 2026" paragraph) | `{anio}` | metadata |

> The `©2026` in the footer contains the same year — only replace the one in the "Femsa - Uruguay / Mayo 2026" block. Use surrounding context to distinguish.

---

## Slide 4 — Resumen del proceso (fuentes de datos)

Hay dos fuentes de datos distintas — **preguntar por separado** en el intake:

| Target context | Target `<a:t>` value | Replace with |
|----------------|---------------------|-------------|
| Near "Datos de clientes" | `Femsa Uruguay` (1st occurrence) | `{embotelladora} {pais}` |
| Near "Datos de clientes" | `(Embotelladora)` (with parens) | stays = `{fuente_clientes}` shown in parens |
| Near "Datos de Ventas" | `Femsa Uruguay` (2nd occurrence) | `{embotelladora} {pais}` |
| Near "Datos de Ventas" | `Embotelladora` (no parens, standalone) | `{fuente_ventas}` |

> The two `Femsa Uruguay` occurrences are identical in XML context — use `replace(old, new, 1)` twice sequentially to target first then second.
> `fuente_clientes` default = "Embotelladora"; `fuente_ventas` = "Embotelladora" or "Sistema NSR".

---

## Slide 7 — Total Portafolio table

**Narrative text** — confirmed element structure from template analysis:

| Target `<a:t>` | Replace with | Notes |
|----------------|-------------|-------|
| `20` | `{s7.nar_pct_clientes}` | % clients in VH+H |
| `3` | `{s7.nar_k_clientes}` | ~k clients in VH+H |
| `81` | `{s7.nar_pct_vol_total}` | % vol in VH+H |
| `55` | `{s7.nar_vh_pct}` | VH % of total growth |
| `141` | `{s7.nar_vh_vol_num}` | VH growth volume number |
| `k) del total del potencial de crecimiento del portafolio (` | `{s7.nar_vh_vol_suf}) del total del potencial de crecimiento del portafolio (` | ⚠️ suffix is EMBEDDED in this text element — not a separate `<a:t>` |
| `255k` | `{s7.nar_total_vol}` | total growth volume |

**Table rows** — VH/High/Moderate/Low each as `pos_n` | `prom_ventas` | `aporte_pct`:

| Uruguay template value | Replace with |
|------------------------|-------------|
| `797` | `{s7.rows[0].pos_n}` |
| `516k` | `{s7.rows[0].prom_ventas}` |
| `55.44` | `{s7.rows[0].aporte_pct}` |
| `2,390` | `{s7.rows[1].pos_n}` |
| `437k` | `{s7.rows[1].prom_ventas}` |
| `25.85` | `{s7.rows[1].aporte_pct}` |
| `4,779` | `{s7.rows[2].pos_n}` |
| `369k` | `{s7.rows[2].prom_ventas}` |
| `14.87` | `{s7.rows[2].aporte_pct}` |
| `7,966` | `{s7.rows[3].pos_n}` |
| `1.4M` | `{s7.rows[3].prom_ventas}` |
| `3.84` | `{s7.rows[3].aporte_pct}` |
| `15,932` | `{s7.rows[4].pos_n}` |
| `2.7` | `{s7.rows[4].prom_ventas_num}` (Total ventas number part) |

---

## Slide 8 — Multi-category table

> ⚠️ **% FORMAT IS DIFFERENT PER ROW:**
> - VH and High rows: aporte `%` is included in the same `<a:t>` → `<a:t>55.84%</a:t>`
> - Total row: aporte is split → `<a:t>81.89</a:t>` + `<a:t>%</a:t>`
> - CocaCola Total ventas: `"560 k"` is ONE combined element (not split)
> - SparklingFlavors/SingleServe Total ventas: check actual XML — format may vary

**Column headers** (only if custom mode — traditional keeps Coca Cola / Sparkling Flavors / Single Serve).

**Data cells** (Uruguay template values to target):

| Row | Cat | pos_n | prom_ventas | aporte |
|-----|-----|-------|-------------|--------|
| VH | Coca Cola | `796` | `299.1 k` | `55.84%` (combined) |
| VH | Sparkling Flavors | `791` | `111.9 k` | `54.15%` (combined) |
| VH | Single Serve | `795` | `81.6 k` | `51.71%` (combined) |
| High | Coca Cola | `2,385` | `261.1 k` | `26.06%` (combined) |
| High | Sparkling Flavors | `2,371` | `92.7 k` | `26.31%` (combined) |
| High | Single Serve | `2,382` | `77.6 k` | `28.16%` (combined) |
| Total | Coca Cola | `3,181` | `560 k` (combined) | `81.89` + `%` (split) |
| Total | Sparkling Flavors | `3,162` | `205` | `80.46` + `%` (split) |
| Total | Single Serve | `3,177` | `159 k` | `79.87` + `%` (split) |

**Narrative:**
| Uruguay text | Replace with |
|-------------|-------------|
| `55.84` (in `"con 55.84% en Very High"`) | `{s8.nar_best_pct}` — separate element, NO `%` |
| `"seguido por Sparkling Flavors con 54.15%"` | `"seguido por {s8.nar_second_cat} con {s8.nar_second_pct}%"` — full string in one element |

---

## Slide 9 — Subchannel Top 5

> ⚠️ **USE `replace()` WITHOUT COUNT LIMIT for subchannel names** — the same name appears in both the narrative text and the table rows. Using `replace(old, new, 1)` will only hit the narrative (which appears first in the XML) and leave the table unchanged.

**Uruguay template names to replace (all occurrences):**
`AUTOSERVICIOS`, `ALMACENES`, `PANADERÍAS`, `MAXIKIOSCOS`, `ALMACENES MAYORISTAS`

**Uruguay template PDV[n] to replace (first occurrence each):**
`1,635`, `8,224`, `1,254`, `1,158`, `66`, `3,595`, `15,932`

**Aporte % to replace (first occurrence each):**
`44.26%`, `44.30%`, `44.40%`, `36.34%`, `34.57%`, `34.26%`, `36.59%`, `27.58%`,
`4.87%`, `5.17%`, `4.92%`, `9.47%`, `3.56%`, `3.69%`, `3.18%`, `7.54%`,
`3.43%`, `3.62%`, `2.37%`, `3.86%`, `9.32%`, `8.97%`, `8.55%`, `15.21%`

## Slide 10 — City Top 5

Same rules as Slide 9. Replace ALL occurrences of city names.

**Uruguay template city names to replace (all occurrences):**
`MONTEVIDEO`, `CANELONES`, `MALDONADO`, `SALTO`, `SAN JOSÉ`

**Uruguay template PDV[n]:** `5,019`, `2,676`, `1,094`, `894`, `518`, `5,731`, `15,932`

**Aporte %:**
`43.22%`, `43.06%`, `38.75%`, `50.02%`, `22.10%`, `22.90%`, `21.63%`, `21.83%`,
`6.57%`, `6.93%`, `7.53%`, `6.80%`, `4.98%`, `5.01%`, `4.53%`, `3.34%`,
`3.86%`, `3.87%`, `4.38%`, `2.66%`, `19.26%`, `18.24%`, `23.18%`, `15.30%`

---

## Slide 11 — Map text

| Target fragment | Replace with |
|----------------|-------------|
| `Departamento de Montevideo y Canelone` | `Departamento de {s11.city1.ciudad} y {s11.city2.ciudad}` |
| `5,019` (POS count city1) | `{s11.city1.pos_n}` |
| `Montevideo ` (in narrative) | `{s11.city1.ciudad} ` |
| `22` (% growth city1) | `{s11.city1.pct_crecimiento}` |
| `Canelones ` (in narrative) | `{s11.city2.ciudad} ` |
| `2,676 ` (POS count city2) | `{s11.city2.pos_n} ` |
| `21` (% growth city2) | `{s11.city2.pct_crecimiento}` |
| `Montevideo` (map label) | `{s11.city1.ciudad}` |
| `Canelones` (map label) | `{s11.city2.ciudad}` |

> ⚠️ **MAP IMAGE — REQUIERE ACCIÓN MANUAL:**
> La imagen del mapa (heat map de territorios coloreados) **no se puede actualizar
> automáticamente**. Al entregar la presentación, avisar al usuario:
>
> *"El slide 11 necesita que reemplaces la imagen del mapa manualmente. Genera la
> visualización en Kepler.gl con los datos geoespaciales de {city1} y {city2} y
> pégala en la diapositiva reemplazando la imagen actual."*

---

## Slide 18 — Contactos

**Agregar** el email del presentador después del párrafo de `nicolas.ayala`.
El email de Nicolas está partido en 3 `<a:t>` elementos: `nicolas.ayala@` + `@kinanalytics.co` + `m`.

Usar `str_replace` para insertar un nuevo `<a:p>` después del cierre del párrafo de Nicolas.
Anchor para búsqueda:

```xml
              <a:t>m</a:t>
            </a:r>
            <a:endParaRPr sz="1400" b="0" i="0" u="none"
```

Reemplazar ese fragmento con el mismo fragmento **más** el nuevo párrafo a continuación:

```xml
              <a:t>m</a:t>
            </a:r>
            <a:endParaRPr sz="1400" b="0" i="0" u="none" strike="noStrike" cap="none">
              <a:solidFill>
                <a:srgbClr val="222326"/>
              </a:solidFill>
              <a:latin typeface="Albert Sans"/>
              <a:ea typeface="Albert Sans"/>
              <a:cs typeface="Albert Sans"/>
              <a:sym typeface="Albert Sans"/>
            </a:endParaRPr>
          </a:p>
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
              <a:t>NUEVO_EMAIL_AQUI</a:t>
            </a:r>
            <a:endParaRPr sz="1400" b="0" i="0" u="none" strike="noStrike" cap="none">
              <a:solidFill><a:schemeClr val="dk1"/></a:solidFill>
              <a:latin typeface="Albert Sans"/>
              <a:ea typeface="Albert Sans"/>
              <a:cs typeface="Albert Sans"/>
              <a:sym typeface="Albert Sans"/>
            </a:endParaRPr>
          </a:p>
          <a:p>
            <a:pPr marL="0" marR="0" lvl="0" indent="0" algn="l" rtl="0">
              <a:lnSpc><a:spcPct val="80000"/></a:lnSpc>
```

> ⚠️ Reemplaza literalmente `NUEVO_EMAIL_AQUI` con el valor de `metadata.email_presentador`.
> Si el XML de la cerradura ya tiene el `endParaRPr` completo (hay que verlo antes de hacer
> el str_replace), asegúrate de no duplicarlo.

---

## Slides 13–16 — Embudos (one per category)

**Traditional mode:**
- Slide 13 → TotalPortafolio
- Slide 14 → GlobalCat_CocaCola (display: "Colas")
- Slide 15 → GlobalCat_SparklingFlavors (display: "Flavors")
- Slide 16 → ServingType_SingleServe (display: "Single Serve")

> ⚠️ **n2_pct_vol SPLIT PATTERN VARIES BY SLIDE** — confirmed from Uruguay template analysis:
>
> | Slide | n2_pct_vol pattern | n2_pct_com pattern |
> |-------|-------------------|-------------------|
> | 13 | `" concentra el 6"` + `"8"` (two elements, first has leading space) | `"% del volumen y el 1"` + `"5"` |
> | 14 | `"Este subcanal concentra el 6"` + `"8"` | same as 13 |
> | 15 | `"Este subcanal concentra el 70% del volumen y el 1"` (COMBINED, % included) + `"5"` | second digit only |
> | 16 | `" concentra el 51% del volumen y el 1"` (COMBINED) + `"2"` | second digit only |
>
> For slide 16, n3_pct_pos is embedded: `"% del volumen y 8% de los POS"` (single element).
> For slides 13-15, n3_pct_vol and n3_pct_pos are separate standalone `<a:t>` elements.

> ⚠️ **Slide 14 "Clientes segmentados" uses `xml:space="preserve"`** with trailing space:
> `<a:t xml:space="preserve">1500 </a:t>` — must match exactly including the space.

### Per embudo replacement targets (Uruguay template → new value)

| Element | Uruguay 13 | Uruguay 14 | Uruguay 15 | Uruguay 16 | New value |
|---------|-----------|-----------|-----------|-----------|----------|
| Title | `Total Portafolio ` | `Colas ` | `Flavors ` | `Single Serve ` | `{embudo.nombre} ` |
| nar_pct | `81` | `82` | `80` | `80` | `{embudo.nar_pct_vol}` |
| total_cli | `15.9` | `15.9` | `15.9` | `15.9` | `{embudo.total_clientes_num}` |
| cat_label | `Total Portafolio` | `Colas` | `Flavors` | `Single Serve` | `{embudo.nombre}` |
| total_vol | `255 k` | `145` | `52.7` | `45` | `{embudo.total_vol_fmt}` |
| n1_detail | `207.29k UC/mes - 3.2K clientes` | `119.15k...` | `42.4k...` | `35.84M...` | `{embudo.n1_detail}` |
| n2_labels | `ALMACENES y AUTOSERVICIOS ` | same | same | same | `{embudo.n2_labels} ` |
| n2_detail | `173.69k UC/mes - 2.4K clientes` | `99.13k...` | `36.69k...` | `23.08k...` | `{embudo.n2_detail}` |
| n3_labels | `Montevideo y Canelones ` | same | same | same | `{embudo.n3_labels} ` |
| n3_detail | `116.01k UC/mes - 1.5K clientes` | `66.51k...` | `22.58k...` | `17.15k...` | `{embudo.n3_detail}` |
| n3_pct_vol | `45` | `46` | `43` | `38` | `{embudo.n3_pct_vol}` |
| n3_pct_pos | `9` | `9` | `9` | `8%...POS` (embedded) | `{embudo.n3_pct_pos}` |
| n3_vol_num | `116` | `66` | `22.6` | `17.15` | `{embudo.n3_vol_num}` |
| n3_vol_suf | ` K UC/mes` | ` K UC/mes` | ` K UC/mes` | ` K UC/mes` | ` {embudo.n3_vol_suf} UC/mes` |
| n3_pos | `1500` | `1500 ` (preserve) | `1400` | `1300` | `{embudo.n3_pos_fmt}` |

---

## Validation checklist after replacement

Run after packing:
```bash
extract-text output.pptx | grep -i "Femsa\|Uruguay\|Mayo\|15,932\|797"
```
This confirms old values were replaced. Then do visual QA via `soffice` + `pdftoppm`.

Check slide 18 contacts manually to confirm the new email appears correctly.

**Always remind the user about the map image on slide 11:**
> "⚠️ Recuerda actualizar manualmente la imagen del mapa en el slide 11 (Kepler.gl)."
