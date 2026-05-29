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
    "Pagina temporanea per correggere rapidamente i premi delle coppe. "
    "Dopo l'uso puoi eliminarla."
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

default_by_fase = {r[0]: float(r[1]) for r in current_prizes}

st.divider()
st.subheader("Nuova configurazione premi")

premio_gironi = st.number_input(
    "Premio Gironi (Ordine 1)",
    min_value=0.0,
    value=float(default_by_fase.get("Gironi", 0.0)),
    step=0.5
)

premio_semifinale = st.number_input(
    "Premio Semifinale (Ordine 2)",
    min_value=0.0,
    value=float(default_by_fase.get("Semifinale", default_by_fase.get("Semifinali", 0.0))),
    step=0.5
)

premio_finale = st.number_input(
    "Premio Finale (Ordine 3)",
    min_value=0.0,
    value=float(default_by_fase.get("Finale", 0.0)),
    step=0.5
)

premio_vittoria = st.number_input(
    "Premio Vittoria (Ordine 4)",
    min_value=0.0,
    value=float(default_by_fase.get("Vittoria", 0.0)),
    step=0.5
)

st.markdown("### Anteprima cumulativa")
st.write(f"- Eliminato ai Gironi → **{premio_gironi:.2f} FM**")
st.write(f"- Eliminato in Semifinale → **{premio_gironi + premio_semifinale:.2f} FM**")
st.write(f"- Finalista sconfitto → **{premio_gironi + premio_semifinale + premio_finale:.2f} FM**")
st.write(f"- Vincitore → **{premio_gironi + premio_semifinale + premio_finale + premio_vittoria:.2f} FM**")

st.info(
    "Questa operazione sostituisce completamente i premi della competizione selezionata."
)

confirm = st.checkbox("Confermo di voler sostituire i premi di questa competizione")

if st.button("💾 Applica correzione", type="primary", disabled=not confirm):
    ops = [
        ("DELETE FROM premi_competizioni WHERE CompetizioneID = :cid", {"cid": selected_id}),
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
        (
            """
            INSERT INTO premi_competizioni (CompetizioneID, Fase, Premio, Ordine)
            VALUES (:cid, :fase, :premio, :ordine)
            """,
            {"cid": selected_id, "fase": "Vittoria", "premio": premio_vittoria, "ordine": 4}
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