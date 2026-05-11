"""
Módulo de diseño de repetidores para enlaces de microondas.
"""

import math
from core.geography import (
    haversine_distance, calculate_azimuth, calculate_earth_curvature_correction,
    calculate_first_fresnel_radius, calculate_distance_direction,
    calculate_antenna_tilt
)
from core.propagation import (
    total_path_loss, link_power_balance, free_space_loss
)
from core.constants import MIN_DISTANCE_KM


class RepeaterDesigner:
    """Clase para diseñar y calcular repetidores intermedios."""
    
    def __init__(self, site_a, site_b, frequency_ghz):
        """
        Inicializa el diseñador de repetidores.
        
        Parámetros:
        -----------
        site_a : dict
            Diccionario con datos del sitio A (nombre, lat, lon, alt)
        site_b : dict
            Diccionario con datos del sitio B (nombre, lat, lon, alt)
        frequency_ghz : float
            Frecuencia de operación en GHz
        """
        self.site_a = site_a
        self.site_b = site_b
        self.frequency_ghz = frequency_ghz
        
        # Calcular distancia total
        self.distancia_total = haversine_distance(
            site_a['lat'], site_a['lon'],
            site_b['lat'], site_b['lon']
        )
        
        # Calcular latitud media
        self.latitud_media = (site_a['lat'] + site_b['lat']) / 2
    
    def needs_repeater(self, max_distance_km=50):
        """
        Determina si se necesita un repetidor basándose en la distancia.
        
        Parámetros:
        -----------
        max_distance_km : float
            Distancia máxima recomendada para un solo salto
            
        Retorna:
        --------
        bool : True si se necesita repetidor
        """
        return self.distancia_total > max_distance_km
    
    def calculate_midpoint_repeater(self):
        """
        Calcula la posición de un repetidor en el punto medio.
        
        Retorna:
        --------
        dict : Datos del repetidor calculado
        """
        lat_repetidor = (self.site_a['lat'] + self.site_b['lat']) / 2
        lon_repetidor = (self.site_a['lon'] + self.site_b['lon']) / 2
        
        # Estimar altitud del repetidor (promedio simple, idealmente de DEM)
        alt_repetidor = (self.site_a['alt'] + self.site_b['alt']) / 2
        
        # Calcular distancias a cada segmento
        distancia_a_repetidor = haversine_distance(
            self.site_a['lat'], self.site_a['lon'],
            lat_repetidor, lon_repetidor
        )
        
        distancia_b_repetidor = haversine_distance(
            lat_repetidor, lon_repetidor,
            self.site_b['lat'], self.site_b['lon']
        )
        
        return {
            'tipo': 'Punto Medio',
            'latitud': lat_repetidor,
            'longitud': lon_repetidor,
            'altitud': round(alt_repetidor, 2),
            'distancia_a': round(distancia_a_repetidor, 2),
            'distancia_b': round(distancia_b_repetidor, 2),
            'sitio_a': self.site_a['nombre'],
            'sitio_b': self.site_b['nombre']
        }
    
    def calculate_segment_tower_heights(self, repeater_pos, site_a, site_b):
        """
        Calcula las alturas de torres para un segmento del enlace.
        
        Parámetros:
        -----------
        repeater_pos : dict
            Posición del repetidor
        site_a : dict
            Datos del sitio A
        site_b : dict
            Datos del sitio B (puede ser repetidor o sitio final)
            
        Retorna:
        --------
        dict : Alturas de torres calculadas
        """
        # Calcular distancia del segmento
        distancia_segmento = haversine_distance(
            site_a['lat'], site_a['lon'],
            site_b['lat'], site_b['lon']
        )
        
        # Calcular altura de torres
        from core.geography import calculate_tower_height_for_los
        
        altura_torre_a, altura_torre_b = calculate_tower_height_for_los(
            distancia_segmento,
            site_a['alt'],
            site_b['alt'],
            self.frequency_ghz
        )
        
        return {
            'sitio_a': site_a['nombre'],
            'sitio_b': site_b['nombre'],
            'distancia_km': round(distancia_segmento, 2),
            'altura_torre_a': altura_torre_a,
            'altura_torre_b': altura_torre_b,
            'terreno_a': site_a['alt'],
            'terreno_b': site_b['alt']
        }
    
    def calculate_optimal_repeater_location(self, terrain_profile=None):
        """
        Calcula la ubicación óptima del repetidor considerando el terreno.
        
        Parámetros:
        -----------
        terrain_profile : list
            Perfil del terreno entre los dos sitios
            
        Retorna:
        --------
        dict : Datos del repetidor óptimo
        """
        # Usar punto medio como inicio
        mid = self.calculate_midpoint_repeater()
        
        # Si hay perfil del terreno, buscar punto óptimo
        if terrain_profile:
            # Buscar punto con menor altura requerida de torre
            mejor_punto = mid
            menor_altura = float('inf')
            
            for punto in terrain_profile[1:-1]:  # Excluir puntos extremos
                # Calcular altura requerida para ver ambos extremos
                altura_req = self._calculate_required_height_at_point(
                    punto, terrain_profile
                )
                if altura_req < menor_altura:
                    menor_altura = altura_req
                    mejor_punto = {
                        'tipo': 'Óptimo',
                        'latitud': punto['lat'],
                        'longitud': punto['lon'],
                        'altitud': punto['alt'],
                        'distancia_a': punto['distancia_km'],
                        'distancia_b': self.distancia_total - punto['distancia_km']
                    }
            
            return mejor_punto
        
        return mid
    
    def _calculate_required_height_at_point(self, punto, terrain_profile):
        """
        Calcula la altura requerida de torre en un punto específico.
        """
        # Esta es una simplificación - en una implementación real
        # se usaría el perfil de terreno completo
        return punto.get('alt', 0)
    
    def calculate_repeater_link(self, repeater_pos, tx_power, tx_gain, rx_gain, 
                                 availability=99.99):
        """
        Calcula los parámetros completos del enlace con repetidor.
        
        Parámetros:
        -----------
        repeater_pos : dict
            Posición del repetidor
        tx_power : float
            Potencia de transmisión en dBm
        tx_gain : float
            Ganancia de antenas en dBi
        rx_gain : float
            Ganancia de antenas receptoras en dBi
        availability : float
            Disponibilidad requerida
            
        Retorna:
        --------
        dict : Parámetros completos del enlace con repetidor
        """
        # Calcular segmento A -> Repetidor
        sitio_repetidor = {
            'nombre': 'Repetidor',
            'lat': repeater_pos['latitud'],
            'lon': repeater_pos['longitud'],
            'alt': repeater_pos['altitud']
        }
        
        seg_a = self.calculate_segment_tower_heights(
            repeater_pos, self.site_a, sitio_repetidor
        )
        
        # Calcular segmento Repetidor -> B
        seg_b = self.calculate_segment_tower_heights(
            repeater_pos, sitio_repetidor, self.site_b
        )
        
        # Calcular pérdidas de propagación para cada segmento
        lat_segmento_a = (self.site_a['lat'] + repeater_pos['latitud']) / 2
        lat_segmento_b = (repeater_pos['latitud'] + self.site_b['lat']) / 2
        
        perdidas_a = total_path_loss(
            repeater_pos['distancia_a'],
            self.frequency_ghz,
            lat_segmento_a,
            availability
        )
        
        perdidas_b = total_path_loss(
            repeater_pos['distancia_b'],
            self.frequency_ghz,
            lat_segmento_b,
            availability
        )
        
        # Calcular balance de potencia para cada segmento
        balance_a = link_power_balance(
            tx_power, tx_gain, rx_gain,
            perdidas_a['total_loss']
        )
        
        balance_b = link_power_balance(
            tx_power, tx_gain, rx_gain,
            perdidas_b['total_loss']
        )
        
        return {
            'repetidor': repeater_pos,
            'segmento_a': seg_a,
            'segmento_b': seg_b,
            'perdidas_a': perdidas_a,
            'perdidas_b': perdidas_b,
            'balance_a': balance_a,
            'balance_b': balance_b,
            'margen_minimo': min(balance_a['margin_db'], balance_b['margin_db']),
            'estado': 'OK' if min(balance_a['margin_db'], balance_b['margin_db']) >= 10 else 'ADVERTENCIA'
        }
    
    def generate_hop_chain(self, max_hop_distance_km=50):
        """
        Genera una cadena de saltos para enlaces largos.
        
        Parámetros:
        -----------
        max_hop_distance_km : float
            Distancia máxima por salto
            
        Retorna:
        --------
        list : Lista de saltos (sitio_inicio -> sitio_fin)
        """
        num_saltos = math.ceil(self.distancia_total / max_hop_distance_km)
        
        if num_saltos <= 1:
            return [{
                'sitio_inicio': self.site_a,
                'sitio_fin': self.site_b,
                'distancia': self.distancia_total
            }]
        
        # Calcular puntos intermedios
        saltos = []
        
        for i in range(num_saltos):
            t_inicio = i / num_saltos
            t_fin = (i + 1) / num_saltos
            
            lat_inicio = self.site_a['lat'] + t_inicio * (self.site_b['lat'] - self.site_a['lat'])
            lon_inicio = self.site_a['lon'] + t_inicio * (self.site_b['lon'] - self.site_a['lon'])
            alt_inicio = self.site_a['alt'] + t_inicio * (self.site_b['alt'] - self.site_a['alt'])
            
            lat_fin = self.site_a['lat'] + t_fin * (self.site_b['lat'] - self.site_a['lat'])
            lon_fin = self.site_a['lon'] + t_fin * (self.site_b['lon'] - self.site_a['lon'])
            alt_fin = self.site_a['alt'] + t_fin * (self.site_b['alt'] - self.site_a['alt'])
            
            sitio_inicio = {
                'nombre': f'Sitio {i+1}' if i > 0 else self.site_a['nombre'],
                'lat': lat_inicio,
                'lon': lon_inicio,
                'alt': alt_inicio
            }
            
            sitio_fin = {
                'nombre': f'Sitio {i+2}' if i < num_saltos - 1 else self.site_b['nombre'],
                'lat': lat_fin,
                'lon': lon_fin,
                'alt': alt_fin
            }
            
            distancia = haversine_distance(lat_inicio, lon_inicio, lat_fin, lon_fin)
            
            saltos.append({
                'sitio_inicio': sitio_inicio,
                'sitio_fin': sitio_fin,
                'distancia': round(distancia, 2)
            })
        
        return saltos


def create_repeater_link(site_a, site_b, frequency_ghz, tx_power=30, 
                        tx_gain=35, rx_gain=35, use_repeater=True, 
                        availability=99.99, repeater_coords=None):
    """
    Función de alto nivel para crear un enlace con o sin repetidor.
    
    Parámetros:
    -----------
    site_a, site_b : dict
        Datos de los sitios
    frequency_ghz : float
        Frecuencia en GHz
    tx_power : float
        Potencia de transmisión en dBm
    tx_gain, rx_gain : float
        Ganancias de antenas en dBi
    use_repeater : bool
        Si True, usa un repetidor
    availability : float
        Disponibilidad requerida
    repeater_coords : dict, optional
        Coordenadas manuales del repetidor (lat, lon, alt)
        
    Retorna:
    --------
    dict : Resultados del enlace
    """
    distancia = haversine_distance(
        site_a['lat'], site_a['lon'],
        site_b['lat'], site_b['lon']
    )
    
    # Verificar si se necesita repetidor
    if distancia < MIN_DISTANCE_KM:
        return {
            'error': f'La distancia ({distancia:.1f} km) es menor al mínimo ({MIN_DISTANCE_KM} km)',
            'necesita_repetidor': False
        }
    
    # Crear diseñador de repetidores
    diseñador = RepeaterDesigner(site_a, site_b, frequency_ghz)
    
    if use_repeater or distancia > 50:
        # Determinar posición del repetidor
        if repeater_coords is not None:
            # Usar coordenadas manuales
            lat_repetidor = repeater_coords['lat']
            lon_repetidor = repeater_coords['lon']
            alt_repetidor = repeater_coords.get('alt', (site_a['alt'] + site_b['alt']) / 2)
            tipo_repetidor = 'Manual'
        else:
            # Usar punto medio
            repeater_pos = diseñador.calculate_midpoint_repeater()
            lat_repetidor = repeater_pos['latitud']
            lon_repetidor = repeater_pos['longitud']
            alt_repetidor = repeater_pos['altitud']
            tipo_repetidor = 'Punto Medio'
        
        # Calcular distancias a cada segmento
        distancia_a_repetidor = haversine_distance(
            site_a['lat'], site_a['lon'],
            lat_repetidor, lon_repetidor
        )
        distancia_b_repetidor = haversine_distance(
            lat_repetidor, lon_repetidor,
            site_b['lat'], site_b['lon']
        )
        
        # Crear posición del repetidor
        repeater_pos = {
            'tipo': tipo_repetidor,
            'latitud': lat_repetidor,
            'longitud': lon_repetidor,
            'altitud': alt_repetidor,
            'distancia_a': round(distancia_a_repetidor, 2),
            'distancia_b': round(distancia_b_repetidor, 2),
            'sitio_a': site_a['nombre'],
            'sitio_b': site_b['nombre']
        }
        
        # Calcular enlace completo con repetidor
        resultado = diseñador.calculate_repeater_link(
            repeater_pos, tx_power, tx_gain, rx_gain, availability
        )
        
        resultado['distancia_total'] = round(distancia, 2)
        resultado['sitio_a'] = site_a
        resultado['sitio_b'] = site_b
        resultado['frecuencia'] = frequency_ghz
        resultado['necesita_repetidor'] = True
        resultado['tipo_repetidor'] = tipo_repetidor
        
        # Agregar alturas de torres para compatibilidad con GUI
        if 'segmento_a' in resultado:
            resultado['altura_torre_a'] = resultado['segmento_a'].get('altura_torre_a', 0)
            resultado['altura_torre_b'] = resultado['segmento_b'].get('altura_torre_b', 0)
            resultado['altura_repetidor_a'] = resultado['segmento_a'].get('altura_torre_b', 0)
            resultado['altura_repetidor_b'] = resultado['segmento_b'].get('altura_torre_a', 0)
            
            # Calcular inclinación de antenas para segmento A -> Repetidor
            tilt_a = calculate_antenna_tilt(
                resultado['repetidor']['distancia_a'],
                resultado['altura_torre_a'],
                resultado['altura_repetidor_a']
            )
            
            # Calcular inclinación de antenas para Repetidor -> B
            tilt_b = calculate_antenna_tilt(
                resultado['repetidor']['distancia_b'],
                resultado['altura_repetidor_b'],
                resultado['altura_torre_b']
            )
            
            resultado['inclinacion'] = {
                'segmento_a': tilt_a,
                'segmento_b': tilt_b
            }
        
        return resultado
    else:
        # Enlace directo
        from core.geography import calculate_tower_height_for_los, calculate_distance_direction
        from core.propagation import total_path_loss, link_power_balance
        
        altura_a, altura_b = calculate_tower_height_for_los(
            distancia, site_a['alt'], site_b['alt'], frequency_ghz
        )
        
        direccion = calculate_distance_direction(
            site_a['lat'], site_a['lon'],
            site_b['lat'], site_b['lon']
        )
        
        lat_media = (site_a['lat'] + site_b['lat']) / 2
        perdidas = total_path_loss(distancia, frequency_ghz, lat_media, availability)
        
        balance = link_power_balance(tx_power, tx_gain, rx_gain, perdidas['total_loss'])
        
        # Calcular inclinación de antenas
        tilt = calculate_antenna_tilt(distancia, altura_a, altura_b)
        
        return {
            'tipo': 'Directo',
            'distancia_total': round(distancia, 2),
            'sitio_a': site_a,
            'sitio_b': site_b,
            'frecuencia': frequency_ghz,
            'altura_torre_a': altura_a,
            'altura_torre_b': altura_b,
            'direccion': direccion,
            'perdidas': perdidas,
            'balance': balance,
            'necesita_repetidor': False,
            'estado': balance['estado'],
            'inclinacion': tilt
        }
