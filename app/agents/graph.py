from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.services.retrieval import fetch_chunks
from app.services.llm import call_llm
import json

reranker_model = None
def get_reranker():
    global reranker_model
    if reranker_model is None:
        from sentence_transformers import CrossEncoder
        reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
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
    # Sort descending by cross-encoder score
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    
    # Pick top 3 for the LLM
    top_chunks = [c for score, c in scored_chunks[:3]]
    return {"chunks": chunks, "filtered_chunks": top_chunks}

async def summarizer_node(state: AgentState):
    query = state["query"]
    context_text = "\n\n".join([getattr(c, 'text', str(c)) for c in state.get("filtered_chunks", [])])
    
    prompt = f"""
    You are an expert AI assistant tasked with answering questions strictly based on the provided Context.
    CRITICAL RULES:
    1. You MUST ONLY use the provided Context to answer the user's query.
    2. If the Context does not contain the answer, or if the Context is completely empty, you MUST respond exactly with the phrase: "The provided document does not have content relating to this question."
    3. DO NOT use your world knowledge to answer the question under any circumstances.
    
    Return your answer strictly in the following JSON format without any markdown blocks or extra text:
    {{
        "summary": "your detailed summary OR the exact failure phrase as instructed above",
        "key_points": ["point 1", "point 2"],
        "confidence": 0.95
    }}

    Context:
    {context_text}

    User Query: {query}
    """
    
    try:
        response_json = await call_llm(prompt)
        start_idx = response_json.find('{')
        end_idx = response_json.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No valid JSON found in LLM response.")
        clean_json = response_json[start_idx:end_idx]
        data = json.loads(clean_json)
        return {
            "summary": data.get("summary", "No summary generated."),
            "key_points": data.get("key_points", []),
            "confidence": float(data.get("confidence", 0.5))
        }
    except Exception as e:
        return {
            "summary": f"Failed to generate answer via LLM: {str(e)}",
            "key_points": [],
            "confidence": 0.0
        }

def comparator_node(state: AgentState):
    return {"comparison": "Comparison Data Table Generated Here"}

def critic_node(state: AgentState):
    return {"confidence": 0.92}

def route_to_comparator(state: AgentState):
    if "compare" in state["query"].lower():
        return "compare"
    return "skip"

def route_on_confidence(state: AgentState):
    conf = state.get("confidence", 1.0)
    retries = state.get("retry_count", 0)
    if conf < 0.75 and retries < 2:
        return "retry"
    return "approve"

workflow = StateGraph(AgentState)

workflow.add_node("retriever", retriever_node)
workflow.add_node("summarizer", summarizer_node)
workflow.add_node("comparator", comparator_node)
workflow.add_node("critic", critic_node)

workflow.set_entry_point("retriever")
workflow.add_edge("retriever", "summarizer")
workflow.add_conditional_edges("summarizer", route_to_comparator, {"compare": "comparator", "skip": "critic"})
workflow.add_edge("comparator", "critic")
workflow.add_conditional_edges("critic", route_on_confidence, {"retry": "summarizer", "approve": END})

app_graph = workflow.compile()

async def run_workflow(query: str) -> AgentState:
    chunks = await fetch_chunks(query, k=10)
    initial_state = {
        "query": query,
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
