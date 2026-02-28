import streamlit as st
import os
import logging
import hashlib
import pandas as pd
from urllib.parse import quote_plus
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

# Configurazione Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==== 1. GESTIONE UTENTI (su MySQL/TiDB) =====================================

def authenticate(username, password):
    """Verifica credenziali contro la tabella users su MySQL/TiDB."""
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    result = run_query(
        "SELECT role FROM users WHERE username = :user AND password_hash = :pwd",
        {"user": username, "pwd": pwd_hash}
    )
    if result:
        run_query(
            "UPDATE users SET last_login = :now WHERE username = :user",
            {"now": datetime.now(), "user": username}
        )
        return result[0][0]
    return None

# ==== 2. GESTIONE SESSIONE STREAMLIT ==========================================

def login_widget():
    """Widget grafico per il login."""
    if st.session_state.get("logged_in"):
        return
        
    with st.form("login_form"):
        st.subheader("🔐 Accesso FantaManager")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Entra")
        
        if submit:
            role = authenticate(username, password)
            if role:
                st.session_state["logged_in"] = True
                st.session_state["role"] = role
                st.session_state["user"] = username
                st.session_state["login_time"] = datetime.now()
                st.success("Accesso effettuato!")
                st.rerun()
            else:
                st.error("Credenziali non valide")

def require_login():
    """Blocca l'esecuzione se l'utente non è loggato."""
    if not st.session_state.get("logged_in"):
        login_widget()
        st.stop() # Interrompe lo script qui se non loggato
    
    # Logout automatico dopo 30 minuti di inattività (opzionale)
    if datetime.now() - st.session_state.get("login_time", datetime.now()) > timedelta(minutes=30):
        st.session_state.clear()
        st.warning("Sessione scaduta. Rieffettua il login.")
        st.stop()

def is_admin():
    """Controlla se l'utente è admin."""
    return st.session_state.get("role") == "admin"

# ==== 3. DATABASE MYSQL (CORE) ================================================

@st.cache_resource
def get_db_engine():
    """
    Crea il pool di connessione a MySQL/TiDB.
    Legge le credenziali da st.secrets (Streamlit Cloud)
    con fallback a os.getenv (sviluppo locale con Docker).
    """
    try:
        db_conf = st.secrets["database"]
        user = db_conf["user"]
        password = db_conf["password"]
        host = db_conf["host"]
        port = db_conf.get("port", 4000)
        db_name = db_conf["name"]
        ssl_mode = db_conf.get("ssl", True)
        logger.info(f"Connessione via Streamlit Secrets a {host}:{port}")
    except (KeyError, FileNotFoundError) as e:
        logger.warning(f"Secrets non trovati ({e}), uso variabili d'ambiente")
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "root")
        host = os.getenv("DB_HOST", "db")
        port = int(os.getenv("DB_PORT", "3306"))
        db_name = os.getenv("DB_NAME", "fantamanagerxix")
        ssl_mode = False

    url = f"mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/{db_name}"

    connect_args = {}
    if ssl_mode:
        import ssl as ssl_module
        ssl_ctx = ssl_module.create_default_context()
        connect_args["ssl"] = ssl_ctx

    return create_engine(
        url,
        poolclass=QueuePool,
        pool_size=2,
        max_overflow=3,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args
    )

def run_query(query_str, params=None):
    """
    Esegue una singola query SQL.
    
    Args:
        query_str (str): La query SQL.
        params (dict/list): Parametri per la query (sicurezza contro injection).
        
    Returns:
        list: Risultati della SELECT (lista di tuple)
        int: Numero di righe modificate (per INSERT/UPDATE/DELETE)
    """
    engine = get_db_engine()
    try:
        with engine.connect() as conn:
            # Converte la stringa in oggetto Text di SQLAlchemy
            stmt = text(query_str)
            
            result = conn.execute(stmt, params if params else {})
            
            # Se la query ritorna righe (è una SELECT)
            if query_str.strip().upper().startswith("SELECT") or query_str.strip().upper().startswith("WITH"):
                return result.fetchall()
            
            # Se è una modifica, committa e ritorna il count
            conn.commit()
            return result.rowcount
            
    except SQLAlchemyError as e:
        logger.error(f"Errore SQL: {e}")
        st.error(f"Errore Database: {e}")
        return None

def run_transaction_batch(operations):
    """
    Esegue una serie di query in un'unica transazione atomica.
    
    Args:
        operations (list): Lista di tuple (query_str, params).
                           Es: [("INSERT INTO...", {...}), ("UPDATE...", {...})]
    
    Returns:
        bool: True se tutto ok, False se rollback.
    """
    engine = get_db_engine()
    try:
        with engine.begin() as conn: # .begin() gestisce start/commit/rollback automatico
            for query_str, params in operations:
                conn.execute(text(query_str), params if params else {})
        return True
    except SQLAlchemyError as e:
        logger.error(f"Errore Transazione: {e}")
        st.error(f"Errore durante il salvataggio dati: {e}")
        return False
    
def check_connection():
    """
    Verifica che il database risponda e mostra un pallino verde nella sidebar.
    Utile per capire subito se ci sono problemi di rete.
    """
    try:
        # Tenta una query leggerissima
        run_query("SELECT 1")
        # Se passa, mette l'icona verde nella sidebar
        st.sidebar.success("✅ DB Connesso")
        return True
    except Exception as e:
        # Se fallisce, mette l'icona rossa
        st.sidebar.error("❌ DB Offline")
        return False


# ==== 4. HELPERS DI UTILITÀ (NUOVI PER IL DB A ID) ============================

def get_team_id(team_name):
    """Recupera l'ID di una squadra dal nome."""
    res = run_query("SELECT ID FROM fantasquadre WHERE Nome = :name", {"name": team_name})
    return res[0][0] if res else None

def get_team_name(team_id):
    """Recupera il nome di una squadra dall'ID."""
    res = run_query("SELECT Nome FROM fantasquadre WHERE ID = :id", {"id": team_id})
    return res[0][0] if res else None

def get_current_season_from_db():
    """Legge la stagione attuale dal database."""
    try:
        res = run_query("SELECT Valore FROM configurazione WHERE Chiave = 'stagione_corrente'")
        if res:
            return res[0][0]
    except Exception:
        pass
    return "2025/2026"

def update_season_in_db(new_season):
    """Aggiorna la stagione nel database (usato a fine anno)."""
    run_query("UPDATE configurazione SET Valore = :s WHERE Chiave = 'stagione_corrente'", {"s": new_season})