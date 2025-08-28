#!/usr/bin/env python3
"""
Test cases for LangGraph Customer Support Agent
"""
import unittest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent import create_agent


class TestCustomerSupportAgent(unittest.TestCase):
    """Test cases for the Customer Support Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = create_agent()
        self.sample_input = {
            "customer_name": "Test Customer",
            "email": "test@example.com",
            "query": "Test query for support",
            "priority": "medium",
            "ticket_id": "TEST-001"
        }
    
    def test_agent_creation(self):
        """Test that agent can be created successfully"""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.graph)
    
    def test_workflow_execution(self):
        """Test that workflow executes successfully"""
        result = self.agent.run(self.sample_input, thread_id="test_thread")
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["final_payload"])
        self.assertGreater(len(result["stage_history"]), 0)
        self.assertGreater(len(result["mcp_calls"]), 0)
    
    def test_stage_sequence(self):
        """Test that all stages are executed in correct order"""
        result = self.agent.run(self.sample_input, thread_id="test_sequence")
        
        expected_stages = [
            "INTAKE", "UNDERSTAND", "PREPARE", "ASK", "WAIT", 
            "RETRIEVE", "DECIDE", "UPDATE", "CREATE", "DO", "COMPLETE"
        ]
        
        self.assertEqual(result["stage_history"], expected_stages)
    
    def test_mcp_calls(self):
        """Test that MCP calls are made to correct servers"""
        result = self.agent.run(self.sample_input, thread_id="test_mcp")
        
        # Check that both COMMON and ATLAS servers are called
        servers_called = set(call["server"] for call in result["mcp_calls"])
        self.assertIn("COMMON", servers_called)
        self.assertIn("ATLAS", servers_called)
    
    def test_final_payload_structure(self):
        """Test that final payload has correct structure"""
        result = self.agent.run(self.sample_input, thread_id="test_payload")
        
        final_payload = result["final_payload"]
        
        # Check required fields
        required_fields = [
            "ticket_id", "customer_name", "email", "original_query",
            "priority", "resolution_status", "escalated", "generated_response",
            "stage_history", "processing_summary", "completed_at"
        ]
        
        for field in required_fields:
            self.assertIn(field, final_payload)
    
    def test_escalation_scenario(self):
        """Test escalation scenario with low solution scores"""
        # This would require modifying the mock to return low scores
        # For now, we'll just verify the escalation logic exists
        result = self.agent.run(self.sample_input, thread_id="test_escalation")
        
        # Check that escalation decision is recorded
        final_payload = result["final_payload"]
        self.assertIn("escalated", final_payload)
        self.assertIsInstance(final_payload["escalated"], bool)


class TestMCPIntegration(unittest.TestCase):
    """Test MCP client integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        from src.mcp_client import create_mcp_client
        self.common_client = create_mcp_client("COMMON")
        self.atlas_client = create_mcp_client("ATLAS")
    
    def test_common_server_abilities(self):
        """Test COMMON server abilities"""
        test_payload = {"query": "test query"}
        
        # Test parse_request_text
        result = self.common_client.call_ability("parse_request_text", test_payload)
        self.assertIn("parsed_request", result)
        
        # Test normalize_fields
        result = self.common_client.call_ability("normalize_fields", test_payload)
        self.assertIn("normalized_fields", result)
    
    def test_atlas_server_abilities(self):
        """Test ATLAS server abilities"""
        test_payload = {"query": "test query"}
        
        # Test extract_entities
        result = self.atlas_client.call_ability("extract_entities", test_payload)
        self.assertIn("extracted_entities", result)
        
        # Test knowledge_base_search
        result = self.atlas_client.call_ability("knowledge_base_search", test_payload)
        self.assertIn("knowledge_base_results", result)


if __name__ == "__main__":
    unittest.main()

