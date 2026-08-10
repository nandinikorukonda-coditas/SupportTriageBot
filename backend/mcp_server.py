import os
import json
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SupportTriageStore")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "tickets_store.json")

def load_filed_tickets():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_filed_tickets(tickets):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)

@mcp.tool()
def file_ticket_tool(
    ticket_id: str,
    category: str,
    suggested_response: str,
    original_text: str = "",
    agent_comment: str = "",
    confidence: float = 0.95,
    similar_ticket_ids: list = None,
    channel: str = "text"
) -> str:
    """Files a ticket record into the backend store via MCP protocol."""
    filed_list = load_filed_tickets()
    file_id = f"FILE-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    record = {
        "fileId": file_id,
        "ticketId": ticket_id or f"TKT-{len(filed_list) + 100:03d}",
        "category": category,
        "confidence": confidence,
        "suggestedResponse": suggested_response,
        "similarTicketIds": similar_ticket_ids or [],
        "channel": channel,
        "originalText": original_text,
        "agentComment": agent_comment or "Filed via support triage workflow.",
        "filedAt": datetime.now(timezone.utc).isoformat()
    }
    filed_list.insert(0, record)
    save_filed_tickets(filed_list)
    return json.dumps({"ok": True, "file_id": file_id, "ticket_id": record["ticketId"], "record": record})

if __name__ == "__main__":
    mcp.run()
