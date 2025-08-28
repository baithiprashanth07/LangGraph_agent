"""
LangGraph Customer Support Agent Implementation
"""
import json
import logging
from typing import Dict, Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import CustomerSupportState
from .stages import (
    intake_stage, understand_stage, prepare_stage, ask_stage, wait_stage,
    retrieve_stage, decide_stage, update_stage, create_stage, do_stage, complete_stage
)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CustomerSupportAgent:
    """LangGraph-based Customer Support Agent"""
    
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(CustomerSupportState)
        
        # Add nodes for each stage
        workflow.add_node("intake", intake_stage)
        workflow.add_node("understand", understand_stage)
        workflow.add_node("prepare", prepare_stage)
        workflow.add_node("ask", ask_stage)
        workflow.add_node("wait", wait_stage)
        workflow.add_node("retrieve", retrieve_stage)
        workflow.add_node("decide", decide_stage)
        workflow.add_node("update", update_stage)
        workflow.add_node("create", create_stage)
        workflow.add_node("do", do_stage)
        workflow.add_node("complete", complete_stage)
        
        # Set entry point
        workflow.set_entry_point("intake")
        
        # Add deterministic edges (sequential flow)
        workflow.add_edge("intake", "understand")
        workflow.add_edge("understand", "prepare")
        workflow.add_edge("prepare", "ask")
        workflow.add_edge("ask", "wait")
        workflow.add_edge("wait", "retrieve")
        workflow.add_edge("retrieve", "decide")
        
        # Add conditional edge for decision stage (non-deterministic)
        workflow.add_conditional_edges(
            "decide",
            self._should_escalate,
            {
                "escalate": "complete",  # Skip to completion if escalated
                "continue": "update"     # Continue normal flow
            }
        )
        
        # Continue deterministic flow after decision
        workflow.add_edge("update", "create")
        workflow.add_edge("create", "do")
        workflow.add_edge("do", "complete")
        
        # End at complete stage
        workflow.add_edge("complete", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _should_escalate(self, state: CustomerSupportState) -> str:
        """Conditional logic for escalation decision"""
        escalation_decision = state.get("escalation_decision", False)
        
        if escalation_decision:
            logger.info("Escalating to human agent - skipping automated resolution")
            return "escalate"
        else:
            logger.info("Continuing with automated resolution")
            return "continue"
    
    def run(self, input_payload: Dict[str, Any], thread_id: str = "default") -> Dict[str, Any]:
        """Run the customer support workflow"""
        
        logger.info(f"Starting customer support workflow for ticket: {input_payload.get('ticket_id')}")
        
        # Initialize state with input payload
        initial_state = CustomerSupportState(
            customer_name=input_payload["customer_name"],
            email=input_payload["email"],
            query=input_payload["query"],
            priority=input_payload["priority"],
            ticket_id=input_payload["ticket_id"],
            current_stage="",
            stage_history=[],
            parsed_request=None,
            extracted_entities=None,
            normalized_fields=None,
            enriched_records=None,
            flags_calculations=None,
            clarification_question=None,
            customer_answer=None,
            knowledge_base_results=None,
            solution_scores=None,
            escalation_decision=None,
            escalation_reason=None,
            ticket_status=None,
            ticket_updates=None,
            generated_response=None,
            api_calls_executed=None,
            notifications_sent=None,
            final_payload=None,
            execution_log=[],
            mcp_calls=[],
            errors=[]
        )
        
        # Configure thread for state persistence
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Run the workflow
            result = self.graph.invoke(initial_state, config)
            
            logger.info(f"Workflow completed for ticket: {input_payload.get('ticket_id')}")
            
            return {
                "success": True,
                "final_payload": result.get("final_payload"),
                "execution_log": result.get("execution_log", []),
                "mcp_calls": result.get("mcp_calls", []),
                "stage_history": result.get("stage_history", []),
                "errors": result.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Workflow failed for ticket {input_payload.get('ticket_id')}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "final_payload": None,
                "execution_log": [],
                "mcp_calls": [],
                "stage_history": [],
                "errors": [str(e)]
            }
    
    def get_workflow_visualization(self) -> str:
        """Get a text representation of the workflow"""
        return """
Customer Support Agent Workflow:

INTAKE → UNDERSTAND → PREPARE → ASK → WAIT → RETRIEVE → DECIDE
                                                           ↓
                                                      [Escalate?]
                                                     ↙         ↘
                                               COMPLETE    UPDATE → CREATE → DO → COMPLETE

Stages:
1. INTAKE: Accept customer payload
2. UNDERSTAND: Parse request and extract entities (Deterministic)
3. PREPARE: Normalize, enrich, and calculate flags (Deterministic)
4. ASK: Generate clarification questions (Human interaction)
5. WAIT: Capture customer responses (Deterministic)
6. RETRIEVE: Search knowledge base (Deterministic)
7. DECIDE: Evaluate solutions and escalation (Non-deterministic)
8. UPDATE: Update and close tickets (Deterministic)
9. CREATE: Generate customer response (Deterministic)
10. DO: Execute API calls and notifications
11. COMPLETE: Output final payload

MCP Server Mapping:
- COMMON: Internal abilities (parsing, normalization, scoring, response generation)
- ATLAS: External system interactions (entity extraction, enrichment, KB search, notifications)
"""


def create_agent() -> CustomerSupportAgent:
    """Factory function to create a customer support agent"""
    return CustomerSupportAgent()

