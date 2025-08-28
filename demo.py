#!/usr/bin/env python3
"""
Demo script for LangGraph Customer Support Agent
"""
import json
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent import create_agent


def main():
    """Run the demo"""
    print("=" * 80)
    print("LangGraph Customer Support Agent Demo")
    print("=" * 80)
    
    # Sample customer query
    sample_input = {
        "customer_name": "John Smith",
        "email": "john.smith@example.com",
        "query": "I can't log into my account. I keep getting a 'Login Failed' error message when I try to access the system.",
        "priority": "high",
        "ticket_id": "TICKET-2024-001"
    }
    
    print("\n📥 INPUT PAYLOAD:")
    print(json.dumps(sample_input, indent=2))
    
    # Create and run the agent
    print("\n🤖 CREATING LANGGRAPH AGENT...")
    agent = create_agent()
    
    print("\n📊 WORKFLOW VISUALIZATION:")
    print(agent.get_workflow_visualization())
    
    print("\n🚀 RUNNING CUSTOMER SUPPORT WORKFLOW...")
    print("-" * 50)
    
    # Run the workflow
    result = agent.run(sample_input, thread_id=f"demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    print("\n" + "=" * 80)
    print("WORKFLOW EXECUTION RESULTS")
    print("=" * 80)
    
    if result["success"]:
        print("✅ Workflow completed successfully!")
        
        print("\n📋 STAGE EXECUTION HISTORY:")
        for i, stage in enumerate(result["stage_history"], 1):
            print(f"  {i}. {stage}")
        
        print("\n🔧 MCP CLIENT CALLS:")
        for call in result["mcp_calls"]:
            print(f"  • {call['server']}/{call['ability']} at {call['timestamp']}")
        
        print("\n📄 FINAL PAYLOAD:")
        print(json.dumps(result["final_payload"], indent=2))
        
        print("\n📝 EXECUTION LOG:")
        for log_entry in result["execution_log"]:
            print(f"  [{log_entry['timestamp']}] {log_entry['stage']}: {log_entry['details']}")
        
    else:
        print("❌ Workflow failed!")
        print(f"Error: {result['error']}")
        if result["errors"]:
            print("Additional errors:")
            for error in result["errors"]:
                print(f"  • {error}")
    
    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()

