---
name: prospeccion-digital
description: >
  Skill para generar presentaciones de Prospección Digital de KinAnalytics. Úsalo SIEMPRE que el usuario
  quiera crear, generar o actualizar una presentación de prospección digital, análisis de Priority,
  resultados de Dataplor, o cualquier entregable de presentación PowerPoint para embotelladores
  (Femsa, Arca, OXXO, etc.). También activa cuando el usuario mencione "base de Priority",
  "maestra de clientes", "prospección", "no match", "match", "probability_existence_cat",
  "channel_cat", "business_category" en el contexto de una presentación. Este skill guía todo
  el proceso interactivo: hace preguntas al usuario, procesa la base de datos, genera gráficos
  y produce el PPTX final listo para entregar.
---

# Skill: Prospección Digital — Presentación PowerPoint

Este skill genera automáticamente la presentación de resultados de Prospección Digital
a partir de una base de datos de Priority y la plantilla corporativa de KinAnalytics.

---

## PASO 1 — Preguntas iniciales (OBLIGATORIO al arrancar)

Antes de hacer cualquier otra cosa, pregunta al usuario estas 6 cosas:

1. **¿En qué país se realiza el ejercicio?**  
   (Ejemplo: Nicaragua, Guatemala, México, Honduras…)

2. **¿Cuál es la embotelladora?**  
   (Ejemplo: Femsa, Arca, OXXO, Coca-Cola FEMSA…)

3. **¿Cuándo fue entregada la base de clientes (maestra de clientes)?**  
   (Ejemplo: "Abril 2026", "Marzo 2026"…)

4. **¿Quién hizo la entrega de la base de clientes?**  
   Opciones: `"por embotelladora"` o `"por NSR"`

5. **¿Cuántos clientes tiene la maestra del embotellador (total de registros en la base de clientes)?**  
   (Ejemplo: 45.164 — este número NO se puede calcular desde la base de Priority, debe ser confirmado por el usuario)

6. **¿En qué idioma desea los resultados de la presentación?**  
   Opciones: `"Español"`, `"Inglés"` o `"Portugués"`

Una vez respondidas, pide la **base de datos de Priority** (archivo CSV o Excel).

> ⚠️ **IMPORTANTE**: El total de clientes del embotellador (pregunta 5) es un dato externo que **no coincide necesariamente** con el conteo de `match` en la base de Priority. Siempre usar el número confirmado por el usuario para la diapositiva 9.

> ⚠️ **IDIOMA**: Guarda la selección en la variable `LANG` (`'es'`, `'en'` o `'pt'`). Todos los textos generados dinámicamente — títulos de tablas, encabezados, subtítulos, textos descriptivos, insights, callouts y etapas — deben estar en el idioma seleccionado usando el diccionario `T` definido en el PASO 2b.

---

## PASO 2 — Cargar y analizar la base de Priority

La base de Priority debe contener al menos estas columnas clave:

| Columna | Descripción |
|---|---|
| `match_no_match` | Valores: `match` o `no_match` |
| `probability_existence_cat` | Valores: `High`, `Moderate`, `Low` |
| `channel_cat` | Valores: `On Premise`, `Off Premise` |
| `business_category` | Categoría del negocio |
| `city` | Ciudad del punto |

### Calcular métricas para las diapositivas:

```python
import pandas as pd

df = pd.read_csv("base_priority.csv")  # o read_excel según el formato

# Totales generales (diapositiva 9)
total_dataplor = len(df)
total_embotellador = df[df['match_no_match'] == 'match']['pos_id'].nunique()  
# Si no hay pos_id, usar count de match

# Resumen no_match por categoría de probabilidad
no_match = df[df['match_no_match'] == 'no_match']
high_count    = len(no_match[no_match['probability_existence_cat'] == 'High'])
moderate_count = len(no_match[no_match['probability_existence_cat'] == 'Moderate'])
low_count     = len(no_match[no_match['probability_existence_cat'] == 'Low'])
total_no_match = len(no_match)
total_match    = len(df[df['match_no_match'] == 'match'])

# Segmento High+Moderate no_match (diapositivas 10-15)
hm_nomatch = no_match[no_match['probability_existence_cat'].isin(['High', 'Moderate'])]

# Diapositiva 10 — por ciudad y canal
slide10 = hm_nomatch.groupby(['city', 'channel_cat']).size().unstack(fill_value=0)

# Diapositiva 11 — por business_category y channel_cat
slide11 = hm_nomatch.groupby(['business_category', 'channel_cat']).size().unstack(fill_value=0)

# Diapositiva 12 — On Premise: top categorías y top ciudades
on_prem = hm_nomatch[hm_nomatch['channel_cat'] == 'On Premise']
slide12_cat  = on_prem.groupby('business_category').size().sort_values(ascending=False).head(10)
slide12_city = on_prem.groupby('city').size().sort_values(ascending=False).head(10)

# Diapositiva 13 — Off Premise: top categorías y top ciudades
off_prem = hm_nomatch[hm_nomatch['channel_cat'] == 'Off Premise']
slide13_cat  = off_prem.groupby('business_category').size().sort_values(ascending=False).head(10)
slide13_city = off_prem.groupby('city').size().sort_values(ascending=False).head(10)

# Diapositiva 15 — Impacto por etapas
# Top N ciudades y categorías para cada etapa (3, 5, 8, resto)
```

---

## PASO 2b — Diccionario de traducciones

Definir `LANG` y el diccionario `T` antes de generar cualquier texto:

```python
# LANG viene de la respuesta del usuario: 'es', 'en' o 'pt'
# Ejemplo: LANG = 'en'

TRANSLATIONS = {
    'es': {
        # ── Meses ───────────────────────────────────────────────────────────
        'months': ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
                   'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
        # ── Tabla encabezados ───────────────────────────────────────────────
        'ciudad': 'Ciudad',
        'total': 'Total',
        'otros': 'Otros',
        'business_category': 'Business Category',
        'high': 'High',
        'moderate': 'Moderate',
        'low': 'Low',
        'others': 'Others',
        # ── Subtítulos de tablas ────────────────────────────────────────────
        'no_match_subtitle': 'No Match - probabilidad de existencia',
        'city_opp_subtitle':  'Oportunidad por ciudad y potencial High/Moderate*',
        'footnote_table':     '* Total de High y Moderate No-Match points',
        'footnote_table2':    '*Para esta tabla se ha seleccionado las 5 categorías con mayor oportunidad con alta probabilidad de existencia (high y moderate no-match)',
        # ── Títulos de diapositivas ─────────────────────────────────────────
        'resumen_resultados':      'Resumen de resultados',
        'resumen_resultados_star': 'Resumen de resultados*',
        'on_premise_detail':  'Detalle de oportunidad canal On Premise',
        'off_premise_detail': 'Detalle de oportunidad canal Off Premise',
        'impacto_titulo':     'Impacto del proyecto',
        # ── Gráficos ────────────────────────────────────────────────────────
        'chart_on_title':  'Top categorías – On Premise',
        'chart_off_title': 'Top categorías – Off Premise',
        'chart_xlabel':    'Número de puntos',
        # ── Textos descriptivos (slides 10-13) ──────────────────────────────
        'slide10_desc': 'A continuación se presenta el potencial total identificado en la prospección digital, desglosado por ciudad y canal. Esta vista permite priorizar mercados con mayor concentración de puntos High y Moderate, tanto en Off Premise como en On Premise, para enfocar los esfuerzos comerciales donde el impacto puede ser más alto.',
        'slide11_desc': 'En la prospección digital se identifica una alta concentración de puntos por categoría. Para On Premise, {cat1_on} y {cat2_on} representan cerca del {pct_on}% del total de oportunidad del canal. En Off Premise, {cat1_off} y {cat2_off} abarcan alrededor del {pct_off}%. Estas categorías concentran la mayor parte del potencial y guían las prioridades comerciales.',
        'slide12_desc': 'Para el canal On Premise, la mayor parte del potencial High–Moderate se concentra en {top5_on} que en conjunto representan más del {pct5_on}% de la oportunidad total. Además, {top_city_on} destaca como la ciudad con mayor volumen de puntos High–Moderate, acumulando el {pct_city_on}% del total, mientras que el resto del país concentra el {resto_on}% restante.',
        'slide13_desc': 'Para el canal Off Premise, la mayor parte del potencial High–Moderate se concentra en {top5_off} que en conjunto representan cerca del {pct5_off}% de la oportunidad total. Además, {top_city_off} aporta aproximadamente el {pct_city_off}% de este potencial, mientras que el resto del país concentra el {resto_off}%.',
        # ── Slide 14 ────────────────────────────────────────────────────────
        'slide14_title':  '{top_city} concentra la mayor cantidad de puntos con',
        'slide14_bold':   'alta probabilidad',
        'slide14_title2': 'de existencia',
        'slide14_p1': 'Considerando que {top_city} es el mercado con la mayor concentración de puntos High y Moderate ({hm_city} POS, {pct_city}% del total H+M), el análisis espacial muestra una alta densidad de oportunidades en el área metropolitana.',
        'slide14_p2': 'Las zonas marcadas concentran hexágonos con densidad alta y muy alta, indicando las áreas prioritarias donde se recomienda focalizar los esfuerzos comerciales en {pais}.',
        # ── Slide 15 ────────────────────────────────────────────────────────
        'slide15_intro':  'De acuerdo a los datos y análisis mostrados, consideramos que se puede capturar valor para {embotelladora} {pais} de la siguiente manera:',
        'slide15_etapas': 'Resultados esperados por etapas*',
        'etapa1': 'Activación de puntos high y moderate en el top 3 ciudades y top 3 categorías de negocio (+{n1} POS, +{pct1}% del portafolio actual)',
        'etapa2': 'Expansión hacia las Top 5 ciudades y Top 5 categorías (+{n2} POS adicionales, +{pct2}% acumulado)',
        'etapa3': 'Activación del siguiente bloque ampliado, Top 8 ciudades y Top 8 categorías (+{n3} POS adicionales, +{pct3}% acumulado)',
        'etapa4': 'Activación del resto de ciudades y categorías fuera del Top 8 (+{n4} POS adicionales, completando el 100% del potencial H+M)',
        'slide15_total': 'En total, la activación por etapas representa un potencial de +{total_hm} nuevos puntos, equivalente a un crecimiento de +{pct_total}% del potencial H+M sobre el portafolio {embotelladora} {pais} ({portfolio} POS).',
        # ── Slide 5 ─────────────────────────────────────────────────────────
        'slide5_label': 'Maestra de clientes - {embotelladora} {pais}',
        'slide5_fecha': '({mes_entrega} compartida por {quien_entrego})',
        'entregada_por_embotelladora': 'embotelladora',
        'entregada_por_nsr': 'NSR',
        # ── Insights ────────────────────────────────────────────────────────
        'insight_s9':  'Con solo el {pct_high}% del potencial en categoría High, {pais} presenta un perfil de oportunidad {perfil}: {total_hm} POS equivalen a un +{pct_portfolio}% sobre el portafolio de {portfolio} POS.',
        'insight_s10': 'El {pct_resto}% del potencial H+M está disperso fuera de las 5 principales ciudades — patrón de {patron} que demanda una estrategia de cobertura {estrategia}.',
        'insight_s11': '{cat1_on} concentra el {pct1_on}% del canal On Premise con {n1_on} POS — {conclusion_on}. En Off Premise, la dupla {cat1_off} + {cat2_off} abarca el {pct12_off}% ({n12_off} POS).',
        'insight_s14': 'A pesar de ser la capital, {top_city} concentra solo el {pct_city}% del potencial H+M — el mercado está altamente atomizado, con el {pct_resto}% del potencial distribuido en departamentos del interior del país.',
        'insight_s15': 'Activar por etapas permite a {embotelladora} {pais} capturar el +{pct_portfolio}% de crecimiento potencial de forma progresiva. La alta dispersión geográfica hace especialmente crítica la priorización por etapas para maximizar el ROI de cada visita comercial.',
    },

    'en': {
        'months': ['January','February','March','April','May','June',
                   'July','August','September','October','November','December'],
        'ciudad': 'City',
        'total': 'Total',
        'otros': 'Others',
        'business_category': 'Business Category',
        'high': 'High',
        'moderate': 'Moderate',
        'low': 'Low',
        'others': 'Others',
        'no_match_subtitle': 'No Match - probability of existence',
        'city_opp_subtitle':  'Opportunity by city and High/Moderate potential*',
        'footnote_table':     '* Total of High and Moderate No-Match points',
        'footnote_table2':    '*This table shows the top 5 categories with the highest opportunity and high probability of existence (high and moderate no-match)',
        'resumen_resultados':      'Results Summary',
        'resumen_resultados_star': 'Results Summary*',
        'on_premise_detail':  'On Premise Channel Opportunity Detail',
        'off_premise_detail': 'Off Premise Channel Opportunity Detail',
        'impacto_titulo':     'Project Impact',
        'chart_on_title':  'Top categories – On Premise',
        'chart_off_title': 'Top categories – Off Premise',
        'chart_xlabel':    'Number of points',
        'slide10_desc': 'The following presents the total potential identified in the digital prospecting exercise, broken down by city and channel. This view allows prioritizing markets with the highest concentration of High and Moderate points, both in Off Premise and On Premise, to focus commercial efforts where the impact can be highest.',
        'slide11_desc': 'The digital prospecting identifies a high concentration of points by category. For On Premise, {cat1_on} and {cat2_on} represent approximately {pct_on}% of the total channel opportunity. In Off Premise, {cat1_off} and {cat2_off} account for around {pct_off}%. These categories concentrate most of the potential and guide commercial priorities.',
        'slide12_desc': 'For the On Premise channel, most of the High–Moderate potential is concentrated in {top5_on}, which together represent more than {pct5_on}% of the total opportunity. Additionally, {top_city_on} stands out as the city with the highest volume of High–Moderate points, accounting for {pct_city_on}% of the total, while the rest of the country holds the remaining {resto_on}%.',
        'slide13_desc': 'For the Off Premise channel, most of the High–Moderate potential is concentrated in {top5_off}, which together represent approximately {pct5_off}% of the total opportunity. Additionally, {top_city_off} contributes approximately {pct_city_off}% of this potential, while the rest of the country accounts for {resto_off}%.',
        'slide14_title':  '{top_city} concentrates the highest number of points with',
        'slide14_bold':   'high probability',
        'slide14_title2': 'of existence',
        'slide14_p1': 'Considering that {top_city} is the market with the highest concentration of High and Moderate points ({hm_city} POS, {pct_city}% of total H+M), the spatial analysis shows a high density of opportunities in the metropolitan area.',
        'slide14_p2': 'The marked areas concentrate hexagons with high and very high density, indicating priority zones where commercial efforts should be focused in {pais}.',
        'slide15_intro':  'Based on the data and analysis presented, we consider that value can be captured for {embotelladora} {pais} as follows:',
        'slide15_etapas': 'Expected results by stage*',
        'etapa1': 'Activation of high and moderate points in the top 3 cities and top 3 business categories (+{n1} POS, +{pct1}% of current portfolio)',
        'etapa2': 'Expansion to the Top 5 cities and Top 5 categories (+{n2} additional POS, +{pct2}% cumulative)',
        'etapa3': 'Activation of the next expanded block, Top 8 cities and Top 8 categories (+{n3} additional POS, +{pct3}% cumulative)',
        'etapa4': 'Activation of remaining cities and categories outside Top 8 (+{n4} additional POS, completing 100% of H+M potential)',
        'slide15_total': 'In total, the staged activation represents a potential of +{total_hm} new points, equivalent to +{pct_total}% H+M growth over the {embotelladora} {pais} current portfolio ({portfolio} POS).',
        'slide5_label': 'Customer master - {embotelladora} {pais}',
        'slide5_fecha': '({mes_entrega} shared by {quien_entrego})',
        'entregada_por_embotelladora': 'bottler',
        'entregada_por_nsr': 'NSR',
        'insight_s9':  'With only {pct_high}% of the potential in the High category, {pais} presents a {perfil} opportunity profile: {total_hm} POS equivalent to a +{pct_portfolio}% growth over a portfolio of {portfolio} POS.',
        'insight_s10': '{pct_resto}% of the H+M potential is dispersed outside the top 5 cities — a {patron} pattern that requires a {estrategia} coverage strategy rather than urban focus.',
        'insight_s11': '{cat1_on} captures {pct1_on}% of the On Premise channel with {n1_on} POS — {conclusion_on}. In Off Premise, the pair {cat1_off} + {cat2_off} accounts for {pct12_off}% ({n12_off} POS).',
        'insight_s14': 'Despite being the capital, {top_city} concentrates only {pct_city}% of the H+M potential — the market is highly atomized, with {pct_resto}% of the potential distributed across secondary cities.',
        'insight_s15': 'A staged activation allows {embotelladora} {pais} to capture +{pct_portfolio}% growth potential progressively. The high geographic dispersion makes stage prioritization especially critical to maximize ROI per commercial visit.',
    },

    'pt': {
        'months': ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                   'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'],
        'ciudad': 'Cidade',
        'total': 'Total',
        'otros': 'Outros',
        'business_category': 'Categoria de Negócio',
        'high': 'High',
        'moderate': 'Moderate',
        'low': 'Low',
        'others': 'Outros',
        'no_match_subtitle': 'No Match - probabilidade de existência',
        'city_opp_subtitle':  'Oportunidade por cidade e potencial High/Moderate*',
        'footnote_table':     '* Total de pontos High e Moderate No-Match',
        'footnote_table2':    '*Esta tabela apresenta as 5 categorias com maior oportunidade e alta probabilidade de existência (high e moderate no-match)',
        'resumen_resultados':      'Resumo de Resultados',
        'resumen_resultados_star': 'Resumo de Resultados*',
        'on_premise_detail':  'Detalhe de Oportunidade Canal On Premise',
        'off_premise_detail': 'Detalhe de Oportunidade Canal Off Premise',
        'impacto_titulo':     'Impacto do Projeto',
        'chart_on_title':  'Top categorias – On Premise',
        'chart_off_title': 'Top categorias – Off Premise',
        'chart_xlabel':    'Número de pontos',
        'slide10_desc': 'A seguir é apresentado o potencial total identificado na prospecção digital, desagregado por cidade e canal. Esta visão permite priorizar mercados com maior concentração de pontos High e Moderate, tanto em Off Premise como em On Premise, para direcionar os esforços comerciais onde o impacto pode ser mais elevado.',
        'slide11_desc': 'A prospecção digital identifica uma alta concentração de pontos por categoria. Para On Premise, {cat1_on} e {cat2_on} representam cerca de {pct_on}% do total de oportunidade do canal. Em Off Premise, {cat1_off} e {cat2_off} abrangem aproximadamente {pct_off}%. Estas categorias concentram a maior parte do potencial e orientam as prioridades comerciais.',
        'slide12_desc': 'Para o canal On Premise, a maior parte do potencial High–Moderate está concentrada em {top5_on}, que em conjunto representam mais de {pct5_on}% da oportunidade total. Além disso, {top_city_on} destaca-se como a cidade com maior volume de pontos High–Moderate, acumulando {pct_city_on}% do total, enquanto o restante do país concentra os {resto_on}% restantes.',
        'slide13_desc': 'Para o canal Off Premise, a maior parte do potencial High–Moderate está concentrada em {top5_off}, que em conjunto representam cerca de {pct5_off}% da oportunidade total. Além disso, {top_city_off} contribui com aproximadamente {pct_city_off}% desse potencial, enquanto o restante do país concentra {resto_off}%.',
        'slide14_title':  '{top_city} concentra a maior quantidade de pontos com',
        'slide14_bold':   'alta probabilidade',
        'slide14_title2': 'de existência',
        'slide14_p1': 'Considerando que {top_city} é o mercado com a maior concentração de pontos High e Moderate ({hm_city} POS, {pct_city}% do total H+M), a análise espacial mostra uma alta densidade de oportunidades na área metropolitana.',
        'slide14_p2': 'As zonas marcadas concentram hexágonos com densidade alta e muito alta, indicando as áreas prioritárias onde se recomenda focar os esforços comerciais em {pais}.',
        'slide15_intro':  'Com base nos dados e análises apresentados, consideramos que é possível capturar valor para {embotelladora} {pais} da seguinte forma:',
        'slide15_etapas': 'Resultados esperados por etapas*',
        'etapa1': 'Ativação de pontos high e moderate no top 3 cidades e top 3 categorias de negócio (+{n1} POS, +{pct1}% do portfólio atual)',
        'etapa2': 'Expansão para as Top 5 cidades e Top 5 categorias (+{n2} POS adicionais, +{pct2}% acumulado)',
        'etapa3': 'Ativação do próximo bloco expandido, Top 8 cidades e Top 8 categorias (+{n3} POS adicionais, +{pct3}% acumulado)',
        'etapa4': 'Ativação das demais cidades e categorias fora do Top 8 (+{n4} POS adicionais, completando 100% do potencial H+M)',
        'slide15_total': 'No total, a ativação por etapas representa um potencial de +{total_hm} novos pontos, equivalente a um crescimento de +{pct_total}% do potencial H+M sobre o portfólio {embotelladora} {pais} ({portfolio} POS).',
        'slide5_label': 'Base de clientes - {embotelladora} {pais}',
        'slide5_fecha': '({mes_entrega} compartilhada por {quien_entrego})',
        'entregada_por_embotelladora': 'engarrafadora',
        'entregada_por_nsr': 'NSR',
        'insight_s9':  'Com apenas {pct_high}% do potencial na categoria High, {pais} apresenta um perfil de oportunidade {perfil}: {total_hm} POS equivalem a +{pct_portfolio}% sobre o portfólio de {portfolio} POS.',
        'insight_s10': '{pct_resto}% do potencial H+M está disperso fora das 5 principais cidades — padrão de {patron} que exige uma estratégia de cobertura {estrategia}.',
        'insight_s11': '{cat1_on} concentra {pct1_on}% do canal On Premise com {n1_on} POS — {conclusion_on}. Em Off Premise, a dupla {cat1_off} + {cat2_off} abrange {pct12_off}% ({n12_off} POS).',
        'insight_s14': 'Apesar de ser a capital, {top_city} concentra apenas {pct_city}% do potencial H+M — o mercado está altamente atomizado, com {pct_resto}% do potencial distribuído nas cidades secundárias.',
        'insight_s15': 'A ativação por etapas permite à {embotelladora} {pais} capturar +{pct_portfolio}% de crescimento potencial de forma progressiva. A alta dispersão geográfica torna a priorização por etapas especialmente crítica para maximizar o ROI de cada visita comercial.',
    },
}

def T(key):
    return TRANSLATIONS[LANG][key]

# Uso del mes actual en el idioma seleccionado:
# from datetime import datetime
# mes_actual = T('months')[datetime.now().month - 1]  # e.g. "May" / "Mayo" / "Maio"
```

> ⚠️ **APLICACIÓN**: Usar `T('key')` en **TODOS** los textos generados dinámicamente. Los textos fijos de las diapositivas 2–8 y 16–22 permanecen en español (idioma base de la plantilla). Solo las diapositivas que se modifican activamente (1, 5, 9, 10, 11, 12, 13, 14, 15) deben estar en el idioma seleccionado.

---

## PASO 3 — Editar la presentación

### Plantilla
La plantilla está en: `assets/Plantilla_Prospección_Digital.pptx`

Sigue el flujo del skill PPTX (ver `/mnt/skills/public/pptx/SKILL.md` y `editing.md`):
1. Copia la plantilla al directorio de trabajo
2. Desempaca con `unpack.py`
3. Edita los XMLs de cada diapositiva
4. Limpia y empaca

---

## PASO 4 — Cambios por diapositiva

### Diapositiva 1 — Portada
Busca y reemplaza en `slide1.xml`:

| Texto actual | Nuevo texto |
|---|---|
| `Nicaragua` | `{PAIS}` |
| `Femsa` | `{EMBOTELLADORA}` |
| `Mayo 2026` | mes y año actuales en español (ej: "Mayo 2026") |

> El mes debe generarse dinámicamente con `datetime.now()` en español.

---

### Diapositivas 2, 3, 4 — SIN CAMBIOS
No tocar nada.

---

### Diapositiva 5 — Datos de entrada
Texto a actualizar: `Maestra de clientes - Femsa Nicaragua (Abril 2026 compartida por cliente)`

Formato nuevo:
```
Maestra de clientes - {EMBOTELLADORA} {PAIS}
({MES_ENTREGA} compartida por {QUIEN_ENTREGO})
```

Donde `{QUIEN_ENTREGO}` es:
- `"embotelladora"` → `"compartida por embotelladora"`
- `"NSR"` → `"compartida por NSR"`

---

### Diapositivas 6, 7, 8 — SIN CAMBIOS
No tocar nada.

---

### Diapositiva 9 — Resumen de resultados (números)

Actualizar los números en el XML con los valores calculados en PASO 2:

```
Dataplor         → {total_dataplor}   (total registros en base Priority)
Embotellador     → {total_embotellador} (clientes en base de clientes / match)

High             → {high_count}
Moderate         → {moderate_count}
Low              → {low_count}
Total            → {total_no_match}

{high_count} high & {moderate_count} moderate no-match   (texto resumen)
{low_count} no-match                                      (grey area)
{total_match} Match                                       (match POS)
```

> ⚠️ **IMPORTANTE**: La plantilla base tiene los valores de Guatemala (34.626, 229.077, 896, 2.636, 5.952, 9.484, 25.142). Siempre parchear desde esos valores originales del template, NO desde valores de un ejercicio anterior.

```python
# Valores originales del template a reemplazar en slide9.xml
ORIGINAL_VALUES = {
    '<a:t>34.626</a:t>': f'<a:t>{total_dataplor_fmt}</a:t>',
    '<a:t>229.077</a:t>': f'<a:t>{embotellador_fmt}</a:t>',
    '<a:t>896</a:t>': f'<a:t>{high_fmt}</a:t>',
    '<a:t>2.636</a:t>': f'<a:t>{moderate_fmt}</a:t>',
    '<a:t>5.952</a:t>': f'<a:t>{low_fmt}</a:t>',
    '<a:t>9.484</a:t>': f'<a:t>{total_nomatch_fmt}</a:t>',
    '<a:t>896 high</a:t>': f'<a:t>{high_fmt} high</a:t>',
    '<a:t>2.636 moderate no-match</a:t>': f'<a:t>{moderate_fmt} moderate no-match</a:t>',
    '<a:t>5.952 no-match</a:t>': f'<a:t>{low_fmt} no-match</a:t>',
    '<a:t>25.142 Match</a:t>': f'<a:t>{match_fmt} Match</a:t>',
}
```

---

### Diapositiva 10 — Resumen por ciudad y canal

Crear una **TABLA** (no gráfico de barras) con el siguiente formato:

| Ciudad | Off Premise | On Premise | Total |
|---|---|---|---|
| Ciudad 1 | X | X | X |
| ... (top 5) | | | |
| Otros | X | X | X |
| **Total** | **X** | **X** | **X** |

Estilo de la tabla:
- Encabezado: fondo amarillo `#E8E800`, texto negro, bold
- Fila Total: fondo negro `#1A1A1A`, texto blanco, bold
- Filas alternas: `#F2F2F2` / `#FFFFFF`
- Columna Ciudad: alineada a la izquierda; demás columnas: centradas

Eliminar cualquier gráfico de barras previo que pudiera existir en la diapositiva.

Actualizar el texto descriptivo con datos reales:
```
Las 5 principales ciudades abarcan el {X}% del potencial total de High y Moderate
({total_HM_top5} potenciales nuevos POS)
```

---

### Diapositiva 11 — Por categoría y canal

Crear **2 gráficos de barras horizontales**:
- Gráfico izquierdo: **On Premise** — top categorías por business_category (High+Moderate no_match)
- Gráfico derecho: **Off Premise** — top categorías por business_category (High+Moderate no_match)

**Color de las barras: amarillo-verde `#C8D400`** (NO azul ni naranja — es el color corporativo KinAnalytics)

### Dimensiones y posición de los gráficos (diapositiva 11)

```python
from pptx.util import Cm

target_w  = Cm(10.42)
target_h  = Cm(8.15)
footer_top = Cm(12.99)
chart_top  = footer_top - target_h   # 4.84cm — flush contra el footer

margin = Cm(1.44)
gap    = Cm(2.12)
left1  = margin                       # gráfico izquierdo
left2  = margin + target_w + gap      # gráfico derecho (13.98cm)
```

> Los dos gráficos quedan centrados y su borde inferior toca exactamente el inicio del footer.

El texto descriptivo usa el formato:
```
Para On Premise, {cat1} y {cat2} representan el {X}% del total de oportunidad del canal.
En Off Premise, {cat1} y {cat2} abarcan el {X}%.
```
⚠️ El texto está fragmentado en múltiples runs en el XML — siempre identificar el run exacto antes de reemplazar.

---

### Diapositivas 12 y 13 — Detalle On Premise / Off Premise

Crear **2 TABLAS** por diapositiva (mismas en formato que diap 10):

**Tabla izquierda** — `Business Category | High | Moderate | Total`
- Top 5 categorías del canal, fila Others, fila Total
- Encabezado amarillo, Total negro, filas alternas grises

**Tabla derecha** — `Business Category | Ciudad1 | Ciudad2 | Others | Total`
- Top 5 categorías del canal
- Columnas = top 2 ciudades del canal + Others + Total
- Mismo estilo de colores

Calcular top 2 ciudades por separado para On Premise y Off Premise (pueden ser distintas).

**NO usar gráficos de barras en estas diapositivas — solo tablas.**

### Dimensiones y posición de las tablas (diapositivas 12 y 13)

```python
from pptx.util import Cm

# Posiciones validadas manualmente — usar estas como referencia base
subtitle_top = Cm(4.85)   # subtítulos ("No Match..." / "Oportunidad por ciudad...")
table_top    = Cm(5.85)   # inicio de tablas

# Tabla izquierda (Business Category | High | Moderate | Total)
left1_t1    = Cm(0.73)
width_t1    = Cm(11.47)   # On Premise; Off Premise puede variar ~10.59cm
height_t1   = Cm(5.25)
col_widths_t1 = [Cm(3.91), Cm(2.52), Cm(2.52), Cm(2.52)]  # On Premise
# col_widths_t1 = [Cm(3.61), Cm(2.33), Cm(2.33), Cm(2.33)]  # Off Premise

# Tabla derecha (Business Category | Ciudad1 | Ciudad2 | Others | Total)  
left2_t2    = Cm(13.20)
width_t2    = Cm(11.47)   # On Premise; Off Premise puede variar ~11.68cm
height_t2   = Cm(5.57)    # On Premise; Off Premise ~5.25cm
col_widths_t2 = [Cm(3.56), Cm(1.98), Cm(1.98), Cm(1.98), Cm(1.98)]  # On Premise
# col_widths_t2 = [Cm(3.62), Cm(2.02), Cm(2.02), Cm(2.02), Cm(2.02)]  # Off Premise

# Alturas de fila
row_h_header = Cm(0.63)   # encabezado
row_h_data   = Cm(0.63)   # filas de datos
# Para tabla 2 On Premise: header = Cm(0.98), datos = Cm(0.61)
```

> ⚠️ El texto descriptivo termina alrededor de 4.79cm.  
> Si en otro ejercicio el texto ocupa más líneas, medir el `bottom` del shape descriptivo y ajustar  
> `subtitle_top = texto_bottom + Cm(0.05)` y `table_top = subtitle_top + Cm(1.0)`.

Actualizar el texto descriptivo con las categorías y % reales de cada canal.

---

## NOTA IMPORTANTE — Logo footer en diapositivas con contenido nuevo

Cuando se insertan tablas o gráficos nuevos en las diapositivas 10, 11, 12 y 13, el logo de
**Kin Analytics** del footer puede desaparecer (solo quedan los textos "Let knowledge in." y
"KinAnalytics.com"). Siempre copiar el logo desde la diapositiva 9 (shape tipo PICTURE en el footer):

```python
from pptx import Presentation
from lxml import etree
import copy

# Copiar logo de slide 9 a slides 10-13
s9 = prs.slides[8]
logo_shape = next((sh for sh in s9.shapes if sh.shape_type == 13 and sh.top/360000 > 12), None)

for slide_idx in [9, 10, 11, 12]:
    slide = prs.slides[slide_idx]
    has_logo = any(sh.shape_type == 13 and sh.top/360000 > 12 for sh in slide.shapes)
    if has_logo:
        continue
    logo_copy = copy.deepcopy(logo_shape._element)
    # Copiar relación de imagen
    for blip in logo_copy.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
        old_rId = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if old_rId:
            img_part = s9.part.related_part(old_rId)
            new_rId = slide.part.relate_to(img_part,
                'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image')
            blip.set('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed', new_rId)
    slide.shapes._spTree.append(logo_copy)
```

---

### Diapositiva 14 — Mapa

⚠️ **Esta diapositiva requiere proceso manual.**

Informa al usuario:
> "La diapositiva 14 (mapa de calor geográfico) **requiere proceso manual** usando Kepler.gl.
> Para generarlo:
> 1. Exporta los puntos High y Moderate no_match con latitud/longitud
> 2. Sube el CSV a kepler.gl
> 3. Configura hexbins con densidad por concentración de puntos
> 4. Captura pantalla y reemplaza la imagen en la diapositiva 14 manualmente"
>
> Por ahora la diapositiva queda con el texto actualizado pero sin el mapa.

Actualizar solo el texto de la diapositiva:
- Reemplazar `"Ciudad de Guatemala"` → ciudad principal con más puntos High+Moderate del dataset
- Actualizar el texto descriptivo con la ciudad correcta

---

### Diapositiva 15 — Impacto del proyecto

Calcular las etapas usando los datos reales:

```python
# Ordenar ciudades y categorías por volumen High+Moderate no_match
top_cities = hm_nomatch.groupby('city').size().sort_values(ascending=False)
top_cats   = hm_nomatch.groupby('business_category').size().sort_values(ascending=False)

etapa1 = hm_nomatch[
    hm_nomatch['city'].isin(top_cities.head(3).index) &
    hm_nomatch['business_category'].isin(top_cats.head(3).index)
]
etapa2_incremental = hm_nomatch[
    hm_nomatch['city'].isin(top_cities.head(5).index) &
    hm_nomatch['business_category'].isin(top_cats.head(5).index)
] 
# ... etc para etapas 3 y 4

# Calcular % sobre portafolio actual (total_embotellador)
```

Actualizar el texto completo de la diapositiva con los números reales de cada etapa,
incluyendo el total de POS potenciales y el % de crecimiento sobre portafolio actual.

Actualizar también: `"Femsa"` → `{EMBOTELLADORA}`

---

### Diapositivas 16–22 — SIN CAMBIOS EN TEXTO

No modificar contenido. Al finalizar, **avisar al usuario**:

> ⚠️ **Acciones manuales pendientes (diapositivas 16–22):**
> - **Diapositivas 18–21 (Vista previa / Glosario):** Reemplazar las imágenes de ejemplo con
>   capturas de pantalla de la base de datos real que se va a entregar.
> - **Diapositiva 22 (Contactos):** Revisar y actualizar los correos electrónicos si es necesario.
>   Actualmente aparecen: `paula.lara@kinanalytics.com`, `miguel.mena@kinanalytics.com`,
>   `nicolas.ayala@kinanalytics.com`

---

## PASO 5 — Generar gráficos con python-pptx

Para insertar gráficos (diapositivas 10, 11, 12, 13) usa `python-pptx` con `XmlChartPart`
o genera los gráficos como imágenes PNG con `matplotlib` e insértalos en el XML.

### Patrón recomendado — gráfico como imagen PNG:

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def crear_grafico_barras_horizontal(datos_series, titulo, colores, output_path):
    """
    datos_series: dict {nombre_categoria: count}
    colores: lista de colores hex
    """
    categorias = list(datos_series.keys())[:10]  # top 10
    valores = [datos_series[c] for c in categorias]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(categorias[::-1], valores[::-1], color=colores[0])
    
    # Etiquetas de valor
    for bar, val in zip(bars, valores[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=9)
    
    ax.set_title(titulo, fontsize=12, fontweight='bold')
    ax.set_xlabel('Cantidad de POS')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', transparent=True)
    plt.close()
```

### Insertar imagen PNG en XML de la diapositiva:

```python
# Después de generar el PNG, insertar en el XML del slide usando python-pptx
from pptx import Presentation
from pptx.util import Inches, Pt

# Si trabajas directo con python-pptx para insertar la imagen:
prs = Presentation("output_parcial.pptx")
slide = prs.slides[9]  # slide 10 (índice 9)
slide.shapes.add_picture("chart_slide10.png", Inches(1), Inches(2), Inches(8), Inches(4))
prs.save("output_con_grafico.pptx")
```

---

## PASO 6 — Colores corporativos KinAnalytics

Usar estos colores en todos los gráficos:

| Elemento | Color Hex |
|---|---|
| On Premise (barras) | `#1F4E79` (azul oscuro) |
| Off Premise (barras) | `#C55A11` (naranja) |
| High | `#1F4E79` |
| Moderate | `#2E75B6` |
| Low | `#9DC3E6` |
| Fondo gráfico | transparente |
| Texto | `#404040` |

---

## PASO 7 — Output final

1. Guardar el archivo como: `Prospección_Digital_{PAIS}_{EMBOTELLADORA}_{MES_ANO}.pptx`
2. Copiar a `/mnt/user-data/outputs/`
3. Presentar con `present_files`

---

## Notas importantes

- **Siempre usar "ciudad"** en lugar de "departamento" en los textos de las diapositivas 10, 12, 13.
- **El segmento analizado siempre es**: `no_match` con `probability_existence_cat` en `High` o `Moderate`.
- **La diapositiva 14 (mapa) siempre es manual** — informar al usuario.
- **Las diapositivas 16–22 son siempre manuales** — recordar al usuario cambiar imágenes y correos.
- Si la base no tiene alguna columna esperada, preguntar al usuario cuál columna equivalente usar.
- **Idioma**: `LANG = 'es'|'en'|'pt'`. Siempre usar `T('key')` para generar texto. Los gráficos de slide 11 también deben generarse con los títulos en el idioma correcto usando `T('chart_on_title')`, `T('chart_off_title')`, `T('chart_xlabel')`. Los encabezados de las tablas (Ciudad/City/Cidade, Total, Others/Otros/Outros, Business Category/Categoria de Negócio) deben estar en el idioma seleccionado.
- **Slide 14**: La plantilla tiene "Ciudad de Guatemala" en DOS runs separados — siempre iterar TODOS los runs de TODOS los shapes y reemplazar cualquier ocurrencia de "Ciudad de Guatemala" por la ciudad real.
- **Slide 15**: Cambiar todas las alineaciones JUSTIFY a LEFT en todos los párrafos del shape de etapas.

---

## Formato de números y escritura de textos

### Miles con punto (formato español)
Todos los números ≥ 1.000 deben usar punto como separador de miles en tablas y textos:
```python
def fmt(n):
    return f"{int(n):,}".replace(",", ".")
# 1129 → 1.129 | 3387 → 3.387 | 4516 → 4.516
```
Aplicar en: tablas de diapositivas 9, 10, 12, 13, y todos los textos descriptivos.

### Insights — AGREGAR, no reemplazar

El texto descriptivo original de cada diapositiva se **mantiene intacto**. El insight se agrega como elemento adicional.

**Implementación según espacio disponible:**

1. **Slides con espacio libre** (9, 10): Usar `add_callout()` — barra lima + caja fondo amarillo + texto itálico azul
2. **Slides con poco espacio** (11): Desplazar gráficos ~0.7cm hacia abajo y añadir callout compacto
3. **Slides con tablas** (12, 13): Añadir insight como segundo párrafo en la caja de texto existente con `→ ` y fuente 7.5pt itálica, luego ajustar posición de subtítulos y tablas hacia abajo
4. **Slide 14**: Añadir como tercer párrafo en el text box inferior
5. **Slide 15**: Añadir callout compacto entre el texto intro y las etapas

```python
LIME = RGBColor(0xC8, 0xD4, 0x00)
BLUE = RGBColor(0x1F, 0x4E, 0x79)
BGCOL = 'FAFFD6'

def add_callout(slide, text, left, top, width, height, font_size=8.5):
    # Lime accent bar (0.22cm wide)
    bar = slide.shapes.add_shape(1, Cm(left), Cm(top), Cm(0.22), Cm(height))
    bar.fill.solid(); bar.fill.fore_color.rgb = LIME; bar.line.fill.background()
    # Light yellow text box
    txb = slide.shapes.add_textbox(Cm(left+0.38), Cm(top), Cm(width-0.38), Cm(height))
    spPr = txb._element.find(qn('p:spPr'))
    spPr.append(etree.fromstring(f'<a:solidFill xmlns:a="..."><a:srgbClr val="{BGCOL}"/></a:solidFill>'))
    tf = txb.text_frame; tf.word_wrap = True
    para = tf.paragraphs[0]; para.alignment = PP_ALIGN.LEFT
    run = para.add_run(); run.text = text
    run.font.size = Pt(font_size); run.font.italic = True; run.font.color.rgb = BLUE
```

El insight debe: (1) señalar algo no obvio, (2) tener implicación comercial clara, (3) NO ser una explicación de la tabla.

| ❌ Descripción | ✅ Insight |
|---|---|
| "Restaurant y hotel representan el 42%" | "Solo 2 categorías capturan >40% en ambos canales — estrategia focalizada captura mitad del potencial con esfuerzo mínimo" |
| "Caracas tiene el 17% del potencial" | "55% del potencial está fuera del top 5 — mercados secundarios desatendidos de alta densidad comercial" |
| "Valencia supera a Caracas Off Premise" | "Valencia supera a Caracas Off Premise — hallazgo contraintuitivo que señala mayor densidad de puntos alternativos en secundarios" |
