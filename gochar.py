
from datetime import datetime
from typing import TypedDict, Dict
from utils import (
    get_raw_positions, get_rashi, get_degree_in_rashi, 
    get_house, get_nakshatra, get_pada
)
from constants import (
    UCCH_RASHI, NEECH_RASHI, RASHI_NAMES, NAKSHATRA_NAMES
)
import matplotlib.pyplot as plt
import io

class GocharPlanetDetails(TypedDict):
    degree: float
    house: int
    retrograde: bool
    ucch: bool
    neech: bool

def generate_lagna_gochar(
    lat: float, lon: float, asc_rashi:int
) -> tuple[str, Dict[str, GocharPlanetDetails]]:
    """
    Calculates the positions of current (transit) planets and maps them 
    to the Houses of the Birth Ascendant (Lagna Gochar).
    """
    
    transit_date = datetime.now()
        
    transit_positions, _, _ = get_raw_positions(
        transit_date.year, transit_date.month, transit_date.day,
        transit_date.hour, transit_date.minute, lat, lon
    )
    
    gochar_data: Dict[str, GocharPlanetDetails] = {}

    report_lines = []
    report_lines.append(f"=== LAGNA GOCHAR REPORT ===")
    report_lines.append(f"Birth Lagna (Ascendant): {RASHI_NAMES[asc_rashi]}\n")
    
    for planet, data in transit_positions.items():
        t_long = data["longitude"]

        t_rashi = get_rashi(t_long)
        t_degree = get_degree_in_rashi(t_long)
        t_nakshatra = get_nakshatra(t_long)
        t_pada = get_pada(t_long)

        gochar_house = get_house(t_rashi, asc_rashi)

        is_retro = data.get("retrograde", False)
        is_ucch = t_rashi == UCCH_RASHI.get(planet, -1)
        is_neech = t_rashi == NEECH_RASHI.get(planet, -1)

        gochar_data[planet]={
            "degree":t_degree,
            "house":gochar_house,
            "retrograde":is_retro,
            "ucch":is_ucch,
            "neech":is_neech
        }
        
        block = (
            f"--- {planet} (Transit) ---\n"
            f"Transit Rashi: {RASHI_NAMES[t_rashi]} ({t_degree:.2f}°)\n"
            f"Gochar House: {gochar_house} (Relative to Birth Lagna)\n"
            f"Nakshatra: {NAKSHATRA_NAMES[t_nakshatra]} ({t_pada})\n"
            f"Status: {'[Retro]' if is_retro else ''} {'[Exalted]' if is_ucch else ''} {'[Debilitated]' if is_neech else ''}\n"
        )
        report_lines.append(block)
        
    return "\n".join(report_lines), gochar_data


def generate_gochar_img(kundli_data:Dict[str,GocharPlanetDetails], ascendant_sign:int):
    ascendant_sign+=1
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.axis('off')

    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color='black', linewidth=2)
    ax.plot([0, 1], [0, 1], color='black', linewidth=1.5)
    ax.plot([0, 1], [1, 0], color='black', linewidth=1.5)
    ax.plot([0.5, 1, 0.5, 0, 0.5], [0, 0.5, 1, 0.5, 0], color='black', linewidth=1.5)

    house_coords = {
        1:  {'planet': (0.5, 0.75), 'rashi': (0.5, 0.55)},
        4:  {'planet': (0.25, 0.5), 'rashi': (0.46, 0.5)}, 
        7:  {'planet': (0.5, 0.25), 'rashi': (0.5, 0.45)},
        10: {'planet': (0.75, 0.5), 'rashi': (0.54, 0.5)}, 
        2:  {'planet': (0.25, 0.85),'rashi': (0.15, 0.92)},
        3:  {'planet': (0.1, 0.65), 'rashi': (0.05, 0.75)},
        5:  {'planet': (0.1, 0.35), 'rashi': (0.05, 0.25)},
        6:  {'planet': (0.25, 0.15),'rashi': (0.15, 0.08)},
        8:  {'planet': (0.75, 0.15),'rashi': (0.85, 0.08)},
        9:  {'planet': (0.9, 0.35), 'rashi': (0.95, 0.25)}, 
        11: {'planet': (0.9, 0.65), 'rashi': (0.95, 0.75)}, 
        12: {'planet': (0.75, 0.85),'rashi': (0.85, 0.92)}
    }

    house_occupants = {i: [] for i in range(1, 13)}

    for planet, details in kundli_data.items():
        h = details['house']
        if 1 <= h <= 12:
            markers = ""
            if details['retrograde']:      markers += r"*"
            if details['ucch']:       markers += r"\uparrow"
            if details['neech']:      markers += r"\downarrow"

            raw_deg = details["degree"]
            try:
                deg_str = f"{float(raw_deg):.2f}"
            except (ValueError, TypeError):
                deg_str = str(raw_deg)

            label = f"$\mathbf{{{planet}}}^{{{markers}}}_{{{deg_str}^\circ}}$"
            
            house_occupants[h].append(label)

    for house_num in range(1, 13):
        coords = house_coords[house_num]

        rashi_num = (ascendant_sign + house_num - 2) % 12 + 1

        rx, ry = coords['rashi']
        ax.text(rx, ry, str(rashi_num), fontsize=10, color='gold', 
                ha='center', va='center', fontweight='bold')

        planets = house_occupants[house_num]
        if planets:
            label = "\n".join(planets)
            px, py = coords['planet']
            ax.text(px, py, label, fontsize=9, color='green', 
                    ha='center', va='center', fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    plt.close(fig)
    return buf