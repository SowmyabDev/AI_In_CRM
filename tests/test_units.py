"""
Unit Tests for E-Commerce CRM Chatbot
Tests core functionality of the chatbot components.
"""

import pytest
import json
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi_backend.intents import detect_intent, is_intent_resolvable, RESOLVABLE_INTENTS, ESCALATABLE_INTENTS
from fastapi_backend.analytics import ChatbotAnalytics
from fastapi_backend.models import ChatRequest, LoginRequest


class TestIntentDetection:
    """Test intent detection functionality."""
    
    def test_detect_greeting(self):
        """Test greeting detection."""
        assert detect_intent("hi") == "greet"
        assert detect_intent("hello") == "greet"
        assert detect_intent("Hey there") == "greet"
    
    def test_detect_goodbye(self):
        """Test goodbye detection."""
        assert detect_intent("bye") == "goodbye"
        assert detect_intent("thank you") == "goodbye"
        assert detect_intent("thanks") == "goodbye"
    
    def test_detect_orders(self):
        """Test order detection."""
        assert detect_intent("my orders") == "my_orders"
        assert detect_intent("order history") == "my_orders"
        assert detect_intent("show orders") == "my_orders"
    
    def test_detect_product_search(self):
        """Test product search detection."""
        assert detect_intent("search for laptop") == "search_products"
        assert detect_intent("do you have headphones") == "search_products"
    
    def test_detect_browse(self):
        """Test product browsing detection."""
        assert detect_intent("show products") == "browse_products"
        assert detect_intent("what products do you have") == "browse_products"
    
    def test_detect_cart(self):
        """Test cart detection."""
        assert detect_intent("show cart") == "show_cart"
        assert detect_intent("my cart") == "show_cart"
        assert detect_intent("add to cart") == "add_to_cart"
    
    def test_detect_refund(self):
        """Test refund detection."""
        assert detect_intent("refund") == "refund_query"
        assert detect_intent("i want a refund") == "refund_query"
    
    def test_detect_complaint(self):
        """Test complaint detection."""
        assert detect_intent("complaint") == "complaint"
        assert detect_intent("this is broken") == "complaint"


class TestIntentClassification:
    """Test intent classification (resolvable vs escalatable)."""
    
    def test_resolvable_intents_exist(self):
        """Test that resolvable intents are defined."""
        assert len(RESOLVABLE_INTENTS) > 0
        assert "greet" in RESOLVABLE_INTENTS
        assert "browse_products" in RESOLVABLE_INTENTS
    
    def test_escalatable_intents_exist(self):
        """Test that escalatable intents are defined."""
        assert len(ESCALATABLE_INTENTS) > 0
        assert "refund_query" in ESCALATABLE_INTENTS
        assert "complaint" in ESCALATABLE_INTENTS
    
    def test_no_overlap(self):
        """Test that resolvable and escalatable don't overlap."""
        overlap = RESOLVABLE_INTENTS & ESCALATABLE_INTENTS
        assert len(overlap) == 0, f"Overlapping intents: {overlap}"


class TestAnalytics:
    """Test analytics tracking."""
    
    @pytest.fixture
    def analytics(self):
        """Create test analytics instance."""
        analytics = ChatbotAnalytics("test_analytics.json")
        analytics.metrics = {
            "total_queries": 0,
            "resolved_queries": 0,
            "escalated_queries": 0,
            "by_intent": {}
        }
        yield analytics
        # Cleanup
        if os.path.exists("test_analytics.json"):
            os.remove("test_analytics.json")
    
    def test_record_resolved_query(self, analytics):
        """Test recording a resolved query."""
        analytics.record_query("greet", resolved=True)
        assert analytics.metrics["total_queries"] == 1
        assert analytics.metrics["resolved_queries"] == 1
        assert analytics.get_resolution_rate() == 1.0
    
    def test_record_escalated_query(self, analytics):
        """Test recording an escalated query."""
        analytics.record_query("refund_query", resolved=False)
        assert analytics.metrics["total_queries"] == 1
        assert analytics.metrics["escalated_queries"] == 1
        assert analytics.get_escalation_rate() == 1.0
    
    def test_mixed_queries(self, analytics):
        """Test mixed resolved and escalated queries."""
        analytics.record_query("greet", resolved=True)
        analytics.record_query("greet", resolved=True)
        analytics.record_query("refund_query", resolved=False)
        
        assert analytics.metrics["total_queries"] == 3
        assert analytics.metrics["resolved_queries"] == 2
        assert analytics.metrics["escalated_queries"] == 1
        assert pytest.approx(analytics.get_resolution_rate()) == 2/3
    
    def test_by_intent_tracking(self, analytics):
        """Test per-intent tracking."""
        analytics.record_query("greet", resolved=True)
        analytics.record_query("greet", resolved=False)
        analytics.record_query("refund_query", resolved=False)
        
        assert analytics.metrics["by_intent"]["greet"]["total"] == 2
        assert analytics.metrics["by_intent"]["greet"]["resolved"] == 1
        assert pytest.approx(analytics.metrics["by_intent"]["greet"]["resolution_rate"]) == 0.5
        
        assert analytics.metrics["by_intent"]["refund_query"]["total"] == 1
        assert analytics.metrics["by_intent"]["refund_query"]["resolved"] == 0


class TestModels:
    """Test Pydantic models."""
    
    def test_chat_request_valid(self):
        """Test valid chat request."""
        req = ChatRequest(message="Hello", session_id="sess123")
        assert req.message == "Hello"
        assert req.session_id == "sess123"
    
    def test_chat_request_empty_message(self):
        """Test chat request with empty message."""
        with pytest.raises(Exception):  # Pydantic validation error
            ChatRequest(message="", session_id="sess123")
    
    def test_login_request_valid(self):
        """Test valid login request."""
        req = LoginRequest(
            email="user@example.com",
            password="password123",
            session_id="sess123"
        )
        assert req.email == "user@example.com"
    
    def test_login_request_invalid_email(self):
        """Test login request with invalid email."""
        with pytest.raises(Exception):  # Pydantic validation error
            LoginRequest(
                email="invalid-email",
                password="password123",
                session_id="sess123"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
