from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent import graph
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn

app = FastAPI(title="Vinmec AI API")

# --- CORS Configuration ---
# Cho phép React (thường chạy ở port 5173 hoặc 3000) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Trong production nên giới hạn lại
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class ChatMessage(BaseModel):
    role: str # "user" hoặc "bot"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "Vinmec AI API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 1. Chuyển đổi history sang định dạng LangChain
        history = []
        for msg in request.history:
            if msg.role == "user" or msg.role == "human":
                history.append(HumanMessage(content=msg.content))
            else:
                history.append(AIMessage(content=msg.content))
        
        # Thêm tin nhắn mới nhất
        history.append(HumanMessage(content=request.message))
        
        # 2. Gọi Agent
        result = graph.invoke({"messages": history})
        response_content = result["messages"][-1].content
        
        return ChatResponse(response=response_content)
    
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
