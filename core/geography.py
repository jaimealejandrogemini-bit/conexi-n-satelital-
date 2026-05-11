"""
Módulo de cálculos geográficos y geodésicos para enlaces de microondas.
"""

import math
from core.constants import EARTH_RADIUS_KM, MARGEN_FRESNEL, MARGEN_SEGURIDAD_M


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia ortodrómica entre dos puntos usando la fórmula de Haversine.
    
    Parámetros:
    -----------
    lat1, lon1 : float
        Latitud y longitud del punto 1 en grados decimales
    lat2, lon2 : float
        Latitud y longitud del punto 2 en grados decimales
        
    Retorna:
    --------
    float : Distancia en kilómetros
    """
    # Convertir a radianes
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Fórmula de Haversine
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distancia = EARTH_RADIUS_KM * c
    return distancia


def calculate_azimuth(lat1, lon1, lat2, lon2):
    """
    Calcula el azimut desde el punto 1 hacia el punto 2.
    
    El azimut es el ángulo horizontal medido desde el norte verdadero (0°)
    hacia el este (90°), sur (180°), oeste (270°), etc.
    
    Parámetros:
    -----------
    lat1, lon1 : float
        Latitud y longitud del punto 1 en grados decimales
    lat2, lon2 : float
        Latitud y longitud del punto 2 en grados decimales
        
    Retorna:
    --------
    float : Azimut en grados (0-360)
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)
    
    # Calcular componentes del vector
    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    
    # Calcular azimut
    azimut = math.atan2(x, y)
    azimut = math.degrees(azimut)
    azimut = (azimut + 360) % 360  # Normalizar a 0-360 grados
    
    return azimut


def calculate_reverse_azimuth(lat1, lon1, lat2, lon2):
    """
    Calcula el azimut inverso (desde punto 2 hacia punto 1).
    
    Parámetros:
    -----------
    lat1, lon1 : float
        Latitud y longitud del punto 1 en grados decimales
    lat2, lon2 : float
        Latitud y longitud del punto 2 en grados decimales
        
    Retorna:
    --------
    float : Azimut inverso en grados (0-360)
    """
    return calculate_azimuth(lat2, lon2, lat1, lon1)


def calculate_earth_curvature_correction(distance_km, k=4/3):
    """
    Calcula la corrección por curvatura terrestre.
    
    Parámetros:
    -----------
    distance_km : float
        Distancia entre puntos en kilómetros
    k : float
        Factor k del radio terrestre (típico 4/3)
        
    Retorna:
    --------
    float : Corrección en metros (altura adicional por curvatura en punto medio)
    """
    R = EARTH_RADIUS_KM * k  # Radio terrestre efectivo
    # Altura de la curvatura en el punto medio: d²/(8R)
    curvatura = (distance_km ** 2) / (8 * R) * 1000  # Convertir a metros
    return curvatura


def calculate_first_fresnel_radius(distance_km, frequency_ghz):
    """
    Calcula el radio de la primera zona de Fresnel en el punto medio.
    
    Parámetros:
    -----------
    distance_km : float
        Distancia total del enlace en kilómetros
    frequency_ghz : float
        Frecuencia de operación en GHz
        
    Retorna:
    --------
    float : Radio de la primera zona de Fresnel en metros
    """
    # Longitud de onda en metros
    longitud_onda = 0.299792458 / frequency_ghz
    
    # Distancia al punto medio
    d1 = distance_km / 2
    d2 = distance_km / 2
    
    # Radio de la primera zona de Fresnel: 17.3 * sqrt(d1*d2/(f*d))
    # donde d1, d2 en km y f en GHz
    radio_fresnel = 17.3 * math.sqrt((d1 * d2) / (frequency_ghz * distance_km))
    
    return radio_fresnel


def calculate_required_clearance(distance_km, frequency_ghz, clearance_factor=MARGEN_FRESNEL):
    """
    Calcula el despejamiento mínimo requerido de la zona de Fresnel.
    
    Parámetros:
    -----------
    distance_km : float
        Distancia del enlace en kilómetros
    frequency_ghz : float
        Frecuencia en GHz
    clearance_factor : float
        Factor de despejamiento (típico 0.6 = 60%)
        
    Retorna:
    --------
    float : Despejamiento mínimo requerido en metros
    """
    radio_fresnel = calculate_first_fresnel_radius(distance_km, frequency_ghz)
    return radio_fresnel * clearance_factor


def calculate_tower_height_for_los(distance_km, altura_terreno_1, altura_terreno_2, 
                                    frequency_ghz, k=4/3):
    """
    Calcula la altura mínima de las torres para mantener línea de vista (LOS).
    
    Utiliza el método de cálculo considerando:
    - Curvatura terrestre con factor k
    - Zona de Fresnel (despejamiento del 60%)
    - Margen de seguridad
    
    Parámetros:
    -----------
    distance_km : float
        Distancia entre puntos en kilómetros
    altura_terreno_1 : float
        Altura del terreno en punto 1 (metros)
    altura_terreno_2 : float
        Altura del terreno en punto 2 (metros)
    frequency_ghz : float
        Frecuencia de operación en GHz
    k : float
        Factor k del radio terrestre (típico 4/3)
        
    Retorna:
    --------
    tuple : (altura_torre_1, altura_torre_2) en metros
    """
    # Convertir distancia a metros
    d_m = distance_km * 1000
    
    # Diferencia de altura entre terrenos
    delta_h = abs(altura_terreno_2 - altura_terreno_1)
    
    # Corrección por curvatura terrestre
    # Formula: h = d1*d2 / (2*k*R) donde d1 y d2 son las distancias desde los extremos
    R = EARTH_RADIUS_KM * k  # Radio terrestre efectivo en km
    R_m = R * 1000  # En metros
    
    # Para el punto medio, d1 = d2 = d_m/2
    curvatura_punto_medio = (d_m / 2) * (d_m / 2) / (2 * R_m)
    curvatura_punto_medio = curvatura_punto_medio  # en metros
    
    # Despejamiento requerido de zona de Fresnel (60% = 0.6)
    fresnel = calculate_required_clearance(distance_km, frequency_ghz)
    
    # Altura mínima para línea de vista en el punto medio
    # Esta es la altura mínima sobre el terreno en el punto medio
    altura_minima_sobre_terreno = curvatura_punto_medio + fresnel + MARGEN_SEGURIDAD_M
    
    # Para calcular las alturas de las torres, usamos la línea de vista directa
    # La línea recta entre las dos torres debe pasar a altura_minima_sobre_terreno
    # sobre el punto más alto del terreno en el punto medio
    
    # Método simplificado: distribuir la altura requerida proporcionalmente
    # basado en las altitudes del terreno
    altura_terreno_medio = (altura_terreno_1 + altura_terreno_2) / 2
    altura_terreno_max = max(altura_terreno_1, altura_terreno_2)
    
    # Calcular altura de la línea de referencia (línea entre puntos extremos)
    # La altura de la línea de vista en el punto medio es:
    h_linea_vista = altura_terreno_medio + altura_minima_sobre_terreno
    
    # Para mantener línea de vista, las torres deben estar por encima de esta línea
    # Calculamos la altura mínima de cada torre
    
    # En el punto 1, la altura de la línea de vista es altura_terreno_1 + altura_torre_1
    # En el punto medio, la altura de la línea de vista debe ser h_linea_vista
    # La línea entre puntos es lineal, así que:
    # altura_torre_1 + altura_terreno_1 = h_linea_vista - (delta_h/2) * (d_m/2)/(d_m)
    # Simplificado: altura_torre_1 = curvatura_punto_medio + fresnel + margen - delta_h/4
    
    altura_torre_1 = altura_minima_sobre_terreno + (altura_terreno_max - altura_terreno_1)
    altura_torre_2 = altura_minima_sobre_terreno + (altura_terreno_max - altura_terreno_2)
    
    # Asegurar que ninguna altura sea menor que la mínima
    altura_minima = curvatura_punto_medio + fresnel + MARGEN_SEGURIDAD_M
    altura_torre_1 = max(altura_torre_1, altura_minima)
    altura_torre_2 = max(altura_torre_2, altura_minima)
    
    return (round(altura_torre_1, 2), round(altura_torre_2, 2))


def interpolate_terrain_points(lat1, lon1, alt1, lat2, lon2, alt2, num_points=100):
    """
    Interpola puntos del terreno entre dos ubicaciones.
    
    Parámetros:
    -----------
    lat1, lon1, alt1 : float
        Coordenadas y altitud del punto 1
    lat2, lon2, alt2 : float
        Coordenadas y altitud del punto 2
    num_points : int
        Número de puntos a interpolar
        
    Retorna:
    --------
    list : Lista de diccionarios con lat, lon, alt, distancia
    """
    puntos = []
    
    for i in range(num_points + 1):
        t = i / num_points
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        alt = alt1 + t * (alt2 - alt1)
        
        # Calcular distancia desde punto 1
        distancia = haversine_distance(lat1, lon1, lat, lon) * 1000  # en metros
        
        puntos.append({
            'lat': lat,
            'lon': lon,
            'alt': alt,
            'distancia': distancia,
            'distancia_km': distancia / 1000
        })
    
    return puntos


def calculate_distance_direction(lat1, lon1, lat2, lon2):
    """
    Calcula distancia y dirección entre dos puntos.
    
    Parámetros:
    -----------
    lat1, lon1 : float
        Coordenadas del punto 1
    lat2, lon2 : float
        Coordenadas del punto 2
        
    Retorna:
    --------
    dict : Diccionario con distancia, azimut y azimut_inverso
    """
    distancia = haversine_distance(lat1, lon1, lat2, lon2)
    azimut = calculate_azimuth(lat1, lon1, lat2, lon2)
    azimut_inverso = calculate_reverse_azimuth(lat1, lon1, lat2, lon2)
    
    return {
        'distancia_km': distancia,
        'distancia_m': distancia * 1000,
        'azimut_grados': azimut,
        'azimut_inverso_grados': azimut_inverso,
        'azimut_texto': get_cardinal_direction(azimut),
        'azimut_inverso_texto': get_cardinal_direction(azimut_inverso)
    }


def get_cardinal_direction(azimut):
    """
    Convierte azimut numérico a dirección cardinal.
    
    Parámetros:
    -----------
    azimut : float
        Azimut en grados
        
    Retorna:
    --------
    str : Dirección cardinal (N, NE, E, SE, S, SW, W, NW)
    """
    direcciones = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    indice = round(azimut / 45) % 8
    return direcciones[indice]


def calculate_antenna_tilt(distancia_km, altura_torre_1, altura_torre_2):
    """
    Calcula la inclinación (tilt) de las antenas necesario para compensar
    la diferencia de altura entre torres.
    
    Parámetros:
    -----------
    distancia_km : float
        Distancia entre torres en kilómetros
    altura_torre_1 : float
        Altura de la torre 1 en metros
    altura_torre_2 : float
        Altura de la torre 2 en metros
        
    Retorna:
    --------
    dict : Inclinación en grados para cada antenna
    """
    # Diferencia de altura
    delta_h = altura_torre_2 - altura_torre_1
    
    # Distancia horizontal en metros
    distancia_m = distancia_km * 1000
    
    # Inclinación en radianes (arctan)
    tilt_radians = math.atan2(delta_h, distancia_m)
    
    # Convertir a grados
    tilt_degrees = math.degrees(tilt_radians)
    
    return {
        'tilt_torre_1': round(tilt_degrees, 2),  # Positivo = inclinado hacia arriba
        'tilt_torre_2': round(-tilt_degrees, 2),  # Negativo = inclinado hacia abajo
        'diferencia_altura': round(delta_h, 2)
    }
