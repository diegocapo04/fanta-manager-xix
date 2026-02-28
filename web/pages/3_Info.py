import streamlit as st
from utils import require_login, run_query, check_connection

st.set_page_config(page_title="Info Squadra", page_icon="ℹ️", layout="wide")

# --- 1. SETUP ---
require_login()
check_connection()

st.title("ℹ️ Dettagli Club & Infrastrutture")

# --- 2. SELEZIONE SQUADRA ---
teams = run_query("SELECT ID, Nome FROM fantasquadre ORDER BY Nome")

if not teams:
    st.warning("⚠️ Nessuna squadra disponibile.")
    st.stop()

team_dict = {row[1]: row[0] for row in teams}

col_sel, col_space = st.columns([1, 2])
with col_sel:
    selected_team_name = st.selectbox("Seleziona Club", list(team_dict.keys()))
    selected_team_id = team_dict[selected_team_name]

# --- 3. RECUPERO DATI ---

def get_team_info(tid):
    """Recupera dati da 'fantasquadre' (Nome, CreditiResidui)"""
    q = "SELECT Nome, CreditiResidui FROM fantasquadre WHERE ID = :id"
    res = run_query(q, {"id": tid})
    if res:
        # Conversione esplicita a float per sicurezza
        return (res[0][0], float(res[0][1] or 0.0))
    return (selected_team_name, 0.0)

def get_stadium(tid):
    q = "SELECT Livello, IncassoPartita, Costo FROM stadi WHERE SquadraID = :tid"
    res = run_query(q, {"tid": tid})
    if res:
        return {
            "Livello":   int(res[0][0] or 1),
            "Incasso":   float(res[0][1] or 0.0),
            "CostoOrig": float(res[0][2] or 0.0),
            "Esiste":    True
        }
    else:
        return {
            "Livello":   0,
            "Incasso":   0.0,
            "CostoOrig": 0.0,
            "Esiste":    False
        }

def get_youth_sector(tid):
    """Recupera dati settore giovanile: slot acquistati, slot max, e giovani tesserati."""
    q = "SELECT SlotAcquistati, SlotMax FROM settori_giovanili WHERE SquadraID = :tid"
    res = run_query(q, {"tid": tid})
    slot_acq = int(res[0][0]) if res else 0
    slot_max = int(res[0][1]) if res else 0
    # Conta giovani attualmente tesserati
    q2 = "SELECT COUNT(*) FROM contratti WHERE SquadraID = :tid AND SettoreGiovanile = 1"
    res2 = run_query(q2, {"tid": tid})
    occupati = int(res2[0][0]) if res2 else 0
    return {"slot_acquistati": slot_acq, "slot_max": slot_max, "occupati": occupati}

# Esecuzione Query
info = get_team_info(selected_team_id) # (Nome, CreditiResidui)
stadium = get_stadium(selected_team_id)
youth = get_youth_sector(selected_team_id)

# --- 4. DASHBOARD UI ---
st.divider()

# HEADER SQUADRA
c1, c2 = st.columns([1, 5])
with c1:
    # Logo finto con iniziale
    initial = selected_team_name[0]
    st.markdown(f"""
    <div style='background-color:#1E88E5; color:white; font-size:40px; 
    border-radius:15px; width:80px; height:80px; display:flex; 
    align-items:center; justify_content:center;'><b>{initial}</b></div>
    """, unsafe_allow_html=True)
with c2:
    st.header(info[0])
    # Mostra i Crediti Residui (il vero budget dal DB)
    st.markdown(f"💰 Budget Disponibile: **{info[1]:,.2f} FM**")

st.divider()

# SEZIONE STADIO + VIVAIO
col_stadio, col_vivaio, col_palm = st.columns([2, 2, 1])

with col_stadio:
    st.subheader("🏟️ Stadio")
    st.info(f"Stadio di **{selected_team_name}** — Livello {stadium['Livello']}")

    st.markdown("##### 📊 Rendimento Match Casalingo")

    st.metric(
        "Incasso Netto a Partita",
        f"{stadium['Incasso']:,.2f} FM",
        help="Guadagno pulito per ogni partita in casa"
    )

    if stadium['Esiste']:
        st.caption(f"Valore Asset Impianto: {stadium['CostoOrig']:,.2f} FM")

with col_vivaio:
    st.subheader("🌱 Settore Giovanile")
    liberi = youth["slot_acquistati"] - youth["occupati"]
    v1, v2 = st.columns(2)
    v1.metric("Slot Acquistati", f"{youth['slot_acquistati']} / {youth['slot_max']}")
    v2.metric("Slot Disponibili", f"{liberi}", help="Slot acquistati meno giovani attualmente tesserati")
    st.metric("Giovani Tesserati", youth["occupati"])

with col_palm:
    st.subheader("🏆 Palmares")
    st.caption("Nessun dato storico disponibile.")