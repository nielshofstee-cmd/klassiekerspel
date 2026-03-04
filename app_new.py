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
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

/* === ROOT VARIABELEN === */
:root {
    --blauw: #1a2e4a;
    --blauw-mid: #1e3a5f;
    --blauw-licht: #2d5986;
    --oranje: #f47c20;
    --oranje-licht: #ff9a45;
    --wit: #ffffff;
    --grijs-licht: #f4f6f9;
    --grijs-mid: #e2e8f0;
    --tekst-donker: #1a2e4a;
    --tekst-grijs: #64748b;
}

/* === ACHTERGROND === */
.stApp {
    background-color: var(--grijs-licht);
    font-family: 'Inter', sans-serif;
}

/* === VERBERG STANDAARD SIDEBAR === */
[data-testid="stSidebar"] {
    display: none !important;
}

/* === VERBERG STREAMLIT HEADER/TOOLBAR === */
header[data-testid="stHeader"] {
    background: var(--blauw) !important;
}
#MainMenu, footer, header .stToolbar {
    visibility: hidden;
}

/* === TOPBALK NAVIGATIE === */
.nav-container {
    background: linear-gradient(135deg, var(--blauw) 0%, var(--blauw-mid) 100%);
    padding: 0;
    margin: -1rem -1rem 2rem -1rem;
    box-shadow: 0 4px 20px rgba(26,46,74,0.3);
    position: sticky;
    top: 0;
    z-index: 999;
}

.nav-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px 0 24px;
}

.nav-logo {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: var(--wit);
    letter-spacing: 1px;
    text-transform: uppercase;
}

.nav-logo span {
    color: var(--oranje);
}

.nav-season {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 500;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* === PAGE TITLE STYLING === */
h1 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    color: var(--blauw) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 1.5rem !important;
}

h2, h3 {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    color: var(--blauw) !important;
}

/* === METRIC CARDS === */
[data-testid="stMetric"] {
    background: var(--wit);
    border-radius: 12px;
    padding: 20px !important;
    border-left: 4px solid var(--oranje);
    box-shadow: 0 2px 12px rgba(26,46,74,0.08);
}

[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif;
    font-size: 12px !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--tekst-grijs) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem !important;
    font-weight: 700;
    color: var(--blauw) !important;
}

/* === TABS STYLING === */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--wit);
    border-radius: 10px;
    padding: 6px;
    gap: 4px;
    box-shadow: 0 2px 8px rgba(26,46,74,0.08);
    margin-bottom: 1.5rem;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 13px;
    color: var(--tekst-grijs);
    border-radius: 8px;
    padding: 8px 16px;
    border: none !important;
    background: transparent;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: var(--blauw) !important;
    color: var(--wit) !important;
}

/* === DATAFRAME STYLING === */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(26,46,74,0.08);
    border: 1px solid var(--grijs-mid);
}

/* === SELECTBOX & INPUT STYLING === */
[data-testid="stSelectbox"] > div > div {
    border-radius: 8px !important;
    border-color: var(--grijs-mid) !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border-color: var(--grijs-mid) !important;
    font-family: 'Inter', sans-serif;
}

/* === BUTTONS === */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--oranje) 0%, var(--oranje-licht) 100%);
    color: var(--wit);
    border: none;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 24px;
    box-shadow: 0 4px 12px rgba(244,124,32,0.3);
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(244,124,32,0.4);
}

/* === ALERTS & INFO === */
[data-testid="stAlert"] {
    border-radius: 10px;
    font-family: 'Inter', sans-serif;
}

/* === DIVIDER === */
hr {
    border-color: var(--grijs-mid) !important;
    margin: 1.5rem 0 !important;
}

/* === CARD CONTAINERS === */
.card {
    background: var(--wit);
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 2px 16px rgba(26,46,74,0.08);
    margin-bottom: 1.5rem;
    border: 1px solid var(--grijs-mid);
}

.card-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--blauw);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 2px solid var(--oranje);
    display: inline-block;
}

/* === RANGLIJST PODIUM === */
.podium-row {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 8px;
    background: var(--wit);
    box-shadow: 0 1px 6px rgba(26,46,74,0.06);
    font-family: 'Inter', sans-serif;
}

.rank-1 { border-left: 4px solid #FFD700; }
.rank-2 { border-left: 4px solid #C0C0C0; }
.rank-3 { border-left: 4px solid #CD7F32; }

/* === SPINNER === */
[data-testid="stSpinner"] {
    color: var(--oranje) !important;
}

/* === MOBIEL RESPONSIVE === */
@media (max-width: 768px) {
    .nav-header {
        padding: 12px 16px 0 16px;
    }
    .nav-logo {
        font-size: 18px;
    }
    h1 {
        font-size: 1.8rem !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        font-size: 11px;
        padding: 6px 10px;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
    }
}

/* === KOERS BADGE === */
.koers-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--blauw) 0%, var(--blauw-licht) 100%);
    color: var(--wit);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.5px;
    margin: 2px;
}

.oranje-badge {
    background: linear-gradient(135deg, var(--oranje) 0%, var(--oranje-licht) 100%);
}
</style>
""", unsafe_allow_html=True)

# --- DATABASE CONFIGURATIE & VERBINDING ---
import os, json

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

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

# 5. --- DATA INLADEN MET PAUZES EN KOLOM-SCHOONMAAK ---
u_all = read_sheet("uitslagen")
if not u_all.empty: 
    u_all.columns = [str(c).strip().lower() for c in u_all.columns]

time.sleep(1) # API Pauze

s_all = read_sheet("speler_teams")
if not s_all.empty: 
    s_all.columns = [str(c).strip().lower() for c in s_all.columns]

time.sleep(1) # API Pauze

k_all = read_sheet("keuzes")
# Vangnet: als de sheet leeg is, maak een DataFrame met de juiste koppen
if k_all is None or k_all.empty:
    k_all = pd.DataFrame(columns=["speler_naam", "koers_naam", "captain_1", "captain_2", "captain_3"])
else:
    k_all.columns = [str(c).strip().lower() for c in k_all.columns]

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
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
        time.sleep(random.uniform(2, 4))
        response = scraper.get(url, timeout=25)
        if response.status_code != 200: 
            return False, f"Foutcode {response.status_code}"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='results')
        if not table: 
            return False, "Geen uitslagentabel gevonden."

        # 1. Haal huidige uitslagen op om te filteren
        existing_df = read_sheet("uitslagen")
        standard_cols = ['koers_naam', 'rank', 'rider', 'team']

        if not existing_df.empty:
            existing_df.columns = [str(c).strip().lower() for c in existing_df.columns]
            # Behoud alles BEHALVE de koers die we nu scrapen (voorkomt dubbele data)
            other_races_df = existing_df[existing_df['koers_naam'] != koers_naam].copy()
        else:
            other_races_df = pd.DataFrame(columns=standard_cols)
        
        # 2. Scrape de nieuwe data
        temp_data = []
        rows = table.find_all('tr')
        
        # Statussen die we expliciet willen meenemen naast de cijfers
        toegestane_statussen = ["DNF", "OTL", "DSQ"]

        for row in rows:
            tds = row.find_all('td')
            if not tds: continue
            
            # Haal de tekst uit de eerste kolom en maak schoon
            rank_raw = tds[0].get_text(strip=True).upper()
            
            links = row.find_all('a', href=True)
            rider, team = "", ""
            for link in links:
                href = link['href']
                if "rider/" in href and not rider: 
                    # separator=' ' zorgt dat voor- en achternaam gescheiden blijven
                    rider = link.get_text(separator=' ', strip=True) 
                elif "team/" in href and not team: 
                    team = link.get_text(separator=' ', strip=True)
            
            # Logica: Alleen toevoegen als het een getal is OF in ons lijstje staat
            is_getal = rank_raw.isdigit()
            is_uitvaller = rank_raw in toegestane_statussen
            
            if rider and (is_getal or is_uitvaller):
                temp_data.append({
                    "koers_naam": koers_naam, 
                    "rank": rank_raw, 
                    "rider": rider, 
                    "team": team
                })
        
        new_scraped_df = pd.DataFrame(temp_data)

        # 3. Combineer: Oude andere koersen + Nieuwe uitslag van deze koers
        final_df = pd.concat([other_races_df, new_scraped_df], ignore_index=True)
        final_df = final_df[standard_cols] # Altijd juiste volgorde

        # 4. Schrijf de volledige gecombineerde lijst terug naar Google Sheets
        ws_u = sh.worksheet("uitslagen")
        ws_u.clear() 
        ws_u.update([standard_cols] + final_df.values.tolist())
        
        # Forceer cache refresh zodat de nieuwe data direct zichtbaar is in de app
        st.cache_data.clear()
        
        return True, f"Succes! {len(temp_data)} renners verwerkt (incl. DNF/OTL/DSQ)."
    except Exception as e:
        return False, f"Fout: {str(e)}"

# --- REKEN LOGICA (AANGEPAST VOOR TEAM PUNTEN BIJ DNF/OTL/DSQ) ---
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

# Admin modus bepalen via query params
query_params = st.query_params
admin_modus = query_params.get("beheer", "") == "1"

# Topnavigatie header met beheerknop rechtsboven
beheer_url = "?beheer=1"
slotje = "🔓" if admin_modus else "🔒"
st.markdown(f"""
<div class="nav-container">
    <div class="nav-header">
        <div class="nav-logo">K1<span>x</span>Sam <span style="color:rgba(255,255,255,0.4);font-weight:300;">|</span> Klassiekerspel</div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div class="nav-season">🚴 Seizoen 2026</div>
            <a href="{beheer_url}" title="Beheer" style="
                color: rgba(255,255,255,0.25);
                font-size: 16px;
                text-decoration: none;
                transition: color 0.2s;
                padding: 4px;
            " onmouseover="this.style.color='rgba(244,124,32,0.8)'" onmouseout="this.style.color='rgba(255,255,255,0.25)'">{slotje}</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

PAGINA_OPTIES = ["🏆 Klassement", "🏁 Uitslagen", "📊 Matrix", "🚌 Mijn Team", "©️ Captains"]
PAGINA_KEYS  = ["Klassement", "Uitslag per Koers", "Renner-Koers Matrix", "Mijn Team", "Captains Kiezen"]

tab_klas, tab_uitslag, tab_matrix, tab_team, tab_captains = st.tabs(PAGINA_OPTIES)

# Data inladen via Google Sheets (ttl=0 zorgt dat we altijd verse data hebben)
u_all = read_sheet("uitslagen")
s_all = read_sheet("speler_teams")
k_all = read_sheet("keuzes")

# =============================================
# 1. KLASSEMENT
# =============================================
with tab_klas:
    st.title("🏆 Klassementen")
    if u_all.empty or s_all.empty:
        st.info("Nog geen data beschikbaar. Zorg dat teams en uitslagen zijn geladen.")
    else:
        volgorde_csv = get_koersen_volgorde()
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

        # Functie voor compacte weergave
        def display_compact_df(df, rows_visible=12):
            # Bereken hoogte: header (~35px) + (aantal rijen * ~35px)
            calc_height = 36 + (rows_visible * 36) 
            
            st.dataframe(
                df[['Deelnemer', 'Totaal']],
                column_config={
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
            df_alg.index += 1
            # Hier roepen we de functie aan
            display_compact_df(df_alg, rows_visible=12)

        def toon_poule_tabel(poule_naam):
            mask = df_scores['Poules'].apply(lambda x: poule_naam in x)
            df_p = df_scores[mask].sort_values('Totaal', ascending=False).reset_index(drop=True)
            if not df_p.empty:
                df_p.index += 1
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
        volgorde = get_koersen_volgorde()
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
            
            st.dataframe(
            df_koers_punten,
            column_config={
                "Deelnemer": st.column_config.TextColumn(
                    "Deelnemer",
                    width="medium"
                ),
                "Punten": st.column_config.NumberColumn(
                    "Punten",
                    width="small",
                    format="%d"
                ),
                "Scorende Renners": st.column_config.TextColumn(
                    "Scorende Renners",
                    width=2500,  # FORCEER een enorme breedte in pixels
                    help="Scroll naar rechts om alle renners te zien"
                ),
            },
            hide_index=False,
            use_container_width=True
        )
        else:
            st.info("Geen gegevens beschikbaar voor deze koers.")

# =============================================
# 3. RENNER-KOERS PUNTEN MATRIX
# =============================================
with tab_matrix:
    st.title("📊 Punten Matrix")
    if not s_all.empty and not u_all.empty:
        speler = st.selectbox("Selecteer Deelnemer", sorted(s_all['speler_naam'].unique()))
        
        volgorde = get_koersen_volgorde()
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
                return 'color: #155724; background-color: #d4edda; font-weight: bold;'
            elif v in ["DNF", "OTL", "DSQ"]:
                return 'color: #721c24; background-color: #f8d7da; font-style: italic;'
            elif v == "-":
                return 'color: #ccc;'
            else:
                return 'color: #999;'

        st.dataframe(df_matrix.style.applymap(style_matrix), use_container_width=True)

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
        st.dataframe(
            df_mijn_team,
            column_config={
                "Renner": st.column_config.TextColumn("Renner", width="medium"),
                "Totaal Punten": st.column_config.NumberColumn(
                    "Totaal Punten",
                    width="medium",  # Iets breder gemaakt zodat de titel past
                    format="%d"
                ),
            },
            hide_index=True,
            use_container_width=False,
            height=921  # Verhoog dit getal (pixels) om meer rijen tegelijk te tonen
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
                    c1 = st.selectbox("Kies Captain 1 (3.0x)", mr)
                    c2 = st.selectbox("Kies Captain 2 (2.5x)", [r for r in mr if r != c1])
                    c3 = st.selectbox("Kies Captain 3 (2.0x)", [r for r in mr if r not in [c1, c2]])
                    
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
# 6. ADMIN (verborgen - toegang via ?beheer=1)
# =============================================
if admin_modus:
    st.title("⚙️ Admin Dashboard")
    
    # --- WACHTWOORD BEVEILIGING ---
    poging = st.text_input("Voer het admin-wachtwoord in:", type="password")
    
    if poging == "kankerbuffel":
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