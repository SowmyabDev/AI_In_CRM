"""
Chatbot Analytics Module
Tracks resolution and escalation metrics at the intent level.
Used to calculate the true human agent workload.
"""

import json
import os
from typing import Dict


class ChatbotAnalytics:
    """
    Tracks chatbot performance metrics for staffing analysis.
    Records total queries, resolved/escalated counts, and per-intent stats.
    """
    def __init__(self, data_file: str = "chatbot_metrics.json"):
        self.data_file = data_file
        self.metrics = {
            "total_queries": 0,
            "resolved_queries": 0,
            "escalated_queries": 0,
            "by_intent": {}
        }
        self.load_metrics()

    def load_metrics(self) -> None:
        """Load existing metrics from file if available."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.metrics = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load metrics file: {e}")

    def save_metrics(self) -> None:
        """Save metrics to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save metrics file: {e}")

    def record_query(self, intent: str, resolved: bool, response_type: str = "chatbot") -> None:
        """
        Record a query and its resolution status.
        Args:
            intent: The detected intent
            resolved: True if chatbot resolved it, False if escalated
            response_type: 'chatbot' or 'human' (for future use)
        """
        self.metrics["total_queries"] += 1
        if resolved:
            self.metrics["resolved_queries"] += 1
        else:
            self.metrics["escalated_queries"] += 1
        # Track by intent
        if intent not in self.metrics["by_intent"]:
            self.metrics["by_intent"][intent] = {
                "total": 0,
                "resolved": 0,
                "escalated": 0,
                "resolution_rate": 0.0
            }
        self.metrics["by_intent"][intent]["total"] += 1
        if resolved:
            self.metrics["by_intent"][intent]["resolved"] += 1
        else:
            self.metrics["by_intent"][intent]["escalated"] += 1
        # Calculate resolution rate
        total = self.metrics["by_intent"][intent]["total"]
        resolved_count = self.metrics["by_intent"][intent]["resolved"]
        self.metrics["by_intent"][intent]["resolution_rate"] = (
            resolved_count / total if total > 0 else 0.0
        )
        self.save_metrics()

    def get_resolution_rate(self) -> float:
        """Get overall chatbot resolution rate (0.0 to 1.0)."""
        if self.metrics["total_queries"] == 0:
            return 0.0
        return self.metrics["resolved_queries"] / self.metrics["total_queries"]

    def get_escalation_rate(self) -> float:
        """Get overall escalation rate (0.0 to 1.0)."""
        return 1.0 - self.get_resolution_rate()

    def get_resolution_rate_by_intent(self, intent: str) -> float:
        """Get resolution rate for a specific intent."""
        if intent not in self.metrics["by_intent"]:
            return 0.0
        return self.metrics["by_intent"][intent]["resolution_rate"]

    def get_metrics_summary(self) -> Dict:
        """Get summary metrics for reporting."""
        return {
            "total_queries": self.metrics["total_queries"],
            "resolved_queries": self.metrics["resolved_queries"],
            "escalated_queries": self.metrics["escalated_queries"],
            "overall_resolution_rate": self.get_resolution_rate(),
            "overall_escalation_rate": self.get_escalation_rate(),
            "by_intent": self.metrics["by_intent"]
        }

    def print_report(self) -> None:
        """Print a detailed analytics report to stdout."""
        print("\n" + "="*70)
        print("CHATBOT PERFORMANCE ANALYTICS REPORT")
        print("="*70)
        print(f"Total Queries Processed: {self.metrics['total_queries']}")
        print(f"Resolved by Chatbot: {self.metrics['resolved_queries']} ({self.get_resolution_rate()*100:.1f}%)")
        print(f"Escalated to Human: {self.metrics['escalated_queries']} ({self.get_escalation_rate()*100:.1f}%)")
        print("\nResolution Rate by Intent:")
        print("-"*70)
        for intent, data in self.metrics["by_intent"].items():
            rate = data["resolution_rate"] * 100
            print(f"  {intent:20s}: {data['total']:3d} queries → {rate:5.1f}% resolved, {100-rate:5.1f}% escalated")
        print("="*70 + "\n")


# Global analytics instance
analytics = ChatbotAnalytics()
