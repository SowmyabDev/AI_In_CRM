"""
SimPy-based Queue Simulation for Support Agent Staffing Analysis
Models customer queries being handled by human support agents.
"""

import simpy
from typing import List, Dict
import statistics
import random


class SupportAgent:
    """
    Represents a human support agent in the simulation.
    Each agent can handle one query at a time.
    """
    
    def __init__(self, env: simpy.Environment, agent_id: int):
        self.env = env
        self.agent_id = agent_id
        self.resource = simpy.Resource(env, capacity=1)
        self.queries_handled = 0
        self.idle_time = 0
        self.busy_start = 0
    
    def handle_query(self, duration: float):
        """Handle a customer query for the given duration (in minutes)."""
        with self.resource.request() as req:
            yield req
            self.busy_start = self.env.now
            yield self.env.timeout(duration)
            self.queries_handled += 1


class CustomerQuery:
    """
    Represents a customer query that needs human support.
    Tracks arrival, wait, and handling times.
    """
    
    def __init__(self, query_id: int, arrival_time: float, duration: float):
        self.query_id = query_id
        self.arrival_time = arrival_time
        self.duration = duration
        self.wait_time = 0
        self.start_time = 0
        self.end_time = 0
        self.abandoned = False


class SupportQueueSimulation:
    """
    SimPy simulation for support queue with multiple agents.
    Models arrivals, queueing, abandonment, and agent handling.
    """
    
    def __init__(self, num_agents: int, arrival_rate: float = 5.0, avg_handle_time: float = 8.0):
        """
        Initialize simulation.
        
        Args:
            num_agents: Number of support agents
            arrival_rate: Average queries per hour
            avg_handle_time: Average handling time in minutes per query
        """
        self.env = simpy.Environment()
        self.num_agents = num_agents
        self.arrival_rate = arrival_rate  # queries per hour
        self.avg_handle_time = avg_handle_time  # minutes
        self.agents = [SupportAgent(self.env, i) for i in range(num_agents)]
        self.queries: List[CustomerQuery] = []
        self.query_counter = 0
        self.abandonment_threshold = 30  # minutes - customer abandons if wait > 30 min
    
    def customer_arrival_process(self, total_hours: float = 8):
        """Generate customer arrivals (Poisson-like)."""
        arrival_interval = 60 / self.arrival_rate  # minutes between arrivals
        
        time_elapsed = 0
        while time_elapsed < total_hours * 60:
            # Slight randomness in intervals
            wait_time = random.expovariate(1.0 / arrival_interval)
            time_elapsed += wait_time
            
            if time_elapsed < total_hours * 60:
                # Generate query handle time (random around average)
                duration = random.gauss(self.avg_handle_time, self.avg_handle_time * 0.3)
                duration = max(2, duration)  # At least 2 minutes
                
                query = CustomerQuery(
                    query_id=self.query_counter,
                    arrival_time=time_elapsed,
                    duration=duration
                )
                self.query_counter += 1
                self.env.process(self.process_query(query))
                yield self.env.timeout(wait_time)
    
    def process_query(self, query: CustomerQuery):
        """Process a customer query through the queue."""
        query.start_time = self.env.now
        
        # Check if customer will abandon if wait is too long
        # Try to find the agent with shortest queue
        best_agent = min(self.agents, key=lambda a: len(a.resource.queue))
        
        with best_agent.resource.request() as req:
            yield req
            
            query.wait_time = self.env.now - query.start_time
            
            # Check abandonment
            if query.wait_time > self.abandonment_threshold:
                query.abandoned = True
                self.queries.append(query)
                return
            
            # Handle the query
            yield self.env.timeout(query.duration)
            query.end_time = self.env.now
            best_agent.queries_handled += 1
        
        self.queries.append(query)
    
    def run(self, simulation_hours: float = 8):
        """Run the simulation for the specified number of hours."""
        self.env.process(self.customer_arrival_process(simulation_hours))
        self.env.run()
    
    def get_statistics(self) -> Dict:
        """Calculate and return simulation statistics."""
        if not self.queries:
            return {}
        
        wait_times = [q.wait_time for q in self.queries if not q.abandoned]
        abandoned_count = sum(1 for q in self.queries if q.abandoned)
        
        stats = {
            "num_agents": self.num_agents,
            "total_queries": len(self.queries),
            "processed_queries": len(self.queries) - abandoned_count,
            "abandoned_queries": abandoned_count,
            "abandonment_rate": (abandoned_count / len(self.queries) * 100) if self.queries else 0,
            "avg_wait_time_min": statistics.mean(wait_times) if wait_times else 0,
            "max_wait_time_min": max(wait_times) if wait_times else 0,
            "median_wait_time_min": statistics.median(wait_times) if wait_times else 0,
            "p95_wait_time_min": sorted(wait_times)[int(len(wait_times)*0.95)] if len(wait_times) > 1 else 0,
        }
        
        return stats
    
    def print_report(self):
        """Print simulation results to stdout."""
        stats = self.get_statistics()
        if not stats:
            print("No query data to report.")
            return
        
        print(f"\nSimulation Results (Agents: {self.num_agents})")
        print("-" * 60)
        print(f"Total Queries: {stats['total_queries']}")
        print(f"Processed: {stats['processed_queries']}")
        print(f"Abandoned: {stats['abandoned_queries']} ({stats['abandonment_rate']:.1f}%)")
        print(f"Avg Wait Time: {stats['avg_wait_time_min']:.2f} min")
        print(f"Max Wait Time: {stats['max_wait_time_min']:.2f} min")
        print(f"Median Wait Time: {stats['median_wait_time_min']:.2f} min")
        print(f"95th Percentile: {stats['p95_wait_time_min']:.2f} min")
        print("-" * 60 + "\n")


def run_staffing_analysis(escalation_queries_per_hour: float, num_simulations: int = 3) -> List[Dict]:
    """
    Run simulations with different staffing levels to find optimal agent count.
    
    Args:
        escalation_queries_per_hour: Number of queries escalated to humans per hour
        num_simulations: Number of simulation runs per staffing level
    
    Returns:
        List of results with different agent counts
    """
    results = []
    
    for num_agents in [5, 10, 15, 18, 20]:
        all_stats = []
        
        for _ in range(num_simulations):
            sim = SupportQueueSimulation(
                num_agents=num_agents,
                arrival_rate=escalation_queries_per_hour,
                avg_handle_time=8.0  # 8 minutes average
            )
            sim.run(simulation_hours=8)
            stats = sim.get_statistics()
            all_stats.append(stats)
        
        # Average across simulations
        avg_stats = {
            "num_agents": num_agents,
            "avg_wait_time": sum(s["avg_wait_time_min"] for s in all_stats) / len(all_stats),
            "avg_abandonment": sum(s["abandonment_rate"] for s in all_stats) / len(all_stats),
        }
        
        # Classify staffing level
        if avg_stats["avg_abandonment"] > 10:
            outcome = "❌ Insufficient"
        elif avg_stats["avg_abandonment"] > 2:
            outcome = "⚠️  Acceptable but not optimal"
        elif avg_stats["avg_wait_time"] < 1:
            outcome = "✅ Optimal (N*)"
        else:
            outcome = "✅ Acceptable"
        
        avg_stats["outcome"] = outcome
        results.append(avg_stats)
    
    return results


def print_staffing_recommendations(results: List[Dict]):
    """Print staffing analysis recommendations to stdout."""
    print("\n" + "="*80)
    print("STAFFING ANALYSIS RECOMMENDATIONS")
    print("="*80)
    print(f"{'Agents':<8} {'Avg Wait Time':<18} {'Abandonment %':<18} {'Outcome':<30}")
    print("-"*80)
    
    for result in results:
        print(
            f"{result['num_agents']:<8} "
            f"{result['avg_wait_time']:<17.2f}m "
            f"{result['avg_abandonment']:<17.1f}% "
            f"{result['outcome']:<30}"
        )
    
    print("="*80 + "\n")
