import streamlit as st
from main import AgentRouter

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

    .metric-title {
        color: #94a3b8;
        font-size: 0.9rem;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 6px;
    }

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

    .footer-note {
        color: #94a3b8;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 14px;
    }
</style>
""", unsafe_allow_html=True)

if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = None
if "profile_skipped" not in st.session_state:
    st.session_state.profile_skipped = False

route_display = {
    "workout": "💪 Workout Agent",
    "nutrition": "🥗 Nutrition Agent",
    "recovery": "🛌 Recovery Agent",
    "both": "⚡ Workout + Nutrition",
    "unknown": "❓ Unknown"
}

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

    st.subheader("👤 User Profile")

    if st.session_state.profile:
        p = st.session_state.profile
        st.markdown(f"""
        <div class="info-card" style="border-color: rgba(34,197,94,0.28);">
            <div style="color:#4ade80; font-weight:700; margin-bottom:10px;">✅ Active Profile</div>
            <strong>Age:</strong> {p['age']}<br>
            <strong>Weight:</strong> {p['weight']} kg<br>
            <strong>Height:</strong> {p['height']} cm<br>
            <strong>Goal:</strong> {p['goal']}
        </div>
        """, unsafe_allow_html=True)

        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.profile = None
            st.session_state.profile_skipped = False
            st.rerun()

    elif not st.session_state.profile_skipped:
        age = st.number_input("Age", min_value=10, max_value=100, value=21)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
        height = st.number_input("Height (cm)", min_value=100, max_value=230, value=170)
        goal = st.selectbox(
            "Primary Goal",
            ["Lose Weight", "Build Muscle", "Stay Fit", "Improve Endurance"]
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary", use_container_width=True):
                st.session_state.profile = {
                    "age": age,
                    "weight": weight,
                    "height": height,
                    "goal": goal
                }
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

    st.subheader("🧾 Project Highlights")
    st.markdown("""
    - Multi-agent architecture  
    - Intelligent routing  
    - Personalized fitness suggestions  
    - Streamlit-based interactive UI  
    """)

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = AgentRouter()
        st.rerun()

st.markdown('<div class="app-title">Fitness AI Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">A multi-agent assistant for workout planning, nutrition guidance, and recovery advice.</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Core Modules</div>
        <div class="metric-value">4 Agents</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Personalization</div>
        <div class="metric-value">Profile-Based</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Interface</div>
        <div class="metric-value">Interactive Chat</div>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <h2 style="margin-top:0;">Welcome to your AI Fitness Assistant 🚀</h2>
        <p style="color:#cbd5e1; font-size:1.05rem; margin-bottom:0;">
            Ask anything related to training, food, recovery, or fitness planning.
            <br><br>
            <b>Examples:</b><br>
            “Create a 4-day muscle gain workout plan”<br>
            “Suggest a high-protein vegetarian diet”<br>
            “How can I recover faster from leg day soreness?”
        </p>
    </div>
    """, unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and "route" in message:
            st.markdown(
                f'<div class="agent-badge">{route_display.get(message["route"], message["route"])}</div>',
                unsafe_allow_html=True
            )
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about fitness..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            profile = st.session_state.profile

            if profile:
                enriched_prompt = f"""
User Profile:
- Age: {profile['age']}
- Weight: {profile['weight']} kg
- Height: {profile['height']} cm
- Goal: {profile['goal']}

User Query:
{prompt}
"""
            else:
                enriched_prompt = prompt

            try:
                reply, route = st.session_state.agent.run(enriched_prompt)
                st.markdown(
                    f'<div class="agent-badge">{route_display.get(route, route)}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(reply)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                    "route": route
                })
            except Exception as e:
                error_msg = f"Error: {e}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "route": "unknown"
                })

st.markdown(
    '<div class="footer-note">Built using Streamlit + Python + Multi-Agent Routing</div>',
    unsafe_allow_html=True
)