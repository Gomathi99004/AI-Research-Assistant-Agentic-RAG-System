import json
import os
from collections import defaultdict

def analyze_logs():
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "app.log")
    if not os.path.exists(log_path):
        print(f"No log file found at {log_path}")
        return

    clusters = defaultdict(list)
    total_queries = 0
    total_failures = 0

    with open(log_path, "r") as f:
        for line in f:
            try:
                record = json.loads(line)
                if record.get("message") == "Workflow completed":
                    total_queries += 1
                    trace = record.get("trace", [])
                    
                    # Detect if there was an adversarial fail
                    adv_fail = any("Adversarial FAIL" in step for step in trace)
                    
                    if adv_fail or record.get("hops", 1) > 1:
                        total_failures += 1
                        query = record.get("query", "Unknown")
                        hops = record.get("hops", 1)
                        
                        # Naive clustering: categorize by hop count and if adversarial fail occurred
                        if adv_fail:
                            cluster_key = "Adversarial Hallucination"
                        elif hops >= 3:
                            cluster_key = "Deep Multi-Hop Failure (Hard Retrieval)"
                        else:
                            cluster_key = "Routine Re-retrieval (Recoverable)"
                            
                        clusters[cluster_key].append({"query": query, "hops": hops})
            except json.JSONDecodeError:
                pass

    print("--- Failure Clustering Analysis ---")
    print(f"Total Queries Logged: {total_queries}")
    print(f"Total Queries with Retries/Failures: {total_failures}")
    print("-" * 35)
    
    for cluster, items in clusters.items():
        print(f"\nCluster: {cluster} (Count: {len(items)})")
        for item in items[:5]: # Show max 5 examples
            print(f"  - Query: {item['query']} | Hops: {item['hops']}")
        if len(items) > 5:
            print(f"  ... and {len(items) - 5} more.")

if __name__ == "__main__":
    analyze_logs()
