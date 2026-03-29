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
        try:
            firebase_credentials = dict(st.secrets["firebase"])
            cred = credentials.Certificate(firebase_credentials)
        except Exception:
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

# ─── UTILITY: PASSWORD HASHING ───────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── UTILITY: GRAB LATEST MESSAGE FROM EACH AGENT ────────────────────────────
def get_latest_agent_messages():
    found = {}
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and "agent_route" in msg:
            route = msg["agent_route"]
            if route not in found:
                found[route] = msg["content"]
    return found

# ─── UTILITY: BUILD EMAIL BODY ────────────────────────────────────────────────
def build_email_body(messages, username):
    parts = []
    label_map = {
        "workout":   "💪 WORKOUT",
        "nutrition": "🥗 NUTRITION",
        "recovery":  "🛌 RECOVERY",
        "both":      "⚡ WORKOUT + NUTRITION",
        "plan":      "📅 FULL FITNESS PLAN",
        "general":   "🤖 GENERAL ADVICE",
    }
    for route, content in messages.items():
        label = label_map.get(route, route.upper())
        parts.append(f"{label}\n{content}")

    body  = f"Hi {username}!\n\nHere's your fitness update:\n\n"
    body += "\n\n---\n\n".join(parts)
    body += "\n\n---\nYours truly,\nFitness App 💪"
    return body

# ─── UI STYLING ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .app-title { font-size: 3rem; font-weight: 800; background: linear-gradient(90deg, #16a34a, #0891b2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0rem; line-height: 1.15; }
    .app-subtitle { color: var(--text-color); opacity: 0.6; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .info-card { background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); border-radius: 14px; padding: 16px; margin-bottom: 16px; color: var(--text-color); }
    .welcome-box { background: var(--secondary-background-color); border: 1px solid rgba(22,163,74,0.35); border-left: 4px solid #16a34a; border-radius: 14px; padding: 28px; margin: 18px 0 24px 0; color: var(--text-color); }
    .agent-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; background: rgba(22,163,74,0.15); color: #16a34a; border: 1px solid rgba(22,163,74,0.35); margin-bottom: 8px; }
    .plan-badge { background: rgba(139,92,246,0.15); color: #7c3aed; border: 1px solid rgba(139,92,246,0.35); }
    div[data-testid="stChatMessage"] { border-radius: 14px; padding: 12px; background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.12); }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) { background: rgba(8,145,178,0.08); border: 1px solid rgba(8,145,178,0.2); }
</style>
""", unsafe_allow_html=True)

# ─── 2. SESSION STATE ─────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_email_input" not in st.session_state:
    st.session_state.show_email_input = False

route_display = {
    "workout":   "💪 Workout Agent",
    "nutrition": "🥗 Nutrition Agent",
    "recovery":  "🛌 Recovery Agent",
    "both":      "⚡ Workout + Nutrition",
    "general":   "🤖 Fitness Assistant",
    "plan":      "🧠 Full Plan — All Agents",
}

# ─── 3. AUTHENTICATION ────────────────────────────────────────────────────────
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
        signup_email = st.text_input("Your Email (for future notifications)", key="signup_email")
        if st.button("Create Account"):
            if signup_user and signup_pass:
                user_ref = db.collection("users").document(signup_user)
                if user_ref.get().exists:
                    st.error("Username already exists! Please choose another one.")
                else:
                    user_ref.set({
                        "password": hash_password(signup_pass),
                        "email": signup_email,
                        "created_at": str(date.today())
                    })
                    st.success("Account created! You can now log in.")
            else:
                st.warning("Please fill in username and password.")

# ─── 4. MAIN APP ──────────────────────────────────────────────────────────────
else:
    with st.sidebar:                                          # ← sidebar opens here
        st.success(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.messages = []
            st.session_state.show_email_input = False
            st.rerun()

        st.divider()
        st.markdown("""<div class="info-card"><h2 style="margin-top:0;">🏋️ Fitness AI Agent</h2><p style="margin-bottom:0; opacity:0.8;">Your personal multi-agent fitness assistant. Ask anything about workouts, nutrition, or recovery.</p></div>""", unsafe_allow_html=True)

        st.divider()

        # ─── EMAIL YOURSELF SECTION ───────────────────────────────────────────
        st.subheader("📧 Email Yourself")                    # ← indented inside sidebar

        if not st.session_state.show_email_input:
            if st.button("📧 Email Yourself", use_container_width=True):
                st.session_state.show_email_input = True
                st.rerun()
        else:
            latest = get_latest_agent_messages()

            if not latest:
                st.info("💡 Chat first — ask about workouts, nutrition, or request a **full fitness package**!")

            email_input = st.text_input("Enter your email", key="email_input")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📨 Send", use_container_width=True, type="primary"):
                    if not email_input:
                        st.warning("Enter an email first.")
                    elif not latest:
                        st.warning("Have a conversation first!")
                    else:
                        body = build_email_body(latest, st.session_state.username)
                        # ✅ calls email_agent.send() from EmailAgent class
                        ok, msg = st.session_state.agent.email_agent.send(
                            email_input,
                            "Fitness Update 🏋️",
                            body
                        )
                        if ok:
                            st.success("🎉 Sent! Check your inbox.")
                            st.session_state.show_email_input = False
                            st.rerun()
                        else:
                            st.error(f"Failed: {msg}")
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_email_input = False
                    st.rerun()

        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent = AgentRouter()
            st.rerun()
                                                              # ← sidebar closes here
    # ─── MAIN CHAT AREA ───────────────────────────────────────────────────────
    st.markdown('<div class="app-title">Fitness AI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Your personalized multi-agent assistant.</div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-box">
            <h2 style="margin-top:0;">Welcome back, {st.session_state.username} 🚀</h2>
            <p style="font-size:1.05rem; margin-bottom:0;">
                Ask me anything about training, food, or recovery.
                Want everything at once? Ask for a <strong>full fitness package</strong> and all agents will collaborate on your plan!
            </p>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "agent_route" in message:
                route = message["agent_route"]
                extra = "plan-badge" if route == "plan" else ""
                st.markdown(f'<div class="agent-badge {extra}">{route_display.get(route, "🤖 General")}</div>', unsafe_allow_html=True)
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about fitness..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

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
                    route_extra = "plan-badge" if route == "plan" else ""
                    st.markdown(f'<div class="agent-badge {route_extra}">{route_display.get(route, "🤖 General")}</div>', unsafe_allow_html=True)
                    st.markdown(reply)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "exhausted" in error_msg or "quota" in error_msg:
                        st.warning("⏳ API speed limit reached. Please wait 60 seconds and try again.")
                    else:
                        st.error(f"API Error: {e}")
        st.rerun()