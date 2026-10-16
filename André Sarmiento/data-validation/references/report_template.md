# Estructura del Reporte Word — Plantilla Kin Analytics

## Estructura general del documento

```
1. Portada
   - Título: "Validación de Información"
   - Subtítulo: "— [Cliente] —"
   - Project, Company, Version, Fecha, Confidencial

2. Resumen Ejecutivo
   - Integridad y cobertura (bullets con los hallazgos principales)
   - POS finales previstos (en negrita)

3. Introducción
   - Párrafo estándar explicando el objetivo del informe

4. [Por cada base recibida]:
   4a. Maestra de Clientes
       - Identificador de cliente
       - Ubicación geográfica del POS
       - Filtros de calidad (tabla)
       - Ciudad (tabla top 10 + Otros)
       - Subchannel (tabla)
       - Channel (tabla)
       - Customer Type (tabla, si existe)
       - Size Classification (tabla, si existe)
       - Puntos de acción

   4b. Maestra de Productos
       - Totales y únicos
       - Duplicados
       - Valores vacíos (tabla)
       - Brand (tabla)
       - Global Category (tabla)
       - Serving Type (tabla)
       - Refillability (tabla)

   4c. Base de Ventas
       - Totales y rango de fechas
       - Cobertura de clientes (tabla)
       - Actividad por POS — buckets 24 meses (tabla)

5. Insights Adicionales y Recomendaciones
   - Hallazgos no estándar detectados automáticamente
```

## Notas de formato

- **Cabeceras de tabla**: Fondo `#1F2937` (azul oscuro), texto blanco, negrita
- **Filas alternas**: Fondo `#F2F2F2` (gris claro)
- **Alineación de tablas**: Centrada
- **Márgenes**: 2.5cm arriba/abajo, 3cm izquierda/derecha
- **Pie de página**: "Kin Analytics — [Cliente] — Confidencial — [Fecha]"

## Insights adicionales que Claude debe buscar proactivamente

### En Clientes:
- Concentración geográfica: si el top 3 ciudades > 60% del total
- Coordenadas faltantes: si > 10% de POS no tienen coordenadas
- Tasa de baja alta: si > 30% de POS tienen fecha de baja
- IDs duplicados: si hay pos_id repetidos

### En Productos:
- Productos sin categoría global: impacta el procesamiento de ventas
- Refillability desconocido: confirmar si es NonReturnable
- Emerging Beverages: recordar que se excluye de ventas

### En Ventas:
- Clientes sin ventas: POS que no aparecen en ventas (posibles inactivos no marcados)
- POS en ventas sin maestra: problema de integridad referencial
- Productos en ventas sin maestra: SKUs no reconocidos
- Actividad baja: si < 50% de POS tienen 12+ meses activos

## Variables de personalización por cliente

Cuando el usuario use el skill para un cliente nuevo, debe proporcionar o confirmar:
- `client_name`: Nombre del embotellador/empresa (ej: "Femsa Guatemala")
- `file_name`: Nombre del archivo recibido
- `date_str`: Fecha de descarga de la base
- País/territorio: para validar que el GeoJSON corresponde
