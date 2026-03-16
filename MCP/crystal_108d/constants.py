"""
Shared constants for the crystal_108d package.
Centralises values that were previously duplicated across modules.
"""

# Superphase / wreath code → human-readable name
SUPERPHASE_NAMES: dict[str, str] = {
    "Su": "Sulfur",
    "Me": "Mercury",
    "Sa": "Salt",
}

# Lens code → full name
LENS_CODES: dict[str, str] = {
    "S": "Square",
    "F": "Flower",
    "C": "Cloud",
    "R": "Fractal",
}

# 12 archetype names in canonical order (index 1-12)
ARCHETYPE_NAMES: list[str] = [
    "Apex Seed",
    "Möbius Axle",
    "Modal Trefoil",
    "Crystal Quartet",
    "Observer Pentad",
    "Dyadic Hinge Hexad",
    "Change/Arc Heptad",
    "Antispin Octad",
    "Emergent Ennead",
    "Deca-Cascade Crown",
    "Odd-Orbit Hendecad",
    "Dodecad Bundle",
]

# Total shells, nodes, wreaths
TOTAL_SHELLS = 36
TOTAL_NODES = 666  # T_36 = 36 * 37 / 2
TOTAL_WREATHS = 3

# Master clock
MASTER_CLOCK_PERIOD = 420  # lcm(3, 4, 5, 7)
