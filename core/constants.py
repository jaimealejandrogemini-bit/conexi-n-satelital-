"""
Constantes y configuraciones para la aplicación de diseño de enlaces de microondas.
"""

# Constantes físicas
EARTH_RADIUS_KM = 6371  # Radio terrestre medio en km
SPEED_OF_LIGHT_KM_S = 299792.458  # Velocidad de la luz en km/s

# Bandas de frecuencia recomendadas para enlaces de microondas en Colombia
FREQUENCY_BANDS = [
    {"nombre": "L", "rango": "1-2 GHz", "valor": 1.5},
    {"nombre": "S", "rango": "2-4 GHz", "valor": 3.0},
    {"nombre": "C", "rango": "4-8 GHz", "valor": 6.0},
    {"nombre": "X", "rango": "8-12 GHz", "valor": 11.0},
    {"nombre": "Ku", "rango": "12-18 GHz", "valor": 15.0},
    {"nombre": "K", "rango": "18-27 GHz", "valor": 23.0},
    {"nombre": "Ka", "rango": "27-40 GHz", "valor": 38.0},
]

# Frecuencias por defecto para la aplicación
DEFAULT_FREQUENCIES = [
    {"nombre": "6 GHz (Banda C)", "valor": 6.0},
    {"nombre": "11 GHz (Banda X)", "valor": 11.0},
    {"nombre": "15 GHz (Banda Ku)", "valor": 15.0},
    {"nombre": "18 GHz (Banda K)", "valor": 18.0},
    {"nombre": "23 GHz (Banda K)", "valor": 23.0},
    {"nombre": "38 GHz (Banda Ka)", "valor": 38.0},
]

# Porcentajes de disponibilidad típicos
AVAILABILITY_OPTIONS = [
    {"nombre": "99.9%", "valor": 99.9},
    {"nombre": "99.95%", "valor": 99.95},
    {"nombre": "99.99%", "valor": 99.99},
    {"nombre": "99.999%", "valor": 99.999},
]

# Parámetros de antenas típicos
ANTENNA_GAINS = [
    {"nombre": "0.6 m (dBi)", "valor_6ghz": 25, "valor_11ghz": 29, "valor_15ghz": 32, "valor_23ghz": 35},
    {"nombre": "1.2 m (dBi)", "valor_6ghz": 31, "valor_11ghz": 35, "valor_15ghz": 38, "valor_23ghz": 41},
    {"nombre": "1.8 m (dBi)", "valor_6ghz": 34, "valor_11ghz": 38, "valor_15ghz": 41, "valor_23ghz": 44},
    {"nombre": "2.4 m (dBi)", "valor_6ghz": 36, "valor_11ghz": 40, "valor_15ghz": 43, "valor_23ghz": 46},
]

# Potencias de transmisión típicas
TX_POWER_OPTIONS = [
    {"nombre": "+20 dBm (100 mW)", "valor": 20},
    {"nombre": "+23 dBm (200 mW)", "valor": 23},
    {"nombre": "+27 dBm (500 mW)", "valor": 27},
    {"nombre": "+30 dBm (1 W)", "valor": 30},
    {"nombre": "+33 dBm (2 W)", "valor": 33},
]

# Sensibilidad típica de receptores
RECEIVER_SENSITIVITY = -75  # dBm típica para sistemas de 6-38 GHz

# Distancia mínima requerida entre ciudades
MIN_DISTANCE_KM = 100

# Constantes para cálculos
MARGEN_FRESNEL = 0.6  # 60% de la primera zona de Fresnel
MARGEN_SEGURIDAD_M = 10  # Margen de seguridad en metros

# Factor k de radio terrestre (típico para enlaces de microondas)
K_DEFAULT = 4/3  # Factor k estándar
K_MIN = 2/3  # Factor k mínimo para condiciones adversas
