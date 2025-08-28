"""
Customer Support Agent Stages Implementation
"""
import logging
from typing import Dict, Any
from datetime import datetime

from .state import CustomerSupportState
from .mcp_client import create_mcp_client


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_stage_execution(state: CustomerSupportState, stage_name: str, details: Dict[str, Any]):
    """Log stage execution details"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "stage": stage_name,
        "details": details
    }
    state["execution_log"].append(log_entry)
    logger.info(f"Stage {stage_name}: {details}")


def log_mcp_call(state: CustomerSupportState, server_type: str, ability: str, result: Dict[str, Any]):
    """Log MCP client calls"""
    mcp_entry = {
        "timestamp": datetime.now().isoformat(),
        "server": server_type,
        "ability": ability,
        "result": result
    }
    state["mcp_calls"].append(mcp_entry)
    logger.info(f"MCP Call - {server_type}/{ability}: {result}")


# Stage 1: INTAKE
def intake_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Accept payload - Entry point for customer support workflow"""
    log_stage_execution(state, "INTAKE", {"action": "accept_payload"})
    
    state["current_stage"] = "INTAKE"
    state["stage_history"].append("INTAKE")
    
    # Initialize execution log and mcp_calls if not present
    if "execution_log" not in state:
        state["execution_log"] = []
    if "mcp_calls" not in state:
        state["mcp_calls"] = []
    if "errors" not in state:
        state["errors"] = []
    
    log_stage_execution(state, "INTAKE", {
        "customer": state["customer_name"],
        "ticket_id": state["ticket_id"],
        "priority": state["priority"]
    })
    
    return state


# Stage 2: UNDERSTAND (Deterministic)
def understand_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Parse request and extract entities"""
    state["current_stage"] = "UNDERSTAND"
    state["stage_history"].append("UNDERSTAND")
    
    # Create MCP clients
    common_client = create_mcp_client("COMMON")
    atlas_client = create_mcp_client("ATLAS")
    
    # Parse request text (COMMON)
    parse_result = common_client.call_ability("parse_request_text", state)
    log_mcp_call(state, "COMMON", "parse_request_text", parse_result)
    state["parsed_request"] = parse_result.get("parsed_request")
    
    # Extract entities (ATLAS)
    entities_result = atlas_client.call_ability("extract_entities", state)
    log_mcp_call(state, "ATLAS", "extract_entities", entities_result)
    state["extracted_entities"] = entities_result.get("extracted_entities")
    
    log_stage_execution(state, "UNDERSTAND", {
        "parsed_request": state["parsed_request"],
        "extracted_entities": state["extracted_entities"]
    })
    
    return state


# Stage 3: PREPARE (Deterministic)
def prepare_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Normalize fields, enrich records, add flags calculations"""
    state["current_stage"] = "PREPARE"
    state["stage_history"].append("PREPARE")
    
    # Create MCP clients
    common_client = create_mcp_client("COMMON")
    atlas_client = create_mcp_client("ATLAS")
    
    # Normalize fields (COMMON)
    normalize_result = common_client.call_ability("normalize_fields", state)
    log_mcp_call(state, "COMMON", "normalize_fields", normalize_result)
    state["normalized_fields"] = normalize_result.get("normalized_fields")
    
    # Enrich records (ATLAS)
    enrich_result = atlas_client.call_ability("enrich_records", state)
    log_mcp_call(state, "ATLAS", "enrich_records", enrich_result)
    state["enriched_records"] = enrich_result.get("enriched_records")
    
    # Add flags calculations (COMMON)
    flags_result = common_client.call_ability("add_flags_calculations", state)
    log_mcp_call(state, "COMMON", "add_flags_calculations", flags_result)
    state["flags_calculations"] = flags_result.get("flags_calculations")
    
    log_stage_execution(state, "PREPARE", {
        "normalized_fields": state["normalized_fields"],
        "enriched_records": state["enriched_records"],
        "flags_calculations": state["flags_calculations"]
    })
    
    return state


# Stage 4: ASK (Human)
def ask_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Request missing information from customer"""
    state["current_stage"] = "ASK"
    state["stage_history"].append("ASK")
    
    # Create ATLAS client
    atlas_client = create_mcp_client("ATLAS")
    
    # Generate clarification question (ATLAS)
    clarify_result = atlas_client.call_ability("clarify_question", state)
    log_mcp_call(state, "ATLAS", "clarify_question", clarify_result)
    state["clarification_question"] = clarify_result.get("clarification_question")
    
    log_stage_execution(state, "ASK", {
        "clarification_question": state["clarification_question"]
    })
    
    return state


# Stage 5: WAIT (Deterministic)
def wait_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Wait and capture customer response"""
    state["current_stage"] = "WAIT"
    state["stage_history"].append("WAIT")
    
    # Create ATLAS client
    atlas_client = create_mcp_client("ATLAS")
    
    # Extract answer (ATLAS) - simulated customer response
    answer_result = atlas_client.call_ability("extract_answer", state)
    log_mcp_call(state, "ATLAS", "extract_answer", answer_result)
    state["customer_answer"] = answer_result.get("customer_answer")
    
    log_stage_execution(state, "WAIT", {
        "customer_answer": state["customer_answer"]
    })
    
    return state


# Stage 6: RETRIEVE (Deterministic)
def retrieve_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Search knowledge base and store data"""
    state["current_stage"] = "RETRIEVE"
    state["stage_history"].append("RETRIEVE")
    
    # Create ATLAS client
    atlas_client = create_mcp_client("ATLAS")
    
    # Knowledge base search (ATLAS)
    kb_result = atlas_client.call_ability("knowledge_base_search", state)
    log_mcp_call(state, "ATLAS", "knowledge_base_search", kb_result)
    state["knowledge_base_results"] = kb_result.get("knowledge_base_results")
    
    log_stage_execution(state, "RETRIEVE", {
        "knowledge_base_results": state["knowledge_base_results"]
    })
    
    return state


# Stage 7: DECIDE (Non-deterministic)
def decide_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Score solutions and make escalation decision"""
    state["current_stage"] = "DECIDE"
    state["stage_history"].append("DECIDE")
    
    # Create MCP clients
    common_client = create_mcp_client("COMMON")
    atlas_client = create_mcp_client("ATLAS")
    
    # Solution evaluation (COMMON)
    eval_result = common_client.call_ability("solution_evaluation", state)
    log_mcp_call(state, "COMMON", "solution_evaluation", eval_result)
    state["solution_scores"] = eval_result.get("solution_scores")
    
    # Escalation decision (ATLAS) - Non-deterministic based on scores
    escalation_result = atlas_client.call_ability("escalation_decision", state)
    log_mcp_call(state, "ATLAS", "escalation_decision", escalation_result)
    state["escalation_decision"] = escalation_result.get("escalation_decision")
    state["escalation_reason"] = escalation_result.get("escalation_reason")
    
    log_stage_execution(state, "DECIDE", {
        "solution_scores": state["solution_scores"],
        "escalation_decision": state["escalation_decision"],
        "escalation_reason": state["escalation_reason"]
    })
    
    return state


# Stage 8: UPDATE (Deterministic)
def update_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Update and close ticket"""
    state["current_stage"] = "UPDATE"
    state["stage_history"].append("UPDATE")
    
    # Create ATLAS client
    atlas_client = create_mcp_client("ATLAS")
    
    # Update ticket (ATLAS)
    update_result = atlas_client.call_ability("update_ticket", state)
    log_mcp_call(state, "ATLAS", "update_ticket", update_result)
    state["ticket_updates"] = update_result.get("ticket_updates")
    
    # Close ticket (ATLAS) - only if not escalated
    if not state.get("escalation_decision", False):
        close_result = atlas_client.call_ability("close_ticket", state)
        log_mcp_call(state, "ATLAS", "close_ticket", close_result)
        state["ticket_status"] = close_result.get("ticket_status")
    
    log_stage_execution(state, "UPDATE", {
        "ticket_updates": state["ticket_updates"],
        "ticket_status": state.get("ticket_status")
    })
    
    return state


# Stage 9: CREATE (Deterministic)
def create_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Generate customer response"""
    state["current_stage"] = "CREATE"
    state["stage_history"].append("CREATE")
    
    # Create COMMON client
    common_client = create_mcp_client("COMMON")
    
    # Response generation (COMMON)
    response_result = common_client.call_ability("response_generation", state)
    log_mcp_call(state, "COMMON", "response_generation", response_result)
    state["generated_response"] = response_result.get("generated_response")
    
    log_stage_execution(state, "CREATE", {
        "generated_response": state["generated_response"]
    })
    
    return state


# Stage 10: DO
def do_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Execute API calls and trigger notifications"""
    state["current_stage"] = "DO"
    state["stage_history"].append("DO")
    
    # Create ATLAS client
    atlas_client = create_mcp_client("ATLAS")
    
    # Execute API calls (ATLAS)
    api_result = atlas_client.call_ability("execute_api_calls", state)
    log_mcp_call(state, "ATLAS", "execute_api_calls", api_result)
    state["api_calls_executed"] = api_result.get("api_calls_executed")
    
    # Trigger notifications (ATLAS)
    notify_result = atlas_client.call_ability("trigger_notifications", state)
    log_mcp_call(state, "ATLAS", "trigger_notifications", notify_result)
    state["notifications_sent"] = notify_result.get("notifications_sent")
    
    log_stage_execution(state, "DO", {
        "api_calls_executed": state["api_calls_executed"],
        "notifications_sent": state["notifications_sent"]
    })
    
    return state


# Stage 11: COMPLETE
def complete_stage(state: CustomerSupportState) -> CustomerSupportState:
    """Output final payload"""
    state["current_stage"] = "COMPLETE"
    state["stage_history"].append("COMPLETE")
    
    # Create final payload
    final_payload = {
        "ticket_id": state["ticket_id"],
        "customer_name": state["customer_name"],
        "email": state["email"],
        "original_query": state["query"],
        "priority": state["priority"],
        "resolution_status": state.get("ticket_status", "in_progress"),
        "escalated": state.get("escalation_decision", False),
        "escalation_reason": state.get("escalation_reason"),
        "generated_response": state.get("generated_response"),
        "stage_history": state["stage_history"],
        "processing_summary": {
            "parsed_request": state.get("parsed_request"),
            "extracted_entities": state.get("extracted_entities"),
            "knowledge_base_matches": len(state.get("knowledge_base_results", [])),
            "solution_scores": state.get("solution_scores"),
            "api_calls": len(state.get("api_calls_executed", [])),
            "notifications": len(state.get("notifications_sent", []))
        },
        "completed_at": datetime.now().isoformat()
    }
    
    state["final_payload"] = final_payload
    
    log_stage_execution(state, "COMPLETE", {
        "final_payload": final_payload
    })
    
    return state

