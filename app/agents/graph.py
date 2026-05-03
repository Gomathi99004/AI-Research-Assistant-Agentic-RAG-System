from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.services.retrieval import fetch_chunks
from app.services.llm import call_llm
from app.services.classifier import classify_query
from app.services.compressor import compress_context
import json
from collections import defaultdict

reranker_model = None

def get_reranker():
    global reranker_model
    if reranker_model is None:
        from sentence_transformers import CrossEncoder
        from app.core.config import settings
        reranker_model = CrossEncoder(settings.RERANKER_MODEL, max_length=512)
    return reranker_model


# ─────────────────────────────────────────────────────────────
# NODE 1: Query Classifier
# ─────────────────────────────────────────────────────────────
async def classifier_node(state: AgentState):
    """Classifies query into: factual, conceptual, comparison, multi-hop, keyword-heavy."""
    query = state["query"]
    query_type = await classify_query(query)
    print(f"[Classifier] query_type={query_type}")
    return {"query_type": query_type}


# ─────────────────────────────────────────────────────────────
# NODE 2: Query Expansion
# ─────────────────────────────────────────────────────────────
async def expansion_node(state: AgentState):
    """Generates alternate search queries to improve retrieval recall."""
    query = state["query"]
    count = state.get("re_retrieve_count", 0)

    prompt = f"""You are an expert search query generator. Based on the user's original query, generate 2 alternate search queries that use different keywords but seek the same information.
This is to improve document retrieval recall.
Return exactly the 2 alternate queries, separated by a newline, with no bullet points or extra text.
Original Query: {query}
"""
    expanded = []
    try:
        response_text = await call_llm(prompt, max_tokens=150)
        expanded = [q.strip() for q in response_text.split('\n') if q.strip()]
    except Exception as e:
        print(f"[Expansion] Query expansion failed: {e}")

    return {"expanded_queries": expanded, "re_retrieve_count": count + 1}


# ─────────────────────────────────────────────────────────────
# NODE 3: Retriever (Hybrid + Reranker + Diagnostics + Multi-hop)
# ─────────────────────────────────────────────────────────────
async def retriever_node(state: AgentState):
    """Fetches, reranks, deduplicates chunks. Runs multi-hop for complex queries."""
    query = state["query"]
    files = state.get("files")
    query_type = state.get("query_type", "conceptual")
    expanded_queries = state.get("expanded_queries", [])
    strategy = state.get("retrieval_strategy", {})
    trace = state.get("reasoning_trace", [])

    all_queries = [query] + expanded_queries

    # Multi-hop: decompose complex queries into sub-queries
    if query_type == "multi-hop" and not expanded_queries:
        decompose_prompt = f"""You are a research decomposition engine.
Break the following complex query into 2 simpler, atomic sub-questions that each address a single aspect.
Return ONLY the 2 sub-questions, one per line. No bullets, no numbering, no extra text.
Query: {query}
"""
        try:
            decomposed = await call_llm(decompose_prompt, max_tokens=100)
            sub_queries = [q.strip() for q in decomposed.split('\n') if q.strip()]
            all_queries += sub_queries
            print(f"[Retriever] Multi-hop sub-queries: {sub_queries}")
            trace.append(f"Decomposed multi-hop query into: {sub_queries}")
        except Exception as e:
            print(f"[Retriever] Multi-hop decomposition failed: {e}")

    # Fetch from all queries (deduped by chunk_id)
    all_chunks = []
    seen_chunk_ids = set()
    
    # Adjust top_k if strategy dictates
    k = strategy.get("top_k", 7)
    
    for q in all_queries:
        chunks = await fetch_chunks(q, files, k=k, query_type=query_type, strategy=strategy)
        for c in chunks:
            cid = getattr(c, "chunk_id", None)
            if cid not in seen_chunk_ids:
                all_chunks.append(c)
                if cid:
                    seen_chunk_ids.add(cid)

    if not all_chunks:
        return {"chunks": [], "filtered_chunks": [], "retrieval_quality": "empty", "reasoning_trace": trace}

    # Rerank
    model = get_reranker()
    pairs = [[query, getattr(c, "text", "")] for c in all_chunks]
    scores = model.predict(pairs)

    scored_chunks = list(zip(scores, all_chunks))
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # ── Retrieval Diagnostics (Pre-LLM CRAG) ──
    top_scores = [float(s) for s, _ in scored_chunks[:5]]
    avg_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
    sources = set(getattr(c, "source_title", "") for _, c in scored_chunks[:5])
    
    if avg_score < 0.45 or len(sources) == 1 and len(scored_chunks) > 3:
        quality = "low"
        print(f"[Retriever] Retrieval quality=LOW (avg_score={avg_score:.2f}, sources={len(sources)})")
        trace.append(f"Retrieved {len(all_chunks)} chunks. Quality=LOW (avg={avg_score:.2f}, sources={len(sources)}).")
    else:
        quality = "ok"
        print(f"[Retriever] Retrieval quality=OK (avg_score={avg_score:.2f})")
        trace.append(f"Retrieved {len(all_chunks)} chunks. Quality=OK.")

    # Context deduplication (compression step 1: string similarity)
    top_chunks = []
    seen_texts = []
    for score, chunk in scored_chunks:
        text = getattr(chunk, "text", "")
        if not any(text in s or s in text for s in seen_texts):
            top_chunks.append(chunk)
            seen_texts.append(text)
        if len(top_chunks) >= 5:
            break

    return {"chunks": all_chunks, "filtered_chunks": top_chunks, "retrieval_quality": quality, "reasoning_trace": trace}


# ─────────────────────────────────────────────────────────────
# NODE 4: Context Compressor
# ─────────────────────────────────────────────────────────────
async def compression_node(state: AgentState):
    """Uses LLM to merge retrieved chunks into a dense, non-redundant knowledge block."""
    chunks = state.get("filtered_chunks", [])
    query = state["query"]
    compressed = await compress_context(chunks, query)
    return {"compressed_context": compressed}


# ─────────────────────────────────────────────────────────────
# NODE 5: Summarizer (Answer Generator)
# ─────────────────────────────────────────────────────────────
async def summarizer_node(state: AgentState):
    query = state["query"]
    retry_count = state.get("retry_count", 0)
    compressed = state.get("compressed_context", "")

    # Fall back to raw chunk concat if compressor produced nothing
    if not compressed:
        compressed = "\n\n".join([
            f"SOURCE FILE: {getattr(c, 'source_title', 'Unknown')}\nTEXT:\n{getattr(c, 'text', str(c))}"
            for c in state.get("filtered_chunks", [])
        ])

    prompt = f"""You are an elite AI research assistant. Provide a highly structured, theoretical answer based ONLY on the provided Context.

CRITICAL INSTRUCTIONS:
1. Answer EXCLUSIVELY from the provided Context. Do NOT use outside world knowledge.
2. FORMAT: Use Markdown formatting — `**bold**` for key terms, `- ` for bullet lists, `### ` for sub-headers. Provide detailed, educational theory answers.
3. COMPARATIVE MODE (CRITICAL): If multiple SOURCE FILES define the same concept differently, state those differences FIRST before giving a unified explanation.
4. If the Context does not contain relevant information, respond with exactly: "The provided document does not have content relating to this question."

Return ONLY valid JSON without any markdown code fences:
{{
    "summary": "Your detailed markdown-formatted answer here...",
    "key_points": ["Concise point 1", "Concise point 2", "Concise point 3"],
    "confidence": 0.92
}}

Context:
{compressed}

User Query: {query}
"""

    try:
        response_text = await call_llm(prompt, max_tokens=2048)

        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in LLM response.")

        raw_json = cleaned[start_idx:end_idx]

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            import re
            summary_match = re.search(r'"summary"\s*:\s*"(.*?)"(?=\s*,\s*"key_points")', raw_json, re.DOTALL)
            confidence_match = re.search(r'"confidence"\s*:\s*([\d.]+)', raw_json)
            data = {
                "summary": summary_match.group(1).replace('\\n', '\n') if summary_match else cleaned,
                "key_points": [],
                "confidence": float(confidence_match.group(1)) if confidence_match else 0.5
            }

        confidence = float(data.get("confidence", 0.5))
        return {
            "summary": data.get("summary", "No summary generated."),
            "key_points": data.get("key_points", []),
            "confidence": confidence,
            "retry_count": retry_count + 1
        }
    except Exception as e:
        return {
            "summary": f"Failed to generate answer via LLM: {str(e)}",
            "key_points": [],
            "confidence": 0.0,
            "retry_count": retry_count + 1
        }


# ─────────────────────────────────────────────────────────────
# NODE 6: Verifier (Grounding Score & Adversarial)
# ─────────────────────────────────────────────────────────────
async def verifier_node(state: AgentState):
    from app.services.grounding import calculate_grounding_score, adversarial_verify
    answer = state.get("summary", "")
    context = state.get("compressed_context", "")
    trace = state.get("reasoning_trace", [])
    
    score = await calculate_grounding_score(answer, context)
    print(f"[Verifier] Grounding score = {score:.2f}")
    
    adv_result = await adversarial_verify(answer, context)
    
    trace_msg = f"Verifier: Score={score:.2f}. "
    if adv_result["adversarial_fail"]:
        print(f"[Verifier] Adversarial FAIL: {adv_result['reason']}")
        trace_msg += f"Adversarial FAIL ({adv_result['reason']})"
        score = min(score, 0.4) # artificially lower score to trigger re-retrieval
    else:
        print("[Verifier] Adversarial PASS")
        trace_msg += "Adversarial PASS."
        
    trace.append(trace_msg)
    
    return {"grounding_score": score, "reasoning_trace": trace}

# ─────────────────────────────────────────────────────────────
# NODE 7: Comparator
# ─────────────────────────────────────────────────────────────
async def comparator_node(state: AgentState):
    """Real LLM-powered comparison of definitions across multiple source files."""
    query = state["query"]
    chunks = state.get("filtered_chunks", [])

    if not chunks:
        return {"comparison": None}

    grouped = defaultdict(list)
    for c in chunks:
        grouped[getattr(c, 'source_title', 'Unknown')].append(getattr(c, 'text', ''))

    sources_block = "\n\n".join([
        f"=== {fname} ===\n" + "\n".join(texts)
        for fname, texts in grouped.items()
    ])

    prompt = f"""You are an expert academic comparator. You have been given text excerpts from multiple documents.
Your task: compare how each document defines or discusses the topic in the user's query.

Write a structured paragraph comparison. For each document, state its position. Then summarize the key differences.
Be concise and academic. Do not hallucinate — only use what is in the provided excerpts.

Documents:
{sources_block}

User Query: {query}

Respond with only the comparison text — no JSON, no code blocks.
"""
    try:
        comparison_text = await call_llm(prompt, max_tokens=1024)
        return {"comparison": comparison_text.strip()}
    except Exception as e:
        return {"comparison": f"Comparison generation failed: {str(e)}"}


# ─────────────────────────────────────────────────────────────
# NODE 8: Failure Analysis (Fallback Strategy)
# ─────────────────────────────────────────────────────────────
async def failure_analysis_node(state: AgentState):
    """Analyzes failure and updates retrieval strategy for the next hop."""
    hops = state.get("hop_count", 0)
    strategy = state.get("retrieval_strategy", {})
    trace = state.get("reasoning_trace", [])
    
    # Progressive multi-level fallback strategy
    if hops == 1:
        strategy["action"] = "expand"
        trace.append(f"Hop {hops}: Failure detected. Strategy: Query expansion.")
    elif hops == 2:
        strategy["action"] = "sparse_shift"
        strategy["hybrid_weights"] = (0.2, 0.8) # Shift heavily to sparse
        trace.append(f"Hop {hops}: Failure detected. Strategy: Shift to Sparse BM25.")
    elif hops >= 3:
        strategy["action"] = "broaden"
        strategy["top_k"] = 15 # Increase K
        trace.append(f"Hop {hops}: Failure detected. Strategy: Broaden search (top_k=15).")
        
    print(f"[Failure Analysis] Updated strategy: {strategy}")
    return {"retrieval_strategy": strategy, "reasoning_trace": trace, "hop_count": hops + 1}

# ─────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────
MAX_HOPS = 4

def route_after_retriever(state: AgentState):
    """Pre-LLM CRAG: if retrieval quality is low, re-expand before summarizing."""
    quality = state.get("retrieval_quality", "ok")
    hops = state.get("hop_count", 0)
    
    if quality == "low" and hops < MAX_HOPS:
        print(f"[Router] Retrieval quality low. Hop {hops}/{MAX_HOPS} → failure_analysis.")
        return "analyze_failure"
    return "compress"


def route_after_verifier(state: AgentState):
    """Post-generation routing based on grounding score and confidence."""
    query_lower = state["query"].lower()
    files = state.get("files") or []
    conf = state.get("confidence", 1.0)
    grounding = state.get("grounding_score", 1.0)
    hops = state.get("hop_count", 0)

    # Low grounding or confidence → trigger another hop if under limit
    if (grounding < 0.60 or conf < 0.60) and hops < MAX_HOPS:
        print(f"[Router] Grounding ({grounding:.2f}) or Conf ({conf:.2f}) too low. Hop {hops}/{MAX_HOPS} → failure_analysis.")
        return "analyze_failure"

    # Comparator trigger
    if "compare" in query_lower or "difference" in query_lower or "vs" in query_lower or len(files) > 1:
        return "compare"

    return "end"

# ─────────────────────────────────────────────────────────────
# GRAPH ASSEMBLY
# ─────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("classifier", classifier_node)
workflow.add_node("expansion", expansion_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("compressor", compression_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("verifier", verifier_node)
workflow.add_node("comparator", comparator_node)
workflow.add_node("failure_analysis", failure_analysis_node)

workflow.set_entry_point("classifier")
workflow.add_edge("classifier", "expansion")
workflow.add_edge("expansion", "retriever")
workflow.add_conditional_edges(
    "retriever",
    route_after_retriever,
    {"analyze_failure": "failure_analysis", "compress": "compressor"}
)
workflow.add_edge("compressor", "summarizer")
workflow.add_edge("summarizer", "verifier")
workflow.add_conditional_edges(
    "verifier",
    route_after_verifier,
    {"analyze_failure": "failure_analysis", "compare": "comparator", "end": END}
)
workflow.add_edge("failure_analysis", "expansion")
workflow.add_edge("comparator", END)

app_graph = workflow.compile()

from app.core.logger import get_logger
log = get_logger()

async def run_workflow(query: str, files: list = None) -> AgentState:
    initial_state = {
        "query": query,
        "files": files,
        "query_type": "conceptual",
        "expanded_queries": [],
        "sub_queries": [],
        "chunks": [],
        "filtered_chunks": [],
        "compressed_context": "",
        "retrieval_quality": "ok",
        "summary": "",
        "key_points": [],
        "comparison": None,
        "confidence": 1.0,
        "grounding_score": 1.0,
        "retry_count": 0,
        "re_retrieve_count": 0,
        "hop_count": 1,
        "failure_memory": [],
        "retrieval_strategy": {},
        "reasoning_trace": [f"Start Query: {query}"],
        "final_response": None
    }
    result = await app_graph.ainvoke(initial_state)
    
    # Log the final reasoning trace
    trace = result.get("reasoning_trace", [])
    log.info("Workflow completed", extra_data={"query": query, "trace": trace, "hops": result.get("hop_count")})
    
    return result

