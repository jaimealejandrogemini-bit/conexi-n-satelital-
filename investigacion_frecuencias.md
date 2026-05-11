# Investigación: Bandas de Frecuencia para Enlaces de Microondas en Colombia

## Recomendaciones ITU-R

La Unión Internacional de Telecomunicaciones (UIT) a través de la recomendación ITU-R F.1101 define las características de los sistemas de enlaces digitales fijos operando en las bandas de frecuencia desde aproximadamente 1 GHz hasta aproximadamente 86 GHz.

### Bandas de Frecuencia Comunes para Enlaces de Microondas

| Banda | Rango de Frecuencia | Uso Típico |
|-------|-------------------|------------|
| L | 1-2 GHz | Enlaces de larga distancia, backhaul celular |
| S | 2-4 GHz | Enlaces regionales, redundancia |
| C | 4-8 GHz | Enlaces interurbanos (más común en Colombia) |
| X | 8-12 GHz | Enlaces urbanos y suburbanos |
| Ku | 12-18 GHz | Enlaces de corta y media distancia |
| K | 18-27 GHz | Enlaces de alta capacidad, corta distancia |
| Ka | 27-40 GHz | Enlaces de muy alta capacidad |

## Regulación Colombiana (ANE/MinTic)

En Colombia, la asignación de frecuencias para enlaces de microondas está regulada por la Agencia Nacional del Espectro (ANE) y el Ministerio de Tecnologías de la Información y las Comunicaciones (MinTic).

### Bandas Asignadas en Colombia

Las bandas más utilizadas para enlaces punto a punto en Colombia son:
- **3.5 GHz**: Banda licenciada para servicios fijos
- **5.8 GHz**: Banda unlicensed (uso libre con restricciones)
- **6 GHz**: Banda licenciada para servicios fijos
- **11 GHz**: Banda licenciada para enlaces de microondas
- **13 GHz**: Banda licenciada para alta capacidad
- **15 GHz**: Banda licenciada para alta capacidad
- **18 GHz**: Banda licenciada para muy alta capacidad
- **23 GHz**: Banda licenciada para alta capacidad

## Parámetros de Diseño Recomendados

### Frecuencias de Trabajo Sugeridas para la Herramienta

Para el diseño de la herramienta, se sugieren las siguientes frecuencias:
- **Frecuencia primaria**: 6 GHz (banda C)
- **Frecuencia alternativa**: 11 GHz (banda X)
- **Frecuencia alternativa**: 18 GHz (banda K)

### Ancho de Banda del Canal

- 28 MHz para sistemas de alta capacidad
- 14 MHz para sistemas de capacidad media
- 7 MHz para sistemas de baja capacidad

## Referencias Normativas

1. ITU-R F.1101: Characteristics of fixed service digital transmission systems
2. ITU-R F.386: Impulse propagation prediction on line-of-sight radio-relay systems
3. ITU-R P.530: Propagation data and prediction methods required for the design of terrestrial line-of-sight systems
4. Resolución CRC 5050/2017 - Cuadro nacional de atribución de bandas de frecuencia
5. Ley 1341 de 2009 - Gestión del espectro radioeléctrico en Colombia
