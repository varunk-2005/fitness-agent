import streamlit as st
from main import AgentRouter

with st.sidebar:
    st.title("About")
    st.markdown("This AI fitness assistant uses multiple specialized agents to give you the best advice.")
    st.markdown("**Agents:**")
    st.markdown("- 💪 Workout Agent")
    st.markdown("- 🥗 Nutrition Agent")
    st.markdown("- 🔀 Router Agent")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.agent = AgentRouter()
        st.rerun()

st.title("💪 Fitness AI Agent")

if "agent" not in st.session_state:
    st.session_state.agent = AgentRouter()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me about fitness..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Thinking..."):
        reply, route = st.session_state.agent.run(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)