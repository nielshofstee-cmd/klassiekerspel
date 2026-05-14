import os
import json
import unicodedata
import streamlit as st
import pandas as pd
import requests
from curl_cffi import requests as cffi_requests
from bs4 import BeautifulSoup
import time
import random
from thefuzz import fuzz, process
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import extra_streamlit_components as stx

_AMS = ZoneInfo("Europe/Amsterdam")


# py -m streamlit run app_new.py         >> C:\Users\hofsteen\OneDrive - HEMA\Niels HEMA\Python projects\wielerspel\Wielerspel 2.0

# --- CONFIGURATIE ---
st.set_page_config(page_title="K1xSam Wielerspel 2026", page_icon="🚴‍♂️", layout="wide")

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
.block-container {
    padding-top: 0 !important;
}

[data-testid="stImage"] > img {
    border-radius: 0 !important;
    display: block;
}

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
    background-color: #ffffff !important;
}

[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe {
    background-color: #ffffff !important;
}

/* Tekst in tabellen donkerblauw (werkt bij niet-canvas rendering) */
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [class*="cell"],
[data-testid="stDataFrame"] [class*="header"] {
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
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[role="listbox"] {
    background: #ffffff !important;
    background-color: #ffffff !important;
}

[data-baseweb="popover"] li,
[data-baseweb="menu"] li,
[role="listbox"] li,
[role="option"] {
    color: var(--tekst-donker) !important;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px !important;
    background: #ffffff !important;
    background-color: #ffffff !important;
}

[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background: #f0f4f8 !important;
    background-color: #f0f4f8 !important;
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
        background: #ffffff !important;
        background-color: #ffffff !important;
    }

    [data-testid="stSelectbox"] > div > div *,
    [role="option"],
    [data-baseweb="menu"] li {
        color: var(--tekst-donker) !important;
        font-size: 15px !important;
    }

    /* Dropdown popover op mobiel altijd wit */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
    }

    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [role="option"] {
        background: #ffffff !important;
        background-color: #ffffff !important;
        color: #0d1f35 !important;
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
        background-color: #ffffff !important;
    }

    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] iframe {
        background-color: #ffffff !important;
    }

    /* Kolommen op mobiel onder elkaar */
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
}

/* Verberg "Clear all" knop op multiselect */
button[aria-label="Clear all"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE CONFIGURATIE & VERBINDING ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gspread_client():
    try:
        creds_info = None
        try:
            if "gcp_service_account" in st.secrets:
                creds_info = dict(st.secrets["gcp_service_account"])
        except Exception:
            pass

        if creds_info:
            if "\\n" in creds_info["private_key"]:
                creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
            credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
        else:
            google_creds_env = os.environ.get("GOOGLE_CREDENTIALS")
            if google_creds_env:
                creds_info = json.loads(google_creds_env)
                credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
            else:
                credentials = Credentials.from_service_account_file("google_keys.json", scopes=scopes)
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"❌ Verbinding met Google mislukt: {e}")
        return None

# Initialiseer de verbinding
gc = get_gspread_client()

# --- HET WACHTWOORD INSTELLEN ---
# We kijken eerst in secrets.toml, dan in de environment, en anders een harde fallback
try:
    ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD", "kankerbuffel"))
except Exception:
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "kankerbuffel")

if gc:
    try:
        SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1i8UB1igCk8cSCneTeQEGkxO0XFsuhSP2u4BLZfwHllM/edit"
        sh = gc.open_by_url(SPREADSHEET_URL)
    except Exception as e:
        st.error(f"❌ De Google Sheet kon niet worden geopend: {e}")
        st.stop()
else:
    st.stop()

# --- HULPFUNCTIES VOOR DATA ---

@st.cache_data(ttl=60) # Onthoud de data voor 60 seconden
def read_sheet(worksheet_name):
    try:
        # Een kleine random pauze helpt tegen de '429 Too Many Requests' error
        time.sleep(random.uniform(0.5, 1.5))
        worksheet = sh.worksheet(worksheet_name)
        # get_all_values() ipv get_all_records() om te voorkomen dat lege/dubbele
        # kolomkoppen een exception gooien (bijv. extra lege kolommen in de sheet)
        values = worksheet.get_all_values()
        if not values:
            return pd.DataFrame()
        headers = [str(h).strip().lower() for h in values[0]]
        df = pd.DataFrame(values[1:], columns=headers)
        # Verwijder kolommen zonder naam (lege header)
        df = df.loc[:, df.columns != '']
        return df
    except gspread.exceptions.WorksheetNotFound:
        return pd.DataFrame()
    except Exception as e:
        if "429" in str(e):
            st.error("Google limiet bereikt. Wacht even en ververs de pagina.")
        else:
            st.error(f"Fout bij laden van {worksheet_name}: {e}")
        return pd.DataFrame()

def get_koersen_volgorde():
    try:
        df_k = read_sheet("koersen")
        if not df_k.empty and 'koers_naam' in df_k.columns:
            return df_k['koers_naam'].tolist()
        return []
    except Exception:
        return []

# --- CONSTANTEN ---
PUNTEN_SCHEMA = {
    1:100, 2:90, 3:80, 4:70, 5:64, 6:60, 7:56, 8:52, 9:48, 10:44,
    11:40, 12:36, 13:32, 14:28, 15:24, 16:20, 17:16, 18:12, 19:8, 20:4
}

TABLE_HEADER_HEIGHT = 38
TABLE_ROW_HEIGHT = 35

# --- CONFIGURATIE DEADLINES 2026 ---
_KOERS_DATA_FALLBACK = {
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
    "Brabantse Pijl": "2026-04-17 12:00",
    "Amstel Gold Race": "2026-04-19 10:00",
    "La Fleche Wallone": "2026-04-22 11:00",
    "Liege Bastogne Liege": "2026-04-26 10:00"
}

# Laad deadlines vanuit de koersen sheet; valt terug op hardcoded waarden als de
# 'deadline' kolom ontbreekt. Voeg een 'deadline' kolom toe aan de koersen sheet
# (formaat: "YYYY-MM-DD HH:MM") om hier onderhoud te vermijden.
_df_koersen_init = read_sheet("koersen")
if (not _df_koersen_init.empty
        and 'koers_naam' in _df_koersen_init.columns
        and 'deadline' in _df_koersen_init.columns):
    KOERS_DATA = {
        str(row['koers_naam']).strip(): str(row['deadline']).strip()
        for _, row in _df_koersen_init.iterrows()
        if pd.notna(row['koers_naam']) and pd.notna(row['deadline'])
           and str(row['deadline']).strip() != ""
    } or _KOERS_DATA_FALLBACK
else:
    KOERS_DATA = _KOERS_DATA_FALLBACK


def get_standaard_koers_index(koers_lijst):
    """Geeft de index van de koers waarvan de deadlinedatum het dichtst bij vandaag ligt.
    Zo wordt een race van vandaag (deadline al voorbij) verkozen boven een race van morgen."""
    nu = datetime.now(_AMS)
    best_i, best_delta = 0, None
    for i, k in enumerate(koers_lijst):
        if k in KOERS_DATA:
            try:
                dt = datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
                delta = abs((dt - nu).total_seconds())
                if best_delta is None or delta < best_delta:
                    best_delta, best_i = delta, i
            except ValueError:
                pass
    return best_i

def get_volgende_koers_index(koers_lijst):
    """Geeft de index van de eerstvolgende koers (deadline in de toekomst).
    Als alle koersen voorbij zijn, wordt de laatste koers teruggegeven."""
    nu = datetime.now(_AMS)
    for i, k in enumerate(koers_lijst):
        if k in KOERS_DATA:
            try:
                dt = datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
                if dt > nu:
                    return i
            except ValueError:
                pass
    return max(0, len(koers_lijst) - 1)  # alle voorbij: laatste koers


# --- HANDMATIGE UITSLAG INVOER (fallback als scrapen mislukt) ---
def _handmatige_uitslag_opslaan(koers_naam, tekst):
    try:
        standard_cols = ['koers_naam', 'rank', 'rider', 'team']
        toegestane_statussen = {"DNF", "OTL", "DSQ", "DNS"}
        temp_data = []
        for regel in tekst.strip().splitlines():
            regel = regel.strip()
            if not regel:
                continue
            delen = [d.strip() for d in regel.split(',')]
            if len(delen) < 2:
                continue
            rank = delen[0].upper()
            rider_raw = delen[1] if len(delen) > 1 else ''
            team = delen[2] if len(delen) > 2 else ''
            rider = ' '.join(w.capitalize() for w in rider_raw.split())
            is_getal = rank.isdigit()
            is_status = rank in toegestane_statussen
            if rider and (is_getal or is_status):
                temp_data.append({"koers_naam": koers_naam, "rank": rank, "rider": rider, "team": team})

        if not temp_data:
            return False, "Geen geldige regels gevonden. Controleer het formaat: rank,rider,team"

        existing_df = read_sheet("uitslagen")
        if not existing_df.empty:
            other_races_df = existing_df[existing_df['koers_naam'] != koers_naam].copy()
        else:
            other_races_df = pd.DataFrame(columns=standard_cols)

        new_df = pd.DataFrame(temp_data)
        final_df = pd.concat([other_races_df, new_df], ignore_index=True)[standard_cols]

        ws_u = sh.worksheet("uitslagen")
        ws_u.clear()
        ws_u.update([standard_cols] + final_df.values.tolist())
        st.cache_data.clear()
        return True, f"Succes! {len(temp_data)} renners handmatig opgeslagen voor {koers_naam}."
    except Exception as e:
        return False, f"Fout bij opslaan: {str(e)}"


# --- SCRAPER: curl_cffi (echte browser TLS-fingerprint) + BeautifulSoup parsing ---

def _pcs_get(url, max_pogingen=4):
    """Haal een PCS-URL op via curl_cffi met Chrome-impersonatie (omzeilt Cloudflare)."""
    # Probeer meerdere recente Chrome-versies op volgorde
    impersonate_targets = ["chrome131", "chrome124", "chrome110", "chrome107"]
    laatste_fout = None
    for poging in range(max_pogingen):
        try:
            if poging > 0:
                time.sleep(random.uniform(2, 5) * poging)
            target = impersonate_targets[poging % len(impersonate_targets)]
            # Bouw referer op uit de URL (bijv. race-pagina als referer voor startlist)
            referer = "https://www.procyclingstats.com/"
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Upgrade-Insecure-Requests": "1",
                "Referer": referer,
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
            }
            resp = cffi_requests.get(url, impersonate=target, headers=headers, timeout=30)
            if resp.status_code == 403:
                laatste_fout = Exception(f"HTTP 403 bij poging {poging+1} (impersonate={target}). PCS blokkeert de request.")
                continue
            resp.raise_for_status()
            return resp
        except Exception as e:
            laatste_fout = e
            continue
    raise laatste_fout


# --- SCRAPER LOGICA ---

def scrape_en_save(koers_naam, url):
    """
    Scrapt de uitslag van een PCS result-pagina.
    PCS HTML-structuur (results):
      <table class="results basic moblist10 ...">
        <tbody>
          <tr>
            <td><span>1</span></td>           <!-- rank, soms in span -->
            <td>...</td>                       <!-- vlag -->
            <td><a href="rider/...">NAAM</a></td>
            <td><a href="team/...">TEAM</a></td>
            <td>3:03:15</td>
            ...
          </tr>
          <!-- DNF/OTL/DSQ rijen: rank-cel bevat de tekst direct -->
        </tbody>
      </table>
    """
    try:
        full_url = url.rstrip('/') + '/'
        response = _pcs_get(full_url)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Anti-bot check: als Cloudflare challenge wordt teruggegeven
        if soup.title and 'just a moment' in soup.title.text.lower():
            return False, "Cloudflare blokkade. Probeer later opnieuw."

        # Zoek de resultatentabel — PCS gebruikt class 'results' (soms met extra klassen)
        table = soup.find('table', class_=lambda c: c and 'results' in c)
        if not table:
            # Fallback: elke tabel met een tbody die rider-links bevat
            for t in soup.find_all('table'):
                if t.find('a', href=lambda h: h and 'rider/' in h):
                    table = t
                    break

        if not table:
            return False, "Geen uitslag tabel gevonden op deze pagina."

        data = []
        tbody = table.find('tbody') or table
        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue

            # Rank: PCS zet het getal soms in een <span> binnen de eerste <td>
            rank_td = cols[0]
            span = rank_td.find('span')
            rank = (span.text if span else rank_td.text).strip()

            # Renner: zoek link met 'rider/' in href
            rider = ""
            team = ""
            for a in row.find_all('a', href=True):
                href = a['href']
                if 'rider/' in href and not rider:
                    rider = a.text.strip()
                elif 'team/' in href and not team:
                    team = a.text.strip()

            # Sla op als er een renner gevonden is — sla DNS over (niet gestart = geen punten)
            if rider and rank and rank.upper() != 'DNS':
                norm_rank = rank.upper() if not rank.isdigit() else rank
                data.append([koers_naam, norm_rank, rider, team])

        if not data:
            return False, "Geen renners gevonden in de tabel. Is de uitslag al beschikbaar?"

        # Opslaan naar Google Sheets
        ws_u = sh.worksheet("uitslagen")
        current_data = ws_u.get_all_records()
        df_new = pd.DataFrame(data, columns=["koers_naam", "rank", "rider", "team"])

        if current_data:
            df_old = pd.DataFrame(current_data)
            df_old = df_old[df_old['koers_naam'] != koers_naam]
            final_df = pd.concat([df_old, df_new], ignore_index=True)
        else:
            final_df = df_new

        ws_u.clear()
        ws_u.update(values=[final_df.columns.values.tolist()] + final_df.values.tolist(), range_name='A1')

        return True, f"Uitslag voor {koers_naam} succesvol opgeslagen ({len(data)} renners)."

    except Exception as e:
        return False, f"Fout: {str(e)}"


def scrape_startlijst_en_save(koers_naam, url):
    """
    Scrapt de startlijst van een PCS startlist-pagina.
    PCS HTML-structuur (startlist_v4):
      <ul class="startlist_v4 ...">
        <li class="ridersCont">
          <b><a href="team/uae-team-emirates/2026">UAE Team Emirates</a></b>
          <ul>
            <li>
              <div class="bib">11</div>
              <a href="rider/tadej-pogacar">POGACAR Tadej</a>
            </li>
          </ul>
        </li>
      </ul>
    """
    try:
        # URL normaliseren naar /startlist
        base = url.rstrip('/')
        for suffix in ('/result', '/startlist'):
            if base.endswith(suffix):
                base = base[:-len(suffix)]
                break
        startlist_url = base + '/startlist'

        resp = _pcs_get(startlist_url)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Anti-bot check
        if soup.title and 'just a moment' in soup.title.text.lower():
            return False, "Cloudflare blokkade. Probeer later opnieuw."

        riders_data = []

        # --- Methode 1: table.basic (PCS tabel-layout) ---
        table_el = soup.find('table', class_='basic')
        if table_el:
            for row in (table_el.find('tbody') or table_el).find_all('tr'):
                r_link = row.find('a', href=lambda h: h and 'rider/' in h)
                if not r_link:
                    continue
                raw = r_link.text.strip()
                team_link = row.find('a', href=lambda h: h and 'team/' in h)
                team_name = team_link.text.strip() if team_link else ""
                cols = row.find_all('td')
                bib = ""
                if cols:
                    bib_txt = cols[0].text.strip()
                    bib = bib_txt if bib_txt.isdigit() else ""
                if raw and len(raw) > 2:
                    riders_data.append({
                        "koers_naam": koers_naam,
                        "startnummer": bib,
                        "rider": raw,
                        "team": team_name,
                    })

        # --- Methode 2: .startlist_v4 met .ridersCont (standaard PCS layout) ---
        if not riders_data:
            container = soup.find(class_='startlist_v4')
            if container:
                for team_block in container.find_all(class_='ridersCont'):
                    # Teamnaam: eerste <a> in het team-blok (exact zoals procyclingstats library)
                    first_a = team_block.find('a')
                    team_name = first_a.text.strip() if first_a else ""

                    rider_ul = team_block.find('ul')
                    if not rider_ul:
                        continue

                    for li in rider_ul.find_all('li', recursive=False):
                        # Bib: direct child element met class 'bib'
                        bib = ""
                        bib_el = li.find(class_='bib')
                        if bib_el:
                            bib_txt = bib_el.text.strip().split()[0] if bib_el.text.strip() else ""
                            bib = bib_txt if bib_txt.isdigit() else ""

                        r_link = li.find('a', href=lambda h: h and 'rider/' in h)
                        if not r_link:
                            continue
                        raw = r_link.text.strip()
                        if raw and len(raw) > 2:
                            riders_data.append({
                                "koers_naam": koers_naam,
                                "startnummer": bib,
                                "rider": raw,
                                "team": team_name,
                            })

        # --- Methode 3: andere startlist_v versies (v2, v3, v5...) ---
        if not riders_data:
            container = soup.find(class_=lambda c: c and isinstance(c, list) and
                any(cls.startswith('startlist_v') for cls in c))
            if container:
                for r_link in container.find_all('a', href=lambda h: h and 'rider/' in h):
                    raw = r_link.text.strip()
                    if not raw or len(raw) <= 2:
                        continue
                    parent = r_link.find_parent(class_='ridersCont')
                    team_name = ""
                    if parent:
                        first_a = parent.find('a')
                        team_name = first_a.text.strip() if first_a and first_a != r_link else ""
                    riders_data.append({
                        "koers_naam": koers_naam,
                        "startnummer": "",
                        "rider": raw,
                        "team": team_name,
                    })

        df_new = pd.DataFrame(riders_data).drop_duplicates(subset=['rider'])

        if df_new.empty:
            # Debug info: welke classes zitten er wel in de HTML?
            page_title = soup.title.text.strip() if soup.title else "geen titel"
            all_classes = set()
            for tag in soup.find_all(True):
                for cls in (tag.get('class') or []):
                    if 'startlist' in cls or 'riders' in cls or 'team' in cls.lower():
                        all_classes.add(cls)
            debug = f"Paginatitel: '{page_title}'. Gevonden classes: {sorted(all_classes)[:10]}"
            return False, f"Geen renners gevonden op PCS. {debug}"

        standard_cols = ['koers_naam', 'startnummer', 'rider', 'team']
        existing_sl = read_sheet("startlijsten")

        if not existing_sl.empty:
            other_sl = existing_sl[existing_sl['koers_naam'] != koers_naam].copy()
            final_sl = pd.concat([other_sl, df_new[standard_cols]], ignore_index=True)
        else:
            final_sl = df_new[standard_cols]

        final_sl = final_sl[standard_cols].astype(str).replace('nan', '')

        ws_sl = sh.worksheet("startlijsten")
        ws_sl.clear()
        ws_sl.update([standard_cols] + final_sl.values.tolist(), range_name='A1')

        st.cache_data.clear()
        return True, f"Succes! {len(df_new)} renners gevonden voor {koers_naam}."

    except Exception as e:
        return False, f"Startlijst fout: {str(e)}"


def scrape_pcs_resultaat(url, limit=None):
    """
    Generieke PCS scraper voor etappe-uitslag, GC, punten, KOM en youth.
    Dezelfde tabel-parsing als scrape_en_save() maar zonder sheet-opslag.
    Geeft (True, list_of_dicts) of (False, foutmelding) terug.
    limit: max aantal rijen te bewaren (None = alles)
    """
    try:
        resp = _pcs_get(url.rstrip('/') + '/')
        soup = BeautifulSoup(resp.text, 'html.parser')

        if soup.title and 'just a moment' in soup.title.text.lower():
            return False, "Cloudflare blokkade. Probeer later opnieuw."

        _url_clean = url.rstrip('/').lower()
        results_tables = soup.find_all('table', class_=lambda c: c and 'results' in c)
        _suffix = next((s for s in ('gc', 'points', 'kom', 'youth')
                        if _url_clean.endswith('-' + s)), None)

        if not results_tables:
            table = None
            for t in soup.find_all('table'):
                if t.find('a', href=lambda h: h and 'rider/' in h):
                    table = t
                    break
        elif _suffix:
            if _suffix in ('gc', 'points'):
                _idx = {'gc': 1, 'points': 2}[_suffix]
                table = results_tables[_idx] if _idx < len(results_tables) else None
            else:
                def _last_table_with_heading(keyword):
                    _found = None
                    for _t in results_tables:
                        _ph = _t.find_previous(['h1', 'h2', 'h3', 'h4'])
                        if _ph and keyword in _ph.get_text().lower():
                            _found = _t
                    return _found
                if _suffix == 'kom':
                    table = _last_table_with_heading('points at finish')
                else:  # youth
                    table = _last_table_with_heading('kom sprint')
            if not table:
                return False, f"Geen {_suffix.upper()}-klassementstabel gevonden op deze pagina (mogelijk nog niet beschikbaar)."
        else:
            table = results_tables[0]

        if not table:
            return False, "Geen resultatentabel gevonden op deze pagina."

        data = []
        tbody = table.find('tbody') or table
        for row in tbody.find_all('tr'):
            if limit and len(data) >= limit:
                break
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            rank_td = cols[0]
            span = rank_td.find('span')
            rank = (span.text if span else rank_td.text).strip()
            rider, team = '', ''
            for a in row.find_all('a', href=True):
                href = a['href']
                if 'rider/' in href and not rider:
                    rider = a.text.strip()
                elif 'team/' in href and not team:
                    team = a.text.strip()
            if rider and rank:
                data.append({'rank': rank.upper() if not rank.isdigit() else rank,
                             'rider': rider, 'team': team})

        if not data:
            return False, "Geen renners gevonden in de tabel. Is de uitslag al beschikbaar?"
        return True, data
    except Exception as e:
        return False, str(e)


def scrape_pcs_oranje_schildjes(url):
    """
    Scrapt renners met een oranje schild van een PCS etappe-pagina.
    PCS markeert het oranje schild met <div class="svg_shield">.
    """
    try:
        resp = _pcs_get(url.rstrip('/') + '/')
        soup = BeautifulSoup(resp.text, 'html.parser')
        if soup.title and 'just a moment' in soup.title.text.lower():
            return False, "Cloudflare blokkade. Probeer later opnieuw."

        table = soup.find('table', class_=lambda c: c and 'results' in c)
        if not table:
            for t in soup.find_all('table'):
                if t.find('a', href=lambda h: h and 'rider/' in h):
                    table = t
                    break
        if not table:
            return False, "Geen resultatentabel gevonden."

        data = []
        tbody = table.find('tbody') or table
        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            rank_td = cols[0]
            span_r = rank_td.find('span')
            rank = (span_r.text if span_r else rank_td.text).strip()
            rider, team = '', ''
            for a in row.find_all('a', href=True):
                href = a['href']
                if 'rider/' in href and not rider:
                    rider = a.text.strip()
                elif 'team/' in href and not team:
                    team = a.text.strip()
            if not rider:
                continue

            rider_cell = next(
                (td for td in cols if td.find('a', href=lambda h: h and 'rider/' in h)),
                None
            )
            has_shield = bool(
                rider_cell and rider_cell.find('div', class_='svg_shield')
            )

            if has_shield:
                data.append({'rank': rank, 'rider': rider, 'team': team})

        if not data:
            return False, "Geen renners met oranje schild gevonden op deze pagina."
        return True, data
    except Exception as e:
        return False, str(e)


def debug_pcs_row_html(url, max_rows=5):
    """
    Geeft per rij de ruwe HTML + alle icon-elementen met hun attributen,
    zodat je kunt zien welke class/style/title/href PCS gebruikt.
    """
    try:
        resp = _pcs_get(url.rstrip('/') + '/')
        soup = BeautifulSoup(resp.text, 'html.parser')
        if soup.title and 'just a moment' in soup.title.text.lower():
            return False, "Cloudflare blokkade."
        table = soup.find('table', class_=lambda c: c and 'results' in c)
        if not table:
            for t in soup.find_all('table'):
                if t.find('a', href=lambda h: h and 'rider/' in h):
                    table = t
                    break
        if not table:
            return False, "Geen tabel gevonden."
        tbody = table.find('tbody') or table
        out = []
        for row in tbody.find_all('tr')[:max_rows]:
            if not row.find_all('td'):
                continue
            rider_cell = next(
                (td for td in row.find_all('td')
                 if td.find('a', href=lambda h: h and 'rider/' in h)),
                None
            )
            icons_info = []
            if rider_cell:
                for elem in rider_cell.find_all(['svg', 'span', 'i', 'img', 'b', 'em', 'use']):
                    attrs = {k: v for k, v in elem.attrs.items()}
                    if attrs:
                        icons_info.append(f"<{elem.name} {attrs}>")
            out.append({
                'html':  str(row),
                'icons': icons_info,
            })
        return True, out
    except Exception as e:
        return False, str(e)

_RONDE_PUNTEN = {
    "etappe": {1:50, 2:44, 3:40, 4:36, 5:32, 6:30, 7:28, 8:26, 9:24, 10:22,
               11:20, 12:18, 13:16, 14:14, 15:12, 16:10, 17:8, 18:6, 19:4, 20:2},
    "gc":     {1:10, 2:8, 3:6, 4:4, 5:2},
    "points": {1:8,  2:6, 3:4, 4:2, 5:1},
    "kom":    {1:8,  2:6, 3:4, 4:2, 5:1},
    "youth":  {1:6,  2:4, 3:3, 4:2, 5:1},
}

_TEAM_BONUS = {'etappe': 10, 'gc': 8, 'points': 6, 'kom': 6, 'youth': 3}


def bereken_ronde_score(mijn_renners, uit_df, keuzes_df=None, speler_naam=None, etappes_df=None, team_df=None):
    """
    Berekent totaalpunten voor een speler over alle etappes en klassementen.
    mijn_renners : list van rennersnamen (alle, inclusief uitgewisseld)
    uit_df       : uitslagen_rondes DataFrame (al gefilterd op ronde/spel)
    keuzes_df    : keuzes_rondes DataFrame, optioneel
    speler_naam  : naam van de speler voor captain lookup, optioneel
    etappes_df   : etappes_rondes DataFrame, optioneel
    team_df      : speler_teams_rondes rijen voor deze speler (met vanaf_datum/tot_datum)
    Returns (totaal_int, details_list_of_dicts)
    """
    if not mijn_renners or uit_df.empty:
        return 0, []

    # Build etappe type lookup: etappe_str -> 'super'/'normaal'/'itt'/'tt'
    _et_type_lkp = {}
    if etappes_df is not None and not etappes_df.empty and 'type' in etappes_df.columns:
        for _, _er in etappes_df.iterrows():
            _et_type_lkp[str(_er['etappe'])] = str(_er.get('type', '')).strip().lower()

    # Build etappe deadline lookup: etappe_str -> date (for active-window filtering)
    _et_dl_lkp = {}
    if etappes_df is not None and not etappes_df.empty and 'deadline' in etappes_df.columns:
        for _, _er in etappes_df.iterrows():
            _dl_s = str(_er.get('deadline', '')).strip()
            for _fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    _et_dl_lkp[str(_er['etappe'])] = datetime.strptime(_dl_s, _fmt).date()
                    break
                except (ValueError, TypeError):
                    pass

    # Build per-rider active windows: renner_lower -> [(van_date, tot_date_or_None)]
    _rider_windows = {}
    if team_df is not None and not team_df.empty:
        for _, _tr in team_df.iterrows():
            _rn = str(_tr.get('renner_naam', '')).strip().lower()
            _van_s = str(_tr.get('vanaf_datum', '')).strip()
            _tot_s = str(_tr.get('tot_datum', '')).strip()
            _van_d, _tot_d = None, None
            if _van_s:
                for _fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        _van_d = datetime.strptime(_van_s, _fmt).date()
                        break
                    except (ValueError, TypeError):
                        pass
            if _tot_s:
                for _fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                    try:
                        _tot_d = datetime.strptime(_tot_s, _fmt).date()
                        break
                    except (ValueError, TypeError):
                        pass
            _rider_windows.setdefault(_rn, []).append((_van_d, _tot_d))

    def _active(rider_lower, etappe_str):
        """True if rider was in the team on the day of this etappe's deadline."""
        if not _rider_windows or rider_lower not in _rider_windows:
            return True
        _dl = _et_dl_lkp.get(etappe_str)
        if _dl is None:
            return True  # no deadline known → assume active
        for _van, _tot in _rider_windows[rider_lower]:
            # joined on or before deadline AND (not yet swapped out OR swapped out after deadline)
            if (_van is None or _dl >= _van) and (_tot is None or _dl < _tot):
                return True
        return False

    # Build captain lookup: etappe_str -> {rider_name: multiplier}
    _cap_lkp = {}
    if keuzes_df is not None and not keuzes_df.empty and speler_naam:
        _sp_k = keuzes_df[keuzes_df['speler_naam'] == speler_naam]
        for _, _kr in _sp_k.iterrows():
            _et_k = str(_kr['etappe'])
            _is_super = 'super' in _et_type_lkp.get(_et_k, '')
            _caps = {}
            _c1 = str(_kr.get('captain_1', '')).strip()
            if _c1:
                _caps[_c1] = 3.0 if _is_super else 2.0
            if _is_super:
                _c2 = str(_kr.get('captain_2', '')).strip()
                _c3 = str(_kr.get('captain_3', '')).strip()
                if _c2:
                    _caps[_c2] = 2.5
                if _c3:
                    _caps[_c3] = 2.0
            _cap_lkp[_et_k] = _caps

    # Case-insensitive lookup: lowercase key → original saved name
    renner_lower = {r.strip().lower(): r.strip() for r in mijn_renners}
    totaal = 0
    details = []
    for _, row in uit_df.iterrows():
        rider_raw = str(row.get('rider', '')).strip()
        rider_key = rider_raw.lower()
        if rider_key not in renner_lower:
            continue
        rider = renner_lower[rider_key]  # use saved name for captain lookup
        type_r = str(row.get('type_result', '')).strip()
        etappe_str = str(row.get('etappe', ''))
        if not _active(rider_key, etappe_str):
            continue
        # Captain multiplier only applies to individual etappe points
        multiplier = _cap_lkp.get(etappe_str, {}).get(rider, 1.0) if type_r == 'etappe' else 1.0

        # Oranje schildje: flat 20 punten per etappe, ongeacht positie
        if type_r == "schildjes":
            base_pnt = 20
            final_pnt = round(base_pnt * multiplier)
            totaal += final_pnt
            details.append({
                'etappe':     etappe_str,
                'type':       'schildjes',
                'renner':     rider,
                'rank':       row.get('rank', ''),
                'punten':     final_pnt,
                'multiplier': multiplier,
            })
            continue

        tabel = _RONDE_PUNTEN.get(type_r, {})
        if not tabel:
            continue
        rank_str = str(row.get('rank', '')).strip()
        if rank_str.isdigit():
            base_pnt = tabel.get(int(rank_str), 0)
            if base_pnt > 0:
                final_pnt = round(base_pnt * multiplier)
                totaal += final_pnt
                details.append({
                    'etappe':     etappe_str,
                    'type':       type_r,
                    'renner':     rider,
                    'rank':       rank_str,
                    'punten':     final_pnt,
                    'multiplier': multiplier,
                })

    # ── Teampunten ────────────────────────────────────────────────────────────
    # Build lowercase rider→team from all rows in uit_df
    _rider_team = {}
    for _, _tr in uit_df.iterrows():
        _rn = str(_tr.get('rider', '')).strip().lower()
        _tm = str(_tr.get('team', '')).strip()
        if _rn and _tm:
            _rider_team[_rn] = _tm

    # Per etappe + type: find rank-1 rider and their team
    _rank1_lkp = {}
    for _, _tr in uit_df.iterrows():
        if str(_tr.get('rank', '')).strip() != '1':
            continue
        _t = str(_tr.get('type_result', '')).strip()
        if _t not in _TEAM_BONUS:
            continue
        _et = str(_tr.get('etappe', ''))
        _rn = str(_tr.get('rider', '')).strip()
        _tm = str(_tr.get('team', '')).strip()
        if _rn and _tm:
            _rank1_lkp[(_et, _t)] = (_rn, _tm)

    for (_et, _t), (_leader, _leader_team) in _rank1_lkp.items():
        _bonus = _TEAM_BONUS[_t]
        for _rider_saved in renner_lower.values():
            if _rider_saved.lower() == _leader.lower():
                continue
            if not _active(_rider_saved.lower(), _et):
                continue
            if _rider_team.get(_rider_saved.lower(), '') == _leader_team:
                _mul = 1.0
                _pts = _bonus
                totaal += _pts
                details.append({
                    'etappe':     _et,
                    'type':       f'team_{_t}',
                    'renner':     _rider_saved,
                    'rank':       f'teamgenoot van {_leader}',
                    'punten':     _pts,
                    'multiplier': _mul,
                })

    return totaal, details


def save_ronde_uitslagen(spel, etappe, type_result, data):
    """Slaat gescrapete resultaten op in de 'uitslagen_rondes' sheet."""
    COLS = ['spel', 'etappe', 'type_result', 'rank', 'rider', 'team']
    try:
        try:
            ws = sh.worksheet('uitslagen_rondes')
            vals = ws.get_all_values()
            if len(vals) > 1:
                hdrs = [h.strip().lower() for h in vals[0]]
                existing = pd.DataFrame(vals[1:], columns=hdrs)
                existing = existing.loc[:, existing.columns != '']
            else:
                existing = pd.DataFrame(columns=COLS)
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet('uitslagen_rondes', rows=5000, cols=8)
            existing = pd.DataFrame(columns=COLS)

        if not existing.empty and all(c in existing.columns for c in ['spel', 'etappe', 'type_result']):
            existing = existing[
                ~((existing['spel'] == str(spel)) &
                  (existing['etappe'].astype(str) == str(etappe)) &
                  (existing['type_result'] == str(type_result)))
            ]

        new_rows = pd.DataFrame([
            {'spel': spel, 'etappe': str(etappe), 'type_result': type_result,
             'rank': r['rank'], 'rider': r['rider'], 'team': r['team']}
            for r in data
        ])
        for c in COLS:
            if c not in existing.columns:
                existing[c] = ''
        final = pd.concat([existing[COLS], new_rows], ignore_index=True)
        ws.clear()
        ws.update([COLS] + final.values.tolist())
        st.cache_data.clear()
        return True, f"{len(data)} resultaten opgeslagen (etappe {etappe} – {type_result})."
    except Exception as e:
        return False, str(e)


def add_manual_uitval_ronde(spel, etappe, rider, rank, team=''):
    """Voegt een handmatige DNS/DNF/OTL/DSQ toe aan uitslagen_rondes voor één renner.
    Overschrijft alleen de rij voor deze renner in de opgegeven etappe; alle
    overige etappe-rijen blijven ongewijzigd.
    """
    COLS = ['spel', 'etappe', 'type_result', 'rank', 'rider', 'team']
    try:
        try:
            ws = sh.worksheet('uitslagen_rondes')
            vals = ws.get_all_values()
            if len(vals) > 1:
                hdrs = [h.strip().lower() for h in vals[0]]
                existing = pd.DataFrame(vals[1:], columns=hdrs)
                existing = existing.loc[:, existing.columns != '']
            else:
                existing = pd.DataFrame(columns=COLS)
        except gspread.exceptions.WorksheetNotFound:
            ws = sh.add_worksheet('uitslagen_rondes', rows=5000, cols=8)
            existing = pd.DataFrame(columns=COLS)

        for c in COLS:
            if c not in existing.columns:
                existing[c] = ''

        # Remove existing row for this specific rider / etappe / type_result=etappe
        mask_remove = (
            (existing['spel'].astype(str).str.strip() == str(spel)) &
            (existing['etappe'].astype(str).str.strip() == str(etappe)) &
            (existing['type_result'].astype(str).str.strip() == 'etappe') &
            (existing['rider'].astype(str).str.strip().str.lower() == rider.strip().lower())
        )
        existing = existing[~mask_remove]

        new_row = pd.DataFrame([{
            'spel': spel, 'etappe': str(etappe), 'type_result': 'etappe',
            'rank': rank.upper(), 'rider': rider, 'team': team,
        }])
        final = pd.concat([existing[COLS], new_row], ignore_index=True)
        ws.clear()
        ws.update([COLS] + final.fillna('').values.tolist())
        st.cache_data.clear()
        return True, f"{rider} opgeslagen als {rank.upper()} voor etappe {etappe}."
    except Exception as e:
        return False, str(e)

# (AANGEPAST VOOR TEAM PUNTEN BIJ DNF/OTL/DSQ)
@st.cache_data(ttl=60)
def bereken_volledige_score(speler_naam, koers_naam, u_all, k_all, mijn_renners):
    # Lokale kopieën maken om de originele data niet te beschadigen
    u_df_local = u_all.copy()
    k_df_local = k_all.copy()

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
        
        if match_res and match_res[1] > 85:
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
            
            # Team punten logica: top-3 finishers en DNS krijgen GEEN teampunten
            punten_team = 0
            top3_renner = str(rank) in {"1", "2", "3"}
            is_dns = str(rank).upper() == "DNS"
            if rt and not top3_renner and not is_dns:
                if t1 and rt == t1: punten_team += 30
                if t2 and rt == t2: punten_team += 20
                if t3 and rt == t3: punten_team += 10
            
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

PAGINA_OPTIES = ["🏆 Klassement", "🏁 Uitslagen", "🚦 Startlijsten", "📊 Matrix", "🚌 Mijn Team", "🔄 Wissels", "©️ Captains", "⚙️ Beheer"]

# Data inladen via Google Sheets
u_all = read_sheet("uitslagen")
s_all = read_sheet("speler_teams")
creds_all = read_sheet("speler_credentials")
k_all = read_sheet("keuzes")
if k_all is None or k_all.empty:
    k_all = pd.DataFrame(columns=["speler_naam", "koers_naam", "captain_1", "captain_2", "captain_3"])

koersen_volgorde = get_koersen_volgorde()

# =============================================
# LOGIN (met persistente cookie)
# =============================================
cookie_manager = stx.CookieManager(key="km")
_COOKIE_NAME = "klassiekerspel_speler"

# Zorg dat session state bestaat
if 'ingelogd_speler' not in st.session_state:
    st.session_state['ingelogd_speler'] = None
    st.session_state['uitgelogd'] = False

# Herstel sessie vanuit cookie — alleen als niet expliciet uitgelogd
# CookieManager is asynchroon: waarde komt pas na 1e render beschikbaar
if st.session_state['ingelogd_speler'] is None and not st.session_state.get('uitgelogd', False):
    opgeslagen = cookie_manager.get(cookie=_COOKIE_NAME)
    if opgeslagen:
        st.session_state['ingelogd_speler'] = opgeslagen
        st.rerun()

# ── LANDING PAGE: geen login vereist ─────────────────────────────────────────
_GELDIGE_SPELLEN = {"klassiekerspel", "giro", "tour", "vuelta"}
_spel_param = st.query_params.get("spel", "").lower().strip()

if _spel_param and _spel_param not in _GELDIGE_SPELLEN:
    st.query_params.clear()
    st.rerun()

if _spel_param == "":
    # Logout afhandelen als er ?logout=1 in de URL staat
    if st.query_params.get("logout") == "1":
        try:
            cookie_manager.delete(_COOKIE_NAME)
        except Exception:
            pass
        st.session_state['ingelogd_speler'] = None
        st.session_state['uitgelogd'] = True
        st.query_params.clear()
        st.rerun()

    _li_early = st.session_state.get('ingelogd_speler')
    if _li_early:
        _creds_src_e = creds_all if (not creds_all.empty and 'email' in creds_all.columns) else s_all
        _row_e = _creds_src_e[_creds_src_e['speler_naam'] == _li_early]
        _email_e = _row_e['email'].iloc[0] if not _row_e.empty and 'email' in _row_e.columns else ""
        _nav_l = (
            f'<div class="nav-container"><div class="nav-header">'
            f'<div style="display:flex;align-items:center;">'
            f'<a href="/" style="text-decoration:none;"><span class="nav-logo">K1<span>x</span>Sam<span class="sep">|</span>Wielerspel</span></a>'
            f'</div>'
            f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:2px;">'
            f'<span style="font-size:12px;color:rgba(255,255,255,0.85);font-weight:600;">👤 {_li_early}</span>'
            f'<span style="font-size:10px;color:rgba(255,255,255,0.45);">{_email_e}</span>'
            f'<form action="" method="get" style="margin:0;padding:0;">'
            f'<input type="hidden" name="logout" value="1">'
            f'<button type="submit" style="background:transparent;border:none;color:rgba(255,120,80,0.85);cursor:pointer;font-size:10px;padding:0;margin-top:1px;">🚪 uitloggen</button>'
            f'</form>'
            f'</div></div></div>'
        )
    else:
        _nav_l = (
            f'<div class="nav-container"><div class="nav-header">'
            f'<div style="display:flex;align-items:center;">'
            f'<span class="nav-logo">K1<span>x</span>Sam<span class="sep">|</span>Wielerspel</span>'
            f'</div></div></div>'
        )
    st.markdown(_nav_l, unsafe_allow_html=True)
    st.markdown("""
    <style>
    .spel-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 24px;
        margin: 48px 0 32px 0;
    }
    @media (max-width: 900px) { .spel-grid { grid-template-columns: repeat(2, 1fr); } }
    @media (max-width: 500px) { .spel-grid { grid-template-columns: 1fr; } }
    .spel-card {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        background: white; border-radius: 20px; padding: 40px 24px 36px 24px;
        text-decoration: none; color: #0d1f35;
        box-shadow: 0 4px 24px rgba(13,31,53,0.10); border: 1.5px solid #d8e0eb;
        transition: box-shadow 0.2s ease, transform 0.18s ease, border-color 0.18s ease;
        min-height: 220px; cursor: pointer;
    }
    .spel-card:hover { box-shadow: 0 12px 40px rgba(13,31,53,0.18); transform: translateY(-4px); border-color: #f47c20; text-decoration: none; }
    .spel-card-icon { font-size: 52px; line-height: 1; margin-bottom: 18px; }
    .spel-card-title { font-family: 'Bebas Neue', sans-serif; font-size: 26px; letter-spacing: 2px; color: #0d1f35; margin-bottom: 6px; line-height: 1; }
    .spel-card-sub { font-family: 'DM Sans', sans-serif; font-size: 12px; font-weight: 500; color: #8a9ab5; text-transform: uppercase; letter-spacing: 1.5px; }
    .spel-card-badge { margin-top: 14px; background: #f47c20; color: white; font-family: 'DM Sans', sans-serif; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 20px; letter-spacing: 1px; text-transform: uppercase; }
    .spel-card-soon { margin-top: 14px; background: #eef1f6; color: #8a9ab5; font-family: 'DM Sans', sans-serif; font-size: 10px; font-weight: 700; padding: 3px 10px; border-radius: 20px; letter-spacing: 1px; text-transform: uppercase; }
    .landing-title { font-family: 'Bebas Neue', sans-serif; font-size: 2.2rem; color: #0d1f35; letter-spacing: 2px; margin-bottom: 4px; }
    .landing-sub { font-family: 'DM Sans', sans-serif; font-size: 15px; color: #5a6a82; margin-bottom: 0; }
    </style>
    <div style="margin-top:32px;">
        <div class="landing-title">Kies een spel</div>
        <div class="landing-sub">Selecteer een van de vier wielerspellen om door te gaan.</div>
    </div>
    <div class="spel-grid">
        <a href="?spel=klassiekerspel" class="spel-card">
            <div class="spel-card-icon">🚴</div>
            <div class="spel-card-title">Klassiekerspel</div>
            <div class="spel-card-sub">Voorjaarswedstrijden 2026</div>
            <div class="spel-card-badge">Actief</div>
        </a>
        <a href="?spel=giro" class="spel-card">
            <div class="spel-card-icon"><img src="https://flagcdn.com/w80/it.png" width="64" style="border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"></div>
            <div class="spel-card-title">Giro d'Italia</div>
            <div class="spel-card-sub">Grote ronde · Mei 2026</div>
            <div class="spel-card-badge">Actief</div>
        </a>
        <a href="?spel=tour" class="spel-card">
            <div class="spel-card-icon"><img src="https://flagcdn.com/w80/fr.png" width="64" style="border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"></div>
            <div class="spel-card-title">Tour de France</div>
            <div class="spel-card-sub">Grote ronde · Juli 2026</div>
            <div class="spel-card-soon">Binnenkort</div>
        </a>
        <a href="?spel=vuelta" class="spel-card">
            <div class="spel-card-icon"><img src="https://flagcdn.com/w80/es.png" width="64" style="border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"></div>
            <div class="spel-card-title">Vuelta a España</div>
            <div class="spel-card-sub">Grote ronde · Augustus 2026</div>
            <div class="spel-card-soon">Binnenkort</div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if st.session_state['ingelogd_speler'] is None:
    st.subheader("🔐 Inloggen")
    _login_src = creds_all if (not creds_all.empty and 'email' in creds_all.columns) else s_all
    if not _login_src.empty and 'email' in _login_src.columns:
        col_login, _ = st.columns([1, 2])
        with col_login:
            email_in = st.text_input("E-mailadres:")
            pin_in   = st.text_input("Pincode:", type="password")
            if st.button("Inloggen", type="primary"):
                match = _login_src[_login_src['email'].str.strip().str.lower() == email_in.strip().lower()]
                if match.empty:
                    st.error("E-mailadres niet gevonden.")
                else:
                    speler_naam_in = match['speler_naam'].iloc[0]
                    correct_pin_in = str(match['pincode'].iloc[0])
                    if pin_in == correct_pin_in:
                        st.session_state['ingelogd_speler'] = speler_naam_in
                        st.session_state['uitgelogd'] = False
                        cookie_manager.set(_COOKIE_NAME, speler_naam_in,
                                           expires_at=datetime.now() + timedelta(days=365))
                        st.rerun()
                    else:
                        st.error("Onjuiste pincode.")
    else:
        st.error("Kan spelerdata niet laden.")
    st.stop()

ingelogd_speler = st.session_state['ingelogd_speler']

# Logout via query param (?logout=1)
if st.query_params.get("logout") == "1":
    try:
        cookie_manager.delete(_COOKIE_NAME)
    except (KeyError, Exception):
        pass  # cookie was al verwijderd of nog niet geladen
    st.session_state['ingelogd_speler'] = None
    st.session_state['uitgelogd'] = True
    st.query_params.clear()
    st.rerun()

# Haal e-mailadres op van ingelogde speler (uit credentials sheet)
_creds_src = creds_all if (not creds_all.empty and 'email' in creds_all.columns) else s_all
_speler_row = (_creds_src[_creds_src['speler_naam'] == ingelogd_speler]
               if 'speler_naam' in _creds_src.columns else pd.DataFrame())
ingelogd_email = _speler_row['email'].iloc[0] if not _speler_row.empty and 'email' in _speler_row.columns else ""

# Actief spel bepalen voor badge in nav
_huidig_spel = st.query_params.get("spel", "")
_SPEL_LABELS = {
    "klassiekerspel": "🚴 Klassiekerspel",
    "giro":   '<img src="https://flagcdn.com/w20/it.png" style="height:13px;border-radius:2px;vertical-align:middle;margin-right:5px;"> Giro',
    "tour":   '<img src="https://flagcdn.com/w20/fr.png" style="height:13px;border-radius:2px;vertical-align:middle;margin-right:5px;"> Tour',
    "vuelta": '<img src="https://flagcdn.com/w20/es.png" style="height:13px;border-radius:2px;vertical-align:middle;margin-right:5px;"> Vuelta',
}
_spel_badge = (
    f'<span style="font-size:11px;font-weight:600;color:rgba(255,255,255,0.75);'
    f'background:rgba(255,255,255,0.10);padding:3px 10px;border-radius:20px;'
    f'border:1px solid rgba(255,255,255,0.15);margin-left:12px;letter-spacing:0.5px;">'
    f'{_SPEL_LABELS.get(_huidig_spel, "")}</span>'
    if _huidig_spel else ""
)

# Dynamische nav header met user info + uitloglink rechtsboven
_nav_html = (
    f'<div class="nav-container"><div class="nav-header">'
    f'<div style="display:flex;align-items:center;">'
    f'<a href="/" style="text-decoration:none;"><span class="nav-logo">K1<span>x</span>Sam<span class="sep">|</span>Wielerspel</span></a>'
    f'{_spel_badge}'
    f'</div>'
    f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:2px;">'
    f'<span style="font-size:12px;color:rgba(255,255,255,0.85);font-weight:600;">👤 {ingelogd_speler}</span>'
    f'<span style="font-size:10px;color:rgba(255,255,255,0.45);">{ingelogd_email}</span>'
    f'<form action="" method="get" style="margin:0;padding:0;">'
    f'<input type="hidden" name="logout" value="1">'
    f'<button type="submit" style="background:transparent;border:none;color:rgba(255,120,80,0.85);cursor:pointer;font-size:10px;padding:0;margin-top:1px;">🚪 uitloggen</button>'
    f'</form>'
    f'</div></div></div>'
)
st.markdown(_nav_html, unsafe_allow_html=True)

# ── _spel_param al bepaald boven de login-check ──────────────────────────────
# (landing page en routing worden afgehandeld vóór de login)
if False:
    st.markdown("""
    <style>
    .spel-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 24px;
        margin: 48px 0 32px 0;
    }
    @media (max-width: 900px) {
        .spel-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 500px) {
        .spel-grid { grid-template-columns: 1fr; }
    }
    .spel-card {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: white;
        border-radius: 20px;
        padding: 40px 24px 36px 24px;
        text-decoration: none;
        color: #0d1f35;
        box-shadow: 0 4px 24px rgba(13,31,53,0.10);
        border: 1.5px solid #d8e0eb;
        transition: box-shadow 0.2s ease, transform 0.18s ease, border-color 0.18s ease;
        min-height: 220px;
        cursor: pointer;
    }
    .spel-card:hover {
        box-shadow: 0 12px 40px rgba(13,31,53,0.18);
        transform: translateY(-4px);
        border-color: #f47c20;
        text-decoration: none;
    }
    .spel-card-icon {
        font-size: 52px;
        line-height: 1;
        margin-bottom: 18px;
    }
    .spel-card-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 26px;
        letter-spacing: 2px;
        color: #0d1f35;
        margin-bottom: 6px;
        line-height: 1;
    }
    .spel-card-sub {
        font-family: 'DM Sans', sans-serif;
        font-size: 12px;
        font-weight: 500;
        color: #8a9ab5;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    .spel-card-badge {
        margin-top: 14px;
        background: #f47c20;
        color: white;
        font-family: 'DM Sans', sans-serif;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .spel-card-soon {
        margin-top: 14px;
        background: #eef1f6;
        color: #8a9ab5;
        font-family: 'DM Sans', sans-serif;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .landing-title {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.2rem;
        color: #0d1f35;
        letter-spacing: 2px;
        margin-bottom: 4px;
    }
    .landing-sub {
        font-family: 'DM Sans', sans-serif;
        font-size: 15px;
        color: #5a6a82;
        margin-bottom: 0;
    }
    </style>

    <div style="margin-top:32px;">
        <div class="landing-title">Kies een spel</div>
        <div class="landing-sub">Selecteer een van de vier wielerspellen om door te gaan.</div>
    </div>

    <div class="spel-grid">
        <a href="?spel=klassiekerspel" class="spel-card">
            <div class="spel-card-icon">🚴</div>
            <div class="spel-card-title">Klassiekerspel</div>
            <div class="spel-card-sub">Voorjaarswedstrijden 2026</div>
            <div class="spel-card-badge">Actief</div>
        </a>
        <a href="?spel=giro" class="spel-card">
            <div class="spel-card-icon"><img src="https://flagcdn.com/w80/it.png" width="64" style="border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"></div>
            <div class="spel-card-title">Giro d'Italia</div>
            <div class="spel-card-sub">Grote ronde · Mei 2026</div>
            <div class="spel-card-soon">Binnenkort</div>
        </a>
        <a href="?spel=tour" class="spel-card">
            <div class="spel-card-icon"><img src="https://flagcdn.com/w80/fr.png" width="64" style="border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"></div>
            <div class="spel-card-title">Tour de France</div>
            <div class="spel-card-sub">Grote ronde · Juli 2026</div>
            <div class="spel-card-soon">Binnenkort</div>
        </a>
        <a href="?spel=vuelta" class="spel-card">
            <div class="spel-card-icon"><img src="https://flagcdn.com/w80/es.png" width="64" style="border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);"></div>
            <div class="spel-card-title">Vuelta a España</div>
            <div class="spel-card-sub">Grote ronde · Augustus 2026</div>
            <div class="spel-card-soon">Binnenkort</div>
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── PLOEG SELECTIE VOOR GROTE RONDES ─────────────────────────────────────────
if _spel_param in ("giro", "tour", "vuelta"):
    _SPEL_INFO = {
        "giro":   ("it", "Giro d'Italia",   "Mei 2026",      "categorie giro"),
        "tour":   ("fr", "Tour de France",  "Juli 2026",     "categorie tour"),
        "vuelta": ("es", "Vuelta a España", "Augustus 2026", "categorie vuelta"),
    }
    _flag_code, _naam, _periode, _cat_col = _SPEL_INFO[_spel_param]
    _flag_img_lg = (f'<img src="https://flagcdn.com/w80/{_flag_code}.png" '
                    f'style="height:36px;border-radius:3px;vertical-align:middle;'
                    f'margin-right:12px;box-shadow:0 2px 6px rgba(0,0,0,0.18);">')

    MAX_RENNERS_R   = 25
    MAX_PER_PLOEG_R = 2
    MAX_PER_LAND_R  = 5
    MAX_TOPPER_R    = 5
    MAX_SUBTOPPER_R = 5
    MIN_RENNER_R    = 3

    def _cat_type_ronde(cat):
        # Exacte waarden: "Max5 topper", "Max5 subtopper", "Min3 renner"
        c = str(cat).strip().lower()
        if "subtopper" in c: return "subtopper"
        if "topper" in c:    return "topper"
        if "renner" in c:    return "renner"
        return ""  # leeg/onbekend = nog niet ingedeeld

    # Alle renners laden; categorie-kolom alleen voor constraint-check
    _r_df = read_sheet("renners")
    if not _r_df.empty:
        _nc_r = next((c for c in ['renner','naam','name','rider','renner_naam'] if c in _r_df.columns), _r_df.columns[0])
        if _nc_r != 'renner':
            _r_df = _r_df.rename(columns={_nc_r: 'renner'})

    if not _r_df.empty:
        _r_race = _r_df.copy()
        if _cat_col in _r_race.columns:
            _r_race['_cat'] = _r_race[_cat_col].map(_cat_type_ronde)
        else:
            _r_race['_cat'] = "renner"
    else:
        _r_race = pd.DataFrame()

    # Opgeslagen ploeg ophalen (geen fout als sheet nog niet bestaat)
    _saved_r = []
    try:
        _ws_pr_read = sh.worksheet("speler_teams_rondes")
        _pr_vals = _ws_pr_read.get_all_values()
        if len(_pr_vals) > 1:
            _pr_hdrs = [str(h).strip().lower() for h in _pr_vals[0]]
            _pr_raw  = pd.DataFrame(_pr_vals[1:], columns=_pr_hdrs)
            _pr_raw  = _pr_raw.loc[:, _pr_raw.columns != '']
            if all(c in _pr_raw.columns for c in ["speler_naam","spel","renner_naam"]):
                _saved_r = _pr_raw[
                    (_pr_raw['speler_naam'].str.strip() == ingelogd_speler.strip()) &
                    (_pr_raw['spel'].str.strip().str.lower() == _spel_param)
                ]['renner_naam'].str.strip().tolist()
    except Exception:
        pass

    # Vriendelijke categorielabels (voor filter en tabel)
    _CAT_DISPLAY = {"topper": "Max5 topper", "subtopper": "Max5 subtopper", "renner": "Min3 renner", "": "—"}

    # ── Data laden voor alle tabbladen ──────────────────────────────────────────
    _pr_df_all_ronde = pd.DataFrame()
    try:
        _ws_pr_all = sh.worksheet("speler_teams_rondes")
        _pr_all_vals = _ws_pr_all.get_all_values()
        if len(_pr_all_vals) > 1:
            _hdrs_all = [str(h).strip().lower() for h in _pr_all_vals[0]]
            _pr_df_all_ronde = pd.DataFrame(_pr_all_vals[1:], columns=_hdrs_all)
            _pr_df_all_ronde = _pr_df_all_ronde.loc[:, _pr_df_all_ronde.columns != '']
            if 'spel' in _pr_df_all_ronde.columns:
                _pr_df_all_ronde = _pr_df_all_ronde[
                    _pr_df_all_ronde['spel'].str.strip().str.lower() == _spel_param
                ]
    except Exception:
        pass

    _uit_ronde = read_sheet("uitslagen_rondes")
    if not _uit_ronde.empty:
        _ronde_fc = next((c for c in ['ronde', 'spel'] if c in _uit_ronde.columns), None)
        if _ronde_fc:
            _uit_ronde = _uit_ronde[_uit_ronde[_ronde_fc].str.strip().str.lower() == _spel_param]

    _keuzes_ronde = read_sheet("keuzes_rondes")
    if not _keuzes_ronde.empty and 'ronde' in _keuzes_ronde.columns:
        _keuzes_ronde = _keuzes_ronde[_keuzes_ronde['ronde'].str.strip().str.lower() == _spel_param]

    _etappes_ronde = read_sheet("etappes_rondes")
    if not _etappes_ronde.empty:
        _etappes_ronde.columns = [c.strip().lower() for c in _etappes_ronde.columns]
        _ec_ronde = next((c for c in ['ronde', 'spel'] if c in _etappes_ronde.columns), None)
        if _ec_ronde:
            _etappes_ronde = _etappes_ronde[_etappes_ronde[_ec_ronde].str.strip().str.lower() == _spel_param]

    # Deadline etappe 1 → teams van anderen pas zichtbaar na deze tijd
    _et1_deadline = None
    if not _etappes_ronde.empty and 'etappe' in _etappes_ronde.columns and 'deadline' in _etappes_ronde.columns:
        _et1_row = _etappes_ronde[_etappes_ronde['etappe'].astype(str) == "1"]
        if not _et1_row.empty:
            _dl1_str = str(_et1_row.iloc[0].get('deadline', '')).strip()
            for _fmt1 in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    _et1_deadline = datetime.strptime(_dl1_str, _fmt1).replace(tzinfo=_AMS)
                    break
                except ValueError:
                    pass
    _giro_gestart = _et1_deadline is not None and datetime.now(_AMS) >= _et1_deadline

    tab_ploeg, tab_klassement, tab_uitslagen, tab_matrix, tab_team, tab_wissels, tab_captains, tab_beheer = st.tabs(
        ["👥 Ploeg", "🏆 Klassement", "🏁 Uitslagen", "📊 Matrix", "🚌 Mijn Team", "🔄 Wissels", "©️ Captains", "⚙️ Beheer"]
    )
    with tab_ploeg:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Ploeg Selectie</h1>', unsafe_allow_html=True)

        if _r_race.empty:
            st.warning(
                f"Geen renners gevonden voor **{_naam}**. "
                f"Zorg dat de renners-sheet beschikbaar is."
            )
        else:
            # Startlijst kolom opzoeken (bijv. 'giro pcs startlist')
            _sl_col = f"{_spel_param} pcs startlist"
            if _sl_col in _r_race.columns:
                _r_race['_starter'] = _r_race[_sl_col].astype(str).str.strip().str.lower() == "true"
            else:
                _r_race['_starter'] = False

            # Weergavenaam: bevestigde starters krijgen ✅ achteraan
            _r_race['_disp'] = _r_race.apply(
                lambda row: f"{row['renner']} ✅" if row['_starter'] else row['renner'], axis=1
            )
            # Starters eerst, daarna alfabetisch
            _r_sorted = _r_race.sort_values(['_starter', 'renner'], ascending=[False, True])
            alle_namen_r   = _r_sorted['_disp'].dropna().tolist()
            _disp2naam = dict(zip(_r_race['_disp'], _r_race['renner']))
            _naam2disp = dict(zip(_r_race['renner'], _r_race['_disp']))

            standaard_r = [_naam2disp.get(r, r) for r in _saved_r if _naam2disp.get(r, r) in alle_namen_r][:MAX_RENNERS_R]

            # Opgeslagen status tonen
            if standaard_r:
                st.info(f"💾 Je hebt **{len(standaard_r)} renners** opgeslagen voor {_naam}. "
                        f"Voeg meer toe of pas je selectie aan en sla opnieuw op.")
            else:
                st.caption(f"Nog geen ploeg opgeslagen voor {_naam}.")

            # ── Renners overzicht (opvouwbaar) ───────────────────────────────
            _n_starters = int(_r_race['_starter'].sum())
            with st.expander(f"📋 Alle beschikbare renners ({len(alle_namen_r)}, waarvan {_n_starters} ✅ bevestigd)", expanded=False):
                _ov_cols = [c for c in ['renner','_starter','_cat','team','land'] if c in _r_race.columns]
                _ov = _r_race[_ov_cols].copy().rename(columns={
                    'renner':'Renner','_starter':'Starter','_cat':'Categorie','team':'Ploeg','land':'Land'
                })
                _ov['Starter']   = _ov['Starter'].map({True: '✅', False: ''})
                _ov['Categorie'] = _ov['Categorie'].map(lambda x: _CAT_DISPLAY.get(x, x))
                _cat_opts = ["Alle", "Max5 topper", "Max5 subtopper", "Min3 renner", "—"]
                _cat_filter = st.selectbox(
                    "Filter op categorie",
                    _cat_opts,
                    key=f"cat_filter_{_spel_param}",
                )
                if _cat_filter != "Alle":
                    _ov = _ov[_ov['Categorie'] == _cat_filter]
                st.dataframe(
                    _ov.sort_values(['Starter','Renner'], ascending=[False, True]).reset_index(drop=True),
                    use_container_width=True, hide_index=True,
                    height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * min(len(_ov), 20)
                )

            st.markdown("---")

            if _giro_gestart:
                # Ploeg is vergrendeld na de start van de Giro
                st.warning(f"🔒 De {_naam} is gestart — je ploeg kan niet meer worden gewijzigd. Gebruik het Wissels-tabblad voor wijzigingen.")
                gekozen_r = _saved_r
                # Determine swapped-out riders (used in regels check and team table)
                _inactief_ploeg = set()
                if not _pr_df_all_ronde.empty:
                    _sp_rows_pl = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == ingelogd_speler]
                    if 'tot_datum' in _sp_rows_pl.columns:
                        _inactief_ploeg = set(
                            _sp_rows_pl[_sp_rows_pl['tot_datum'].astype(str).str.strip() != '']['renner_naam'].tolist()
                        )
                col_sel_r, col_chk_r = st.columns([3, 2])
                with col_sel_r:
                    st.subheader("Jouw vergrendelde ploeg")
            else:
                _inactief_ploeg = set()
                col_sel_r, col_chk_r = st.columns([3, 2])

            with col_sel_r:
                if not _giro_gestart:
                    st.subheader(f"Selecteer jouw ploeg")
                    st.caption("✅ = bevestigd op de startlijst · starters staan bovenaan")
                    _gekozen_disp = st.multiselect(
                        f"Kies renners (typ om te zoeken, max {MAX_RENNERS_R}):",
                        options=alle_namen_r,
                        default=standaard_r,
                        max_selections=MAX_RENNERS_R,
                        key=f"ploeg_{_spel_param}",
                    )
                    # Converteer weergavenamen terug naar echte namen
                    gekozen_r = [_disp2naam.get(d, d.replace(' ✅', '').strip()) for d in _gekozen_disp]
                    _pct = min(100, int(len(gekozen_r) / MAX_RENNERS_R * 100))
                    st.progress(_pct, text=f"{len(gekozen_r)} / {MAX_RENNERS_R} geselecteerd")

            with col_chk_r:
                st.subheader("Regels check")
                if gekozen_r:
                    _actief_r = [r for r in gekozen_r if r not in _inactief_ploeg] if _giro_gestart else gekozen_r
                    _sel = _r_race[_r_race['renner'].isin(_actief_r)].copy()
                    _n      = len(_actief_r)
                    _n_top  = int((_sel['_cat'] == 'topper').sum())
                    _n_sub  = int((_sel['_cat'] == 'subtopper').sum())
                    _n_ren  = int((_sel['_cat'] == 'renner').sum())

                    _ploeg_cnt = _sel['team'].value_counts() if 'team' in _sel.columns else pd.Series(dtype=int)
                    _land_cnt  = _sel['land'].value_counts() if 'land' in _sel.columns else pd.Series(dtype=int)
                    _ploeg_viol = _ploeg_cnt[_ploeg_cnt > MAX_PER_PLOEG_R].index.tolist()
                    _land_viol  = _land_cnt[_land_cnt  > MAX_PER_LAND_R ].index.tolist()

                    def _chk(ok, txt):
                        return f"{'✅' if ok else '❌'} {txt}"

                    st.markdown(_chk(_n <= MAX_RENNERS_R,
                        f"Totaal: **{_n} / {MAX_RENNERS_R}** renners"))
                    st.markdown(_chk(not _ploeg_viol,
                        f"Max {MAX_PER_PLOEG_R} per ploeg"
                        + (f"  \n&nbsp;&nbsp;⚠ {', '.join(_ploeg_viol)}" if _ploeg_viol else "")))
                    st.markdown(_chk(not _land_viol,
                        f"Max {MAX_PER_LAND_R} per land"
                        + (f"  \n&nbsp;&nbsp;⚠ {', '.join(_land_viol)}" if _land_viol else "")))
                    st.markdown(_chk(_n_top <= MAX_TOPPER_R,
                        f"Max5 topper: **{_n_top} / {MAX_TOPPER_R}**"))
                    st.markdown(_chk(_n_sub <= MAX_SUBTOPPER_R,
                        f"Max5 subtopper: **{_n_sub} / {MAX_SUBTOPPER_R}**"))
                    st.markdown(_chk(_n_ren >= MIN_RENNER_R,
                        f"Min3 renner: **{_n_ren}** (min {MIN_RENNER_R})"))

                    _all_ok_r = (
                        _n <= MAX_RENNERS_R
                        and not _ploeg_viol
                        and not _land_viol
                        and _n_top  <= MAX_TOPPER_R
                        and _n_sub  <= MAX_SUBTOPPER_R
                        and _n_ren  >= MIN_RENNER_R
                    )
                    if _all_ok_r:
                        st.success("Alle regels zijn OK!")
                    else:
                        st.caption("ℹ️ Je kunt tussentijds opslaan; pas wel de regels aan voor de deadline.")
                else:
                    _all_ok_r = True
                    st.info("Selecteer renners om de regels te controleren.")

            # Geselecteerde ploeg tabel
            if gekozen_r:
                st.markdown("---")
                st.subheader("Geselecteerde ploeg")
                _show_cols = [c for c in ['renner','_cat','team','land'] if c in _r_race.columns]
                _show_r = _r_race[_r_race['renner'].isin(gekozen_r)][_show_cols].copy()
                _show_r = _show_r.rename(columns={'renner':'Renner','_cat':'Categorie','team':'Ploeg','land':'Land'})
                _show_r['Categorie'] = _show_r['Categorie'].map(lambda x: _CAT_DISPLAY.get(x, x))
                if _inactief_ploeg:
                    _show_r['Status'] = _show_r['Renner'].apply(lambda r: '❌ Gewisseld' if r in _inactief_ploeg else '✅ Actief')
                _show_r = _show_r.sort_values(['Categorie','Renner']).reset_index(drop=True)
                st.dataframe(_show_r, use_container_width=True, hide_index=True,
                             height=TABLE_HEADER_HEIGHT + TABLE_ROW_HEIGHT * min(len(_show_r), 25))

            # Opslaan — altijd mogelijk zolang er renners geselecteerd zijn
            st.markdown("---")
            _btn_col, _ = st.columns([1, 3])
            with _btn_col:
                if st.button("💾 Ploeg opslaan", type="primary",
                             disabled=not gekozen_r or _giro_gestart,
                             key=f"save_{_spel_param}"):
                    try:
                        try:
                            _ws_pr = sh.worksheet("speler_teams_rondes")
                            _pr_ex = pd.DataFrame(_ws_pr.get_all_records())
                            if not _pr_ex.empty:
                                _pr_ex.columns = [str(c).strip().lower() for c in _pr_ex.columns]
                        except gspread.exceptions.WorksheetNotFound:
                            _ws_pr = sh.add_worksheet("speler_teams_rondes", rows=2000, cols=5)
                            _pr_ex = pd.DataFrame(columns=["speler_naam","spel","renner_naam"])

                        if not _pr_ex.empty and 'speler_naam' in _pr_ex.columns:
                            _pr_ex = _pr_ex[
                                ~((_pr_ex['speler_naam'] == ingelogd_speler) &
                                  (_pr_ex['spel'] == _spel_param))
                            ]
                        _vandaag = datetime.now(_AMS).strftime("%Y-%m-%d")
                        _pr_new = pd.DataFrame([
                            {"speler_naam": ingelogd_speler, "spel": _spel_param,
                             "renner_naam": r, "vanaf_datum": _vandaag, "tot_datum": ""}
                            for r in gekozen_r
                        ])
                        _COLS_PR = ["speler_naam","spel","renner_naam","vanaf_datum","tot_datum"]
                        for _c in _COLS_PR:
                            if _c not in _pr_ex.columns:
                                _pr_ex[_c] = ""
                        _pr_final = pd.concat([_pr_ex, _pr_new], ignore_index=True)[_COLS_PR]
                        _ws_pr.clear()
                        _ws_pr.update([_COLS_PR] + _pr_final.values.tolist())
                        st.cache_data.clear()
                        st.success(f"✅ Ploeg opgeslagen voor {_naam}! ({len(gekozen_r)} renners)")
                    except Exception as _e:
                        st.error(f"Fout bij opslaan: {_e}")

    # =============================================
    # KLASSEMENT
    # =============================================
    with tab_klassement:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Klassement</h1>', unsafe_allow_html=True)
        with st.expander("🔍 Debug klassement", expanded=False):
            st.write(f"Spel: `{_spel_param}` | Ploegen geladen: {len(_pr_df_all_ronde)} rijen | Uitslagen geladen: {len(_uit_ronde)} rijen")
            if not _pr_df_all_ronde.empty:
                st.write("Spelers in sheet:", sorted(_pr_df_all_ronde['speler_naam'].unique().tolist()))
                st.write("Voorbeeld rennersnamen (saved):", _pr_df_all_ronde['renner_naam'].dropna().head(5).tolist())
            if not _uit_ronde.empty:
                st.write("Etappes/types in uitslagen:", _uit_ronde.groupby(['etappe','type_result']).size().to_dict())
                _sample_riders = _uit_ronde[_uit_ronde['type_result'] == 'etappe']['rider'].head(5).tolist()
                st.write("Voorbeeld rider-namen (PCS):", _sample_riders)
                if not _pr_df_all_ronde.empty:
                    _saved_set = set(_pr_df_all_ronde['renner_naam'].str.strip())
                    _pcs_set   = set(_uit_ronde['rider'].str.strip())
                    _overlap   = _saved_set & _pcs_set
                    st.write(f"Overlap saved ↔ PCS: **{len(_overlap)}** van {len(_saved_set)} opgeslagen renners")
                    if not _overlap:
                        st.error("Geen enkele naam komt overeen — dit is de oorzaak van de 0 punten.")
                    else:
                        st.write("Matches:", sorted(_overlap)[:10])

        if _pr_df_all_ronde.empty:
            st.warning("Nog geen ploegen opgeslagen voor dit spel.")
        else:
            # Subpoule per speler ophalen uit credentials sheet
            _creds_kl = creds_all if (not creds_all.empty and 'subpoule' in creds_all.columns) else pd.DataFrame()
            def _get_poules(speler):
                if _creds_kl.empty:
                    return []
                _row = _creds_kl[_creds_kl['speler_naam'].str.strip() == speler.strip()]
                if _row.empty:
                    return []
                _val = str(_row['subpoule'].iloc[0]).strip()
                return [p.strip() for p in _val.split(',') if p.strip()] if _val and _val.lower() != 'nan' else []

            _spelers_kl = sorted(_pr_df_all_ronde['speler_naam'].unique())

            # Last etappe with results (for the extra column)
            _laatste_et_kl = None
            if not _uit_ronde.empty:
                _et_nums = [int(str(e)) for e in _uit_ronde['etappe'].unique() if str(e).isdigit()]
                if _et_nums:
                    _laatste_et_kl = str(max(_et_nums))
            _klas_col_et = f"Etappe {_laatste_et_kl}" if _laatste_et_kl else None

            _klas_data = []
            with st.spinner("Klassement berekenen..."):
                for _sp_kl in _spelers_kl:
                    _renners_kl = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _sp_kl]['renner_naam'].tolist()
                    _team_df_kl = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _sp_kl]
                    _tot_kl, _det_kl = bereken_ronde_score(_renners_kl, _uit_ronde, _keuzes_ronde, _sp_kl, _etappes_ronde, _team_df_kl)
                    _row_kl = {"Deelnemer": _sp_kl, "Punten": _tot_kl, "Poules": _get_poules(_sp_kl)}
                    if _laatste_et_kl:
                        _row_kl[_klas_col_et] = sum(d['punten'] for d in _det_kl if str(d.get('etappe', '')) == _laatste_et_kl)
                    _klas_data.append(_row_kl)

            _df_klas = (pd.DataFrame(_klas_data)
                        .sort_values("Punten", ascending=False)
                        .reset_index(drop=True))

            # Verzamel unieke poule-namen
            _alle_poules = sorted({p for row in _df_klas['Poules'] for p in row})

            def _toon_klas_tabel(df_sub):
                _ds = df_sub.copy().reset_index(drop=True)
                # Current ranks (df_sub is already sorted descending by Punten)
                _curr_rank = {name: i + 1 for i, name in enumerate(_ds['Deelnemer'])}

                _cols_show = ['Deelnemer']
                _col_cfg = {'Deelnemer': st.column_config.TextColumn('Deelnemer')}

                # Rank-change column (requires etappe column to derive previous total)
                if _klas_col_et and _klas_col_et in _ds.columns:
                    _prev_totals = _ds['Punten'] - _ds[_klas_col_et]
                    _prev_sorted = (
                        pd.DataFrame({'Deelnemer': _ds['Deelnemer'], '_p': _prev_totals})
                        .sort_values('_p', ascending=False)['Deelnemer'].tolist()
                    )
                    _prev_rank = {n: i + 1 for i, n in enumerate(_prev_sorted)}

                    def _trend(name):
                        c, p = _curr_rank.get(name), _prev_rank.get(name)
                        if c is None or p is None:
                            return ''
                        return '🟢 ▲' if c < p else ('🔴 ▼' if c > p else '🔵 —')

                    _ds['↕'] = _ds['Deelnemer'].apply(_trend)
                    _cols_show = ['↕'] + _cols_show
                    _col_cfg['↕'] = st.column_config.TextColumn('↕', width=50)

                # Etappe column first, then Tussenstand
                if _klas_col_et and _klas_col_et in _ds.columns:
                    _cols_show.append(_klas_col_et)
                    _col_cfg[_klas_col_et] = st.column_config.NumberColumn(_klas_col_et, format='%d')

                _cols_show.append('Punten')
                _col_cfg['Punten'] = st.column_config.NumberColumn('Tussenstand', format='%d')

                _ds = _ds[_cols_show].reset_index(drop=True)
                _ds.index += 1
                st.dataframe(
                    _ds,
                    column_config=_col_cfg,
                    use_container_width=True,
                    height=TABLE_HEADER_HEIGHT + len(_ds) * TABLE_ROW_HEIGHT,
                )

            if _alle_poules:
                _klas_tabs = st.tabs(["🌍 Algemeen"] + [f"👥 {p}" for p in _alle_poules])
                with _klas_tabs[0]:
                    _toon_klas_tabel(_df_klas)
                for _ki, _pnaam in enumerate(_alle_poules):
                    with _klas_tabs[_ki + 1]:
                        _df_p = _df_klas[_df_klas['Poules'].apply(lambda x: _pnaam in x)].reset_index(drop=True)
                        if _df_p.empty:
                            st.info(f"Geen spelers gevonden voor poule '{_pnaam}'.")
                        else:
                            _toon_klas_tabel(_df_p)
            else:
                _toon_klas_tabel(_df_klas)

    # =============================================
    # UITSLAGEN
    # =============================================
    with tab_uitslagen:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Uitslagen</h1>', unsafe_allow_html=True)
        if _uit_ronde.empty:
            st.info("Nog geen uitslagen beschikbaar. Scrape ze via het ⚙️ Beheer tabblad.")
        else:
            _TYPE_LABELS_U = {"etappe": "🏁 Etappe", "gc": "🏆 GC", "points": "💚 Punten", "kom": "🔴 KOM", "youth": "⬜ Jongeren"}
            _etappe_opties_u = sorted(_uit_ronde['etappe'].unique(), key=lambda x: int(str(x)) if str(x).isdigit() else 0)
            _ges_etappe_u = st.selectbox("Selecteer etappe:", _etappe_opties_u, key=f"uit_et_{_spel_param}")
            _uit_et_u = _uit_ronde[_uit_ronde['etappe'].astype(str) == str(_ges_etappe_u)]
            _type_opties_u = [t for t in ["etappe", "gc", "points", "kom", "youth"] if t in _uit_et_u['type_result'].values]
            if not _type_opties_u:
                st.info("Geen resultaten beschikbaar voor deze etappe.")
            else:
                _ges_type_u = st.selectbox("Resultaat type:", _type_opties_u,
                                            format_func=lambda x: _TYPE_LABELS_U.get(x, x),
                                            key=f"uit_type_{_spel_param}")
                _uit_show_u = _uit_et_u[_uit_et_u['type_result'] == _ges_type_u].copy()
                _uit_show_u['_sort'] = pd.to_numeric(_uit_show_u['rank'], errors='coerce').fillna(999)

                st.subheader(f"Etappe {_ges_etappe_u} – {_TYPE_LABELS_U.get(_ges_type_u, _ges_type_u)}")
                _disp_u = _uit_show_u.sort_values('_sort').head(50)
                _disp_cols_u = [c for c in ['rank', 'rider', 'team'] if c in _disp_u.columns]
                st.dataframe(_disp_u[_disp_cols_u], hide_index=True, use_container_width=True)

            st.divider()
            st.subheader(f"Punten per deelnemer – Etappe {_ges_etappe_u}")
            _uit_et_pu = _uit_ronde[_uit_ronde['etappe'].astype(str) == str(_ges_etappe_u)]
            _spelers_u = sorted(_pr_df_all_ronde['speler_naam'].unique())
            _rijen_pu = []
            for _sp_u in _spelers_u:
                _sp_rows_u = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _sp_u]
                _renners_u = _sp_rows_u['renner_naam'].tolist()
                _, _details_u = bereken_ronde_score(
                    _renners_u, _uit_et_pu,
                    keuzes_df=_keuzes_ronde, speler_naam=_sp_u,
                    etappes_df=_etappes_ronde, team_df=_sp_rows_u,
                )
                _per_renner_u = {}
                for _d in _details_u:
                    _rn = _d['renner']
                    _per_renner_u[_rn] = _per_renner_u.get(_rn, 0) + _d['punten']
                _samenvatting = ", ".join(
                    f"{_rn} ({_pts})"
                    for _rn, _pts in sorted(_per_renner_u.items(), key=lambda x: -x[1])
                    if _pts > 0
                )
                _totaal_u = sum(_per_renner_u.values())
                _rijen_pu.append({"Deelnemer": _sp_u, "Totaal": _totaal_u, "Renners (punten)": _samenvatting or "—"})
            if _rijen_pu:
                _df_pu = pd.DataFrame(_rijen_pu).sort_values("Totaal", ascending=False)
                st.dataframe(_df_pu, hide_index=True, use_container_width=False,
                             column_config={
                                 "Deelnemer": st.column_config.TextColumn("Deelnemer", width=130),
                                 "Totaal": st.column_config.NumberColumn("Totaal", width=80),
                                 "Renners (punten)": st.column_config.TextColumn("Renners (punten)", width=1200),
                             },
                             height=TABLE_HEADER_HEIGHT + len(_df_pu) * TABLE_ROW_HEIGHT)

    # =============================================
    # MATRIX
    # =============================================
    with tab_matrix:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Punten Matrix</h1>', unsafe_allow_html=True)
        if _pr_df_all_ronde.empty:
            st.info("Nog geen ploegen opgeslagen.")
        elif _uit_ronde.empty:
            st.info("Nog geen uitslagen beschikbaar.")
        else:
            if _giro_gestart:
                _spelers_mx = sorted(_pr_df_all_ronde['speler_naam'].unique())
                _def_mx = _spelers_mx.index(ingelogd_speler) if ingelogd_speler in _spelers_mx else 0
                _speler_mx = st.selectbox("Selecteer deelnemer:", _spelers_mx, index=_def_mx, key=f"mx_sp_{_spel_param}")
            else:
                _speler_mx = ingelogd_speler
                if _et1_deadline:
                    st.info(f"🔒 Teams van andere deelnemers zijn zichtbaar na de start van de {_naam} ({_et1_deadline.strftime('%d-%m-%Y %H:%M')}).")

            _sp_rows_mx = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _speler_mx]
            _mijn_r_mx = _sp_rows_mx['renner_naam'].tolist()
            if 'tot_datum' in _sp_rows_mx.columns:
                _inactief_mx = set(
                    _sp_rows_mx[_sp_rows_mx['tot_datum'].astype(str).str.strip() != '']['renner_naam'].tolist()
                )
            else:
                _inactief_mx = set()

            _etappes_mx = sorted(_uit_ronde['etappe'].unique(), key=lambda x: int(str(x)) if str(x).isdigit() else 0)

            # Bereken alle punten via bereken_ronde_score en groepeer per (renner, etappe)
            _, _details_mx = bereken_ronde_score(
                _mijn_r_mx, _uit_ronde,
                keuzes_df=_keuzes_ronde, speler_naam=_speler_mx,
                etappes_df=_etappes_ronde, team_df=_sp_rows_mx,
            )
            _pnten_mx = {}  # (renner, etappe) -> punten
            for _d in _details_mx:
                _k = (_d['renner'], str(_d['etappe']))
                _pnten_mx[_k] = _pnten_mx.get(_k, 0) + _d['punten']

            _matrix_r = []
            for _rn_mx in sorted(_mijn_r_mx):
                _label_mx = f"❌ {_rn_mx}" if _rn_mx in _inactief_mx else _rn_mx
                _rij_mx = {"Renner": _label_mx}
                _totaal_mx = 0
                for _et_mx in _etappes_mx:
                    _pnt = _pnten_mx.get((_rn_mx, str(_et_mx)), 0)
                    _rij_mx[f"E{_et_mx}"] = _pnt
                    _totaal_mx += _pnt
                _rij_mx["Totaal"] = _totaal_mx
                _matrix_r.append(_rij_mx)

            if _matrix_r:
                _df_mx = pd.DataFrame(_matrix_r).set_index("Renner")
                _df_mx = _df_mx.sort_values("Totaal", ascending=False)
                st.dataframe(_df_mx, use_container_width=True,
                             height=TABLE_HEADER_HEIGHT + len(_df_mx) * TABLE_ROW_HEIGHT)
            else:
                st.info("Geen renners gevonden.")

    # =============================================
    # MIJN TEAM
    # =============================================
    with tab_team:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Mijn Team</h1>', unsafe_allow_html=True)
        if _pr_df_all_ronde.empty:
            st.info("Nog geen ploegen opgeslagen voor dit spel.")
        else:
            if _giro_gestart:
                _spelers_tm = sorted(_pr_df_all_ronde['speler_naam'].unique())
                _def_tm = _spelers_tm.index(ingelogd_speler) if ingelogd_speler in _spelers_tm else 0
                _speler_tm = st.selectbox("Deelnemer:", _spelers_tm, index=_def_tm, key=f"tm_sp_{_spel_param}")
            else:
                _speler_tm = ingelogd_speler
                if _et1_deadline:
                    st.info(f"🔒 Teams van andere deelnemers zijn zichtbaar na de start van de {_naam} ({_et1_deadline.strftime('%d-%m-%Y %H:%M')}).")

            _sp_rows_tm_all = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _speler_tm]
            _sp_renners_tm = _sp_rows_tm_all['renner_naam'].tolist()
            # Inactive (swapped-out) riders for this player
            if 'tot_datum' in _sp_rows_tm_all.columns:
                _inactief_tm = set(
                    _sp_rows_tm_all[_sp_rows_tm_all['tot_datum'].astype(str).str.strip() != '']['renner_naam'].tolist()
                )
            else:
                _inactief_tm = set()
            if not _sp_renners_tm:
                st.info(f"{_speler_tm} heeft nog geen ploeg opgeslagen.")
            else:
                # Bereken punten per renner
                _tot_tm, _det_tm = bereken_ronde_score(_sp_renners_tm, _uit_ronde, _keuzes_ronde, _speler_tm, _etappes_ronde, _sp_rows_tm_all)
                _renner_pnt_tm = {}
                for _d in _det_tm:
                    _renner_pnt_tm[_d['renner']] = _renner_pnt_tm.get(_d['renner'], 0) + _d['punten']

                _team_rows_tm = []
                for _rn_tm in sorted(_sp_renners_tm):
                    _info_tm = _r_race[_r_race['renner'] == _rn_tm]
                    _pnt_tm = _renner_pnt_tm.get(_rn_tm, 0)
                    _status_tm = '❌ Gewisseld' if _rn_tm in _inactief_tm else '✅ Actief'
                    if not _info_tm.empty:
                        _ri_tm = _info_tm.iloc[0]
                        _team_rows_tm.append({
                            "Status": _status_tm,
                            "Renner": _rn_tm,
                            "Categorie": _CAT_DISPLAY.get(str(_ri_tm.get('_cat', '')), str(_ri_tm.get('_cat', ''))),
                            "Ploeg": _ri_tm.get('team', ''),
                            "Land": _ri_tm.get('land', ''),
                            "Punten": _pnt_tm,
                        })
                    else:
                        _team_rows_tm.append({"Status": _status_tm, "Renner": _rn_tm, "Categorie": "", "Ploeg": "", "Land": "", "Punten": _pnt_tm})
                _df_tm = (pd.DataFrame(_team_rows_tm)
                          .sort_values("Punten", ascending=False)
                          .reset_index(drop=True))
                st.dataframe(
                    _df_tm,
                    column_config={"Punten": st.column_config.NumberColumn("Punten", format="%d")},
                    hide_index=True,
                    use_container_width=True,
                    height=TABLE_HEADER_HEIGHT + len(_df_tm) * TABLE_ROW_HEIGHT,
                )
                st.metric("Totaal", f"{_tot_tm} punten", help=f"{len(_sp_renners_tm)} renners")

                # Puntenuitsplitsing per renner
                if _det_tm:
                    with st.expander("📋 Puntenuitsplitsing per renner"):
                        _sel_rn = st.selectbox(
                            "Renner:",
                            options=sorted({d['renner'] for d in _det_tm}),
                            key=f"detail_rn_{_spel_param}"
                        )
                        _TYPE_NL = {
                            'etappe': '🏁 Etappe', 'gc': '🏆 GC', 'points': '💚 Punten',
                            'kom': '🔴 KOM', 'youth': '⬜ Jongeren', 'schildjes': '🟠 Schildjes',
                            'team_etappe': '👥 Team etappe', 'team_gc': '👥 Team GC',
                            'team_points': '👥 Team punten', 'team_kom': '👥 Team KOM',
                            'team_youth': '👥 Team jongeren',
                        }
                        _rows_detail = [
                            {
                                'Etappe': d['etappe'],
                                'Type': _TYPE_NL.get(d['type'], d['type']),
                                'Rank': d['rank'],
                                'Basis': round(d['punten'] / d['multiplier']) if d.get('multiplier', 1) != 1 else d['punten'],
                                '×': f"{d.get('multiplier', 1.0):.1f}×" if d.get('multiplier', 1.0) != 1.0 else '—',
                                'Punten': d['punten'],
                            }
                            for d in _det_tm if d['renner'] == _sel_rn
                        ]
                        if _rows_detail:
                            _df_detail = pd.DataFrame(_rows_detail)
                            st.dataframe(_df_detail, hide_index=True, use_container_width=True)
                            st.write(f"**Totaal {_sel_rn}:** {sum(r['Punten'] for r in _rows_detail)} punten")
                        else:
                            st.info("Geen punten gevonden voor deze renner.")

    # =============================================
    # WISSELS
    # =============================================
    with tab_wissels:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Wissels</h1>', unsafe_allow_html=True)
        _MAX_WISSELS_R      = 3   # max 3 wissels per speler
        _MAX_PER_LAND_W     = 6   # max per land NA wissel (verruimd)
        _MAX_PER_PLOEG_W    = 3   # max per ploeg NA wissel (verruimd)

        if _pr_df_all_ronde.empty or _r_race.empty:
            st.info("Data niet beschikbaar.")
        else:
            _naam_w = ingelogd_speler
            _sp_rows_w = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _naam_w].copy()
            if _sp_rows_w.empty:
                st.info(f"Je hebt nog geen ploeg opgeslagen voor {_naam}.")
            else:
                _nu_w = datetime.now(_AMS)
                _today_w = pd.to_datetime(_nu_w.date())
                if 'tot_datum' in _sp_rows_w.columns and 'vanaf_datum' in _sp_rows_w.columns:
                    _van_parsed_w = pd.to_datetime(_sp_rows_w['vanaf_datum'], errors='coerce')
                    _tot_parsed_w = pd.to_datetime(_sp_rows_w['tot_datum'], errors='coerce')
                    _mask_act_w = (
                        (_van_parsed_w.isna() | (_van_parsed_w <= _today_w)) &
                        (_sp_rows_w['tot_datum'].isna() | (_sp_rows_w['tot_datum'] == "") |
                         (_tot_parsed_w > _today_w))
                    )
                    _actief_w = _sp_rows_w[_mask_act_w]['renner_naam'].tolist()
                    _wissels_gebruikt_w = int((_sp_rows_w['tot_datum'].notna() & (_sp_rows_w['tot_datum'] != "")).sum())
                else:
                    _actief_w = _sp_rows_w['renner_naam'].tolist()
                    _wissels_gebruikt_w = 0
                _wissels_over_w = max(0, _MAX_WISSELS_R - _wissels_gebruikt_w)

                # ── Bepaal laatste gerijde etappe en DNF/DNS-renners ─────────
                _laatste_et_nr_w = None
                _dnf_renners_w = set()   # genormaliseerde namen (stripped, lowercase)
                _dnf_naam_map_w = {}     # lowercase → originele naam uit uitslagen
                _dnf_rank_w = {}         # lowercase → rank string (DNF/DNS/OTL/DSQ)
                if not _uit_ronde.empty and 'type_result' in _uit_ronde.columns and 'etappe' in _uit_ronde.columns:
                    # Case-insensitive filter op type_result
                    _et_uitsl = _uit_ronde[_uit_ronde['type_result'].str.strip().str.lower() == 'etappe']
                    if not _et_uitsl.empty:
                        _laatste_et_nr_w = str(max(
                            _et_uitsl['etappe'].unique(),
                            key=lambda x: int(str(x)) if str(x).isdigit() else 0
                        ))
                        _et_last_rows = _et_uitsl[_et_uitsl['etappe'].astype(str) == _laatste_et_nr_w]
                        # DNF/OTL/DSQ/DNS: rank is niet-numeriek
                        _dnf_mask = ~pd.to_numeric(_et_last_rows['rank'], errors='coerce').notna()
                        for _, _dnf_row in _et_last_rows[_dnf_mask].iterrows():
                            _r_dnf = str(_dnf_row['rider']).strip()
                            _r_dnf_norm = _r_dnf.lower()
                            _dnf_renners_w.add(_r_dnf_norm)
                            _dnf_naam_map_w[_r_dnf_norm] = _r_dnf
                            _dnf_rank_w[_r_dnf_norm] = str(_dnf_row.get('rank', 'DNF')).upper()

                # Normaliseer actief-team namen voor vergelijking
                _actief_w_norm = {str(r).strip().lower(): str(r).strip() for r in _actief_w}

                # ── Bepaal beschermde renners (niet inwisselbaar) ─────────────
                _beschermd_w = {}   # genormaliseerde naam → reden
                if not _uit_ronde.empty:
                    # GC top 10
                    _gc_w = _uit_ronde[_uit_ronde['type_result'].str.strip().str.lower() == 'gc']
                    if not _gc_w.empty:
                        _lgc_et = str(max(_gc_w['etappe'].unique(),
                                          key=lambda x: int(str(x)) if str(x).isdigit() else 0))
                        _gc_last_w = _gc_w[_gc_w['etappe'].astype(str) == _lgc_et].copy()
                        _gc_last_w['_rn'] = pd.to_numeric(_gc_last_w['rank'], errors='coerce')
                        for _r in _gc_last_w[_gc_last_w['_rn'] <= 10]['rider'].tolist():
                            _beschermd_w[str(_r).strip().lower()] = f"🏆 GC top 10 (et.{_lgc_et})"
                    # Points/KOM/Youth top 3
                    for _klt, _lbl in [('points', '💚 Punten'), ('kom', '🔴 KOM'), ('youth', '⬜ Jongeren')]:
                        _kl_w = _uit_ronde[_uit_ronde['type_result'].str.strip().str.lower() == _klt]
                        if not _kl_w.empty:
                            _lkl_et = str(max(_kl_w['etappe'].unique(),
                                              key=lambda x: int(str(x)) if str(x).isdigit() else 0))
                            _kl_last_w = _kl_w[_kl_w['etappe'].astype(str) == _lkl_et].copy()
                            _kl_last_w['_rn'] = pd.to_numeric(_kl_last_w['rank'], errors='coerce')
                            for _r in _kl_last_w[_kl_last_w['_rn'] <= 3]['rider'].tolist():
                                _r_norm = str(_r).strip().lower()
                                if _r_norm not in _beschermd_w:
                                    _beschermd_w[_r_norm] = f"{_lbl} top 3 (et.{_lkl_et})"

                # ── Huidig team overzicht ──────────────────────────────────────
                col_w1, col_w2, col_w3 = st.columns(3)
                col_w1.metric("Wissels gebruikt", f"{_wissels_gebruikt_w} / {_MAX_WISSELS_R}")
                col_w2.metric("Wissels over", str(_wissels_over_w))
                if _laatste_et_nr_w:
                    col_w3.metric("Laatste etappe (DNF/DNS-check)", f"Etappe {_laatste_et_nr_w}")
                else:
                    col_w3.info("Nog geen etappe-uitslag beschikbaar.")

                st.subheader(f"Huidig team — {len(_actief_w)} renners")
                _team_info_w = []
                for _rn_w in sorted(_actief_w):
                    _rn_info_w = _r_race[_r_race['renner'] == _rn_w]
                    _rn_w_norm = str(_rn_w).strip().lower()
                    _is_dnf_w   = _rn_w_norm in _dnf_renners_w
                    _besch_w    = _beschermd_w.get(_rn_w_norm, "")
                    _uitval_lbl = f"❌ {_dnf_rank_w.get(_rn_w_norm, 'DNF')}" if _is_dnf_w else "✅ Actief"
                    _status_w   = _uitval_lbl if _is_dnf_w else (("🔒 " + _besch_w) if _besch_w else _uitval_lbl)
                    if not _rn_info_w.empty:
                        _ri_w = _rn_info_w.iloc[0]
                        _team_info_w.append({
                            "Renner":    _rn_w,
                            "Status":    _status_w,
                            "Ploeg":     _ri_w.get('team', ''),
                            "Land":      _ri_w.get('land', ''),
                            "Categorie": _CAT_DISPLAY.get(str(_ri_w.get('_cat', '')), str(_ri_w.get('_cat', ''))),
                        })
                    else:
                        _team_info_w.append({"Renner": _rn_w, "Status": _status_w,
                                             "Ploeg": "", "Land": "", "Categorie": ""})
                _df_team_w = pd.DataFrame(_team_info_w)
                st.dataframe(_df_team_w, hide_index=True, use_container_width=True,
                             height=TABLE_HEADER_HEIGHT + len(_df_team_w) * TABLE_ROW_HEIGHT)

                st.divider()

                # ── Debug-expander ─────────────────────────────────────────────
                with st.expander("🔍 Debug wissel-info", expanded=False):
                    st.write(f"**Laatste etappe:** {_laatste_et_nr_w}")
                    st.write(f"**DNF/DNS-renners gevonden in uitslagen (genormaliseerd):** {sorted(_dnf_renners_w) or '(geen)'}")
                    st.write(f"**Actief team genormaliseerd:** {sorted(_actief_w_norm.keys())}")
                    _debug_overlap = sorted(set(_actief_w_norm.keys()) & _dnf_renners_w)
                    st.write(f"**Overlap (wissels mogelijk):** {_debug_overlap or '(geen — controleer naamsverschil!)'}")
                    st.write(f"**_sp_rows_w shape:** {_sp_rows_w.shape}, columns: {list(_sp_rows_w.columns)}")
                    st.write(f"**_today_w:** {_today_w}")
                    st.dataframe(_sp_rows_w[['renner_naam','vanaf_datum','tot_datum']].head(5)
                                 if all(c in _sp_rows_w.columns for c in ['renner_naam','vanaf_datum','tot_datum'])
                                 else _sp_rows_w.head(5),
                                 hide_index=True, use_container_width=True)
                    _debug_match = []
                    for _an, _ao in sorted(_actief_w_norm.items()):
                        _in_dnf = _an in _dnf_renners_w
                        _beschermd = _beschermd_w.get(_an, "")
                        _debug_match.append({"Renner (team)": _ao, "Genorm. teamnaam": _an,
                                             "In DNF-lijst": _in_dnf, "Beschermd": _beschermd or "—"})
                    st.dataframe(pd.DataFrame(_debug_match), hide_index=True, use_container_width=True)
                    if _dnf_renners_w:
                        st.write("**DNF-namen uit uitslagen (genormaliseerd):**")
                        st.write(sorted(_dnf_renners_w))

                st.divider()
                if _wissels_over_w <= 0:
                    st.warning(f"Je hebt alle {_MAX_WISSELS_R} wissels al gebruikt.")
                elif _laatste_et_nr_w is None:
                    st.info("Er zijn nog geen etappe-uitslagen beschikbaar. Wissels zijn pas mogelijk nadat de eerste etappe is gescraped.")
                else:
                    # Renners die uit mogen: DNF/DNS in laatste etappe (beschermd klassement geldt alleen voor erin)
                    # Vergelijking via genormaliseerde namen (case-insensitive, stripped)
                    _inwisselbaar_w = [
                        _actief_w_norm[_an]
                        for _an in _actief_w_norm
                        if _an in _dnf_renners_w
                    ]

                    if not _inwisselbaar_w:
                        st.info(
                            f"Geen van jouw renners heeft een DNF of DNS in etappe {_laatste_et_nr_w}. "
                            "Open de debug-expander hierboven voor details."
                        )
                    else:
                        st.subheader("Wissel doorvoeren")
                        st.caption(
                            f"Alleen renners met DNF of DNS in etappe {_laatste_et_nr_w} mogen eruit. "
                            f"Renners in een beschermd klassement (GC top 10 / andere top 3) kunnen niet worden ingewisseld, "
                            f"maar mogen wel eruit als ze DNF/DNS hebben. "
                            f"Na de wissel gelden: max {MAX_TOPPER_R} toppers, max {MAX_SUBTOPPER_R} subtoppers, "
                            f"max {_MAX_PER_PLOEG_W} per ploeg, max {_MAX_PER_LAND_W} per land."
                        )

                        _actief_set_w = set(_actief_w)
                        # Only show confirmed starters; fall back to all riders if startlist unknown
                        _heeft_starters_w = '_starter' in _r_race.columns and _r_race['_starter'].any()
                        _starter_pool_w = (
                            set(_r_race[_r_race['_starter']]['renner'].tolist())
                            if _heeft_starters_w else set(_r_race['renner'].tolist())
                        )
                        _beschikbaar_w = sorted([r for r in _starter_pool_w
                                                 if r not in _actief_set_w
                                                 and str(r).strip().lower() not in _beschermd_w])

                        _max_n_w = min(_wissels_over_w, len(_inwisselbaar_w))
                        _n_w = st.number_input("Hoeveel wissels?", min_value=1, max_value=_max_n_w,
                                               value=1, step=1, key=f"n_wissels_{_spel_param}")

                        _uit_keuzes_w, _in_keuzes_w = [], []
                        for _i_w in range(int(_n_w)):
                            st.markdown(f"**Wissel {_i_w + 1}**")
                            _cw1, _cw2 = st.columns(2)
                            with _cw1:
                                _uit_opties_w = [r for r in _inwisselbaar_w if r not in _uit_keuzes_w]
                                _uit_w = st.selectbox("Eruit (DNF/DNS):", _uit_opties_w,
                                                      key=f"wuit_{_spel_param}_{_i_w}")
                                _uit_keuzes_w.append(_uit_w)
                            with _cw2:
                                _in_w = st.selectbox("Erin:", [r for r in _beschikbaar_w if r not in _in_keuzes_w],
                                                     key=f"win_{_spel_param}_{_i_w}")
                                _in_keuzes_w.append(_in_w)

                        if st.button("✅ Bevestig wissels", key=f"wissel_btn_{_spel_param}"):
                            # ── Valideer nieuw team ───────────────────────────
                            _nieuw_team_w = [r for r in _actief_w if r not in _uit_keuzes_w] + _in_keuzes_w
                            _nieuw_info_w = _r_race[_r_race['renner'].isin(_nieuw_team_w)]
                            _w_err = []

                            _n_top_w  = int((_nieuw_info_w['_cat'] == 'topper').sum())
                            _n_sub_w  = int((_nieuw_info_w['_cat'] == 'subtopper').sum())
                            _n_ren_w  = int((_nieuw_info_w['_cat'] == 'renner').sum())
                            if _n_top_w > MAX_TOPPER_R:
                                _w_err.append(f"Te veel toppers: {_n_top_w} (max {MAX_TOPPER_R})")
                            if _n_sub_w > MAX_SUBTOPPER_R:
                                _w_err.append(f"Te veel subtoppers: {_n_sub_w} (max {MAX_SUBTOPPER_R})")
                            if _n_ren_w < 3:
                                _w_err.append(f"Te weinig renners: {_n_ren_w} (min 3)")

                            if 'team' in _nieuw_info_w.columns:
                                _ploeg_cnt_w = _nieuw_info_w['team'].value_counts()
                                _ploeg_viol_w = _ploeg_cnt_w[_ploeg_cnt_w > _MAX_PER_PLOEG_W].index.tolist()
                                if _ploeg_viol_w:
                                    _w_err.append(f"Max {_MAX_PER_PLOEG_W} per ploeg overschreden: {', '.join(_ploeg_viol_w)}")
                            if 'land' in _nieuw_info_w.columns:
                                _land_cnt_w = _nieuw_info_w['land'].value_counts()
                                _land_viol_w = _land_cnt_w[_land_cnt_w > _MAX_PER_LAND_W].index.tolist()
                                if _land_viol_w:
                                    _w_err.append(f"Max {_MAX_PER_LAND_W} per land overschreden: {', '.join(_land_viol_w)}")

                            # Controleer of "eruit" renners nog steeds eligible zijn (genormaliseerd)
                            _niet_elig_w = [r for r in _uit_keuzes_w
                                            if str(r).strip().lower() not in _dnf_renners_w]
                            if _niet_elig_w:
                                _w_err.append(f"Niet inwisselbaar: {', '.join(_niet_elig_w)}")

                            # Controleer of "erin" renners niet beschermd zijn
                            _in_beschermd_w = [r for r in _in_keuzes_w
                                               if str(r).strip().lower() in _beschermd_w]
                            if _in_beschermd_w:
                                _w_err.append(f"Kan niet erin: {', '.join(_in_beschermd_w)} staat in een beschermd klassement")

                            if _w_err:
                                for _we in _w_err:
                                    st.error(_we)
                            else:
                                try:
                                    _ws_pr_w2 = sh.worksheet("speler_teams_rondes")
                                    _pr_w2_vals = _ws_pr_w2.get_all_values()
                                    _pr_w2_hdrs = [str(h).strip().lower() for h in _pr_w2_vals[0]]
                                    _pr_w2_df = (pd.DataFrame(_pr_w2_vals[1:], columns=_pr_w2_hdrs)
                                                 if len(_pr_w2_vals) > 1
                                                 else pd.DataFrame(columns=_pr_w2_hdrs))
                                    _pr_w2_df = _pr_w2_df.loc[:, _pr_w2_df.columns != '']
                                    _datum_w2 = _nu_w.strftime("%Y-%m-%d")
                                    _mask_sp_w2 = (_pr_w2_df['speler_naam'] == _naam_w) & (_pr_w2_df['spel'] == _spel_param)
                                    for _r_uit_w in _uit_keuzes_w:
                                        _idx_w = _pr_w2_df[
                                            _mask_sp_w2 & (_pr_w2_df['renner_naam'] == _r_uit_w) &
                                            ((_pr_w2_df['tot_datum'] == "") | _pr_w2_df['tot_datum'].isna())
                                        ].index
                                        _pr_w2_df.loc[_idx_w, 'tot_datum'] = _datum_w2
                                    _cols_wr = ['speler_naam', 'spel', 'renner_naam', 'vanaf_datum', 'tot_datum']
                                    for _r_in_w in _in_keuzes_w:
                                        _new_wr = pd.DataFrame([{"speler_naam": _naam_w, "spel": _spel_param,
                                                                  "renner_naam": _r_in_w, "vanaf_datum": _datum_w2, "tot_datum": ""}])
                                        _pr_w2_df = pd.concat([_pr_w2_df, _new_wr], ignore_index=True)
                                    for _c_wr in _cols_wr:
                                        if _c_wr not in _pr_w2_df.columns:
                                            _pr_w2_df[_c_wr] = ""
                                    _ws_pr_w2.clear()
                                    _ws_pr_w2.update([_cols_wr] + _pr_w2_df[_cols_wr].fillna("").values.tolist())
                                    st.cache_data.clear()
                                    st.success(f"Wissels opgeslagen! {', '.join(_uit_keuzes_w)} → {', '.join(_in_keuzes_w)}")
                                    time.sleep(1)
                                    st.rerun()
                                except Exception as _ew:
                                    st.error(f"Fout bij opslaan: {_ew}")

    # =============================================
    # CAPTAINS
    # =============================================
    with tab_captains:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Captains</h1>', unsafe_allow_html=True)
        if _pr_df_all_ronde.empty:
            st.info("Nog geen ploegen opgeslagen voor dit spel.")
        elif _etappes_ronde.empty:
            st.info("Geen etappes geconfigureerd voor dit spel. Voeg etappes toe via de etappes_rondes sheet.")
        else:
            _nu_cap = datetime.now(_AMS)
            _spelers_cap = sorted(_pr_df_all_ronde['speler_naam'].unique())

            # Bouw deadline dict per etappe
            _et_deadlines = {}
            if 'etappe' in _etappes_ronde.columns and 'deadline' in _etappes_ronde.columns:
                for _, _erow in _etappes_ronde.iterrows():
                    _dl_str = str(_erow.get('deadline', '')).strip()
                    _dl_dt = None
                    if _dl_str:
                        for _fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                            try:
                                _dl_dt = datetime.strptime(_dl_str, _fmt).replace(tzinfo=_AMS)
                                break
                            except ValueError:
                                pass
                    _et_deadlines[str(_erow['etappe'])] = _dl_dt

            # Overzicht captains (tabel)
            st.subheader("📋 Overzicht Captains")
            _gestart_et = [e for e, d in _et_deadlines.items() if d and d <= _nu_cap]
            _toekomst_et = [e for e, d in _et_deadlines.items() if not d or d > _nu_cap]
            _laatste_g_et = _gestart_et[-1] if _gestart_et else None
            _toon_et = ([_laatste_g_et] if _laatste_g_et else []) + _toekomst_et

            if _toon_et:
                _th_s = "padding:6px 10px;background:#1a2e4a;color:white;font-size:12px;text-align:center;white-space:nowrap;"
                _td_sp_s = "padding:6px 10px;font-size:13px;font-weight:600;white-space:nowrap;background:white;border-bottom:1px solid #e2e8f0;"
                _td_b_s = "padding:6px 10px;font-size:13px;text-align:center;background:white;border-bottom:1px solid #e2e8f0;"
                _ov_html = f'<table style="width:100%;border-collapse:collapse;"><thead><tr><th style="{_th_s}text-align:left;">Speler</th>'
                for _et_c in _toon_et:
                    _ov_html += f'<th style="{_th_s}">Et.{_et_c}</th>'
                _ov_html += "</tr></thead><tbody>"
                for _sp_c in _spelers_cap:
                    _ov_html += f'<tr><td style="{_td_sp_s}">{_sp_c}</td>'
                    for _et_c in _toon_et:
                        _keuze_c = (
                            _keuzes_ronde[(_keuzes_ronde['speler_naam'] == _sp_c) & (_keuzes_ronde['etappe'].astype(str) == str(_et_c))]
                            if not _keuzes_ronde.empty and 'etappe' in _keuzes_ronde.columns
                            else pd.DataFrame()
                        )
                        _heeft_c = not _keuze_c.empty and str(_keuze_c.iloc[0].get('captain_1', '')).strip() != ""
                        _dl_c = _et_deadlines.get(str(_et_c))
                        _et_type_ov = str(_etappes_ronde[_etappes_ronde['etappe'].astype(str) == str(_et_c)].iloc[0].get('type', '')).strip().lower() if not _etappes_ronde[_etappes_ronde['etappe'].astype(str) == str(_et_c)].empty else ""
                        _is_super_ov = 'super' in _et_type_ov
                        if _dl_c and _dl_c <= _nu_cap:
                            if _heeft_c:
                                _rc = _keuze_c.iloc[0]
                                if _is_super_ov:
                                    _cel = f"{_rc.get('captain_1','')} · {_rc.get('captain_2','')} · {_rc.get('captain_3','')}"
                                else:
                                    _cel = str(_rc.get('captain_1', ''))
                            else:
                                _cel = "—"
                            _ov_html += f'<td style="{_td_b_s}">{_cel}</td>'
                        else:
                            _icon_c = '<span style="color:green;font-weight:bold;">✓</span>' if _heeft_c else '<span style="color:red;font-weight:bold;">✗</span>'
                            _ov_html += f'<td style="{_td_b_s}">{_icon_c}</td>'
                    _ov_html += "</tr>"
                _ov_html += "</tbody></table>"
                st.markdown(_ov_html, unsafe_allow_html=True)

            st.divider()
            st.subheader("📝 Captains Instellen")
            if 'etappe' not in _etappes_ronde.columns:
                st.info("Geen etappenummers gevonden in de etappes_rondes sheet.")
            else:
                _et_opties_cap = _etappes_ronde['etappe'].tolist()
                _et_sorted_cap = sorted(_et_opties_cap, key=lambda x: int(str(x)) if str(x).isdigit() else 0)
                _next_et_cap = next(
                    (e for e in _et_sorted_cap if _et_deadlines.get(str(e)) and _et_deadlines[str(e)] > _nu_cap),
                    _et_sorted_cap[-1] if _et_sorted_cap else None,
                )
                _default_et_idx = _et_opties_cap.index(_next_et_cap) if _next_et_cap in _et_opties_cap else 0
                _et_cap = st.selectbox("Voor welke etappe?", _et_opties_cap, index=_default_et_idx, key=f"cap_et_{_spel_param}")
                _et_row_cap = _etappes_ronde[_etappes_ronde['etappe'].astype(str) == str(_et_cap)]
                _deadline_cap_str = str(_et_row_cap.iloc[0].get('deadline', '')).strip() if not _et_row_cap.empty else ""
                _deadline_cap_dt = _et_deadlines.get(str(_et_cap))
                _et_type_cap = str(_et_row_cap.iloc[0].get('type', '')).strip().lower() if not _et_row_cap.empty else ""
                _is_super_cap = 'super' in _et_type_cap

                _naam_cap = ingelogd_speler
                _huid_cap = (
                    _keuzes_ronde[(_keuzes_ronde['speler_naam'] == _naam_cap) & (_keuzes_ronde['etappe'].astype(str) == str(_et_cap))]
                    if not _keuzes_ronde.empty and 'etappe' in _keuzes_ronde.columns
                    else pd.DataFrame()
                )
                if not _huid_cap.empty:
                    _rc_h = _huid_cap.iloc[0]
                    if _is_super_cap:
                        st.info(f"Huidige keuze: 1. {_rc_h.get('captain_1','')} (3.0×), 2. {_rc_h.get('captain_2','')} (2.5×), 3. {_rc_h.get('captain_3','')} (2.0×)")
                    else:
                        st.info(f"Huidige keuze: {_rc_h.get('captain_1','')} (2.0×)")

                _is_gestart_cap = bool(_deadline_cap_dt and datetime.now(_AMS) >= _deadline_cap_dt)
                if _is_gestart_cap:
                    st.warning(f"⚠️ De deadline voor etappe {_et_cap} is verstreken ({_deadline_cap_str}). Captains kunnen niet meer worden gewijzigd.")
                else:
                    if _deadline_cap_str:
                        _cap_type_label = "Super etappe – 3 captains (3.0× / 2.5× / 2.0×)" if _is_super_cap else "Etappe – 1 captain (2.0×)"
                        st.caption(f"Deadline: {_deadline_cap_str}   •   {_cap_type_label}")
                    _mr_cap_rows = _pr_df_all_ronde[_pr_df_all_ronde['speler_naam'] == _naam_cap]
                    if 'tot_datum' in _mr_cap_rows.columns:
                        _mr_cap = _mr_cap_rows[
                            _mr_cap_rows['tot_datum'].astype(str).str.strip() == ''
                        ]['renner_naam'].tolist()
                    else:
                        _mr_cap = _mr_cap_rows['renner_naam'].tolist()
                    if not _mr_cap:
                        st.info("Je hebt nog geen ploeg opgeslagen. Ga naar het Ploeg tabblad.")
                    else:
                        def _verrijk_cap(renner):
                            if '_starter' in _r_race.columns:
                                _rs = _r_race[_r_race['renner'] == renner]
                                if not _rs.empty:
                                    return f"✅ {renner}" if _rs.iloc[0]['_starter'] else f"○ {renner}"
                            return renner
                        _mr_cap_v = [_verrijk_cap(r) for r in sorted(_mr_cap)]
                        _mr_cap_sorted = sorted(_mr_cap_v, key=lambda x: (0 if x.startswith("✅") else 1, x))
                        st.caption("✅ = bevestigd op startlijst   ○ = niet bevestigd")

                        if _is_super_cap:
                            _c1_v = st.selectbox("Kies Captain 1 (3.0×):", _mr_cap_sorted, key=f"cap1_{_spel_param}_{_et_cap}")
                            _c2_v = st.selectbox("Kies Captain 2 (2.5×):", [r for r in _mr_cap_sorted if r != _c1_v], key=f"cap2_{_spel_param}_{_et_cap}")
                            _c3_v = st.selectbox("Kies Captain 3 (2.0×):", [r for r in _mr_cap_sorted if r not in [_c1_v, _c2_v]], key=f"cap3_{_spel_param}_{_et_cap}")
                        else:
                            _c1_v = st.selectbox("Kies Captain (2.0×):", _mr_cap_sorted, key=f"cap1_{_spel_param}_{_et_cap}")
                            _c2_v = ""
                            _c3_v = ""

                        def _strip_cap(s):
                            return s.replace("✅ ", "").replace("○ ", "")

                        if st.button("Captain Opslaan", key=f"cap_save_{_spel_param}_{_et_cap}"):
                            _c1_s = _strip_cap(_c1_v)
                            _c2_s = _strip_cap(_c2_v) if _is_super_cap else ""
                            _c3_s = _strip_cap(_c3_v) if _is_super_cap else ""
                            _new_cap = pd.DataFrame([{
                                "speler_naam": _naam_cap, "ronde": _spel_param, "etappe": str(_et_cap),
                                "captain_1": _c1_s, "captain_2": _c2_s, "captain_3": _c3_s
                            }])
                            try:
                                try:
                                    _ws_cap = sh.worksheet("keuzes_rondes")
                                    _cap_vals = _ws_cap.get_all_values()
                                    if len(_cap_vals) > 1:
                                        _cap_hdrs = [str(h).strip().lower() for h in _cap_vals[0]]
                                        _cap_df = pd.DataFrame(_cap_vals[1:], columns=_cap_hdrs)
                                    else:
                                        _cap_df = pd.DataFrame(columns=["speler_naam", "ronde", "etappe", "captain_1", "captain_2", "captain_3"])
                                except gspread.exceptions.WorksheetNotFound:
                                    _ws_cap = sh.add_worksheet("keuzes_rondes", rows=2000, cols=6)
                                    _cap_df = pd.DataFrame(columns=["speler_naam", "ronde", "etappe", "captain_1", "captain_2", "captain_3"])
                                _cap_hdrs_out = ["speler_naam", "ronde", "etappe", "captain_1", "captain_2", "captain_3"]
                                for _ch in _cap_hdrs_out:
                                    if _ch not in _cap_df.columns:
                                        _cap_df[_ch] = ""
                                _masker_cap = (
                                    (_cap_df['speler_naam'] == _naam_cap) &
                                    (_cap_df['ronde'] == _spel_param) &
                                    (_cap_df['etappe'].astype(str) == str(_et_cap))
                                )
                                _cap_df = _cap_df[~_masker_cap]
                                _cap_df = pd.concat([_cap_df[_cap_hdrs_out], _new_cap], ignore_index=True)
                                _ws_cap.clear()
                                _ws_cap.update([_cap_hdrs_out] + _cap_df.fillna("").values.tolist())
                                st.cache_data.clear()
                                st.success(f"Captains opgeslagen voor etappe {_et_cap}!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as _ec_err:
                                st.error(f"Fout bij opslaan: {_ec_err}")

    with tab_beheer:
        st.markdown(f'<h1>{_flag_img_lg}{_naam} – Beheer</h1>', unsafe_allow_html=True)
        _beh_pw = st.text_input("Voer het admin-wachtwoord in:", type="password", key=f"beh_pw_{_spel_param}")
        if ADMIN_PASSWORD and _beh_pw == ADMIN_PASSWORD:
            st.success("Wachtwoord correct.")
            _etappes_df = read_sheet("etappes_rondes")
            if _etappes_df.empty:
                st.warning("Geen gegevens gevonden in de 'etappes_rondes' sheet.")
            else:
                # Normalize column names
                _etappes_df.columns = [c.strip().lower() for c in _etappes_df.columns]
                # Filter by 'ronde' column (giro/tour/vuelta)
                if 'ronde' in _etappes_df.columns:
                    _etappes_df = _etappes_df[_etappes_df['ronde'].str.strip().str.lower() == _spel_param]
                elif 'spel' in _etappes_df.columns:
                    _etappes_df = _etappes_df[_etappes_df['spel'].str.strip().str.lower() == _spel_param]

                st.subheader("📋 Etappes")
                st.dataframe(_etappes_df, use_container_width=True)

                # Etappe selectie
                _etappe_keuzes = _etappes_df['etappe'].dropna().tolist() if 'etappe' in _etappes_df.columns else []
                if not _etappe_keuzes:
                    st.info("Geen etappes beschikbaar.")
                else:
                    _gekozen_etappe = st.selectbox("Kies etappe:", _etappe_keuzes, key=f"etappe_sel_{_spel_param}")
                    _etappe_row = _etappes_df[_etappes_df['etappe'].astype(str) == str(_gekozen_etappe)].iloc[0]

                    _URL_TYPES = [
                        ("url_etappe", "🏁 Etappe"),
                        ("url_gc",     "🏆 GC"),
                        ("url_points", "💚 Punten"),
                        ("url_kom",    "🔴 KOM"),
                        ("url_youth",  "⬜ Jongeren"),
                    ]

                    st.subheader(f"Etappe {_gekozen_etappe} – URLs")
                    _available = [(key, label, str(_etappe_row.get(key, "")).strip())
                                  for key, label in _URL_TYPES
                                  if key in _etappe_row.index and str(_etappe_row.get(key, "")).strip()]

                    if not _available:
                        st.info("Geen URLs geconfigureerd voor deze etappe.")
                    else:
                        for _url_key, _url_label, _url_val in _available:
                            st.markdown(f"**{_url_label}**: `{_url_val}`")

                        st.divider()

                        # Individual scrape buttons
                        _url_etappe_val = next((v for k, _, v in _available if k == "url_etappe"), "")
                        for _url_key, _url_label, _url_val in _available:
                            _type_key = _url_key.replace("url_", "")
                            _sc_limit = None if _type_key == "etappe" else 10
                            if st.button(f"Scrape {_url_label}", key=f"scrape_{_spel_param}_{_gekozen_etappe}_{_url_key}"):
                                with st.spinner(f"Scrapen van {_url_label}..."):
                                    _ok, _result = scrape_pcs_resultaat(_url_val, limit=_sc_limit)
                                if _ok:
                                    _sv_ok, _sv_msg = save_ronde_uitslagen(_spel_param, _gekozen_etappe, _type_key, _result)
                                    if _sv_ok:
                                        st.success(f"✅ {_url_label}: {_sv_msg}")
                                    else:
                                        st.error(f"Opslaan mislukt: {_sv_msg}")
                                else:
                                    st.error(f"Scrapen mislukt: {_result}")

                        if _url_etappe_val:
                            if st.button("🟠 Scrape oranje schildjes", key=f"scrape_schild_{_spel_param}_{_gekozen_etappe}"):
                                with st.spinner("Scrapen van oranje schildjes..."):
                                    _sh_ok, _sh_result = scrape_pcs_oranje_schildjes(_url_etappe_val)
                                if _sh_ok:
                                    _sv_ok, _sv_msg = save_ronde_uitslagen(_spel_param, _gekozen_etappe, "schildjes", _sh_result)
                                    if _sv_ok:
                                        st.success(f"✅ {_sv_msg}")
                                        st.dataframe(_sh_result, use_container_width=True)
                                    else:
                                        st.error(f"Opslaan mislukt: {_sv_msg}")
                                else:
                                    st.error(f"Scrapen mislukt: {_sh_result}")

                        st.divider()
                        # Scrape all button (inclusief oranje schildjes)
                        if st.button(f"🔄 Scrape alle URLs (etappe {_gekozen_etappe})", key=f"scrape_all_{_spel_param}_{_gekozen_etappe}"):
                            _all_ok = True
                            for _url_key, _url_label, _url_val in _available:
                                _type_key = _url_key.replace("url_", "")
                                _sc_limit = None if _type_key == "etappe" else 10
                                with st.spinner(f"Scrapen van {_url_label}..."):
                                    _ok, _result = scrape_pcs_resultaat(_url_val, limit=_sc_limit)
                                if _ok:
                                    _sv_ok, _sv_msg = save_ronde_uitslagen(_spel_param, _gekozen_etappe, _type_key, _result)
                                    if _sv_ok:
                                        st.success(f"✅ {_url_label}: {_sv_msg}")
                                    else:
                                        st.error(f"❌ {_url_label} opslaan mislukt: {_sv_msg}")
                                        _all_ok = False
                                else:
                                    st.error(f"❌ {_url_label} scrapen mislukt: {_result}")
                                    _all_ok = False
                            if _url_etappe_val:
                                with st.spinner("Scrapen van oranje schildjes..."):
                                    _sh_ok, _sh_result = scrape_pcs_oranje_schildjes(_url_etappe_val)
                                if _sh_ok:
                                    _sv_ok, _sv_msg = save_ronde_uitslagen(_spel_param, _gekozen_etappe, "schildjes", _sh_result)
                                    if _sv_ok:
                                        st.success(f"✅ Oranje schildjes: {_sv_msg}")
                                    else:
                                        st.error(f"❌ Oranje schildjes opslaan mislukt: {_sv_msg}")
                                        _all_ok = False
                                else:
                                    st.error(f"❌ Oranje schildjes scrapen mislukt: {_sh_result}")
                                    _all_ok = False
                            if _all_ok:
                                st.balloons()

                        st.divider()

                        with st.expander("🔍 Debug: bekijk icon-attributen van eerste rijen"):
                            if _url_etappe_val:
                                if st.button("Haal HTML op", key=f"debug_html_{_spel_param}_{_gekozen_etappe}"):
                                    with st.spinner("HTML ophalen..."):
                                        _db_ok, _db_rows = debug_pcs_row_html(_url_etappe_val, max_rows=5)
                                    if _db_ok:
                                        for _i_db, _row_data in enumerate(_db_rows):
                                            st.markdown(f"**Rij {_i_db + 1}:**")
                                            if _row_data['icons']:
                                                st.write("Icon-elementen en hun attributen:")
                                                for _ic in _row_data['icons']:
                                                    st.code(_ic)
                                            else:
                                                st.write("_(geen icon-elementen gevonden in renner-cel)_")
                                            with st.expander(f"Volledige HTML rij {_i_db + 1}"):
                                                st.code(_row_data['html'], language="html")
                                    else:
                                        st.error(_db_rows)
                            else:
                                st.info("Geen etappe-URL geconfigureerd.")

                        with st.expander("🔍 Debug: klassement tabel HTML (GC/punten/KOM/jongeren)"):
                            _cl_url_options = [(k, lbl, v) for k, lbl, v in _available if k != "url_etappe"]
                            if not _cl_url_options:
                                st.info("Geen klassement-URLs beschikbaar.")
                            else:
                                _cl_sel = st.selectbox(
                                    "Kies klassement:",
                                    options=[k for k, _, _ in _cl_url_options],
                                    format_func=lambda k: next(lbl for ck, lbl, _ in _cl_url_options if ck == k),
                                    key=f"cl_debug_sel_{_spel_param}_{_gekozen_etappe}"
                                )
                                _cl_url_val = next(v for k, _, v in _cl_url_options if k == _cl_sel)
                                st.code(_cl_url_val)
                                if st.button("Haal klassement HTML op", key=f"cl_debug_btn_{_spel_param}_{_gekozen_etappe}"):
                                    with st.spinner("HTML ophalen..."):
                                        try:
                                            _cl_resp = _pcs_get(_cl_url_val.rstrip('/') + '/')
                                            _cl_soup = BeautifulSoup(_cl_resp.text, 'html.parser')
                                            _cl_tables = _cl_soup.find_all('table', class_=lambda c: c and 'results' in c)
                                            st.write(f"**Aantal 'results' tabellen gevonden:** {len(_cl_tables)}")
                                            _cl_url_lower = _cl_url_val.rstrip('/').lower()
                                            _cl_is_class = any(_cl_url_lower.endswith(s) for s in ('-gc', '-points', '-kom', '-youth'))
                                            st.write(f"**Herkend als klassement-URL:** {_cl_is_class}")
                                            if _cl_tables:
                                                def _cl_rider_count(t):
                                                    return sum(1 for a in t.find_all('a', href=True) if 'rider/' in a['href'])
                                                st.write("**Alle results-tabellen (heading | class | rider-links):**")
                                                for _ci, _ct in enumerate(_cl_tables):
                                                    _cc = _cl_rider_count(_ct)
                                                    _prev_h = _ct.find_previous(['h1','h2','h3','h4'])
                                                    _h_txt = _prev_h.get_text().strip() if _prev_h else '(geen heading)'
                                                    st.write(f"  Tabel {_ci+1}: heading=`{_h_txt}` | class=`{_ct.get('class')}` | {_cc} rider-links")
                                                _cl_suffix = next((s for s in ('gc','points','kom','youth') if _cl_url_lower.endswith('-'+s)), None)
                                                # Replicate selection logic
                                                if _cl_suffix in ('gc', 'points'):
                                                    _cl_idx2 = {'gc':1,'points':2}[_cl_suffix]
                                                    _cl_tbl = _cl_tables[_cl_idx2] if _cl_idx2 < len(_cl_tables) else None
                                                    if _cl_tbl:
                                                        st.success(f"Vaste positie index {_cl_idx2} voor '{_cl_suffix}'")
                                                else:
                                                    _cl_youth_i = None
                                                    for _cli2, _ct2 in enumerate(_cl_tables):
                                                        _ph2 = _ct2.find_previous(['h1','h2','h3','h4'])
                                                        if _ph2 and 'youth' in _ph2.get_text().lower():
                                                            _cl_youth_i = _cli2
                                                            break
                                                    st.write(f"Youth tabel positie: {_cl_youth_i+1 if _cl_youth_i is not None else 'niet gevonden'}")
                                                    if _cl_suffix == 'youth':
                                                        _cl_tbl = _cl_tables[_cl_youth_i] if _cl_youth_i is not None else None
                                                    else:  # kom
                                                        _cl_tbl = _cl_tables[_cl_youth_i - 1] if _cl_youth_i and _cl_youth_i > 0 else None
                                                    if _cl_tbl:
                                                        st.success(f"Selecteert tabel voor '{_cl_suffix}'")
                                                if not _cl_tbl:
                                                    st.error(f"Geen tabel gevonden voor '{_cl_suffix}'")
                                                    st.stop()
                                                _cl_tbody = _cl_tbl.find('tbody') or _cl_tbl
                                                _cl_rows = _cl_tbody.find_all('tr')[:5]
                                                st.write(f"**Geselecteerde tabel class:** `{_cl_tbl.get('class')}`")
                                                st.write(f"**Aantal rijen in tbody:** {len(_cl_tbody.find_all('tr'))}")
                                                for _cli, _clr in enumerate(_cl_rows):
                                                    with st.expander(f"Rij {_cli + 1} HTML"):
                                                        st.code(str(_clr)[:2000], language="html")
                                            else:
                                                st.warning("Geen 'results' tabel gevonden. Alle tabellen op de pagina:")
                                                for _clt in _cl_soup.find_all('table'):
                                                    st.code(f"class={_clt.get('class')} | eerste 200 chars: {str(_clt)[:200]}", language="html")
                                        except Exception as _cl_e:
                                            st.error(str(_cl_e))

                    # ── Handmatige DNS/DNF invoer ─────────────────────────────
                    st.divider()
                    st.subheader("✍️ Handmatige DNS/DNF invoer")
                    st.caption("Voeg een DNS of DNF handmatig toe voor een renner. Overschrijft alleen de rij voor die renner in die etappe.")

                    _heeft_starters_beh = '_starter' in _r_race.columns and _r_race['_starter'].any() if not _r_race.empty else False
                    _man_renner_opties = sorted(
                        _r_race[_r_race['_starter']]['renner'].tolist()
                        if _heeft_starters_beh
                        else _r_race['renner'].tolist()
                    ) if not _r_race.empty else []
                    if not _man_renner_opties:
                        st.info("Geen renners beschikbaar (laad eerst de renners sheet).")
                    else:
                        _mc1, _mc2, _mc3 = st.columns(3)
                        with _mc1:
                            _man_renner = st.selectbox(
                                "Renner:",
                                _man_renner_opties,
                                key=f"man_renner_{_spel_param}",
                            )
                        with _mc2:
                            _man_etappe = st.selectbox(
                                "Etappe:",
                                _etappe_keuzes,
                                key=f"man_etappe_{_spel_param}",
                            )
                        with _mc3:
                            _man_rank = st.selectbox(
                                "Status:",
                                ["DNS", "DNF", "OTL", "DSQ"],
                                key=f"man_rank_{_spel_param}",
                            )

                        if st.button("💾 Opslaan", key=f"man_save_{_spel_param}"):
                            _man_team = ''
                            if not _r_race.empty and 'team' in _r_race.columns:
                                _rr_row = _r_race[_r_race['renner'] == _man_renner]
                                if not _rr_row.empty:
                                    _man_team = str(_rr_row.iloc[0].get('team', '')).strip()
                            _m_ok, _m_msg = add_manual_uitval_ronde(
                                _spel_param, _man_etappe, _man_renner, _man_rank, _man_team
                            )
                            if _m_ok:
                                st.success(f"✅ {_m_msg}")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"Fout bij opslaan: {_m_msg}")

        elif _beh_pw:
            st.error("Onjuist wachtwoord.")

    st.stop()

# ── KLASSIEKERSPEL ────────────────────────────────────────────────────────────
tab_klas, tab_uitslag, tab_startlijst, tab_matrix, tab_team, tab_wissels, tab_captains, tab_admin = st.tabs(PAGINA_OPTIES)

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
        laatste_koers = koersen_gehad[-1] if koersen_gehad else None

        with st.spinner('Klassement berekenen...'):
            for speler in sorted(s_all['speler_naam'].unique()):
                speler_rows = s_all[s_all['speler_naam'] == speler].copy()
                poule_val = speler_rows['subpoule'].iloc[0] if not speler_rows['subpoule'].empty else ""
                poule_lijst = [p.strip() for p in str(poule_val).split(",")] if poule_val else []

                cumulatief = 0
                laatste_score = 0
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
                    if k == laatste_koers:
                        laatste_score = int(koers_score)

                    koers_idx = koersen_gehad.index(k) + 1
                    koers_label = f"{koers_idx:02d}. {k}"
                    history_data.append({"Koers": koers_label, "Speler": speler, "Punten": int(cumulatief)})

                scores.append({"Deelnemer": speler, "Totaal": int(cumulatief), "Laatste": laatste_score, "Poules": poule_lijst})

        df_scores = pd.DataFrame(scores)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌍 Algemeen", "🥇 Kamer 1", "🥈 Sammeke", "📈 Verloop", "🏅 Eindwinnaars"])

        # Bereken vorige stand (op één na laatste koers) voor pijltjes
        def bereken_vorige_stand(history_data, koersen_gehad, spelers=None):
            if len(koersen_gehad) < 2:
                return {}
            # Puntentotaal tot en met één koers terug
            vorige_koers_label = f"{(len(koersen_gehad)-1):02d}. {koersen_gehad[-2]}"
            vorige = {}
            for entry in history_data:
                if entry['Koers'] == vorige_koers_label:
                    if spelers is None or entry['Speler'] in spelers:
                        vorige[entry['Speler']] = entry['Punten']
            if not vorige:
                return {}
            # Rangschik op vorige stand (alleen binnen de opgegeven spelers)
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

        # Functie voor compacte weergave zonder lege rijen, met trend kolom
        def display_compact_df(df, vorige_ranks):
            n_rijen = len(df)
            calc_height = TABLE_HEADER_HEIGHT + (n_rijen * TABLE_ROW_HEIGHT)

            df_show = df[['Deelnemer', 'Totaal']].copy().reset_index(drop=True)
            df_show.index += 1

            # Voeg laatste koers kolom in vóór Totaal
            col_config = {
                "Deelnemer": st.column_config.TextColumn("Deelnemer"),
                "Totaal": st.column_config.NumberColumn("Totaal", width="small", format="%d"),
            }
            if laatste_koers and 'Laatste' in df.columns:
                df_show.insert(len(df_show.columns) - 1, laatste_koers, df['Laatste'].values)
                col_config[laatste_koers] = st.column_config.NumberColumn(laatste_koers, width="small", format="%d")

            # Voeg trend kolom toe als er vorige stands zijn
            if vorige_ranks:
                df_show.insert(0, '↕', maak_trend_kolom(df_show, vorige_ranks))
                col_config["↕"] = st.column_config.TextColumn("↕", width=50)

            st.dataframe(
                df_show,
                column_config=col_config,
                hide_index=False,
                use_container_width=True,
                height=calc_height
            )

        with tab1:
            st.subheader("Algemeen Klassement")
            df_alg = df_scores.sort_values('Totaal', ascending=False).reset_index(drop=True)
            vorige_ranks_alg = bereken_vorige_stand(history_data, koersen_gehad)
            display_compact_df(df_alg, vorige_ranks_alg)

        def toon_poule_tabel(poule_naam):
            mask = df_scores['Poules'].apply(lambda x: poule_naam in x)
            df_p = df_scores[mask].sort_values('Totaal', ascending=False).reset_index(drop=True)
            if not df_p.empty:
                spelers_in_poule = set(df_p['Deelnemer'])
                vorige_ranks_poule = bereken_vorige_stand(history_data, koersen_gehad, spelers=spelers_in_poule)
                display_compact_df(df_p, vorige_ranks_poule)
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

        with tab5:
            try:
                sh_fresh = gc.open_by_url(SPREADSHEET_URL)
                ws_w = None
                for ws in sh_fresh.worksheets():
                    if ws.title.strip().lower() == "eindwinnaars":
                        ws_w = ws
                        break
                if ws_w is None:
                    beschikbaar = [ws.title for ws in sh_fresh.worksheets()]
                    st.error(f"Tabblad 'Eindwinnaars' niet gevonden. Beschikbaar: {beschikbaar}")
                else:
                    rows = ws_w.get_all_values()
                    if len(rows) < 2:
                        st.info("Geen historische winnaars gevonden.")
                    else:
                        headers = [c.strip() for c in rows[0]]
                        df_winnaars = pd.DataFrame(rows[1:], columns=headers)
                        df_winnaars = df_winnaars.replace('', '-')
                        st.dataframe(df_winnaars, hide_index=True, use_container_width=True)
            except Exception as e:
                st.error(f"Fout bij laden van eindwinnaars: {e}")

# =============================================
# 2. UITSLAG PER KOERS
# =============================================
with tab_uitslag:
    st.title("🏁 Koersuitslag & Puntenverdeling")
    if u_all.empty:
        st.info("Nog geen uitslagen beschikbaar. Scrape ze eerst via de Beheer pagina.")
    elif not u_all.empty:
        volgorde = koersen_volgorde
        koers_opties = [k for k in volgorde if k in u_all['koers_naam'].unique()]
        _ul = koers_opties if koers_opties else list(u_all['koers_naam'].unique())
        koers = st.selectbox("Selecteer een koers:", _ul, index=get_standaard_koers_index(_ul))
        
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
            punten_height = TABLE_HEADER_HEIGHT + (n_punten * 38)
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
        # Koers dropdown - gebruik volgorde uit koersen sheet
        volgorde_sl = koersen_volgorde
        beschikbare_koersen_sl = sl_all['koers_naam'].unique().tolist()
        koersen_sl_gesorteerd = [k for k in volgorde_sl if k in beschikbare_koersen_sl]
        # Voeg koersen toe die niet in de volgorde staan (vangnet)
        koersen_sl_gesorteerd += [k for k in beschikbare_koersen_sl if k not in koersen_sl_gesorteerd]

        if not koersen_sl_gesorteerd:
            st.info("Geen koersen gevonden in de startlijsten database.")
        else:
            gekozen_koers = st.selectbox("Selecteer een koers:", koersen_sl_gesorteerd, index=get_volgende_koers_index(koersen_sl_gesorteerd), key="sl_koers_view")

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
        spelers_m = sorted(s_all['speler_naam'].unique())
        default_m = spelers_m.index(ingelogd_speler) if ingelogd_speler in spelers_m else 0
        speler = st.selectbox("Selecteer Deelnemer", spelers_m, index=default_m)
        
        volgorde = koersen_volgorde
        beschikbare_koersen = u_all['koers_naam'].unique()
        koersen = [k for k in volgorde if k in beschikbare_koersen]
        
        # Bepaal display_date: laatste verlopen race-deadline
        _nu_mx = datetime.now(_AMS)
        _verstreken_mx = [
            datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
            for k in KOERS_DATA
            if datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS) <= _nu_mx
        ]
        _display_date_mx = pd.to_datetime(max(_verstreken_mx).date()) if _verstreken_mx else pd.to_datetime("2000-01-01")

        # Haal renners op: uitgaande altijd, inkomende pas na display_date
        mijn_renners_df = s_all[s_all['speler_naam'] == speler]
        mijn_renners_df = mijn_renners_df[
            pd.to_datetime(mijn_renners_df['vanaf_datum'], errors='coerce') <= _display_date_mx
        ]
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
        matrix_height = TABLE_HEADER_HEIGHT + (n_matrix_rows * 38)
        st.dataframe(
            df_matrix.style.map(style_matrix),
            use_container_width=True,
            height=matrix_height
        )

# =============================================
# 4. MIJN TEAM
# =============================================
with tab_team:
    st.title("🚌 Mijn Team Overzicht")
    if not s_all.empty:
        spelers = sorted(s_all['speler_naam'].unique())
        default_idx = spelers.index(ingelogd_speler) if ingelogd_speler in spelers else 0
        speler = st.selectbox("Naam:", spelers, index=default_idx)

        # Bepaal weergave-datum: team zoals het was op het moment van de
        # laatste verlopen race-deadline. Zo worden wissel-renners pas
        # zichtbaar nadat de deadline van die koers is verstreken.
        _nu_team = datetime.now(_AMS)
        _verstreken = [
            datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
            for k in KOERS_DATA
            if datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS) <= _nu_team
        ]
        if _verstreken:
            _display_date = pd.to_datetime(max(_verstreken).date())
        else:
            _display_date = pd.to_datetime("2000-01-01")  # vóór eerste race: toon alles

        # Filter actieve renners op weergave-datum:
        # - Uitgaande renners (tot_datum gezet): altijd zichtbaar (historische punten)
        # - Inkomende renners (vanaf_datum in toekomst): pas na display_date
        _speler_rows_t = s_all[s_all['speler_naam'] == speler].copy()
        _mask_t = (pd.to_datetime(_speler_rows_t['vanaf_datum'], errors='coerce') <= _display_date)
        mr = _speler_rows_t[_mask_t]['renner_naam'].tolist()
        
        r_data = []
        with st.spinner('Punten berekenen...'):
            koersen_met_uitslag = u_all['koers_naam'].unique() if not u_all.empty else []
            for r in mr:
                score = sum(int(bereken_volledige_score(speler, k, u_all, k_all, [r])[0]) for k in koersen_met_uitslag)
                r_data.append({"Renner": r, "Totaal Punten": score})
        
        # Maak DataFrame en sorteer
        df_mijn_team = pd.DataFrame(r_data).sort_values("Totaal Punten", ascending=False)

        # Weergave met aangepaste kolombreedte en tabelhoogte
        n_renners = len(df_mijn_team)
        team_height = TABLE_HEADER_HEIGHT + (n_renners * TABLE_ROW_HEIGHT)
        st.dataframe(
            df_mijn_team,
            column_config={
                "Renner": st.column_config.TextColumn("Renner"),
                "Totaal Punten": st.column_config.NumberColumn("Totaal Punten", width="small", format="%d"),
            },
            hide_index=True,
            use_container_width=True,
            height=team_height
        )
        

# =============================================
# 5. WISSELS
# =============================================
with tab_wissels:
    st.title("🔄 Wissels")

    WISSEL_START    = pd.to_datetime("2026-04-16")   # dag voor deadline Brabantse Pijl
    MAX_WISSELS     = 5
    CAT_TOPPER      = "max5 topper"
    CAT_SUBTOPPER   = "max5 subtopper"
    CAT_RENNER      = "min3 renner"

    renners_db = read_sheet("renners")   # kolommen: renner, land, team, categorie

    # Auto-detect naamkolom (sheet kan 'naam', 'renner', 'name' etc. hebben)
    if not renners_db.empty:
        _naam_kandidaten = ['renner', 'naam', 'name', 'rider', 'renner_naam']
        _naam_col_r = next((c for c in _naam_kandidaten if c in renners_db.columns),
                           renners_db.columns[0])
        if _naam_col_r != 'renner':
            renners_db = renners_db.rename(columns={_naam_col_r: 'renner'})
        # Genormaliseerde key voor accent-insensitieve matching
        import unicodedata as _ud
        def _norm_naam(s):
            s = str(s).strip().lower()
            return ''.join(c for c in _ud.normalize('NFKD', s) if not _ud.combining(c))
        renners_db['_key'] = renners_db['renner'].map(_norm_naam)
        # Bouw lookup dict: genorm. naam → rij-metadata
        _r_lookup = {row['_key']: row for _, row in renners_db.iterrows()}
        def _meta(naam):
            row = _r_lookup.get(_norm_naam(naam))
            if row is not None:
                return str(row.get('team','?')), str(row.get('land','?')), str(row.get('categorie','?')).lower()
            return '?', '?', '?'

    if s_all.empty or renners_db.empty:
        st.info("Data niet beschikbaar.")
    else:
        nu_w = datetime.now(_AMS)
        today_w = pd.to_datetime(nu_w.date())
        # Wissels zijn nu al zichtbaar maar gaan pas in op WISSEL_START
        wissel_datum = max(today_w, WISSEL_START).strftime("%Y-%m-%d")

        naam_w = ingelogd_speler
        speler_rows_w = s_all[s_all['speler_naam'] == naam_w].copy()

        # --- Actief team vandaag ---
        mask_actief = (
            (pd.to_datetime(speler_rows_w['vanaf_datum'], errors='coerce') <= today_w) &
            (
                speler_rows_w['tot_datum'].isna() |
                (speler_rows_w['tot_datum'] == "") |
                (pd.to_datetime(speler_rows_w['tot_datum'], errors='coerce') > today_w)
            )
        )
        actief_team = speler_rows_w[mask_actief]['renner_naam'].tolist()

        # --- Wissels gebruikt ---
        mask_wissel_out = (
            speler_rows_w['tot_datum'].notna() &
            (speler_rows_w['tot_datum'] != "") &
            (pd.to_datetime(speler_rows_w['tot_datum'], errors='coerce') >= WISSEL_START)
        )
        wissels_gebruikt = int(mask_wissel_out.sum())
        wissels_over     = MAX_WISSELS - wissels_gebruikt

        # --- Team-regel validatie ---
        def check_regels(team_namen):
            rows = [{'team': t, 'land': l, 'categorie': c}
                    for naam in team_namen for t, l, c in [_meta(naam)]]
            info = pd.DataFrame(rows)
            fouten = []
            if len(team_namen) > 25:
                fouten.append(f"Max 25 renners — huidig: {len(team_namen)}")
            for ploeg, cnt in info['team'].value_counts().items():
                if cnt > 2 and ploeg != '?':
                    fouten.append(f"Max 2 per ploeg — {ploeg}: {cnt}")
            for land, cnt in info['land'].value_counts().items():
                if cnt > 5 and land != '?':
                    fouten.append(f"Max 5 per land — {land}: {cnt}")
            cat_counts = info['categorie'].value_counts()
            if cat_counts.get(CAT_TOPPER, 0) > 5:
                fouten.append(f"Max 5 {CAT_TOPPER} — huidig: {cat_counts.get(CAT_TOPPER, 0)}")
            if cat_counts.get(CAT_SUBTOPPER, 0) > 5:
                fouten.append(f"Max 5 {CAT_SUBTOPPER} — huidig: {cat_counts.get(CAT_SUBTOPPER, 0)}")
            if cat_counts.get(CAT_RENNER, 0) < 3:
                fouten.append(f"Min 3 {CAT_RENNER} — huidig: {cat_counts.get(CAT_RENNER, 0)}")
            return fouten

        # --- Huidig team weergeven ---
        st.subheader(f"Huidig team — {len(actief_team)} renners")
        col_budget, col_used = st.columns(2)
        col_budget.metric("Wissels over", f"{wissels_over} / {MAX_WISSELS}")

        team_info_df = pd.DataFrame([
            {'renner': naam, 'team': t, 'land': l, 'categorie': c}
            for naam in actief_team for t, l, c in [_meta(naam)]
        ])
        team_info_df = team_info_df.sort_values('categorie').reset_index(drop=True)
        team_info_df.index += 1
        st.dataframe(
            team_info_df,
            use_container_width=True,
            height=TABLE_HEADER_HEIGHT + len(team_info_df) * TABLE_ROW_HEIGHT,
            hide_index=False,
        )

        # Huidige regelcheck tonen
        huidige_fouten = check_regels(actief_team)
        if huidige_fouten:
            with st.expander("⚠️ Huidige team-regelovertredingen"):
                for f in huidige_fouten:
                    st.warning(f)

        st.divider()

        if wissels_over <= 0:
            st.warning("Je hebt alle 5 wissels al gebruikt.")
        else:
            st.subheader("Wissel doorvoeren")
            if today_w < WISSEL_START:
                st.info(f"ℹ️ Je wissels gaan in op {WISSEL_START.strftime('%d-%m-%Y')} (deadline Brabantse Pijl). Je kunt ze alvast klaarzetten.")
            n_w = st.number_input(
                f"Hoeveel wissels wil je nu doorvoeren? (max {wissels_over})",
                min_value=1, max_value=wissels_over, value=1, step=1, key="n_wissels"
            )

            actief_keys = {_norm_naam(r) for r in actief_team}
            beschikbaar = sorted([
                r for r in renners_db['renner'].tolist()
                if _norm_naam(r) not in actief_keys
            ])

            uit_keuzes = []
            in_keuzes  = []

            for i in range(int(n_w)):
                st.markdown(f"**Wissel {i+1}**")
                c1, c2 = st.columns(2)
                with c1:
                    opties_uit = [r for r in actief_team if r not in uit_keuzes]
                    uit = st.selectbox(f"Eruit:", opties_uit, key=f"uit_{i}")
                    uit_keuzes.append(uit)
                with c2:
                    opties_in = [r for r in beschikbaar if r not in in_keuzes]
                    inn = st.selectbox(f"Erin:", opties_in, key=f"in_{i}")
                    in_keuzes.append(inn)

            # Preview nieuw team
            nieuw_team = [r for r in actief_team if r not in uit_keuzes] + in_keuzes
            fouten_nieuw = check_regels(nieuw_team)

            st.markdown("**Preview nieuw team na wissel:**")
            nieuw_info = pd.DataFrame([
                {'renner': naam, 'team': t, 'land': l, 'categorie': c}
                for naam in nieuw_team for t, l, c in [_meta(naam)]
            ])
            cat_c  = nieuw_info['categorie'].value_counts()
            land_c = nieuw_info['land'].value_counts()
            ploeg_c = nieuw_info[nieuw_info['team'] != '?']['team'].value_counts()
            m1, m2, m3, m4, m5, m6 = st.columns(6)
            m1.metric("Totaal", len(nieuw_team))
            m2.metric("Toppers", f"{cat_c.get(CAT_TOPPER,0)}/5")
            m3.metric("Subtoppers", f"{cat_c.get(CAT_SUBTOPPER,0)}/5")
            m4.metric("Renners", f"{cat_c.get(CAT_RENNER,0)} (min 3)")
            m5.metric("Max land", f"{land_c[land_c.index != '?'].max() if not land_c.empty else 0}/5")
            m6.metric("Max ploeg", f"{ploeg_c.max() if not ploeg_c.empty else 0}/2")

            if fouten_nieuw:
                for f in fouten_nieuw:
                    st.error(f"❌ {f}")
            else:
                st.success("✅ Nieuw team voldoet aan alle regels")

            if st.button("✅ Bevestig wissels opslaan", disabled=bool(fouten_nieuw)):
                s_updated = s_all.copy()

                # Zet tot_datum voor uitgaande renners
                for r_uit in uit_keuzes:
                    idx = s_updated[
                        (s_updated['speler_naam'] == naam_w) &
                        (s_updated['renner_naam'] == r_uit) &
                        (s_updated['tot_datum'].isna() | (s_updated['tot_datum'] == ""))
                    ].index
                    s_updated.loc[idx, 'tot_datum'] = wissel_datum

                # Voeg inkomende renners toe
                pin_val      = speler_rows_w['pincode'].iloc[0]
                subpoule_val = speler_rows_w['subpoule'].iloc[0] if 'subpoule' in speler_rows_w.columns else ""
                email_val    = speler_rows_w['email'].iloc[0] if 'email' in speler_rows_w.columns else ""

                for r_in in in_keuzes:
                    new_row = pd.DataFrame([{
                        'speler_naam': naam_w,
                        'renner_naam': r_in,
                        'pincode':     pin_val,
                        'subpoule':    subpoule_val,
                        'email':       email_val,
                        'vanaf_datum': wissel_datum,
                        'tot_datum':   ""
                    }])
                    s_updated = pd.concat([s_updated, new_row], ignore_index=True)

                # Schrijf terug naar sheet
                cols_s = ['speler_naam', 'renner_naam', 'pincode', 'subpoule', 'email', 'vanaf_datum', 'tot_datum']
                ws_s = sh.worksheet("speler_teams")
                ws_s.clear()
                ws_s.update([cols_s] + s_updated[cols_s].fillna("").values.tolist())
                st.cache_data.clear()
                st.success(f"Wissels opgeslagen! {', '.join(uit_keuzes)} → {', '.join(in_keuzes)}")
                time.sleep(1)
                st.rerun()

# =============================================
# 6. CAPTAINS KIEZEN
# =============================================
with tab_captains:
    st.title("©️ Captains Beheer")

    if not s_all.empty:

        # --- PUBLIEK OVERZICHT (geen login vereist) ---
        st.subheader("📋 Overzicht Captains")
        nu_ov = datetime.now(_AMS)
        alle_koersen_ov = list(KOERS_DATA.keys())
        spelers_ov = sorted(s_all['speler_naam'].unique())

        gestart = [k for k in alle_koersen_ov if datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS) <= nu_ov]
        toekomst = [k for k in alle_koersen_ov if datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS) > nu_ov]
        laatste_gestart = gestart[-1] if gestart else None
        toon_koersen = ([laatste_gestart] if laatste_gestart else []) + toekomst

        # Bouw HTML tabel
        th_style = "padding:6px 10px;background:#1a2e4a;color:white;font-size:12px;text-align:center;white-space:nowrap;"
        td_speler = "padding:6px 10px;font-size:13px;font-weight:600;white-space:nowrap;background:white;border-bottom:1px solid #e2e8f0;"
        td_base = "padding:6px 10px;font-size:13px;text-align:center;background:white;border-bottom:1px solid #e2e8f0;"

        html = f'<table style="width:100%;border-collapse:collapse;background:white;"><thead><tr><th style="{th_style}text-align:left;">Speler</th>'
        for koers in toon_koersen:
            html += f'<th style="{th_style}">{koers}</th>'
        html += "</tr></thead><tbody>"

        for speler in spelers_ov:
            html += f'<tr><td style="{td_speler}">{speler}</td>'
            for koers in toon_koersen:
                start_dt = datetime.strptime(KOERS_DATA[koers], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
                keuze = k_all[(k_all['speler_naam'] == speler) & (k_all['koers_naam'] == koers)]
                heeft_keuze = not keuze.empty and str(keuze.iloc[0]['captain_1']).strip() != ""
                if start_dt <= nu_ov:
                    if heeft_keuze:
                        r = keuze.iloc[0]
                        cel = f"{r['captain_1']}, {r['captain_2']}, {r['captain_3']}"
                    else:
                        cel = "—"
                    html += f'<td style="{td_base}">{cel}</td>'
                else:
                    if heeft_keuze:
                        html += f'<td style="{td_base}color:green;font-weight:bold;font-size:16px;">✓</td>'
                    else:
                        html += f'<td style="{td_base}color:red;font-weight:bold;font-size:16px;">✗</td>'
            html += "</tr>"
        html += "</tbody></table>"

        st.markdown(html, unsafe_allow_html=True)

        st.divider()
        naam = ingelogd_speler

        # --- SECTIE 1: CAPTAINS INSTELLEN ---
        st.subheader("📝 Captains Instellen")
        _captain_koersen = list(KOERS_DATA.keys())
        koers_keuze = st.selectbox("Voor welke koers?", _captain_koersen, index=get_volgende_koers_index(_captain_koersen))

        # Check of koers al gestart is
        deadline_str = KOERS_DATA[koers_keuze]
        deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
        is_gestart = datetime.now(_AMS) >= deadline_dt

        huidige_keuze = k_all[(k_all['speler_naam'] == naam) & (k_all['koers_naam'] == koers_keuze)]
        if not huidige_keuze.empty:
            st.info(f"Huidige keuze voor {koers_keuze}: 1. {huidige_keuze.iloc[0]['captain_1']}, 2. {huidige_keuze.iloc[0]['captain_2']}, 3. {huidige_keuze.iloc[0]['captain_3']}")

        if is_gestart:
            st.warning(f"⚠️ De deadline voor {koers_keuze} is verstreken ({deadline_str}). Je kunt je captains niet meer wijzigen.")
        else:
            # Alleen renners die actief zijn op de datum van deze koers
            koers_datum_cap = pd.to_datetime(deadline_str.split(" ")[0])
            _rows_cap = s_all[s_all['speler_naam'] == naam].copy()
            _mask_cap = (
                (pd.to_datetime(_rows_cap['vanaf_datum'], errors='coerce') <= koers_datum_cap) &
                (
                    _rows_cap['tot_datum'].isna() |
                    (_rows_cap['tot_datum'] == "") |
                    (pd.to_datetime(_rows_cap['tot_datum'], errors='coerce') > koers_datum_cap)
                )
            )
            mr = sorted(_rows_cap[_mask_cap]['renner_naam'].tolist())

            # Haal startlijst op voor deze koers
            sl_data = read_sheet("startlijsten")
            if not sl_data.empty:
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
            def strip_prefix(s):
                return s.replace("✅ ", "").replace("○ ", "")

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
                st.dataframe(mijn_tabel[['koers_naam', 'captain_1', 'captain_2', 'captain_3']], hide_index=True, use_container_width=True, height=TABLE_HEADER_HEIGHT + len(mijn_tabel) * TABLE_ROW_HEIGHT)
            else:
                st.info("Je hebt nog geen captains ingesteld.")

        with tab_alle:
            _alle_koersen = list(KOERS_DATA.keys())
            bekijk_koers = st.selectbox("Bekijk captains voor:", _alle_koersen, index=get_volgende_koers_index(_alle_koersen), key="view_others")
            nu = datetime.now(_AMS)
            start_tijd = datetime.strptime(KOERS_DATA[bekijk_koers], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)

            if nu < start_tijd:
                st.info(f"🤫 De captains voor **{bekijk_koers}** blijven geheim tot de start om {start_tijd.strftime('%H:%M')} uur.")
            else:
                st.write(f"🔓 De koers is gestart! Hier zijn de keuzes voor {bekijk_koers}:")
                andere_keuzes = k_all[k_all['koers_naam'] == bekijk_koers].copy()
                if not andere_keuzes.empty:
                    st.dataframe(andere_keuzes[['speler_naam', 'captain_1', 'captain_2', 'captain_3']], hide_index=True, use_container_width=True, height=TABLE_HEADER_HEIGHT + len(andere_keuzes) * TABLE_ROW_HEIGHT)
                else:
                    st.info("Niemand heeft captains ingevuld voor deze koers.")

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

        # --- EMAIL REMINDERS ---
        st.subheader("📧 Email Reminders")
        reminder_koersen = list(KOERS_DATA.keys())
        reminder_koers = st.selectbox("Koers waarvoor je reminders wil sturen:", reminder_koersen, index=get_standaard_koers_index(reminder_koersen), key="reminder_koers")

        if st.button("Stuur reminders naar spelers zonder captains"):
            import resend

            resend_api_key = os.environ.get("RESEND_API_KEY")
            if not resend_api_key:
                st.error("RESEND_API_KEY niet ingesteld als environment variable.")
            else:
                resend.api_key = resend_api_key
                spelers_mail = read_sheet("speler_teams")
                keuzes_mail = read_sheet("keuzes")

                if "email" not in spelers_mail.columns:
                    st.error("Kolom 'email' ontbreekt in de speler_teams sheet.")
                else:
                    deadline_str = KOERS_DATA[reminder_koers]
                    deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
                    deadline_mooi = deadline_dt.strftime("%d-%m-%Y om %H:%M")

                    speler_info = (
                        spelers_mail[["speler_naam", "email"]]
                        .drop_duplicates("speler_naam")
                    )

                    verzonden, overgeslagen = [], []
                    for _, row in speler_info.iterrows():
                        speler_naam = row["speler_naam"]
                        email = str(row["email"]).strip()
                        if not email or email.lower() == "nan":
                            overgeslagen.append(f"{speler_naam} (geen e-mail)")
                            continue

                        keuze = keuzes_mail[
                            (keuzes_mail["speler_naam"] == speler_naam) &
                            (keuzes_mail["koers_naam"] == reminder_koers)
                        ]
                        heeft_captain = (
                            not keuze.empty and
                            str(keuze.iloc[0]["captain_1"]).strip() not in ("", "nan")
                        )
                        if heeft_captain:
                            overgeslagen.append(f"{speler_naam} (al ingevuld)")
                            continue

                        try:
                            resend.Emails.send({
                                "from": "K1xSam Klassiekerspel <onboarding@resend.dev>",
                                "to": "hetgrotewielerspel@gmail.com",
                                "subject": f"⏰ Reminder: {speler_naam} heeft nog geen captains voor {reminder_koers}",
                                "text": (
                                    f"Hoi,\n\n"
                                    f"{speler_naam} heeft nog geen captains ingevuld voor {reminder_koers}.\n\n"
                                    f"De deadline is {deadline_mooi} uur.\n\n"
                                    f"Stuur deze reminder door naar {speler_naam} ({email}).\n\n"
                                    f"Groeten,\nK1xSam Klassiekerspel"
                                ),
                            })
                            verzonden.append(f"{speler_naam} ({email})")
                        except Exception as e:
                            overgeslagen.append(f"{speler_naam} (fout: {e})")

                    if verzonden:
                        st.success(f"✅ Reminder verstuurd naar {len(verzonden)} speler(s): {', '.join(verzonden)}")
                    else:
                        st.info("Geen reminders verstuurd — iedereen heeft al captains ingevuld.")
                    if overgeslagen:
                        st.caption(f"Overgeslagen: {', '.join(overgeslagen)}")

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
                        st.info("💡 Scrapen mislukt? Gebruik de handmatige invoer hieronder.")

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
        if not df_k.empty:
            koers_lijst2 = df_k['koers_naam'].tolist()

            geselecteerde_koers_sl = st.selectbox("Selecteer een koers voor startlijst:", ["---"] + koers_lijst2, key="sl_koers")
            if st.button("Scrape startlijst geselecteerde koers") and geselecteerde_koers_sl != "---":
                rij = df_k[df_k['koers_naam'] == geselecteerde_koers_sl].iloc[0]
                ok, msg = scrape_startlijst_en_save(rij['koers_naam'], rij['url'])
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")

            st.write("---")

            if st.button("Scrape startlijsten voor ALLE koersen"):
                nu_scrape = datetime.now(_AMS)
                toekomstige_koersen = df_k[df_k['koers_naam'].apply(
                    lambda k: k in KOERS_DATA and
                    datetime.strptime(KOERS_DATA[k], "%Y-%m-%d %H:%M").replace(tzinfo=_AMS) > nu_scrape
                )]
                if toekomstige_koersen.empty:
                    st.info("Geen aankomende koersen gevonden.")
                else:
                    status_placeholder2 = st.empty()
                    for index, r in toekomstige_koersen.iterrows():
                        k_naam = r['koers_naam']
                        k_url = r['url']
                        status_placeholder2.info(f"Bezig met {k_naam}...")
                        ok, msg = scrape_startlijst_en_save(k_naam, k_url)
                        st.write(f"{'✅' if ok else '❌'} {k_naam}: {msg}")
                    status_placeholder2.success("Klaar!")
                st.cache_data.clear()
        else:
            st.error("Geen koersen gevonden.")



    elif poging != "":
        st.error("Onjuist wachtwoord. Toegang geweigerd.")
    else:
        st.info("Voer het wachtwoord in om de beheerdersfuncties te ontgrendelen.")