import os
import sys
import argparse
import logging

# Clear proxy environment variables that might cause Client.__init__ error
for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(var, None)

from interface.cli import CLI
from interface.streamlit_ui import StreamlitUI
from core.orchestrator import Orchestrator
import config

# Configure logging
logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

def setup_orchestrator():
    return Orchestrator()

def main():
    # Detect if running inside Streamlit
    if os.getenv("STREAMLIT_SERVER_RUNNING"):
        interface_mode = 'web'
    else:
        parser = argparse.ArgumentParser(description='Personal AI Assistant')
        parser.add_argument(
            '--interface',
            choices=['cli', 'web'],
            default='web',
            help='Choose interface type (cli or web)'
        )
        args = parser.parse_args()
        interface_mode = args.interface

    orchestrator = setup_orchestrator()

    if interface_mode == 'cli':
        interface = CLI(orchestrator)
        try:
            interface.run()
        except Exception as e:
            logging.error(f"Unexpected CLI error: {e}", exc_info=True)
            print("An unexpected error occurred in CLI. Check logs.")
    else:
        interface = StreamlitUI(orchestrator)
        try:
            interface.run()
        except Exception as e:
            logging.error(f"Unexpected Streamlit error: {e}", exc_info=True)
            # Streamlit shows errors in UI automatically

if __name__ == "__main__":
    main()
