from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.services.retrieval import fetch_chunks
from app.services.llm import call_llm
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


def retriever_node(state: AgentState):
    query = state["query"]
    chunks = state.get("chunks", [])
    if not chunks:
        return {"chunks": chunks, "filtered_chunks": []}

    model = get_reranker()
    pairs = [[query, getattr(c, "text", "")] for c in chunks]
    scores = model.predict(pairs)

    scored_chunks = list(zip(scores, chunks))
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # Top 5 for the LLM (increased from 3 for richer context)
    top_chunks = [c for _, c in scored_chunks[:5]]
    return {"chunks": chunks, "filtered_chunks": top_chunks}


async def summarizer_node(state: AgentState):
    query = state["query"]
    retry_count = state.get("retry_count", 0)

    context_text = "\n\n".join([
        f"SOURCE FILE: {getattr(c, 'source_title', 'Unknown')}\nTEXT:\n{getattr(c, 'text', str(c))}"
        for c in state.get("filtered_chunks", [])
    ])

    prompt = f"""
You are an elite AI research assistant. Provide a highly structured, theoretical answer based ONLY on the provided Context.

CRITICAL INSTRUCTIONS:
1. Answer EXCLUSIVELY from the provided Context. Do NOT use outside world knowledge.
2. FORMAT: Use Markdown formatting — `**bold**` for key terms, `- ` for bullet lists, `### ` for sub-headers. Provide detailed, educational theory answers.
3. COMPARATIVE MODE (CRITICAL): If multiple SOURCE FILES define the same concept differently, state those differences FIRST before giving a unified explanation. Example: "**According to Grammar.pdf**, X is defined as... However, **Linguistics.pdf** defines it as..."
4. If the Context does not contain relevant information, respond with exactly: "The provided document does not have content relating to this question."

Return ONLY valid JSON without any markdown code fences:
{{
    "summary": "Your detailed markdown-formatted answer here...",
    "key_points": ["Concise point 1", "Concise point 2", "Concise point 3"],
    "confidence": 0.92
}}

Context:
{context_text}

User Query: {query}
"""

    try:
        response_text = await call_llm(prompt, max_tokens=2048)
        
        # Strip markdown code fences if LLM wrapped the JSON in ```json ... ```
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()
        
        # Find the outermost JSON object
        start_idx = cleaned.find('{')
        end_idx = cleaned.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in LLM response.")
        
        raw_json = cleaned[start_idx:end_idx]
        
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            # Fallback: use regex to extract fields individually
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


async def comparator_node(state: AgentState):
    """Real LLM-powered comparison of definitions across multiple source files."""
    query = state["query"]
    chunks = state.get("filtered_chunks", [])

    if not chunks:
        return {"comparison": None}

    # Group chunk text by source file for a clean side-by-side prompt
    grouped = defaultdict(list)
    for c in chunks:
        grouped[getattr(c, 'source_title', 'Unknown')].append(getattr(c, 'text', ''))

    sources_block = "\n\n".join([
        f"=== {fname} ===\n" + "\n".join(texts)
        for fname, texts in grouped.items()
    ])

    prompt = f"""
You are an expert academic comparator. You have been given text excerpts from multiple documents.
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


def route_after_summarizer(state: AgentState):
    """Single routing function from summarizer — handles compare, retry, and approve."""
    query_lower = state["query"].lower()
    files = state.get("files") or []
    conf = state.get("confidence", 1.0)
    retries = state.get("retry_count", 0)

    # Low confidence: retry (max 2 times)
    if conf < 0.60 and retries < 2:
        return "retry"

    # Comparator trigger: multi-file selection or compare keyword
    if "compare" in query_lower or "difference" in query_lower or "vs" in query_lower or len(files) > 1:
        return "compare"

    return "end"


workflow = StateGraph(AgentState)

workflow.add_node("retriever", retriever_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("comparator", comparator_node)

workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "summarizer")
workflow.add_conditional_edges(
    "summarizer",
    route_after_summarizer,
    {"retry": "summarizer", "compare": "comparator", "end": END}
)
workflow.add_edge("comparator", END)

app_graph = workflow.compile()


async def run_workflow(query: str, files: list = None) -> AgentState:
    chunks = await fetch_chunks(query, files, k=10)
    initial_state = {
        "query": query,
        "files": files,
        "sub_queries": [],
        "chunks": chunks,
        "filtered_chunks": [],
        "summary": "",
        "key_points": [],
        "comparison": None,
        "confidence": 1.0,
        "retry_count": 0,
        "final_response": None
    }
    result = await app_graph.ainvoke(initial_state)
    return result
