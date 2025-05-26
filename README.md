# Personal Assistant Application

This project is a personal assistant application designed to help users manage their tasks, notes, and schedules efficiently. It integrates various functionalities through specialized agents and utilizes a memory subsystem for semantic retrieval.

## Project Structure

The project is organized into several directories and files, each serving a specific purpose:

- **main.py**: Entry point for the application, handling user interactions.
- **config.py**: Contains configuration settings and constants.
- **.env**: Stores environment variables for sensitive information.
- **core/**: Contains the core logic of the application, including routing and agent management.
- **agents/**: Modular agents that handle specific tasks such as note-taking, calendar management, and web searching.
- **memory/**: Implements a vector memory subsystem for semantic retrieval.
- **interface/**: User-facing interfaces, including a command-line interface and a web interface.
- **services/**: External service integrations, such as Google Calendar and Gmail.
- **data/**: Stores user data, including notes and uploaded documents.
- **tests/**: Contains unit and integration tests for the application.
- **logs/**: Logs application events and errors.
- **requirements.txt**: Lists the dependencies required for the project.
- **setup.py**: Used for packaging and installing the application.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd personal-assistant
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables in the `.env` file.

5. Run the application:
   ```
   python main.py
   ```

## Usage

After running the application, users can interact with the personal assistant through the command-line interface or the web interface. The assistant can take notes, manage calendar events, perform web searches, and more.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.