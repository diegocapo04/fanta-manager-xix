import streamlit as st
import pandas as pd
import plotly.express as px
from utils import require_login, run_query, check_connection

st.set_page_config(page_title="Rose", page_icon="📋", layout="wide")

# --- 1. SETUP ---
require_login()
check_connection()

st.title("📋 Consultazione Rose")

# --- 2. SELEZIONE SQUADRA ---
teams = run_query("SELECT ID, Nome FROM fantasquadre ORDER BY Nome ASC")

if not teams:
    st.warning("⚠️ Nessuna squadra disponibile.")
    st.stop()

team_dict = {row[1]: row[0] for row in teams}
col_sel, _ = st.columns([1, 2])
with col_sel:
    selected_team_name = st.selectbox("Seleziona Club", list(team_dict.keys()))
    selected_team_id = team_dict[selected_team_name]

# --- 3. DATI ---
def get_roster(tid):
    q = """
    SELECT 
        g.Nome, g.Cognome, g.Ruolo, 
        c.Stipendio, c.AnniDurata, c.CostoAcquisto, 
        c.PrimaSquadra, c.SettoreGiovanile
    FROM contratti c 
    JOIN giocatori g ON c.GiocatoreID = g.ID
    WHERE c.SquadraID = :tid
    ORDER BY FIELD(g.Ruolo, 'P', 'D', 'C', 'A'), g.Cognome
    """
    return run_query(q, {"tid": tid})

def get_budget(tid):
    q = "SELECT CreditiResidui FROM fantasquadre WHERE ID = :tid"
    res = run_query(q, {"tid": tid})
    return float(res[0][0]) if res else 0.0

roster_data = get_roster(selected_team_id)
current_budget = get_budget(selected_team_id)

# --- 4. KPI ---
if roster_data:
    df = pd.DataFrame(roster_data, columns=[
        "Nome", "Cognome", "Ruolo", "Stipendio", "Anni", "Costo", "PS", "SG"
    ])
    df["Giocatore"] = df["Cognome"] + " " + df["Nome"]
    
    # Casting numerico sicuro
    for col in ["Stipendio", "Costo"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
    
    # Suddivisione
    df_ps = df[df["PS"] == 1]
    df_sg = df[df["SG"] == 1]
    
    tot_ingaggi = df_ps["Stipendio"].sum()
    valore_rosa = df_ps["Costo"].sum() # Somma costi di acquisto
    n_ps = len(df_ps)
    n_sg = len(df_sg)
else:
    df = pd.DataFrame()
    df_ps = pd.DataFrame()
    df_sg = pd.DataFrame()
    tot_ingaggi = 0.0
    valore_rosa = 0.0
    n_ps = 0; n_sg = 0

st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("👥 Prima Squadra", n_ps)
k2.metric("🌱 Settore Giovanile", n_sg)
k3.metric("💶 Monte Ingaggi", f"{tot_ingaggi:,.2f} FM")
k4.metric("💰 Budget Residuo", f"{current_budget:,.2f} FM")
k5.metric("📌 Investimento Totale", f"{valore_rosa:,.2f} FM")

st.divider()

# --- 5. VISUALIZZAZIONE ---
if not df.empty:
    tab_ps, tab_sg, tab_scad, tab_graf = st.tabs(["🏟️ Prima Squadra", "🧒 Vivaio", "⚠️ Scadenze", "📊 Analisi"])
    
    # Configurazione Colonne Comune
    cols_cfg = {
        "Stipendio": st.column_config.NumberColumn(format="%.2f FM"),
        "Costo": st.column_config.NumberColumn("Costo Acquisto", format="%.2f FM"),
        "Ruolo": st.column_config.TextColumn(width="small"),
        "Giocatore": st.column_config.TextColumn(width="medium"),
    }

    with tab_ps:
        st.subheader(f"Rosa: {selected_team_name}")
        if not df_ps.empty:
            st.dataframe(
                df_ps[["Ruolo", "Giocatore", "Stipendio", "Anni", "Costo"]],
                use_container_width=True, hide_index=True,
                column_config=cols_cfg
            )
        else:
            st.info("Nessun giocatore in prima squadra.")
            
    with tab_sg:
        st.subheader("Settore Giovanile")
        if not df_sg.empty:
            st.dataframe(
                df_sg[["Ruolo", "Giocatore", "Stipendio", "Anni"]],
                use_container_width=True, hide_index=True,
                column_config=cols_cfg
            )
        else:
            st.info("Nessun giovane in rosa.")
            
    with tab_scad:
        st.subheader("Contratti in Scadenza (Fine Stagione)")
        st.caption("Giocatori con **1 anno** residuo di contratto.")
        df_scad = df[df["Anni"] == 1]
        if not df_scad.empty:
            st.dataframe(
                df_scad[["Ruolo", "Giocatore", "Stipendio"]],
                use_container_width=True, hide_index=True,
                column_config=cols_cfg
            )
        else:
            st.success("Nessun giocatore in scadenza imminente.")

    with tab_graf:
        st.subheader("Ripartizione Ingaggi per Ruolo")
        if not df_ps.empty:
            stats = df_ps.groupby("Ruolo")["Stipendio"].sum().reset_index()
            fig = px.pie(
                stats, values="Stipendio", names="Ruolo", 
                color="Ruolo", hole=0.4,
                color_discrete_map={"P":"gold", "D":"green", "C":"blue", "A":"red"}
            )
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Questa squadra non ha ancora tesserato giocatori.")