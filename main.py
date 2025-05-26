import argparse
import logging
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

def setup_orchestrator():
    """Initialize the orchestrator with all required components"""
    return Orchestrator()

def main():
    parser = argparse.ArgumentParser(description='Personal AI Assistant')
    parser.add_argument(
        '--interface', 
        choices=['cli', 'web'], 
        default='cli',
        help='Choose interface type (cli or web)'
    )
    
    args = parser.parse_args()
    orchestrator = setup_orchestrator()
    
    if args.interface == 'cli':
        interface = CLI(orchestrator)
    else:
        interface = StreamlitUI(orchestrator)
    
    interface.run()

if __name__ == "__main__":
    main()