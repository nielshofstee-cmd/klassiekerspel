"""
Stuur e-mailreminders naar spelers die nog geen captains hebben ingevuld
voor een koers die vandaag plaatsvindt.

Draai dagelijks via Railway cron job (bijv. 07:00 Amsterdam-tijd).

Vereiste environment variables:
  RESEND_API_KEY      - API key van resend.com
  GOOGLE_CREDENTIALS  - JSON-string met Google service account credentials
"""

import os
import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import resend
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

_AMS = ZoneInfo("Europe/Amsterdam")

KOERS_DATA = {
    "Omloop Het Nieuwsblad":   "2026-02-28 11:00",
    "Kuurne Brussel Kuurne":   "2026-03-01 11:00",
    "Strade Bianche":          "2026-03-07 11:00",
    "Milano Sanremo":          "2026-03-21 10:00",
    "Classic Brugge De Panne": "2026-03-25 12:00",
    "E3 Harelbeke":            "2026-03-27 12:00",
    "Gent Wevelgem":           "2026-03-29 10:00",
    "Dwars Door Vlaanderen":   "2026-04-01 12:00",
    "Ronde Van Vlaanderen":    "2026-04-05 10:00",
    "Scheldeprijs":            "2026-04-08 12:00",
    "Paris Roubaix":           "2026-04-12 11:00",
    "Brabantse Pijl":          "2026-04-15 12:00",
    "Amstel Gold Race":        "2026-04-19 10:00",
    "La Fleche Wallone":       "2026-04-22 11:00",
    "Liege Bastogne Liege":    "2026-04-26 10:00",
}


def get_sheet_client():
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_env = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_env:
        creds_info = json.loads(creds_env)
    else:
        with open("google_keys.json") as f:
            creds_info = json.load(f)
    credentials = Credentials.from_service_account_info(creds_info, scopes=scopes)
    return gspread.authorize(credentials)


def lees_sheet(gc, spreadsheet_url, tab):
    ws = gc.open_by_url(spreadsheet_url).worksheet(tab)
    return pd.DataFrame(ws.get_all_records())


def stuur_mail(aan, speler_naam, koers_naam, deadline_str):
    deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)
    deadline_mooi = deadline_dt.strftime("%d-%m-%Y om %H:%M")
    resend.Emails.send({
        "from": "K1xSam Klassiekerspel <onboarding@resend.dev>",
        "to": "hetgrotewielerspel@gmail.com",
        "subject": f"⏰ Reminder: {speler_naam} heeft nog geen captains voor {koers_naam}",
        "text": (
            f"Hoi,\n\n"
            f"{speler_naam} heeft nog geen captains ingevuld voor {koers_naam}.\n\n"
            f"De deadline is {deadline_mooi} uur.\n\n"
            f"Stuur deze reminder door naar {speler_naam} ({aan}).\n\n"
            f"Groeten,\nK1xSam Klassiekerspel"
        ),
    })


def main():
    resend_api_key = os.environ.get("RESEND_API_KEY")
    spreadsheet_url = os.environ.get(
        "SPREADSHEET_URL",
        "https://docs.google.com/spreadsheets/d/1i8UB1igCk8cSCneTeQEGkxO0XFsuhSP2u4BLZfwHllM/edit"
    )

    if not resend_api_key:
        print("FOUT: RESEND_API_KEY niet ingesteld.")
        sys.exit(1)

    resend.api_key = resend_api_key

    nu = datetime.now(_AMS)
    vandaag = nu.date()

    koersen_vandaag = [
        (naam, deadline)
        for naam, deadline in KOERS_DATA.items()
        if datetime.strptime(deadline, "%Y-%m-%d %H:%M").date() == vandaag
    ]

    if not koersen_vandaag:
        print(f"Geen koersen vandaag ({vandaag}). Klaar.")
        return

    gc = get_sheet_client()
    spelers_df = lees_sheet(gc, spreadsheet_url, "speler_teams")
    keuzes_df = lees_sheet(gc, spreadsheet_url, "keuzes")

    if "email" not in spelers_df.columns:
        print("FOUT: Kolom 'email' ontbreekt in sheet 'speler_teams'.")
        sys.exit(1)

    speler_info = (
        spelers_df[["speler_naam", "email"]]
        .drop_duplicates("speler_naam")
        .set_index("speler_naam")
    )

    for koers_naam, deadline_str in koersen_vandaag:
        deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M").replace(tzinfo=_AMS)

        if nu >= deadline_dt:
            print(f"{koers_naam}: deadline al voorbij, geen reminders verstuurd.")
            continue

        print(f"\nKoers vandaag: {koers_naam} (deadline {deadline_str})")

        verzonden = 0
        for speler_naam, row in speler_info.iterrows():
            email = str(row["email"]).strip()
            if not email or email.lower() in ("", "nan"):
                print(f"  {speler_naam}: geen e-mailadres, overgeslagen.")
                continue

            keuze = keuzes_df[
                (keuzes_df["speler_naam"] == speler_naam) &
                (keuzes_df["koers_naam"] == koers_naam)
            ]
            heeft_captain = (
                not keuze.empty and
                str(keuze.iloc[0]["captain_1"]).strip() not in ("", "nan")
            )

            if heeft_captain:
                print(f"  {speler_naam}: captains al ingevuld, geen reminder.")
                continue

            try:
                stuur_mail(email, speler_naam, koers_naam, deadline_str)
                print(f"  {speler_naam}: reminder verstuurd naar {email}.")
                verzonden += 1
            except Exception as e:
                print(f"  {speler_naam}: FOUT bij versturen naar {email}: {e}")

        print(f"  Totaal verstuurd: {verzonden}")


if __name__ == "__main__":
    main()
