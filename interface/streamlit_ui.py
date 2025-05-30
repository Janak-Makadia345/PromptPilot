import streamlit as st
from datetime import datetime
import traceback
import base64

# Helper function to convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

class StreamlitUI:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        if "history" not in st.session_state:
            st.session_state.history = []

    def run(self):
        # Load and embed logo image
        logo_data = get_base64_image("interface/assets/prompt_pilot.png")

        st.set_page_config(
            page_title="PromptPilot - Personal AI Assistant",
            page_icon=logo_data,
            layout="centered",
            initial_sidebar_state="expanded"
        )

        # Display logo and title inline
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 30px;'>
                <img src='{logo_data}' alt='PromptPilot Logo' width='80' height='80'>
                <h1 style='margin: 0;'>PromptPilot: Your Personal AI Assistant 🚀</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Sidebar settings
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

        # Prompt input
        prompt = st.text_area("Enter your prompt here:", height=120)

        # On submit
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

        # Show history
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
