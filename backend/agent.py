import re
import json
import time
import uuid
import random
from typing import Dict, Any, List
from mcp_client import file_ticket
from rag import retrieve_similar_tickets
from llm import generate_completion

MAX_ITERATIONS = 5

VALID_TOOLS = {
    "retrieve_similar_tickets_tool",
    "route_category_tool",
    "generate_department_response_tool"
}

def execute_agent_tool(tool_name: str, tool_input: Dict[str, Any], text: str) -> str:
    if tool_name == "retrieve_similar_tickets_tool":
        query_text = tool_input.get("text", text) if isinstance(tool_input, dict) else text
        tickets = retrieve_similar_tickets(query_text, top_k=3)
        return json.dumps(tickets)
    elif tool_name == "route_category_tool":
        prompt = f"""Classify this support ticket text into exactly one category: Billing, Delivery, Technical, Account, Product Quality.
Ticket text: "{text}"
Explain your reasoning (Chain-of-Thought) briefly, then output the final JSON:
{{"category": "<Category>", "confidence": 0.95}}"""
        res = generate_completion("You are a Support Router.", prompt, temperature=0.2)
        return res
    elif tool_name == "generate_department_response_tool":
        category = tool_input.get("category", "General") if isinstance(tool_input, dict) else "General"
        similar_ids = tool_input.get("similar_ticket_ids", []) if isinstance(tool_input, dict) else []
        prompt = f"""Draft a professional customer support response for this {category} ticket:
"{text}"
Reference resolved ticket IDs: {similar_ids}"""
        res = generate_completion(f"You are a {category} Support Specialist.", prompt, temperature=0.7)
        return res
    else:
        return f"Error: Tool '{tool_name}' not recognized."

def run_react_agent(text: str, channel: str = "text") -> Dict[str, Any]:
    start_time = time.time()
    ticket_id = f"TKT-{random.randint(100, 999)}"
    trace: List[Dict[str, Any]] = []
    tool_calls: List[Dict[str, Any]] = []
    
    messages = [
        {
            "role": "system",
            "content": """You are a Customer Support Triage Coordinator.
You run a ReAct loop (Thought -> Action -> Observation).
Available tools:
1. retrieve_similar_tickets_tool: Search vector database for similar resolved tickets. Input: {"text": "..."}
2. route_category_tool: Classify category (Billing, Delivery, Technical, Account, Product Quality). Input: {"text": "..."}
3. generate_department_response_tool: Draft reply via specialist. Input: {"category": "...", "similar_ticket_ids": [...]}

Format to call a tool:
Thought: <reasoning>
Action: <tool_name>
Action Input: {"key": "value"}"""
        },
        {"role": "user", "content": f"Triage ticket: '{text}'"}
    ]

    category = "General"
    confidence = 0.92
    suggested_response = ""
    similar_ids: List[str] = []
    executed_tools = set()

    for iter_idx in range(1, MAX_ITERATIONS + 1):
        # Stop loop early if all key triage results are gathered
        if suggested_response and category != "General" and len(executed_tools) >= 3:
            break

        prompt_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in messages])
        llm_out = generate_completion("You are a ReAct agent.", prompt_str, temperature=0.2)
        messages.append({"role": "assistant", "content": llm_out})

        action_match = re.search(r"Action:\s*([a-zA-Z0-9_]+)", llm_out, re.IGNORECASE)
        action_name = action_match.group(1).strip() if action_match else ""

        action_input = {}
        input_match = re.search(r"Action Input:\s*({.*?})", llm_out, re.DOTALL | re.IGNORECASE)
        if input_match:
            try:
                action_input = json.loads(input_match.group(1).strip())
            except Exception:
                pass

        if action_name in VALID_TOOLS and action_name not in executed_tools:
            tool_call_id = f"call-{uuid.uuid4().hex[:6]}"
            t_start = time.time()
            observation = execute_agent_tool(action_name, action_input, text)
            t_elapsed = int((time.time() - t_start) * 1000)
            executed_tools.add(action_name)

            if action_name == "retrieve_similar_tickets_tool":
                try:
                    sim_list = json.loads(observation)
                    similar_ids = [t["id"] for t in sim_list if "id" in t]
                except Exception:
                    pass
            elif action_name == "route_category_tool":
                try:
                    if "{" in observation and "}" in observation:
                        j_str = observation[observation.index("{"):observation.rindex("}")+1]
                        parsed = json.loads(j_str)
                        category = parsed.get("category", category)
                        confidence = float(parsed.get("confidence", confidence))
                except Exception:
                    pass
            elif action_name == "generate_department_response_tool":
                suggested_response = observation

            trace.append({
                "id": tool_call_id,
                "name": action_name.replace("_", " ").upper(),
                "status": "complete",
                "detail": f"[{tool_call_id}] Executed in {t_elapsed}ms. Input: {json.dumps(action_input)}. Obs: {observation[:100]}..."
            })
            tool_calls.append({"toolId": tool_call_id, "toolName": action_name})
            messages.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            # Deterministic execution fallback if LLM output finished without a new valid tool call
            if "retrieve_similar_tickets_tool" not in executed_tools:
                sim_res = execute_agent_tool("retrieve_similar_tickets_tool", {}, text)
                executed_tools.add("retrieve_similar_tickets_tool")
                try:
                    sim_list = json.loads(sim_res)
                    similar_ids = [t["id"] for t in sim_list if "id" in t]
                except Exception:
                    pass
                t_id = f"call-{uuid.uuid4().hex[:6]}"
                trace.append({"id": t_id, "name": "RETRIEVE SIMILAR TICKETS TOOL", "status": "complete", "detail": f"[{t_id}] Retrieved context tickets: {similar_ids}"})
                tool_calls.append({"toolId": t_id, "toolName": "retrieve_similar_tickets_tool"})

            if "route_category_tool" not in executed_tools:
                route_res = execute_agent_tool("route_category_tool", {}, text)
                executed_tools.add("route_category_tool")
                try:
                    if "{" in route_res and "}" in route_res:
                        parsed = json.loads(route_res[route_res.index("{"):route_res.rindex("}")+1])
                        category = parsed.get("category", category)
                        confidence = float(parsed.get("confidence", confidence))
                except Exception:
                    pass
                t_id = f"call-{uuid.uuid4().hex[:6]}"
                trace.append({"id": t_id, "name": "ROUTE CATEGORY TOOL", "status": "complete", "detail": f"[{t_id}] Categorized as '{category}'"})
                tool_calls.append({"toolId": t_id, "toolName": "route_category_tool"})

            if "generate_department_response_tool" not in executed_tools or not suggested_response:
                suggested_response = execute_agent_tool("generate_department_response_tool", {"category": category, "similar_ticket_ids": similar_ids}, text)
                executed_tools.add("generate_department_response_tool")
                t_id = f"call-{uuid.uuid4().hex[:6]}"
                trace.append({"id": t_id, "name": "GENERATE DEPARTMENT RESPONSE TOOL", "status": "complete", "detail": f"[{t_id}] Drafted specialist response for {category}"})
                tool_calls.append({"toolId": t_id, "toolName": "generate_department_response_tool"})
            
            # Clean exit after fallback
            break

    elapsed_ms = int((time.time() - start_time) * 1000)

    return {
        "ticket_id": ticket_id,
        "ticketId": ticket_id,
        "channel": channel,
        "originalText": text,
        "category": category,
        "suggestedResponse": suggested_response,
        "confidence": confidence,
        "similarTicketIds": similar_ids,
        "timingMs": elapsed_ms,
        "agentTrace": trace,
        "toolCalls": tool_calls
    }

def file_ticket_with_mcp(record: Dict[str, Any]) -> Dict[str, Any]:
    return file_ticket(record)
