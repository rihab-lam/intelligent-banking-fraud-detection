import streamlit as st
import plotly.graph_objects as go
import requests
import numpy as np
from datetime import datetime

# --- CONFIGURATION DES URLS BACKEND ---
URL_AUTH = "http://127.0.0.1:8081"
URL_ML = "http://127.0.0.1:8002"
URL_TRANSACTION = "http://127.0.0.1:8000"

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="FraudGuard - Détection Bancaire",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALISATION DES ÉTATS DE SESSION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "user_token" not in st.session_state:
    st.session_state.user_token = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = "Analyste Senior"
if "page" not in st.session_state:
    st.session_state.page = "vue_ensemble"
if "simulation_result" not in st.session_state:
    st.session_state.simulation_result = None

# --- DESIGN GRAPHIQUE CONFIGURÉ (BLEU NUIT & GLOW) ---
st.markdown("""
    <style>
    /* Fond global et sidebar */
    .stApp { background-color: #0b132b; color: #f0f6fc; }
    [data-testid="stSidebar"] { background-color: #1c2541; border-right: 1px solid #2a3457; }
    
    /* Boutons de la Sidebar */
    .stSidebar div div button {
        background-color: transparent !important;
        color: #afb9d0 !important;
        border: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
    }
    .stSidebar div div button:hover {
        background-color: rgba(56, 139, 253, 0.1) !important;
        color: #ffffff !important;
    }
    
    /* Cartes KPI */
    .kpi-card {
        background-color: #1c2541;
        border: 1px solid #2a3457;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .kpi-title { color: #8b949e; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { color: #ffffff; font-size: 32px; font-weight: 700; margin: 8px 0 4px 0; }
    
    /* Tendances et Badges */
    .sub-green { color: #3fb950; font-size: 12px; font-weight: 500; display: flex; align-items: center; gap: 4px; }
    .sub-red { color: #f85149; font-size: 12px; font-weight: 500; display: flex; align-items: center; gap: 4px; }
    .sub-purple { color: #bc8cff; font-size: 12px; font-weight: 500; display: flex; align-items: center; gap: 4px; }
    
    .progress-bar-container { background-color: #0b132b; border-radius: 4px; height: 4px; width: 100%; margin-top: 8px; }
    .progress-blue { background-color: #388bfd; height: 100%; border-radius: 4px; }
    .progress-red { background-color: #f85149; height: 100%; border-radius: 4px; }
    .progress-green { background-color: #3fb950; height: 100%; border-radius: 4px; }
    .progress-purple { background-color: #bc8cff; height: 100%; border-radius: 4px; }

    /* Alertes et Liste */
    .alert-box { background-color: #1c2541; border: 1px solid #2a3457; border-radius: 12px; padding: 20px; }
    .alert-item {
        background-color: #0b132b;
        border: 1px solid #2a3457;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .score-badge {
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .score-high { background-color: rgba(248, 81, 73, 0.15); color: #f85149; border: 1px solid #f85149; }
    .score-medium { background-color: rgba(210, 153, 34, 0.15); color: #d29922; border: 1px solid #d29922; }
    .score-low { background-color: rgba(63, 185, 80, 0.15); color: #3fb950; border: 1px solid #3fb950; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# GESTION DES ÉCRANS DE BIENVENUE (LOGIN / REGISTER)
# ==============================================================================
if not st.session_state.authenticated:
    st.markdown("<div style='max-width: 450px; margin: 60px auto 20px auto; padding: 40px; background-color: #1c2541; border-radius: 16px; border: 1px solid #2a3457; box-shadow: 0 10px 30px rgba(0,0,0,0.3);'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🛡️ FraudGuard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e; font-size: 14px; margin-top: 5px;'>Analyse des risques & Détection Random Forest</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- MODE 1 : CONNEXION ---
    if st.session_state.auth_mode == "login":
        st.markdown("<h4 style='margin-top:0;'>Connexion</h4>", unsafe_allow_html=True)
        username_input = st.text_input("Identifiant", placeholder="ex: yahya_dev", key="login_user")
        password_input = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Se connecter au terminal", use_container_width=True):
            if username_input and password_input:
                try:
                    payload = {"identifiant": username_input, "mot_de_passe": password_input}
                    response = requests.post(f"{URL_AUTH}/auth/login", json=payload, timeout=2.5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.user_token = data.get("access_token")
                        st.session_state.username = username_input
                        st.session_state.user_role = data.get("role", "analyste_senior")
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects ou refusés par le serveur.")
                except requests.exceptions.RequestException:
                    st.warning("⚠️ Service d'authentification hors-ligne. Passage en mode Démo.")
                    st.session_state.username = username_input
                    st.session_state.user_role = "analyste_senior"
                    st.session_state.authenticated = True
                    st.rerun()
            else:
                st.error("Veuillez remplir tous les champs.")
                
        st.markdown("<p style='text-align: center; margin-top: 20px; font-size: 13px; color: #8b949e;'>Nouveau sur la plateforme ?</p>", unsafe_allow_html=True)
        if st.button("Créer un compte analyste", use_container_width=True):
            st.session_state.auth_mode = "register"
            st.rerun()

    # --- MODE 2 : INSCRIPTION ---
    elif st.session_state.auth_mode == "register":
        st.markdown("<h4 style='margin-top:0; color: #388bfd;'>Créer un compte</h4>", unsafe_allow_html=True)
        
        reg_user = st.text_input("Choisir un identifiant", placeholder="ex: yahya_dev", key="reg_user")
        reg_email = st.text_input("Adresse Email", placeholder="analyste@banque.com", key="reg_email")
        reg_pass = st.text_input("Mot de passe sécurisé", type="password", placeholder="••••••••", key="reg_pass")
        reg_role = st.selectbox("Rôle attribué", ["Analyste Senior", "Analyste Junior", "Administrateur Système"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Valider l'inscription", use_container_width=True):
            if reg_user and reg_email and reg_pass:
                try:
                    payload_register = {
                        "identifiant": reg_user,
                        "email": reg_email,
                        "mot_de_passe": reg_pass,
                        "role": reg_role.lower().replace(" ", "_")
                    }
                    response = requests.post(f"{URL_AUTH}/auth/register", json=payload_register, timeout=2.5)
                    
                    if response.status_code in [200, 201]:
                        st.success("🎉 Compte créé avec succès ! Connectez-vous.")
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(f"❌ Erreur lors de la création : {response.text}")
                except requests.exceptions.RequestException:
                    st.warning("⚠️ Service Auth hors-ligne. Inscription simulée localement !")
                    st.session_state.username = reg_user
                    st.session_state.user_role = reg_role.lower().replace(" ", "_")
                    st.session_state.auth_mode = "login"
                    st.rerun()
            else:
                st.error("Veuillez remplir l'ensemble du formulaire d'inscription.")
                
        if st.button("Retourner à l'écran de connexion", use_container_width=True):
            st.session_state.auth_mode = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# INTERFACE DU TABLEAU DE BORD PRINCIPAL (ACCÈS AUTORISÉ)
# ==============================================================================
else:
    # --- BARRE LATÉRALE DE NAVIGATION ---
    with st.sidebar:
        st.markdown("<h2 style='color: #ffffff; margin-bottom: 0;'>🛡️ FraudGuard</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8b949e; font-size: 12px; margin-top: 0;'>Détection bancaire</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<p style='color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase;'>Tableau de bord</p>", unsafe_allow_html=True)
        if st.button("📊 Vue d'ensemble", use_container_width=True):
            st.session_state.page = "vue_ensemble"
        if st.button("📈 Transactions", use_container_width=True):
            st.session_state.page = "transactions"
        if st.button("⚠️ Alertes", use_container_width=True):
            st.session_state.page = "alertes"
        
        st.markdown("<p style='color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-top: 20px;'>Analyse</p>", unsafe_allow_html=True)
        if st.button("📉 Statistiques", use_container_width=True):
            st.session_state.page = "statistiques"
        if st.button("👥 Comptes", use_container_width=True):
            st.session_state.page = "comptes"
        if st.button("🤖 Modèle IA", use_container_width=True):
            st.session_state.page = "modele_ia"

        st.markdown("<p style='color: #8b949e; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-top: 20px;'>Système</p>", unsafe_allow_html=True)
        if st.button("⚙️ Paramètres", use_container_width=True):
            st.session_state.page = "parametres"
        if st.button("📁 Rapports", use_container_width=True):
            st.session_state.page = "rapports"
        
        # --- BLOC DE PROFIL UTILISATEUR DYNAMIQUE ---
        current_user = st.session_state.get("username", "Analyste").strip()
        
        # Logique d'initiales automatiques
        if " " in current_user:
            initials = "".join([part[0].upper() for part in current_user.split()[:2]])
        elif len(current_user) >= 2:
            initials = current_user[:2].upper()
        else:
            initials = current_user.upper() if current_user else "FG"

        user_role = st.session_state.get("user_role", "analyste_senior").replace("_", " ").title()

        st.markdown("---")
        st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 15px;'>
                <div style='background-color: #388bfd; border-radius: 50%; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; min-width: 38px;'>
                    {initials}
                </div>
                <div style='overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>
                    <p style='margin: 0; font-size: 14px; font-weight: bold; color: #ffffff;'>{current_user}</p>
                    <p style='margin: 0; font-size: 11px; color: #8b949e;'>{user_role}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_token = None
            st.session_state.auth_mode = "login"
            st.rerun()

    # ==========================================================================
    # PAGE : VUE D'ENSEMBLE
    # ==========================================================================
    if st.session_state.page == "vue_ensemble":
        col_title, col_status = st.columns([4, 1])
        with col_title:
            st.markdown("<h1>Vue d'ensemble — Mai 2026</h1>", unsafe_allow_html=True)
        with col_status:
            st.markdown("<div style='text-align: right; margin-top: 15px;'><span style='background-color: rgba(63, 185, 80, 0.15); color: #3fb950; padding: 6px 14px; border-radius: 20px; font-size: 12px; font-weight: bold; border: 1px solid #3fb950;'>● Système actif</span></div>", unsafe_allow_html=True)

        # Ligne des 4 Cartes KPI
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown('<div class="kpi-card"><div class="kpi-title">💳 Transactions</div><div class="kpi-value">24 817</div><div class="sub-green">▲ +8.2% ce mois</div><div class="progress-bar-container"><div class="progress-blue" style="width: 65%;"></div></div></div>', unsafe_allow_html=True)
        with kpi2:
            st.markdown('<div class="kpi-card"><div class="kpi-title">🛑 Fraudes Détectées</div><div class="kpi-value" style="color: #f85149;">143</div><div class="sub-red">▲ +3 aujourd\'hui</div><div class="progress-bar-container"><div class="progress-red" style="width: 40%;"></div></div></div>', unsafe_allow_html=True)
        with kpi3:
            st.markdown('<div class="kpi-card"><div class="kpi-title">🎯 Taux Détection</div><div class="kpi-value" style="color: #3fb950;">97.4%</div><div class="sub-green">▲ +0.3% vs mois dernier</div><div class="progress-bar-container"><div class="progress-green" style="width: 97%;"></div></div></div>', unsafe_allow_html=True)
        with kpi4:
            st.markdown('<div class="kpi-card"><div class="kpi-title">⚡ Temps Réponse</div><div class="kpi-value" style="color: #388bfd;">1.2ms</div><div class="sub-purple">▼ -0.4ms optimisé</div><div class="progress-bar-container"><div class="progress-purple" style="width: 85%;"></div></div></div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([1.5, 1])
        
        with col_left:
            # INTERACTION AVEC LE MOTEUR DE SCORING INTERNE
            st.markdown("<div class='alert-box' style='margin-bottom: 20px;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0;'>⚡ Évaluation en temps réel (Moteur de règles)</h3>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                amount = st.number_input("Montant de la transaction (DH)", min_value=1.0, value=4500.0)
            with c2:
                country_code = st.selectbox("Code Pays de l'opération", ["MA", "FR", "US", "IR", "KP"])
            with c3:
                nb_tx = st.slider("Transactions cette heure", 1, 15, 2)
                
            new_beneficiary = st.checkbox("Nouveau bénéficiaire ?")
                
            if st.button("Calculer le score de risque", use_container_width=True):
                score_total = 0
                regles = []
                if amount > 20000: score_total += 100; regles.append("montant_tres_eleve")
                elif amount >= 10000: score_total += 75; regles.append("montant_eleve")
                elif amount > 3000: score_total += 50; regles.append("montant_a_surveiller")
                
                if country_code in ["KP", "IR"]: score_total += 80; regles.append("pays_risque_eleve")
                if nb_tx > 7: score_total += 80; regles.append("transactions_anormales")
                elif 4 <= nb_tx <= 7: score_total += 40; regles.append("transactions_suspectes")
                
                if new_beneficiary:
                    if amount > 20000: score_total += 100; regles.append("nouveau_benef_montant_critique")
                    elif amount > 3000: score_total += 75; regles.append("nouveau_benef_montant_eleve")
                    else: score_total += 25; regles.append("nouveau_benef_leger_risque")
                
                score_final = min(score_total, 100)
                decision, risque, color = ("FRAUDE", "élevé", "red") if score_final > 70 else (("SUSPECTE", "moyen", "orange") if score_final >= 50 else ("NORMALE", "faible", "green"))
                    
                st.session_state.simulation_result = {
                    "score": score_final, "decision": decision, "risque": risque, "color": color, "regles": regles
                }
            
            if st.session_state.simulation_result:
                res = st.session_state.simulation_result
                if res["color"] == "red": st.error(f"🚨 ALERT : {res['decision']} (Score: {res['score']}/100)")
                elif res["color"] == "orange": st.warning(f"⚠️ ATTENTION : {res['decision']} (Score: {res['score']}/100)")
                else: st.success(f"✅ VALIDÉE : {res['decision']} (Score: {res['score']}/100)")
            st.markdown("</div>", unsafe_allow_html=True)

            # Graphe d'activité sur 7j
            st.markdown("<div class='alert-box'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0;'>📊 Activité — 7 derniers jours</h3>", unsafe_allow_html=True)
            jours = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=jours, y=[320, 600, 340, 300, 480, 180, 160], name='Normal', marker_color='#388bfd'))
            fig_bar.add_trace(go.Bar(x=jours, y=[20, 45, 25, 35, 50, 15, 12], name='Suspect', marker_color='#e29578'))
            fig_bar.add_trace(go.Bar(x=jours, y=[5, 12, 8, 5, 14, 5, 3], name='Fraude', marker_color='#f85149'))
            fig_bar.update_layout(
                barmode='stack', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=10, b=10), height=220, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
                font=dict(color="#8b949e"), yaxis=dict(gridcolor="#2a3457"), xaxis=dict(gridcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("<div class='alert-box' style='height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-top: 0;'>🛡️ Score de risque global</h3>", unsafe_allow_html=True)
            
            # --- CORRECTION PLOTLY APPORTÉE ICI ---
            fig_gauge = go.Figure(go.Pie(
                values=[75, 25], hole=0.78, direction="clockwise", sort=False,
                marker=dict(colors=['#3fb950', '#0b132b']), textinfo='none', hoverinfo='none'
            ))
            fig_gauge.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=20, r=20, t=10, b=10), height=180, showlegend=False,
                annotations=[
                    dict(text='75%', x=0.5, y=0.55, font_size=34, font_weight='bold', showarrow=False, font_color='#ffffff'),
                    dict(text='sécurisé', x=0.5, y=0.35, font_size=12, showarrow=False, font_color='#8b949e')
                ]
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
            st.markdown("<p style='text-align:center; font-size:12px; color:#8b949e; margin-top:-10px;'>Indice de sécurité du système</p>", unsafe_allow_html=True)

            # Indicateurs horizontaux complémentaires
            st.markdown("""
                <div style='margin-top:20px; font-size:13px;'>
                    <div style='display:flex; justify-content:between; margin-between:4px;'><span>Précision modèle</span><strong style='color:#3fb950;'>97%</strong></div>
                    <div style='display:flex; justify-content:between; margin-between:4px;'><span>Faux positifs</span><strong style='color:#8b949e;'>0.8%</strong></div>
                    <div style='display:flex; justify-content:between; margin-between:4px;'><span>Charge système</span><strong style='color:#388bfd;'>43%</strong></div>
                    <div style='display:flex; justify-content:between;'><span>Alertes actives</span><strong style='color:#f85149;'>3/10</strong></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h4 style='font-size:14px; color:#ffffff; margin-top:25px;'>📋 Dernières alertes</h4>", unsafe_allow_html=True)
            st.markdown("""
                <div class="alert-item">
                    <div><span style="color: #f85149; margin-right:8px;">●</span><strong>TXN-88421</strong> · 15 200 DH<br><small style='color:#8b949e;'>Virement · Maroc ➔ Espagne</small></div>
                    <div class="score-badge score-high">Score 94</div>
                </div>
                <div class="alert-item">
                    <div><span style="color: #d29922; margin-right:8px;">●</span><strong>TXN-88398</strong> · 3 450 DH<br><small style='color:#8b949e;'>En ligne · IP Inhabituelle</small></div>
                    <div class="score-badge score-medium">Score 71</div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ==============================================================================
    # PAGE : TRANSACTIONS
    # ==============================================================================
    elif st.session_state.page == "transactions":
        st.markdown("<h1>📈 Transactions</h1>", unsafe_allow_html=True)
        st.markdown("Liste des transactions analysées par le moteur de détection.")

        try:
            response = requests.get(f"{URL_TRANSACTION}/transactions/", timeout=3)

            if response.status_code == 200:
                transactions = response.json()

                if transactions:
                    st.dataframe(transactions, use_container_width=True)

                    fraudes = [
                        tx for tx in transactions
                        if tx.get("decision") == "fraude"
                    ]

                    col1, col2 = st.columns(2)
                    col1.metric("Total transactions", len(transactions))
                    col2.metric("Fraudes détectées", len(fraudes))
                else:
                    st.warning("Aucune transaction trouvée pour le moment.")
            else:
                st.error("Erreur lors de la récupération des transactions.")

        except requests.exceptions.RequestException:
            st.error("Impossible de se connecter au backend transactionnel.")

    # ==============================================================================
    # PAGES SATELLITES
    # ==============================================================================
    elif st.session_state.page in ["alertes", "statistiques", "comptes", "parametres", "rapports"]:
        st.markdown(f"<h1>📂 Section {st.session_state.page.replace('_', ' ').capitalize()}</h1>", unsafe_allow_html=True)
        st.info("Interface connectée à la base de données PostgreSQL centrale.")

    # ==============================================================================
    # PAGE : MODÈLE IA (RANDOM FOREST METRICS)
    # ==============================================================================
    elif st.session_state.page == "modele_ia":
        st.markdown("<h1>🤖 Métriques Algorithmiques (Random Forest)</h1>", unsafe_allow_html=True)
        st.markdown("---")

        try:
            res_roc = requests.get(f"{URL_ML}/ml/roc-curve", timeout=2)
            if res_roc.status_code == 200:
                data_roc = res_roc.json()
                fpr, tpr = data_roc.get("fpr", []), data_roc.get("tpr", [])
                auc_val = data_roc.get("auc", 0.974)
                connection_ml = "online"
            else: raise ValueError
        except: connection_ml = "offline"

        if connection_ml == "offline":
            fpr = np.linspace(0, 1, 100)
            tpr = 1 - np.exp(-6 * fpr)
            auc_val = 0.974
            recall = np.linspace(0, 1, 100)
            precision = 1 - (recall ** 4) * 0.25
        
        col_roc, col_pr = st.columns(2)
        with col_roc:
            st.markdown("<div class='alert-box'>", unsafe_allow_html=True)
            st.markdown(f"<h3>📈 Courbe ROC (AUC = {auc_val:.3f})</h3>", unsafe_allow_html=True)
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name='Random Forest', line=dict(color='#388bfd', width=3)))
            fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', name='Chance', line=dict(color='#8b949e', dash='dash')))
            fig_roc.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=20, t=20, b=40), height=320, font=dict(color="#8b949e"),
                xaxis=dict(title="FPR", gridcolor="#2a3457"), yaxis=dict(title="TPR", gridcolor="#2a3457")
            )
            st.plotly_chart(fig_roc, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_pr:
            st.markdown("<div class='alert-box'>", unsafe_allow_html=True)
            st.markdown("<h3>🎯 Courbe Précision-Rappel</h3>", unsafe_allow_html=True)
            fig_pr = go.Figure()
            fig_pr.add_trace(go.Scatter(x=recall, y=precision, mode='lines', name='Random Forest', line=dict(color='#3fb950', width=3)))
            fig_pr.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=20, t=20, b=40), height=320, font=dict(color="#8b949e"),
                xaxis=dict(title="Recall", gridcolor="#2a3457"), yaxis=dict(title="Precision", gridcolor="#2a3457")
            )
            st.plotly_chart(fig_pr, use_container_width=True, config={'displayModeBar': False})
            st.markdown("</div>", unsafe_allow_html=True)
