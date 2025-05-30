# 🚀 PromptPilot: Your Personal AI Assistant 🧠🛸  
Built with ❤️ using **Python**, **LangChain**, **Gemini 2.0**, **FAISS**, and Modular AI Agents

🔗 [Check out the repo!](https://github.com/Janak-Makadia345/PromptPilot.git)

---

## 🤖 What is PromptPilot?

**PromptPilot** is an intelligent, multi-agent, prompt-driven assistant built to automate digital workflows using natural language. Powered by a **central Gemini 2.0 Flash LLM** and orchestrated modular agents, PromptPilot understands your intent and performs tasks like:

- 🧠 Taking notes  
- ✉️ Sending and reading emails  
- 📅 Managing calendar events  
- 🌍 Searching the web  
- 📂 Analyzing files  
- 💻 Understanding or debugging code  

All with one goal: **Just prompt it — we’ll handle the rest.**

---

## ✨ Key Functionalities

- 🔁 Modular, pluggable agents using a shared LLM
- 🧠 Semantic memory with FAISS vector embeddings
- 🔐 OAuth2 integration with Gmail and Calendar APIs
- 📂 Full support for local file parsing (PDFs, text, code)
- 🧩 Intelligent task routing to appropriate agents
- 🧪 Natural language as the only interface you need

---

## 🛠️ Tech Stack

| Component       | Tools Used                                 |
|----------------|---------------------------------------------|
| LLM             | Gemini 2.0 Flash via LangChain              |
| Framework       | Python, LangChain                          |
| Vector Store    | FAISS for embedding and memory retrieval    |
| Email API       | Gmail API via OAuth2                        |
| Calendar API    | Google Calendar API                         |
| Web Search      | SerpAPI or Google Search                    |
| PDF Parsing     | PyMuPDF                                     |
| Code Parsing    | AST + Python built-ins                      |
| Env Management  | python-dotenv                               |

---

## 🧩 AI Agents & Their Responsibilities

### 📝 NoteTaker Agent
The NoteTaker Agent is your personal digital notebook.

- Takes quick notes via prompt like:  
  _"Take a note: start preparing quarterly goals"_
- Automatically timestamps and embeds notes in FAISS
- Retrieve notes by natural query:  
  _"What were my notes about product launch?"_
- Notes are stored persistently and can be reused by other agents

---

### 🌐 WebSearch Agent
The WebSearch Agent helps you get real-time information from the internet.

- Accepts queries like:  
  _"Search latest AI breakthroughs in 2025"_
- Uses SerpAPI to fetch live search results
- Passes those results to LLM to summarize and respond concisely
- Can be used by other agents like the FileAnalyzer or EmailAgent for context enrichment

---

### 📅 Calendar Agent
The Calendar Agent manages all your scheduling needs.

- Create new events using prompts like:  
  _"Schedule meeting with Ravi on Tuesday at 10 AM"_
- View upcoming events:  
  _"What’s on my schedule this week?"_
- Uses **Google Calendar API** with secure OAuth2
- Automatically resolves relative dates like “next Friday”

---

### 📧 Email Agent
A full-featured mail assistant using **Gmail API**.

- **Send Emails**  
  _"Send an email to alex@gmail.com about our progress"_  
  → Drafted by LLM, confirmed with the user, then sent

- **Read & Filter Emails**  
  _"Show me unread emails from Google"_  
  _"What did John mail me last week?"_

- Supports subject filtering, date-based queries, sender matching

- Reuses vector memory to recall email context over time

---

### 📂 File Analyzer Agent
This agent helps you understand and extract knowledge from documents.

- Accepts files: PDFs, `.txt`, `.csv`, etc.
- Breaks content into semantic chunks
- Embeds all chunks into FAISS
- Supports follow-up questions like:  
  _"What are the key points of this document?"_  
  _"List all deadlines mentioned"_

- Great for contract review, academic papers, project briefs

---

### 💻 Code Agent
A smart code assistant for analysis, explanation, and debugging.

- Accepts `.py`, `.js`, and more
- Understands and explains code blocks via prompts:  
  _"What does this Python function do?"_
- Identifies bugs, poor patterns, or missing edge cases
- Can generate new code based on instructions like:  
  _"Write a Flask API for a to-do app"_
- Uses abstract syntax tree (AST) and semantic reasoning

---

## 💬 Prompt Examples

- 🗒️ “Take a note: Migrate backend to FastAPI”
- 📬 “Send an email to raj@example.com about the demo video”
- 🌍 “Search for best practices in prompt engineering”
- 📂 “Analyze this PDF for budget highlights”
- 📅 “Schedule a call with Sam next Thursday at 3 PM”
- 💻 “Debug this script and suggest improvements”

---

## ⚙️ Setup Instructions

```bash
# 🔧 One-step Setup Guide

# 1. Clone the repository
git clone https://github.com/Janak-Makadia345/PromptPilot.git && cd PromptPilot

# 2. Set up a virtual environment
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create a .env file in the root directory and add:
# 
# GEMINI_API_KEY=your_gemini_key
# SERPAPI_API_KEY=your_serpapi_key
# GOOGLE_APPLICATION_CREDENTIALS=path_to_your_gcp_credentials.json

# 5. Run the assistant
python main.py
```
---

## 🌱 Roadmap

- 🧵 Memory across long conversations and chained prompts  
- 🗣️ Voice-to-command interface with Whisper  
- 🧑‍💻 Web-based GUI for prompt input/output visualization  
- 📱 Telegram/Slack bot version  
- 🧠 Agent-to-agent collaboration  

---

## 🤝 Contribute

We’d love your help in growing PromptPilot!

1. 🍴 Fork the repo  
2. 🌱 Create a new branch  
3. 💾 Make your changes  
4. 📬 Submit a pull request  

---

## 👤 Author

Made with 💡 by Janak Makadia  
Let’s build the future of AI together! 🛸

---

🧠 PromptPilot – Just prompt it. We’ll handle it.
