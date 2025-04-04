from fastapi import FastAPI, Request
from pydantic import BaseModel
from textblob import TextBlob

app = FastAPI()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    return {"message": "This is a test response!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
