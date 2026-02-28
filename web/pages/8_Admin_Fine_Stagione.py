import streamlit as st
import pandas as pd
from utils import (
    require_login, run_query, is_admin, check_connection,
    run_transaction_batch, get_current_season_from_db
)

st.set_page_config(page_title="Fine Stagione", page_icon="🏁", layout="wide")

require_login()
check_connection()

if not is_admin():
    st.error("⛔ Accesso riservato agli amministratori.")
    st.stop()

current_season = get_current_season_from_db()
st.title(f"🏁 Chiusura Stagione {current_season}")
st.markdown("---")


# ======================================================================
# FUNZIONI LOGICHE
# ======================================================================

def get_next_season_str(season):
    try:
        parts = season.split("/")
        y1, y2 = int(parts[0]), int(parts[1])
        return f"{y1+1}/{y2+1}"
    except Exception:
        return "Nuova Stagione"


def get_season_summary(season):
    res_e = run_query("SELECT COUNT(*) FROM contratti WHERE AnniDurata <= 1")
    res_c = run_query(
        "SELECT COUNT(DISTINCT CompetizioneID) FROM partite WHERE Stagione = :s",
        {"s": season}
    )
    return {
        "scadenze":     res_e[0][0] if res_e else 0,
        "competizioni": res_c[0][0] if res_c else 0,
    }


def get_total_wages():
    res = run_query("""
        SELECT fs.Nome, SUM(c.Stipendio) AS Totale
        FROM contratti c
        JOIN fantasquadre fs ON c.SquadraID = fs.ID
        GROUP BY fs.ID, fs.Nome
        ORDER BY Totale DESC
    """)
    return res or []


def get_comp_prizes(comp_id):
    """Recupera fasi e premi di una competizione in ordine crescente."""
    return run_query(
        "SELECT Fase, Premio, Ordine FROM premi_competizioni "
        "WHERE CompetizioneID = :cid ORDER BY Ordine",
        {"cid": comp_id}
    ) or []


def get_campionato_standings(season, comp_id):
    """Calcola la classifica finale del campionato."""
    q = """
    WITH Stats AS (
        SELECT SquadraCasaID AS SquadraID,
               CASE WHEN GolCasa > GolOspite THEN 3
                    WHEN GolCasa = GolOspite THEN 1
                    ELSE 0 END AS Punti,
               GolCasa - GolOspite AS DR
        FROM partite
        WHERE Giocata = 1 AND Stagione = :s AND CompetizioneID = :cid
        UNION ALL
        SELECT SquadraOspiteID,
               CASE WHEN GolOspite > GolCasa THEN 3
                    WHEN GolOspite = GolCasa THEN 1
                    ELSE 0 END,
               GolOspite - GolCasa
        FROM partite
        WHERE Giocata = 1 AND Stagione = :s AND CompetizioneID = :cid
    )
    SELECT fs.ID, fs.Nome, SUM(Punti) AS Punti, SUM(DR) AS DR
    FROM Stats ms
    JOIN fantasquadre fs ON ms.SquadraID = fs.ID
    GROUP BY fs.ID, fs.Nome
    ORDER BY Punti DESC, DR DESC, fs.Nome ASC
    """
    return run_query(q, {"s": season, "cid": comp_id}) or []


def assign_campionato_prizes(season, comp_id):
    """Assegna i premi del campionato basandosi sulla classifica finale."""
    standings = get_campionato_standings(season, comp_id)
    prizes    = get_comp_prizes(comp_id)
    # Per campionato: Ordine == posizione (1-10)
    prize_map = {p[2]: float(p[1]) for p in prizes}

    ops      = []
    log_msgs = []
    medals   = {1: "🥇", 2: "🥈", 3: "🥉"}

    for i, row in enumerate(standings):
        pos       = i + 1
        team_id, team_name, punti, dr = row
        amount    = prize_map.get(pos, 0.0)
        medal     = medals.get(pos, f"#{pos}")
        if amount > 0:
            ops.append((
                "UPDATE fantasquadre SET CreditiResidui = CreditiResidui + :m WHERE ID = :tid",
                {"m": amount, "tid": team_id}
            ))
        log_msgs.append(
            f"{medal} **{team_name}** ({int(punti)} pt, DR {int(dr):+d}) → **+{amount:.2f} FM**"
        )

    if not ops:
        return True, log_msgs + ["ℹ️ Nessun premio da assegnare (importi a zero)."]

    ok = run_transaction_batch(ops)
    return ok, log_msgs


def assign_coppa_prizes(phase_assignments, phases):
    """
    Assegna premi cumulativi per una competizione a eliminazione.

    phase_assignments: lista di (team_id, team_name, ordine_max | None)
    phases: lista di (Fase, Premio, Ordine) ordinate per Ordine crescente
    """
    ops      = []
    log_msgs = []

    for team_id, team_name, max_ordine in phase_assignments:
        if max_ordine is None:
            continue
        total     = sum(float(p[1]) for p in phases if p[2] <= max_ordine)
        fase_name = next((p[0] for p in phases if p[2] == max_ordine), "?")
        if total > 0:
            ops.append((
                "UPDATE fantasquadre SET CreditiResidui = CreditiResidui + :m WHERE ID = :tid",
                {"m": total, "tid": team_id}
            ))
            log_msgs.append(
                f"✅ **{team_name}** → {fase_name} → **+{total:.2f} FM**"
            )

    if not ops:
        return True, ["ℹ️ Nessun premio da assegnare."]

    ok = run_transaction_batch(ops)
    return ok, log_msgs


def execute_season_rollover(current_season, next_season):
    ops = []

    # 1. Scala stipendi annuali da ogni squadra
    ops.append(("""
        UPDATE fantasquadre fs
        JOIN (
            SELECT SquadraID, SUM(Stipendio) AS TotaleStipendi
            FROM contratti
            GROUP BY SquadraID
        ) AS sub ON fs.ID = sub.SquadraID
        SET fs.CreditiResidui = fs.CreditiResidui - sub.TotaleStipendi
    """, {}))

    # 2. Decrementa tutti i contratti di 1 anno
    ops.append(("UPDATE contratti SET AnniDurata = AnniDurata - 1", {}))

    # 3. Elimina i contratti scaduti
    ops.append(("DELETE FROM contratti WHERE AnniDurata <= 0", {}))

    # 4. Aggiorna la stagione nel DB
    ops.append((
        "UPDATE configurazione SET Valore = :ns WHERE Chiave = 'stagione_corrente'",
        {"ns": next_season}
    ))

    return run_transaction_batch(ops)


# ======================================================================
# UI — INTESTAZIONE
# ======================================================================

next_season = get_next_season_str(current_season)

col_head1, col_head2 = st.columns(2)
col_head1.info(f"📅 Stagione Attuale: **{current_season}**")
col_head2.success(f"🔜 Prossima Stagione: **{next_season}**")

summary = get_season_summary(current_season)

st.subheader("📊 Stato Stagione")
kpi1, kpi2 = st.columns(2)
kpi1.metric("🏆 Competizioni con partite",  summary["competizioni"])
kpi2.metric("⚠️ Contratti in Scadenza",     summary["scadenze"],
            help="Diventeranno svincolati dopo il rollover.")

wages = get_total_wages()
if wages:
    with st.expander("💶 Anteprima deduzione stipendi per squadra"):
        df_w = pd.DataFrame(wages, columns=["Squadra", "Totale Stipendi (FM)"])
        df_w["Totale Stipendi (FM)"] = df_w["Totale Stipendi (FM)"].astype(float)
        st.dataframe(df_w, use_container_width=True, hide_index=True)
        st.caption(
            f"Totale complessivo: **{df_w['Totale Stipendi (FM)'].sum():,.2f} FM**"
        )

st.divider()

# ======================================================================
# STEP 1 — ASSEGNAZIONE PREMI
# ======================================================================

st.header("⚙️ Step 1 — Assegnazione Premi")
st.warning(
    "⚠️ I premi vanno assegnati **una sola volta** prima del rollover. "
    "Eseguire due volte accredita i premi due volte."
)

comps = run_query(
    "SELECT ID, Nome, Tipo FROM competizioni WHERE Stagione = :s ORDER BY Nome",
    {"s": current_season}
) or []

if not comps:
    st.info("Nessuna competizione trovata per questa stagione.")
else:
    tabs = st.tabs([c[1] for c in comps])

    for i, (c_id, c_nome, c_tipo) in enumerate(comps):
        with tabs[i]:
            prizes = get_comp_prizes(c_id)

            if not prizes:
                st.warning(
                    f"⚠️ Nessun premio configurato nella tabella `premi_competizioni` "
                    f"per **{c_nome}** (ID={c_id})."
                )
                continue

            # ----------------------------------------------------------------
            # CAMPIONATO — assegnazione automatica da classifica
            # ----------------------------------------------------------------
            if c_tipo == 'Campionato':
                standings = get_campionato_standings(current_season, c_id)

                if not standings:
                    st.info(f"Nessuna partita giocata in **{c_nome}**.")
                    continue

                prize_map = {p[2]: float(p[1]) for p in prizes}  # ordine(=pos) → FM
                medals    = {1: "🥇", 2: "🥈", 3: "🥉"}

                rows = []
                for idx, row in enumerate(standings):
                    pos = idx + 1
                    _, team_name, punti, dr = row
                    rows.append({
                        "Pos":        medals.get(pos, str(pos)),
                        "Squadra":    team_name,
                        "Punti":      int(punti),
                        "DR":         f"{int(dr):+d}",
                        "Premio (FM)": prize_map.get(pos, 0.0),
                    })

                df_preview = pd.DataFrame(rows)
                st.subheader(f"🏆 Classifica Finale — {c_nome}")
                st.dataframe(df_preview, use_container_width=True, hide_index=True)
                st.caption(
                    f"Totale premi da distribuire: **{df_preview['Premio (FM)'].sum():.2f} FM**"
                )

                if st.button(
                    f"💰 Assegna Premi {c_nome}", type="primary", key=f"btn_{c_id}"
                ):
                    with st.spinner("Assegnazione in corso..."):
                        ok, logs = assign_campionato_prizes(current_season, c_id)
                    if ok:
                        st.success("✅ Premi assegnati!")
                    else:
                        st.error("❌ Errore DB durante l'assegnazione.")
                    for msg in logs:
                        st.markdown(msg)

            # ----------------------------------------------------------------
            # COPPA — selezione manuale della fase massima per squadra
            # ----------------------------------------------------------------
            else:
                st.subheader(f"🏆 {c_nome} — Fase massima raggiunta per squadra")

                # Riepilogo premi configurati + cumulativi
                with st.expander("📋 Premi configurati (cumulativi)"):
                    rows_cfg = []
                    running  = 0.0
                    for fase, premio, _ in prizes:
                        running += float(premio)
                        rows_cfg.append({
                            "Fase":            fase,
                            "Premio fase (FM)": float(premio),
                            "Tot. cumulato":   running,
                        })
                    st.dataframe(
                        pd.DataFrame(rows_cfg),
                        use_container_width=True,
                        hide_index=True
                    )

                teams = run_query(
                    "SELECT ID, Nome FROM fantasquadre ORDER BY Nome"
                ) or []

                phase_options = ["Non partecipante"] + [p[0] for p in prizes]
                phase_ordine  = {p[0]: p[2] for p in prizes}  # Fase → Ordine

                st.markdown("Seleziona la **fase massima raggiunta** per ogni squadra:")

                phase_assignments = []
                cols_per_row      = 2

                for row_i in range(0, len(teams), cols_per_row):
                    row_teams = teams[row_i: row_i + cols_per_row]
                    cols      = st.columns(cols_per_row)
                    for col_i, (tid, tname) in enumerate(row_teams):
                        with cols[col_i]:
                            selected = st.selectbox(
                                tname,
                                options=phase_options,
                                key=f"phase_{c_id}_{tid}"
                            )
                            if selected != "Non partecipante":
                                ord_max     = phase_ordine[selected]
                                total_prize = sum(
                                    float(p[1]) for p in prizes if p[2] <= ord_max
                                )
                                st.caption(f"Premio cumulato: **+{total_prize:.2f} FM**")
                            else:
                                ord_max = None
                                st.caption("Premio: 0 FM")
                            phase_assignments.append((tid, tname, ord_max))

                # Tabella riepilogo premi
                st.markdown("#### Riepilogo")
                riepilogo = []
                for tid, tname, ord_max in phase_assignments:
                    if ord_max is not None:
                        fase_name = next(
                            (p[0] for p in prizes if p[2] == ord_max), "?"
                        )
                        total = sum(float(p[1]) for p in prizes if p[2] <= ord_max)
                    else:
                        fase_name = "—"
                        total     = 0.0
                    riepilogo.append({
                        "Squadra":    tname,
                        "Fase":       fase_name,
                        "Premio (FM)": total,
                    })

                df_riepilogo = pd.DataFrame(riepilogo)
                st.dataframe(df_riepilogo, use_container_width=True, hide_index=True)
                st.caption(
                    f"Totale premi da distribuire: "
                    f"**{df_riepilogo['Premio (FM)'].sum():.2f} FM**"
                )

                if st.button(
                    f"💰 Assegna Premi {c_nome}", type="primary", key=f"btn_{c_id}"
                ):
                    with st.spinner("Assegnazione in corso..."):
                        ok, logs = assign_coppa_prizes(phase_assignments, prizes)
                    if ok:
                        st.success("✅ Premi assegnati!")
                    else:
                        st.error("❌ Errore DB durante l'assegnazione.")
                    for msg in logs:
                        st.markdown(msg)

# ======================================================================
# STEP 2 — ROLLOVER STAGIONE
# ======================================================================

st.divider()
st.header("⚙️ Step 2 — Chiusura e Nuova Stagione")
st.warning(
    "⚠️ ATTENZIONE: Questa procedura è **irreversibile**. "
    "Assicurati di aver inserito TUTTI i risultati delle partite "
    "e di aver assegnato tutti i premi (Step 1)."
)

st.markdown(f"""
- Deduce gli stipendi annuali dal budget di ogni squadra
- Invecchia i contratti (−1 anno)
- Svincola i giocatori con contratto scaduto
- Imposta la stagione a **{next_season}**
""")

confirm = st.checkbox(f"Confermo la chiusura della stagione **{current_season}**")
if st.button("🏁 AVVIA NUOVA STAGIONE", type="secondary", disabled=not confirm):
    with st.spinner("⏳ Elaborazione fine anno..."):
        ok = execute_season_rollover(current_season, next_season)
    if ok:
        st.balloons()
        st.success("✅ STAGIONE CHIUSA CON SUCCESSO!")
        st.markdown(f"### 🎉 Benvenuto nella stagione {next_season}!")
        st.session_state["current_season"] = next_season
        st.rerun()
    else:
        st.error("❌ Errore DB durante il rollover.")
