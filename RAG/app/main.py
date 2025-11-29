from fastapi import FastAPI
from Backend.app.rag.generate_answer import generate_answer 
app= FastAPI()

@app.post("/ask")
def ask_question(q: str , thread_id: str = "default"):
    print("user Qe", q)
    answer = generate_answer(q ,thread_id)  # ✅ pass string, not dict
    print("answer", answer)
    return {"result": answer}
#uvicorn main:app --reload 
