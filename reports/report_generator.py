"""
Módulo de generación de informes técnicos para enlaces de microondas.
"""

from datetime import datetime
import math


class ReportGenerator:
    """Generador de informes técnicos para enlaces de microondas."""
    
    def __init__(self, resultados, nombre_archivo="informe_enlace"):
        """
        Inicializa el generador de informes.
        
        Parámetros:
        -----------
        resultados : dict
            Diccionario con los resultados del cálculo del enlace
        nombre_archivo : str
            Nombre base para el archivo de informe
        """
        self.resultados = resultados
        self.nombre_archivo = nombre_archivo
    
    def generar_texto(self):
        """
        Genera el contenido del informe en formato texto.
        
        Retorna:
        --------
        str : Contenido del informe
        """
        r = self.resultados
        
        informe = []
        
        # Encabezado
        informe.append("=" * 80)
        informe.append("INFORME TÉCNICO DE DISEÑO DE ENLACE DE MICROONDAS")
        informe.append("=" * 80)
        informe.append("")
        informe.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        informe.append("")
        
        # 1. Resumen Ejecutivo
        informe.append("1. RESUMEN EJECUTIVO")
        informe.append("-" * 80)
        
        tipo = r.get('tipo', 'Con Repetidor')
        informe.append(f"Tipo de enlace: {tipo}")
        informe.append(f"Sitio A: {r['sitio_a']['nombre']}")
        informe.append(f"Sitio B: {r['sitio_b']['nombre']}")
        informe.append(f"Distancia total: {r['distancia_total']:.2f} km")
        informe.append(f"Frecuencia de operación: {r['frecuencia']:.1f} GHz")
        
        if 'balance' in r:
            estado = r['balance'].get('estado', 'N/A')
            margen = r['balance'].get('margin_db', 0)
            informe.append(f"Estado del enlace: {estado}")
            informe.append(f"Margen del enlace: {margen:.2f} dB")
        
        if r.get('necesita_repetidor'):
            if 'repetidor' in r:
                informe.append(f"Repetidor requerido: Sí")
                informe.append(f"Ubicación del repetidor: Lat {r['repetidor']['latitud']:.4f}°, "
                             f"Lon {r['repetidor']['longitud']:.4f}°")
        
        informe.append("")
        
        # 2. Especificaciones del Sistema
        informe.append("2. ESPECIFICACIONES DEL SISTEMA")
        informe.append("-" * 80)
        
        informe.append("Parámetros de transmisión:")
        if 'balance' in r:
            informe.append(f"  - Potencia de transmisión: {r['balance']['tx_power_dbm']} dBm")
            informe.append(f"  - Ganancia de antenas TX/RX: {r['balance']['tx_gain_dbi']} dBi")
            informe.append(f"  - PIRE: {r['balance']['pire_dbm']} dBm")
        
        informe.append("")
        informe.append("Parámetros de recepción:")
        if 'balance' in r:
            informe.append(f"  - Sensibilidad del receptor: {r['balance']['rx_sensitivity_dbm']} dBm")
            informe.append(f"  - Potencia recibida: {r['balance']['rx_power_dbm']} dBm")
        
        informe.append("")
        
        # 3. Parámetros del Enlace
        informe.append("3. PARÁMETROS DEL ENLACE")
        informe.append("-" * 80)
        
        informe.append("Coordenadas geográficas:")
        informe.append(f"Sitio A ({r['sitio_a']['nombre']}):")
        informe.append(f"  Latitud: {r['sitio_a']['lat']:.6f}°")
        informe.append(f"  Longitud: {r['sitio_a']['lon']:.6f}°")
        informe.append(f"  Altitud: {r['sitio_a']['alt']} m.s.n.m")
        
        informe.append("")
        informe.append(f"Sitio B ({r['sitio_b']['nombre']}):")
        informe.append(f"  Latitud: {r['sitio_b']['lat']:.6f}°")
        informe.append(f"  Longitud: {r['sitio_b']['lon']:.6f}°")
        informe.append(f"  Altitud: {r['sitio_b']['alt']} m.s.n.m")
        
        informe.append("")
        
        # 4. Cálculos de Ingeniería
        informe.append("4. CÁLCULOS DE INGENIERÍA")
        informe.append("-" * 80)
        
        # Alturas de torres
        informe.append("Alturas de torres:")
        if 'altura_torre_a' in r:
            informe.append(f"  Torre {r['sitio_a']['nombre']}: {r['altura_torre_a']:.2f} m")
            informe.append(f"  Torre {r['sitio_b']['nombre']}: {r['altura_torre_b']:.2f} m")
        
        if r.get('necesita_repetidor') and 'segmento_a' in r:
            seg_a = r['segmento_a']
            seg_b = r['segmento_b']
            informe.append("")
            informe.append("Con repetidor:")
            informe.append(f"  Segmento 1 ({r['sitio_a']['nombre']} -> Repetidor): {seg_a['distancia_km']:.2f} km")
            informe.append(f"    Torre {r['sitio_a']['nombre']}: {seg_a['altura_torre_a']:.2f} m")
            informe.append(f"    Torre Repetidor: {seg_a['altura_torre_b']:.2f} m")
            informe.append(f"  Segmento 2 (Repetidor -> {r['sitio_b']['nombre']}): {seg_b['distancia_km']:.2f} km")
            informe.append(f"    Torre Repetidor: {seg_b['altura_torre_a']:.2f} m")
            informe.append(f"    Torre {r['sitio_b']['nombre']}: {seg_b['altura_torre_b']:.2f} m")
        
        # Zona de Fresnel
        from core.geography import calculate_first_fresnel_radius
        fresnel = calculate_first_fresnel_radius(r['distancia_total'], r['frecuencia'])
        informe.append("")
        informe.append("Zona de Fresnel:")
        informe.append(f"  Radio primera zona: {fresnel:.2f} m")
        informe.append(f"  Despejamiento 60%: {fresnel*0.6:.2f} m")
        
        informe.append("")
        
        # 5. Pérdidas de Propagación
        informe.append("5. PÉRDIDAS DE PROPAGACIÓN")
        informe.append("-" * 80)
        
        if 'perdidas' in r:
            p = r['perdidas']
            informe.append("Modelo ITU-R P.530:")
            informe.append(f"  Pérdida en espacio libre: {p['free_space_loss']:.2f} dB")
            informe.append(f"  Atenuación por lluvia: {p['rain_loss']:.2f} dB")
            informe.append(f"  Atenuación por gases: {p['gas_loss']:.2f} dB")
            informe.append(f"  PÉRDIDA TOTAL: {p['total_loss']:.2f} dB")
        
        if r.get('necesita_repetidor'):
            if 'perdidas_a' in r and 'perdidas_b' in r:
                pa = r['perdidas_a']
                pb = r['perdidas_b']
                informe.append("")
                informe.append("Con repetidor:")
                informe.append(f"  Segmento A->Repetidor: {pa['total_loss']:.2f} dB")
                informe.append(f"  Segmento Repetidor->B: {pb['total_loss']:.2f} dB")
                total_rep = pa['total_loss'] + pb['total_loss']
                informe.append(f"  Pérdida total (2 saltos): {total_rep:.2f} dB")
        
        informe.append("")
        
        # 6. Conclusiones y Recomendaciones
        informe.append("6. CONCLUSIONES Y RECOMENDACIONES")
        informe.append("-" * 80)
        
        if 'balance' in r:
            margen = r['balance']['margin_db']
            if margen >= 10:
                informe.append(f"El enlace tiene un margen adecuado de {margen:.2f} dB.")
                informe.append("Se recomienda proceder con la implementación.")
            elif margen >= 3:
                informe.append(f"Advertencia: El margen del enlace es de {margen:.2f} dB.")
                informe.append("Considere aumentar la potencia o增益 de las antenas.")
            else:
                informe.append(f"ERROR: El margen del enlace es insuficiente ({margen:.2f} dB).")
                informe.append("Es necesario rediseñar el enlace.")
        
        informe.append("")
        
        # Pie de página
        informe.append("=" * 80)
        informe.append("INFORME GENERADO CON HERRAMIENTA DE DISEÑO DE MICROONDAS")
        informe.append("Cumple con recomendaciones ITU-R F.1101 y P.530")
        informe.append("=" * 80)
        
        return "\n".join(informe)
    
    def guardar(self, nombre_archivo=None):
        """
        Guarda el informe en un archivo de texto.
        
        Parámetros:
        -----------
        nombre_archivo : str
            Nombre del archivo (opcional)
            
        Retorna:
        --------
        str : Ruta del archivo guardado
        """
        if nombre_archivo is None:
            nombre_archivo = self.nombre_archivo
        
        nombre_completo = f"{nombre_archivo}.txt"
        
        contenido = self.generar_texto()
        
        with open(nombre_completo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return nombre_completo


def generar_informe(resultados, nombre_archivo="informe_enlace"):
    """
    Función de conveniencia para generar un informe.
    
    Parámetros:
    -----------
    resultados : dict
        Resultados del cálculo del enlace
    nombre_archivo : str
        Nombre base para el archivo
        
    Retorna:
    --------
    str : Ruta del archivo guardado
    """
    generador = ReportGenerator(resultados, nombre_archivo)
    return generador.guardar()
