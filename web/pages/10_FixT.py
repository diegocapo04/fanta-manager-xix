import streamlit as st
from utils import require_login, is_admin, check_connection, run_query, run_transaction_batch, get_current_season_from_db

st.set_page_config(page_title="Fix Premi Coppe", page_icon="🛠️", layout="centered")

require_login()
check_connection()

if not is_admin():
    st.error("⛔ Accesso riservato agli amministratori.")
    st.stop()

current_season = get_current_season_from_db()

st.title("🛠️ Fix Premi Coppe")
st.caption(f"Stagione corrente: {current_season}")

st.warning(
    "Questa pagina serve solo per correggere rapidamente le fasi premio delle coppe. "
    "Usala una volta, verifica il risultato, poi eliminala."
)

comps = run_query(
    """
    SELECT ID, Nome, Tipo
    FROM competizioni
    WHERE Stagione = :s AND Tipo = 'Coppa'
    ORDER BY Nome
    """,
    {"s": current_season}
) or []

if not comps:
    st.info("Nessuna competizione di tipo Coppa trovata.")
    st.stop()

comp_map = {f"{nome} (ID {cid})": cid for cid, nome, _ in comps}
selected_label = st.selectbox("Seleziona la competizione da correggere", list(comp_map.keys()))
selected_id = comp_map[selected_label]

current_prizes = run_query(
    """
    SELECT Fase, Premio, Ordine
    FROM premi_competizioni
    WHERE CompetizioneID = :cid
    ORDER BY Ordine
    """,
    {"cid": selected_id}
) or []

st.subheader("Configurazione attuale")
if current_prizes:
    st.dataframe(
        [{"Fase": r[0], "Premio": float(r[1]), "Ordine": int(r[2])} for r in current_prizes],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Nessun premio configurato per questa competizione.")

st.divider()
st.subheader("Nuova configurazione")

st.markdown(
    "Imposta le tre fasi reali della coppa nel tuo formato:\n"
    "- Gironi\n"
    "- Semifinale\n"
    "- Finale"
)

default_map = {int(r[2]): float(r[1]) for r in current_prizes} if current_prizes else {}

premio_gironi = st.number_input("Premio Gironi (Ordine 1)", min_value=0.0, value=float(default_map.get(1, 0.0)), step=0.5)
premio_semifinale = st.number_input("Premio Semifinale (Ordine 2)", min_value=0.0, value=float(default_map.get(2, 0.0)), step=0.5)
premio_finale = st.number_input("Premio Finale (Ordine 3)", min_value=0.0, value=float(default_map.get(3, 0.0)), step=0.5)

st.info(
    "Questa operazione sostituisce completamente i premi della competizione selezionata "
    "nella tabella premi_competizioni."
)

confirm = st.checkbox("Confermo di voler sostituire i premi di questa competizione")

if st.button("💾 Applica correzione", type="primary", disabled=not confirm):
    ops = [
        (
            "DELETE FROM premi_competizioni WHERE CompetizioneID = :cid",
            {"cid": selected_id}
        ),
        (
            """
            INSERT INTO premi_competizioni (CompetizioneID, Fase, Premio, Ordine)
            VALUES (:cid, :fase, :premio, :ordine)
            """,
            {"cid": selected_id, "fase": "Gironi", "premio": premio_gironi, "ordine": 1}
        ),
        (
            """
            INSERT INTO premi_competizioni (CompetizioneID, Fase, Premio, Ordine)
            VALUES (:cid, :fase, :premio, :ordine)
            """,
            {"cid": selected_id, "fase": "Semifinale", "premio": premio_semifinale, "ordine": 2}
        ),
        (
            """
            INSERT INTO premi_competizioni (CompetizioneID, Fase, Premio, Ordine)
            VALUES (:cid, :fase, :premio, :ordine)
            """,
            {"cid": selected_id, "fase": "Finale", "premio": premio_finale, "ordine": 3}
        ),
    ]

    ok = run_transaction_batch(ops)

    if ok:
        st.success("✅ Premi aggiornati correttamente.")
        updated = run_query(
            """
            SELECT Fase, Premio, Ordine
            FROM premi_competizioni
            WHERE CompetizioneID = :cid
            ORDER BY Ordine
            """,
            {"cid": selected_id}
        ) or []

        st.dataframe(
            [{"Fase": r[0], "Premio": float(r[1]), "Ordine": int(r[2])} for r in updated],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.error("❌ Errore durante l'aggiornamento dei premi.")