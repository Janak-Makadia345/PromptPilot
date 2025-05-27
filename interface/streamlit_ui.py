# interface/streamlit_ui.py

import streamlit as st

class StreamlitUI:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def run(self):
        st.title("Personal AI Assistant - Streamlit UI")

        user_input = st.text_input("Enter your prompt:")

        if st.button("Submit") and user_input:
            result = self.orchestrator.process_prompt(user_input)
            if 'response' in result:
                st.markdown(f"**Response ({result['agent']}):** {result['response']}")
                st.markdown(f"_Processing time: {result['processing_time']:.2f} seconds_")
            else:
                st.error(f"Error: {result.get('error', 'Unknown error')}")

        # Optionally show conversation history
        if st.checkbox("Show conversation history"):
            history = self.orchestrator.get_conversation_history()
            for turn in history:
                role = turn.get('role', 'unknown')
                content = turn.get('content', '')
                st.markdown(f"**{role.capitalize()}:** {content}")

