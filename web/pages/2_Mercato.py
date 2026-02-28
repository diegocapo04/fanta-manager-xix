import streamlit as st
import pandas as pd
import plotly.express as px
from utils import require_login, run_query, check_connection, get_current_season_from_db 

st.set_page_config(page_title="Osservatorio Mercato", page_icon="💰", layout="wide")

# --- 1. SETUP ---
require_login()
check_connection()

# Recupera la stagione vera dal DB
current_season = get_current_season_from_db()
st.title(f"💰 Osservatorio Mercato ({current_season})")

# --- 2. FILTRI ---
with st.sidebar:
    st.header("🔍 Filtri")
    
    # Recupero stagioni disponibili
    res_seasons = run_query("SELECT DISTINCT Stagione FROM operazioni_mercato ORDER BY Stagione DESC")
    avail_seasons = [r[0] for r in res_seasons] if res_seasons else [current_season]
    
    # Default sulla stagione corrente
    default_idx = 0
    if current_season in avail_seasons:
        default_idx = avail_seasons.index(current_season)

    sel_season = st.selectbox("Stagione", avail_seasons, index=default_idx)
    sel_session = st.radio("Sessione", ["Tutte", "Estiva", "Invernale"], index=0)

# --- 3. DATI ---
def get_market_data(season, session):
    sql = """
    SELECT 
        fs.Nome AS Squadra, 
        g.Nome AS NomeG, 
        g.Cognome AS CognomeG, 
        g.Ruolo, 
        op.Tipo, 
        op.Costo, 
        op.Sessione, 
        op.Note 
    FROM operazioni_mercato op 
    JOIN fantasquadre fs ON op.SquadraID = fs.ID 
    JOIN giocatori g ON op.GiocatoreID = g.ID 
    WHERE op.Stagione = :season 
    """
    params = {"season": season}
    
    if session != "Tutte":
        sql += " AND op.Sessione = :sess"
        params["sess"] = session
        
    sql += " ORDER BY op.ID DESC" 
    
    return run_query(sql, params)

raw_data = get_market_data(sel_season, sel_session)

# --- 4. VISUALIZZAZIONE ---
if raw_data:
    df = pd.DataFrame(raw_data, columns=[
        "Squadra", "Nome", "Cognome", "Ruolo", "Tipo", "Costo", "Sessione", "Note"
    ])
    
    # --- FIX CRITICO: CONVERSIONE TIPI (Decimal -> Float) ---
    df["Costo"] = pd.to_numeric(df["Costo"], errors='coerce').fillna(0.0)
    
    df["Giocatore"] = df["Cognome"] + " " + df["Nome"]
    
    # KPI
    tot_ops = len(df)
    vol_affari = df["Costo"].abs().sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Movimenti Totali", tot_ops)
    c2.metric("Volume Affari", f"{vol_affari:,.2f} FM")
    
    # Top Spender
    spese = df[df["Costo"] > 0].groupby("Squadra")["Costo"].sum()
    if not spese.empty:
        top_spender = spese.idxmax()
        val_spender = spese.max()
        c3.metric("Top Spender", top_spender, f"{val_spender:,.2f} FM")
    else:
        c3.metric("Top Spender", "N/D", "0.00 FM")
    
    st.divider()
    
    # --- TABELLA ---
    st.subheader(f"📜 Lista Movimenti - {sel_season}")
    
    st.dataframe(
        df[["Sessione", "Squadra", "Giocatore", "Ruolo", "Tipo", "Costo", "Note"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Costo": st.column_config.NumberColumn(
                "Importo (FM)", 
                format="%.2f",
                help="Positivo = Spesa (Acquisto), Negativo = Incasso (Cessione)"
            ),
            "Note": st.column_config.TextColumn(width="medium")
        }
    )
    
    # --- GRAFICI ---
    st.divider()
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("📊 Spese vs Incassi")
        # Aggreghiamo per squadra: Spese (Costo > 0) e Incassi (Costo < 0)
        df["Categoria"] = df["Costo"].apply(lambda x: "Spesa" if x > 0 else "Incasso")
        df["ValoreAssoluto"] = df["Costo"].abs()
        
        # Raggruppa per avere barre pulite
        df_bar = df.groupby(["Squadra", "Categoria"])["ValoreAssoluto"].sum().reset_index()
        
        fig_bar = px.bar(
            df_bar, 
            x="Squadra", 
            y="ValoreAssoluto", 
            color="Categoria",
            barmode="group",
            title="Flussi di Cassa per Squadra",
            color_discrete_map={"Spesa": "#FF4B4B", "Incasso": "#00CC96"} 
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_g2:
        st.subheader("🍰 Ruoli Scambiati")
        df_ruoli = df["Ruolo"].value_counts().reset_index()
        fig_pie = px.pie(
            df_ruoli, 
            names="Ruolo", 
            values="count", 
            title="Giocatori movimentati per Ruolo",
            hole=0.4,
            color="Ruolo",
            color_discrete_map={"P": "gold", "D": "green", "C": "blue", "A": "red"}
        )
        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning(f"Nessuna operazione trovata per la stagione {sel_season}.")