"""
translations.py
Módulo de traducciones para el skill de validación de datos.
Soporta: Español (es), English (en), Português (pt)

Uso:
    from scripts.translations import T
    t = T("es")  # or "en" or "pt"
    print(t("report_title"))
"""

TRANSLATIONS = {

    # ── Portada / Cover ───────────────────────────────────────────────────────
    "report_title": {
        "es": "Reporte de Calidad de Datos",
        "en": "Data Quality Report",
        "pt": "Relatório de Qualidade de Dados",
    },
    "report_subtitle": {
        "es": "Revisión de la Base de Clientes",
        "en": "Customer Database Review",
        "pt": "Revisão da Base de Clientes",
    },

    # ── Secciones principales ────────────────────────────────────────────────
    "section_summary": {
        "es": "¿Qué encontramos en tu base de datos?",
        "en": "What did we find in your database?",
        "pt": "O que encontramos na sua base de dados?",
    },
    "section_summary_intro": {
        "es": "Antes de poder usar tu información para el proyecto, revisamos la calidad de cada registro. A continuación te mostramos los principales hallazgos:",
        "en": "Before using your data for the project, we reviewed the quality of each record. Below are the main findings:",
        "pt": "Antes de usar suas informações para o projeto, revisamos a qualidade de cada registro. A seguir apresentamos os principais achados:",
    },
    "section_intro_title": {
        "es": "Introducción",
        "en": "Introduction",
        "pt": "Introdução",
    },
    "section_intro_body": {
        "es": "Este reporte explica en qué estado llegó la información de clientes que nos fue entregada y qué ajustes se realizaron para dejarla lista para el proyecto.",
        "en": "This report explains the state of the customer data delivered to us and what adjustments were made to prepare it for the project.",
        "pt": "Este relatório explica o estado em que chegaram as informações de clientes e quais ajustes foram realizados para deixá-las prontas para o projeto.",
    },
    "section_detail_title": {
        "es": "Detalle por tipo de información",
        "en": "Detail by information type",
        "pt": "Detalhe por tipo de informação",
    },
    "section_clients": {
        "es": "Base de Clientes (Maestra de Clientes)",
        "en": "Customer Database (Master Clients)",
        "pt": "Base de Clientes (Mestra de Clientes)",
    },
    "section_actions": {
        "es": "¿Qué necesitamos confirmar o corregir contigo?",
        "en": "What do we need to confirm or correct with you?",
        "pt": "O que precisamos confirmar ou corrigir com você?",
    },

    # ── Campos de metadata ───────────────────────────────────────────────────
    "field_download_date": {
        "es": "Fecha de Descarga",
        "en": "Download Date",
        "pt": "Data de Download",
    },
    "field_file": {
        "es": "File",
        "en": "File",
        "pt": "Arquivo",
    },

    # ── Subsecciones ─────────────────────────────────────────────────────────
    "subsection_identifier": {
        "es": "Identificador de cliente (Cliente):",
        "en": "Customer Identifier (Customer ID):",
        "pt": "Identificador do cliente (Cliente):",
    },
    "subsection_geo": {
        "es": "Ubicación geográfica:",
        "en": "Geographic Location:",
        "pt": "Localização geográfica:",
    },
    "subsection_filters": {
        "es": "Resumen de los ajustes realizados:",
        "en": "Summary of adjustments made:",
        "pt": "Resumo dos ajustes realizados:",
    },
    "subsection_city": {
        "es": "Distribución por Ciudad:",
        "en": "Distribution by City:",
        "pt": "Distribuição por Cidade:",
    },
    "subsection_subchannel": {
        "es": "Distribución por Tipo de Negocio (Subcanal):",
        "en": "Distribution by Business Type (Subchannel):",
        "pt": "Distribuição por Tipo de Negócio (Subcanal):",
    },
    "subsection_channel": {
        "es": "Distribución por Canal de Venta:",
        "en": "Distribution by Sales Channel:",
        "pt": "Distribuição por Canal de Vendas:",
    },

    # ── Bullets del resumen ───────────────────────────────────────────────────
    "bullet_outside_territory": {
        "es": "De los {total} clientes, {fuera} ({pct}%) estaban fuera del territorio de la operación y fueron descartados.",
        "en": "Out of {total} customers, {fuera} ({pct}%) were outside the operation territory and were discarded.",
        "pt": "De {total} clientes, {fuera} ({pct}%) estavam fora do território de operação e foram descartados.",
    },
    "bullet_no_pos_name": {
        "es": "No fue posible verificar duplicados por nombre ya que la base no contiene pos_name. Se recomienda obtener este dato del embotellador.",
        "en": "Duplicate verification by name was not possible since the database does not contain pos_name. It is recommended to obtain this data from the bottler.",
        "pt": "Não foi possível verificar duplicatas por nome pois a base não contém pos_name. Recomenda-se obter esse dado do engarrafador.",
    },
    "bullet_dups": {
        "es": "{dups} registros tienen duplicados de latitud, longitud y nombre por lo cual fueron eliminados.",
        "en": "{dups} records have duplicate latitude, longitude and name and were removed.",
        "pt": "{dups} registros têm duplicatas de latitude, longitude e nome e foram removidos.",
    },
    "bullet_zero_coords": {
        "es": "{zero} clientes tienen coordenadas con valor cero (0,0), lo que indica que no se capturó su ubicación correctamente.",
        "en": "{zero} customers have zero coordinates (0,0), indicating their location was not properly captured.",
        "pt": "{zero} clientes têm coordenadas com valor zero (0,0), indicando que sua localização não foi capturada corretamente.",
    },
    "bullet_no_address": {
        "es": "La base no contiene pos_name ni pos_address. Estos datos son importantes para identificar cada punto de venta.",
        "en": "The database does not contain pos_name or pos_address. These are important fields to identify each point of sale.",
        "pt": "A base não contém pos_name nem pos_address. Esses dados são importantes para identificar cada ponto de venda.",
    },
    "bullet_address_nulls": {
        "es": "{addr_null} clientes ({pct}%) no tienen dirección registrada (pos_address).",
        "en": "{addr_null} customers ({pct}%) have no registered address (pos_address).",
        "pt": "{addr_null} clientes ({pct}%) não têm endereço registrado (pos_address).",
    },
    "bullet_all_complete": {
        "es": "Todos los clientes tienen nombre y dirección registrada.",
        "en": "All customers have name and address registered.",
        "pt": "Todos os clientes têm nome e endereço registrados.",
    },
    "bullet_city_nulls": {
        "es": "{city_null} clientes ({pct}%) no tienen ciudad, subcanal ni tipo de canal registrado.",
        "en": "{city_null} customers ({pct}%) have no registered city, subchannel or channel type.",
        "pt": "{city_null} clientes ({pct}%) não têm cidade, subcanal ou tipo de canal registrado.",
    },
    "bullet_all_city": {
        "es": "Todos los clientes tienen ciudad registrada.",
        "en": "All customers have a registered city.",
        "pt": "Todos os clientes têm cidade registrada.",
    },
    "bullet_fecha_baja": {
        "es": "{con_baja} clientes ({pct}%) tienen fecha de baja ({fb_min} → {fb_max}). Se mantienen para prospección.",
        "en": "{con_baja} customers ({pct}%) have a deactivation date ({fb_min} → {fb_max}). They are kept for prospecting.",
        "pt": "{con_baja} clientes ({pct}%) têm data de desativação ({fb_min} → {fb_max}). São mantidos para prospecção.",
    },
    "bullet_pos_final": {
        "es": "Total de clientes listos para usar: {pos_final} registros.",
        "en": "Total customers ready to use: {pos_final} records.",
        "pt": "Total de clientes prontos para uso: {pos_final} registros.",
    },

    # ── Textos de sección ────────────────────────────────────────────────────
    "text_total_clients": {
        "es": "La base contiene {total} clientes en total. Cada uno tiene un código único que permite identificarlo sin confusión.",
        "en": "The database contains {total} customers in total. Each one has a unique code for unambiguous identification.",
        "pt": "A base contém {total} clientes no total. Cada um tem um código único que permite identificá-lo sem confusão.",
    },
    "text_outside_geo": {
        "es": "{fuera} clientes ({pct}%) aparecían fuera del territorio de operación de {client} y fueron excluidos.",
        "en": "{fuera} customers ({pct}%) appeared outside the {client} operation territory and were excluded.",
        "pt": "{fuera} clientes ({pct}%) apareciam fora do território de operação de {client} e foram excluídos.",
    },
    "text_discarded": {
        "es": "En total se descartaron {total_desc} clientes ({pct}%).",
        "en": "A total of {total_desc} customers ({pct}%) were discarded.",
        "pt": "No total, {total_desc} clientes ({pct}%) foram descartados.",
    },
    "text_city_distribution": {
        "es": "Los clientes están distribuidos en múltiples zonas y franquicias dentro del territorio.",
        "en": "Customers are distributed across multiple zones and franchises within the territory.",
        "pt": "Os clientes estão distribuídos em múltiplas zonas e franquias dentro do território.",
    },
    "text_subchannel": {
        "es": "{top1}, {top2} y {top3} representan el {pct}% de todos los puntos de venta.",
        "en": "{top1}, {top2} and {top3} represent {pct}% of all points of sale.",
        "pt": "{top1}, {top2} e {top3} representam {pct}% de todos os pontos de venda.",
    },
    "text_channel": {
        "es": "Canal predominante: {channel} con el {pct}% de los clientes.",
        "en": "Predominant channel: {channel} with {pct}% of customers.",
        "pt": "Canal predominante: {channel} com {pct}% dos clientes.",
    },

    # ── Puntos de acción ─────────────────────────────────────────────────────
    "action_no_pos_name": {
        "es": "La base no incluye pos_name ni pos_address. ¿Es posible obtener estos datos del embotellador?",
        "en": "The database does not include pos_name or pos_address. Is it possible to obtain these from the bottler?",
        "pt": "A base não inclui pos_name nem pos_address. É possível obter esses dados do engarrafador?",
    },
    "action_outside_geo": {
        "es": "Se excluyeron {fuera} clientes fuera del territorio. ¿Confirmas que el GeoJSON representa correctamente el área de operación?",
        "en": "{fuera} customers outside the territory were excluded. Do you confirm the GeoJSON correctly represents the operation area?",
        "pt": "{fuera} clientes fora do território foram excluídos. Você confirma que o GeoJSON representa corretamente a área de operação?",
    },
    "action_zero_coords": {
        "es": "{zero} clientes tienen coordenadas en cero. ¿Pueden corregirse desde el sistema fuente antes de continuar?",
        "en": "{zero} customers have zero coordinates. Can these be corrected from the source system before continuing?",
        "pt": "{zero} clientes têm coordenadas em zero. Podem ser corrigidos no sistema de origem antes de continuar?",
    },
    "action_fecha_baja": {
        "es": "{con_baja} clientes con fecha de baja se mantienen para prospección. Para segmentación se recomienda eliminarlos.",
        "en": "{con_baja} customers with a deactivation date are kept for prospecting. For segmentation, it is recommended to remove them.",
        "pt": "{con_baja} clientes com data de desativação são mantidos para prospecção. Para segmentação, recomenda-se removê-los.",
    },

    # ── Cabeceras de tablas ───────────────────────────────────────────────────
    "table_filter":      {"es": "Filtro",               "en": "Filter",           "pt": "Filtro"},
    "table_description": {"es": "Descripción",          "en": "Description",      "pt": "Descrição"},
    "table_affected":    {"es": "Registros Afectados",  "en": "Affected Records", "pt": "Registros Afetados"},
    "table_remaining":   {"es": "POS Restantes",        "en": "Remaining POS",    "pt": "POS Restantes"},
    "table_pct":         {"es": "POS %",                "en": "POS %",            "pt": "POS %"},
    "table_total":       {"es": "Total",                "en": "Total",            "pt": "Total"},
    "table_others":      {"es": "Otros",                "en": "Others",           "pt": "Outros"},
    "table_city":        {"es": "Ciudad",               "en": "City",             "pt": "Cidade"},
    "table_subchannel":  {"es": "Subcanal",             "en": "Subchannel",       "pt": "Subcanal"},
    "table_channel":     {"es": "Canal",                "en": "Channel",          "pt": "Canal"},
    "table_pos_n":       {"es": "POS[n]",               "en": "POS[n]",           "pt": "POS[n]"},
    "table_pos_pct":     {"es": "POS [%]",              "en": "POS [%]",          "pt": "POS [%]"},

    # ── Descripciones de filtros en tabla ─────────────────────────────────────
    "filter_outside": {
        "es": "Clientes con coordenadas fuera del límite operativo.",
        "en": "Customers with coordinates outside the operating boundary.",
        "pt": "Clientes com coordenadas fora do limite operacional.",
    },
    "filter_zero_coords": {
        "es": "Clientes sin ubicación válida (lat=0, lon=0).",
        "en": "Customers without valid location (lat=0, lon=0).",
        "pt": "Clientes sem localização válida (lat=0, lon=0).",
    },
    "filter_dups": {
        "es": "Duplicados con nombre y coordenadas idénticos.",
        "en": "Duplicates with identical name and coordinates.",
        "pt": "Duplicatas com nome e coordenadas idênticos.",
    },
    "filter_no_pos_name": {
        "es": "No se realizó deduplicación por nombre (dato no disponible).",
        "en": "Name-based deduplication was skipped (data not available).",
        "pt": "Deduplicação por nome não foi realizada (dado não disponível).",
    },
    "filter_fecha_baja": {
        "es": "POS con fecha de baja (se mantienen para prospección).",
        "en": "POS with deactivation date (kept for prospecting).",
        "pt": "POS com data de desativação (mantidos para prospecção).",
    },

    # ── Mensajes del chat ─────────────────────────────────────────────────────
    "chat_geojson_found": {
        "es": "Encontré y descargué el GeoJSON de {pais} automáticamente. Continuando con la validación...",
        "en": "I found and downloaded the GeoJSON for {pais} automatically. Continuing with validation...",
        "pt": "Encontrei e baixei o GeoJSON de {pais} automaticamente. Continuando com a validação...",
    },
    "chat_geojson_not_found": {
        "es": "No pude descargar el GeoJSON de {pais} automáticamente. ¿Puedes subirlo manualmente? Puedes descargarlo desde https://www.geoboundaries.org o https://gadm.org",
        "en": "I could not automatically download the GeoJSON for {pais}. Can you upload it manually? You can download it from https://www.geoboundaries.org or https://gadm.org",
        "pt": "Não consegui baixar o GeoJSON de {pais} automaticamente. Você pode fazer o upload manualmente? Você pode baixá-lo em https://www.geoboundaries.org ou https://gadm.org",
    },
    "chat_mapping_confirm": {
        "es": "He identificado el siguiente mapeo de columnas. ¿Todo correcto?",
        "en": "I've identified the following column mapping. Does everything look correct?",
        "pt": "Identifiquei o seguinte mapeamento de colunas. Está tudo correto?",
    },
    "chat_validation_complete": {
        "es": "✅ Validación completa.",
        "en": "✅ Validation complete.",
        "pt": "✅ Validação concluída.",
    },
    "chat_clean_base": {
        "es": "Base limpia: {n} registros",
        "en": "Clean base: {n} records",
        "pt": "Base limpa: {n} registros",
    },
    "chat_issues_base": {
        "es": "Base con problemas: {n} registros",
        "en": "Records with issues: {n}",
        "pt": "Registros com problemas: {n}",
    },

    # ── Pie de página ─────────────────────────────────────────────────────────
    "footer": {
        "es": "Kin Analytics — {client} — Confidencial — {date}",
        "en": "Kin Analytics — {client} — Confidential — {date}",
        "pt": "Kin Analytics — {client} — Confidencial — {date}",
    },
}


class T:
    """
    Clase de traducción. Instanciar con el código de idioma y llamar como función.

    Ejemplo:
        t = T("en")
        texto = t("bullet_pos_final", pos_final="45,164")
        # → "Total customers ready to use: 45,164 records."
    """

    SUPPORTED = {"es", "en", "pt"}
    DEFAULT   = "es"

    def __init__(self, lang: str = "es"):
        lang = lang.lower().strip()
        self.lang = lang if lang in self.SUPPORTED else self.DEFAULT

    def __call__(self, key: str, **kwargs) -> str:
        """
        Obtiene el texto en el idioma seleccionado y aplica formato con kwargs.
        Si la clave no existe, devuelve la clave misma como fallback.
        """
        entry = TRANSLATIONS.get(key, {})
        text  = entry.get(self.lang, entry.get(self.DEFAULT, key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

    def lang_name(self) -> str:
        return {"es": "Español", "en": "English", "pt": "Português"}.get(self.lang, self.lang)
