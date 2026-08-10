import numpy as np
from typing import List, Dict, Any
from embeddings import get_embedding

class VectorStore:
    def __init__(self):
        self.tickets: List[Dict[str, Any]] = []
        self.embeddings: List[np.ndarray] = []

    def clear(self):
        self.tickets = []
        self.embeddings = []

    def add_ticket(self, ticket: Dict[str, Any]):
        text = ticket.get("text", "")
        emb = get_embedding(text)
        self.tickets.append(ticket)
        self.embeddings.append(emb)

    def add_tickets(self, tickets: List[Dict[str, Any]]):
        for ticket in tickets:
            self.add_ticket(ticket)

    def search(self, query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.embeddings:
            return []
        
        query_emb = get_embedding(query_text)
        scores = []
        for idx, emb in enumerate(self.embeddings):
            dot = np.dot(query_emb, emb)
            norm_q = np.linalg.norm(query_emb)
            norm_e = np.linalg.norm(emb)
            similarity = float(dot / (norm_q * norm_e)) if norm_q > 0 and norm_e > 0 else 0.0
            scores.append((similarity, self.tickets[idx]))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]

vector_store = VectorStore()
