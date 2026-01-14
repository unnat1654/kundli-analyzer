from datetime import datetime, timedelta
from typing import Any, Dict
from utils import get_sub_period_duration
from constants import NAKSHATRA_NAMES, DASHA_ORDER, DASHA_YEARS

def generate_dasha(moon_lon:float, birth_date:datetime)->tuple[str, Dict[str, Any]]:
    target_date=datetime.now()
    # --- 1. Calculate Birth Dasha ---
    nakshatra_span = 13 + (1/3) 
    
    nakshatra_idx = int(moon_lon / nakshatra_span)
    degree_into_nak = moon_lon % nakshatra_span

    nakshatra_name = NAKSHATRA_NAMES[nakshatra_idx % 27] 
    
    fraction_traversed = degree_into_nak / nakshatra_span
    fraction_remaining = 1.0 - fraction_traversed
    
    lord_idx = nakshatra_idx % 9
    birth_lord = DASHA_ORDER[lord_idx]
    full_period_years = DASHA_YEARS[birth_lord]
    
    balance_years = fraction_remaining * full_period_years
    balance_days = balance_years * 365.2425
    
    birth_dasha_end_date = birth_date + timedelta(days=balance_days)

    birth_data = {
        "lord": birth_lord,
        "nakshatra_name": nakshatra_name,
        "nakshatra_idx": nakshatra_idx + 1, 
        "balance_years": round(balance_years, 4),
        "start_date": birth_date, 
        "end_date": birth_dasha_end_date
    }

    current_md_lord = birth_lord
    md_start_date = birth_date
    md_end_date = birth_dasha_end_date
    
    curr_idx = lord_idx
    
    if target_date <= birth_dasha_end_date:
        current_md_lord = birth_lord
        md_start_date = birth_date
        md_end_date = birth_dasha_end_date
    else:
        while md_end_date < target_date:
            curr_idx = (curr_idx + 1) % 9
            current_md_lord = DASHA_ORDER[curr_idx]
            duration = DASHA_YEARS[current_md_lord]
            
            md_start_date = md_end_date
            md_end_date = md_start_date + timedelta(days=duration * 365.2425)

    # --- 3. Calculate Antardasha ---
    ad_lord = current_md_lord
    ad_start_date = md_start_date
    ad_end_date = md_start_date 
    ad_idx = DASHA_ORDER.index(current_md_lord)
    
    while True:
        ad_lord_name = DASHA_ORDER[ad_idx]
        ad_duration_days = get_sub_period_duration(DASHA_YEARS[ad_lord_name], DASHA_YEARS[current_md_lord])
        ad_end_date = ad_start_date + timedelta(days=ad_duration_days)
        
        if ad_end_date > target_date:
            ad_lord = ad_lord_name
            break
        
        ad_start_date = ad_end_date
        ad_idx = (ad_idx + 1) % 9

    pd_lord = ad_lord
    pd_start_date = ad_start_date
    pd_end_date = ad_start_date 
    pd_idx = DASHA_ORDER.index(ad_lord)
    
    while True:
        pd_lord_name = DASHA_ORDER[pd_idx]
        pd_years = (DASHA_YEARS[current_md_lord] * DASHA_YEARS[ad_lord] * DASHA_YEARS[pd_lord_name]) / 14400.0
        pd_duration_days = pd_years * 365.2425
        
        pd_end_date = pd_start_date + timedelta(days=pd_duration_days)
        
        if pd_end_date > target_date:
            pd_lord = pd_lord_name
            break
            
        pd_start_date = pd_end_date
        pd_idx = (pd_idx + 1) % 9

    # --- 5. Save Data ---
    dasha_data = {
        "birth_dasha": birth_data,
        "current_dasha": {
            "mahadasha": {
                "lord": current_md_lord,
                "start": md_start_date,
                "end": md_end_date
            },
            "antardasha": {
                "lord": ad_lord,
                "start": ad_start_date,
                "end": ad_end_date
            },
            "pratyantardasha": {
                "lord": pd_lord,
                "start": pd_start_date,
                "end": pd_end_date
            }
        }
    }

    fmt = "%Y-%m-%d"
    bd = dasha_data['birth_dasha']
    md = dasha_data['current_dasha']['mahadasha']
    ad = dasha_data['current_dasha']['antardasha']
    pd = dasha_data['current_dasha']['pratyantardasha']

    is_active = target_date <= bd['end_date']

    md_section = ""
    if not is_active:
        md_section = (
            f"   MAHADASHA (Major Period): {md['lord']}\n"
            f"   > Active from {md['start'].strftime(fmt)} to {md['end'].strftime(fmt)}\n"
        )

    dasha_str = (
        f"VIMSHOTTARI DASHA REPORT\n"
        f"========================\n"
        f"1. BIRTH CONTEXT\n"
        f"   Birth Nakshatra: {bd['nakshatra_name']}\n"
        f"   Born under {bd['lord']} Dasha.\n"
        f"   Balance at birth: {bd['balance_years']} years.\n"
        f"   This foundation period {'ends' if is_active else 'ended'} on: {bd['end_date'].strftime(fmt)}\n"
        f"2. CURRENT STATUS\n"
        f"{md_section}"
        f"   ANTARDASHA (Sub Period): {ad['lord']}\n"
        f"   > Active from {ad['start'].strftime(fmt)} to {ad['end'].strftime(fmt)}\n"
        f"   PRATYANTARDASHA (Sub-Sub Period): {pd['lord']}\n"
        f"   > Active from {pd['start'].strftime(fmt)} to {pd['end'].strftime(fmt)}\n"
    )
    return dasha_str, dasha_data

if __name__ == "__main__":
    moon_longitude = 45.0 
    dob = datetime(2000, 1, 1)

    print(generate_dasha(moon_longitude, dob))