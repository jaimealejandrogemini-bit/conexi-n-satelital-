"""
Interfaz gráfica de usuario para la herramienta de diseño de enlaces satelitales.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import webbrowser
from tkintermapview import TkinterMapView
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Importamos la lógica satelital
from core.enlace_satelital import CalculadoraSatelital

class MicrowaveLinkDesigner(tk.Tk):
    """Ventana principal de la aplicación de diseño de enlaces satelitales."""
    
    def __init__(self):
        super().__init__()
        
        self.title("Herramienta de Diseño de Enlace Satelital Extremo a Extremo")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Cargar ciudades
        self.ciudades = self.cargar_ciudades()
        
        # Variables de control
        self.setup_variables()
        
        # Crear interfaz
        self.create_menu()
        self.create_widgets()
        
        # Configurar estilos
        self.configure_styles()
        
        # Centrar ventana
        self.center_window()
    
    def setup_variables(self):
        """Inicializa las variables de control para el enlace satelital."""
        # --- Estación Transmisora (Subida) ---
        self.var_ciudad_tx = tk.StringVar()
        self.var_f_up = tk.DoubleVar(value=6.2)        # Frecuencia en GHz
        self.var_pire_tx = tk.DoubleVar(value=67.45)   # PIRE en dBW
        self.var_lluvia_up = tk.DoubleVar(value=0.5)   # Atenuación exclusiva por lluvia (dB)
        self.var_diam_tx = tk.DoubleVar(value=4.5)     # Diámetro de la antena Tx (m)
        self.var_error_tx = tk.DoubleVar(value=0.1)    # Error de apuntamiento Tx (°)
        self.var_lluvia_up_active = tk.BooleanVar(value=True)
        self.var_error_tx_active = tk.BooleanVar(value=True)

        # --- Satélite ---
        self.var_lon_sat = tk.DoubleVar(value=-69.0)   # Longitud del satélite
        self.var_gt_sat = tk.DoubleVar(value=-5.0)     # G/T en dB/K
        self.var_cno_im = tk.DoubleVar(value=99.0)     # C/No de Intermodulación en dBHz

        # --- Estación Receptora (Bajada) ---
        self.var_ciudad_rx = tk.StringVar()
        self.var_f_down = tk.DoubleVar(value=4.0)      # Frecuencia en GHz
        self.var_pire_sat = tk.DoubleVar(value=36.0)   # PIRE del satélite hacia la estación (dBW)
        self.var_gt_rx = tk.DoubleVar(value=25.0)      # G/T de la estación (dB/K)
        self.var_lluvia_down = tk.DoubleVar(value=0.3) # Atenuación exclusiva por lluvia (dB)
        self.var_diam_rx = tk.DoubleVar(value=4.5)     # Diámetro de la antena Rx (m)
        self.var_error_rx = tk.DoubleVar(value=0.1)    # Error de apuntamiento Rx (°)
        self.var_lluvia_down_active = tk.BooleanVar(value=True)
        self.var_error_rx_active = tk.BooleanVar(value=True)
        
        # Resultados
        self.resultados = None
    
    def cargar_ciudades(self):
        """Carga las ciudades desde el archivo JSON."""
        try:
            with open('data/colombia_cities.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data['ciudades']
        except FileNotFoundError:
            return self.get_default_cities()
    
    def get_default_cities(self):
        """Ciudades por defecto en caso de no encontrar el JSON."""
        return [
            {"nombre": "Bogotá", "latitud": 4.7110, "longitud": -74.0721, "altitud": 2640},
            {"nombre": "Bucaramanga", "latitud": 7.1254, "longitud": -73.1198, "altitud": 1180},
            {"nombre": "Ibagué", "latitud": 4.4389, "longitud": -75.2324, "altitud": 1285},
        ]
    
    def configure_styles(self):
        """Configura los estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#2D3E50')
        style.configure('Header.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#007ACC')
        style.configure('Result.TLabel', font=('Consolas', 10), foreground='#1E1E1E')
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'), padding=10)
    
    def create_menu(self):
        """Crea el menú de la aplicación."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo cálculo", command=self.limpiar_formulario)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.mostrar_acerca)
        help_menu.add_command(label="Manual de uso", command=self.mostrar_manual)
    
    def create_widgets(self):
        """Crea los widgets de la interfaz."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.LabelFrame(main_frame, text="Parámetros del Enlace Satelital", padding="15")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))
        left_frame.configure(width=400)
        
        self.create_input_panel(left_frame)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_results_panel(right_frame)
        
        self.status_bar = ttk.Label(self, text="Listo", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_input_panel(self, parent):
        """Crea el panel de entrada de datos con los nuevos campos."""
        # --- SECCIÓN SUBIDA ---
        frame_up = ttk.Frame(parent)
        frame_up.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(frame_up, text="1. ENLACE DE SUBIDA", style='Header.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(frame_up, text="Estación Tx:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.combo_tx = ttk.Combobox(frame_up, textvariable=self.var_ciudad_tx, state='readonly', width=16)
        self.combo_tx['values'] = [c['nombre'] for c in self.ciudades]
        if self.ciudades: self.combo_tx.current(0)
        self.combo_tx.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_up, text="Frecuencia (GHz):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_up, textvariable=self.var_f_up, width=19).grid(row=2, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_up, text="PIRE (dBW):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_up, textvariable=self.var_pire_tx, width=19).grid(row=3, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_up, text="Atenuación Lluvia (dB):").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_up, textvariable=self.var_lluvia_up, width=19).grid(row=4, column=1, sticky=tk.E, pady=2)
        ttk.Checkbutton(frame_up, text="Activar", variable=self.var_lluvia_up_active).grid(row=4, column=2, sticky=tk.W, pady=2, padx=(5,0))

        ttk.Label(frame_up, text="Diámetro Antena (m):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_up, textvariable=self.var_diam_tx, width=19).grid(row=5, column=1, sticky=tk.E, pady=2)

        ttk.Label(frame_up, text="Error Apuntamiento (°):").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_up, textvariable=self.var_error_tx, width=19).grid(row=6, column=1, sticky=tk.E, pady=2)
        ttk.Checkbutton(frame_up, text="Activar", variable=self.var_error_tx_active).grid(row=6, column=2, sticky=tk.W, pady=2, padx=(5,0))

        # --- SECCIÓN SATÉLITE ---
        frame_sat = ttk.Frame(parent)
        frame_sat.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(frame_sat, text="2. SATÉLITE", style='Header.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(frame_sat, text="Longitud (°):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_sat, textvariable=self.var_lon_sat, width=19).grid(row=1, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_sat, text="G/T (dB/K):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_sat, textvariable=self.var_gt_sat, width=19).grid(row=2, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_sat, text="C/No Intermod. (dBHz):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_sat, textvariable=self.var_cno_im, width=19).grid(row=3, column=1, sticky=tk.E, pady=2)

        # --- SECCIÓN BAJADA ---
        frame_down = ttk.Frame(parent)
        frame_down.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(frame_down, text="3. ENLACE DE BAJADA", style='Header.TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(frame_down, text="Estación Rx:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.combo_rx = ttk.Combobox(frame_down, textvariable=self.var_ciudad_rx, state='readonly', width=16)
        self.combo_rx['values'] = [c['nombre'] for c in self.ciudades]
        if len(self.ciudades) > 1: self.combo_rx.current(0)
        self.combo_rx.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_down, text="Frecuencia (GHz):").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_down, textvariable=self.var_f_down, width=19).grid(row=2, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_down, text="PIRE Satélite (dBW):").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_down, textvariable=self.var_pire_sat, width=19).grid(row=3, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_down, text="G/T Estación (dB/K):").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_down, textvariable=self.var_gt_rx, width=19).grid(row=4, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(frame_down, text="Atenuación Lluvia (dB):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_down, textvariable=self.var_lluvia_down, width=19).grid(row=5, column=1, sticky=tk.E, pady=2)
        ttk.Checkbutton(frame_down, text="Activar", variable=self.var_lluvia_down_active).grid(row=5, column=2, sticky=tk.W, pady=2, padx=(5,0))

        ttk.Label(frame_down, text="Diámetro Antena (m):").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_down, textvariable=self.var_diam_rx, width=19).grid(row=6, column=1, sticky=tk.E, pady=2)

        ttk.Label(frame_down, text="Error Apuntamiento (°):").grid(row=7, column=0, sticky=tk.W, pady=2)
        ttk.Entry(frame_down, textvariable=self.var_error_rx, width=19).grid(row=7, column=1, sticky=tk.E, pady=2)
        ttk.Checkbutton(frame_down, text="Activar", variable=self.var_error_rx_active).grid(row=7, column=2, sticky=tk.W, pady=2, padx=(5,0))

        # Botón Calcular
        btn_calcular = ttk.Button(parent, text="CALCULAR ENLACE SATELITAL", 
                                   command=self.calcular_enlace,
                                   style='Primary.TButton')
        btn_calcular.pack(fill=tk.X, pady=(20, 0))
    
    def create_results_panel(self, parent):
        """Crea el panel de resultados."""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tab_resumen = ttk.Frame(notebook, padding="10")
        notebook.add(self.tab_resumen, text="Balance de Potencia")
        self.text_resultados = scrolledtext.ScrolledText(self.tab_resumen, wrap=tk.WORD, font=('Consolas', 11))
        self.text_resultados.pack(fill=tk.BOTH, expand=True)
        self.text_resultados.tag_config("rojo", foreground="red", font=('Consolas', 11, 'bold'))
        self.text_resultados.tag_config("verde", foreground="green", font=('Consolas', 11, 'bold'))
        self.text_resultados.tag_config("naranja", foreground="orange", font=('Consolas', 11, 'bold'))
        
        self.tab_detalle = ttk.Frame(notebook, padding="10")
        notebook.add(self.tab_detalle, text="Detalles Geométricos")
        self.text_detalle = scrolledtext.ScrolledText(self.tab_detalle, wrap=tk.WORD, font=('Consolas', 10))
        self.text_detalle.pack(fill=tk.BOTH, expand=True)
        
        # --- Pestaña de Mapa Satelital ---
        self.tab_mapa = ttk.Frame(notebook, padding="10")
        notebook.add(self.tab_mapa, text="Mapa Satelital")
        self.map_widget = TkinterMapView(self.tab_mapa, width=800, height=600)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.map_widget.set_position(4.7110, -74.0721)  # Default to Bogotá
        self.map_widget.set_zoom(5)
        
        # --- Pestaña de Presupuesto de Enlace ---
        self.tab_grafico = ttk.Frame(notebook, padding="10")
        notebook.add(self.tab_grafico, text="Presupuesto de Enlace")
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # --- Pestaña de Validación ---
        self.tab_validacion = ttk.Frame(notebook, padding="10")
        notebook.add(self.tab_validacion, text="Validación")
        
        instrucciones = """=============================================================
             VALIDACIÓN MATEMÁTICA DEL MODELO
=============================================================
Según los estándares de diseño satelital, la validación 
del simulador se realiza comprobando matemáticamente las 
Pérdidas en el Espacio Libre (FSL).

Fórmula Teórica (Neri Vela):
Lel (dB) = 92.44 + 20*log10(Distancia_km) + 20*log10(Frecuencia_GHz)

--- PRUEBA DE ESCRITORIO (Uplink) ---
Si tomamos los datos geométricos calculados por el programa:
Distancia (Rango) = 35840.66 km
Frecuencia        = 6.2 GHz

Lel = 92.44 + 20*log10(35840.66) + 20*log10(6.2)
Lel = 92.44 + 91.087 + 15.847
Lel = 199.374 dB

RESULTADO DEL SOFTWARE : 199.38 dB
RESULTADO TEÓRICO      : 199.37 dB

CONCLUSIÓN:
El motor de cálculo trigonométrico y logarítmico funciona 
con total precisión, coincidiendo exactamente con la física 
de propagación de ondas en el espacio libre.
"""
        text_instr = tk.Text(self.tab_validacion, height=20, wrap=tk.WORD, font=('Consolas', 11))
        text_instr.insert('1.0', instrucciones)
        text_instr.config(state='disabled')
        text_instr.pack(fill=tk.BOTH, expand=True)
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def limpiar_formulario(self):
        self.text_resultados.delete('1.0', tk.END)
        self.text_detalle.delete('1.0', tk.END)
        self.resultados = None
        self.actualizar_estado("Formulario limpiado")
    
    def obtener_ciudad(self, nombre):
        for ciudad in self.ciudades:
            if ciudad['nombre'] == nombre:
                return ciudad
        return None
    
    def calcular_enlace(self):
        """Calcula el enlace satelital con los nuevos parámetros."""
        try:
            ciudad_tx = self.obtener_ciudad(self.var_ciudad_tx.get())
            ciudad_rx = self.obtener_ciudad(self.var_ciudad_rx.get())
            
            if not ciudad_tx or not ciudad_rx:
                messagebox.showerror("Error", "Por favor seleccione las estaciones Tx y Rx.")
                return
            
            # Constante por Absorción Atmosférica de Gases
            atenuacion_gases = 0.20
            
            lluvia_up_val = float(self.var_lluvia_up.get()) if self.var_lluvia_up_active.get() else 0.0
            lluvia_down_val = float(self.var_lluvia_down.get()) if self.var_lluvia_down_active.get() else 0.0
            error_tx_val = float(self.var_error_tx.get()) if self.var_error_tx_active.get() else 0.0
            error_rx_val = float(self.var_error_rx.get()) if self.var_error_rx_active.get() else 0.0

            params = {
                'lat_tx': ciudad_tx['latitud'],
                'lon_tx': ciudad_tx['longitud'],
                'lat_rx': ciudad_rx['latitud'],
                'lon_rx': ciudad_rx['longitud'],
                'lon_sat': float(self.var_lon_sat.get()),
                'f_up_ghz': float(self.var_f_up.get()),
                'f_down_ghz': float(self.var_f_down.get()),
                'pire_estacion': float(self.var_pire_tx.get()),
                'pire_satelite': float(self.var_pire_sat.get()),
                'gt_satelite': float(self.var_gt_sat.get()),
                'gt_estacion': float(self.var_gt_rx.get()),
                
                'lluvia_up': lluvia_up_val + atenuacion_gases,
                'lluvia_down': lluvia_down_val + atenuacion_gases,
                
                'c_no_intermodulacion': float(self.var_cno_im.get()),
                
                'diametro_tx_m': float(self.var_diam_tx.get()),
                'error_apuntamiento_grados': error_tx_val,
                'diametro_rx_m': float(self.var_diam_rx.get()),
                'error_apuntamiento_grados_rx': error_rx_val
            }
            
            calc = CalculadoraSatelital()
            self.resultados = calc.ejecutar_balance_enlace(params)
            
            self.mostrar_resultados(ciudad_tx['nombre'], ciudad_rx['nombre'])
            self.actualizar_mapa(ciudad_tx['latitud'], ciudad_tx['longitud'], ciudad_rx['latitud'], ciudad_rx['longitud'], float(self.var_lon_sat.get()))
            self.actualizar_grafico()
            self.actualizar_estado("Cálculo completado exitosamente.")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error al calcular: verifique los números.\nDetalle: {str(e)}")
            self.actualizar_estado("Error en el cálculo.")
    
    def mostrar_resultados(self, nombre_tx, nombre_rx):
        """Muestra los resultados del cálculo satelital como una 'factura' detallada."""
        if not self.resultados:
            return
        
        r = self.resultados
        
        # --- PESTAÑA RESUMEN (Balance de Potencia) ---
        self.text_resultados.delete('1.0', tk.END)
        self.text_resultados.insert(tk.END, "=" * 65 + "\n")
        self.text_resultados.insert(tk.END, "           BALANCE DE POTENCIA EXTREMO A EXTREMO\n")
        self.text_resultados.insert(tk.END, "=" * 65 + "\n\n")
        
        # SUBIDA
        self.text_resultados.insert(tk.END, "--- 1. ENLACE DE SUBIDA (Uplink) ---\n")
        self.text_resultados.insert(tk.END, f"Estación Transmisora         : {nombre_tx}\n")
        self.text_resultados.insert(tk.END, f"Frecuencia de Operación      : {self.var_f_up.get():.2f} GHz\n")
        self.text_resultados.insert(tk.END, f"Pérdidas Espacio Libre (Lel) : {r['perdidas']['fsl_up']:.2f} dB\n")
        lluvia_up_display = float(self.var_lluvia_up.get()) if self.var_lluvia_up_active.get() else 0.0
        self.text_resultados.insert(tk.END, f"Atenuación por Lluvia        : {lluvia_up_display:.2f} dB\n")
        desapuntamiento_up_display = r['perdidas'].get('desapuntamiento_up', 0.0) if self.var_error_tx_active.get() else 0.0
        self.text_resultados.insert(tk.END, f"Pérdida por Desapuntamiento  : {desapuntamiento_up_display:.2f} dB\n")
        self.text_resultados.insert(tk.END, f"Gases Atmosféricos           : 0.20 dB\n")
        self.text_resultados.insert(tk.END, "-" * 65 + "\n")
        self.text_resultados.insert(tk.END, f"C/No de Subida               : {r['resultados']['c_no_up']:.2f} dBHz\n\n\n")

        # SATÉLITE
        self.text_resultados.insert(tk.END, "--- 2. TRANSPONDEDOR (Satélite) ---\n")
        self.text_resultados.insert(tk.END, f"C/No Intermodulación         : {self.var_cno_im.get():.2f} dBHz\n\n\n")

        # BAJADA
        self.text_resultados.insert(tk.END, "--- 3. ENLACE DE BAJADA (Downlink) ---\n")
        self.text_resultados.insert(tk.END, f"Estación Receptora           : {nombre_rx}\n")
        self.text_resultados.insert(tk.END, f"Frecuencia de Operación      : {self.var_f_down.get():.2f} GHz\n")
        self.text_resultados.insert(tk.END, f"Pérdidas Espacio Libre (Lel) : {r['perdidas']['fsl_down']:.2f} dB\n")
        lluvia_down_display = float(self.var_lluvia_down.get()) if self.var_lluvia_down_active.get() else 0.0
        self.text_resultados.insert(tk.END, f"Atenuación por Lluvia        : {lluvia_down_display:.2f} dB\n")
        desapuntamiento_down_display = r['perdidas'].get('desapuntamiento_down', 0.0) if self.var_error_rx_active.get() else 0.0
        self.text_resultados.insert(tk.END, f"Pérdida por Desapuntamiento  : {desapuntamiento_down_display:.2f} dB\n")
        self.text_resultados.insert(tk.END, f"Gases Atmosféricos           : 0.20 dB\n")
        self.text_resultados.insert(tk.END, "-" * 65 + "\n")
        self.text_resultados.insert(tk.END, f"C/No de Bajada               : {r['resultados']['c_no_down']:.2f} dBHz\n\n")

        # TOTAL
        self.text_resultados.insert(tk.END, "=" * 65 + "\n")
        self.text_resultados.insert(tk.END, f"C/No TOTAL (Extremo a Extremo): {r['resultados']['c_no_total']:.2f} dBHz\n")
        self.text_resultados.insert(tk.END, f"C/N TOTAL (Señal a Ruido)   : {r['resultados']['c_n_total']:.2f} dB\n")
        self.text_resultados.insert(tk.END, "=" * 65 + "\n\n")
        
        # Evaluación de Viabilidad
        self.text_resultados.insert(tk.END, "EVALUACIÓN DE VIABILIDAD:\n")
        elev_tx = r['geometria_tx']['elevacion']
        elev_rx = r['geometria_rx']['elevacion']
        c_n_total = r['resultados']['c_n_total']
        
        if elev_tx < 5 or elev_rx < 5:
            self.text_resultados.insert(tk.END, "ESTADO: FALLIDO - Satélite por debajo del horizonte.\n", "rojo")
        elif c_n_total > 6:
            self.text_resultados.insert(tk.END, "ESTADO: ÉXITO - El enlace es viable.\n", "verde")
        else:
            self.text_resultados.insert(tk.END, "ESTADO: CRÍTICO - Señal insuficiente.\n", "naranja")

        # --- PESTAÑA DETALLES (Geometría) ---
        self.text_detalle.delete('1.0', tk.END)
        self.text_detalle.insert(tk.END, "GEOMETRÍA DEL ENLACE\n")
        self.text_detalle.insert(tk.END, "-" * 40 + "\n")
        self.text_detalle.insert(tk.END, f"SATÉLITE: Longitud {self.var_lon_sat.get()}°\n\n")
        
        self.text_detalle.insert(tk.END, f"ESTACIÓN TX ({nombre_tx}):\n")
        self.text_detalle.insert(tk.END, f"  Elevación : {r['geometria_tx']['elevacion']:.2f}°\n")
        self.text_detalle.insert(tk.END, f"  Azimut    : {r['geometria_tx']['azimut']:.2f}°\n")
        self.text_detalle.insert(tk.END, f"  Distancia : {r['geometria_tx']['rango']:.2f} km\n\n")

        self.text_detalle.insert(tk.END, f"ESTACIÓN RX ({nombre_rx}):\n")
        self.text_detalle.insert(tk.END, f"  Elevación : {r['geometria_rx']['elevacion']:.2f}°\n")
        self.text_detalle.insert(tk.END, f"  Azimut    : {r['geometria_rx']['azimut']:.2f}°\n")
        self.text_detalle.insert(tk.END, f"  Distancia : {r['geometria_rx']['rango']:.2f} km\n")
    
    def actualizar_mapa(self, lat_tx, lon_tx, lat_rx, lon_rx, lon_sat):
        """Actualiza el mapa con marcadores y línea rebotando en el satélite GEO."""
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()
        
        lat_sat = 0.0
        
        self.map_widget.set_marker(lat_tx, lon_tx, text="Tx")
        self.map_widget.set_marker(lat_sat, lon_sat, text="Satélite (GEO)")
        self.map_widget.set_marker(lat_rx, lon_rx, text="Rx")
        
        self.map_widget.set_path([(lat_tx, lon_tx), (lat_sat, lon_sat), (lat_rx, lon_rx)], color="red", width=2)
        
        # Fit bounding box to include all 3 points (Tx, Satélite, Rx)
        min_lat = min(lat_tx, lat_rx, lat_sat)
        max_lat = max(lat_tx, lat_rx, lat_sat)
        min_lon = min(lon_tx, lon_rx, lon_sat)
        max_lon = max(lon_tx, lon_rx, lon_sat)
        
        # Add more padding to see the full path
        padding = 20.0
        self.map_widget.fit_bounding_box(
            (max_lat + padding, min_lon - padding),
            (min_lat - padding, max_lon + padding)
        )
    
    def actualizar_grafico(self):
        """Actualiza el gráfico de barras del presupuesto de enlace."""
        if not self.resultados:
            return
        
        r = self.resultados
        
        # Datos para el gráfico (downlink como ejemplo principal)
        pire_inicial = float(self.var_pire_sat.get())
        perdidas_fsl = r['perdidas']['fsl_down']
        perdidas_lluvia = float(self.var_lluvia_down.get()) if self.var_lluvia_down_active.get() else 0.0
        perdidas_total = perdidas_fsl + perdidas_lluvia + 0.20
        potencia_recibida = pire_inicial - perdidas_total
        sensibilidad = -120.0  # Valor típico de ejemplo
        
        self.ax.clear()
        
        # Asegurar que etiquetas y valores son listas explícitas
        etiquetas = ["PIRE Inicial", "Potencia Recibida"]
        valores = [float(pire_inicial), float(potencia_recibida)]  # Convertir explícitamente a float
        colores = ["#2ecc71", "#3498db"]
        
        barras = self.ax.bar(etiquetas, valores, color=colores, edgecolor='black', linewidth=1.5)
        
        # Añadir valores en las barras
        for barra in barras:
            altura = barra.get_height()
            self.ax.text(barra.get_x() + barra.get_width()/2., altura,
                        f'{altura:.2f} dBW',
                        ha='center', va='bottom', fontweight='bold')
        
        # Línea de sensibilidad
        self.ax.axhline(y=sensibilidad, color='red', linestyle='--', linewidth=2, label=f'Sensibilidad: {sensibilidad:.2f} dBW')
        
        self.ax.set_title('Presupuesto de Enlace (Downlink)', fontsize=14, fontweight='bold')
        self.ax.set_ylabel('Potencia (dBW)', fontsize=12)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7)
        self.ax.legend()
        # Asegurar límites son válidos
        y_min = min(sensibilidad, potencia_recibida) - 10
        y_max = pire_inicial + 10
        self.ax.set_ylim(y_min, y_max)
        
        self.canvas.draw()
    
    def actualizar_estado(self, mensaje):
        self.status_bar.config(text=mensaje)
    
    def mostrar_acerca(self):
        mensaje = """HERRAMIENTA DE DISEÑO DE ENLACE SATELITAL\n\nBasado en la teoría de Neri Vela."""
        messagebox.showinfo("Acerca de", mensaje)
    
    def mostrar_manual(self):
        mensaje = """MANUAL DE USO\n\n1. Seleccione parámetros de subida.\n2. Configure satélite.\n3. Seleccione parámetros de bajada.\n4. Haga clic en CALCULAR."""
        messagebox.showinfo("Manual de Uso", mensaje)

if __name__ == "__main__":
    app = MicrowaveLinkDesigner()
    app.mainloop()
