"""
translations.py — All generated text strings for Customer Potential presentation.

Supported languages: 'es' (Español), 'en' (English), 'pt' (Português)
Usage:
    from translations import T
    lang = 'en'
    title = T[lang]['brecha_title'].format(cat='Coca Cola')
"""

T = {

    # ─────────────────────────────────────────────────────────────
    # ESPAÑOL (default)
    # ─────────────────────────────────────────────────────────────
    'es': {

        # ── Slide 7 narrative ──────────────────────────────────
        's7_nar': (
            "El {pct_clientes}% de los clientes (~{k_clientes}k) tienen el mayor "
            "aporte al crecimiento total ({pct_vol}%)."
        ),
        's7_nar_vh': (
            "El aporte al crecimiento de volumen (UC) de los clientes Very High, "
            "basado en el promedio mensual, es del {vh_pct}% ({vh_vol}{vh_suf}) "
            "del total del potencial de crecimiento del portafolio ({total_vol})."
        ),

        # ── Slide 8 narrative ──────────────────────────────────
        's8_nar': (
            "{best_cat} es la categoría que presenta un mayor crecimiento, con "
            "{best_pct}% en Very High, seguido por {second_cat} con {second_pct}%. "
            "Para generar un impacto más directo, los esfuerzos deben ser "
            "concentrados en estos dos segmentos."
        ),

        # ── Embudo detail strings ──────────────────────────────
        'embudo_n1_detail': "{vol} UC/mes - {pos}K clientes",
        'embudo_n2_detail': "{vol} UC/mes - {pos}K clientes",
        'embudo_n3_detail': "{vol} UC/mes - {pos}K clientes",
        'embudo_n2_pct':    "Este subcanal concentra el {pct_vol}% del volumen y el {pct_com}% de los comercios",
        'embudo_n3_pct':    "El grueso de la oportunidad se encuentra en estas ciudades que concentra el {pct_vol}% del volumen y {pct_pos}% de los POS",
        'embudo_n1_label':  "Very High y high",
        'clientes_seg':     "Clientes segmentados",
        'uc_mes':           "UC/mes",

        # ── Slide 11 map ───────────────────────────────────────
        's11_nar': (
            "Fueron identificados {pos1} POS en {city1} con un crecimiento promedio "
            "de {pct1}%, mientras que en {city2} se encuentran {pos2} POS con un "
            "promedio de {pct2}%."
        ),
        's11_title': "Departamento de {city1} y {city2}",

        # ── Giro section divider ───────────────────────────────
        'giro_divider_title':    "Brecha de Capitalización",
        'giro_divider_subtitle': (
            "Distribución del potencial, brecha de capitalización y priorización\n"
            "comercial por tipo de punto de venta (pos_subchannel)."
        ),

        # ── Slide B — Distribution table ──────────────────────
        'dist_title':  "Distribución del Potencial por Giro  —  {cat}",
        'dist_expl': (
            "Esta tabla muestra los 5 giros de negocio con mayor aporte al "
            "crecimiento potencial. La barra de % VH+High indica la madurez "
            "comercial del giro: verde lima ≥ 40%, verde suave < 40%."
        ),
        'dist_col_giro':   "Giro de Negocio",
        'dist_col_pdv':    "PDV [n]",
        'dist_col_vhh':    "% VH+High",
        'dist_col_aporte': "Aporte Crecimiento",
        'dist_col_venta':  "Venta Prom. UC",

        # Insights B
        'dist_i1': "Los 2 giros principales concentran el {pct:.1f}% del crecimiento potencial de {cat}.",
        'dist_i2': "{giro} lidera en madurez comercial con {vhh:.0f}% de sus PDVs en Very High+High.",
        'dist_i3_low':  "{giro} tiene {pdv:,} PDVs con solo {vhh:.0f}% VH+High — mayor oportunidad de desarrollo.",
        'dist_i3_high': "{giro} tiene la venta promedio más alta ({venta} UC/PDV), indicando potencial de replicar.",

        # ── Slide C — Brecha ───────────────────────────────────
        'brecha_title': "Brecha de Capitalización  —  {cat}",
        'brecha_expl': (
            "Comparación entre la venta promedio actual (UC/mes) y el potencial "
            "adicional estimado por PDV. La barra verde representa la oportunidad "
            "de crecimiento mensual no capitalizada. Un +X mayor indica mayor "
            "retorno esperado por PDV."
        ),
        'brecha_legend_actual':    "Venta Actual Prom. UC",
        'brecha_legend_potencial': "Potencial Adicional Prom. UC",
        'brecha_xlabel':           "UC/mes por PDV (promedio)",

        # Insights C
        'brecha_i1': "Mayor brecha: {giro} con +{val:,.0f} UC/PDV de potencial adicional mensual.",
        'brecha_i2': "{giro} muestra la mejor relación potencial/base ({pct:.0f}%) — alta eficiencia de conversión.",
        'brecha_i3': "Potencial total sin capitalizar en el top 5 giros: {total} UC/mes de crecimiento adicional.",

        # ── Slide D — Scatter ──────────────────────────────────
        'scatter_title': "Mapa de Priorización Comercial  —  {cat}",
        'scatter_expl': (
            "Cada punto es un giro de negocio. Eje X = % PDVs con Very High+High; "
            "eje Y = potencial total de crecimiento; tamaño = número de PDVs. "
            "Cuadrante superior-derecho (Prioridad Alta) = alto potencial Y alta madurez."
        ),
        'scatter_xlabel': "% PDVs con Potencial VH + High",
        'scatter_ylabel': "Potencial Total de Crecimiento (UC/mes)",
        'scatter_q_alta':    "Prioridad Alta",
        'scatter_q_desar':   "Desarrollar",
        'scatter_q_mant':    "Mantener",
        'scatter_q_monit':   "Monitorear",
        'scatter_yformat':   lambda v: f'{v/1000:.0f}k' if v >= 1000 else f'{v:.0f}',

        # Insights D
        'scatter_i1': "Prioridad Alta ({n} giro(s)): {names}. Alto % VH+High Y mayor potencial — enfocar acciones aquí.",
        'scatter_i2_desar': "Desarrollar ({n} giro(s)): {names}. Gran potencial total con bajo % VH+High — hay clientes sin activar.",
        'scatter_i2_mant':  "Mantener ({n} giro(s)): alto % VH+High pero menor volumen. Consolidar y defender share.",
        'scatter_i3': "El tamaño de cada burbuja refleja el número de PDVs. Giros grandes en 'Desarrollar' representan la mayor oportunidad estructural.",

        # ── Brecha slide (type 18 XML clone) ──────────────────
        'brecha18_title':   "Brecha de Capitalización – {cat}",
        'brecha18_insight': (
            "La mayor brecha de crecimiento la encontramos en {giro1} que tiene "
            "un crecimiento de +{gap:.0f} potencial adicional mensual. "
            "{giro2} muestra la mejor relación potencial/base ({eff:.0f}%), "
            "alta eficiencia de conversión."
        ),
        'brecha18_expl': (
            "Comparación entre la venta promedio actual (UC/mes) y el potencial "
            "adicional estimado por PDV. La barra verde representa la oportunidad "
            "de crecimiento mensual no capitalizada. Un +X mayor indica mayor "
            "retorno esperado por PDV."
        ),
    },


    # ─────────────────────────────────────────────────────────────
    # ENGLISH
    # ─────────────────────────────────────────────────────────────
    'en': {

        # ── Slide 7 narrative ──────────────────────────────────
        's7_nar': (
            "{pct_clientes}% of clients (~{k_clientes}k) account for the highest "
            "contribution to total growth ({pct_vol}%)."
        ),
        's7_nar_vh': (
            "The volume growth contribution (UC) of Very High clients, based on "
            "monthly average, is {vh_pct}% ({vh_vol}{vh_suf}) of total portfolio "
            "growth potential ({total_vol})."
        ),

        # ── Slide 8 narrative ──────────────────────────────────
        's8_nar': (
            "{best_cat} is the category showing the highest growth, with "
            "{best_pct}% in Very High, followed by {second_cat} with {second_pct}%. "
            "To generate a more direct impact, efforts should be concentrated "
            "in these two segments."
        ),

        # ── Embudo detail strings ──────────────────────────────
        'embudo_n1_detail': "{vol} UC/month - {pos}K clients",
        'embudo_n2_detail': "{vol} UC/month - {pos}K clients",
        'embudo_n3_detail': "{vol} UC/month - {pos}K clients",
        'embudo_n2_pct':    "This subchannel concentrates {pct_vol}% of volume and {pct_com}% of outlets",
        'embudo_n3_pct':    "Most of the opportunity is in these cities, concentrating {pct_vol}% of volume and {pct_pos}% of POS",
        'embudo_n1_label':  "Very High and High",
        'clientes_seg':     "Segmented clients",
        'uc_mes':           "UC/month",

        # ── Slide 11 map ───────────────────────────────────────
        's11_nar': (
            "{pos1} POS were identified in {city1} with an average growth of "
            "{pct1}%, while {city2} has {pos2} POS with an average of {pct2}%."
        ),
        's11_title': "{city1} and {city2}",

        # ── Giro section divider ───────────────────────────────
        'giro_divider_title':    "Capitalization Gap",
        'giro_divider_subtitle': (
            "Potential distribution, capitalization gap and commercial\n"
            "prioritization by outlet type (pos_subchannel)."
        ),

        # ── Slide B — Distribution table ──────────────────────
        'dist_title':  "Potential Distribution by Business Type  —  {cat}",
        'dist_expl': (
            "Top 5 business types by contribution to growth potential. "
            "The VH+High % bar indicates commercial maturity: "
            "lime green ≥ 40%, light green < 40%."
        ),
        'dist_col_giro':   "Business Type",
        'dist_col_pdv':    "POS [n]",
        'dist_col_vhh':    "% VH+High",
        'dist_col_aporte': "Growth Contribution",
        'dist_col_venta':  "Avg Sales UC",

        # Insights B
        'dist_i1': "Top 2 business types account for {pct:.1f}% of {cat} growth potential.",
        'dist_i2': "{giro} leads in commercial maturity with {vhh:.0f}% of its POS in Very High+High.",
        'dist_i3_low':  "{giro} has {pdv:,} POS with only {vhh:.0f}% VH+High — highest untapped development opportunity.",
        'dist_i3_high': "{giro} has the highest average sales ({venta} UC/POS), indicating replication potential.",

        # ── Slide C — Brecha ───────────────────────────────────
        'brecha_title': "Capitalization Gap  —  {cat}",
        'brecha_expl': (
            "Comparison between current average sales (UC/month) and estimated "
            "additional potential per POS. The green bar represents the uncaptured "
            "monthly growth opportunity. A larger +X indicates higher expected return per POS."
        ),
        'brecha_legend_actual':    "Avg. Current Sales UC",
        'brecha_legend_potencial': "Avg. Additional Potential UC",
        'brecha_xlabel':           "UC/month per POS (average)",

        # Insights C
        'brecha_i1': "Largest gap: {giro} with +{val:,.0f} UC/POS of additional monthly potential.",
        'brecha_i2': "{giro} shows the best potential/base ratio ({pct:.0f}%) — high conversion efficiency.",
        'brecha_i3': "Total uncaptured potential in top 5 types: {total} UC/month of additional growth.",

        # ── Slide D — Scatter ──────────────────────────────────
        'scatter_title': "Commercial Prioritization Map  —  {cat}",
        'scatter_expl': (
            "Each dot is a business type. X axis = % POS with Very High+High; "
            "Y axis = total growth potential; size = number of POS. "
            "Top-right quadrant (High Priority) = high potential AND high maturity."
        ),
        'scatter_xlabel': "% POS with VH + High Potential",
        'scatter_ylabel': "Total Growth Potential (UC/month)",
        'scatter_q_alta':    "High Priority",
        'scatter_q_desar':   "Develop",
        'scatter_q_mant':    "Maintain",
        'scatter_q_monit':   "Monitor",
        'scatter_yformat':   lambda v: f'{v/1000:.0f}k' if v >= 1000 else f'{v:.0f}',

        # Insights D
        'scatter_i1': "High Priority ({n} type(s)): {names}. High % VH+High AND high potential — focus actions here.",
        'scatter_i2_desar': "Develop ({n} type(s)): {names}. High total potential with low % VH+High — untapped clients.",
        'scatter_i2_mant':  "Maintain ({n} type(s)): high % VH+High but lower volume. Consolidate and defend share.",
        'scatter_i3': "Bubble size reflects number of POS. Large bubbles in 'Develop' represent the biggest structural opportunity.",

        # ── Brecha slide (type 18 XML clone) ──────────────────
        'brecha18_title':   "Capitalization Gap – {cat}",
        'brecha18_insight': (
            "The largest growth gap is in {giro1} with an increase of "
            "+{gap:.0f} additional potential monthly. "
            "{giro2} shows the best potential/base ratio ({eff:.0f}%), "
            "high conversion efficiency."
        ),
        'brecha18_expl': (
            "Comparison between current average sales (UC/month) and estimated "
            "additional potential per POS. The green bar represents uncaptured "
            "monthly growth opportunity. A larger +X indicates higher expected return per POS."
        ),
    },


    # ─────────────────────────────────────────────────────────────
    # PORTUGUÊS
    # ─────────────────────────────────────────────────────────────
    'pt': {

        # ── Slide 7 narrative ──────────────────────────────────
        's7_nar': (
            "{pct_clientes}% dos clientes (~{k_clientes}k) têm a maior contribuição "
            "ao crescimento total ({pct_vol}%)."
        ),
        's7_nar_vh': (
            "A contribuição de crescimento de volume (UC) dos clientes Very High, "
            "com base na média mensal, é de {vh_pct}% ({vh_vol}{vh_suf}) do "
            "total do potencial de crescimento do portfólio ({total_vol})."
        ),

        # ── Slide 8 narrative ──────────────────────────────────
        's8_nar': (
            "{best_cat} é a categoria que apresenta maior crescimento, com "
            "{best_pct}% em Very High, seguida por {second_cat} com {second_pct}%. "
            "Para gerar um impacto mais direto, os esforços devem ser concentrados "
            "nesses dois segmentos."
        ),

        # ── Embudo detail strings ──────────────────────────────
        'embudo_n1_detail': "{vol} UC/mês - {pos}K clientes",
        'embudo_n2_detail': "{vol} UC/mês - {pos}K clientes",
        'embudo_n3_detail': "{vol} UC/mês - {pos}K clientes",
        'embudo_n2_pct':    "Este subcanal concentra {pct_vol}% do volume e {pct_com}% dos estabelecimentos",
        'embudo_n3_pct':    "A maior parte da oportunidade está nestas cidades, concentrando {pct_vol}% do volume e {pct_pos}% dos PDVs",
        'embudo_n1_label':  "Very High e High",
        'clientes_seg':     "Clientes segmentados",
        'uc_mes':           "UC/mês",

        # ── Slide 11 map ───────────────────────────────────────
        's11_nar': (
            "Foram identificados {pos1} PDVs em {city1} com crescimento médio de "
            "{pct1}%, enquanto em {city2} há {pos2} PDVs com média de {pct2}%."
        ),
        's11_title': "{city1} e {city2}",

        # ── Giro section divider ───────────────────────────────
        'giro_divider_title':    "Brecha de Capitalização",
        'giro_divider_subtitle': (
            "Distribuição do potencial, brecha de capitalização e priorização\n"
            "comercial por tipo de ponto de venda (pos_subchannel)."
        ),

        # ── Slide B — Distribution table ──────────────────────
        'dist_title':  "Distribuição do Potencial por Tipo de Negócio  —  {cat}",
        'dist_expl': (
            "Esta tabela mostra os 5 tipos de negócio com maior contribuição ao "
            "crescimento potencial. A barra % VH+High indica a maturidade comercial: "
            "verde-lima ≥ 40%, verde suave < 40%."
        ),
        'dist_col_giro':   "Tipo de Negócio",
        'dist_col_pdv':    "PDV [n]",
        'dist_col_vhh':    "% VH+High",
        'dist_col_aporte': "Contribuição Crescimento",
        'dist_col_venta':  "Venda Méd. UC",

        # Insights B
        'dist_i1': "Os 2 principais tipos concentram {pct:.1f}% do potencial de crescimento de {cat}.",
        'dist_i2': "{giro} lidera em maturidade comercial com {vhh:.0f}% de seus PDVs em Very High+High.",
        'dist_i3_low':  "{giro} tem {pdv:,} PDVs com apenas {vhh:.0f}% VH+High — maior oportunidade de desenvolvimento.",
        'dist_i3_high': "{giro} tem a maior venda média ({venta} UC/PDV), indicando potencial de replicação.",

        # ── Slide C — Brecha ───────────────────────────────────
        'brecha_title': "Brecha de Capitalização  —  {cat}",
        'brecha_expl': (
            "Comparação entre a venda média atual (UC/mês) e o potencial adicional "
            "estimado por PDV. A barra verde representa a oportunidade de crescimento "
            "mensal não capitalizado. Um +X maior indica maior retorno esperado por PDV."
        ),
        'brecha_legend_actual':    "Venda Atual Méd. UC",
        'brecha_legend_potencial': "Potencial Adicional Méd. UC",
        'brecha_xlabel':           "UC/mês por PDV (média)",

        # Insights C
        'brecha_i1': "Maior brecha: {giro} com +{val:,.0f} UC/PDV de potencial adicional mensal.",
        'brecha_i2': "{giro} apresenta a melhor relação potencial/base ({pct:.0f}%) — alta eficiência de conversão.",
        'brecha_i3': "Potencial total não capitalizado no top 5: {total} UC/mês de crescimento adicional.",

        # ── Slide D — Scatter ──────────────────────────────────
        'scatter_title': "Mapa de Priorização Comercial  —  {cat}",
        'scatter_expl': (
            "Cada ponto é um tipo de negócio. Eixo X = % PDVs com Very High+High; "
            "eixo Y = potencial total de crescimento; tamanho = número de PDVs. "
            "Quadrante superior-direito (Prioridade Alta) = alto potencial E alta maturidade."
        ),
        'scatter_xlabel': "% PDVs com Potencial VH + High",
        'scatter_ylabel': "Potencial Total de Crescimento (UC/mês)",
        'scatter_q_alta':    "Prioridade Alta",
        'scatter_q_desar':   "Desenvolver",
        'scatter_q_mant':    "Manter",
        'scatter_q_monit':   "Monitorar",
        'scatter_yformat':   lambda v: f'{v/1000:.0f}k' if v >= 1000 else f'{v:.0f}',

        # Insights D
        'scatter_i1': "Prioridade Alta ({n} tipo(s)): {names}. Alto % VH+High E alto potencial — concentrar ações aqui.",
        'scatter_i2_desar': "Desenvolver ({n} tipo(s)): {names}. Grande potencial total com baixo % VH+High — clientes por ativar.",
        'scatter_i2_mant':  "Manter ({n} tipo(s)): alto % VH+High mas menor volume. Consolidar e defender participação.",
        'scatter_i3': "O tamanho de cada bolha reflete o número de PDVs. Bolhas grandes em 'Desenvolver' representam a maior oportunidade estrutural.",

        # ── Brecha slide (type 18 XML clone) ──────────────────
        'brecha18_title':   "Brecha de Capitalização – {cat}",
        'brecha18_insight': (
            "A maior brecha de crescimento está em {giro1}, com aumento de "
            "+{gap:.0f} potencial adicional mensal. "
            "{giro2} apresenta a melhor relação potencial/base ({eff:.0f}%), "
            "alta eficiência de conversão."
        ),
        'brecha18_expl': (
            "Comparação entre a venda média atual (UC/mês) e o potencial adicional "
            "estimado por PDV. A barra verde representa a oportunidade de crescimento "
            "mensal não capitalizado. Um +X maior indica maior retorno esperado por PDV."
        ),
    },
}

# Language display names for intake question
LANG_OPTIONS = {
    'es': 'Español',
    'en': 'English',
    'pt': 'Português',
}

def get(lang: str, key: str, **kwargs) -> str:
    """Get translated string, falling back to Spanish if key not found."""
    lang = lang.lower()[:2]
    if lang not in T:
        lang = 'es'
    text = T[lang].get(key, T['es'].get(key, f'[{key}]'))
    if callable(text):
        return text
    return text.format(**kwargs) if kwargs else text
