import streamlit as st
from datetime import datetime
import traceback

class StreamlitUI:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        if "history" not in st.session_state:
            st.session_state.history = []

    def run(self):
        st.set_page_config(
            page_title="PromptPilot - Personal AI Assistant",
            page_icon="🤖",
            layout="centered",
            initial_sidebar_state="expanded"
        )

        st.title("🚀 PromptPilot: Your Personal AI Assistant")

        with st.sidebar:
            st.header("Settings")
            selected_agent = st.selectbox(
                "Choose Agent (optional)",
                options=["Auto", "NoteTaker", "EmailAgent", "CalendarAgent", "WebSearch", "FileAnalyzer", "CodeAgent"],
                index=0
            )
            if st.button("Clear Conversation History"):
                st.session_state.history = []
                st.success("Conversation history cleared.")

            st.markdown("---")
            st.markdown("Made with 💡 by Janak Makadia")

        prompt = st.text_area("Enter your prompt here:", height=120)

        if st.button("Submit") and prompt.strip():
            with st.spinner("Processing your request..."):
                try:
                    if selected_agent != "Auto":
                        result = self.orchestrator.process_prompt(prompt, agent=selected_agent)
                    else:
                        result = self.orchestrator.process_prompt(prompt)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.text(traceback.format_exc())
                    return

                # Debug: show raw result object
                st.write("### Debug: Raw result from orchestrator")
                st.json(result)

                response_text = result.get('response', 'No response.')
                agent_used = result.get('agent', 'Unknown')
                processing_time = result.get('processing_time', None)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                st.session_state.history.append({
                    "timestamp": timestamp,
                    "prompt": prompt,
                    "response": response_text,
                    "agent": agent_used,
                    "processing_time": processing_time,
                })

                st.markdown(f"### 🤖 Response from **{agent_used}**")
                st.markdown(response_text)
                if processing_time is not None:
                    st.caption(f"Processing time: {processing_time:.2f} seconds")
        else:
            st.info("Please enter a prompt above and press Submit to get started.")

        if st.checkbox("Show conversation history"):
            st.markdown("## 📝 Conversation History")
            if not st.session_state.history:
                st.info("No conversation history yet.")
            else:
                for idx, turn in enumerate(reversed(st.session_state.history), 1):
                    st.markdown(f"**[{turn['timestamp']}] Prompt:**")
                    st.markdown(f"> {turn['prompt']}")
                    st.markdown(f"**Response ({turn['agent']}):**")
                    st.markdown(f"{turn['response']}")
                    if turn['processing_time'] is not None:
                        st.caption(f"Processing time: {turn['processing_time']:.2f} seconds")
                    st.markdown("---")
