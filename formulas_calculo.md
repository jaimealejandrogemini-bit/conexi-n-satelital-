# Fórmulas y Algoritmos para Diseño de Enlaces de Microondas

## 1. Cálculo de Distancia entre Dos Puntos

### Fórmula de Haversine
Para calcular la distancia ortodrómica (distancia más corta sobre la superficie terrestre) entre dos puntos dados por sus coordenadas geográficas:

```python
import math

def calcular_distancia(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos geográficos usando la fórmula de Haversine.
    Parámetros:
    - lat1, lon1: Latitud y longitud del punto 1 (en grados)
    - lat2, lon2: Latitud y longitud del punto 2 (en grados)
    Retorna: Distancia en kilómetros
    """
    R = 6371  # Radio terrestre medio en km
    
    # Convertir a radianes
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Fórmula de Haversine
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distancia = R * c
    return distancia
```

## 2. Cálculo de Azimut

El azimut es el ángulo horizontal desde el norte verdadero hasta el punto de interés.

```python
def calcular_azimut(lat1, lon1, lat2, lon2):
    """
    Calcula el azimut desde el punto 1 hacia el punto 2.
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    azimut = math.atan2(x, y)
    azimut = math.degrees(azimut)
    azimut = (azimut + 360) % 360  # Normalizar a 0-360 grados
    
    return azimut
```

## 3. Cálculo de Altura de Torres

### Método Trigonométrico Básico
Para garantizar línea de vista (LOS), la altura de las torres debe considerar la curvatura terrestre y el despejamiento de la primera zona de Fresnel.

```python
def calcular_altura_torre(distancia_km, altura_terreno_1, altura_terreno_2, radio_tierra=6371):
    """
    Calcula la altura mínima necesaria de las torres para mantener LOS.
    
    Parámetros:
    - distancia_km: Distancia entre puntos en km
    - altura_terreno_1: Altura del terreno en punto 1 (m)
    - altura_terreno_2: Altura del terreno en punto 2 (m)
    - radio_tierra: Radio terrestre en km (default: 6371 km)
    
    Retorna: Tupla (altura_torre_1, altura_torre_2) en metros
    """
    # Corrección por curvatura terrestre
    # d^2 / (8 * R) da la altura de curvatura en el punto medio
    d_km = distancia_km
    curvatura = (d_km ** 2) / (8 * radio_tierra) * 1000  # en metros
    
    # Altura mínima considerando línea de vista directa
    # Para un enlace sin repetidor, ambas torres deben estar a la misma altura
    # sobre el terreno para mantener línea de vista
    altura_minima = curvatura + 10  # 10m adicional como margen de seguridad
    
    return altura_minima
```

### Cálculo de Despejamiento de Zona de Fresnel
La primera zona de Fresnel debe estar libre para evitar pérdidas significativas.

```python
def calcular_radio_fresnel(distancia_km, frecuencia_ghz):
    """
    Calcula el radio de la primera zona de Fresnel en el punto medio.
    
    Parámetros:
    - distancia_km: Distancia total del enlace en km
    - frecuencia_ghz: Frecuencia de operación en GHz
    
    Retorna: Radio de la primera zona de Fresnel en metros
    """
    # Radio de la primera zona de Fresnel
    # λ = c/f, donde c = 3e8 m/s, f en Hz
    longitud_onda = 0.299792458 / frecuencia_ghz  # en metros
    
    d_km = distancia_km
    d1 = d_km / 2  # Distancia al punto medio
    d2 = d_km / 2
    
    # Radio de la primera zona de Fresnel
    radio_fresnel = 549 * math.sqrt((d1 * d2) / (frecuencia_ghz * d_km))
    
    return radio_fresnel
```

## 4. Cálculo de Inclinación de Antenas

```python
def calcular_inclinacion(altura_torre_1, altura_torre_2, distancia_m):
    """
    Calcula el ángulo de inclinación de las antenas.
    
    Parámetros:
    - altura_torre_1: Altura de la torre 1 en metros
    - altura_torre_2: Altura de la torre 2 en metros
    - distancia_m: Distancia entre torres en metros
    
    Retorna: Ángulo de inclinación en grados
    """
    diferencia_altura = altura_torre_2 - altura_torre_1
    
    # Ángulo de elevación desde torre 1 hacia torre 2
    inclinacion = math.degrees(math.atan2(diferencia_altura, distancia_m))
    
    return inclinacion
```

## 5. Cálculo de Pérdidas por Propagación

### Pérdidas en el Espacio Libre (Free Space Loss - FSL)

```python
def calcular_perdida_espacio_libre(distancia_km, frecuencia_ghz):
    """
    Calcula las pérdidas en el espacio libre usando el modelo de Friis.
    
    Parámetros:
    - distancia_km: Distancia del enlace en km
    - frecuencia_ghz: Frecuencia de operación en GHz
    
    Retorna: Pérdidas en dB
    """
    # FSL = 20*log10(d) + 20*log10(f) + 32.44
    # donde d en km y f en MHz
    
    # Convertir a MHz
    frecuencia_mhz = frecuencia_ghz * 1000
    
    fsl = 20 * math.log10(distancia_km) + 20 * math.log10(frecuencia_mhz) + 32.44
    
    return fsl
```

### Pérdidas por Lluvia (ITU-R P.530)

```python
def calcular_perdida_lluvia(distancia_km, frecuencia_ghz, latitud, Disponibilidad=99.99):
    """
    Calcula las pérdidas por lluvia según ITU-R P.530.
    
    Parámetros:
    - distancia_km: Distancia del enlace en km
    - frecuencia_ghz: Frecuencia en GHz
    - latitud: Latitud del enlace en grados
    - Disponibilidad: Porcentaje de disponibilidad (default 99.99%)
    
    Retorna: Pérdidas por lluvia en dB
    """
    # Intensidad de lluvia para diferentes disponibilidades
    # Valores típicos para Colombia (zona tropical)
    R_001 = 100  # mm/h para 0.01% del tiempo (disponibilidad 99.99%)
    
    # Factor de reducción
    gamma = 0.036 * frecuencia_ghz ** 0.6
    
    #longitud efectiva del enlace
    if distancia_km <= 10:
        longitud_efectiva = distancia_km
    else:
        longitud_efectiva = 10 * (1 - math.exp(-distancia_km / 10))
    
    # Pérdidas por lluvia
    perdidas_lluvia = gamma * R_001 * longitud_efectiva
    
    return perdidas_lluvia
```

### Pérdidas Totales

```python
def calcular_perdidas_totales(distancia_km, frecuencia_ghz, latitud, disponibilidad=99.99):
    """
    Calcula las pérdidas totales del enlace.
    """
    # Pérdidas en el espacio libre
    fsl = calcular_perdida_espacio_libre(distancia_km, frecuencia_ghz)
    
    # Pérdidas por lluvia
    lluvia = calcular_perdida_lluvia(distancia_km, frecuencia_ghz, latitud, disponibilidad)
    
    # Pérdidas por gases atmosféricos (a frecuencias > 10 GHz)
    if frecuencia_ghz > 10:
        # Pérdidas por oxígeno y vapor de agua
        perdidas_gases = 0.01 * distancia_km * frecuencia_ghz
    else:
        perdidas_gases = 0
    
    # Pérdidas totales
    perdidas_totales = fsl + lluvia + perdidas_gases
    
    return {
        'fsl': fsl,
        'lluvia': lluvia,
        'gases': perdidas_gases,
        'total': perdidas_totales
    }
```

## 6. Diseño de Repetidores

```python
def disenar_repetidor(lat1, lon1, alt1, lat2, lon2, alt2, distancia_minima=100):
    """
    Diseña la ubicación de un repetidor intermediano.
    
    Parámetros:
    - lat1, lon1, alt1: Coordenadas y altitud del punto 1
    - lat2, lon2, alt2: Coordenadas y altitud del punto 2
    - distancia_minima: Distancia mínima entre ciudades (km)
    
    Retorna: Coordenadas del repetidor y parámetros del enlace
    """
    # Calcular distancia total
    distancia_total = calcular_distancia(lat1, lon1, lat2, lon2)
    
    if distancia_total < distancia_minima:
        return None  # No se necesita repetidor
    
    # Ubicación del repetidor (punto medio)
    lat_repetidor = (lat1 + lat2) / 2
    lon_repetidor = (lon1 + lon2) / 2
    
    # Dividir el enlace en dos segmentos
    distancia_segmento = distancia_total / 2
    
    # Calcular altura de torres para cada segmento
    altura_torre_1 = calcular_altura_torre(distancia_segmento, alt1, alt2)
    altura_torre_2 = calcular_altura_torre(distancia_segmento, alt2, alt1)
    
    return {
        'latitud': lat_repetidor,
        'longitud': lon_repetidor,
        'distancia_segmento': distancia_segmento,
        'altura_torre_1': altura_torre_1,
        'altura_torre_2': altura_torre_2
    }
```

## 7. Cálculo de Balance de Potencia del Enlace

```python
def calcular_balance_potencia(pt_dbm, gt_dbi, gr_dbi, perdidas_total, sensibilidad_dbm):
    """
    Calcula el margen del enlace.
    
    Parámetros:
    - pt_dbm: Potencia de transmisión en dBm
    - gt_dbi: Ganancia de antenna transmisora en dBi
    - gr_dbi: Ganancia de antenna receptora en dBi
    - perdidas_total: Pérdidas totales del enlace en dB
    - sensibilidad_dbm: Sensibilidad del receptor en dBm
    
    Retorna: Margen del enlace en dB
    """
    # Potencia recibida
    pr_dbm = pt_dbm + gt_dbi + gr_dbi - perdidas_total
    
    # Margen del enlace
    margen = pr_dbm - sensibilidad_dbm
    
    return {
        'potencia_recibida': pr_dbm,
        'margen': margen,
        'estado': 'OK' if margen > 10 else 'ADVERTENCIA' if margen > 0 else 'FALLO'
    }
```

## Referencias

1. ITU-R P.530-17: Propagation data and prediction methods required for the design of terrestrial line-of-sight systems
2. ITU-R F.1101: Characteristics of fixed service digital transmission systems
3. Freeman & Co: "Radio System Design for Telecommunications"
4. Rappaport, T.S.: "Wireless Communications: Principles and Practice"
