import math

class CalculadoraSatelital:
    """
    Calculadora de enlace satelital extremo a extremo (uplink + downlink)
    Basado en teoría estándar (Neri Vela) - Versión Robusta
    """

    def __init__(self):
        self.k_db = 228.6  # Constante de Boltzmann en dBHz

    # -----------------------------
    # GEOMETRÍA (Blindada)
    # -----------------------------
    def calcular_geometria(self, lat_est, lon_est, lon_sat):
        lat = math.radians(lat_est)
        lon = math.radians(lon_est)
        lon_sat = math.radians(lon_sat)

        delta_lon = lon_sat - lon
        c = math.cos(lat) * math.cos(delta_lon)
        c = max(min(c, 1), -1)  

        # Protección contra división por cero en el cénit
        den = math.sqrt(max(1 - c**2, 1e-10))
        elev = math.degrees(math.atan((c - 0.15127) / den))
        
        rango = 35786 * math.sqrt(1.4199 - 0.4199 * c)
        
        # Azimut preciso con atan2
        azimut = math.degrees(
            math.atan2(
                math.sin(delta_lon),
                math.cos(lat) * math.tan(0) - math.sin(lat) * math.cos(delta_lon)
            )
        )
        if azimut < 0:
            azimut += 360

        return elev, azimut, rango

    # -----------------------------
    # PÉRDIDAS FÍSICAS
    # -----------------------------
    def perdidas_espacio_libre(self, distancia_km, frecuencia_ghz):
        return 92.44 + 20 * math.log10(distancia_km) + 20 * math.log10(frecuencia_ghz)

    def calcular_desapuntamiento(self, diametro_antena_m, frecuencia_ghz, error_grados):
        """Calcula la pérdida por desapuntamiento según Neri Vela"""
        if error_grados == 0 or diametro_antena_m == 0:
            return 0.0
        
        longitud_onda_m = 0.3 / frecuencia_ghz
        theta_3db = 70.0 * (longitud_onda_m / diametro_antena_m)
        return 12.0 * (error_grados / theta_3db)**2

    # -----------------------------
    # RELACIONES DE RUIDO Y POTENCIA
    # -----------------------------
    def calcular_c_no(self, pire, perdidas_el, atenuacion_total, g_t):
        return pire - (perdidas_el + atenuacion_total) + g_t + self.k_db

    def calcular_c_no_total(self, c_up, c_down, c_im):
        up = 10 ** (c_up / 10)
        down = 10 ** (c_down / 10)
        im = 10 ** (c_im / 10)
        return 10 * math.log10(1 / ((1 / up) + (1 / down) + (1 / im)))

    def calcular_c_n(self, c_no, ancho_banda_mhz):
        ancho_banda_hz = ancho_banda_mhz * 1000000
        return c_no - 10 * math.log10(ancho_banda_hz)

    # -----------------------------
    # EJECUCIÓN DEL BALANCE
    # -----------------------------
    def ejecutar_balance_enlace(self, params):
        # 1. Geometría
        elev_up, az_up, rango_up = self.calcular_geometria(params['lat_tx'], params['lon_tx'], params['lon_sat'])
        elev_dw, az_down, rango_down = self.calcular_geometria(params['lat_rx'], params['lon_rx'], params['lon_sat'])

        # 2. Pérdidas Espacio Libre
        fsl_up = self.perdidas_espacio_libre(rango_up, params['f_up_ghz'])
        fsl_down = self.perdidas_espacio_libre(rango_down, params['f_down_ghz'])

        # 3. Pérdidas por Desapuntamiento (Uplink y Downlink)
        diametro_tx = params.get('diametro_tx_m', 2.4)
        error_tx = params.get('error_apuntamiento_grados', 0.1) 
        desapuntamiento_up = self.calcular_desapuntamiento(diametro_tx, params['f_up_ghz'], error_tx)
        atenuacion_total_up = params['lluvia_up'] + desapuntamiento_up

        diametro_rx = params.get('diametro_rx_m', 2.4)
        error_rx = params.get('error_apuntamiento_grados_rx', error_tx) # Usa el mismo error si no se especifica
        desapuntamiento_down = self.calcular_desapuntamiento(diametro_rx, params['f_down_ghz'], error_rx)
        atenuacion_total_down = params['lluvia_down'] + desapuntamiento_down

        # 4. Relación Señal a Ruido (C/No)
        c_no_up = self.calcular_c_no(params['pire_estacion'], fsl_up, atenuacion_total_up, params['gt_satelite'])
        c_no_down = self.calcular_c_no(params['pire_satelite'], fsl_down, atenuacion_total_down, params['gt_estacion'])
        
        c_no_total = self.calcular_c_no_total(c_no_up, c_no_down, params['c_no_intermodulacion'])

        # 5. Relación total de potencias C/N
        bw_mhz = params.get('ancho_banda_mhz', 36.0) 
        c_n_total = self.calcular_c_n(c_no_total, bw_mhz)

        return {
            "geometria_tx": {"elevacion": elev_up, "azimut": az_up, "rango": rango_up},
            "geometria_rx": {"elevacion": elev_dw, "azimut": az_down, "rango": rango_down},
            "perdidas": {
                "fsl_up": fsl_up, 
                "fsl_down": fsl_down,
                "desapuntamiento_up": desapuntamiento_up,
                "desapuntamiento_down": desapuntamiento_down
            },
            "resultados": {
                "c_no_up": c_no_up, 
                "c_no_down": c_no_down, 
                "c_no_total": c_no_total,
                "c_n_total": c_n_total
            }
        }