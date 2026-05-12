"""
Módulo de generación de informes técnicos para enlaces satelitales en PDF.
"""

from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class ReportGenerator:
    """Generador de informes técnicos en PDF para enlaces satelitales."""
    
    def __init__(self, resultados, params, nombre_archivo="informe_enlace_satelital"):
        """
        Inicializa el generador de informes.
        
        Parámetros:
        -----------
        resultados : dict
            Diccionario con los resultados del cálculo del enlace
        params : dict
            Diccionario con los parámetros de entrada
        nombre_archivo : str
            Nombre base para el archivo de informe
        """
        self.resultados = resultados
        self.params = params
        self.nombre_archivo = nombre_archivo
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF."""
        self.styles.add(ParagraphStyle(
            name='TituloCentrado',
            parent=self.styles['Title'],
            alignment=TA_CENTER,
            fontSize=18,
            spaceAfter=20
        ))
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            spaceBefore=15,
            spaceAfter=10
        ))
        self.styles.add(ParagraphStyle(
            name='NormalJustificado',
            parent=self.styles['Normal'],
            spaceBefore=5,
            spaceAfter=5
        ))
    
    def generar_pdf(self):
        """
        Genera el contenido del informe en formato PDF.
        
        Retorna:
        --------
        str : Ruta del archivo PDF generado
        """
        nombre_completo = f"{self.nombre_archivo}.pdf"
        doc = SimpleDocTemplate(nombre_completo, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        story = []
        
        # Título principal
        story.append(Paragraph("INFORME TÉCNICO DE DISEÑO DE ENLACE SATELITAL", self.styles['TituloCentrado']))
        
        # Fecha de generación
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph(f"Fecha de generación: {fecha}", self.styles['NormalJustificado']))
        story.append(Spacer(1, 20))
        
        # 1. Datos de Entrada
        story.append(Paragraph("1. DATOS DE ENTRADA", self.styles['Subtitulo']))
        story.append(self._crear_tabla_entrada())
        story.append(Spacer(1, 15))
        
        # 2. Resultados del Enlace
        story.append(Paragraph("2. RESULTADOS DEL ENLACE", self.styles['Subtitulo']))
        story.append(self._crear_tabla_resultados())
        
        doc.build(story)
        return nombre_completo
    
    def _crear_tabla_entrada(self):
        """Crea la tabla con los datos de entrada."""
        datos = [
            ["Parámetro", "Valor"],
            ["Latitud Tx (°)", f"{self.params.get('lat_tx', 0):.6f}"],
            ["Longitud Tx (°)", f"{self.params.get('lon_tx', 0):.6f}"],
            ["Latitud Rx (°)", f"{self.params.get('lat_rx', 0):.6f}"],
            ["Longitud Rx (°)", f"{self.params.get('lon_rx', 0):.6f}"],
            ["Longitud Satélite (°)", f"{self.params.get('lon_sat', 0):.2f}"],
            ["Frecuencia Up (GHz)", f"{self.params.get('f_up_ghz', 0):.2f}"],
            ["Frecuencia Down (GHz)", f"{self.params.get('f_down_ghz', 0):.2f}"],
            ["PIRE Estación (dBW)", f"{self.params.get('pire_estacion', 0):.2f}"],
            ["PIRE Satélite (dBW)", f"{self.params.get('pire_satelite', 0):.2f}"],
            ["G/T Satélite (dB/K)", f"{self.params.get('gt_satelite', 0):.2f}"],
            ["G/T Estación (dB/K)", f"{self.params.get('gt_estacion', 0):.2f}"]
        ]
        
        tabla = Table(datos, colWidths=[200, 150])
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007ACC')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
        tabla.setStyle(estilo)
        return tabla
    
    def _crear_tabla_resultados(self):
        """Crea la tabla con los resultados del enlace."""
        r = self.resultados
        datos = [
            ["Resultado", "Valor"],
            ["C/No Up (dBHz)", f"{r['resultados']['c_no_up']:.2f}"],
            ["C/No Down (dBHz)", f"{r['resultados']['c_no_down']:.2f}"],
            ["C/No Total (dBHz)", f"{r['resultados']['c_no_total']:.2f}"],
            ["C/N Total (dB)", f"{r['resultados']['c_n_total']:.2f}"],
            ["FSL Up (dB)", f"{r['perdidas']['fsl_up']:.2f}"],
            ["FSL Down (dB)", f"{r['perdidas']['fsl_down']:.2f}"],
            ["Elevación Tx (°)", f"{r['geometria_tx']['elevacion']:.2f}"],
            ["Azimut Tx (°)", f"{r['geometria_tx']['azimut']:.2f}"],
            ["Rango Tx (km)", f"{r['geometria_tx']['rango']:.2f}"],
            ["Elevación Rx (°)", f"{r['geometria_rx']['elevacion']:.2f}"],
            ["Azimut Rx (°)", f"{r['geometria_rx']['azimut']:.2f}"],
            ["Rango Rx (km)", f"{r['geometria_rx']['rango']:.2f}"]
        ]
        
        tabla = Table(datos, colWidths=[200, 150])
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
        tabla.setStyle(estilo)
        return tabla
    
    def guardar(self, nombre_archivo=None):
        """
        Guarda el informe en un archivo PDF.
        
        Parámetros:
        -----------
        nombre_archivo : str
            Nombre del archivo (opcional)
            
        Retorna:
        --------
        str : Ruta del archivo guardado
        """
        if nombre_archivo is not None:
            self.nombre_archivo = nombre_archivo
        return self.generar_pdf()


def generar_informe(resultados, params, nombre_archivo="informe_enlace_satelital"):
    """
    Función de conveniencia para generar un informe PDF.
    
    Parámetros:
    -----------
    resultados : dict
        Resultados del cálculo del enlace
    params : dict
        Parámetros de entrada
    nombre_archivo : str
        Nombre base para el archivo
        
    Retorna:
    --------
    str : Ruta del archivo guardado
    """
    generador = ReportGenerator(resultados, params, nombre_archivo)
    return generador.guardar()
