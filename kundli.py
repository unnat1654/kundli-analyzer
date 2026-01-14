from typing import TypedDict, Dict, Any
from utils import (
    get_rashi, get_degree_in_rashi, 
    get_navamsa_rashi, get_house, get_nakshatra, get_pada
)
from constants import (
    UCCH_RASHI, NEECH_RASHI, RASHI_NAMES, NAKSHATRA_NAMES
)
import matplotlib
matplotlib.use("Agg")  # NON-GUI backend
import matplotlib.pyplot as plt
import io



class PlanetDetails(TypedDict):
    longitude: float
    rashi: int
    degree: float
    D9_rashi: int
    house: int
    nakshatra: int
    pada: int
    retrograde: bool
    vargottam: bool
    ucch: bool
    neech: bool

def generate_kundli(
   positions: Dict[str, Dict[str, Any]], asc_rashi:int
) -> tuple[str, dict[str, PlanetDetails]]:
    kundli_data: Dict[str, PlanetDetails] = {}
    report_lines = []

    for planet, data in positions.items():
        longitude = data["longitude"]
        
        curr_rashi = get_rashi(longitude)
        curr_d9 = get_navamsa_rashi(longitude)
        
        details: PlanetDetails = {
            "longitude": longitude,
            "rashi": curr_rashi,
            "degree": get_degree_in_rashi(longitude),
            "D9_rashi": curr_d9,
            "house": get_house(curr_rashi, asc_rashi),
            "nakshatra": get_nakshatra(longitude),
            "pada": get_pada(longitude),
            "retrograde": data.get("retrograde", False),
            "vargottam": curr_rashi == curr_d9,
            "ucch": curr_rashi == UCCH_RASHI.get(planet, -1),
            "neech": curr_rashi == NEECH_RASHI.get(planet, -1)
        }
        
        kundli_data[planet] = details

        block = (
            f"--- {planet} ---\n"
            f"Rashi (Sign): {RASHI_NAMES[details['rashi']]}  |  House: {details['house']}\n"
            f"Degree in sign: {details['degree']:.2f}°\n"
            f"Navamsa (D9 Rashi): {RASHI_NAMES[details['D9_rashi']]}\n"
            f"Nakshatra: {NAKSHATRA_NAMES[details['nakshatra']]}  |  Pada: {details['pada']}\n"
            f"Retrograde: {'Yes' if details['retrograde'] else 'No'}\n"
            f"Vargottam: {'Yes' if details['vargottam'] else 'No'}\n"
            f"Ucch: {'Yes' if details['ucch'] else 'No'}  |  Neech: {'Yes' if details['neech'] else 'No'}\n"
        )
        report_lines.append(block)

    return "\n".join(report_lines), kundli_data


def generate_d1_img(kundli_data: Dict[str, PlanetDetails], ascendant_sign: int):
    ascendant_sign+=1
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect('equal')
    ax.axis('off')

    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color='maroon', linewidth=2)
    ax.plot([0, 1], [0, 1], color='maroon', linewidth=1.5)
    ax.plot([0, 1], [1, 0], color='maroon', linewidth=1.5)
    ax.plot([0.5, 1, 0.5, 0, 0.5], [0, 0.5, 1, 0.5, 0], color='maroon', linewidth=1.5)

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
            if details.get('retrograde'):      markers += r"*"
            if details.get('ucch'):       markers += r"\uparrow"
            if details.get('neech'):      markers += r"\downarrow"
            if details.get('vargottam'):  markers += r"\wedge"

            raw_deg = details.get('degree', 0)
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
        ax.text(rx, ry, str(rashi_num), fontsize=10, color='crimson', 
                ha='center', va='center', fontweight='bold')

        planets = house_occupants[house_num]
        if planets:
            label = "\n".join(planets)
            px, py = coords['planet']
            ax.text(px, py, label, fontsize=9, color='navy', 
                    ha='center', va='center', fontweight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    plt.close(fig)
    return buf


