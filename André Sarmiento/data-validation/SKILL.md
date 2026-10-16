---
name: data-validation
description: >
  Validación de calidad de datos para proyectos de prospección y segmentación de clientes Femsa/Coca-Cola.
  Úsalo SIEMPRE que el usuario suba una base de clientes, productos o ventas y pida validarla, limpiarla,
  revisarla o generar un informe de calidad de datos. También activa cuando el usuario mencione palabras
  como "validar base", "validar datos", "limpieza de datos", "informe de datos", "reporte de calidad",
  "maestra de clientes", "maestra de productos", "base de ventas" o "GeoJSON".
  El skill mapea columnas automáticamente, hace preguntas si no está seguro, ejecuta todas las validaciones
  y genera un reporte Word profesional siguiendo la plantilla Kin Analytics.
---

# Data Validation Skill

## Descripción general

Este skill realiza validaciones de calidad de datos sobre tres tipos de bases:
- **Maestra de Clientes** (con geo-validación contra GeoJSON)
- **Maestra de Productos**
- **Ventas**

Puede recibir cualquier combinación de ellas. El reporte Word **solo se genera cuando hay base de clientes** — para ventas o productos solos, se entregan únicamente los CSVs procesados y un resumen de hallazgos en el chat.

---

## Paso 0 — Seleccionar idioma

**Antes de cualquier otra acción**, preguntar al usuario en qué idioma quiere los resultados:

> *"¿En qué idioma quieres los resultados? / In which language do you want the results? / Em qual idioma você quer os resultados?"*
> - 🇪🇸 Español
> - 🇺🇸 English  
> - 🇧🇷 Português

Guardar la selección como `LANG` = `"es"` | `"en"` | `"pt"`.

Usar este idioma en:
- Todos los mensajes del chat durante el proceso
- El reporte Word (textos, títulos, bullets, tablas, puntos de acción)
- Los insights y hallazgos reportados
- Los mensajes de confirmación de mapeo de columnas

Para generar los textos en el idioma correcto usar: `scripts/translations.py`

---

## Paso 1 — Detectar qué archivos se subieron

El usuario puede subir entre 1 y 4 archivos. Identificar cada uno por extensión y contenido de columnas:

| Tipo | Extensiones aceptadas | Señal de reconocimiento |
|---|---|---|
| Clientes | `.csv`, `.xlsx`, `.parquet` | Tiene columna con "cliente", "pos", "nombre", "coordenada" |
| Productos | `.csv`, `.xlsx`, `.parquet` | Tiene columnas con "product", "marca", "categoria", "brand" |
| Ventas | `.csv`, `.xlsx`, `.parquet` | Tiene columnas con "venta", "unit", "cases", "cajas", "fecha" |
| GeoJSON | `.geojson`, `.json` | Es un archivo GeoJSON (tiene `"type": "FeatureCollection"`) |

**⚠️ REGLA OBLIGATORIA — GeoJSON con Clientes:**
Si el usuario sube una base de clientes y **no incluye un GeoJSON**, seguir este flujo:

1. Identificar el país o territorio de la operación (por nombre del archivo, columna pos_city, o preguntando)
2. Buscar el GeoJSON automáticamente:
   - Usar `web_search` con query: `"{país}" country boundary GeoJSON download github`
   - Intentar `web_fetch` en fuentes confiables: **geoBoundaries**, **Natural Earth**, **GADM**, **github.com/datasets/geo-countries**
   - Si se obtiene, guardar en `/home/claude/{pais}.geojson` y avisar:
     > *"Encontré y descargué el GeoJSON de {País} automáticamente. Continuando con la validación..."*
3. Si la descarga automática falla, pedir al usuario:
   > *"No pude descargar el GeoJSON de {País} automáticamente. ¿Puedes subirlo manualmente? Puedes descargarlo desde https://www.geoboundaries.org o https://gadm.org"*

**No continuar sin GeoJSON.** No es opcional.

---

## Paso 2 — Mapeo de columnas

Lee el script de mapeo para ejecutar esta lógica:
→ **`scripts/column_mapper.py`**

**Reglas del mapeo:**
1. Comparar columnas del archivo con los nombres internos esperados (ver `references/column_catalog.md`)
2. Usar coincidencia exacta primero, luego fuzzy matching (similitud de texto)
3. Para cada columna que no tenga coincidencia exacta, proponer la más probable con una pregunta:

> *"La columna `Cod. Cliente` parece ser `pos_id`. ¿La usamos así?"*

4. Si no encuentra ninguna columna candidata razonable para una columna **obligatoria**, preguntar directamente:

> *"No encontré una columna que parezca ser `pos_latitude`. ¿Cuál columna tiene las coordenadas de latitud?"*

5. Mostrar al usuario el mapeo completo antes de continuar y pedir confirmación.

**Ejemplo de presentación del mapeo:**
```
He identificado el siguiente mapeo de columnas:
✅ Cliente          → pos_id
✅ Nombre del Cliente → pos_name
✅ Nombre Municipio → pos_city
⚠️  Coordenada X    → pos_longitude  ← ¿Correcto?
⚠️  Coordenada Y    → pos_latitude   ← ¿Correcto?
❓ No encontré columna para pos_address — ¿cuál columna tiene la dirección?
```

---

## Paso 2b — Lógica especial: `pos_consumer_type`

Después del mapeo, verificar si `pos_consumer_type` fue encontrada o no:

### Caso A: `pos_consumer_type` existe en el archivo
Usarla directamente. Contiene valores como `ON PREMISE`, `OFF PREMISE`, `MODERNO`, etc.

### Caso B: `pos_consumer_type` NO existe pero `pos_subchannel` SÍ existe
Informar al usuario con este mensaje exacto:

> *"No encontré una columna `pos_consumer_type` (On Premise / Off Premise) en la base. Sin embargo, tengo la columna `pos_subchannel` y puedo construir una clasificación equivalente a partir de ella. La llamaré `pos_consumer_type_internal` para distinguirla de la oficial. ¿Procedo?"*

Si el usuario confirma, ejecutar la derivación usando `scripts/derive_consumer_type.py`.

### Caso C: Ninguna de las dos existe
Avisar al usuario:

> *"No encontré `pos_consumer_type` ni `pos_subchannel`. No será posible mostrar la distribución de Channel Type en el reporte. Puedes continuar sin esta columna."*

Continuar sin bloquear el proceso.

---

## Paso 3 — Ejecutar validaciones

Leer el script correspondiente según las bases recibidas:

| Base | Script |
|---|---|
| Clientes | `scripts/validate_clients.py` |
| Productos | `scripts/validate_products.py` |
| Ventas | `scripts/validate_sales.py` |

Ejecutar los scripts pasando el DataFrame ya renombrado con el mapeo confirmado.

---

## Paso 4 — Generar reporte Word (solo con base de clientes)

**⚠️ REGLA: El reporte Word SOLO se genera si se subió una base de clientes.**

- Si solo hay **ventas** → entregar CSV limpio + resumen de hallazgos en el chat. NO generar Word.
- Si solo hay **productos** → entregar CSV limpio + resumen de hallazgos en el chat. NO generar Word.
- Si hay **clientes** (con o sin ventas/productos) → generar el reporte Word completo.

Cuando aplica, leer instrucciones en: `references/report_template.md`

**La plantilla Word está embebida en el skill** — no es necesario que el usuario la suba.
Siempre usar: `assets/template.docx` como base del reporte.

El flujo correcto es:
1. Copiar `assets/template.docx` a `/home/claude/reporte_output.docx`
2. Abrirla con `python-docx` y editar textos + tablas in-place
3. Guardar y presentar al usuario

Esto preserva el 100% del diseño original: logo Kin Analytics, imágenes de fondo,
tipografía Albert Sans, colores, estilos de headings, header/footer.

El reporte debe:
- Reemplazar todos los valores numéricos y textos con los datos reales calculados
- Actualizar las tablas (filtros, ciudad, subchannel, channel) con los datos reales
- Si hay ventas además de clientes, agregar sección de actividad de ventas
- Guardarse como `.docx` y presentarse al usuario

Para generar el Word, ver `scripts/generate_report.py`.

---

## Paso 5 — Exportar bases procesadas

Al finalizar las validaciones, **siempre exportar** los siguientes archivos y presentarlos al usuario junto con el reporte Word:

### Para cada base recibida:

| Archivo | Contenido | Nombre sugerido |
|---|---|---|
| `clientes_clean_[fecha].csv` | Registros sin ningún problema (df_final) | Base lista para prospección/segmentación |
| `clientes_issues_[fecha].csv` | Registros con problemas + columna `validation_issues` | Para revisión del cliente |
| `productos_clean_[fecha].csv` | Productos validados | Base limpia de productos |
| `ventas_clean_[fecha].csv` | Ventas procesadas | Base limpia de ventas |

La columna `validation_issues` contiene los códigos de problema separados por `;`, por ejemplo:
`outside_geojson;missing_pos_city` o `duplicate_id_drop;zero_coord`

### Códigos de issue posibles (clientes):
| Código | Significado |
|---|---|
| `missing_id` | pos_id vacío |
| `duplicate_id` | pos_id duplicado |
| `duplicate_id_drop` | Eliminado por duplicado de ID (se conservó el más completo) |
| `missing_lat` / `missing_lon` | Coordenada nula |
| `zero_coord` | Lat o lon exactamente en 0 |
| `invalid_coord_range` | Coordenada fuera de rango válido |
| `possible_inverted_range` | Lat/lon probablemente invertidos (por rango) |
| `possible_inverted_distribution` | Lat/lon probablemente invertidos (estadístico) |
| `outside_geojson` | POS fuera del territorio |
| `duplicate_name_coord_drop` | Eliminado por duplicado de nombre+coordenadas |
| `missing_[col]` | Campo vacío en columna específica |

---

## Notas importantes

- La plantilla Word está en `assets/template.docx` — **no pedirla al usuario**
- Pasar siempre `skill_dir` al llamar `generate_report()` para que encuentre la plantilla
- Siempre instalar dependencias que falten con `pip install --break-system-packages`
- Los archivos grandes (>500K filas) cargarlos en batches de 1,000,000 filas
- Las coordenadas enteras (0, 1, 2, 3, 4) son **inválidas** — tratarlas como nulas
- Las longitudes positivas para países de América Latina deben corregirse a negativas
- Los registros con `pos_fecha_baja` **no se eliminan** — se mantienen con flag para prospección
- Al final del proceso exportar: reporte `.docx`, base limpia `.csv`, base con issues `.csv`
