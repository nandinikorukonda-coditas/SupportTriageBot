import json
import os
from typing import List, Dict, Any
from vector_store import vector_store

TICKETS_FILE = os.path.join(os.path.dirname(__file__), "tickets.json")

def ingest_corpus() -> int:
    """Ingest tickets.json into vector store."""
    if not os.path.exists(TICKETS_FILE):
        return 0
    
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        tickets = json.load(f)

    vector_store.clear()
    vector_store.add_tickets(tickets)
    return len(tickets)

def retrieve_similar_tickets(text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve top_k similar tickets from vector store."""
    # Ensure vector store is populated
    if not vector_store.tickets:
        ingest_corpus()
    return vector_store.search(text, top_k=top_k)
