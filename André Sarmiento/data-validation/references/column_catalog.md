# Catálogo de Columnas Esperadas

## Maestra de Clientes

### Columnas Obligatorias

| Nombre Interno | Descripción | Aliases Conocidos |
|---|---|---|
| `pos_id` | Identificador único del punto de venta | Cliente, cod_cliente, client_id, id_cliente, cliente_id_key, COD_CLIENTE, codigo_cliente |
| `pos_name` | Nombre del punto de venta | Nombre del Cliente, nombre_cliente, pos_nombre, razon_social, NOMBRE |
| `pos_latitude` | Latitud del POS | Coordenada Y, latitud, lat, LATITUDE, y, coord_y, LAT |
| `pos_longitude` | Longitud del POS | Coordenada X, longitud, lon, long, LONGITUDE, x, coord_x, LON |
| `pos_city` | Ciudad o municipio | Nombre Municipio, municipio, ciudad, city, CIUDAD, MUNICIPIO |
| `pos_subchannel` | Subcanal de venta | Descr. Canal, subcanal, sub_canal, subchannel, SUBCANAL |
| `pos_channel` | Canal de venta | Descr. Canal País, canal, channel, CANAL |

### Columnas Opcionales

| Nombre Interno | Descripción | Aliases Conocidos |
|---|---|---|
| `pos_address` | Dirección del POS | Calle, direccion, address, CALLE, DIRECCION, pos_addres |
| `pos_consumer_type` | Tipo de consumidor (On/Off Premise). **Opcional** — si no existe pero hay `pos_subchannel`, se puede derivar automáticamente como `pos_consumer_type_internal`. Ver `scripts/derive_consumer_type.py` | Descr. Tipo de Canal de Cliente, tipo_consumidor, consumer_type, TIPO_CANAL, tipo de canal |
| `pos_size_classification` | Clasificación de tamaño | Descr. GEC, size, tamaño, clasificacion, GEC |
| `pos_fecha_alta` | Fecha de incorporación | Fecha de alta, fecha_alta, alta, date_open |
| `pos_fecha_baja` | Fecha de desvinculación | Fecha de Baja, fecha_baja, baja, date_close, inactivo |
| `pos_neighborhood` | Colonia / barrio | colonia, barrio, neighborhood, COLONIA |
| `pos_region` | Región o zona | region, zona, zone, REGION |
| `segmentacion` | Segmentación asignada | segmento, segment, SEGMENTO |

---

## Maestra de Productos

### Columnas Obligatorias

| Nombre Interno | Descripción | Aliases Conocidos |
|---|---|---|
| `product_id` | Identificador único del producto | src_prod_cd, cod_producto, product_code, producto_id_key, SKU, sku |
| `product_name` | Nombre del producto | BPP_Name, nombre_producto, descripcion_producto, product_description |
| `product_brand` | Marca del producto | Brand_Group, marca_producto, brand, MARCA |
| `global_category` | Categoría global | Category_Group, categoria_global, global_cat |
| `serving_type` | Tipo de envase/presentación | Serving_Type, tipo_envase, presentacion, serving |
| `refillability` | Retornable o no retornable | LT1_4_Refillability, retornable, refillable, RETORNABLE |

### Columnas Opcionales

| Nombre Interno | Descripción | Aliases Conocidos |
|---|---|---|
| `product_subcategory` | Subcategoría | Sub_Category, subcategoria, sub_cat |
| `product_category` | Categoría | Category, categoria, cat |

---

## Ventas

### Columnas Obligatorias

| Nombre Interno | Descripción | Aliases Conocidos |
|---|---|---|
| `pos_id` | Identificador del punto de venta | cliente_id_key, cod_cliente, client_id, POS_ID |
| `product_id` | Identificador del producto | producto_id_key, cod_producto, SKU, sku |
| `unit_cases` | Unidades / cajas vendidas | cajas, units, cases, cantidad, volumen, CAJAS |
| `fecha` | Fecha de la venta | fecha_entrega, week_445, date, FECHA, semana |

### Columnas Opcionales

| Nombre Interno | Descripción | Aliases Conocidos |
|---|---|---|
| `month` | Mes en formato YYYYMM | month_445, mes, MONTH |
| `n_active_months` | Meses activos del POS | meses_activos, active_months |

---

## Notas de Mapeo

1. **Fuzzy matching**: Si la similitud entre el nombre de columna y el alias es ≥ 70%, proponer como candidato con `⚠️`
2. **Columnas con espacios al inicio**: Común en exports de SAP (ej: `     Coordenada X`). Hacer `.strip()` antes de comparar.
3. **Mayúsculas/minúsculas**: Ignorar al comparar (usar `.lower()`)
4. **Caracteres especiales**: Normalizar tildes y ñ antes de comparar (ej: `Dirección` → `direccion`)
