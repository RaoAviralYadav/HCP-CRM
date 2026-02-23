# 🏥 HCP-CRM — AI-First Healthcare Professional CRM

<div align="center">

![HCP CRM Banner](https://img.shields.io/badge/Life%20Sciences-CRM-2563eb?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyek0xMSA3aDJ2NmgtMlY3em0wIDhoMnYyaC0ydi0yeiIvPjwvc3ZnPg==)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-ReAct%20Agent-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph)
[![Groq](https://img.shields.io/badge/Groq-llama--3.3--70b-F54B3D?style=flat-square)](https://console.groq.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![Redux](https://img.shields.io/badge/Redux-Toolkit-764ABC?style=flat-square&logo=redux)](https://redux-toolkit.js.org)

**A conversational AI-driven CRM for Life Sciences field representatives. Describe your HCP interaction in plain English — the AI fills the form for you.**

</div>

---

## ✨ What Makes This Different

Most CRM tools force you to manually fill every field after a long day of meetings. This system flips that completely. Instead of typing into forms, you *talk* to an AI assistant — exactly like you'd describe the meeting to a colleague — and it automatically populates every field in real time.

Behind the scenes, a **LangGraph ReAct agent** orchestrates a set of specialized tools, uses an LLM to understand context and extract entities, and synchronises the result into a Redux-managed form — all without a single manual input from the user.

---

## 🎥 Demo

> **Left panel** — Interaction form (AI-controlled, not manually filled)  
> **Right panel** — AI assistant chat



| User types... | AI extracts & fills... |
|---|---|
| *"Met Dr. Patel today. Discussed OncoBoost Phase III trial. Sentiment was positive. Shared the efficacy brochure."* | HCP Name → Dr. Patel, Date → today, Topics → OncoBoost Phase III, Sentiment → Positive, Materials → Efficacy brochure |
| *"Sorry, the sentiment was actually negative and the name was Dr. John."* | Sentiment → Negative, HCP Name → Dr. John *(all other fields unchanged)* |

---

## 🧠 LangGraph Agent Architecture

The core of this application is a **ReAct (Reasoning + Acting) agent** built with LangGraph. The agent decides — based on the user's message — which tool to call, calls it, observes the result, and then decides what to do next. This loop continues until the task is complete.

```
User Message
     │
     ▼
┌──────────────────────────────┐
│     LangGraph ReAct Agent    │
│   (llama-3.3-70b via Groq)   │
│                              │
│  Thinks → Picks Tool → Acts  │
│      ↑                  │    │
│      └──── Observes ────┘    │
└──────────────┬───────────────┘
               │ Calls one of 5 tools
    ┌──────────┼──────────┼───────────┼───────────┐
    ▼          ▼          ▼           ▼           ▼
log_     edit_      get_hcp_   suggest_   summarize_
interaction interaction  details  followup  interaction
    │
    ▼
PostgreSQL DB → form_data → Redux Store → React UI
```

### The 5 Tools

**1. `log_interaction`** — The primary tool. When you describe a meeting, the LLM extracts structured fields (HCP name, date, sentiment, materials shared, topics discussed, outcomes) and persists them to the database. Returns the full record which populates the entire left-panel form in one shot.

**2. `edit_interaction`** — A surgical update tool. Accepts only the fields the user explicitly mentions changing and updates only those — every other field is left untouched. This is powered by the LLM's ability to identify *what changed* vs. what was merely mentioned.

**3. `get_hcp_details`** — Looks up a Healthcare Professional in the database by name (fuzzy match). Returns specialty, hospital, city, and contact info. Called automatically when the agent needs to verify or enrich HCP information before logging.

**4. `suggest_followup`** — Runs after logging an interaction and generates context-aware follow-up recommendations. The suggestions are influenced by the interaction's sentiment, topics discussed, and outcomes — a negative sentiment triggers escalation suggestions; mentions of samples trigger compliance reminders.

**5. `summarize_interaction`** — Condenses verbose interaction notes into a clean, structured professional summary suitable for reporting or sharing with a manager.

---

## 🏗️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Frontend** | React 18 + Vite | Fast dev experience, component-based UI |
| **State Management** | Redux Toolkit | Predictable global form state; AI updates flow through a single `setFormFromAI` action |
| **Backend** | Python + FastAPI | Async-ready, auto-generates OpenAPI docs |
| **AI Agent** | LangGraph (ReAct) | Stateful multi-step reasoning with tool use |
| **LLM** | Groq — `llama-3.3-70b-versatile` | Fast inference, strong entity extraction |
| **ORM** | SQLAlchemy 2.0 | Clean DB layer with type safety |
| **Database** | PostgreSQL 15 | Reliable relational store for interactions & HCPs |
| **Font** | Google Inter | Clean, legible, life-science appropriate |

---

## 📁 Project Structure

```
HCP-CRM/
│
├── backend/
│   ├── main.py            # FastAPI app + all REST routes
│   ├── agent.py           # LangGraph ReAct agent setup & runner
│   ├── tools.py           # All 5 LangGraph tools (core logic lives here)
│   ├── database.py        # SQLAlchemy models + DB init + seed data
│   ├── requirements.txt
│   └── .env               # Groq API key + DB URL (not committed)
│
└── frontend/
    ├── src/
    │   ├── App.jsx                        # Root with Redux Provider
    │   ├── index.css                      # All styles — Inter font, split layout
    │   ├── store/
    │   │   ├── index.js                   # Redux store config
    │   │   └── interactionSlice.js        # Form state + setFormFromAI action
    │   └── components/
    │       ├── InteractionForm.jsx        # Left panel — AI-controlled form
    │       └── AIAssistant.jsx            # Right panel — chat + API calls
    ├── index.html
    ├── package.json
    └── vite.config.js                     # Proxies /api → localhost:8000
```

---

## ⚡ Quick Start

**Prerequisites:** Python 3.10+, Node.js 18+, Docker

### 1. Database

```bash
docker run -d --name hcp-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=hcp_crm \
  -p 5432:5432 postgres:15
```

### 2. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt --only-binary=:all:
```

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hcp_crm
CORS_ORIGINS=http://localhost:5173
```

```bash
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the app is live.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Main agent endpoint — processes natural language |
| `GET` | `/api/interactions` | List all logged interactions |
| `GET` | `/api/interactions/{id}` | Get a single interaction |
| `PUT` | `/api/interactions/{id}` | Update an interaction |
| `DELETE` | `/api/interactions/{id}` | Delete an interaction |
| `GET` | `/api/hcps` | List all HCPs |
| `GET` | `/api/hcps/search?q=` | Search HCPs by name |
| `GET` | `/health` | Health check |

---

## 💡 Example Prompts to Try

```
"Today I met Dr. Smith and discussed Product X efficacy. 
Sentiment was positive. I shared the brochures and the Phase III data."
```

```
"Had a call with Dr. Patel. He was negative about the new drug pricing.
Distributed 5 samples of OncoBoost."
```

```
"Sorry, correct the name to Dr. Anika Sharma and change the sentiment to neutral."
```

```
"What do you know about Dr. Williams?"
```

```
"Summarize this interaction for my manager."
```

---

## 🔮 How the Form Gets Filled (The Full Data Flow)

Understanding this flow is key to seeing why LangGraph was the right choice here:

When you type a message, the frontend sends it along with the full conversation history to `POST /api/chat`. The FastAPI backend passes this to the LangGraph agent. The LLM reads the message, reasons about it, and decides to call `log_interaction` with structured parameters it extracted from your text. LangGraph executes the tool, which writes to PostgreSQL and returns a `form_data` object. The backend sends this back to the frontend inside the API response. The React app dispatches a Redux `setFormFromAI` action, which updates the global store. Every field in the `InteractionForm` component reads from this store — so they all update simultaneously, with no manual input.

The form is intentionally **read-only** from the user's perspective. The AI is the only thing that can fill it. This enforces the design principle that the assistant controls the form, not the human.

---

## 👤 Author

**Aviral Yadav**  
[GitHub](https://github.com/RaoAviralYadav) · [LinkedIn](https://www.linkedin.com/in/aviral-yadav-bb30a032a/)

---

<div align="center">
  <sub>Built as part of a Life Sciences AI-First CRM assignment · Uses LangGraph + Groq for real AI-driven form interaction</sub>
</div>