import simpy
import random
import numpy as np
import pandas as pd

from simulation.config import *
from crm_chatbot.chatbot_engine import chatbot_resolves_query


def set_random_seeds():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

def chatbot_resolves():
    """
    Simulation-facing chatbot call.
    Treats chatbot as a black box.
    """
    user_query = random.choice(CHATBOT_QUERIES)
    return chatbot_resolves_query(user_query)

def customer(env, agents, stats):
    arrival_time = env.now

    if chatbot_resolves():
        stats["resolved_by_bot"] += 1
        return

    stats["escalated"] += 1

    with agents.request() as request:
        patience = random.expovariate(1.0 / PATIENCE_TIME)
        result = yield request | env.timeout(patience)

        if request not in result:
            stats["abandoned"] += 1
            return

        wait_time = env.now - arrival_time
        stats["wait_times"].append(wait_time)

        service_time = random.expovariate(1.0 / SERVICE_TIME)
        yield env.timeout(service_time)

        stats["served"] += 1

def arrival_process(env, agents, stats):
    while env.now < WORKING_HOURS_MIN:
        interarrival = random.expovariate(ARRIVAL_RATE)
        yield env.timeout(interarrival)
        env.process(customer(env, agents, stats))

def run_simulation(n_agents):
    env = simpy.Environment()
    agents = simpy.Resource(env, capacity=n_agents)

    stats = {
        "resolved_by_bot": 0,
        "escalated": 0,
        "served": 0,
        "abandoned": 0,
        "wait_times": []
    }

    env.process(arrival_process(env, agents, stats))
    env.run(until=WORKING_HOURS_MIN)

    avg_wait = np.mean(stats["wait_times"]) if stats["wait_times"] else 0.0
    abandonment = (
        stats["abandoned"] / stats["escalated"] * 100
        if stats["escalated"] > 0 else 0.0
    )

    return avg_wait, abandonment

def main():
    set_random_seeds()
    results = []

    print("================ STARTING SIMULATION =================\n")

    for n_agents in range(1, MAX_AGENTS + 1):
        print(f"Running simulation for N = {n_agents} agent(s)")
        avg_wait, abandon = run_simulation(n_agents)

       

        print(
            f"[SIM DONE] Agents={n_agents} | "
            f"AvgWait={avg_wait:.4f} min | "
            f"Abandonment={abandon:.2f}%"
        )

        results.append({
            "Agents": n_agents,
            "Avg Wait Time (min)": avg_wait,
            "Abandonment %": abandon
        })

    df = pd.DataFrame(results)

    df["Dist_to_Optimal"] = np.sqrt(
        df["Avg Wait Time (min)"] ** 2 +
        df["Abandonment %"] ** 2
    )

    df["Dist_to_TARGET"] = np.sqrt(
        (df["Avg Wait Time (min)"] - TARGET_AVG_WAIT) ** 2 +
        (df["Abandonment %"] - TARGET_ABANDONMENT) ** 2
    )

    optimal_idx = df["Dist_to_Optimal"].idxmin()
    acceptable_idx = df["Dist_to_TARGET"].idxmin()

    optimal_agents = df.loc[optimal_idx, "Agents"]

    df["Label"] = "Other"
    df.loc[acceptable_idx, "Label"] = "Acceptable (Target)"
    df.loc[optimal_idx, "Label"] = "Optimal (Perfect)"

    df_final = df[df["Agents"] <= optimal_agents].copy()

    df_final["Avg Wait Time (min)"] = df_final["Avg Wait Time (min)"].round(4)
    df_final["Abandonment %"] = df_final["Abandonment %"].round(4)

    print("\n-------------- STAFFING RESULTS (1 to OPTIMAL) --------------\n")
    print(
        df_final[[
            "Agents",
            "Avg Wait Time (min)",
            "Abandonment %",
            "Label"
        ]].to_string(index=False)
    )

    print(f"\nAcceptable agents (Target): {df.loc[acceptable_idx, 'Agents']}")
    print(f"Optimal agents (Perfect): {optimal_agents}")


if __name__ == "__main__":
    main()