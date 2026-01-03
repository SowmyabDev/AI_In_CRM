#!/usr/bin/env python3
"""
Test Script: Staffing Analysis Feature
Simulates chatbot queries and generates staffing recommendations.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi_backend.analytics import ChatbotAnalytics
from fastapi_backend.simulation import run_staffing_analysis, print_staffing_recommendations
from fastapi_backend.intents import RESOLVABLE_INTENTS, ESCALATABLE_INTENTS
import random


def simulate_chatbot_usage():
    """Simulate 150 chatbot interactions with realistic distribution."""
    
    analytics = ChatbotAnalytics("test_metrics.json")
    
    # Reset for testing
    analytics.metrics = {
        "total_queries": 0,
        "resolved_queries": 0,
        "escalated_queries": 0,
        "by_intent": {}
    }
    
    print("Simulating 150 chatbot interactions...")
    
    # Simulate resolvable queries (typically high success rate)
    resolvable_distribution = {
        "greet": (15, 1.0),  # greeting count, success rate
        "my_orders": (18, 0.95),
        "browse_products": (20, 1.0),
        "search_products": (25, 0.88),
        "show_cart": (12, 0.95),
        "product_details": (8, 0.90),
        "recommendations": (10, 0.92),
    }
    
    # Simulate escalatable queries (typically low success rate)
    escalatable_distribution = {
        "refund_query": (8, 0.0),   # Should always escalate
        "complaint": (6, 0.1),      # Usually escalate
        "return_request": (7, 0.15),
        "payment": (5, 0.2),
        "account": (6, 0.25),
    }
    
    # Resolvable intents
    for intent, (count, success_rate) in resolvable_distribution.items():
        for _ in range(count):
            resolved = random.random() < success_rate
            analytics.record_query(intent, resolved=resolved)
    
    # Escalatable intents
    for intent, (count, success_rate) in escalatable_distribution.items():
        for _ in range(count):
            resolved = random.random() < success_rate
            analytics.record_query(intent, resolved=resolved)
    
    return analytics


def main():
    print("\n" + "="*80)
    print("STAFFING ANALYSIS TEST - CHATBOT PERFORMANCE SIMULATION")
    print("="*80 + "\n")
    
    # Simulate chatbot interactions
    analytics = simulate_chatbot_usage()
    
    # Show metrics
    analytics.print_report()
    
    # Extract key metrics
    escalation_rate = analytics.get_escalation_rate()
    queries_per_hour = 20
    escalated_per_hour = queries_per_hour * escalation_rate
    
    print(f"📊 KEY METRICS")
    print(f"   Overall Resolution Rate: {analytics.get_resolution_rate()*100:.1f}%")
    print(f"   Overall Escalation Rate: {escalation_rate*100:.1f}%")
    print(f"   Baseline Queries/Hour: {queries_per_hour}")
    print(f"   Expected Escalations/Hour: {escalated_per_hour:.1f}")
    
    # Run staffing analysis
    print(f"\n🔄 RUNNING STAFFING SIMULATIONS...")
    print(f"   (Testing 5 agents → 20 agents with 3 simulations each)")
    print(f"   (This may take 30-60 seconds...)\n")
    
    results = run_staffing_analysis(escalated_per_hour, num_simulations=3)
    
    # Display recommendations
    print_staffing_recommendations(results)
    
    # Find optimal
    optimal = None
    for result in results:
        if "Optimal" in result["outcome"]:
            optimal = result
            break
    
    if optimal:
        print(f"\n" + "="*80)
        print(f"✅ STAFFING RECOMMENDATION")
        print(f"="*80)
        print(f"Recommended Agent Count: {optimal['num_agents']}")
        print(f"Average Wait Time: {optimal['avg_wait_time']:.2f} minutes")
        print(f"Customer Abandonment: {optimal['avg_abandonment']:.2f}%")
        print(f"Service Quality: OPTIMAL ✨")
        print(f"="*80 + "\n")
    
    print("✅ Test completed successfully!")
    print(f"   Metrics saved to: test_metrics.json")
    print(f"   View detailed API responses at:")
    print(f"   - GET http://127.0.0.1:8000/analytics/metrics")
    print(f"   - GET http://127.0.0.1:8000/analytics/staffing")


if __name__ == "__main__":
    main()
