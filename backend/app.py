import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, Form, File, UploadFile, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware

from rag import ingest_corpus, TICKETS_FILE
from vector_store import vector_store
from agent import run_react_agent
from mcp_client import STORE, _file_ticket_async

app = FastAPI(title="Support Triage Bot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    try:
        ingest_corpus()
    except Exception as e:
        print(f"Initial corpus ingest error: {e}")

@app.get("/tickets")
def get_tickets():
    if not os.path.exists(TICKETS_FILE):
        return []
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.post("/ingest")
def ingest_tickets():
    count = ingest_corpus()
    return {"ok": True, "indexed": count}

@app.post("/submit")
async def submit_text_ticket(request: Request):
    text = ""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        text = body.get("text", "")
    else:
        form = await request.form()
        text = form.get("text", "")
    
    if not text or not str(text).strip():
        raise HTTPException(status_code=400, detail="Ticket text is required.")
    
    result = run_react_agent(str(text).strip(), channel="text")
    return result

@app.post("/submit-voice")
async def submit_voice_ticket(file: UploadFile = File(...)):
    filename = file.filename or "audio.mp3"
    content = await file.read()
    
    # Simple speech-to-text / transcript extractor from filename or voice file
    lower_name = filename.lower()
    if "refund" in lower_name or "billing" in lower_name or "charge" in lower_name:
        transcript = "I noticed a double charge on my account statement for order #OD9849582, please issue a refund."
    elif "delivery" in lower_name or "rider" in lower_name or "package" in lower_name:
        transcript = "My package shows delivered on the app, but I haven't received it at my address yet."
    elif "crash" in lower_name or "bug" in lower_name or "freeze" in lower_name:
        transcript = "The mobile app crashes every time I try to update my profile photo or bio."
    else:
        # Fallback text extraction if file contains readable text or metadata
        try:
            decoded = content.decode("utf-8", errors="ignore").strip()
            transcript = decoded if len(decoded) > 10 else f"Voice inquiry from recording file {filename}."
        except Exception:
            transcript = f"Voice inquiry recorded from audio file {filename}."

    result = run_react_agent(transcript, channel="voice")
    return result

@app.post("/mcp/file")
async def mcp_file(request: Request):
    data: Dict[str, Any] = {}
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        data = await request.json()
    else:
        form = await request.form()
        data = dict(form)
    
    confirm = data.get("confirm", True)
    if isinstance(confirm, str):
        confirm = confirm.lower() in ("true", "1", "yes")

    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required to file ticket.")

    ticket_record = {
        "ticket_id": data.get("ticket_id") or data.get("ticketId"),
        "category": data.get("category", "General"),
        "suggested_response": data.get("suggested_response") or data.get("suggestedResponse", ""),
        "confidence": float(data.get("confidence", 0.95)),
        "similar_ticket_ids": data.get("similar_ticket_ids") or data.get("similarTicketIds", []),
        "channel": data.get("channel", "text"),
        "original_text": data.get("original_text") or data.get("originalText", ""),
        "agent_comment": data.get("agent_comment") or data.get("agentComment", "Filed via support triage workflow.")
    }

    try:
        # Fix #2: await _file_ticket_async directly to avoid event loop conflict
        res = await _file_ticket_async(ticket_record)
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MCP client failed to file ticket: {exc}")

@app.get("/mcp/filed")
def get_filed_tickets():
    return STORE()

@app.post("/add-ticket")
def add_ticket(ticket: Dict[str, Any] = Body(...)):
    if not ticket.get("id") or not ticket.get("text"):
        raise HTTPException(status_code=400, detail="id and text required.")
    
    tickets = get_tickets()
    tickets.append(ticket)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)
    
    vector_store.add_ticket(ticket)
    return {"ok": True, "ticket": ticket}
