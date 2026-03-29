import streamlit as st
from main import AgentRouter
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import date
import hashlib

# ─── 1. FIREBASE SETUP ────────────────────────────────────────────────────────
@st.cache_resource
def init_db():
    if not firebase_admin._apps:
        # This tells the app to look in the Cloud Vault first!
        if "firebase" in st.secrets:
            firebase_credentials = dict(st.secrets["firebase"])
            cred = credentials.Certificate(firebase_credentials)
        else:
            # Fallback for your local laptop
            cred = credentials.Certificate("firebase-key.json") 
            
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_db()

st.set_page_config(
    page_title="Fitness AI Agent",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── UTILITY: SECURE PASSWORD HASHING ────────────────────────────────────────
def hash_password(password):
    """Converts a plain-text password into a secure SHA-256 hash"""
    return hashlib.sha256(password.encode()).hexdigest()

# ─── UI STYLING ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .app-title { font-size: 3rem; font-weight: 800; background: linear-gradient(90deg, #16a34a, #0891b2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0rem; line-height: 1.15; }
    .app-subtitle { color: var(--text-color); opacity: 0.6; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .info-card { background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); border-radius: 14px; padding: 16px; margin-bottom: 16px; color: var(--text-color); }
    .metric-card { background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.18); border-radius: 16px; padding: 18px; text-align: center; }
    .metric-title { color: var(--text-color); opacity: 0.55; font-size: 0.9rem; }
    .metric-value { color: var(--text-color); font-size: 1.2rem; font-weight: 700; margin-top: 6px; }
    .welcome-box { background: var(--secondary-background-color); border: 1px solid rgba(22,163,74,0.35); border-left: 4px solid #16a34a; border-radius: 14px; padding: 28px; margin: 18px 0 24px 0; color: var(--text-color); }
    .agent-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; background: rgba(22,163,74,0.15); color: #16a34a; border: 1px solid rgba(22,163,74,0.35); margin-bottom: 8px; }
    div[data-testid="stChatMessage"] { border-radius: 14px; padding: 12px; background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.12); }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) { background: rgba(8,145,178,0.08); border: 1px solid rgba(8,145,178,0.2); }
</style>
""", unsafe_allow_html=True)

# ─── 2. SESSION STATE (The Memory) ───────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()
if "profile" not in st.session_state:
    st.session_state.profile = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "first_msg_sent" not in st.session_state:
    st.session_state.first_msg_sent = False

route_display = {
    "workout":   "💪 Workout Agent",
    "nutrition": "🥗 Nutrition Agent",
    "recovery":  "🛌 Recovery Agent",
    "both":      "⚡ Workout + Nutrition",
    "general":   "🤖 Fitness Assistant",
}

# ─── 3. AUTHENTICATION (Login & Sign Up) ─────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="app-title">Welcome to Fitness AI</div>', unsafe_allow_html=True)
    st.write("Please log in or create an account to continue.")
    
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Sign Up"])
    
    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            if login_user and login_pass:
                user_ref = db.collection("users").document(login_user)
                doc = user_ref.get()
                if doc.exists:
                    if doc.to_dict().get("password") == hash_password(login_pass):
                        st.session_state.username = login_user
                        st.session_state.logged_in = True
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("Username not found. Please sign up.")
            else:
                st.warning("Please fill in both fields.")

    with tab2:
        signup_user = st.text_input("Choose a Username", key="signup_user")
        signup_pass = st.text_input("Choose a Password", type="password", key="signup_pass")
        if st.button("Create Account"):
            if signup_user and signup_pass:
                user_ref = db.collection("users").document(signup_user)
                if user_ref.get().exists:
                    st.error("Username already exists! Please choose another one.")
                else:
                    user_ref.set({"password": hash_password(signup_pass), "created_at": str(date.today())})
                    st.success("Account created successfully! You can now log in.")
            else:
                st.warning("Please fill in both fields.")

# ─── 4. THE MAIN APP (Only visible if logged in) ─────────────────────────────
else:
    with st.sidebar:
        st.success(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = [] 
            st.rerun()
            
        st.divider()
        st.markdown("""<div class="info-card"><h2 style="margin-top:0;">🏋️ Fitness AI Agent</h2><p style="margin-bottom:0; opacity:0.8;">Multi-agent fitness assistant.</p></div>""", unsafe_allow_html=True)

        # --- LOG SECTION ---
        st.subheader("📋 Log Today")
        log_tab = st.selectbox("Log type", ["Workout", "Nutrition"])

        if log_tab == "Workout":
            w_type = st.text_input("Workout type (e.g. Chest, Legs)")
            w_dur = st.number_input("Duration (mins)", min_value=1, max_value=300, value=45)
            if st.button("💾 Save Workout Log", use_container_width=True):
                log_data = {"date": str(date.today()), "category": "workout", "workout_type": w_type, "duration_minutes": w_dur}
                db.collection("users").document(st.session_state.username).collection("daily_logs").add(log_data)
                st.success("✅ Workout saved to Cloud!")

        elif log_tab == "Nutrition":
            n_cal = st.number_input("Calories", min_value=0, max_value=10000, value=2000)
            n_pro = st.number_input("Protein (g)", min_value=0, max_value=500, value=100)
            if st.button("💾 Save Nutrition Log", use_container_width=True):
                log_data = {"date": str(date.today()), "category": "nutrition", "calories": n_cal, "protein_g": n_pro}
                db.collection("users").document(st.session_state.username).collection("daily_logs").add(log_data)
                st.success("✅ Nutrition saved to Cloud!")

        st.divider()
        
        # --- PROGRESS AGENT TRIGGER ---
        st.subheader("📈 Weekly Review")
        if st.button("Generate Progress Report", type="primary", use_container_width=True):
            with st.spinner("Analyzing your cloud data..."):
                try:
                    from agent.progress import ProgressAgent
                    progress_agent = ProgressAgent(db) 
                    report = progress_agent.run_analysis(st.session_state.username)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": report,
                        "agent_route": "general" 
                    })
                except ImportError:
                    st.error("Could not find agent/progress.py file! Make sure you created it.")
            st.rerun()

        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent = AgentRouter()
            st.rerun()

    # --- MAIN CHAT AREA ---
    st.markdown('<div class="app-title">Fitness AI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Your personalized multi-agent assistant.</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-box">
            <h2 style="margin-top:0;">Welcome back, 🚀</h2>
            <p style="font-size:1.05rem; margin-bottom:0;">
                Ask anything related to training, food, recovery, or fitness planning. 
                Don't forget to use the sidebar to log your daily stats and generate your weekly review!
            </p>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "agent_route" in message:
                st.markdown(f'<div class="agent-badge">{route_display.get(message["agent_route"], "🤖 General")}</div>', unsafe_allow_html=True)
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about fitness..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.first_msg_sent = True

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting the agents..."):
                try:
                    reply, route = st.session_state.agent.run(prompt)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": reply,
                        "agent_route": route
                    })
                    st.markdown(f'<div class="agent-badge">{route_display.get(route, "🤖 General")}</div>', unsafe_allow_html=True)
                    st.markdown(reply)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "exhausted" in error_msg or "quota" in error_msg:
                        st.warning("⏳ API speed limit reached. Please wait 60 seconds and try again.")
                    else:
                        st.error(f"API Error: {e}")
        st.rerun()