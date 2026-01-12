import swisseph as swe
from typing import Dict, List

SIDEREAL_MODE: int = swe.SIDM_LAHIRI

PLANET_MAPPING: Dict[str, int] = {
    "Surya": swe.SUN,
    "Chandra": swe.MOON,
    "Mangal": swe.MARS,
    "Budh": swe.MERCURY,
    "Guru": swe.JUPITER,
    "Shukra": swe.VENUS,
    "Shani": swe.SATURN,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "Uranus": swe.URANUS,
    "Rahu": swe.MEAN_NODE,
}

UCCH_RASHI: Dict[str, int] = {
    "Surya": 0, "Chandra": 1, "Mangal": 9, "Budh": 7,
    "Guru": 3, "Shukra": 11, "Shani": 6, "Rahu": 1, "Ketu": 7
}

NEECH_RASHI: Dict[str, int] = {
    "Surya": 6, "Chandra": 7, "Mangal": 3, "Budh": 11,
    "Guru": 9, "Shukra": 7, "Shani": 0, "Rahu": 7, "Ketu": 1
}

MOVABLE_SIGNS: List[int] = [0, 3, 6, 9]
FIXED_SIGNS: List[int] = [1, 4, 7, 10]
DUAL_SIGNS: List[int] = [2, 5, 8, 11]

RASHI_NAMES: List[str] = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)",
    "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrischika (Scorpio)",
    "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

NAKSHATRA_NAMES: List[str] = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]


DASHA_ORDER: List[str] = ['Ketu', 'Shukra', 'Surya', 'Chandra', 'Mangal', 'Rahu', 'Guru', 'Shani', 'Budh']

DASHA_YEARS: Dict[str, int] = {
    'Ketu': 7, 'Shukra': 20, 'Surya': 6, 'Chandra': 10, 'Mangal': 7, 
    'Rahu': 18, 'Guru': 16, 'Shani': 19, 'Budh': 17
}