Even readme.md is written by AI 😁
But I worked harder on the project than AI

# WebTesterAgent 🚀

WebTesterAgent is a powerful, AI-driven web automation tool powered by **Google Gemini 2.0**. It allows users to control a web browser using natural language, making it ideal for automated testing, web scraping, and complex web interactions.

The agent can "see" the UI state, reason about the elements, and perform actions like clicking, typing, and navigating—just like a human.

## ✨ Features

- **Natural Language Control**: Describe what you want to do in plain English.
- **AI-Powered Reasoning**: Uses Gemini 2.0 Flash to understand complex UI layouts and dynamic content.
- **Smart UI Snapshots**: Automatically annotates clickable elements with unique IDs for precise interaction.
- **Action Batching**: Can perform multiple actions (like filling out a form) in a single turn.
- **Human-in-the-Loop**: Supports `wait_user` and `ask_user` actions for manual intervention when needed (e.g., solving CAPTCHAs, choosing certificates).
- **Stuck-State Detection**: Detects when actions have no effect and prompts for a different strategy.
- **Playwright Integration**: Built on top of Playwright for reliable and fast browser automation.

## 🛠️ Tech Stack

- **Languge**: Python 3.10+
- **LLM**: Google Gemini 2.0 Flash (`gemini-2.0-flash-exp` or similar)
- **Automation**: Playwright
- **Configuration**: Pydantic, Python-Dotenv

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.10+** installed.
2.  A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### Installation

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/WebTesterAgent.git
    cd WebTesterAgent
    ```

2.  **Create and activate a virtual environment**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4.  **Install Playwright browsers**:
    ```bash
    playwright install chromium
    ```

### Configuration

Create a `.env` file in the root directory and add your credentials:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

## 🎮 Usage

Run the agent using the `main.py` script:

```bash
python main.py
```

You can then enter your request, such as:

- _"Go to hippo.uz, login with my credentials, and check the latest invoices."_
- _"Search for 'Playwright' on YouTube and play the first video."_
- _"Navigate to example.com and tell me what the header says."_

Alternatively, you can pass the request as a command-line argument:

```bash
python main.py "Go to google.com and search for the weather in Tashkent"
```

## 📂 Project Structure

- `main.py`: The entry point of the application.
- `config.py`: Loads environment variables and initializes the Gemini client.
- `agent/`
  - `loop.py`: The core agent loop that manages the conversation and execution.
  - `browser.py`: Playwright wrapper for browser interactions and UI state capture.
  - `tools.py`: Definitions for agent actions and system instructions.

## ⚠️ Important Note

The agent is designed to be deterministic and cautious. If it gets stuck or requires manual input, it will pause and wait for your instructions. You can use this to handle complex steps that require human intervention.

---

Built with ❤️ using Gemini and Playwright.
