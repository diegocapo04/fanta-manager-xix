import streamlit as st
import pandas as pd
from utils import (
    require_login, run_query, run_transaction_batch,
    is_admin, check_connection, get_current_season_from_db
)

st.set_page_config(page_title="Gestione Mercato", page_icon="⚖️", layout="wide")

def fmt_money(value):
    return f"{float(value):,.2f} FM" if value else "0.00 FM"

require_login()
check_connection()

if not is_admin():
    st.error("⛔ Accesso riservato agli amministratori.")
    st.stop()

current_season = get_current_season_from_db()
st.title(f"⚖️ Gestione Mercato ({current_season})")

# ======================================================================
# FUNZIONI DATI
# ======================================================================

def get_teams():
    res = run_query("SELECT ID, Nome, CreditiResidui FROM fantasquadre ORDER BY Nome")
    return {row[1]: {"id": row[0], "budget": float(row[2] or 0.0)} for row in res} if res else {}

def get_all_players():
    res = run_query("SELECT ID, Cognome, Nome, Ruolo, ValoreMercato FROM giocatori ORDER BY Cognome")
    return {
        f"{r[1]} {r[2]}": {"id": r[0], "n": r[2], "c": r[1], "r": r[3], "v": float(r[4] or 0.0)}
        for r in res
    } if res else {}

def get_free_agents():
    res = run_query("""
        SELECT g.ID, g.Nome, g.Cognome, g.Ruolo, g.ValoreMercato
        FROM giocatori g
        WHERE g.ID NOT IN (SELECT GiocatoreID FROM contratti)
        ORDER BY g.Cognome
    """)
    return {
        f"{r[2]} {r[1]} ({r[3]})": {"id": r[0], "val": float(r[4] or 0.0)}
        for r in res
    } if res else {}

def get_team_players(team_id):
    res = run_query("""
        SELECT g.ID, g.Nome, g.Cognome, g.Ruolo, c.Stipendio, g.ValoreMercato, c.AnniDurata
        FROM contratti c JOIN giocatori g ON c.GiocatoreID = g.ID
        WHERE c.SquadraID = :tid ORDER BY g.Cognome
    """, {"tid": team_id})
    return {
        f"{r[2]} {r[1]} ({r[3]})": {
            "id": r[0], "stipendio": float(r[4] or 0.0),
            "valore": float(r[5] or 0.0), "anni": int(r[6])
        }
        for r in res
    } if res else {}

# ======================================================================
# UI — 5 tab principali
# ======================================================================

teams_data = get_teams()
teams_map  = {k: v["id"] for k, v in teams_data.items()}

t_anag, t_acq, t_cess, t_scambio, t_rinn = st.tabs([
    "👤 Gestione Giocatori",
    "➕ Acquisto",
    "👋 Svincolo",
    "🔄 Scambio",
    "📝 Rinnovo",
])

# ==================== TAB 1: GESTIONE DB ====================
with t_anag:
    st.subheader("Database Giocatori")
    sub_view, sub_new, sub_edit = st.tabs(["📋 Visualizza", "➕ Nuovo", "✏️ Modifica / Elimina"])

    with sub_view:
        rows = run_query("""
            SELECT g.ID, g.Cognome, g.Nome, g.Ruolo, g.ValoreMercato,
                   COALESCE(fs.Nome, '— Svincolato') AS Squadra
            FROM giocatori g
            LEFT JOIN contratti c  ON g.ID = c.GiocatoreID
            LEFT JOIN fantasquadre fs ON c.SquadraID = fs.ID
            ORDER BY g.Cognome
        """)
        if rows:
            df = pd.DataFrame(rows, columns=["ID", "Cognome", "Nome", "Ruolo", "Valore (FM)", "Squadra"])
            df["Valore (FM)"] = df["Valore (FM)"].astype(float)

            f1, f2, f3 = st.columns(3)
            ruolo_f   = f1.multiselect("Ruolo",   ["P","D","C","A"], default=["P","D","C","A"])
            squadre_f = f2.multiselect("Squadra", sorted(df["Squadra"].unique().tolist()),
                                       default=sorted(df["Squadra"].unique().tolist()))
            search_f  = f3.text_input("🔍 Cerca")

            mask = (
                df["Ruolo"].isin(ruolo_f) &
                df["Squadra"].isin(squadre_f) &
                df["Cognome"].str.lower().str.contains(search_f.lower(), na=False)
            )
            st.dataframe(df[mask].drop(columns=["ID"]), use_container_width=True, hide_index=True)
            st.caption(f"{mask.sum()} giocatori su {len(df)}")

    with sub_new:
        with st.form("new_player"):
            c1, c2 = st.columns(2)
            nome    = c1.text_input("Nome")
            cognome = c2.text_input("Cognome *")
            ruolo   = c1.selectbox("Ruolo", ["P", "D", "C", "A"])
            valore  = c2.number_input("Valore di Mercato (FM)", min_value=0.01, step=0.5, value=10.0)

            if st.form_submit_button("💾 Crea Giocatore", type="primary"):
                if cognome.strip():
                    dup = run_query(
                        "SELECT ID FROM giocatori WHERE Cognome=:c AND Nome=:n",
                        {"c": cognome.strip(), "n": nome.strip()}
                    )
                    if dup:
                        st.error(f"Giocatore già presente: {cognome} {nome}")
                    else:
                        run_query(
                            "INSERT INTO giocatori (Nome, Cognome, Ruolo, ValoreMercato) VALUES (:n,:c,:r,:v)",
                            {"n": nome.strip(), "c": cognome.strip(), "r": ruolo, "v": valore}
                        )
                        st.success(f"✅ Creato: {cognome} {nome} ({ruolo}) — {fmt_money(valore)}")
                        st.rerun()
                else:
                    st.error("Il cognome è obbligatorio.")

    with sub_edit:
        all_pl = get_all_players()

        def get_contract_full(giocatore_id):
            """Recupera il contratto completo (se esiste) per un giocatore, con tutti i campi."""
            res = run_query("""
                SELECT c.ID, c.SquadraID, fs.Nome, c.Stipendio, c.CostoAcquisto,
                    c.AnniDurata, c.StagioneFirma, c.PrimaSquadra, c.SettoreGiovanile
                FROM contratti c
                JOIN fantasquadre fs ON c.SquadraID = fs.ID
                WHERE c.GiocatoreID = :gid
            """, {"gid": giocatore_id})
            if not res:
                return None
            r = res[0]
            return {
                "contratto_id": r[0], "squadra_id": r[1], "squadra_nome": r[2],
                "stipendio": float(r[3] or 0.0), "costo_acquisto": float(r[4] or 0.0),
                "anni": int(r[5]), "stagione_firma": r[6],
                "prima_squadra": bool(r[7]), "settore_giovanile": bool(r[8]),
            }

        if all_pl:
            sel_p  = st.selectbox("Seleziona Giocatore", list(all_pl.keys()), key="sel_edit_player")
            data_p = all_pl[sel_p]
            contratto = get_contract_full(data_p["id"])

            st.divider()
            st.markdown("##### 👤 Dati Anagrafici")

            with st.form("edit_player_full"):
                c1, c2 = st.columns(2)
                new_n = c1.text_input("Nome",    data_p["n"])
                new_c = c2.text_input("Cognome", data_p["c"])
                new_r = c1.selectbox("Ruolo", ["P", "D", "C", "A"],
                                    index=["P", "D", "C", "A"].index(data_p["r"]))
                new_v = c2.number_input("Valore Mercato (FM)", min_value=1.0,
                                        step=0.5, value=data_p["v"])

                st.divider()
                st.markdown("##### 📄 Situazione Contrattuale")

                team_names = list(teams_map.keys())

                if contratto:
                    st.caption(
                        f"Attualmente sotto contratto con **{contratto['squadra_nome']}** "
                        f"(firmato stagione {contratto['stagione_firma']})"
                    )
                    default_idx = team_names.index(contratto["squadra_nome"]) if contratto["squadra_nome"] in team_names else 0

                    cc1, cc2 = st.columns(2)
                    new_team = cc1.selectbox("Squadra", team_names, index=default_idx, key="edit_team_sel")
                    new_stagione_firma = cc2.text_input("Stagione Firma", contratto["stagione_firma"])

                    cc3, cc4 = st.columns(2)
                    new_stipendio = cc3.number_input("Stipendio (FM)", min_value=0.0, step=0.5,
                                                    value=contratto["stipendio"])
                    new_costo = cc4.number_input("Costo Acquisto (FM)", min_value=0.0, step=0.5,
                                                value=contratto["costo_acquisto"])

                    cc5, cc6 = st.columns(2)
                    new_anni = cc5.number_input("Anni Durata Contratto", min_value=1, max_value=5,
                                                value=contratto["anni"])
                    new_settore = cc6.checkbox("Settore Giovanile", value=contratto["settore_giovanile"])

                    new_prima_squadra = st.checkbox("Prima Squadra", value=contratto["prima_squadra"])
                    svincola_flag = st.checkbox("🚫 Svincola il giocatore (rimuove il contratto)", value=False)
                else:
                    st.info("Giocatore attualmente **svincolato** — nessun contratto attivo.")
                    assegna_flag = st.checkbox("➕ Assegna a una squadra (crea nuovo contratto)", value=False)
                    new_team = None
                    if assegna_flag:
                        cc1, cc2 = st.columns(2)
                        new_team = cc1.selectbox("Squadra", team_names, key="edit_team_new")
                        new_stagione_firma = cc2.text_input("Stagione Firma", current_season)

                        cc3, cc4 = st.columns(2)
                        new_stipendio = cc3.number_input("Stipendio (FM)", min_value=0.0, step=0.5, value=1.0)
                        new_costo = cc4.number_input("Costo Acquisto (FM)", min_value=0.0, step=0.5, value=0.0)

                        cc5, cc6 = st.columns(2)
                        new_anni = cc5.number_input("Anni Durata Contratto", min_value=1, max_value=5, value=3)
                        new_settore = cc6.checkbox("Settore Giovanile", value=False)

                        new_prima_squadra = st.checkbox("Prima Squadra", value=True)

                st.divider()
                cs, cd = st.columns(2)
                do_save = cs.form_submit_button("💾 Salva Tutte le Modifiche", type="primary")
                do_del  = cd.form_submit_button("🗑️ Elimina Giocatore dal DB")

                if do_save:
                    ops = [
                        ("UPDATE giocatori SET Nome=:n, Cognome=:c, Ruolo=:r, "
                        "ValoreMercato=:v WHERE ID=:id",
                        {"n": new_n, "c": new_c, "r": new_r, "v": new_v, "id": data_p["id"]})
                    ]

                    if contratto:
                        if svincola_flag:
                            ops.append((
                                "DELETE FROM contratti WHERE ID=:cid",
                                {"cid": contratto["contratto_id"]}
                            ))
                        else:
                            new_team_id = teams_map[new_team]
                            ops.append((
                                "UPDATE contratti SET SquadraID=:t, Stipendio=:s, CostoAcquisto=:co, "
                                "AnniDurata=:a, StagioneFirma=:stag, PrimaSquadra=:ps, "
                                "SettoreGiovanile=:sg WHERE ID=:cid",
                                {
                                    "t": new_team_id, "s": new_stipendio, "co": new_costo,
                                    "a": new_anni, "stag": new_stagione_firma,
                                    "ps": int(new_prima_squadra), "sg": int(new_settore),
                                    "cid": contratto["contratto_id"],
                                }
                            ))
                    elif not contratto and new_team is not None:
                        new_team_id = teams_map[new_team]
                        ops.append((
                            "INSERT INTO contratti (SquadraID, GiocatoreID, Stipendio, CostoAcquisto, "
                            "AnniDurata, StagioneFirma, PrimaSquadra, SettoreGiovanile) "
                            "VALUES (:t,:p,:s,:co,:a,:stag,:ps,:sg)",
                            {
                                "t": new_team_id, "p": data_p["id"], "s": new_stipendio,
                                "co": new_costo, "a": new_anni, "stag": new_stagione_firma,
                                "ps": int(new_prima_squadra), "sg": int(new_settore),
                            }
                        ))

                    if run_transaction_batch(ops):
                        st.success("✅ Modifiche salvate con successo!")
                        st.rerun()

                if do_del:
                    if contratto:
                        st.error("⛔ Contratto attivo: svincola prima il giocatore (spunta la casella sopra e salva), poi elimina.")

                    else:
                        run_query("DELETE FROM giocatori WHERE ID=:id", {"id": data_p["id"]})
                        st.success(f"🗑️ Eliminato: {sel_p}")
                        st.rerun()

# ==================== TAB 2: ACQUISTO ====================
with t_acq:
    st.subheader("Ingaggio Svincolato")
    free_agents = get_free_agents()
    if not free_agents:
        st.info("Nessun giocatore svincolato nel DB.")
    else:
        with st.form("buy"):
            c1, c2 = st.columns(2)
            pl  = c1.selectbox("Giocatore", list(free_agents.keys()))
            tm  = c1.selectbox("Squadra",   list(teams_map.keys()))
            c1.caption(f"Budget disponibile: **{fmt_money(teams_data[tm]['budget'])}**")
            pid   = free_agents[pl]["id"]
            costo = c2.number_input("Costo Cartellino (FM)", 0.0, step=1.0)
            stip  = c2.number_input("Stipendio Annuo (FM)",  0.0, step=0.5,
                                    value=round(free_agents[pl]["val"] / 10, 1))
            anni  = c2.number_input("Durata contratto (anni)", 1, 5, 3)
            sess  = c2.radio("Sessione", ["Estiva", "Invernale"], horizontal=True, key="s_buy")

            if st.form_submit_button("✅ Acquista", type="primary"):
                tid = teams_map[tm]
                ops = [
                    ("INSERT INTO contratti (SquadraID, GiocatoreID, Stipendio, CostoAcquisto, "
                     "AnniDurata, StagioneFirma, PrimaSquadra) VALUES (:t,:p,:s,:c,:a,:stag,1)",
                     {"t": tid, "p": pid, "s": stip, "c": costo, "a": anni, "stag": current_season}),
                    ("UPDATE fantasquadre SET CreditiResidui=CreditiResidui-:c WHERE ID=:t",
                     {"c": costo, "t": tid}),
                    ("INSERT INTO operazioni_mercato (Stagione, Sessione, SquadraID, GiocatoreID, "
                     "Tipo, Costo, Note) VALUES (:s,:sess,:t,:p,'Acquisto',:c,'Ingaggio Svincolato')",
                     {"s": current_season, "sess": sess, "t": tid, "p": pid, "c": costo}),
                ]
                if run_transaction_batch(ops):
                    st.success(f"✅ {pl} ingaggiato da **{tm}**!")
                    st.rerun()

# ==================== TAB 3: SVINCOLO ====================
with t_cess:
    st.subheader("Svincolo Giocatore")

    c1, c2 = st.columns(2)
    tm_s         = c1.selectbox("Squadra", list(teams_map.keys()), key="tm_cess")
    tid_s        = teams_map[tm_s]
    players_cess = get_team_players(tid_s)

    if not players_cess:
        st.info(f"Nessun giocatore con contratto per **{tm_s}**.")
    else:
        pl_sel = c1.selectbox("Giocatore", list(players_cess.keys()), key="pl_cess")
        d      = players_cess[pl_sel]
        valore = d["valore"]
        anni   = d["anni"]
        stip   = d["stipendio"]

        c2.metric("Valore di mercato",       fmt_money(valore))
        c2.metric("Anni contratto rimasti",  anni)
        c2.metric("Stipendio annuo",         fmt_money(stip))

        st.divider()

        tipo = st.radio(
            "Tipo di svincolo",
            ["Svincolo Ordinario", "Svincolo Straordinario", "Addio Serie A", "Scadenza Contratto"],
            horizontal=True,
            key="tipo_svincolo"
        )

        # ── Calcolo automatico impatto finanziario ──────────────────────
        if tipo == "Svincolo Ordinario":
            delta       = -((valore * 0.5) + (anni * stip))
            formula_str = (f"−(50% × {fmt_money(valore)}) − ({anni} anni × {fmt_money(stip)}) "
                        f"= {delta:+.2f} FM")
            desc        = "La squadra paga la buonuscita: 50% del valore più gli anni residui di stipendio."

        elif tipo == "Svincolo Straordinario":
            delta       = +(valore * 0.5) - (anni * stip)
            formula_str = (f"+50% × {fmt_money(valore)} − ({anni} anni × {fmt_money(stip)}) "
                        f"= {delta:+.2f} FM")
            desc        = "La squadra incassa il 50% del valore ma liquida gli anni residui di stipendio."

        elif tipo == "Addio Serie A":
            delta       = +(valore - stip)
            formula_str = (f"+{fmt_money(valore)} (valore) − {fmt_money(stip)} (1 anno stipendio) "
                        f"= {delta:+.2f} FM")
            desc        = "Il giocatore lascia la Serie A: incasso del valore meno un anno di contratto."

        else:  # Scadenza Contratto
            delta       = 0.0
            formula_str = "Nessun impatto — contratto naturalmente scaduto."
            desc        = "Il contratto è scaduto: nessun credito guadagnato né perso."

        # ── Riepilogo visuale ────────────────────────────────────────────
        fa, fb = st.columns(2)
        fa.info(f"**Formula:** {formula_str}\n\n_{desc}_")

        if delta > 0:
            fb.success(f"🟢 Impatto budget: **{delta:+.2f} FM**")
        elif delta < 0:
            fb.error(f"🔴 Impatto budget: **{delta:+.2f} FM**")
        else:
            fb.info(f"⚪ Impatto budget: **{delta:+.2f} FM**")

        # Permetti override manuale
        delta_finale = st.number_input(
            "Importo finale (FM) — modifica se necessario",
            value=round(delta, 2), step=0.5, key="delta_svincolo",
            help="Pre-calcolato dalla formula. Positivo = guadagno, Negativo = perdita."
        )
        sess_s = st.radio("Sessione di mercato", ["Estiva", "Invernale"],
                          horizontal=True, key="s_rel")
        st.divider()

        if st.button(f"🗑️ Conferma {tipo}", type="primary"):
            pid_s = d["id"]
            ops = [
                ("DELETE FROM contratti WHERE SquadraID=:t AND GiocatoreID=:p",
                 {"t": tid_s, "p": pid_s}),
                ("UPDATE fantasquadre SET CreditiResidui=CreditiResidui+:d WHERE ID=:t",
                 {"d": delta_finale, "t": tid_s}),
                ("INSERT INTO operazioni_mercato (Stagione, Sessione, SquadraID, GiocatoreID, "
                 "Tipo, Costo, Note) VALUES (:s,:sess,:t,:p,:tipo,:c,:note)",
                 {"s": current_season, "sess": sess_s, "t": tid_s, "p": pid_s,
                  "tipo": tipo, "c": delta_finale, "note": formula_str}),
            ]
            if run_transaction_batch(ops):
                st.success(
                    f"✅ **{pl_sel}** svincolato da **{tm_s}** — "
                    f"budget variazione: **{delta_finale:+.2f} FM**"
                )
                st.rerun()

# ==================== TAB 4: SCAMBIO ====================
with t_scambio:
    st.subheader("Trasferimento tra Club")
    c1, c2 = st.columns(2)
    t1 = c1.selectbox("Squadra cedente",    list(teams_map.keys()), key="t1")
    t2 = c2.selectbox("Squadra acquirente", list(teams_map.keys()), key="t2")
    p1 = get_team_players(teams_map[t1])

    if t1 == t2:
        st.warning("Le due squadre devono essere diverse.")
    elif not p1:
        st.info(f"Nessun giocatore con contratto per **{t1}**.")
    else:
        with st.form("swap"):
            pl        = st.selectbox("Giocatore da trasferire", list(p1.keys()))
            costo     = st.number_input("Costo Trasferimento (FM)", 0.0, step=1.0)
            stip_perc = st.slider("% Stipendio a carico acquirente", 0, 100, 100,
                                  help="100% = stipendio invariato; 0% = contratto azzerato")
            sess      = st.radio("Sessione", ["Estiva","Invernale"],
                                 horizontal=True, key="s_swap")
            d_pl = p1[pl]
            st.caption(
                f"Valore: **{fmt_money(d_pl['valore'])}** | "
                f"Stipendio: **{fmt_money(d_pl['stipendio'])}** → "
                f"**{fmt_money(d_pl['stipendio'] * stip_perc / 100)}** dopo trasferimento | "
                f"Anni rimasti: **{d_pl['anni']}** | "
                f"Budget {t2}: **{fmt_money(teams_data[t2]['budget'])}**"
            )

            if st.form_submit_button("🤝 Conferma Trasferimento", type="primary"):
                tid1, tid2 = teams_map[t1], teams_map[t2]
                pid_sw     = d_pl["id"]
                new_stip   = d_pl["stipendio"] * stip_perc / 100
                ops = [
                    ("UPDATE contratti SET SquadraID=:t2, Stipendio=:ns "
                     "WHERE GiocatoreID=:p AND SquadraID=:t1",
                     {"t2": tid2, "ns": new_stip, "p": pid_sw, "t1": tid1}),
                    ("UPDATE fantasquadre SET CreditiResidui=CreditiResidui-:c WHERE ID=:t",
                     {"c": costo, "t": tid2}),
                    ("UPDATE fantasquadre SET CreditiResidui=CreditiResidui+:c WHERE ID=:t",
                     {"c": costo, "t": tid1}),
                    ("INSERT INTO operazioni_mercato (Stagione, Sessione, SquadraID, GiocatoreID, "
                     "Tipo, Costo, Note) VALUES (:s,:sess,:t,:p,'Acquisto',:c,:n)",
                     {"s": current_season, "sess": sess, "t": tid2, "p": pid_sw,
                      "c": costo, "n": f"Da {t1}"}),
                    ("INSERT INTO operazioni_mercato (Stagione, Sessione, SquadraID, GiocatoreID, "
                     "Tipo, Costo, Note) VALUES (:s,:sess,:t,:p,'Cessione',:c,:n)",
                     {"s": current_season, "sess": sess, "t": tid1, "p": pid_sw,
                      "c": -costo, "n": f"A {t2}"}),
                ]
                if run_transaction_batch(ops):
                    st.success(
                        f"✅ **{pl}** trasferito da **{t1}** a **{t2}** "
                        f"per **{fmt_money(costo)}**!"
                    )
                    st.rerun()

# ==================== TAB 5: RINNOVO ====================
with t_rinn:
    st.subheader("Rinnovo Contrattuale")
    tm_r   = st.selectbox("Squadra", list(teams_map.keys()), key="tm_ren")
    pl_ren = get_team_players(teams_map[tm_r])

    if not pl_ren:
        st.info(f"Nessun giocatore con contratto per **{tm_r}**.")
    else:
        pl_r = st.selectbox("Giocatore", list(pl_ren.keys()), key="pl_ren_sel")
        d_r  = pl_ren[pl_r]
        st.caption(
            f"Stipendio attuale: **{fmt_money(d_r['stipendio'])}** | "
            f"Anni rimasti: **{d_r['anni']}** | "
            f"Valore: **{fmt_money(d_r['valore'])}**"
        )

        with st.form("ren"):
            c1, c2 = st.columns(2)
            ns   = c1.number_input("Nuovo Stipendio (FM)", 0.0, step=0.5, value=d_r["stipendio"])
            na   = c2.number_input("Nuovi Anni di Contratto", 1, 5, value=d_r["anni"])
            sess = st.radio("Sessione", ["Estiva","Invernale"],
                            horizontal=True, key="s_ren")

            if st.form_submit_button("✍️ Conferma Rinnovo", type="primary"):
                tid_r, pid_r = teams_map[tm_r], d_r["id"]
                ops = [
                    ("UPDATE contratti SET Stipendio=:s, AnniDurata=:a, StagioneFirma=:stag "
                     "WHERE GiocatoreID=:p AND SquadraID=:t",
                     {"s": ns, "a": na, "stag": current_season, "p": pid_r, "t": tid_r}),
                    ("INSERT INTO operazioni_mercato (Stagione, Sessione, SquadraID, GiocatoreID, "
                     "Tipo, Costo, Note) VALUES (:s,:sess,:t,:p,'Rinnovo',0,:n)",
                     {"s": current_season, "sess": sess, "t": tid_r, "p": pid_r,
                      "n": f"Rinnovo {na} anni a {ns:.2f} FM/anno"}),
                ]
                if run_transaction_batch(ops):
                    st.success(
                        f"✅ Contratto rinnovato: **{pl_r}** — "
                        f"{na} anni a **{fmt_money(ns)}/anno**"
                    )
                    st.rerun()