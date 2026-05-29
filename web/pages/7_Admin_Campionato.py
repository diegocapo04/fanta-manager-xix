import streamlit as st
import pandas as pd
import re
from utils import require_login, run_query, is_admin, check_connection, run_transaction_batch, get_current_season_from_db


st.set_page_config(page_title="Gestione Gare", page_icon="⚽", layout="wide")


# --- PREMI PER PARTITA (in FM) ---
PREMIO_VITTORIA        = 0.50
PREMIO_PAREGGIO        = 0.25
PREMIO_SCONFITTA       = 0.10
PREMIO_PER_GOL         = 0.50
INCASSO_STADIO_DEFAULT = 5.0


# --- SETUP ---
require_login()
check_connection()

if not is_admin():
    st.error("⛔ Accesso riservato agli amministratori.")
    st.stop()

current_season = get_current_season_from_db()
st.title(f"⚽ Gestione Gare & Calendario ({current_season})")


# ======================================================================
# PARSER EXCEL
# ======================================================================

def parse_calendar_excel(df):
    raw_name = str(df.iloc[0, 0]).strip()
    competition_name = raw_name.replace("Calendario ", "").strip()

    matches = []

    def norm_text(x):
        if pd.isna(x):
            return ""
        return str(x).strip()

    def parse_score(s):
        if pd.isna(s):
            return None, None
        s = str(s).strip()
        if s == "-" or s == "":
            return None, None
        try:
            p = s.split("-")
            if len(p) == 2:
                return int(float(p[0])), int(float(p[1]))
        except:
            pass
        return None, None

    def get_matchday(text):
        if pd.isna(text):
            return None
        m = re.search(r"(\d+)", str(text))
        return int(m.group(1)) if m else None

    def detect_phase_label(text):
        t = norm_text(text).lower()

        phase_map = {
            "ottavi": "Ottavi",
            "quarti": "Quarti",
            "semifinali": "Semifinale",
            "semifinale": "Semifinale",
            "finale": "Finale",
            "gironi": "Gironi",
            "fase a gironi": "Gironi",
            "league phase": "Gironi",
        }

        for key, value in phase_map.items():
            if key in t:
                return value
        return None

    def is_group_letter(val):
        return norm_text(val) in ["A", "B", "C", "D"]

    has_groups = any(
        is_group_letter(df.iloc[r, 0]) or is_group_letter(df.iloc[r, 7] if df.shape[1] > 7 else None)
        for r in range(len(df))
    )

    current_phase = "Gironi"

    if not has_groups:
        row = 0
        while row < len(df):
            # intercetta eventuali intestazioni di fase
            row_values = [norm_text(df.iloc[row, c]) for c in range(min(df.shape[1], 13))]
            detected_phase = None
            for val in row_values:
                detected_phase = detect_phase_label(val)
                if detected_phase:
                    current_phase = detected_phase
                    break

            # due blocchi per riga: sinistra e destra
            for block_col, home_c, away_c, score_c in [(0, 0, 3, 4), (6, 6, 9, 10)]:
                if df.shape[1] <= block_col:
                    continue

                cell = df.iloc[row, block_col]
                if isinstance(cell, str) and "Giornata lega" in cell:
                    giornata = get_matchday(cell)

                    for i in range(1, 6):
                        if row + i >= len(df):
                            break

                        home = df.iloc[row + i, home_c] if df.shape[1] > home_c else None
                        away = df.iloc[row + i, away_c] if df.shape[1] > away_c else None
                        score = df.iloc[row + i, score_c] if df.shape[1] > score_c else None

                        home_txt = norm_text(home)
                        away_txt = norm_text(away)

                        if not home_txt or not away_txt:
                            continue
                        if "Riposa" in home_txt or "Riposa" in away_txt:
                            continue
                        if home_txt == "-" or away_txt == "-":
                            continue

                        gh, ga = parse_score(score)

                        matches.append({
                            "Giornata": giornata,
                            "Casa": home_txt,
                            "Ospite": away_txt,
                            "GolCasa": gh,
                            "GolOspite": ga,
                            "Giocata": 1 if gh is not None else 0,
                            "Girone": None,
                            "Fase": current_phase
                        })
            row += 1

    else:
        row = 0
        while row < len(df):
            row_values = [norm_text(df.iloc[row, c]) for c in range(min(df.shape[1], 13))]
            detected_phase = None
            for val in row_values:
                detected_phase = detect_phase_label(val)
                if detected_phase:
                    current_phase = detected_phase
                    break

            for g_c, home_c, away_c, score_c in [(0, 1, 4, 5), (7, 8, 11, 12)]:
                if df.shape[1] <= g_c:
                    continue

                cell = df.iloc[row, g_c]
                if isinstance(cell, str) and "Giornata lega" in cell:
                    giornata = get_matchday(cell)

                    for i in range(1, 7):
                        if row + i >= len(df):
                            break

                        girone = df.iloc[row + i, g_c] if df.shape[1] > g_c else None
                        home = df.iloc[row + i, home_c] if df.shape[1] > home_c else None
                        away = df.iloc[row + i, away_c] if df.shape[1] > away_c else None
                        score = df.iloc[row + i, score_c] if df.shape[1] > score_c else None

                        home_txt = norm_text(home)
                        away_txt = norm_text(away)
                        girone_txt = norm_text(girone)

                        if not home_txt or not away_txt:
                            continue
                        if "Riposa" in home_txt or "Riposa" in away_txt:
                            continue
                        if not is_group_letter(girone_txt):
                            continue

                        gh, ga = parse_score(score)

                        matches.append({
                            "Giornata": giornata,
                            "Casa": home_txt,
                            "Ospite": away_txt,
                            "GolCasa": gh,
                            "GolOspite": ga,
                            "Giocata": 1 if gh is not None else 0,
                            "Girone": girone_txt,
                            "Fase": current_phase
                        })
            row += 1

    return competition_name, has_groups, pd.DataFrame(matches) if matches else pd.DataFrame()


# ======================================================================
# LOGICA ECONOMICA
# ======================================================================

def calculate_earnings(team_id, is_home, goals_made, goals_conceded):
    earnings, details = 0.0, []
    if goals_made > goals_conceded:
        earnings += PREMIO_VITTORIA;  details.append(f"V(+{PREMIO_VITTORIA})")
    elif goals_made == goals_conceded:
        earnings += PREMIO_PAREGGIO;  details.append(f"P(+{PREMIO_PAREGGIO})")
    else:
        earnings += PREMIO_SCONFITTA; details.append(f"S(+{PREMIO_SCONFITTA})")

    bonus_gol = goals_made * PREMIO_PER_GOL
    if bonus_gol > 0:
        earnings += bonus_gol; details.append(f"{goals_made}G(+{bonus_gol})")

    if is_home:
        res    = run_query("SELECT IncassoPartita FROM stadi WHERE SquadraID = :tid", {"tid": team_id})
        stadio = float(res[0][0]) if res and res[0][0] else INCASSO_STADIO_DEFAULT
        earnings += stadio; details.append(f"Stadio(+{stadio})")

    return earnings, " | ".join(details)


# ======================================================================
# PROCESSING PRINCIPALE
# ======================================================================

def process_new_matchdays(df_matches, comp_id, season, fase=None):
    res = run_query(
        "SELECT COALESCE(MAX(Giornata), 0) FROM partite WHERE CompetizioneID=:c AND Stagione=:s",
        {"c": comp_id, "s": season}
    )
    last_giornata_db = int(res[0][0]) if res else 0

    df_new = df_matches[
        (df_matches["Giornata"] > last_giornata_db) &
        (df_matches["Giocata"] == 1)
    ].copy()

    if df_new.empty:
        return 0, 0, [f"ℹ️ Nessuna nuova giornata rispetto all'ultima salvata (G{last_giornata_db})."]

    res_teams = run_query("SELECT ID, Nome FROM fantasquadre")
    teams     = {row[1]: row[0] for row in res_teams} if res_teams else {}

    ops = []
    log = []
    giornate_nuove = sorted(df_new["Giornata"].unique())

    for _, match in df_new.iterrows():
        home_name = match["Casa"]
        away_name = match["Ospite"]
        home_id   = teams.get(home_name)
        away_id   = teams.get(away_name)
        gh        = int(match["GolCasa"])
        ga        = int(match["GolOspite"])
        giornata  = int(match["Giornata"])

        if not home_id or not away_id:
            log.append(f"⚠️ Squadra non trovata: '{home_name}' o '{away_name}' (G{giornata})")
            continue

        money_home, note_h = calculate_earnings(home_id, True,  gh, ga)
        money_away, note_a = calculate_earnings(away_id, False, ga, gh)

        # INSERT IGNORE evita duplicati grazie alla UNIQUE KEY su partite
        fase_match = match["Fase"] if "Fase" in df_new.columns and pd.notna(match["Fase"]) else fase

        ops.append(("""
            INSERT IGNORE INTO partite
                (CompetizioneID, Stagione, Giornata, SquadraCasaID, SquadraOspiteID,
                GolCasa, GolOspite, Giocata, GuadagnoCasa, GuadagnoOspite, Fase)
            VALUES (:c, :s, :g, :h, :a, :gh, :ga, 1, :mh, :ma, :fase)
        """, {
            "c": comp_id, "s": season, "g": giornata,
            "h": home_id, "a": away_id,
            "gh": gh, "ga": ga,
            "mh": money_home, "ma": money_away,
            "fase": fase_match
        }))

        ops.append((
            "UPDATE fantasquadre SET CreditiResidui=CreditiResidui+:m WHERE ID=:t",
            {"m": money_home, "t": home_id}
        ))
        ops.append((
            "UPDATE fantasquadre SET CreditiResidui=CreditiResidui+:m WHERE ID=:t",
            {"m": money_away, "t": away_id}
        ))

        log.append(f"✅ G{giornata}: {home_name} {gh}-{ga} {away_name} | 🏠{note_h} | ✈️{note_a}")

    if ops:
        if run_transaction_batch(ops):
            log.insert(0, f"🎯 **{len(giornate_nuove)} giornate nuove processate** (G{giornate_nuove[0]}→G{giornate_nuove[-1]})")
        else:
            return 0, 0, ["❌ Errore durante il salvataggio nel database."]

    return len(giornate_nuove), len(df_new), log


# ======================================================================
# FUNZIONI DB HELPER
# ======================================================================

def get_competitions():
    res = run_query(
        "SELECT ID, Nome, Tipo FROM competizioni WHERE Stagione = :s ORDER BY ID",
        {"s": current_season}
    )
    return {row[1]: {"id": row[0], "tipo": row[2]} for row in res} if res else {}

def get_teams_map():
    res = run_query("SELECT ID, Nome FROM fantasquadre ORDER BY Nome")
    return {row[1]: row[0] for row in res} if res else {}

def get_matches(season, played=False, competition_id=None):
    if isinstance(competition_id, dict):
        competition_id = competition_id.get("id")
    status = 1 if played else 0
    q = """
    SELECT p.ID, p.Giornata, fc.Nome, fo.Nome, p.GolCasa, p.GolOspite,
           p.SquadraCasaID, p.SquadraOspiteID, c.Nome
    FROM partite p
    JOIN fantasquadre fc ON p.SquadraCasaID = fc.ID
    JOIN fantasquadre fo ON p.SquadraOspiteID = fo.ID
    JOIN competizioni c  ON p.CompetizioneID  = c.ID
    WHERE p.Stagione=:s AND p.Giocata=:st
    """
    params = {"s": season, "st": status}
    if competition_id:
        q += " AND p.CompetizioneID=:cid"; params["cid"] = competition_id
    q += " ORDER BY p.Giornata ASC, p.ID ASC"
    return run_query(q, params)


# ======================================================================
# UI
# ======================================================================

comps_map = get_competitions()
teams_map = get_teams_map()

tab_upload, tab_manual, tab_hist = st.tabs([
    "📤 Importa da Excel",
    "✏️ Inserimento Manuale",
    "📜 Storico Partite"
])


# ==================== TAB 1: UPLOAD EXCEL ====================
with tab_upload:
    st.header("Importa Calendario da Fantacalcio")
    st.info(
        "Carica il file Excel esportato da Fantacalcio. "
        "L'app rileverà automaticamente il nome della competizione, "
        "il formato (Campionato / Coppa con gironi) e processerà "
        "**solo le giornate non ancora salvate**."
    )

    uploaded = st.file_uploader("Scegli file Excel (.xlsx)", type=["xlsx"])

    if uploaded:
        try:
            df_raw = pd.read_excel(uploaded, header=None)
            comp_name, has_groups, df_parsed = parse_calendar_excel(df_raw)

            if df_parsed.empty:
                st.error("Nessuna partita trovata nel file. Controlla il formato.")
                st.stop()

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("📋 Competizione Rilevata", comp_name)
            col_b.metric("📅 Giornate nel file",     df_parsed["Giornata"].nunique())
            col_c.metric("⚽ Partite Giocate",        int(df_parsed["Giocata"].sum()))

            st.dataframe(
                df_parsed[df_parsed["Giocata"] == 1][["Giornata","Casa","Ospite","GolCasa","GolOspite"]],
                use_container_width=True, hide_index=True
            )

            st.divider()

            # --- Gestione Competizione ---
            comp_id = None
            comp_tipo = None
            if comp_name in comps_map:
                comp_id = comps_map[comp_name]["id"]
                comp_tipo = comps_map[comp_name]["tipo"]
                st.success(f"✅ Competizione **{comp_name}** trovata nel DB (ID: {comp_id})")
            else:
                st.warning(f"⚠️ La competizione **'{comp_name}'** non esiste nel database.")
                with st.expander("➕ Crea nuova competizione", expanded=True):
                    with st.form("new_comp_form"):
                        tipo_new = st.selectbox("Tipo", ["Campionato", "Coppa"])
                        if st.form_submit_button("💾 Crea Competizione"):
                            run_query(
                                "INSERT INTO competizioni (Nome, Stagione, Tipo) "
                                "VALUES (:n, :s, :t)",
                                {"n": comp_name, "s": current_season, "t": tipo_new}
                            )
                            st.success(f"Competizione '{comp_name}' creata!")
                            st.rerun()

            if comp_id:
                # Selezione Fase per competizioni di tipo Coppa
                fase_upload = None
                if comp_tipo == "Coppa":
                    if "Fase" in df_parsed.columns and df_parsed["Fase"].notna().any():
                        fasi_rilevate = [f for f in df_parsed["Fase"].dropna().unique().tolist() if f]
                        st.success(f"Fasi rilevate automaticamente dal file: {', '.join(fasi_rilevate)}")
                        fase_upload = None
                    else:
                        fase_options = ["Gironi", "Ottavi", "Quarti", "Semifinale", "Finale"]
                        fase_upload = st.selectbox(
                            "Fase da importare", fase_options, key="fase_upload",
                            help="Usata solo se il parser non rileva automaticamente la fase"
                        )

                res_last = run_query(
                    "SELECT COALESCE(MAX(Giornata), 0) FROM partite "
                    "WHERE CompetizioneID=:c AND Stagione=:s",
                    {"c": comp_id, "s": current_season}
                )
                last_g = int(res_last[0][0]) if res_last else 0
                new_g  = df_parsed[
                    (df_parsed["Giornata"] > last_g) &
                    (df_parsed["Giocata"] == 1)
                ]["Giornata"].nunique()

                st.info(
                    f"📌 Ultima giornata già nel DB: **G{last_g}** | "
                    f"Nuove giornate da importare: **{new_g}**"
                )

                if new_g == 0:
                    st.success("✅ Il database è già aggiornato con tutte le giornate giocate.")
                else:
                    if st.button(f"🚀 Importa {new_g} Nuove Giornate nel DB", type="primary"):
                        with st.spinner("Elaborazione in corso..."):
                            n_g, n_p, logs = process_new_matchdays(df_parsed, comp_id, current_season, fase=fase_upload)
                        if n_g > 0:
                            st.balloons()
                            st.success(f"Importate {n_g} giornate ({n_p} partite)")
                        with st.expander("📋 Log dettagliato", expanded=True):
                            for msg in logs:
                                st.markdown(msg)

        except Exception as e:
            st.error(f"Errore nella lettura del file: {e}")
            st.exception(e)


# ==================== TAB 2: INSERIMENTO MANUALE ====================
with tab_manual:
    st.header("Inserimento Manuale")

    if not comps_map:
        st.warning("Nessuna competizione trovata per la stagione corrente.")
        st.info("Crea prima una competizione nel tab 'Importa da Excel' oppure usa il form qui sotto.")
        with st.expander("➕ Crea competizione manualmente"):
            with st.form("new_comp_manual"):
                nome_c = st.text_input("Nome competizione")
                tipo_c = st.selectbox("Tipo", ["Campionato", "Coppa"])
                if st.form_submit_button("💾 Crea"):
                    if nome_c.strip():
                        run_query(
                            "INSERT INTO competizioni (Nome, Stagione, Tipo) "
                            "VALUES (:n, :s, :t)",
                            {"n": nome_c.strip(), "s": current_season, "t": tipo_c}
                        )
                        st.success(f"Competizione '{nome_c}' creata!")
                        st.rerun()
    else:
        with st.form("new_match"):
            c1, c2 = st.columns(2)
            comp_sel    = c1.selectbox("Competizione", list(comps_map.keys()))
            comp_id_man = comps_map[comp_sel]["id"]
            comp_tipo_man = comps_map[comp_sel]["tipo"]
            giornata    = c2.number_input("Giornata", 1, 50, 1)

            # Fase per competizioni di tipo Coppa
            fase_man = None
            if comp_tipo_man == "Coppa":
                fase_options_man = ["Gironi", "Ottavi", "Quarti", "Semifinale", "Finale"]
                fase_man = st.selectbox("Fase", fase_options_man, key="fase_manual")

            c3, c4 = st.columns(2)
            casa   = c3.selectbox("Squadra Casa",   list(teams_map.keys()), key="new_h")
            ospite = c4.selectbox("Squadra Ospite", list(teams_map.keys()), key="new_a",
                                  index=min(1, len(teams_map) - 1))
            c5, c6 = st.columns(2)
            gh_m    = c5.number_input("Gol Casa",   0, 20, 0, key="gh_man")
            ga_m    = c6.number_input("Gol Ospite", 0, 20, 0, key="ga_man")
            giocata = st.checkbox("Segna come già giocata", value=True)

            if st.form_submit_button("➕ Aggiungi Partita"):
                if casa == ospite:
                    st.error("Le due squadre devono essere diverse!")
                else:
                    home_id_m = teams_map[casa]
                    away_id_m = teams_map[ospite]
                    if giocata:
                        mh, _ = calculate_earnings(home_id_m, True,  gh_m, ga_m)
                        ma, _ = calculate_earnings(away_id_m, False, ga_m, gh_m)
                        ops = [
                            ("INSERT IGNORE INTO partite "
                             "(CompetizioneID, Stagione, Giornata, SquadraCasaID, SquadraOspiteID, "
                             "GolCasa, GolOspite, Giocata, GuadagnoCasa, GuadagnoOspite, Fase) "
                             "VALUES (:c,:s,:g,:h,:a,:gh,:ga,1,:mh,:ma,:fase)",
                             {"c": comp_id_man, "s": current_season, "g": giornata,
                              "h": home_id_m, "a": away_id_m,
                              "gh": gh_m, "ga": ga_m, "mh": mh, "ma": ma, "fase": fase_man}),
                            ("UPDATE fantasquadre SET CreditiResidui=CreditiResidui+:m WHERE ID=:t",
                             {"m": mh, "t": home_id_m}),
                            ("UPDATE fantasquadre SET CreditiResidui=CreditiResidui+:m WHERE ID=:t",
                             {"m": ma, "t": away_id_m}),
                        ]
                        if run_transaction_batch(ops):
                            st.success("Partita aggiunta e budget aggiornato!")
                            st.rerun()
                    else:
                        run_query(
                            "INSERT IGNORE INTO partite "
                            "(CompetizioneID, Stagione, Giornata, SquadraCasaID, SquadraOspiteID, Giocata, Fase) "
                            "VALUES (:c,:s,:g,:h,:a,0,:fase)",
                            {"c": comp_id_man, "s": current_season, "g": giornata,
                             "h": home_id_m, "a": away_id_m, "fase": fase_man}
                        )
                        st.success("Partita schedulata!")
                        st.rerun()


# ==================== TAB 3: STORICO ====================
with tab_hist:
    st.header("Storico Partite Giocate")

    sel_comp_h = st.selectbox(
        "Filtra per competizione", ["Tutte"] + list(comps_map.keys()), key="hist_comp"
    )
    cid_h = comps_map[sel_comp_h]["id"] if sel_comp_h != "Tutte" else None

    played = get_matches(current_season, played=True, competition_id=cid_h)
    if played:
        df_hist = pd.DataFrame(
            played,
            columns=["ID","Giornata","Casa","Ospite","GolCasa","GolOspite",
                     "CasaID","OspiteID","Competizione"]
        )
        df_hist["Risultato"] = (
            df_hist["GolCasa"].astype(int).astype(str) + " - " +
            df_hist["GolOspite"].astype(int).astype(str)
        )
        st.dataframe(
            df_hist[["Giornata","Competizione","Casa","Ospite","Risultato"]],
            use_container_width=True, hide_index=True,
            column_config={"Giornata": st.column_config.NumberColumn(format="%d")}
        )
        st.caption(f"Totale partite giocate: {len(df_hist)}")
    else:
        st.info("Nessuna partita registrata per questa stagione.")