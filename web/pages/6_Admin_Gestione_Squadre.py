import streamlit as st
import pandas as pd
from utils import require_login, run_query, is_admin, check_connection, run_transaction_batch, get_current_season_from_db 

st.set_page_config(page_title="Admin Squadre", page_icon="🏟️", layout="wide")

# --- 1. SETUP ---
require_login()
check_connection()

if not is_admin():
    st.error("⛔ Accesso riservato agli amministratori.")
    st.stop()

st.title("🏟️ Gestione Squadre e Strutture")

# --- 2. FUNZIONI DATI ---
def get_teams_data():
    query = """
    SELECT 
        fs.ID, fs.Nome, fs.CreditiResidui,
        s.Livello, s.IncassoPartita, s.Costo,
        sg.SlotAcquistati, sg.SlotMax
    FROM fantasquadre fs
    LEFT JOIN stadi s ON fs.ID = s.SquadraID
    LEFT JOIN settori_giovanili sg ON fs.ID = sg.SquadraID
    ORDER BY fs.Nome
    """
    return run_query(query)


def upsert_stadium(team_id, livello, incasso, costo):
    check = run_query("SELECT ID FROM stadi WHERE SquadraID = :tid", {"tid": team_id})
    if check:
        q = "UPDATE stadi SET Livello=:l, IncassoPartita=:i, Costo=:c WHERE SquadraID=:tid"
    else:
        q = "INSERT INTO stadi (SquadraID, Livello, IncassoPartita, Costo) VALUES (:tid, :l, :i, :c)"
    try:
        run_query(q, {"tid": team_id, "l": livello, "i": incasso, "c": costo})
        return True
    except Exception as e:
        st.error(f"Errore DB: {e}")
        return False

def buy_youth_slot(team_id, current_slots, cost=20.0):
    """Aggiunge uno slot al settore giovanile e scala i soldi."""
    ops = []
    
    # 1. Scala soldi
    ops.append(("UPDATE fantasquadre SET CreditiResidui = CreditiResidui - :c WHERE ID = :tid", 
               {"c": cost, "tid": team_id}))
    
    # 2. Aggiorna o Crea record settore giovanile
    exists = run_query("SELECT SquadraID FROM settori_giovanili WHERE SquadraID = :tid", {"tid": team_id})
    
    if exists:
        q_slot = "UPDATE settori_giovanili SET SlotAcquistati = SlotAcquistati + 1 WHERE SquadraID = :tid"
        ops.append((q_slot, {"tid": team_id}))
    else:
        # Crea record (partendo da 1 slot acquistato)
        q_slot = "INSERT INTO settori_giovanili (SquadraID, SlotAcquistati, SlotMax) VALUES (:tid, 1, 5)"
        ops.append((q_slot, {"tid": team_id}))
        
    return run_transaction_batch(ops)

# --- 3. UI ---
data = get_teams_data()
if not data:
    st.warning("Nessuna squadra trovata.")
    st.stop()

# Mappa dati
# row indices: 0:ID, 1:Nome, 2:Crediti, 3:Livello, 4:IncassoPartita, 5:Costo, 6:SlotAcq, 7:SlotMax
teams_map = {row[1]: row for row in data}
sel_team_name = st.selectbox("Seleziona Squadra da Gestire", list(teams_map.keys()))
target = teams_map[sel_team_name]
tid = target[0]

# TABELLA RIASSUNTIVA
st.divider()
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
col_kpi1.metric("Budget Attuale", f"{float(target[2] or 0):,.2f} FM")
col_kpi2.metric("Stadio", target[3] if target[3] else "Non presente")
col_kpi3.metric("Slot Giovanili", f"{target[6] or 0} / 5")

st.divider()

tab_stadio, tab_vivaio, tab_budget = st.tabs(["🏗️ Stadio", "🌱 Settore Giovanile", "💵 Rettifica Budget"])

# === TAB 1: STADIO ===
with tab_stadio:
    st.subheader("Parametri Stadio")
    with st.form("stadio_form"):
        c1, c2 = st.columns(2)
        with c1:
            s_liv  = c1.number_input("Livello (1-5)", 1, 5, int(target[3] or 1))
            s_inc  = c1.number_input("Incasso Partita (FM)", 0.0, step=1.0,
                                     value=float(target[4] or 10.0))
        with c2:
            s_cost = c2.number_input("Costo Costruzione/Valore (FM)", 0.0, step=10.0,
                                     value=float(target[5] or 100.0),
                                     help="Costo una tantum per costruire/comprare questo livello.")

        if st.form_submit_button("💾 Salva Dati Stadio"):
            if upsert_stadium(tid, s_liv, s_inc, s_cost):
                st.success("Stadio aggiornato!")
                st.rerun()

# === TAB 2: SETTORE GIOVANILE ===
with tab_vivaio:
    st.subheader("Espansione Vivaio")
    st.info("Ogni slot aggiuntivo permette di tesserare un giovane in più.")
    
    current_slots = int(target[6] or 0)
    max_slots = 5
    costo_slot = 20.0
    
    col_v1, col_v2 = st.columns([1, 2])
    with col_v1:
        st.metric("Slot Attuali", f"{current_slots}", f"Max {max_slots}")
    
    with col_v2:
        if current_slots < max_slots:
            st.write(f"Costo prossimo slot: **{costo_slot:.2f} FM**")

            if st.button("➕ Acquista Slot (+1)"):
                if buy_youth_slot(tid, current_slots, costo_slot):
                    st.balloons()
                    st.success("Slot acquistato con successo!")
                    st.rerun()
        else:
            st.success("🎉 Strutture giovanili al massimo livello!")

# === TAB 3: RETTIFICA BUDGET ===
with tab_budget:
    st.subheader("Correzione Manuale Crediti")
    st.warning("Da usare solo per penalizzazioni o bonus amministrativi.")
    
    with st.form("budget_fix"):
        new_b = st.number_input("Nuovo Saldo Totale (FM)", step=1.0, value=float(target[2] or 0))
        
        if st.form_submit_button("⚠️ Sovrascrivi Budget"):
            try:
                run_query("UPDATE fantasquadre SET CreditiResidui = :b WHERE ID = :tid", 
                         {"b": new_b, "tid": tid})
                st.success("Budget aggiornato.")
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")