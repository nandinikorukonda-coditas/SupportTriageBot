# SupportTriageBot — Autonomous RAG & MCP Multi-Agent Triage Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Angular](https://img.shields.io/badge/Angular-20.0-DD0031?style=flat-square&logo=angular)](https://angular.dev/)
[![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-6c5ce7?style=flat-square)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python)](https://www.python.org/)

**SupportTriageBot** is an intelligent, end-to-end support ticket classification, retrieval, and filing platform. It combines a **ReAct Agent Loop**, a **Dense Vector RAG Pipeline** (`sentence-transformers`), and **Model Context Protocol (MCP)** tool execution via FastMCP to automatically categorize incoming support requests, retrieve contextually similar historical tickets, draft specialist customer responses, and file validated records to a persistent store.



## 🏗️ Directory Structure

```text
SupportTriageBot/
├── .gitignore                      # Master Git ignore rules
├── README.md                       # Master documentation Note
├── sample-audio/                   # Playable spoken MP3 audio samples (.mp3)
│   ├── app_crash_bug.mp3
│   ├── billing_refund_issue.mp3
│   └── delivery_delay_rider.mp3
├── backend/                        # FastAPI Backend Application
│   ├── .env.example                # Template configuration (DO NOT commit real .env)
│   ├── requirements.txt            # Python dependencies
│   ├── app.py                      # FastAPI routes (/submit, /submit-voice, /mcp/file)
│   ├── agent.py                    # ReAct agent loop (Thought/Action/Observation)
│   ├── llm.py                      # OpenRouter client wrapper (OpenAI client)
│   ├── embeddings.py               # Sentence-Transformers vector encoder (384d)
│   ├── vector_store.py             # In-memory Cosine Similarity vector index
│   ├── rag.py                      # Ingestion & Top-K retrieval functions
│   ├── mcp_server.py               # FastMCP server exposing file_ticket_tool
│   ├── mcp_client.py               # MCP Stdio ClientSession connector
│   ├── tickets.json                # Seed historical corpus (18 resolved tickets)
│   └── data/
│       └── tickets_store.json      # Persistent JSON store for filed MCP tickets
└── frontend/
    └── support-frontend/           # Angular 20 SPA Frontend
        ├── src/
        │   ├── styles.css          # Glassmorphism dark-mode UI design system
        │   ├── assets/sample-audio/# Playable sample audio assets
        │   └── app/
        │       ├── models.ts       # TypeScript interfaces (TriageResult, Ticket)
        │       ├── app.component.ts
        │       ├── services/triage.service.ts
        │       └── components/     # new-ticket, corpus, ticket-details, dashboard
```

---

---

## 🔄 Simple Step-by-Step System Flow (How It Works)

```text
[ User Input (Text / Audio .mp3) ]
              │
              ▼
   1. Voice Channel Ingestion (Python / FastAPI)
   • Audio filename is pattern-matched to a representative sample transcript.
   • Real STT (e.g. Whisper) would replace this in a production version.
              │
              ▼
   2. Local Vector RAG Search (Python)
      • Python converts the text to a 384d vector (all-MiniLM-L6-v2).
      • Python computes Cosine Similarity math against historical tickets (tickets.json).
      • Python retrieves the Top-3 matching ticket IDs (Top-K = 3).
              │
              ▼
   3. ReAct Agent Reasoning & LLM Calls (OpenRouter / Gemini 2.5 Flash)
      • ReAct Coordinator runs a Thought -> Action -> Observation loop.
      • Category Router classifies the department (Billing, Delivery, Technical, Account, Product Quality).
      • Department Specialist drafts a response citing the Top-3 RAG tickets.
              │
              ▼
   4. UI Screen Display (Angular 20 UI)
      • Shows Category Badge, Confidence %, Timing Latency, RAG Match Badges, & Agent Trace Timeline.
              │
              ▼
   5. MCP Protocol Ticket Filing (FastMCP & Stdio Client)
      • When "File Ticket" is clicked, mcp_client.py calls mcp_server.py via stdio JSON-RPC.
      • Appends the filed record to backend/data/tickets_store.json.
```

---


## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1. Start FastAPI Backend
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```
- Server URL: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`

### 2. Start Angular Frontend
```powershell
cd frontend/support-frontend
npm install
npm start
```
- UI Web App: `http://localhost:4200`

---

---
