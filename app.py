import streamlit as st
import time

# --- Dummy AgentRouter for testing the UI ---
# Replace this class with: from main import AgentRouter
class AgentRouter:
    def run(self, prompt):
        time.sleep(1) # Simulate thinking
        return "Here is your personalized fitness advice based on your profile! Let's get to work. 🚀", "💪 Workout Agent"

# ---------- 1. Page Configuration ----------
st.set_page_config(
    page_title="Fitness AI Agent",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- 2. Custom CSS ----------
st.markdown("""
<style>
    /* Gradient Background and general text */
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #f8fafc;
    }

    /* Main Title */
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
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Info Cards */
    .info-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    /* Welcome Box */
    .welcome-box {
        background: linear-gradient(135deg, rgba(34,197,94,0.1), rgba(6,182,212,0.1));
        border: 1px solid rgba(34, 197, 94, 0.2);
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
    }

    /* Badges */
    .agent-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
        background: rgba(34,197,94,0.15);
        color: #4ade80;
        border: 1px solid rgba(34,197,94,0.3);
        margin-bottom: 8px;
    }

    /* Chat Message adjustments */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px;
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255,255,255,0.03);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: rgba(6, 182, 212, 0.05);
        border: 1px solid rgba(6, 182, 212, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------- 3. Session State ----------
if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = None
if "profile_skipped" not in st.session_state:
    st.session_state.profile_skipped = False

# ---------- 4. Sidebar ----------
with st.sidebar:
    st.markdown("""
    <div class="info-card">
        <h2 style="margin-top: 0; padding-top: 0;">🏋️ Fitness AI</h2>
        <p style="margin-bottom: 10px;">Your smart fitness assistant powered by specialized agents.</p>
        <strong>Active Agents:</strong>
        <ul style="margin-top: 8px; margin-bottom: 0; padding-left: 20px;">
            <li>💪 Workout</li>
            <li>🥗 Nutrition</li>
            <li>🛌 Recovery</li>
            <li>🔀 Router</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("👤 Your Profile")
    
    # Profile Display Logic
    if st.session_state.profile:
        p = st.session_state.profile
        st.markdown(f"""
        <div class="info-card" style="border-color: rgba(34,197,94,0.3);">
            <div style="color: #4ade80; font-weight: bold; margin-bottom: 10px;">✅ Profile Active</div>
            <strong>Age:</strong> {p['age']} | <strong>Weight:</strong> {p['weight']}kg<br><br>
            <strong>Height:</strong> {p['height']}cm | <strong>Goal:</strong> {p['goal']}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.profile = None
            st.session_state.profile_skipped = False
            st.rerun()

    # Profile Setup Logic
    elif not st.session_state.profile_skipped:
        age = st.number_input("Age", min_value=10, max_value=100, value=25)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=70)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        goal = st.selectbox("Goal", ["Lose Weight", "Build Muscle", "Stay Fit", "Improve Endurance"])
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save", type="primary", use_container_width=True):
                st.session_state.profile = {"age": age, "weight": weight, "height": height, "goal": goal}
                st.session_state.profile_skipped = False
                st.rerun()
        with col2:
            if st.button("Skip", use_container_width=True):
                st.session_state.profile = None
                st.session_state.profile_skipped = True
                st.rerun()
    
    # Skipped Profile Logic
    else:
        st.info("Profile setup skipped. Advice will be generalized.")
        if st.button("➕ Set Up Profile", use_container_width=True):
            st.session_state.profile_skipped = False
            st.rerun()

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent = AgentRouter()
        st.rerun()

# ---------- 5. Main Chat Interface ----------
st.markdown('<div class="app-title">Fitness AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Your personal coach for workouts, nutrition, and recovery.</div>', unsafe_allow_html=True)

# Empty State Welcome Message
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-box">
        <h2 style="margin-top:0;">Ready to crush your goals? 🚀</h2>
        <p style="color:#cbd5e1; font-size: 1.1rem;">
            Ask me anything about fitness! Try asking:<br><br>
            <em>"Build me a 3-day full body workout."</em><br>
            <em>"What should I eat for high protein on a budget?"</em><br>
            <em>"How do I recover faster from deadlifts?"</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # If it's the assistant, show which agent handled it
        if message["role"] == "assistant" and "route" in message:
            st.markdown(f'<div class="agent-badge">{message["route"]}</div>', unsafe_allow_html=True)
        st.markdown(message["content"])

# Chat Input Handler
if prompt := st.chat_input("Ask me about fitness..."):
    # 1. Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Process with Agent
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your request..."):
            profile = st.session_state.profile
            if profile:
                enriched_prompt = f"[User Profile: Age={profile['age']}, Weight={profile['weight']}kg, Height={profile['height']}cm, Goal={profile['goal']}]\n\n{prompt}"
            else:
                enriched_prompt = prompt
            
            # Call your backend logic
            reply, route = st.session_state.agent.run(enriched_prompt)
            
            # 3. Display Agent Badge and Response
            st.markdown(f'<div class="agent-badge">{route}</div>', unsafe_allow_html=True)
            st.markdown(reply)
            
    # 4. Save assistant response to state
    st.session_state.messages.append({
        "role": "assistant", 
        "content": reply,
        "route": route
    })