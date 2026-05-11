"""
Paquete core - Módulos de cálculo para diseño de enlaces de microondas.
"""

from core.constants import (
    EARTH_RADIUS_KM,
    SPEED_OF_LIGHT_KM_S,
    FREQUENCY_BANDS,
    DEFAULT_FREQUENCIES,
    AVAILABILITY_OPTIONS,
    TX_POWER_OPTIONS,
    RECEIVER_SENSITIVITY,
    MIN_DISTANCE_KM,
    MARGEN_FRESNEL,
    MARGEN_SEGURIDAD_M,
    K_DEFAULT,
    K_MIN
)

from core.geography import (
    haversine_distance,
    calculate_azimuth,
    calculate_reverse_azimuth,
    calculate_earth_curvature_correction,
    calculate_first_fresnel_radius,
    calculate_required_clearance,
    calculate_tower_height_for_los,
    interpolate_terrain_points,
    calculate_distance_direction,
    get_cardinal_direction
)

from core.propagation import (
    free_space_loss,
    rain_attenuation_itu_p530,
    atmospheric_gas_attenuation,
    total_path_loss,
    link_power_balance,
    calculate_link_availability,
    fresnel_zone_clearance
)

from core.repeater import (
    RepeaterDesigner,
    create_repeater_link
)

__all__ = [
    'constants',
    'geography',
    'propagation',
    'repeater'
]
