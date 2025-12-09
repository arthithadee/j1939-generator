"""
J1939 Industrial Database
Extracted from VERC/SwiSys PGN/SPN Working List
"""

# PGN Definitions
PGNS = {
    61444: {
        "name": "Electronic Engine Controller 1 (EEC1)",
        "hex": "0x0CF00400",  # Priority 3, PGN F004, Source 00 (Engine)
        "cycle_time_ms": 20,
        "spns": [899, 4154, 512, 513, 190, 2432]
    },
    65265: {
        "name": "Cruise Control/Vehicle Speed (CCVS1)",
        "hex": "0x18FEF100",
        "cycle_time_ms": 100,
        "spns": [84] 
    },
    65266: {
        "name": "Fuel Economy (LFE)",
        "hex": "0x18FEF200",
        "cycle_time_ms": 100,
        "spns": [183, 184, 51]
    },
    65262: {
        "name": "Engine Temperature 1 (ET1)",
        "hex": "0x18FEEE00",
        "cycle_time_ms": 1000,
        "spns": [110, 175]
    },
    65263: {
        "name": "Engine Fluid Level/Pressure 1 (EFL/P1)",
        "hex": "0x18FEEF00",
        "cycle_time_ms": 500,
        "spns": [98, 100]
    }
}

# SPN Definitions (ID, Name, StartByte, BitLen, Res, Offset, Min, Max, Unit)
# StartByte is 0-indexed here for Python (Doc says 1-indexed)
SPNS = {
    # --- EEC1 ---
    899:  {"name": "Engine Torque Mode", "start_byte": 0, "start_bit": 0, "len": 4, "res": 1, "offset": 0, "min": 0, "max": 15, "unit": "mode"},
    4154: {"name": "Actual Eng % Torque High Res", "start_byte": 0, "start_bit": 4, "len": 4, "res": 0.125, "offset": 0, "min": 0, "max": 0.875, "unit": "%"},
    512:  {"name": "Driver Demand Eng % Torque", "start_byte": 1, "start_bit": 0, "len": 8, "res": 1, "offset": -125, "min": -125, "max": 125, "unit": "%"},
    513:  {"name": "Actual Eng % Torque", "start_byte": 2, "start_bit": 0, "len": 8, "res": 1, "offset": -125, "min": -125, "max": 125, "unit": "%"},
    190:  {"name": "Engine Speed", "start_byte": 3, "start_bit": 0, "len": 16, "res": 0.125, "offset": 0, "min": 0, "max": 8031.875, "unit": "rpm"},
    2432: {"name": "Engine Demand % Torque", "start_byte": 7, "start_bit": 0, "len": 8, "res": 1, "offset": -125, "min": -125, "max": 125, "unit": "%"},

    # --- CCVS1 ---
    84:   {"name": "Wheel-Based Vehicle Speed", "start_byte": 1, "start_bit": 0, "len": 16, "res": 0.00390625, "offset": 0, "min": 0, "max": 250.996, "unit": "km/h"},
    
    # --- LFE ---
    183:  {"name": "Engine Fuel Rate", "start_byte": 0, "start_bit": 0, "len": 16, "res": 0.05, "offset": 0, "min": 0, "max": 3212.75, "unit": "L/h"},
    184:  {"name": "Instantaneous Fuel Economy", "start_byte": 2, "start_bit": 0, "len": 16, "res": 0.001953125, "offset": 0, "min": 0, "max": 125.5, "unit": "km/L"},
    51:   {"name": "Engine Throttle Position", "start_byte": 6, "start_bit": 0, "len": 8, "res": 0.4, "offset": 0, "min": 0, "max": 100, "unit": "%"},

    # --- ET1 ---
    110:  {"name": "Engine Coolant Temperature", "start_byte": 0, "start_bit": 0, "len": 8, "res": 1, "offset": -40, "min": -40, "max": 210, "unit": "deg C"},
    175:  {"name": "Engine Oil Temperature", "start_byte": 2, "start_bit": 0, "len": 16, "res": 0.03125, "offset": -273, "min": -273, "max": 1735, "unit": "deg C"},

    # --- EFL/P1 ---
    98:   {"name": "Engine Oil Level", "start_byte": 2, "start_bit": 0, "len": 8, "res": 0.4, "offset": 0, "min": 0, "max": 100, "unit": "%"},
    100:  {"name": "Engine Oil Pressure", "start_byte": 3, "start_bit": 0, "len": 8, "res": 4, "offset": 0, "min": 0, "max": 1000, "unit": "kPa"},
}
