"""
Braking Tool Constants Module
============================
Purpose:
    Defines physical constants and engineering standards data for braking calculations.
    Based on DIN EN 15746-2:2021-05 European standards for rail vehicle braking.
Layer:
    Backend / Tools / Braking / Constants
Standards:
    - DIN EN 15746-2:2021-05: Railway applications - Railway braking
    - Defines maximum stopping distances for various speeds
    - Used for compliance checking in braking calculations
Physical Constants:
    - G: Standard gravity acceleration (9.81 m/s²)
Data Sources:
    - BRAKING_DATA: Reference braking distances for force calculations
    - MAX_STOPPING_DISTANCES: EN standard limits for compliance checking
Units:
    - Speeds: km/h
    - Distances: meters
    - Forces: Newtons (calculated from mass and deceleration)
"""

# Physical constants
G = 9.81  # Standard gravity acceleration (m/s²)

# Reference braking distances for force capability calculations
# Based on DIN EN 15746-2:2021-05 standards
# Format: {speed_kmh: stopping_distance_meters}
# Used to calculate required braking forces for different speed scenarios
BRAKING_DATA = {
    8: 3,    # 8 km/h requires 3 meters stopping distance
    10: 5,   # 10 km/h requires 5 meters stopping distance
    16: 12,  # 16 km/h requires 12 meters stopping distance
    20: 20,  # 20 km/h requires 20 meters stopping distance
    24: 28,  # 24 km/h requires 28 meters stopping distance
    30: 45,  # 30 km/h requires 45 meters stopping distance
    32: 50,  # 32 km/h requires 50 meters stopping distance
    40: 75,  # 40 km/h requires 75 meters stopping distance
    50: 135, # 50 km/h requires 135 meters stopping distance
    60: 180  # 60 km/h requires 180 meters stopping distance
}

# Maximum allowable stopping distances per EN standards
# Used for compliance checking - if calculated distance exceeds these,
# the design is non-compliant with safety standards
# Format: {speed_kmh: max_stopping_distance_meters}
MAX_STOPPING_DISTANCES = {
    8: 6,    # Maximum 6 meters at 8 km/h
    10: 9,   # Maximum 9 meters at 10 km/h
    16: 18,  # Maximum 18 meters at 16 km/h
    20: 27,  # Maximum 27 meters at 20 km/h
    24: 36,  # Maximum 36 meters at 24 km/h
    30: 55,  # Maximum 55 meters at 30 km/h
    32: 60,  # Maximum 60 meters at 32 km/h
    40: 90,  # Maximum 90 meters at 40 km/h
    50: 155, # Maximum 155 meters at 50 km/h
    60: 230, # Maximum 230 meters at 60 km/h
    70: 300, # Maximum 300 meters at 70 km/h
    80: 400, # Maximum 400 meters at 80 km/h
    90: 500, # Maximum 500 meters at 90 km/h
    100: 620 # Maximum 620 meters at 100 km/h
}