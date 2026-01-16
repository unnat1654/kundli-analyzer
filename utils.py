import swisseph as swe
from typing import Tuple, Dict, Any, List
from constants import MOVABLE_SIGNS, FIXED_SIGNS, SIDEREAL_MODE, PLANET_MAPPING

def normalize_angle(angle: float) -> float:
    return angle % 360

def ist_to_utc_decimal(year: int, month: int, day: int, ist_hour: int, ist_minute: int) -> Tuple[int, int, int, float]:
    total_minutes = ist_hour * 60 + ist_minute
    utc_minutes = total_minutes - 330
    
    if utc_minutes < 0:
        utc_minutes += 1440
        day -= 1
        
    utc_hour = utc_minutes // 60
    utc_minute = utc_minutes % 60
    decimal_hour = utc_hour + utc_minute / 60.0
    
    return year, month, day, decimal_hour

def get_raw_positions(year: int, month: int, day: int, ist_hour: int, ist_minute: int, lat: float, lon: float, **kwargs) -> Tuple[Dict[str, Dict[str, Any]], List[float], List[float]]:
    swe.set_sid_mode(SIDEREAL_MODE)
    
    u_year, u_month, u_date, u_time = ist_to_utc_decimal(year, month, day, ist_hour, ist_minute)
    jd = swe.julday(u_year, u_month, u_date, u_time)
    
    positions = {}
    
    for name, pid in PLANET_MAPPING.items():
        pos, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        planet_long = normalize_angle(pos[0])
        speed = pos[3]
        
        positions[name] = {
            "longitude": planet_long,
            "speed": speed,
            "retrograde": speed < 0
        }
        
    positions["Ketu"] = {
        "longitude": normalize_angle(positions["Rahu"]["longitude"] + 180),
        "retrograde": True,
        "speed": -1 
    }
    
    raw_cusps, raw_ascmc = swe.houses_ex(jd, lat, lon, b'W', swe.FLG_SIDEREAL)
    cusps = [normalize_angle(c) for c in raw_cusps]
    ascmc = [normalize_angle(a) for a in raw_ascmc]
    
    return positions, cusps, ascmc

def get_rashi(longitude: float) -> int:
    return int(longitude // 30)

def get_house(planet_rashi: int, asc_rashi: int) -> int:
    return ((planet_rashi - asc_rashi) % 12) + 1

def get_nakshatra(longitude: float) -> int:
    return int(longitude // (13 + 20/60))

def get_pada(longitude: float) -> int:
    nak_deg = longitude % (13 + 20/60)
    return int(nak_deg // (3 + 20/60)) + 1

def get_degree_in_rashi(longitude: float) -> float:
    return longitude % 30

def get_navamsa_rashi(longitude: float) -> int:
    rashi = int(longitude // 30)
    degree = longitude % 30
    navamsa_part = int(degree // (3.3333333333333335))
    
    if rashi in MOVABLE_SIGNS:
        start = rashi
    elif rashi in FIXED_SIGNS:
        start = (rashi + 8) % 12
    else:
        start = (rashi + 4) % 12
        
    return (start + navamsa_part) % 12

def get_sub_period_duration(lord_years, main_period_years):
    years = (lord_years * main_period_years) / 120.0
    return years * 365.2425 

AGENT_NAME = 'deep-research-pro-preview-12-2025'

def create_prompt(base_kundli: str, dasha_str:str, lagna_gochar: str, jyotish_schools: list[str] = None, inc_remedy_categories: list[str] = None, exc_remedy_categories:list[str]=None, language: str = None):
    if not jyotish_schools:
        jyotish_schools = ["Vedic", "BNN", "KP"]
    
    if not language:
        language="english"

    schools_str = ", ".join(jyotish_schools)
    
    inc_line = ""
    if inc_remedy_categories:
        inc_line = f"- Suggest remedies with the help of {', '.join(inc_remedy_categories)}.\n"

    exc_line = ""
    if exc_remedy_categories:
        exc_line = f"- Avoid remedies involving {', '.join(exc_remedy_categories)}.\n"
    prompt=f'''
CONTEXT:
This is my kundli(birth chart) detail: 
{base_kundli}

This is my dasha detail:
{dasha_str}

This is my gochar phal(transit chart) detail:
{lagna_gochar}

TASK:
Research across the internet and suggest powerful remedies to balance the negatives of my kundali. 
- Consult important books, websites, and social apps.
- Consider {schools_str} schools of astrology.
- Cover all aspects of life such as family, friendships, health, finances, spiritual growth, career, faith.
{inc_line}{exc_line}

OUTPUT FORMAT:
- My Strengths
- My Weaknesses
- Remedies
- Pros and Cons List

STRICT STYLE GUIDELINES:
- Output ONLY the report.
- Do not use conversational openers or closers.
- Do not mention "Since you asked" or "As an AI".
- Start directly with the first header.
- Write in easy but professional {language}.
    '''
    return prompt


def validate_input(data):
    required_fields = ['year', 'month', 'day', 'hours', 'minutes', 'latitude', 'longitude']
    
    if not data:
        return None, "Request body must be JSON"
        
    for field in required_fields:
        if field not in data:
            return None, f"Missing required field: {field}"
        
    if 'jyotish_schools' in data and not isinstance(data['jyotish_schools'], list):
        return None, "'jyotish_schools' must be a list of strings."
        
    if 'inc_remedy_categories' in data and not isinstance(data['inc_remedy_categories'], list):
        return None, "'inc_remedy_categories' must be a list of strings."
    
    if 'exc_remedy_categories' in data and not isinstance(data['exc_remedy_categories'], list):
        return None, "'exc_remedy_categories' must be a list of strings."
    
    if 'language' in data and not isinstance(data['language'], str):
        return None, "'language' must be a string"
    try:
        clean_data = {
            'year': int(data['year']),
            'month': int(data['month']),
            'day': int(data['day']),
            'ist_hour': int(data['hours']),
            'ist_minute': int(data['minutes']),
            'lat': float(data['latitude']),
            'lon': float(data['longitude']),
            'jyotish_schools': data.get('jyotish_schools'), 
            'inc_remedy_categories': data.get('inc_remedy_categories'),
            'exc_remedy_categories': data.get('exc_remedy_categories'),
            'language': data.get('language')
        }

        if not (1 <= clean_data['month'] <= 12): return None, "Month must be 1-12"
        if not (1 <= clean_data['day'] <= 31): return None, "Day must be 1-31"
        if not (0 <= clean_data['ist_hour'] <= 23): return None, "Hours must be 0-23"
        if not (0 <= clean_data['ist_minute'] <= 59): return None, "Minutes must be 0-59"

        return clean_data, None

    except ValueError:
        return None, "Invalid data types. Ensure dates/times are integers and lat/lon are floats."
