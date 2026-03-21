import streamlit as st
from main import AgentRouter

if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = None

with st.sidebar:
    st.title("About")
    st.markdown("This AI fitness assistant uses multiple specialized agents to give you the best advice.")
    st.markdown("**Agents:**")
    st.markdown("- 💪 Workout Agent")
    st.markdown("- 🥗 Nutrition Agent")
    st.markdown("- 🔀 Router Agent")  
    st.markdown("- 🛌 Recovery Agent")  
    st.divider()
    st.subheader("Your Profile")
    if st.session_state.profile:
        p = st.session_state.profile
        st.success(f"✅ Active Profile")
        st.markdown(f"**Age:** {p['age']} | **Weight:** {p['weight']}kg | **Height:** {p['height']}cm")
        st.markdown(f"**Goal:** {p['goal']}")
        if st.button("Edit Profile"):
            st.session_state.profile = None
            st.rerun()
    else:
        age = st.number_input("Age", min_value=10, max_value=100, value=25)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=70)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        goal = st.selectbox("Goal", ["Lose Weight", "Build Muscle", "Stay Fit", "Improve Endurance"])
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Profile"):
                st.session_state.profile = {"age": age, "weight": weight, "height": height, "goal": goal}
                st.rerun()
        with col2:
            if st.button("Skip"):
                st.session_state.profile = None
                st.rerun()

    st.divider()
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.agent = AgentRouter()
        st.rerun()

st.title("💪 Fitness AI Agent")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about fitness..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Thinking..."):
        profile = st.session_state.profile
        if profile:
            enriched_prompt = f"[User Profile: Age={profile['age']}, Weight={profile['weight']}kg, Height={profile['height']}cm, Goal={profile['goal']}]\n\n{prompt}"
        else:
            enriched_prompt = prompt
        reply, route = st.session_state.agent.run(enriched_prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)