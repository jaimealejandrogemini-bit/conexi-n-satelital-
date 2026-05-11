"""
Módulo de cálculos de propagación para enlaces de microondas.
Implementa modelos ITU-R P.530 para predicción de propagación.
"""

import math


def free_space_loss(distance_km, frequency_ghz):
    """
    Calcula la pérdida en el espacio libre (Free Space Loss) usando el modelo de Friis.
    
    FSL = 20*log10(d) + 20*log10(f) + 32.44
    
    Parámetros:
    -----------
    distance_km : float
        Distancia del enlace en kilómetros
    frequency_ghz : float
        Frecuencia de operación en GHz
        
    Retorna:
    --------
    float : Pérdida en espacio libre en dB
    """
    # Convertir a MHz para la fórmula
    frequency_mhz = frequency_ghz * 1000
    
    # Fórmula de pérdida en espacio libre
    fsl = 20 * math.log10(distance_km) + 20 * math.log10(frequency_mhz) + 32.44
    
    return round(fsl, 2)


def rain_attenuation_itu_p530(distance_km, frequency_ghz, latitude, availability=99.99):
    """
    Calcula la atenuación por lluvia según ITU-R P.530-17.
    
    Parámetros:
    -----------
    distance_km : float
        Distancia del enlace en kilómetros
    frequency_ghz : float
        Frecuencia de operación en GHz
    latitude : float
        Latitud del punto medio del enlace en grados
    availability : float
        Porcentaje de disponibilidad requerido (default 99.99%)
        
    Retorna:
    --------
    float : Atenuación por lluvia en dB
    """
    # Intensidad de lluvia para diferentes porcentajes del tiempo (mm/h)
    # Valores típicos para Colombia (zona tropical)
    rain_rates = {
        99.9: 85,
        99.95: 100,
        99.99: 120,
        99.999: 150
    }
    
    # Obtener intensidad de lluvia para la disponibilidad requerida
    R = rain_rates.get(availability, 100)
    
    # Coeficiente específico de atenuación (dB/km por mm/h)
    # k y alpha según ITU-R P.838
    if frequency_ghz <= 2:
        k = 0.0001
        alpha = 1.0
    elif frequency_ghz <= 6:
        k = 0.001
        alpha = 1.3
    elif frequency_ghz <= 12:
        k = 0.01
        alpha = 1.3
    elif frequency_ghz <= 20:
        k = 0.036
        alpha = 1.2
    elif frequency_ghz <= 30:
        k = 0.075
        alpha = 1.1
    else:
        k = 0.1
        alpha = 1.0
    
    # Atenuación específica
    gamma_r = k * (R ** alpha)  # dB/km
    
    # Longitud efectiva del enlace
    if distance_km <= 10:
        L_eff = distance_km
    else:
        L_eff = 10 * (1 - math.exp(-distance_km / 10))
    
    # Atenuación total por lluvia
    rain_loss = gamma_r * L_eff
    
    return round(rain_loss, 2)


def atmospheric_gas_attenuation(distance_km, frequency_ghz):
    """
    Calcula la atenuación por gases atmosféricos (oxígeno y vapor de agua).
    Relevante principalmente para frecuencias > 10 GHz.
    
    Parámetros:
    -----------
    distance_km : float
        Distancia del enlace en kilómetros
    frequency_ghz : float
        Frecuencia de operación en GHz
        
    Retorna:
    --------
    float : Atenuación por gases en dB
    """
    if frequency_ghz < 10:
        return 0.0
    
    # Atenuación típica de gases para diferentes frecuencias
    # Valores aproximados en dB/km
    if frequency_ghz <= 15:
        gas_atten_per_km = 0.01
    elif frequency_ghz <= 20:
        gas_atten_per_km = 0.02
    elif frequency_ghz <= 25:
        gas_atten_per_km = 0.05
    elif frequency_ghz <= 30:
        gas_atten_per_km = 0.1
    elif frequency_ghz <= 35:
        gas_atten_per_km = 0.15
    elif frequency_ghz <= 40:
        gas_atten_per_km = 0.2
    else:
        gas_atten_per_km = 0.3
    
    gas_loss = gas_atten_per_km * distance_km
    
    return round(gas_loss, 2)


def total_path_loss(distance_km, frequency_ghz, latitude, availability=99.99):
    """
    Calcula las pérdidas totales del enlace incluyendo todos los factores.
    
    Parámetros:
    -----------
    distance_km : float
        Distancia del enlace en kilómetros
    frequency_ghz : float
        Frecuencia de operación en GHz
    latitude : float
        Latitud del punto medio en grados
    availability : float
        Porcentaje de disponibilidad requerido
        
    Retorna:
    --------
    dict : Diccionario con todas las pérdidas
    """
    fsl = free_space_loss(distance_km, frequency_ghz)
    rain = rain_attenuation_itu_p530(distance_km, frequency_ghz, latitude, availability)
    gas = atmospheric_gas_attenuation(distance_km, frequency_ghz)
    
    # Pérdidas totales
    total_loss = fsl + rain + gas
    
    return {
        'free_space_loss': fsl,
        'rain_loss': rain,
        'gas_loss': gas,
        'total_loss': round(total_loss, 2),
        'frequency_ghz': frequency_ghz,
        'distance_km': distance_km,
        'latitude': latitude,
        'availability': availability
    }


def link_power_balance(tx_power_dbm, tx_antenna_gain_dbi, rx_antenna_gain_dbi, 
                       path_loss_db, rx_sensitivity_dbm=-75):
    """
    Calcula el balance de potencia del enlace y el margen.
    
    Parámetros:
    -----------
    tx_power_dbm : float
        Potencia de transmisión en dBm
    tx_antenna_gain_dbi : float
        Ganancia de la antena transmisora en dBi
    rx_antenna_gain_dbi : float
        Ganancia de la antena receptora en dBi
    path_loss_db : float
        Pérdidas totales del enlace en dB
    rx_sensitivity_dbm : float
        Sensibilidad del receptor en dBm
        
    Retorna:
    --------
    dict : Balance de potencia y margen del enlace
    """
    # Potencia isotrópica radiada equivalente (PIRE)
    pire_dbm = tx_power_dbm + tx_antenna_gain_dbi
    
    # Potencia recibida
    rx_power_dbm = pire_dbm + rx_antenna_gain_dbi - path_loss_db
    
    # Margen del enlace
    margin_db = rx_power_dbm - rx_sensitivity_dbm
    
    # Determinar estado del enlace
    if margin_db >= 20:
        estado = "Excelente"
    elif margin_db >= 10:
        estado = "Bueno"
    elif margin_db >= 3:
        estado = "Aceptable"
    elif margin_db >= 0:
        estado = "Marginal"
    else:
        estado = "Fallo"
    
    return {
        'tx_power_dbm': tx_power_dbm,
        'tx_gain_dbi': tx_antenna_gain_dbi,
        'rx_gain_dbi': rx_antenna_gain_dbi,
        'pire_dbm': round(pire_dbm, 2),
        'path_loss_db': path_loss_db,
        'rx_power_dbm': round(rx_power_dbm, 2),
        'rx_sensitivity_dbm': rx_sensitivity_dbm,
        'margin_db': round(margin_db, 2),
        'estado': estado
    }


def calculate_link_availability(margin_db):
    """
    Estima la disponibilidad del enlace basada en el margen.
    
    Esta es una aproximación simple. Para cálculos precisos
    se debe usar ITU-R P.530.
    
    Parámetros:
    -----------
    margin_db : float
        Margen del enlace en dB
        
    Retorna:
    --------
    dict : Disponibilidad estimada
    """
    if margin_db >= 30:
        disponibilidad = 99.9999
        calidad = "Excelente"
    elif margin_db >= 20:
        disponibilidad = 99.999
        calidad = "Muy buena"
    elif margin_db >= 15:
        disponibilidad = 99.99
        calidad = "Buena"
    elif margin_db >= 10:
        disponibilidad = 99.9
        calidad = "Aceptable"
    elif margin_db >= 5:
        disponibilidad = 99.5
        calidad = "Regular"
    else:
        disponibilidad = 99.0
        calidad = "Insuficiente"
    
    return {
        'disponibilidad': disponibilidad,
        'calidad': calidad
    }


def fresnel_zone_clearance(altura_terreno, altura_rayo, frecuencia_ghz, distancia_punto):
    """
    Calcula el despejamiento de la zona de Fresnel en un punto del enlace.
    
    Parámetros:
    -----------
    altura_terreno : float
        Altura del terreno sobre el nivel del mar en metros
    altura_rayo : float
        Altura del rayo de línea de vista sobre el nivel del mar en metros
    frecuencia_ghz : float
        Frecuencia en GHz
    distancia_punto : float
        Distancia desde el transmisor en metros
        
    Retorna:
    --------
    dict : Información del despejamiento
    """
    # Radio de la primera zona de Fresnel
    # Para el cálculo simplificado, usamos la frecuencia
    radio_fresnel = 17.3 * math.sqrt(frecuencia_ghz)  # metros (aproximación)
    
    # Claro (diferencia entre rayo y terreno)
    claro = altura_rayo - altura_terreno
    
    # Porcentaje de despejamiento
    if claro > 0:
        porcentaje_despejamiento = (claro / radio_fresnel) * 100
    else:
        porcentaje_despejamiento = 0
    
    # Determinar estado
    if porcentaje_despejamiento >= 60:
        estado = "OK - Zona de Fresnel libre"
    elif porcentaje_despejamiento >= 30:
        estado = "Advertencia - Despejamiento reducido"
    elif porcentaje_despejamiento > 0:
        estado = "Advertencia - Cerca del terreno"
    else:
        estado = "Error - Obstáculo en la trayectoria"
    
    return {
        'claro': round(claro, 2),
        'radio_fresnel': round(radio_fresnel, 2),
        'porcentaje_despejamiento': round(porcentaje_despejamiento, 1),
        'estado': estado
    }
