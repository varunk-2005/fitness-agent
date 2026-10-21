# 💪 Fitness AI Agent

A multi-agent fitness assistant built with **Python**, **Streamlit** and **Google Gemini**. A router agent classifies each question and hands it to a specialist agent (workout, nutrition, recovery, or a full weekly plan). Answers are personalised from the user's profile, and users can email their latest plan to themselves.

## Features

- **Multi-agent routing:** an LLM router sends each message to the right specialist.
- **Specialist agents** for workouts, nutrition, recovery, and a combined "full package" weekly plan.
- **Personalised advice:** optional goal, age, height and weight are added to every prompt. Agents calculate BMI, calorie targets (Mifflin-St Jeor), protein and water intake.
- **Context-aware follow-ups:** the General agent rewrites short replies like "yeah do that" into standalone questions using conversation history, then re-routes them.
- **Per-agent conversation memory**, cleared with one click.
- **Login and sign-up** with SHA-256 hashed passwords.
- **Email yourself:** sends the latest response from each agent to any inbox over Gmail SMTP.
- **Retry with exponential backoff** for Gemini rate-limit (429) and overload (503) errors.
- **Offline test suite:** the Gemini client is mocked, so tests need no API key or network.

## Architecture

```
                         User message (+ optional profile)
                                      │
                                      ▼
                              ┌──────────────┐
                              │ RouterAgent  │  classifies into one word
                              └──────┬───────┘
     ┌───────────┬───────────┬───────┴─────┬──────────────┬─────────────┐
     ▼           ▼           ▼             ▼              ▼             ▼
  workout    nutrition    recovery        both           plan        general
     │           │           │             │              │             │
WorkoutAgent NutritionAgent RecoveryAgent  └─► FullPackageAgent ◄─┘  GeneralAgent
                                                                      │       │
                                                                    chat   reroute
                                                                   (reply) (rewrite query
                                                                            → RouterAgent)
```

| Agent | Role |
|---|---|
| `RouterAgent` | Classifies the message as `workout`, `nutrition`, `recovery`, `both`, `plan` or `general`. Falls back to `general` on any unexpected output. |
| `WorkoutAgent` | Structured training plans (days, exercises, sets, reps), with BMI-aware adjustments. |
| `NutritionAgent` | Calorie, protein and water targets plus sample meals. |
| `RecoveryAgent` | Soreness, sleep, stretching and warning signs, with age- and goal-specific advice. |
| `FullPackageAgent` | One unified weekly plan covering workout, nutrition and recovery. Also handles `both` (workout + nutrition only). |
| `GeneralAgent` | Returns JSON: either `chat` (a friendly reply) or `reroute` (a rewritten fitness query). |
| `EmailAgent` | Sends plans via Gmail SMTP using an App Password. |

All LLM agents use `gemini-2.5-flash` and create their Gemini client lazily, so a missing key fails at first use rather than at import.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM | Google Gemini (`google-genai` SDK) |
| Language | Python 3.11 |
| Storage | Local `users.json` |
| Email | Gmail SMTP (`smtplib`) |
| Testing | pytest (mocked Gemini client) |

## Getting Started

### Prerequisites

- Python 3.11+
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)
- *(Optional)* A Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) for the email feature

### Installation

```bash
git clone https://github.com/varunk-2005/fitness-agent.git
cd fitness-agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GMAIL_USER=your_email@gmail.com          # optional, for email feature
GMAIL_APP_PASSWORD=your_16_char_app_pw   # optional, for email feature
```

On **Streamlit Community Cloud**, add the same keys under *App settings → Secrets*. The app checks Streamlit secrets first, then environment variables.

### Run

```bash
# Web app
streamlit run app.py

# Or the command-line version
python main.py
```

The web app opens at `http://localhost:8501`. The repo also includes a dev container config, so it runs in GitHub Codespaces with no local setup.

### Tests

```bash
pip install pytest
python -m pytest test_api.py -v
```

The tests replace each agent's Gemini client with a fake, so they run offline. They cover routing, the fallback to `general`, JSON parsing in the General agent (including bad JSON), memory reset, email failure without credentials, and end-to-end routing through `AgentRouter`.

## Project Structure

```
fitness-agent/
├── app.py                    # Streamlit UI: auth, profile sidebar, chat, email
├── main.py                   # AgentRouter orchestration + retry logic + CLI
├── agent/
│   ├── config.py             # Reads keys from Streamlit secrets or env vars
│   ├── router.py             # RouterAgent
│   ├── workout.py            # WorkoutAgent
│   ├── nutrition.py          # NutritionAgent
│   ├── recovery.py           # RecoveryAgent
│   ├── full_package_agent.py # FullPackageAgent
│   ├── general.py            # GeneralAgent (chat / reroute)
│   └── email_agent.py        # EmailAgent (Gmail SMTP)
├── test_api.py               # Offline pytest suite
├── requirements.txt
└── .devcontainer/            # Codespaces config
```

## Design Decisions

- **Router plus specialists instead of one big prompt.** Each agent has a short, focused system prompt and a fixed output format, which makes answers more consistent and easier to test.
- **Rewrite then re-route.** Vague follow-ups ("what about protein?") would be misclassified on their own. The General agent uses recent history to turn them into standalone questions before routing again.
- **Lazy client creation.** API keys are read at first use, so the app starts and the tests run without real credentials.
- **Exponential backoff** (3s, 6s, 12s, 24s) handles the Gemini free tier's rate limits without crashing the chat.

## Limitations & Future Improvements

- User accounts live in a local JSON file, which resets on Streamlit Cloud redeploys. Next step: a real database (Firebase / PostgreSQL).
- Agents call Gemini one after another. The full plan could run the three specialists in parallel and merge results.
- Add progress tracking (workout logs, weight over time) with charts.
- Stream responses token by token for faster perceived replies.
- This is not medical advice. Users with health conditions should consult a professional.

## Author

**Varun K** · [GitHub](https://github.com/varunk-2005)
