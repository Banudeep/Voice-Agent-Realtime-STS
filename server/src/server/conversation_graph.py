# server/src/server/conversation_graph.py
import os
from typing import Any, dict
from langgraph import Graph, Node  # assume these exist in your SDK
from langgraph.storage import SqlStorage  # example

# Initialize storage (SQL, could be sqlite or Postgres)
STORAGE_URL = os.getenv("GRAPH_DB_URL", "sqlite:///./graph.db")
storage = SqlStorage(STORAGE_URL)
graph = Graph(storage=storage)

def init_session_graph(session_id: str) -> None:
    """Create basic nodes for a new session if missing."""
    if not graph.has_node(session_id):
        root = graph.create_node(session_id, {"type": "session", "status": "active"})
        graph.create_node(f"{session_id}:intent", {"intent": None, "confidence": 0.0}, parent=root)
        graph.create_node(f"{session_id}:search_results", {"offers": []}, parent=root)
        graph.create_node(f"{session_id}:selection", {"offer_id": None}, parent=root)
        graph.create_node(f"{session_id}:hold", {"hold_id": None, "status": "none"}, parent=root)
        graph.commit()

def get_state(session_id: str) -> dict:
    # read nodes and return dict
    state = {}
    state["intent"] = graph.get_node_data(f"{session_id}:intent")
    state["search_results"] = graph.get_node_data(f"{session_id}:search_results")
    state["selection"] = graph.get_node_data(f"{session_id}:selection")
    state["hold"] = graph.get_node_data(f"{session_id}:hold")
    return state

async def evaluate_user_text(session_id: str, text: str) -> dict:
    """
    Example evaluation:
      - run a small NLU (LLM prompt or rule) to detect intent
      - update graph nodes
      - return 'action' dict describing next step (e.g., {'action': 'search', 'params': {...}})
    """
    init_session_graph(session_id)
    # naive: call an LLM or use a simple rule
    # TODO: use LangGraph prompt nodes or an LLM wrapper
    # For now, do a quick heuristic or forward to your existing LLM for intent classification.
    intent = await call_nlu_llm(text)  # implement or call your LLM
    graph.set_node_data(f"{session_id}:intent", {"intent": intent["label"], "confidence": intent["score"]})
    graph.commit()
    # Decide next action
    if intent["label"] == "search_flights":
        params = extract_search_params(text)
        return {"action": "search", "params": params}
    return {"action": "none"}