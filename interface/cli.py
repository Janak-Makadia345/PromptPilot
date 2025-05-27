# interface/cli.py

class CLI:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def run(self):
        print("CLI interface started.")
        while True:
            user_input = input("You: ")
            if user_input.lower() in ('exit', 'quit'):
                print("Exiting CLI.")
                break

            response = self.orchestrator.process_prompt(user_input)
            print(f"Assistant ({response.get('agent', 'unknown')}): {response.get('response', 'No response')}")
