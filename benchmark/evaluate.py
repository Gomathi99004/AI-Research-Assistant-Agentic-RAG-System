import asyncio
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agents.graph import run_workflow

async def run_evaluation():
    queries_path = os.path.join(os.path.dirname(__file__), "queries.json")
    with open(queries_path, "r") as f:
        queries = json.load(f)

    results = []
    
    print(f"Running evaluation for {len(queries)} queries...")
    
    for q in queries:
        print(f"\nEvaluating: {q['query']}")
        try:
            state = await run_workflow(q["query"])
            
            grounding = state.get("grounding_score", 1.0)
            conf = state.get("confidence", 1.0)
            
            failure_type = "none"
            if grounding < 0.6 or conf < 0.6:
                # Need to determine if it was a retrieval failure or generation failure
                from app.services.llm import call_llm
                context = state.get("compressed_context", "")
                coverage_prompt = f"Does the following Context contain the information required to answer the User Query?\nContext: {context}\nQuery: {q['query']}\nReply with exactly ONE word: YES or NO."
                coverage_resp = await call_llm(coverage_prompt, max_tokens=5, fast_mode=True)
                
                if "yes" in coverage_resp.lower():
                    failure_type = "generation_failure"
                else:
                    failure_type = "retrieval_failure"
            
            # Record metrics
            result = {
                "id": q["id"],
                "query": q["query"],
                "expected_type": q["expected_type"],
                "actual_type": state.get("query_type"),
                "grounding_score": grounding,
                "confidence": conf,
                "hop_count": state.get("hop_count"),
                "retrieval_quality": state.get("retrieval_quality"),
                "failure_type": failure_type,
                "reasoning_trace": state.get("reasoning_trace", [])
            }
            results.append(result)
            print(f"  -> Type: {result['actual_type']} | Grounding: {result['grounding_score']} | Hops: {result['hop_count']} | Failure: {failure_type}")
        except Exception as e:
            print(f"  -> Error: {e}")
            results.append({"id": q["id"], "error": str(e)})
            
    # Save results
    output_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
        
    print(f"\nEvaluation complete. Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())
