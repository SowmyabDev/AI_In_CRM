#!/usr/bin/env python3
"""
Real Chatbot Performance Test
Tests actual chatbot responses and measures success rates.
Then uses real metrics for staffing analysis simulation.
"""

import sys
import os
import json
import requests
from typing import Dict, List, Tuple

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi_backend.analytics import ChatbotAnalytics
from fastapi_backend.simulation import run_staffing_analysis, print_staffing_recommendations
from fastapi_backend.intents import RESOLVABLE_INTENTS, ESCALATABLE_INTENTS

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
SESSION_ID = "test-session-12345"

# Test cases: (message, expected_intent, is_resolvable, keywords_in_response)
TEST_CASES = [
    # Greetings (RESOLVABLE)
    ("Hi there", "greet", True, ["hello", "help", "can i"]),
    ("Hello!", "greet", True, ["hello", "help"]),
    ("Hey how are you", "greet", True, ["hello", "help"]),
    
    # Goodbyes (RESOLVABLE)
    ("Thank you for your help", "goodbye", True, ["thank", "day"]),
    ("Thanks!", "goodbye", True, ["thank"]),
    ("Bye!", "goodbye", True, ["welcome", "bye", "day"]),
    
    # Orders (RESOLVABLE)
    ("Show me my orders", "my_orders", True, ["order", "ORD"]),
    ("What are my current orders", "my_orders", True, ["order", "ORD"]),
    ("Order history", "my_orders", True, ["order", "ORD"]),
    
    # Browse Products (RESOLVABLE)
    ("Show all products", "browse_products", True, ["product", "₹", "available"]),
    ("What products do you have", "browse_products", True, ["product", "available"]),
    ("Show me available items", "browse_products", True, ["product"]),
    
    # Search Products (RESOLVABLE)
    ("Search for headphones", "search_products", True, ["product", "found", "match"]),
    ("Do you have wireless earbuds", "search_products", True, ["found", "match", "product"]),
    ("Find me a laptop", "search_products", True, ["found", "match"]),
    
    # Cart Management (RESOLVABLE)
    ("Show my cart", "show_cart", True, ["cart", "empty"]),
    ("What's in my cart", "show_cart", True, ["cart"]),
    ("My cart items", "show_cart", True, ["cart"]),
    
    # Product Details (RESOLVABLE)
    ("What's the price of Wireless Earbuds", "product_details", True, ["price", "₹", "product"]),
    ("Tell me about the laptop specifications", "product_details", True, ["price", "product", "description"]),
    
    # Recommendations (RESOLVABLE)
    ("Recommend a product", "recommendations", True, ["product", "popular", "best", "recommend"]),
    ("What are the best sellers", "recommendations", True, ["product", "popular"]),
    
    # Promotions (RESOLVABLE)
    ("Do you have any discounts", "promotions", True, ["discount", "deal", "sale", "promo"]),
    ("Show me current deals", "promotions", True, ["discount", "sale"]),
    
    # Refund Request (ESCALATABLE - should escalate)
    ("I want a refund", "refund_query", False, ["refund", "escalat", "human", "agent"]),
    ("Can I get my money back", "refund_query", False, ["refund", "escalat", "human"]),
    
    # Complaint (ESCALATABLE - should escalate)
    ("I have a complaint about my order", "complaint", False, ["escalat", "human", "agent", "complaint"]),
    ("This product is broken", "complaint", False, ["escalat", "human", "agent"]),
    
    # Return Request (ESCALATABLE - should escalate)
    ("I want to return this item", "return_request", False, ["return", "escalat", "human"]),
    ("Can I replace my order", "return_request", False, ["replace", "escalat", "human"]),
    
    # Payment (ESCALATABLE - should escalate)
    ("How do I pay for this", "payment", False, ["payment", "escalat", "human", "checkout"]),
    ("I want to make payment", "payment", False, ["payment", "checkout"]),
    
    # Account (ESCALATABLE - should escalate)
    ("Change my password", "account", False, ["account", "escalat", "human"]),
    ("Update my profile", "account", False, ["account", "profile", "escalat"]),
    
    # Human Handoff (ESCALATABLE - should escalate)
    ("Connect me to a human", "human_handoff", False, ["human", "agent", "escalat"]),
    ("I want to talk to customer support", "human_handoff", False, ["agent", "support", "escalat"]),
]


class ChatbotTestSuite:
    def __init__(self, backend_url: str, session_id: str):
        self.backend_url = backend_url
        self.session_id = session_id
        self.results = []
        self.analytics = ChatbotAnalytics("real_chatbot_metrics.json")
        # Reset metrics
        self.analytics.metrics = {
            "total_queries": 0,
            "resolved_queries": 0,
            "escalated_queries": 0,
            "by_intent": {}
        }
    
    def send_message(self, message: str) -> Dict:
        """Send a message to the chatbot and get response."""
        try:
            response = requests.post(
                f"{self.backend_url}/chat",
                json={
                    "message": message,
                    "session_id": self.session_id
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
            return {"reply": "", "error": str(e)}
    
    def check_response_quality(self, reply: str, keywords: List[str]) -> bool:
        """Check if response contains expected keywords."""
        reply_lower = reply.lower()
        # Should contain at least one keyword
        return any(keyword.lower() in reply_lower for keyword in keywords)
    
    def run_test(self, message: str, expected_intent: str, is_resolvable: bool, keywords: List[str]) -> bool:
        """Run a single test case."""
        response = self.send_message(message)
        reply = response.get("reply", "")
        
        # Check response quality
        has_keywords = self.check_response_quality(reply, keywords)
        
        # Determine if test passed
        if is_resolvable:
            # For resolvable intents, should NOT escalate (no "escalat"/"human" in response)
            is_escalated = "escalat" in reply.lower() or "human" in reply.lower()
            test_passed = has_keywords and not is_escalated
        else:
            # For escalatable intents, should escalate or handle appropriately
            # Check if it mentions escalation, human, or agent
            test_passed = has_keywords or ("escalat" in reply.lower() or "human" in reply.lower() or "agent" in reply.lower())
        
        # Record in analytics
        self.analytics.record_query(expected_intent, resolved=test_passed)
        
        # Store result
        self.results.append({
            "message": message,
            "intent": expected_intent,
            "is_resolvable": is_resolvable,
            "passed": test_passed,
            "reply": reply[:80] + "..." if len(reply) > 80 else reply
        })
        
        return test_passed
    
    def run_all_tests(self) -> None:
        """Run all test cases."""
        passed = 0
        failed = 0
        
        print("\n" + "="*100)
        print("REAL CHATBOT PERFORMANCE TEST SUITE")
        print("="*100 + "\n")
        
        for i, (message, intent, is_resolvable, keywords) in enumerate(TEST_CASES, 1):
            result = self.run_test(message, intent, is_resolvable, keywords)
            status = "✅ PASS" if result else "❌ FAIL"
            
            print(f"{i:2d}. {status} | Intent: {intent:20s} | Msg: {message[:50]}")
            
            if result:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "="*100)
        print(f"RESULTS: {passed} passed, {failed} failed out of {len(TEST_CASES)} tests")
        print(f"Success Rate: {(passed/len(TEST_CASES)*100):.1f}%")
        print("="*100 + "\n")
    
    def print_detailed_results(self) -> None:
        """Print detailed test results."""
        print("\nDETAILED TEST RESULTS:")
        print("-"*100)
        print(f"{'#':<3} {'Status':<8} {'Intent':<20} {'Message':<40} {'Response':<25}")
        print("-"*100)
        
        for i, result in enumerate(self.results, 1):
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(
                f"{i:<3} {status:<8} {result['intent']:<20} "
                f"{result['message'][:40]:<40} {result['reply']:<25}"
            )
        
        print("-"*100 + "\n")


def main():
    print("\n🤖 Starting Real Chatbot Performance Analysis...\n")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"❌ Backend health check failed. Make sure FastAPI is running on {BACKEND_URL}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print("   Start it with: uvicorn fastapi_backend.main:app --reload")
        sys.exit(1)
    
    print(f"✅ Backend is running on {BACKEND_URL}\n")
    
    # Run chatbot tests
    tester = ChatbotTestSuite(BACKEND_URL, SESSION_ID)
    tester.run_all_tests()
    tester.print_detailed_results()
    
    # Show real analytics
    tester.analytics.print_report()
    
    # Extract real metrics
    resolution_rate = tester.analytics.get_resolution_rate()
    escalation_rate = tester.analytics.get_escalation_rate()
    
    print(f"\n📊 REAL CHATBOT METRICS (from {len(TEST_CASES)} interactions)")
    print(f"   Overall Resolution Rate: {resolution_rate*100:.1f}%")
    print(f"   Overall Escalation Rate: {escalation_rate*100:.1f}%")
    
    # Resolution rates by intent
    print(f"\n   Resolution Rates by Intent:")
    print(f"   {'-'*60}")
    for intent in sorted(tester.analytics.metrics["by_intent"].keys()):
        data = tester.analytics.metrics["by_intent"][intent]
        rate = data["resolution_rate"] * 100
        print(f"      {intent:25s}: {rate:5.1f}% ({data['resolved']}/{data['total']})")
    
    # Calculate staffing needs based on real metrics
    queries_per_hour = 20
    escalated_per_hour = queries_per_hour * escalation_rate
    
    print(f"\n📞 STAFFING ANALYSIS PARAMETERS (based on real chatbot performance)")
    print(f"   Baseline Incoming Queries/Hour: {queries_per_hour}")
    print(f"   Real Chatbot Escalation Rate: {escalation_rate*100:.1f}%")
    print(f"   Expected Escalations to Humans/Hour: {escalated_per_hour:.2f}")
    
    # Run staffing simulation with real metrics
    print(f"\n🔄 RUNNING STAFFING SIMULATIONS WITH REAL METRICS...")
    print(f"   (Testing 5-20 agents with 3 simulations each)")
    print(f"   (This may take 30-60 seconds...)\n")
    
    results = run_staffing_analysis(escalated_per_hour, num_simulations=3)
    
    # Display recommendations
    print_staffing_recommendations(results)
    
    # Summary
    print(f"\n" + "="*80)
    print(f"SUMMARY")
    print(f"="*80)
    print(f"✅ Chatbot successfully resolved {resolution_rate*100:.1f}% of queries")
    print(f"📊 {escalated_per_hour:.2f} queries/hour need human agents")
    
    # Find optimal staffing level
    optimal = None
    for r in results:
        if "Optimal" in r["outcome"]:
            optimal = r["num_agents"]
            break
    
    if optimal:
        print(f"🎯 RECOMMENDED STAFFING: {optimal} agents")
    else:
        print(f"🎯 RECOMMENDED STAFFING: Review simulation results above")
    
    print(f"="*80 + "\n")


if __name__ == "__main__":
    main()
