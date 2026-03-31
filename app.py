import streamlit as st
import json
import os
from datetime import date
import hashlib
import traceback

# ── 1. PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fitness AI Agent",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 2. LOCAL DB SETUP ─────────────────────────────────────────────────────────
USERS_FILE = "users.json"


def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)
    except Exception as e:
        st.warning(f"⚠️ Could not save user data: {e}")


# ── 3. UTILITIES ──────────────────────────────────────────────────────────────
def make_agent():
    from main import AgentRouter
    return AgentRouter()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_latest_agent_messages():
    found = {}
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "assistant" and "agent_route" in msg:
            route = msg["agent_route"]
            if route not in found:
                found[route] = msg["content"]
    return found


def build_email_body(messages, username):
    label_map = {
        "workout":   "💪 WORKOUT",
        "nutrition": "🥗 NUTRITION",
        "recovery":  "🛌 RECOVERY",
        "both":      "⚡ WORKOUT + NUTRITION",
        "plan":      "📅 FULL FITNESS PLAN",
        "general":   "🤖 GENERAL ADVICE",
    }
    parts = []
    for route, content in messages.items():
        text = content if isinstance(content, str) else str(content)
        parts.append(f"{label_map.get(route, route.upper())}\n{text}")
    body = f"Hi {username}!\n\nHere's your fitness update:\n\n"
    body += "\n\n---\n\n".join(parts)
    body += "\n\n---\nYours truly,\nFitness App 💪"
    return body


# ── 4. STYLING ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .app-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(90deg, #16a34a, #0891b2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0; line-height: 1.15;
    }
    .app-subtitle { color: var(--text-color); opacity: 0.6; font-size: 1.05rem; margin-bottom: 1.5rem; }
    .info-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 14px; padding: 16px; margin-bottom: 16px; color: var(--text-color);
    }
    .welcome-box {
        background: var(--secondary-background-color);
        border: 1px solid rgba(22,163,74,0.35);
        border-left: 4px solid #16a34a;
        border-radius: 14px; padding: 28px; margin: 18px 0 24px 0; color: var(--text-color);
    }
    .agent-badge {
        display: inline-block; padding: 4px 12px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 700;
        background: rgba(22,163,74,0.15); color: #16a34a;
        border: 1px solid rgba(22,163,74,0.35); margin-bottom: 8px;
    }
    .plan-badge {
        background: rgba(139,92,246,0.15); color: #7c3aed;
        border: 1px solid rgba(139,92,246,0.35);
    }
    div[data-testid="stChatMessage"] {
        border-radius: 14px; padding: 12px;
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.12);
    }
    div[data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {
        background: rgba(8,145,178,0.08);
        border: 1px solid rgba(8,145,178,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ── 5. SESSION STATE ──────────────────────────────────────────────────────────
_defaults = {
    "logged_in": False,
    "username": None,
    "agent": None,
    "messages": [],
    "show_email_input": False,
}
for key, val in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

route_display = {
    "workout":   "💪 Workout Agent",
    "nutrition": "🥗 Nutrition Agent",
    "recovery":  "🛌 Recovery Agent",
    "both":      "⚡ Workout + Nutrition",
    "general":   "🤖 Fitness Assistant",
    "plan":      "🧠 Full Plan — All Agents",
}

# ── 6. AUTH ───────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="app-title">Welcome to Fitness AI</div>', unsafe_allow_html=True)
    st.write("Please log in or create an account to continue.")

    tab1, tab2 = st.tabs(["🔒 Login", "📝 Sign Up"])

    with tab1:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            if login_user and login_pass:
                with st.spinner("Logging in..."):
                    try:
                        users = load_users()
                        if login_user not in users:
                            st.error("❌ Username not found. Please sign up.")
                        elif users[login_user].get("password") != hash_password(login_pass):
                            st.error("❌ Incorrect password.")
                        else:
                            with st.spinner("Setting up your agents..."):
                                try:
                                    st.session_state.agent = make_agent()
                                except Exception:
                                    st.error(f"❌ Agent setup failed:\n\n```\n{traceback.format_exc()}\n```")
                                    st.stop()
                            st.session_state.username = login_user
                            st.session_state.logged_in = True
                            st.success("✅ Login successful!")
                            st.rerun()
                    except Exception:
                        st.error(f"❌ Login error:\n\n```\n{traceback.format_exc()}\n```")
            else:
                st.warning("Please fill in both fields.")

    with tab2:
        signup_user = st.text_input("Choose a Username", key="signup_user")
        signup_pass = st.text_input("Choose a Password", type="password", key="signup_pass")
        signup_email = st.text_input("Your Email (for future notifications)", key="signup_email")
        if st.button("Create Account"):
            if signup_user and signup_pass:
                with st.spinner("Creating account..."):
                    try:
                        users = load_users()
                        if signup_user in users:
                            st.error("❌ Username already exists!")
                        else:
                            users[signup_user] = {
                                "password": hash_password(signup_pass),
                                "email": signup_email,
                                "created_at": str(date.today()),
                            }
                            save_users(users)
                            st.success("✅ Account created! You can now log in.")
                    except Exception:
                        st.error(f"❌ Sign up error:\n\n```\n{traceback.format_exc()}\n```")
            else:
                st.warning("Please fill in username and password.")

# ── 7. MAIN APP ───────────────────────────────────────────────────────────────
else:
    if st.session_state.agent is None:
        with st.spinner("Setting up agents..."):
            try:
                st.session_state.agent = make_agent()
            except Exception:
                st.error(f"❌ Agent init failed:\n\n```\n{traceback.format_exc()}\n```")
                st.stop()

    st.session_state.agent.set_username(st.session_state.username)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.success(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.agent = None
            st.session_state.messages = []
            st.session_state.show_email_input = False
            st.rerun()

        st.divider()
        st.subheader("👤 Your Profile")
        st.info("Fill these in for personalised advice.", icon="💡")

        st.selectbox(
            "Your Goal",
            ["Not Specified", "Lose Weight", "Build Muscle", "Stay Fit", "Improve Endurance"],
            key="profile_goal",
            index=0,
        )
        profile_age = st.number_input(
            "Age", min_value=0, max_value=120, value=0, step=1,
            key="profile_age", help="Leave at 0 to skip",
        )
        profile_height = st.number_input(
            "Height (cm)", min_value=0, max_value=300, value=0, step=1,
            key="profile_height", help="Leave at 0 to skip",
        )
        profile_weight = st.number_input(
            "Weight (kg)", min_value=0, max_value=300, value=0, step=1,
            key="profile_weight", help="Leave at 0 to skip",
        )

        st.divider()
        st.markdown(
            '<div class="info-card"><h2 style="margin-top:0;">🏋️ Fitness AI Agent</h2>'
            '<p style="margin-bottom:0; opacity:0.8;">Your personal multi-agent fitness assistant.</p></div>',
            unsafe_allow_html=True,
        )
        st.divider()

        st.subheader("📧 Email Yourself")
        if not st.session_state.show_email_input:
            if st.button("📧 Email Yourself", use_container_width=True):
                st.session_state.show_email_input = True
                st.rerun()
        else:
            latest = get_latest_agent_messages()
            if not latest:
                st.info("💡 Chat first, then email yourself your plan!")
            email_input = st.text_input("Enter your email", key="email_input")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📨 Send", use_container_width=True, type="primary"):
                    if not email_input:
                        st.warning("Enter an email first.")
                    elif not latest:
                        st.warning("Have a conversation first!")
                    else:
                        with st.spinner("Sending..."):
                            try:
                                body = build_email_body(latest, st.session_state.username)
                                ok, msg = st.session_state.agent.email_agent.send(
                                    email_input, "Fitness Update 🏋️", body
                                )
                                if ok:
                                    st.success("🎉 Sent!")
                                    st.session_state.show_email_input = False
                                    st.rerun()
                                else:
                                    st.error(f"❌ {msg}")
                            except Exception:
                                st.error(f"❌ Email error:\n\n```\n{traceback.format_exc()}\n```")
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_email_input = False
                    st.rerun()

        st.divider()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.agent:
                st.session_state.agent.reset_all()
            else:
                st.session_state.agent = make_agent()
            st.rerun()

    # ── CHAT AREA ─────────────────────────────────────────────────────────────
    st.markdown('<div class="app-title">Fitness AI Agent</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-subtitle">Your personalised multi-agent assistant.</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.markdown(
            f"""
            <div class="welcome-box">
                <h2 style="margin-top:0;">Welcome back, {st.session_state.username} 🚀</h2>
                <p style="font-size:1.05rem; margin-bottom:0;">
                    Ask me anything about training, food, or recovery.
                    Want everything at once? Ask for a <strong>full fitness package</strong>!
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "agent_route" in message:
                route = message["agent_route"]
                extra = "plan-badge" if route == "plan" else ""
                st.markdown(
                    f'<div class="agent-badge {extra}">{route_display.get(route, "🤖 General")}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask me anything about fitness..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting the agents..."):
                profile_parts = []
                if st.session_state.profile_goal != "Not Specified":
                    profile_parts.append(f"Goal={st.session_state.profile_goal}")
                if st.session_state.profile_age > 0:
                    profile_parts.append(f"Age={st.session_state.profile_age}")
                if st.session_state.profile_height > 0:
                    profile_parts.append(f"Height={st.session_state.profile_height}cm")
                if st.session_state.profile_weight > 0:
                    profile_parts.append(f"Weight={st.session_state.profile_weight}kg")
                profile_text = f"User Profile: {', '.join(profile_parts)}" if profile_parts else None

                reply = None
                route = "general"

                try:
                    reply, route = st.session_state.agent.run(prompt, profile_text)

                except (TypeError, AttributeError):
                    # Stale agent in session state — recreate and retry once
                    try:
                        st.session_state.agent = make_agent()
                        st.session_state.agent.set_username(st.session_state.username)
                        reply, route = st.session_state.agent.run(prompt, profile_text)
                    except Exception:
                        st.error(f"❌ Agent setup failed:\n\n```\n{traceback.format_exc()}\n```")

                except Exception as e:
                    # Always show the real error — never hide it behind a vague message
                    err_type = type(e).__name__
                    err_msg = str(e)
                    tb = traceback.format_exc()
                    st.error(
                        f"❌ **{err_type}:** {err_msg}\n\n"
                        f"```\n{tb}\n```"
                    )

                if reply is not None:
                    st.session_state.messages.append(
                        {"role": "assistant", "content": reply, "agent_route": route}
                    )
                    route_extra = "plan-badge" if route == "plan" else ""
                    st.markdown(
                        f'<div class="agent-badge {route_extra}">{route_display.get(route, "🤖 General")}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(reply)