import streamlit as st
import pandas as pd
import plotly.express as px
from utils import require_login, run_query, check_connection, get_current_season_from_db

st.set_page_config(page_title="Statistiche Campionato", page_icon="📈", layout="wide")

# --- 1. SETUP ---
require_login()
check_connection()

current_season = get_current_season_from_db()

st.title(f"📈 Statistiche & Classifica ({current_season})")

# --- 2. SELEZIONE COMPETIZIONE ---
comps = run_query(
    "SELECT ID, Nome, Tipo FROM competizioni WHERE Stagione = :s ORDER BY Nome",
    {"s": current_season}
)

if not comps:
    st.info(f"Nessuna competizione trovata per la stagione {current_season}.")
    st.stop()

comp_options = {row[1]: {"id": row[0], "tipo": row[2]} for row in comps}
selected_comp_name = st.selectbox("🏆 Competizione", list(comp_options.keys()))
selected_comp_id = comp_options[selected_comp_name]["id"]
selected_comp_tipo = comp_options[selected_comp_name]["tipo"]

st.divider()

# --- 3. FUNZIONI ---

def get_standings(season, comp_id, fase_filter=None):
    """
    Classifica aggregata. Se fase_filter è specificato, filtra solo partite di quella fase.
    """
    fase_clause = "AND Fase = :fase" if fase_filter else ""
    params = {"season": season, "comp_id": comp_id}
    if fase_filter:
        params["fase"] = fase_filter

    query = f"""
    WITH MatchStats AS (
        SELECT
            SquadraCasaID as SquadraID,
            CASE
                WHEN GolCasa > GolOspite THEN 3
                WHEN GolCasa = GolOspite THEN 1
                ELSE 0
            END as Punti,
            GolCasa as GF,
            GolOspite as GS,
            GuadagnoCasa as Ricavi
        FROM partite
        WHERE Giocata = 1 AND Stagione = :season AND CompetizioneID = :comp_id {fase_clause}

        UNION ALL

        SELECT
            SquadraOspiteID as SquadraID,
            CASE
                WHEN GolOspite > GolCasa THEN 3
                WHEN GolOspite = GolCasa THEN 1
                ELSE 0
            END as Punti,
            GolOspite as GF,
            GolCasa as GS,
            GuadagnoOspite as Ricavi
        FROM partite
        WHERE Giocata = 1 AND Stagione = :season AND CompetizioneID = :comp_id {fase_clause}
    )
    SELECT
        fs.Nome,
        COUNT(ms.SquadraID) as PartiteGiocate,
        SUM(ms.Punti) as Punti,
        SUM(ms.GF) as GolFatti,
        SUM(ms.GS) as GolSubiti,
        (SUM(ms.GF) - SUM(ms.GS)) as DiffReti,
        SUM(ms.Ricavi) as RicaviTotali
    FROM MatchStats ms
    JOIN fantasquadre fs ON ms.SquadraID = fs.ID
    GROUP BY fs.ID, fs.Nome
    ORDER BY Punti DESC, DiffReti DESC, GolFatti DESC
    """
    try:
        return run_query(query, params)
    except Exception:
        return []


def get_knockout_matches(season, comp_id):
    """Recupera le partite delle fasi ad eliminazione, ordinate per fase e giornata."""
    query = """
    SELECT p.Fase, p.Giornata, fc.Nome as Casa, fo.Nome as Ospite,
           p.GolCasa, p.GolOspite
    FROM partite p
    JOIN fantasquadre fc ON p.SquadraCasaID = fc.ID
    JOIN fantasquadre fo ON p.SquadraOspiteID = fo.ID
    WHERE p.Giocata = 1 AND p.Stagione = :season AND p.CompetizioneID = :comp_id
      AND p.Fase IS NOT NULL AND p.Fase != 'Gironi'
    ORDER BY p.Giornata ASC, p.ID ASC
    """
    return run_query(query, {"season": season, "comp_id": comp_id}) or []


def show_standings_ui(data, title):
    """Mostra classifica, KPI e grafici."""
    if not data:
        st.info(f"📉 Nessuna partita giocata per **{title}**.")
        return

    df = pd.DataFrame(data, columns=[
        "Squadra", "PG", "Punti", "GF", "GS", "Diff.Reti", "Ricavi"
    ])
    for col in ["Punti", "GF", "GS", "Diff.Reti", "Ricavi", "PG"]:
        df[col] = df[col].astype(float)

    # KPI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👑 Capolista", df.iloc[0]["Squadra"])
    with col2:
        best = df.loc[df["GF"].idxmax()]
        st.metric("🔥 Miglior Attacco", f"{best['Squadra']} ({int(best['GF'])} gol)")
    with col3:
        rich = df.loc[df["Ricavi"].idxmax()]
        st.metric("💰 Re degli Incassi", f"{rich['Ricavi']:,.2f} FM", help=f"{rich['Squadra']}")
    with col4:
        pg_tot = df["PG"].sum() / 2
        avg_goals = (df["GF"].sum() / pg_tot) if pg_tot > 0 else 0.0
        st.metric("⚽ Media Gol/Match", f"{avg_goals:.2f}")

    # Classifica
    st.subheader(f"🏆 Classifica — {title}")
    st.dataframe(
        df, use_container_width=True, hide_index=True,
        column_config={
            "Squadra": st.column_config.TextColumn("Club", width="medium"),
            "Punti": st.column_config.ProgressColumn(
                "Punti", format="%d", min_value=0,
                max_value=int(df["Punti"].max() + 3)
            ),
            "Ricavi": st.column_config.NumberColumn("Ricavi Stadio (Tot)", format="%.2f FM"),
            "GF": st.column_config.NumberColumn(format="%d"),
            "GS": st.column_config.NumberColumn(format="%d"),
            "Diff.Reti": st.column_config.NumberColumn(format="%d"),
            "PG": st.column_config.NumberColumn(format="%d"),
        }
    )

    # Grafici
    st.markdown("### 📊 Analisi Performance")
    tab_g1, tab_g2 = st.tabs(["🏹 Attacco vs Difesa", "💸 Analisi Economica"])
    with tab_g1:
        fig = px.scatter(
            df, x="GF", y="GS", text="Squadra", size="Punti",
            color="Diff.Reti", color_continuous_scale="RdBu",
            title=f"Gol Fatti vs Gol Subiti — {title}",
            labels={"GF": "Gol Fatti", "GS": "Gol Subiti"}
        )
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
    with tab_g2:
        fig2 = px.bar(
            df.sort_values("Ricavi", ascending=True),
            x="Ricavi", y="Squadra", orientation='h',
            title=f"Ricavi Totali Stadio — {title}",
            text_auto='.2s', color="Ricavi", color_continuous_scale="Greens"
        )
        st.plotly_chart(fig2, use_container_width=True)


def show_knockout_ui(matches):
    """Mostra risultati delle fasi ad eliminazione raggruppati per fase."""
    if not matches:
        st.info("Nessuna partita ad eliminazione registrata.")
        return

    df = pd.DataFrame(matches, columns=["Fase", "Giornata", "Casa", "Ospite", "GolCasa", "GolOspite"])
    df["Risultato"] = df["GolCasa"].astype(str) + " - " + df["GolOspite"].astype(str)

    fase_order = ["Ottavi", "Quarti", "Semifinale", "Finale"]
    fasi_presenti = [f for f in fase_order if f in df["Fase"].unique()]
    # Aggiungi eventuali fasi non previste nell'ordine
    for f in df["Fase"].unique():
        if f not in fasi_presenti:
            fasi_presenti.append(f)

    for fase in fasi_presenti:
        df_fase = df[df["Fase"] == fase]
        st.markdown(f"#### {fase}")
        for _, row in df_fase.iterrows():
            winner = ""
            if row["GolCasa"] > row["GolOspite"]:
                winner = f"**{row['Casa']}** {row['Risultato']} {row['Ospite']}"
            elif row["GolOspite"] > row["GolCasa"]:
                winner = f"{row['Casa']} {row['Risultato']} **{row['Ospite']}**"
            else:
                winner = f"{row['Casa']} {row['Risultato']} {row['Ospite']}"
            st.markdown(f"- {winner}")
        st.divider()


# --- 4. VISUALIZZAZIONE ---

if selected_comp_tipo == "Campionato":
    # Campionato: classifica unica su tutte le partite
    data = get_standings(current_season, selected_comp_id)
    if data:
        show_standings_ui(data, selected_comp_name)
    else:
        st.info(f"📉 Nessuna partita giocata per **{selected_comp_name}** nella stagione {current_season}.")
        col_e1, col_e2 = st.columns([1, 2])
        with col_e1:
            st.markdown("<div style='font-size: 80px; text-align: center;'>🏟️</div>", unsafe_allow_html=True)
        with col_e2:
            st.markdown("### In attesa del calcio d'inizio!")

else:
    # Coppa: tab Gironi + tab Eliminazione
    tab_gironi, tab_elim = st.tabs(["📋 Fase a Gironi", "🏅 Fase ad Eliminazione"])

    with tab_gironi:
        data_gironi = get_standings(current_season, selected_comp_id, fase_filter="Gironi")
        if data_gironi:
            show_standings_ui(data_gironi, f"{selected_comp_name} — Gironi")
        else:
            st.info("Nessuna partita della fase a gironi registrata.")

    with tab_elim:
        knockout = get_knockout_matches(current_season, selected_comp_id)
        show_knockout_ui(knockout)
