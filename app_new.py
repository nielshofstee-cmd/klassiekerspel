import unicodedata
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import cloudscraper
from thefuzz import fuzz, process
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


# py -m streamlit run app_new.py         >> C:\Users\hofsteen\OneDrive - HEMA\Niels HEMA\Python projects\wielerspel\Wielerspel 2.0

# --- CONFIGURATIE ---
st.set_page_config(page_title="K1xSam Klassiekerspel 2026", page_icon="🚴‍♂️", layout="wide")

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
/* === GOOGLE FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

/* === ROOT VARIABELEN === */
:root {
    --blauw: #0d1f35;
    --blauw-mid: #112840;
    --blauw-licht: #1a4a7a;
    --blauw-accent: #1e5799;
    --oranje: #f47c20;
    --oranje-licht: #ff9a45;
    --oranje-glow: rgba(244,124,32,0.15);
    --wit: #ffffff;
    --grijs-licht: #eef1f6;
    --grijs-mid: #d8e0eb;
    --grijs-donker: #8a9ab5;
    --tekst-donker: #0d1f35;
    --tekst-grijs: #5a6a82;
    --card-shadow: 0 4px 24px rgba(13,31,53,0.10);
    --card-shadow-hover: 0 8px 32px rgba(13,31,53,0.16);
}

/* === ACHTERGROND === */
.stApp {
    background: linear-gradient(160deg, #ccdaee 0%, #b8cfe8 50%, #a0bfde 100%);
    background-attachment: fixed;
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
}

/* Herstel tekst kleuren voor lichte achtergrond */
h1 { color: var(--blauw) !important; }
h2, h3 { color: var(--blauw) !important; }

[data-testid="stMetric"] {
    background: var(--wit) !important;
    border: 1px solid rgba(244,124,32,0.15) !important;
    border-top: 3px solid var(--oranje) !important;
    box-shadow: 0 4px 24px rgba(244,124,32,0.08) !important;
}

[data-testid="stMetricLabel"] { color: var(--tekst-grijs) !important; }
[data-testid="stMetricValue"] { color: var(--blauw) !important; }

[data-testid="stDataFrame"] {
    border: 1px solid rgba(244,124,32,0.12) !important;
    box-shadow: 0 4px 24px rgba(244,124,32,0.06) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--wit) !important;
    border: 1px solid rgba(244,124,32,0.15) !important;
    box-shadow: 0 4px 16px rgba(244,124,32,0.08) !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    color: var(--tekst-grijs) !important;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    background: rgba(244,124,32,0.06) !important;
    color: var(--blauw) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, var(--blauw) 0%, var(--blauw-accent) 100%) !important;
    color: var(--wit) !important;
}

[data-testid="stSelectbox"] > div > div {
    background: var(--wit) !important;
    border-color: rgba(244,124,32,0.2) !important;
}

[data-testid="stTextInput"] input {
    background: var(--wit) !important;
    border-color: rgba(244,124,32,0.2) !important;
}

hr { border-top: 1px solid rgba(244,124,32,0.12) !important; }

[data-testid="stCaptionContainer"] { color: var(--tekst-grijs) !important; }

/* === VERBERG STANDAARD SIDEBAR === */
[data-testid="stSidebar"] { display: none !important; }

/* === VERBERG STREAMLIT CHROME VOLLEDIG === */
header[data-testid="stHeader"] {
    display: none !important;
}
#MainMenu, footer { visibility: hidden; }
.stAppDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* === TOPBALK NAVIGATIE === */
.nav-container {
    background: linear-gradient(160deg, var(--blauw) 0%, var(--blauw-mid) 60%, #0a1e34 100%);
    padding: 0;
    margin: -1rem -1rem 2rem -1rem;
    box-shadow: 0 4px 32px rgba(13,31,53,0.45);
    position: sticky;
    top: 0;
    z-index: 999;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.nav-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    height: 56px;
}

.nav-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 26px;
    font-weight: 400;
    color: var(--wit);
    letter-spacing: 3px;
    text-transform: uppercase;
    line-height: 1;
}

.nav-logo span {
    color: var(--oranje);
    text-shadow: 0 0 20px rgba(244,124,32,0.4);
}

.nav-logo .sep {
    color: rgba(255,255,255,0.2);
    margin: 0 8px;
    font-weight: 300;
}

.nav-season {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px;
    font-weight: 500;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 3px;
    background: rgba(255,255,255,0.05);
    padding: 4px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* === PAGE TITLES === */
h1 {
    font-family: 'Bebas Neue', sans-serif !important;
    font-weight: 400 !important;
    font-size: 2.8rem !important;
    color: var(--blauw) !important;
    letter-spacing: 2px !important;
    margin-bottom: 1.5rem !important;
    line-height: 1 !important;
    position: relative;
}

h1::after {
    content: '';
    display: block;
    width: 48px;
    height: 3px;
    background: linear-gradient(90deg, var(--oranje), transparent);
    margin-top: 8px;
    border-radius: 2px;
}

h2, h3 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    color: var(--blauw) !important;
    letter-spacing: 0.2px !important;
}

/* === METRIC CARDS === */
[data-testid="stMetric"] {
    background: var(--wit);
    border-radius: 14px;
    padding: 22px 24px !important;
    border: 1px solid var(--grijs-mid);
    border-top: 3px solid var(--oranje);
    box-shadow: var(--card-shadow);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    box-shadow: var(--card-shadow-hover);
    transform: translateY(-1px);
}

[data-testid="stMetricLabel"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--tekst-grijs) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem !important;
    font-weight: 400;
    color: var(--blauw) !important;
    letter-spacing: 1px;
}

/* === TABS === */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--wit);
    border-radius: 12px;
    padding: 5px;
    gap: 3px;
    box-shadow: var(--card-shadow);
    margin-bottom: 2rem;
    border: 1px solid var(--grijs-mid);
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 13px;
    color: var(--tekst-grijs);
    border-radius: 9px;
    padding: 9px 18px;
    border: none !important;
    background: transparent;
    transition: all 0.15s ease;
    letter-spacing: 0.2px;
}

[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--blauw);
    background: var(--grijs-licht) !important;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg, var(--blauw) 0%, var(--blauw-accent) 100%) !important;
    color: var(--wit) !important;
    box-shadow: 0 2px 8px rgba(13,31,53,0.2);
}

/* === DATAFRAMES === */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
    box-shadow: var(--card-shadow);
    border: 1px solid var(--grijs-mid);
}

/* Alle tekst in tabellen donkerblauw */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [class*="cell"],
[data-testid="stDataFrame"] [class*="header"],
[data-testid="stDataFrame"] span,
[data-testid="stDataFrame"] div {
    color: var(--tekst-donker) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}

/* Header rij donkerblauw en vet */
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"] {
    background-color: #e8eef6 !important;
    font-weight: 700 !important;
    color: var(--blauw) !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Afwisselende rijkleuren */
[data-testid="stDataFrame"] tr:nth-child(even) td {
    background-color: #f5f8fc !important;
}

/* === SELECTBOX & INPUT === */
[data-testid="stSelectbox"] > div > div {
    border-radius: 10px !important;
    border-color: var(--grijs-mid) !important;
    font-family: 'DM Sans', sans-serif;
    background: var(--wit) !important;
    box-shadow: 0 1px 4px rgba(13,31,53,0.06) !important;
}

[data-testid="stTextInput"] input {
    border-radius: 10px !important;
    border-color: var(--grijs-mid) !important;
    font-family: 'DM Sans', sans-serif;
    box-shadow: 0 1px 4px rgba(13,31,53,0.06) !important;
}

/* === BUTTONS === */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--oranje) 0%, var(--oranje-licht) 100%);
    color: var(--wit);
    border: none;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 13px;
    padding: 10px 24px;
    box-shadow: 0 4px 16px rgba(244,124,32,0.25);
    transition: all 0.2s ease;
    letter-spacing: 0.5px;
}

[data-testid="stButton"] > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(244,124,32,0.35);
}

[data-testid="stButton"] > button:active {
    transform: translateY(0px);
}

/* === ALERTS === */
[data-testid="stAlert"] {
    border-radius: 12px;
    font-family: 'DM Sans', sans-serif;
    border: none;
    font-size: 14px;
}

/* === DIVIDER === */
hr {
    border: none !important;
    border-top: 1px solid var(--grijs-mid) !important;
    margin: 2rem 0 !important;
}

/* === CARDS === */
.card {
    background: var(--wit);
    border-radius: 16px;
    padding: 28px;
    box-shadow: var(--card-shadow);
    margin-bottom: 1.5rem;
    border: 1px solid var(--grijs-mid);
    transition: box-shadow 0.2s ease;
}

.card:hover {
    box-shadow: var(--card-shadow-hover);
}

.card-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: var(--tekst-grijs);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--grijs-mid);
}

/* === PODIUM === */
.rank-1 { border-left: 4px solid #F59E0B; }
.rank-2 { border-left: 4px solid #94A3B8; }
.rank-3 { border-left: 4px solid #B45309; }

/* === CAPTION / KLEINE TEKST === */
[data-testid="stCaptionContainer"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: var(--tekst-grijs);
}

/* === SPINNER === */
[data-testid="stSpinner"] { color: var(--oranje) !important; }

/* === KOERS BADGE === */
.koers-badge {
    display: inline-block;
    background: var(--blauw);
    color: var(--wit);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.5px;
    margin: 2px;
}

.oranje-badge {
    background: var(--oranje);
}

/* === FADE-IN ANIMATIE === */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.stApp > div:first-child {
    animation: fadeInUp 0.4s ease forwards;
}

/* === DROPDOWN TEKST ALTIJD DONKER === */
[data-testid="stSelectbox"] > div > div,
[data-testid="stSelectbox"] > div > div * {
    color: var(--tekst-donker) !important;
    font-family: 'DM Sans', sans-serif;
}

/* Dropdown opties in lijst */
[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="listbox"] li,
[role="option"] {
    color: var(--tekst-donker) !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px !important;
}

/* Input labels */
[data-testid="stSelectbox"] label,
[data-testid="stTextInput"] label {
    color: var(--tekst-donker) !important;
    font-weight: 600;
    font-size: 14px !important;
}

/* === MOBIEL === */
@media (max-width: 768px) {
    /* Nav */
    .nav-header {
        padding: 0 16px;
        height: 52px;
    }
    .nav-logo { font-size: 18px; letter-spacing: 1.5px; }
    .nav-season { display: none; }

    /* Titels */
    h1 { font-size: 1.7rem !important; }
    h2, h3 { font-size: 1.1rem !important; }

    /* Tabs kleiner en scrollbaar */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
        padding: 4px;
        gap: 2px;
        scrollbar-width: none;
        -ms-overflow-style: none;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        font-size: 11px;
        padding: 7px 10px;
        white-space: nowrap;
        flex-shrink: 0;
    }

    /* Metrics op mobiel */
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; }
    [data-testid="stMetric"] { padding: 16px !important; }

    /* Dropdowns groter voor touch */
    [data-testid="stSelectbox"] > div > div {
        min-height: 44px !important;
        font-size: 15px !important;
        color: var(--tekst-donker) !important;
    }

    [data-testid="stSelectbox"] > div > div *,
    [role="option"],
    [data-baseweb="menu"] li {
        color: var(--tekst-donker) !important;
        font-size: 15px !important;
    }

    /* Buttons makkelijker klikbaar op touch */
    [data-testid="stButton"] > button {
        min-height: 44px;
        width: 100%;
        font-size: 14px;
    }

    /* Input velden groter */
    [data-testid="stTextInput"] input {
        min-height: 44px !important;
        font-size: 15px !important;
        color: var(--tekst-donker) !important;
    }

    /* Minder zijmarges op mobiel */
    [data-testid="stMainBlockContainer"] {
        padding-left: 12px !important;
        padding-right: 12px !important;
    }

    /* Dataframe op mobiel */
    [data-testid="stDataFrame"] {
        font-size: 12px;
    }

    /* Kolommen op mobiel onder elkaar */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- DATABASE CONFIGURATIE & VERBINDING ---
import os, json

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")

# Credentials laden: via environment variable (Railway) of lokaal JSON bestand
google_creds_env = os.environ.get("GOOGLE_CREDENTIALS")
if google_creds_env:
    creds_dict = json.loads(google_creds_env)
    credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
else:
    credentials = Credentials.from_service_account_file("google_keys.json", scopes=scopes)

gc = gspread.authorize(credentials)

# 3. Open de sheet
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1i8UB1igCk8cSCneTeQEGkxO0XFsuhSP2u4BLZfwHllM/edit"
sh = gc.open_by_url(SPREADSHEET_URL)

# 4. Hulpfunctie om data te lezen met CACHING (tegen de 429 error)
@st.cache_data(ttl=60) # Onthoud de data voor 60 seconden
def read_sheet(worksheet_name):
    try:
        # Een kleine random pauze helpt om niet tegelijk met andere verzoeken binnen te komen
        time.sleep(random.uniform(0.5, 1.5)) 
        worksheet = sh.worksheet(worksheet_name)
        data = worksheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        if "429" in str(e):
            st.error("Google limiet bereikt. Wacht 10 seconden en ververs de pagina.")
        else:
            st.error(f"Fout bij laden van {worksheet_name}: {e}")
        return pd.DataFrame()


def get_koersen_volgorde():
    try:
        # Gebruik de nieuwe hulpfunctie om de koersen op te halen
        df_k = read_sheet("koersen") 
        if not df_k.empty:
            df_k.columns = [c.strip() for c in df_k.columns]
            return df_k['koers_naam'].tolist()
        return []
    except Exception as e:
        return []

PUNTEN_SCHEMA = {
    1:100, 2:90, 3:80, 4:70, 5:64, 6:60, 7:56, 8:52, 9:48, 10:44,
    11:40, 12:36, 13:32, 14:28, 15:24, 16:20, 17:16, 18:12, 19:8, 20:4
}

# --- CONFIGURATIE DEADLINES 2026 ---
KOERS_DATA = {
    "Omloop Het Nieuwsblad": "2026-02-28 11:00",
    "Kuurne Brussel Kuurne": "2026-03-01 11:00",
    "Strade Bianche": "2026-03-07 11:00",
    "Milano Sanremo": "2026-03-21 10:00",
    "Classic Brugge De Panne": "2026-03-25 12:00",
    "E3 Harelbeke": "2026-03-27 12:00",
    "Gent Wevelgem": "2026-03-29 10:00",
    "Dwars Door Vlaanderen": "2026-04-01 12:00",
    "Ronde Van Vlaanderen": "2026-04-05 10:00",
    "Scheldeprijs": "2026-04-08 12:00",
    "Paris Roubaix": "2026-04-12 11:00",
    "Brabantse Pijl": "2026-04-15 12:00",
    "Amstel Gold Race": "2026-04-19 10:00",
    "La Fleche Wallone": "2026-04-22 11:00",
    "Liege Bastogne Liege": "2026-04-26 10:00"
}


# --- SCRAPER AANGEPAST VOOR FINISHERS + DNF, OTL, DSQ (EXCL. DNS) ---
def scrape_en_save(koers_naam, url):
    try:
        from procyclingstats import Stage
        # Haal het relatieve pad op uit de volledige URL
        relatief_pad = url.replace("https://www.procyclingstats.com/", "").strip("/")
        time.sleep(random.uniform(2, 4))
        stage = Stage(relatief_pad)
        resultaten = stage.results()
        if not resultaten:
            return False, "Geen resultaten gevonden via procyclingstats package."

        # 1. Haal huidige uitslagen op om te filteren
        existing_df = read_sheet("uitslagen")
        standard_cols = ['koers_naam', 'rank', 'rider', 'team']
        if not existing_df.empty:
            existing_df.columns = [str(c).strip().lower() for c in existing_df.columns]
            other_races_df = existing_df[existing_df['koers_naam'] != koers_naam].copy()
        else:
            other_races_df = pd.DataFrame(columns=standard_cols)

        # 2. Verwerk de resultaten
        toegestane_statussen = ["DNF", "OTL", "DSQ", "DNS"]
        temp_data = []
        for r in resultaten:
            # Rank kan in verschillende velden zitten afhankelijk van de package versie
            rank = str(r.get('rank', r.get('status', r.get('result', '')))).upper().strip()
            rider_raw = r.get('rider_name', '').strip()
            rider = ' '.join(w.capitalize() for w in rider_raw.split())
            team = r.get('team_name', '').strip()
            is_getal = rank.isdigit()
            is_uitvaller = rank in toegestane_statussen
            # Voeg toe als gefinisht, uitgevallen, OF als er een team bekend is (vangt edge cases op)
            if rider and (is_getal or is_uitvaller):
                temp_data.append({
                    "koers_naam": koers_naam,
                    "rank": rank,
                    "rider": rider,
                    "team": team
                })
            elif rider and team and not is_getal:
                # Vangnet: renner heeft geen getal als rank maar wel een team -> DNF
                temp_data.append({
                    "koers_naam": koers_naam,
                    "rank": "DNF",
                    "rider": rider,
                    "team": team
                })

        if not temp_data:
            return False, "Geen renners verwerkt uit de resultaten."

        new_scraped_df = pd.DataFrame(temp_data)
        final_df = pd.concat([other_races_df, new_scraped_df], ignore_index=True)
        final_df = final_df[standard_cols]

        ws_u = sh.worksheet("uitslagen")
        ws_u.clear()
        ws_u.update([standard_cols] + final_df.values.tolist())
        st.cache_data.clear()

        return True, f"Succes! {len(temp_data)} renners verwerkt (incl. DNF/OTL/DSQ)."
    except Exception as e:
        return False, f"Fout: {str(e)}"

# --- STARTLIJST SCRAPER ---
def scrape_startlijst_en_save(koers_naam, url):
    try:
        from procyclingstats import RaceStartlist
        # Bouw de startlist URL
        startlist_url = url.replace('/result', '/startlist').rstrip('/')
        if not startlist_url.endswith('/startlist'):
            startlist_url = startlist_url + '/startlist'
        relatief_pad = startlist_url.replace("https://www.procyclingstats.com/", "").strip("/")
        time.sleep(random.uniform(2, 4))
        startlist = RaceStartlist(relatief_pad)
        renners = startlist.startlist()
        if not renners:
            return False, "Geen startlijst gevonden via procyclingstats package."

        # 1. Haal huidige startlijsten op om te filteren
        standard_cols = ['koers_naam', 'startnummer', 'rider', 'team']
        try:
            existing_df = read_sheet("startlijsten")
            if not existing_df.empty:
                existing_df.columns = [str(c).strip().lower() for c in existing_df.columns]
                other_races_df = existing_df[existing_df['koers_naam'] != koers_naam].copy()
            else:
                other_races_df = pd.DataFrame(columns=standard_cols)
        except:
            other_races_df = pd.DataFrame(columns=standard_cols)

        # 2. Verwerk de startlijst
        temp_data = []
        for r in renners:
            rider_raw = r.get('rider_name', '').strip()
            rider = ' '.join(w.capitalize() for w in rider_raw.split())
            team = r.get('team_name', '').strip()
            startnummer = str(r.get('number', r.get('bib', r.get('rank', '')))).strip()
            if rider:
                temp_data.append({
                    "koers_naam": koers_naam,
                    "startnummer": startnummer,
                    "rider": rider,
                    "team": team
                })

        if not temp_data:
            return False, "Geen renners gevonden in de startlijst."

        new_scraped_df = pd.DataFrame(temp_data)
        final_df = pd.concat([other_races_df, new_scraped_df], ignore_index=True)
        final_df = final_df[standard_cols]

        ws_sl = sh.worksheet("startlijsten")
        ws_sl.clear()
        ws_sl.update([standard_cols] + final_df.values.tolist())
        st.cache_data.clear()

        return True, f"Succes! {len(temp_data)} renners in startlijst verwerkt."
    except Exception as e:
        return False, f"Fout: {str(e)}"

# --- REKEN LOGICA (AANGEPAST VOOR TEAM PUNTEN BIJ DNF/OTL/DSQ) ---
@st.cache_data(ttl=60)
def bereken_volledige_score(speler_naam, koers_naam, u_all, k_all, mijn_renners):
    # Lokale kopieën maken om de originele data niet te beschadigen maar wel kolommen te cleansen
    u_df_local = u_all.copy()
    u_df_local.columns = [str(c).strip().lower() for c in u_df_local.columns]
    
    k_df_local = k_all.copy()
    k_df_local.columns = [str(c).strip().lower() for c in k_df_local.columns]

    # Filter uitslagen voor deze koers
    u_df = u_df_local[u_df_local['koers_naam'] == koers_naam]
    if u_df.empty: return 0, []

    def ultra_clean(tekst):
        if not tekst: return ""
        tekst = "".join(c for c in unicodedata.normalize('NFD', str(tekst)) if unicodedata.category(c) != 'Mn')
        tekst = tekst.replace('ø', 'o').replace('Ø', 'O').replace('æ', 'ae').replace('Æ', 'AE')
        return "".join(filter(str.isalnum, tekst)).upper()

    # We bouwen de u_dict op voor ALLE renners in de uitslag (dus ook DNF/OTL/DSQ)
    u_dict = {}
    for _, r in u_df.iterrows():
        clean_name = ultra_clean(r['rider'])
        # Rank bewaren (kan getal of tekst zijn)
        u_dict[clean_name] = {
            'rank': r['rank'], 
            'team': str(r['team']).upper().strip(), 
            'origineel': r['rider']
        }
    
    # Captains ophalen
    caps = {}
    if not k_df_local.empty and 'speler_naam' in k_df_local.columns:
        keuze = k_df_local[(k_df_local['speler_naam'] == speler_naam) & (k_df_local['koers_naam'] == koers_naam)]
        if not keuze.empty:
            for i, factor in zip([1, 2, 3], [3.0, 2.5, 2.0]):
                col_name = f'captain_{i}'
                if col_name in keuze.columns:
                    c_name = keuze.iloc[0][col_name]
                    if pd.notna(c_name) and str(c_name).strip() != "":
                        caps[ultra_clean(c_name)] = factor

    details, totaal = [], 0
    pcs_clean_namen = list(u_dict.keys())

    # Team winnaars bepalen (Top 3 teams)
    def get_team_by_rank(rk):
        row = u_df[u_df['rank'].astype(str) == str(rk)]
        return str(row['team'].values[0]).upper().strip() if not row.empty else None

    t1, t2, t3 = get_team_by_rank(1), get_team_by_rank(2), get_team_by_rank(3)

    for renner_naam_excel in mijn_renners:
        excel_clean = ultra_clean(renner_naam_excel)
        match_res = process.extractOne(excel_clean, pcs_clean_namen, scorer=fuzz.token_set_ratio)
        
        if match_res and match_res[1] > 75:
            best_match_clean = match_res[0]
            data = u_dict[best_match_clean]
            rank, rt = data['rank'], data['team']
            
            # Captain factor bepalen
            f = caps.get(excel_clean, 1.0)
            if f == 1.0: f = caps.get(best_match_clean, 1.0)
            
            # Punten voor eigen klassering (alleen als rank een getal is)
            punten_plek = 0
            try:
                rank_int = int(rank)
                if rank_int <= 20:
                    punten_plek = PUNTEN_SCHEMA.get(rank_int, 0) * f
            except ValueError:
                rank_int = 999 # Voor DNF/OTL/DSQ
            
            # Team punten logica (werkt nu ook voor DNF, want rt is bekend)
            punten_team = 0
            if rt:
                if t1 and rt == t1 and rank != "1" and rank != 1: punten_team += 30
                if t2 and rt == t2 and rank != "2" and rank != 2: punten_team += 20
                if t3 and rt == t3 and rank != "3" and rank != 3: punten_team += 10
            
            subtotaal = punten_plek + punten_team
            totaal += subtotaal
            
            # Toevoegen aan details als er punten zijn gescoord of de renner in de uitslag staat
            if subtotaal > 0 or rank_int <= 50 or rank in ["DNF", "OTL", "DSQ"]:
                details.append({
                    "Renner": renner_naam_excel, 
                    "Punten": int(subtotaal), 
                    "Rank": rank, 
                    "Match": data['origineel']
                })
    
    return totaal, details

# --- MAIN APP NAVIGATIE ---

# Topnavigatie header
st.markdown("""
<div class="nav-container">
    <div class="nav-header">
        <div class="nav-logo">K1<span>x</span>Sam<span class="sep">|</span>Klassiekerspel</div>
        <div class="nav-season">🚴&nbsp;&nbsp;Seizoen 2026</div>
    </div>
</div>
""", unsafe_allow_html=True)

PAGINA_OPTIES = ["🏆 Klassement", "🏁 Uitslagen", "🚦 Startlijsten", "📊 Matrix", "🚌 Mijn Team", "©️ Captains", "⚙️ Beheer"]

tab_klas, tab_uitslag, tab_startlijst, tab_matrix, tab_team, tab_captains, tab_admin = st.tabs(PAGINA_OPTIES)

# Data inladen via Google Sheets
u_all = read_sheet("uitslagen")
if not u_all.empty:
    u_all.columns = [str(c).strip().lower() for c in u_all.columns]

s_all = read_sheet("speler_teams")
if not s_all.empty:
    s_all.columns = [str(c).strip().lower() for c in s_all.columns]

k_all = read_sheet("keuzes")
if k_all is None or k_all.empty:
    k_all = pd.DataFrame(columns=["speler_naam", "koers_naam", "captain_1", "captain_2", "captain_3"])
else:
    k_all.columns = [str(c).strip().lower() for c in k_all.columns]

koersen_volgorde = get_koersen_volgorde()

# =============================================
# 1. KLASSEMENT
# =============================================
with tab_klas:
    st.title("🏆 Klassementen")
    if u_all.empty or s_all.empty:
        st.info("Nog geen data beschikbaar. Zorg dat teams en uitslagen zijn geladen.")
    else:
        volgorde_csv = koersen_volgorde
        beschikbare_koersen = u_all['koers_naam'].unique()
        koersen_gehad = [k for k in volgorde_csv if k in beschikbare_koersen]
        voor_de_zekerheid = [k for k in beschikbare_koersen if k not in koersen_gehad]
        koersen_gehad += sorted(voor_de_zekerheid)

        if 'subpoule' not in s_all.columns: s_all['subpoule'] = ""
        history_data, scores = [], []
        
        with st.spinner('Klassement berekenen...'):
            for speler in sorted(s_all['speler_naam'].unique()):
                speler_rows = s_all[s_all['speler_naam'] == speler].copy()
                poule_val = speler_rows['subpoule'].iloc[0] if not speler_rows['subpoule'].empty else ""
                poule_lijst = [p.strip() for p in str(poule_val).split(",")] if poule_val else []
                
                cumulatief = 0
                for k in koersen_gehad:
                    koers_datum_str = KOERS_DATA[k].split(" ")[0]
                    k_dt = pd.to_datetime(koers_datum_str)

                    mask = (
                        (pd.to_datetime(speler_rows['vanaf_datum']) <= k_dt) & 
                        (
                            (speler_rows['tot_datum'].isna()) | 
                            (speler_rows['tot_datum'] == "") | 
                            (pd.to_datetime(speler_rows['tot_datum']) > k_dt)
                        )
                    )
                    
                    mr_voor_deze_koers = speler_rows[mask]['renner_naam'].tolist()
                    koers_score, _ = bereken_volledige_score(speler, k, u_all, k_all, mr_voor_deze_koers)
                    cumulatief += koers_score
                    
                    koers_idx = koersen_gehad.index(k) + 1
                    koers_label = f"{koers_idx:02d}. {k}"
                    history_data.append({"Koers": koers_label, "Speler": speler, "Punten": int(cumulatief)})
                
                scores.append({"Deelnemer": speler, "Totaal": int(cumulatief), "Poules": poule_lijst})

        df_scores = pd.DataFrame(scores)
        tab1, tab2, tab3, tab4 = st.tabs(["🌍 Algemeen", "🥇 Kamer 1", "🥈 Sammeke", "📈 Verloop"])

        # Bereken vorige stand (op één na laatste koers) voor pijltjes
        def bereken_vorige_stand(df_scores_huidig, history_data, koersen_gehad):
            if len(koersen_gehad) < 2:
                return {}
            # Puntentotaal tot en met één koers terug
            vorige_koers_label = f"{(len(koersen_gehad)-1):02d}. {koersen_gehad[-2]}"
            vorige = {}
            for entry in history_data:
                if entry['Koers'] == vorige_koers_label:
                    vorige[entry['Speler']] = entry['Punten']
            if not vorige:
                return {}
            # Rangschik op vorige stand
            gesorteerd = sorted(vorige.items(), key=lambda x: x[1], reverse=True)
            return {speler: i+1 for i, (speler, _) in enumerate(gesorteerd)}

        def maak_trend_kolom(df_weergave, vorige_ranks):
            rank_lookup = {speler: i + 1 for i, speler in enumerate(df_weergave['Deelnemer'])}
            trends = []
            for i, row in df_weergave.iterrows():
                speler = row['Deelnemer']
                huidige_rank = rank_lookup[speler]
                if speler in vorige_ranks:
                    oud = vorige_ranks[speler]
                    if huidige_rank < oud:
                        trends.append("🟢 ▲")
                    elif huidige_rank > oud:
                        trends.append("🔴 ▼")
                    else:
                        trends.append("🔵 —")
                else:
                    trends.append("")
            return trends

        vorige_ranks = bereken_vorige_stand(df_scores, history_data, koersen_gehad)

        # Functie voor compacte weergave zonder lege rijen, met trend kolom
        def display_compact_df(df):
            n_rijen = len(df)
            # Exacte hoogte: header 38px + elke rij 35px
            calc_height = 38 + (n_rijen * 35)

            df_show = df[['Deelnemer', 'Totaal']].copy().reset_index(drop=True)
            df_show.index += 1

            # Voeg trend kolom toe als er vorige stands zijn
            if vorige_ranks:
                df_show.insert(0, '↕', maak_trend_kolom(df_show, vorige_ranks))

            st.dataframe(
                df_show,
                column_config={
                    "↕": st.column_config.TextColumn("↕", width=50),
                    "Deelnemer": st.column_config.TextColumn("Deelnemer", width="medium"),
                    "Totaal": st.column_config.NumberColumn("Totaal", width="small", format="%d"),
                },
                hide_index=False,
                use_container_width=False,
                height=calc_height
            )

        with tab1:
            st.subheader("Algemeen Klassement")
            df_alg = df_scores.sort_values('Totaal', ascending=False).reset_index(drop=True)
            display_compact_df(df_alg)

        def toon_poule_tabel(poule_naam):
            mask = df_scores['Poules'].apply(lambda x: poule_naam in x)
            df_p = df_scores[mask].sort_values('Totaal', ascending=False).reset_index(drop=True)
            if not df_p.empty:
                display_compact_df(df_p)
            else:
                st.info(f"Geen spelers gevonden voor {poule_naam}.")

        with tab2: toon_poule_tabel("Kamer 1")
        with tab3: toon_poule_tabel("Sammeke")
        with tab4:
            if history_data:
                # Maak pivot table
                df_pivot = pd.DataFrame(history_data).pivot(index='Koers', columns='Speler', values='Punten').sort_index()
                
                # --- SORTEER LEGENDA: Hoogste score eerst ---
                # Pak de laatste rij (eindstand) en sorteer de kolomnamen daarop
                eindstand = df_pivot.iloc[-1].sort_values(ascending=False)
                df_pivot = df_pivot[eindstand.index]
                
                st.line_chart(df_pivot)

# =============================================
# 2. UITSLAG PER KOERS
# =============================================
with tab_uitslag:
    st.title("🏁 Koersuitslag & Puntenverdeling")
    if not u_all.empty:
        volgorde = koersen_volgorde
        koers_opties = [k for k in volgorde if k in u_all['koers_naam'].unique()]
        koers = st.selectbox("Selecteer een koers:", koers_opties if koers_opties else u_all['koers_naam'].unique())
        
        st.subheader(f"Officiële Uitslag: {koers}")
        top_uitslag = u_all[u_all['koers_naam'] == koers].copy()
        top_uitslag['sort_rank'] = pd.to_numeric(top_uitslag['rank'], errors='coerce').fillna(999)
        
        st.dataframe(
            top_uitslag.sort_values('sort_rank').head(50)[['rank', 'rider', 'team']], 
            hide_index=True, 
            use_container_width=True
        )
        
        st.divider()
        st.subheader("Punten per Deelnemer")
        
        # Bepaal datum van de geselecteerde koers
        koers_datum_str = KOERS_DATA[koers].split(" ")[0]
        k_dt = pd.to_datetime(koers_datum_str)
        
        data = []
        for speler in sorted(s_all['speler_naam'].unique()):
            speler_rows = s_all[s_all['speler_naam'] == speler].copy()
            
            # Filter actieve renners voor deze koersdatum
            mask = (
                (pd.to_datetime(speler_rows['vanaf_datum']) <= k_dt) & 
                (
                    (speler_rows['tot_datum'].isna()) | 
                    (speler_rows['tot_datum'] == "") | 
                    (pd.to_datetime(speler_rows['tot_datum']) > k_dt)
                )
            )
            actuele_renners = speler_rows[mask]['renner_naam'].tolist()
            
            # Bereken score
            t, det = bereken_volledige_score(speler, koers, u_all, k_all, actuele_renners)
            
            # Veilige sortering (DNF/OTL onderaan)
            det_gesorteerd = sorted(
                det, 
                key=lambda x: int(x['Rank']) if str(x['Rank']).isdigit() else 999
            )
            
            # Maak de resultaat string
            ren_str = ", ".join([
                f"{d['Renner']} (P{d['Rank']}: {int(d['Punten'])})" 
                for d in det_gesorteerd
            ])
            
            data.append({
                "Deelnemer": speler, 
                "Punten": int(t), 
                "Scorende Renners": ren_str
            })
        
        # Tabel weergeven met verbeterde leesbaarheid
        if data:
            df_koers_punten = pd.DataFrame(data).sort_values("Punten", ascending=False).reset_index(drop=True)
            df_koers_punten.index += 1
            
            n_punten = len(df_koers_punten)
            punten_height = 38 + (n_punten * 38)
            st.dataframe(
                df_koers_punten,
                column_config={
                    "Deelnemer": st.column_config.TextColumn("Deelnemer", width="medium"),
                    "Punten": st.column_config.NumberColumn("Punten", width="small", format="%d"),
                    "Scorende Renners": st.column_config.TextColumn(
                        "Scorende Renners",
                        width=2500,
                        help="Scroll naar rechts om alle renners te zien"
                    ),
                },
                hide_index=False,
                use_container_width=True,
                height=punten_height
            )
        else:
            st.info("Geen gegevens beschikbaar voor deze koers.")

# =============================================
# 2b. STARTLIJSTEN
# =============================================
with tab_startlijst:
    st.title("🚦 Startlijsten")

    sl_all = read_sheet("startlijsten")

    if sl_all.empty:
        st.info("Nog geen startlijsten beschikbaar. Scrape ze eerst via de Beheer pagina.")
    else:
        sl_all.columns = [str(c).strip().lower() for c in sl_all.columns]

        # Koers dropdown - gebruik volgorde uit koersen sheet
        volgorde_sl = koersen_volgorde
        beschikbare_koersen_sl = sl_all['koers_naam'].unique().tolist()
        koersen_sl_gesorteerd = [k for k in volgorde_sl if k in beschikbare_koersen_sl]
        # Voeg koersen toe die niet in de volgorde staan (vangnet)
        koersen_sl_gesorteerd += [k for k in beschikbare_koersen_sl if k not in koersen_sl_gesorteerd]

        if not koersen_sl_gesorteerd:
            st.info("Geen koersen gevonden in de startlijsten database.")
        else:
            gekozen_koers = st.selectbox("Selecteer een koers:", koersen_sl_gesorteerd, key="sl_koers_view")

            koers_df = sl_all[sl_all['koers_naam'] == gekozen_koers].copy()

            if koers_df.empty:
                st.info(f"Geen startlijst beschikbaar voor {gekozen_koers}.")
            else:
                # Groepeer per ploeg, behoud volgorde zoals op PCS (= volgorde in database)
                ploegen = koers_df['team'].unique().tolist()

                st.markdown(f"**{len(koers_df)} renners verdeeld over {len(ploegen)} ploegen**")
                st.divider()

                # Toon per ploeg in kolommen (2 kolommen naast elkaar)
                cols = st.columns(2)
                for i, ploeg in enumerate(ploegen):
                    ploeg_df = koers_df[koers_df['team'] == ploeg].reset_index(drop=True)
                    with cols[i % 2]:
                        # Bouw renners HTML apart op
                        renners_html = ""
                        for _, row in ploeg_df.iterrows():
                            nr = row['startnummer']
                            naam = row['rider']
                            renners_html += (
                                f'<div style="display:flex;align-items:center;padding:5px 0;'
                                f'font-family:Inter,sans-serif;font-size:13px;color:#1a2e4a;'
                                f'border-bottom:1px solid #f4f6f9;">'
                                f'<span style="color:#94a3b8;font-size:11px;width:28px;flex-shrink:0;">#{nr}</span>'
                                f'<span>{naam}</span></div>'
                            )
                        st.markdown(
                            f'<div style="background:white;border-radius:10px;padding:16px;'
                            f'margin-bottom:16px;border-left:4px solid #f47c20;'
                            f'box-shadow:0 2px 8px rgba(26,46,74,0.08);">'
                            f'<div style="font-family:Barlow Condensed,sans-serif;font-size:15px;'
                            f'font-weight:700;color:#1a2e4a;text-transform:uppercase;'
                            f'letter-spacing:0.5px;margin-bottom:10px;padding-bottom:8px;'
                            f'border-bottom:1px solid #e2e8f0;">{ploeg}</div>'
                            f'{renners_html}</div>',
                            unsafe_allow_html=True
                        )

# =============================================
# 3. RENNER-KOERS PUNTEN MATRIX
# =============================================
with tab_matrix:
    st.title("📊 Punten Matrix")
    if not s_all.empty and not u_all.empty:
        speler = st.selectbox("Selecteer Deelnemer", sorted(s_all['speler_naam'].unique()))
        
        volgorde = koersen_volgorde
        beschikbare_koersen = u_all['koers_naam'].unique()
        koersen = [k for k in volgorde if k in beschikbare_koersen]
        
        # Haal ALLE renners op die de speler ooit heeft gehad
        mijn_renners_df = s_all[s_all['speler_naam'] == speler]
        mijn_renners = sorted(mijn_renners_df['renner_naam'].unique().tolist())
        
        matrix = []
        with st.spinner('Matrix opbouwen...'):
            for r in mijn_renners:
                # Haal de meest recente info van deze specifieke renner op voor deze speler
                r_info = mijn_renners_df[mijn_renners_df['renner_naam'] == r].iloc[0]
                
                v_dat = pd.to_datetime(r_info['vanaf_datum'])
                t_dat = pd.to_datetime(r_info['tot_datum']) if pd.notna(r_info['tot_datum']) and r_info['tot_datum'] != "" else pd.to_datetime("2099-01-01")

                rij = {"Renner": r}
                for k in koersen:
                    # Zoek datum op in KOERS_DATA (met fallback voor veiligheid)
                    k_datum_str = KOERS_DATA.get(k, "2026-01-01 00:00").split(" ")[0]
                    k_dt = pd.to_datetime(k_datum_str)
                    
                    # Check of renner actief was tijdens deze koers
                    is_actief = (v_dat <= k_dt) and (t_dat > k_dt)
                    
                    if is_actief:
                        score, det = bereken_volledige_score(speler, k, u_all, k_all, [r])
                        
                        # LOGICA VOOR WEERGAVE:
                        if det:
                            rank_waarde = str(det[0]['Rank'])
                            if score > 0:
                                # Toon de score als er punten zijn (ook als het een DNF met teampunten is)
                                rij[k] = int(score)
                            elif rank_waarde in ["DNF", "OTL", "DSQ"]:
                                # Toon de status als er 0 punten zijn maar wel een status
                                rij[k] = rank_waarde
                            else:
                                # Gewoon een nul als hij gefinisht is zonder punten
                                rij[k] = 0
                        else:
                            # Renner staat niet in de uitslag van deze koers
                            rij[k] = 0
                    else:
                        rij[k] = "-" # Niet in team tijdens deze koers
                
                # Totaal berekenen (negeer tekst zoals DNF en streepjes)
                rij["Totaal"] = sum(v for v in rij.values() if isinstance(v, (int, float)))
                matrix.append(rij)
        
        df_matrix = pd.DataFrame(matrix).set_index("Renner")
        
        # Styling: Kleur de cellen met punten groen, maak DNF/OTL/DSQ grijs
        def style_matrix(v):
            if isinstance(v, (int, float)) and v > 0:
                return 'color: #0d1f35; background-color: #c8f0d4; font-weight: 700; font-size: 13px;'
            elif v in ["DNF", "OTL", "DSQ"]:
                return 'color: #7f1d1d; background-color: #fecaca; font-weight: 600; font-size: 12px;'
            elif v == "-":
                return 'color: #0d1f35; font-size: 13px;'
            elif isinstance(v, (int, float)) and v == 0:
                return 'color: #0d1f35; font-size: 13px;'
            else:
                return 'color: #0d1f35; font-size: 13px; font-weight: 600;'

        n_matrix_rows = len(df_matrix)
        matrix_height = 38 + (n_matrix_rows * 38)
        st.dataframe(
            df_matrix.style.applymap(style_matrix),
            use_container_width=True,
            height=matrix_height
        )

# =============================================
# 4. MIJN TEAM
# =============================================
with tab_team:
    st.title("🚌 Mijn Team Overzicht")
    if not s_all.empty:
        speler = st.selectbox("Naam:", sorted(s_all['speler_naam'].unique()))
        
        # Haal de renners op
        mr = s_all[s_all['speler_naam'] == speler]['renner_naam'].tolist()
        
        r_data = []
        with st.spinner('Punten berekenen...'):
            for r in mr:
                # Bereken de totale score
                score = sum(int(bereken_volledige_score(speler, k, u_all, k_all, [r])[0]) for k in u_all['koers_naam'].unique())
                r_data.append({"Renner": r, "Totaal Punten": score})
        
        # Maak DataFrame en sorteer
        df_mijn_team = pd.DataFrame(r_data).sort_values("Totaal Punten", ascending=False)

        # Weergave met aangepaste kolombreedte en tabelhoogte
        n_renners = len(df_mijn_team)
        team_height = 38 + (n_renners * 35)
        st.dataframe(
            df_mijn_team,
            column_config={
                "Renner": st.column_config.TextColumn("Renner", width="medium"),
                "Totaal Punten": st.column_config.NumberColumn(
                    "Totaal Punten",
                    width="medium",
                    format="%d"
                ),
            },
            hide_index=True,
            use_container_width=False,
            height=team_height
        )
        

# =============================================
# 5. CAPTAINS KIEZEN
# =============================================
with tab_captains:
    st.title("©️ Captains Beheer")

    if not s_all.empty:
        naam = st.selectbox("Wie ben je?", sorted(s_all['speler_naam'].unique()), key="select_speler")
        pin = st.text_input("Voer je pincode in:", type="password")
        
        if pin:
            correct_pin = str(s_all[s_all['speler_naam'] == naam]['pincode'].iloc[0])
            if pin == correct_pin:
                
                # --- SECTIE 1: CAPTAINS INSTELLEN ---
                st.subheader("📝 Captains Instellen")
                koers_keuze = st.selectbox("Voor welke koers?", list(KOERS_DATA.keys()))
                
                # Check of koers al gestart is
                deadline_str = KOERS_DATA[koers_keuze]
                deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M")
                is_gestart = datetime.now() >= deadline_dt

                huidige_keuze = k_all[(k_all['speler_naam'] == naam) & (k_all['koers_naam'] == koers_keuze)]
                if not huidige_keuze.empty:
                    st.info(f"Huidige keuze voor {koers_keuze}: 1. {huidige_keuze.iloc[0]['captain_1']}, 2. {huidige_keuze.iloc[0]['captain_2']}, 3. {huidige_keuze.iloc[0]['captain_3']}")

                if is_gestart:
                    st.warning(f"⚠️ De deadline voor {koers_keuze} is verstreken ({deadline_str}). Je kunt je captains niet meer wijzigen.")
                else:
                    mr = sorted(s_all[s_all['speler_naam'] == naam]['renner_naam'].tolist())

                    # Haal startlijst op voor deze koers
                    sl_data = read_sheet("startlijsten")
                    if not sl_data.empty:
                        sl_data.columns = [str(c).strip().lower() for c in sl_data.columns]
                        startlijst_namen = sl_data[sl_data['koers_naam'] == koers_keuze]['rider'].str.lower().tolist()
                    else:
                        startlijst_namen = []

                    def verrijk_naam(renner):
                        if startlijst_namen and renner.lower() in startlijst_namen:
                            return f"✅ {renner}"
                        elif startlijst_namen:
                            return f"○ {renner}"
                        return renner

                    # Sorteer: renners op startlijst eerst, daarna de rest
                    mr_op_startlijst = [verrijk_naam(r) for r in mr if startlijst_namen and r.lower() in startlijst_namen]
                    mr_niet_op_startlijst = [verrijk_naam(r) for r in mr if not startlijst_namen or r.lower() not in startlijst_namen]
                    mr_verrijkt = mr_op_startlijst + mr_niet_op_startlijst

                    if startlijst_namen:
                        st.caption("✅ = staat op startlijst   ○ = niet op startlijst")

                    c1_verrijkt = st.selectbox("Kies Captain 1 (3.0x)", mr_verrijkt)
                    c2_verrijkt = st.selectbox("Kies Captain 2 (2.5x)", [r for r in mr_verrijkt if r != c1_verrijkt])
                    c3_verrijkt = st.selectbox("Kies Captain 3 (2.0x)", [r for r in mr_verrijkt if r not in [c1_verrijkt, c2_verrijkt]])

                    # Strip het prefix weer voor opslaan
                    def strip_prefix(naam):
                        return naam.replace("✅ ", "").replace("○ ", "")

                    c1 = strip_prefix(c1_verrijkt)
                    c2 = strip_prefix(c2_verrijkt)
                    c3 = strip_prefix(c3_verrijkt)
                    
                    if st.button("Captains Opslaan"):
                        new_entry = pd.DataFrame([{
                            "speler_naam": naam, 
                            "koers_naam": koers_keuze, 
                            "captain_1": c1, 
                            "captain_2": c2, 
                            "captain_3": c3
                        }])
                        
                        k_all_clean = k_all.copy()
                        if not k_all_clean.empty:
                            k_all_clean.columns = [str(c).strip().lower() for c in k_all_clean.columns]
                            masker = (k_all_clean['speler_naam'] == naam) & (k_all_clean['koers_naam'] == koers_keuze)
                            andere_keuzes = k_all_clean[~masker].copy()
                            final_k = pd.concat([andere_keuzes, new_entry], ignore_index=True)
                        else:
                            final_k = new_entry

                        final_k = final_k.fillna("")

                        try:
                            ws_k = sh.worksheet("keuzes")
                            ws_k.clear()
                            headers = ["speler_naam", "koers_naam", "captain_1", "captain_2", "captain_3"]
                            for h in headers:
                                if h not in final_k.columns:
                                    final_k[h] = ""
                            final_k = final_k[headers]
                            ws_k.update([headers] + final_k.values.tolist())
                            
                            st.success(f"Captains voor {koers_keuze} succesvol opgeslagen!")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fout bij opslaan: {e}")

                st.divider()

                # --- SECTIE 2: OVERZICHT ---
                st.subheader("🕵️ Overzicht Captains")
                tab_mijn, tab_alle = st.tabs(["📅 Mijn Overzicht", "🌍 Alle Deelnemers"])
                
                with tab_mijn:
                    st.write("Jouw keuzes voor alle koersen:")
                    mijn_tabel = k_all[k_all['speler_naam'] == naam].copy()
                    if not mijn_tabel.empty:
                        st.dataframe(mijn_tabel[['koers_naam', 'captain_1', 'captain_2', 'captain_3']], hide_index=True, use_container_width=True)
                    else:
                        st.info("Je hebt nog geen captains ingesteld.")

                with tab_alle:
                    bekijk_koers = st.selectbox("Bekijk captains voor:", list(KOERS_DATA.keys()), key="view_others")
                    nu = datetime.now()
                    start_tijd = datetime.strptime(KOERS_DATA[bekijk_koers], "%Y-%m-%d %H:%M")

                    if nu < start_tijd:
                        st.info(f"🤫 De captains voor **{bekijk_koers}** blijven geheim tot de start om {start_tijd.strftime('%H:%M')} uur.")
                    else:
                        st.write(f"🔓 De koers is gestart! Hier zijn de keuzes voor {bekijk_koers}:")
                        andere_keuzes = k_all[k_all['koers_naam'] == bekijk_koers].copy()
                        if not andere_keuzes.empty:
                            st.dataframe(andere_keuzes[['speler_naam', 'captain_1', 'captain_2', 'captain_3']], hide_index=True, use_container_width=True)
                        else:
                            st.info("Niemand heeft captains ingevuld voor deze koers.")
            else:
                st.error("Onjuiste pincode")

# =============================================
# 6. ADMIN
# =============================================
with tab_admin:
    st.title("⚙️ Admin Dashboard")
    
    # --- WACHTWOORD BEVEILIGING ---
    poging = st.text_input("Voer het admin-wachtwoord in:", type="password")
    
    if ADMIN_PASSWORD and poging == ADMIN_PASSWORD:
        st.success("Wachtwoord correct. Welkom beheerder.")
        
        # --- STATISTIEKEN SECTIE ---
        st.divider()
        st.subheader("📊 Database Statistieken")
        
        col_stat1, col_stat2 = st.columns(2)
        
        # Data ophalen voor statistieken
        df_uitslagen_check = read_sheet("uitslagen")
        df_teams_check = read_sheet("speler_teams")
        
        with col_stat1:
            if not df_uitslagen_check.empty:
                # Kolommen opschonen
                df_uitslagen_check.columns = [str(c).strip().lower() for c in df_uitslagen_check.columns]
                
                # Totaal aantal unieke koersen en totaal aantal renners
                totaal_uitslagen = len(df_uitslagen_check)
                st.metric("Totaal aantal renners in database", totaal_uitslagen)
                
                # Telling per koers
                koers_counts = df_uitslagen_check.groupby('koers_naam')['rider'].count().reset_index()
                koers_counts.columns = ['Koers', 'Aantal Renners']
                
                st.write("**Aantal renners per koers:**")
                st.dataframe(koers_counts.sort_values("Aantal Renners", ascending=False), 
                             use_container_width=True, 
                             hide_index=True)
            else:
                st.info("De uitslagen-database is nog leeg.")
            
        with col_stat2:
            if not df_teams_check.empty:
                # Kolommen opschonen
                df_teams_check.columns = [str(c).strip().lower() for c in df_teams_check.columns]
                
                # Tel renners per speler
                spelers_count = df_teams_check.groupby('speler_naam')['renner_naam'].count().reset_index()
                spelers_count.columns = ['Speler', 'Aantal Renners']
                
                st.write("**Renners per speler in database:**")
                st.dataframe(spelers_count.sort_values("Aantal Renners", ascending=False), 
                             use_container_width=True, 
                             hide_index=True)
            else:
                st.write("Geen spelersdata gevonden.")

        # Startlijsten statistieken - volle breedte eronder
        st.divider()
        df_startlijsten_check = read_sheet("startlijsten")
        if not df_startlijsten_check.empty:
            df_startlijsten_check.columns = [str(c).strip().lower() for c in df_startlijsten_check.columns]
            totaal_startlijsten = len(df_startlijsten_check)
            st.metric("Totaal aantal renners in startlijsten", totaal_startlijsten)
            sl_counts = df_startlijsten_check.groupby('koers_naam')['rider'].count().reset_index()
            sl_counts.columns = ['Koers', 'Aantal Renners op Startlijst']
            # Sorteer op chronologische volgorde uit de koersen sheet
            volgorde_admin = koersen_volgorde
            if volgorde_admin:
                sl_counts['volgorde'] = sl_counts['Koers'].apply(
                    lambda k: volgorde_admin.index(k) if k in volgorde_admin else 999
                )
                sl_counts = sl_counts.sort_values('volgorde').drop(columns='volgorde')
            st.write("**Renners per koers op startlijst:**")
            st.dataframe(sl_counts, use_container_width=True, hide_index=True)
        else:
            st.info("De startlijsten-database is nog leeg.")

        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Teams Inladen")
            ft = st.file_uploader("Upload teams.csv", type="csv")
            if ft and st.button("Sla Teams Op"):
                df = pd.read_csv(ft, sep=None, engine='python', encoding='utf-8-sig')
                ws_s = sh.worksheet("speler_teams")
                ws_s.clear()
                ws_s.update([df.columns.values.tolist()] + df.values.tolist())
                st.success("Teams opgeslagen!")
                st.rerun()

        with col2:
            st.subheader("🌐 Koersen Scrapen")
            
            # Haal de lijst met koersen op uit de sheet
            df_k = read_sheet("koersen")
            
            if not df_k.empty:
                df_k.columns = [str(c).strip().lower() for c in df_k.columns]
                koers_lijst = df_k['koers_naam'].tolist()
                
                # Optie 1: Individuele koers
                geselecteerde_koers = st.selectbox("Selecteer een specifieke koers:", ["---"] + koers_lijst)
                if st.button("Scrape geselecteerde koers") and geselecteerde_koers != "---":
                    rij = df_k[df_k['koers_naam'] == geselecteerde_koers].iloc[0]
                    ok, msg = scrape_en_save(rij['koers_naam'], rij['url'])
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
                
                st.write("---")
                
                # Optie 2: Alles tegelijk
                if st.button("Start Scraper voor ALLE koersen"):
                    status_placeholder = st.empty()
                    for index, r in df_k.iterrows():
                        k_naam = r['koers_naam']
                        k_url = r['url']
                        status_placeholder.info(f"Bezig met ({index+1}/{len(df_k)}): {k_naam}...")
                        ok, msg = scrape_en_save(k_naam, k_url)
                        st.write(f"{'✅' if ok else '❌'} {k_naam}")
                    
                    status_placeholder.success("Klaar!")
                    st.cache_data.clear()
            else:
                st.error("Geen koersen gevonden.")

        st.divider()

        # --- STARTLIJSTEN SCRAPER UI ---
        st.subheader("🚦 Startlijsten Scrapen")
        df_k2 = read_sheet("koersen")
        if not df_k2.empty:
            df_k2.columns = [str(c).strip().lower() for c in df_k2.columns]
            koers_lijst2 = df_k2['koers_naam'].tolist()

            geselecteerde_koers_sl = st.selectbox("Selecteer een koers voor startlijst:", ["---"] + koers_lijst2, key="sl_koers")
            if st.button("Scrape startlijst geselecteerde koers") and geselecteerde_koers_sl != "---":
                rij = df_k2[df_k2['koers_naam'] == geselecteerde_koers_sl].iloc[0]
                ok, msg = scrape_startlijst_en_save(rij['koers_naam'], rij['url'])
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

            st.write("---")

            if st.button("Scrape startlijsten voor ALLE koersen"):
                status_placeholder2 = st.empty()
                for index, r in df_k2.iterrows():
                    k_naam = r['koers_naam']
                    k_url = r['url']
                    status_placeholder2.info(f"Bezig met ({index+1}/{len(df_k2)}): {k_naam}...")
                    ok, msg = scrape_startlijst_en_save(k_naam, k_url)
                    st.write(f"{'✅' if ok else '❌'} {k_naam}: {msg}")
                status_placeholder2.success("Klaar!")
                st.cache_data.clear()
        else:
            st.error("Geen koersen gevonden.")

        st.divider()
        
        st.subheader("🗑️ Data opschonen")
        if st.button("Verwijder ALLE uitslagen"):
            ws_u = sh.worksheet("uitslagen")
            ws_u.clear()
            headers = ["koers_naam", "rank", "rider", "team"]
            ws_u.update([headers])
            st.success("Alle uitslagen zijn gewist uit de database.")
            st.cache_data.clear()
            st.rerun()

    elif poging != "":
        st.error("Onjuist wachtwoord. Toegang geweigerd.")
    else:
        st.info("Voer het wachtwoord in om de beheerdersfuncties te ontgrendelen.")