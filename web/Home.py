import streamlit as st
from utils import get_current_season_from_db, require_login, run_query, is_admin

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="FantaManager XIX",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. TITOLO E INTRODUZIONE ---
st.title("⚽ FantaManager XIX")
st.markdown("### Il gestionale per il tuo Fantacalcio Manageriale")

# --- 3. GESTIONE LOGIN ---
require_login()

# Utente loggato
user = st.session_state.get("user", "Utente")
role = st.session_state.get("role", "user")

st.success(f"👋 Benvenuto, **{user}**! (Ruolo: {role.upper()})")

# --- 4. CARICAMENTO DATI GLOBALI ---
with st.spinner("🔄 Caricamento dati..."):
    
    # A. Test Connessione DB
    try:
        if run_query("SELECT 1"):
            db_status = "✅ Online"
        else:
            db_status = "⚠️ Errore Query"
    except Exception as e:
        db_status = "❌ Offline"

    # B. Recupero Stagione (PERSISTENTE DAL DB)
    current_season = get_current_season_from_db()
    st.session_state["current_season"] = current_season

# --- 5. DASHBOARD RIEPILOGATIVA ---
st.divider()
st.subheader(f"📊 Situazione Stagione {current_season}")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Stato Database", value=db_status)

with col2:
    # Conteggio Squadre
    n_squadre = 0
    try:
        res_sq = run_query("SELECT COUNT(*) FROM fantasquadre")
        if res_sq: n_squadre = res_sq[0][0]
    except: pass
    st.metric(label="Squadre Iscritte", value=n_squadre)

with col3:
    # Conteggio Giocatori Totali
    n_gioc = 0
    try:
        res_g = run_query("SELECT COUNT(*) FROM giocatori")
        if res_g: n_gioc = res_g[0][0]
    except: pass
    st.metric(label="Giocatori in DB", value=n_gioc)