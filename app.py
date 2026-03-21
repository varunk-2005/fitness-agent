import streamlit as st
from main import AgentRouter
from database import (
    init_db, save_profile, load_profile,
    save_message, load_chat_history, clear_chat_history,
    save_workout_log, load_workout_logs,
    save_nutrition_log, load_nutrition_logs,
    save_recovery_log, load_recovery_logs
)

# ─── Init DB on every app start ───────────────────────────────────────────────
init_db()

st.set_page_config(
    page_title="Fitness AI Agent",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #f8fafc;
    }
    .app-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #22c55e, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
    }
    .app-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.96);
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    .info-card {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .metric-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 18px;
        text-align: center;
    }
    .metric-title { color: #94a3b8; font-size: 0.9rem; }
    .metric-value { color: #f8fafc; font-size: 1.2rem; font-weight: 700; margin-top: 6px; }
    .welcome-box {
        background: linear-gradient(135deg, rgba(34,197,94,0.12), rgba(6,182,212,0.12));
        border: 1px solid rgba(34, 197, 94, 0.25);
        border-radius: 18px;
        padding: 28px;
        margin: 18px 0 24px 0;
    }
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        background: rgba(34,197,94,0.15);
        color: #4ade80;
        border: 1px solid rgba(34,197,94,0.3);
        margin-bottom: 8px;
    }
    div[data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 12px;
        background: rgba(30, 41, 59, 0.42);
        border: 1px solid rgba(255,255,255,0.05);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: rgba(6, 182, 212, 0.08);
        border: 1px solid rgba(6, 182, 212, 0.14);
    }
    .log-entry {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.88rem;
        color: #cbd5e1;
    }
    .footer-note {
        color: #94a3b8;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ───────────────────────────────────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()
if "profile" not in st.session_state:
    st.session_state.profile = load_profile()        # ← load from DB
if "profile_skipped" not in st.session_state:
    st.session_state.profile_skipped = False
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()  # ← load from DB

route_display = {
    "workout": "💪 Workout Agent",
    "nutrition": "🥗 Nutrition Agent",
    "recovery": "🛌 Recovery Agent",
    "both": "⚡ Workout + Nutrition",
    "unknown": "❓ Unknown"
}

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="info-card">
        <h2 style="margin-top: 0;">🏋️ Fitness AI Agent</h2>
        <p style="margin-bottom: 10px;">
            A multi-agent fitness assistant for workout, nutrition, and recovery guidance.
        </p>
        <strong>Available Agents:</strong>
        <ul style="margin-top: 8px; margin-bottom: 0; padding-left: 20px;">
            <li>💪 Workout Agent</li>
            <li>🥗 Nutrition Agent</li>
            <li>🛌 Recovery Agent</li>
            <li>🔀 Router Agent</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # ── Profile Section ───────────────────────────────────────────────────────
    st.subheader("👤 User Profile")

    if st.session_state.profile:
        p = st.session_state.profile
        bmi = round(p['weight'] / ((p['height'] / 100) ** 2), 1)
        bmi_label = (
            "Underweight" if bmi < 18.5 else
            "Normal"      if bmi < 25   else
            "Overweight"  if bmi < 30   else
            "Obese"
        )
        st.markdown(f"""
        <div class="info-card" style="border-color: rgba(34,197,94,0.28);">
            <div style="color:#4ade80; font-weight:700; margin-bottom:10px;">✅ Active Profile</div>
            <strong>Age:</strong> {p['age']}<br>
            <strong>Weight:</strong> {p['weight']} kg<br>
            <strong>Height:</strong> {p['height']} cm<br>
            <strong>Goal:</strong> {p['goal']}<br>
            <hr style="border-color:rgba(255,255,255,0.08); margin:10px 0;">
            <strong>BMI:</strong> {bmi} — {bmi_label}
        </div>
        """, unsafe_allow_html=True)

        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.profile = None
            st.session_state.profile_skipped = False
            st.rerun()

    elif not st.session_state.profile_skipped:
        age    = st.number_input("Age",         min_value=10,  max_value=100, value=21)
        weight = st.number_input("Weight (kg)", min_value=30,  max_value=200, value=70)
        height = st.number_input("Height (cm)", min_value=100, max_value=230, value=170)
        goal   = st.selectbox("Primary Goal",
                     ["Lose Weight", "Build Muscle", "Stay Fit", "Improve Endurance"])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary", use_container_width=True):
                save_profile(age, weight, height, goal)    # ← save to DB
                st.session_state.profile = load_profile()  # ← reload from DB
                st.rerun()
        with col2:
            if st.button("Skip", use_container_width=True):
                st.session_state.profile_skipped = True
                st.rerun()
    else:
        st.info("Profile not set. Responses will be general.")
        if st.button("➕ Set Up Profile", use_container_width=True):
            st.session_state.profile_skipped = False
            st.rerun()

    st.divider()

    # ── Log Section ───────────────────────────────────────────────────────────
    st.subheader("📋 Log Today")
    log_tab = st.selectbox("Log type", ["Workout", "Nutrition", "Recovery"])

    if log_tab == "Workout":
        w_type = st.text_input("Workout type (e.g. Chest, Legs)")
        w_dur  = st.number_input("Duration (mins)", min_value=1, max_value=300, value=45)
        w_note = st.text_input("Notes (optional)")
        if st.button("💾 Save Workout Log", use_container_width=True):
            save_workout_log(w_type, w_dur, w_note)
            st.success("Workout logged!")

    elif log_tab == "Nutrition":
        n_cal  = st.number_input("Calories", min_value=0, max_value=10000, value=2000)
        n_pro  = st.number_input("Protein (g)", min_value=0, max_value=500, value=100)
        n_note = st.text_input("Notes (optional)")
        if st.button("💾 Save Nutrition Log", use_container_width=True):
            save_nutrition_log(n_cal, n_pro, n_note)
            st.success("Nutrition logged!")

    elif log_tab == "Recovery":
        r_sleep = st.number_input("Sleep (hrs)", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        r_sore  = st.slider("Soreness (1=none, 5=severe)", 1, 5, 2)
        r_note  = st.text_input("Notes (optional)")
        if st.button("💾 Save Recovery Log", use_container_width=True):
            save_recovery_log(r_sleep, r_sore, r_note)
            st.success("Recovery logged!")

    st.divider()

    # ── Recent Logs ───────────────────────────────────────────────────────────
    st.subheader("📊 Recent Logs")
    view_tab = st.selectbox("View logs", ["Workout", "Nutrition", "Recovery"])

    if view_tab == "Workout":
        logs = load_workout_logs(limit=5)
        if logs:
            for log in logs:
                st.markdown(f"""
                <div class="log-entry">
                    📅 {log['date']} &nbsp;|&nbsp; 🏋️ {log['workout_type']} &nbsp;|&nbsp; ⏱ {log['duration_minutes']} mins
                    {"<br>📝 " + log['notes'] if log['notes'] else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.caption("No workout logs yet.")

    elif view_tab == "Nutrition":
        logs = load_nutrition_logs(limit=5)
        if logs:
            for log in logs:
                st.markdown(f"""
                <div class="log-entry">
                    📅 {log['date']} &nbsp;|&nbsp; 🔥 {log['calories']} kcal &nbsp;|&nbsp; 💪 {log['protein_g']}g protein
                    {"<br>📝 " + log['notes'] if log['notes'] else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.caption("No nutrition logs yet.")

    elif view_tab == "Recovery":
        logs = load_recovery_logs(limit=5)
        if logs:
            for log in logs:
                st.markdown(f"""
                <div class="log-entry">
                    📅 {log['date']} &nbsp;|&nbsp; 😴 {log['sleep_hours']} hrs &nbsp;|&nbsp; 🤕 Soreness: {log['soreness_level']}/5
                    {"<br>📝 " + log['notes'] if log['notes'] else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.caption("No recovery logs yet.")

    st.divider()
    st.subheader("🧾 Project Highlights")
    st.markdown("""
    - Multi-agent architecture
    - Intelligent LLM-based routing
    - Personalized fitness suggestions
    - SQLite persistent storage
    - Streamlit-based interactive UI
    """)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_chat_history()               # ← clear from DB
        st.session_state.messages = []
        st.session_state.agent = AgentRouter()
        st.rerun()

# ─── Main Area ────────────────────────────────────────────────────────────────
st.markdown('<div class="app-title">Fitness AI Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">A multi-agent assistant for workout planning, nutrition guidance, and recovery advice.</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""<div class="metric-card">
        <div class="metric-title">Core Modules</div>
        <div class="metric-value">4 Agents</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown("""<div class="metric-card">
        <div class="metric-title">Personalization</div>
        <div class="metric-value">Profile-Based</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown("""<div class="metric-card">
        <div class="metric-title">Storage</div>
        <div class="metric-value">SQLite DB</div>
    </div>""", unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <h2 style="margin-top:0;">Welcome to your AI Fitness Assistant 🚀</h2>
        <p style="color:#cbd5e1; font-size:1.05rem; margin-bottom:0;">
            Ask anything related to training, food, recovery, or fitness planning.
            <br><br>
            <b>Examples:</b><br>
            "Create a 4-day muscle gain workout plan"<br>
            "Suggest a high-protein vegetarian diet"<br>
            "How can I recover faster from leg day soreness?"
        </p>
    </div>
    """, unsafe_allow_html=True)

# ─── Chat History Display ─────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "agent_route" in message:
            st.markdown(
                f'<div class="agent-badge">{route_display.get(message["agent_route"], message["agent_route"])}</div>',
                unsafe_allow_html=True
            )
        st.markdown(message["content"])

# ─── Chat Input ───────────────────────────────────────────────────────────────
if prompt := st.chat_input("Ask me anything about fitness..."):

    save_message("user", prompt, agent_route="user")   # ← save to DB
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            profile = st.session_state.profile

            if profile:
                enriched_prompt = f"""User Profile:
- Age: {profile['age']}
- Weight: {profile['weight']} kg
- Height: {profile['height']} cm
- Goal: {profile['goal']}

User Query:
{prompt}"""
            else:
                enriched_prompt = prompt

            try:
                reply, route = st.session_state.agent.run(enriched_prompt)

                save_message("assistant", reply, agent_route=route)  # ← save to DB
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "agent_route": route
                })

                st.markdown(
                    f'<div class="agent-badge">{route_display.get(route, route)}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(reply)

            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "agent_route": "unknown"
                })

st.markdown(
    '<div class="footer-note">Built using Streamlit · Python · Multi-Agent Routing · SQLite</div>',
    unsafe_allow_html=True
)