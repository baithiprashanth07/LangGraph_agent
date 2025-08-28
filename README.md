# LangGraph Customer Support Agent

A sophisticated customer support workflow automation system built with LangGraph, featuring 11-stage processing pipeline with deterministic and non-deterministic execution modes, state persistence, and MCP (Model Context Protocol) client integration.

## Overview

This project implements **Langie**, a structured and logical LangGraph Agent that models customer support workflows as graph-based stages. The agent demonstrates advanced capabilities in workflow orchestration, state management, and external system integration through mock MCP servers.

### Key Features

- **11-Stage Workflow Pipeline**: Complete customer support flow from intake to completion
- **Deterministic & Non-Deterministic Execution**: Sequential processing with dynamic decision-making
- **State Persistence**: Comprehensive state management across all workflow stages
- **MCP Client Integration**: Dual-server architecture (Atlas & Common) for ability execution
- **Comprehensive Logging**: Detailed execution tracking and audit trails
- **Escalation Logic**: Intelligent decision-making for human handoff scenarios

## Architecture

### Workflow Stages

The agent processes customer support requests through 11 distinct stages:

1. **INTAKE** 📥 - Accept and validate incoming customer payload
2. **UNDERSTAND** 🧠 - Parse request text and extract entities (Deterministic)
3. **PREPARE** 🛠️ - Normalize fields, enrich records, add calculations (Deterministic)
4. **ASK** ❓ - Generate clarification questions (Human interaction)
5. **WAIT** ⏳ - Capture and process customer responses (Deterministic)
6. **RETRIEVE** 📚 - Search knowledge base and store relevant data (Deterministic)
7. **DECIDE** ⚖️ - Evaluate solutions and make escalation decisions (Non-deterministic)
8. **UPDATE** 🔄 - Update ticket status and close if resolved (Deterministic)
9. **CREATE** ✍️ - Generate customer response content (Deterministic)
10. **DO** 🏃 - Execute API calls and trigger notifications
11. **COMPLETE** ✅ - Output final structured payload

### MCP Server Architecture

The system utilizes two specialized MCP servers:

- **COMMON Server**: Handles internal abilities requiring no external data
  - Text parsing, field normalization, solution scoring, response generation
- **ATLAS Server**: Manages external system interactions
  - Entity extraction, record enrichment, knowledge base search, notifications

## Installation

### Prerequisites

- Python 3.11+
- pip package manager

### Setup

1. Clone or download the project:
```bash
git clone <repository-url>
cd langgraph_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python3 demo.py
```

## Usage

### Basic Usage

```python
from src.agent import create_agent

# Create agent instance
agent = create_agent()

# Define customer input
customer_input = {
    "customer_name": "John Smith",
    "email": "john.smith@example.com", 
    "query": "I can't log into my account",
    "priority": "high",
    "ticket_id": "TICKET-2024-001"
}

# Run workflow
result = agent.run(customer_input)

# Access results
if result["success"]:
    print("Final Payload:", result["final_payload"])
    print("Stage History:", result["stage_history"])
    print("MCP Calls:", result["mcp_calls"])
```

### Demo Script

Run the included demo to see the complete workflow in action:

```bash
python3 demo.py
```

### Testing

Execute the test suite to validate functionality:

```bash
python3 tests/test_agent.py
```

## Configuration

The agent configuration is defined in `config/agent_config.yaml`, which includes:

- Input schema validation
- Stage definitions and execution modes
- MCP server ability mappings
- Agent personality traits

## Project Structure

```
langgraph_agent/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Main LangGraph agent implementation
│   ├── state.py             # State schema definition
│   ├── stages.py            # Individual stage implementations
│   └── mcp_client.py        # Mock MCP client implementation
├── config/
│   └── agent_config.yaml    # Agent configuration
├── tests/
│   └── test_agent.py        # Test cases
├── docs/
├── demo.py                  # Demonstration script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## State Management

The agent maintains comprehensive state throughout the workflow execution:

### Core State Fields

- **Input Data**: Customer name, email, query, priority, ticket ID
- **Processing State**: Current stage, stage history
- **Extracted Data**: Parsed requests, entities, normalized fields
- **Decision Data**: Solution scores, escalation decisions
- **Output Data**: Generated responses, API call results
- **Metadata**: Execution logs, MCP calls, error tracking

### State Persistence

State is automatically persisted across stages using LangGraph's built-in checkpointing mechanism with MemorySaver, ensuring data integrity throughout the workflow execution.

## MCP Integration

### Server Types

**COMMON Server Abilities:**
- `parse_request_text`: Convert unstructured text to structured data
- `normalize_fields`: Standardize dates, codes, and identifiers
- `add_flags_calculations`: Compute priority and SLA risk scores
- `solution_evaluation`: Score potential solutions (1-100 scale)
- `response_generation`: Generate customer-facing responses

**ATLAS Server Abilities:**
- `extract_entities`: Identify products, accounts, and dates
- `enrich_records`: Add SLA and historical information
- `clarify_question`: Generate clarification questions
- `extract_answer`: Process customer responses
- `knowledge_base_search`: Search FAQ and knowledge base
- `escalation_decision`: Determine human handoff requirements
- `update_ticket`: Modify ticket status and fields
- `close_ticket`: Mark issues as resolved
- `execute_api_calls`: Trigger external system actions
- `trigger_notifications`: Send customer notifications

### Mock Implementation

The current implementation includes comprehensive mock MCP clients that simulate real-world behavior patterns, providing realistic responses for demonstration and testing purposes.

## Workflow Execution

### Deterministic Stages

Most stages execute in a predetermined sequence, ensuring consistent processing:

- UNDERSTAND → PREPARE → ASK → WAIT → RETRIEVE → UPDATE → CREATE → DO

### Non-Deterministic Stage

The DECIDE stage implements dynamic logic based on solution confidence scores:

- **Score ≥ 90**: Continue with automated resolution
- **Score < 90**: Escalate to human agent and skip to completion

### Conditional Routing

The workflow includes intelligent routing logic that adapts based on processing results:

```python
def _should_escalate(self, state: CustomerSupportState) -> str:
    escalation_decision = state.get("escalation_decision", False)
    
    if escalation_decision:
        return "escalate"  # Skip to completion
    else:
        return "continue"  # Continue normal flow
```

## Logging and Monitoring

### Execution Logging

The system provides comprehensive logging at multiple levels:

- **Stage Execution**: Timestamps, stage names, processing details
- **MCP Calls**: Server type, ability name, request/response data
- **Error Tracking**: Exception handling and error accumulation

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "stage": "UNDERSTAND",
  "details": {
    "parsed_request": {...},
    "extracted_entities": {...}
  }
}
```

## Example Output

### Sample Input

```json
{
  "customer_name": "John Smith",
  "email": "john.smith@example.com",
  "query": "I can't log into my account. I keep getting a 'Login Failed' error message.",
  "priority": "high",
  "ticket_id": "TICKET-2024-001"
}
```

### Sample Final Payload

```json
{
  "ticket_id": "TICKET-2024-001",
  "customer_name": "John Smith",
  "email": "john.smith@example.com",
  "original_query": "I can't log into my account...",
  "priority": "high",
  "resolution_status": "closed",
  "escalated": false,
  "generated_response": "Dear Customer, Thank you for contacting...",
  "stage_history": ["INTAKE", "UNDERSTAND", "PREPARE", ...],
  "processing_summary": {
    "knowledge_base_matches": 2,
    "solution_scores": [...],
    "api_calls": 2,
    "notifications": 1
  },
  "completed_at": "2024-01-15T10:35:00.000Z"
}
```

## Customization

### Adding New Stages

1. Define stage function in `src/stages.py`
2. Add node to workflow in `src/agent.py`
3. Update configuration in `config/agent_config.yaml`
4. Add corresponding tests

### Extending MCP Abilities

1. Implement new ability in `src/mcp_client.py`
2. Map ability to appropriate server in configuration
3. Update stage implementations to use new ability

### Modifying Decision Logic

The escalation logic can be customized by modifying the `_should_escalate` method in the CustomerSupportAgent class.

## Performance Considerations

- **Memory Usage**: State persistence uses in-memory storage (MemorySaver)
- **Execution Time**: Typical workflow completion: 100-200ms
- **Scalability**: Thread-safe execution with configurable thread IDs
- **Error Handling**: Comprehensive exception handling with graceful degradation

## Future Enhancements

- Integration with real MCP servers
- Database-backed state persistence
- Advanced analytics and reporting
- Multi-language support
- Real-time customer interaction capabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## License

This project is provided as a demonstration of LangGraph capabilities for customer support automation.

---

**Author**: Prashanth Baithi
**Version**: 1.0.0  
**Last Updated**: August 2025

