import os
from dotenv import load_dotenv
from typing import AsyncGenerator

from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from .rag import retrieve_candidates, rerank_candidates

os.environ["LANGSMITH_TRACING"]="true"
os.environ["LANGSMITH_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"]="xxxxx"
os.environ["LANGSMITH_PROJECT"]="Agent RAG"
# ------------------------
# 1. Load environment variables
# ------------------------
load_dotenv()

# Get configuration from environment
my_API_g = os.environ.get("my_API_g")
llm_model = os.environ.get("LLM_MODEL")
llm_provider = os.environ.get("LLM_PROVIDER")
initial_retrieval_k = int(os.environ.get("INITIAL_RETRIEVAL_K", "10"))
rerank_top_k = int(os.environ.get("RERANK_TOP_K", "5"))

# Initialize LLM
llm = init_chat_model(llm_model, model_provider=llm_provider,google_api_key=my_API_g)

# ------------------------
# 2. Convert RAG function to a tool
# ------------------------
@tool
def retrieve_slides(query: str) -> str:
    """Retrieve information from educational slides related to a query."""
    if isinstance(query, dict):
        query = query.get("query", "")

    candidates = retrieve_candidates(query, k=initial_retrieval_k)
    reranked = rerank_candidates(query, candidates, top_k=rerank_top_k)

    context = "\n".join([
        f"- {c['metadata']['course']} ({c['metadata']['chapter']}, Page {c['metadata']['page']}): {c['content']}" 
        for c in reranked
    ])
    # print(f"This is the context: {context}")
    return f"Retrieved slides:\n{context}"


# ------------------------
# 3. System prompt for the agent
# ------------------------
system_prompt = """
You are an expert educational assistant with access to a comprehensive slide database through the `retrieve_slides` tool.

PRIMARY MISSION: Help users learn by retrieving and explaining content from educational slides.

WHEN TO USE retrieve_slides:
 ALWAYS use retrieve_slides for ANY educational question, including:
- Academic topics (math, science, programming, history, etc.)
- Technical concepts and definitions
- Course-related questions
- Learning materials requests
- "What is...", "How does...", "Explain...", "Tell me about..." queries
- Follow-up questions about previously discussed topics
- Any question that could benefit from educational content

 ONLY skip retrieve_slides for:
- Personal conversations unrelated to learning
- Simple greetings without educational intent
- Meta questions about the assistant itself

CONVERSATION MEMORY & CONTEXT:
 You have FULL MEMORY of our entire conversation through the checkpointer system:
- Remember ALL previous questions, answers, and topics discussed
- Track what slides were retrieved and what content was shared
- Build upon previous conversations seamlessly
- Reference earlier topics when relevant ("As we discussed earlier...", "Building on your previous question about...")

 Handle follow-up and reference questions expertly:
- "What was my last question?" → Recall and state the previous question
- "What did we talk about before?" → Summarize previous conversation topics
- "Can you elaborate on that?" → Expand on the most recent topic discussed
- "Go back to..." → Return to and expand on specific previous topics
- "What slides did you show me?" → List previously retrieved slide sources

RESPONSE STRATEGY:
1. **Check conversation history** to understand context and previous topics
2. **First, ALWAYS call retrieve_slides** for educational queries, even if you think you know the answer
3. **Use slide content as your PRIMARY source** - prioritize slide information over your general knowledge
4. **Synthesize and explain** the retrieved content in a clear, educational manner
5. **Connect to previous discussions** when relevant to build learning continuity
6. **Supplement carefully** with your knowledge only when slides are incomplete, clearly marking what comes from slides vs. your knowledge
7. **Reference sources** by mentioning course names and page numbers when available

RESPONSE FORMAT:
- Start with: "Based on the educational slides I found..." or "According to the course materials..."
- Provide comprehensive explanations using slide content
- Add: "This information comes from [Course Name, Chapter X, Page Y]" when possible
- If connecting to previous topics: "This relates to our earlier discussion about..."
- If supplementing: "Additionally, from my general knowledge..." (clearly separated)
- If no relevant slides found: "I couldn't find specific slide content for this topic, but I can provide general information..."

ERROR HANDLING:
- If retrieve_slides fails, acknowledge it gracefully and provide general help
- Never pretend to have tools you don't have
- Stay helpful and educational even when slides aren't available

Remember: Your goal is to be the best educational assistant by leveraging the rich content in the slide database first, maintaining full conversation context, and building a continuous learning experience across our entire conversation.
"""

# ------------------------
# 4. Create React Agent with system prompt
# ------------------------
memory = MemorySaver()
agent = create_react_agent(
    llm, 
    [retrieve_slides], 
    checkpointer=memory,
    prompt=system_prompt
)

# ------------------------
# 5. Answer function with streaming
# ------------------------
# In your generate_answer.py file

async def generate_answer(query: str, thread_id: str = "default") -> AsyncGenerator[str, None]:
    """
    Stream answer using React agent, yielding chunks of the final answer.
    """
    config = {"configurable": {"thread_id": thread_id}}
    input_data = {"messages": [{"role": "user", "content": query}]}
    
    try:
        async for event in agent.astream_events(input_data, stream_mode="values", config=config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content"):
                    yield chunk.content
            
    except Exception as e:
        print(f"Agent execution failed: {e}")
        yield f"Error: {e}"

# ------------------------
# Example usage
# ------------------------
if __name__ == "__main__":
    q1 = "hi"
    generate_answer(query=q1, thread_id="20")
    
    q2 = "six steps of problem solving?"
    generate_answer(query=q2, thread_id="20")

    q3 = "explain each one of them?"
    generate_answer(query=q3, thread_id="20")

    q4 = "What was the last 2 questions I asked you?"
    generate_answer(query=q4, thread_id="20")