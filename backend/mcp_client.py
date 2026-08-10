import os
import sys
import json
import asyncio
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "tickets_store.json")
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")

def STORE():
    """Returns all filed tickets from tickets_store.json."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []

async def _file_ticket_async(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Connects to mcp_server.py via stdio MCP client and executes file_ticket_tool.
    """
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=os.environ.copy()
    )

    ticket_id = record.get("ticket_id") or record.get("ticketId") or f"TKT-{int(asyncio.get_event_loop().time() * 1000) % 900 + 100}"
    category = record.get("category", "General")
    suggested_response = record.get("suggested_response") or record.get("suggestedResponse", "")
    original_text = record.get("original_text") or record.get("originalText", "")
    agent_comment = record.get("agent_comment") or record.get("agentComment") or "Filed via support triage workflow."

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                mcp_res = await session.call_tool(
                    "file_ticket_tool",
                    arguments={
                        "ticket_id": ticket_id,
                        "category": category,
                        "suggested_response": suggested_response,
                        "original_text": original_text,
                        "agent_comment": agent_comment,
                        "confidence": float(record.get("confidence", 0.95)),
                        "similar_ticket_ids": record.get("similar_ticket_ids") or record.get("similarTicketIds", []),
                        "channel": record.get("channel", "text")
                    }
                )
                if mcp_res and mcp_res.content:
                    text_out = mcp_res.content[0].text
                    return json.loads(text_out)
    except Exception as exc:
        print(f"Warning: MCP stdio server invocation failed ({exc}), calling tool fallback directly.")
        from mcp_server import file_ticket_tool
        raw = file_ticket_tool(
            ticket_id=ticket_id,
            category=category,
            suggested_response=suggested_response,
            original_text=original_text,
            agent_comment=agent_comment,
            confidence=float(record.get("confidence", 0.95)),
            similar_ticket_ids=record.get("similar_ticket_ids") or record.get("similarTicketIds", []),
            channel=record.get("channel", "text")
        )
        return json.loads(raw)

    return {"ok": False, "error": "MCP execution did not return content"}

def file_ticket(record: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for non-async usage."""
    return asyncio.run(_file_ticket_async(record))
