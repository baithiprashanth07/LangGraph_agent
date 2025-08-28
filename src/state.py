"""
LangGraph State Definition for Customer Support Agent
"""
from typing import Dict, Any, List, Optional
from typing_extensions import TypedDict


class CustomerSupportState(TypedDict):
    """State schema for the customer support workflow"""
    
    # Input payload
    customer_name: str
    email: str
    query: str
    priority: str
    ticket_id: str
    
    # Processing state
    current_stage: str
    stage_history: List[str]
    
    # Extracted and processed data
    parsed_request: Optional[Dict[str, Any]]
    extracted_entities: Optional[Dict[str, Any]]
    normalized_fields: Optional[Dict[str, Any]]
    enriched_records: Optional[Dict[str, Any]]
    flags_calculations: Optional[Dict[str, Any]]
    
    # Human interaction
    clarification_question: Optional[str]
    customer_answer: Optional[str]
    
    # Knowledge retrieval
    knowledge_base_results: Optional[List[Dict[str, Any]]]
    
    # Decision making
    solution_scores: Optional[List[Dict[str, Any]]]
    escalation_decision: Optional[bool]
    escalation_reason: Optional[str]
    
    # Ticket updates
    ticket_status: Optional[str]
    ticket_updates: Optional[Dict[str, Any]]
    
    # Response generation
    generated_response: Optional[str]
    
    # Actions
    api_calls_executed: Optional[List[Dict[str, Any]]]
    notifications_sent: Optional[List[Dict[str, Any]]]
    
    # Final output
    final_payload: Optional[Dict[str, Any]]
    
    # Logging and metadata
    execution_log: List[Dict[str, Any]]
    mcp_calls: List[Dict[str, Any]]
    errors: List[str]

