import time
import uuid
import psutil
from fastapi import FastAPI, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from textblob import TextBlob
from datetime import datetime
from models import Chat
from database import get_db
from services.autoscaler import create_vm

app = FastAPI()

# ----- Request Model -----
class ChatRequest(BaseModel):
    user_id: str
    message: str

# ----- Root -----
@app.get("/")
async def root():
    return {"message": "Hello! Chatbot is running 🚀"}

# ----- Chat Endpoint -----
@app.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    # Sentiment analysis
    analysis = TextBlob(request.message)
    polarity = analysis.sentiment.polarity
    sentiment_label = (
        "Positive 😊" if polarity > 0
        else "Negative 😞" if polarity < 0
        else "Neutral 😐"
    )

    # Autoscaling if CPU usage > 75%
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > 75:
        print(f"🚨 High CPU usage detected: {cpu_percent}% — Creating new VM!")
    timestamp = int(time.time())
    vm_name = f"chatbot-vm-{timestamp}"
    create_vm(vm_name)

    # Save to DB
    try:
        new_chat = Chat(
            user_id=request.user_id,
            message=request.message,
            sentiment=sentiment_label
        )
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
    except Exception as e:
        await db.rollback()
        return {"error": "Database error", "details": str(e)}

    return {
        "user_id": request.user_id,
        "message": request.message,
        "sentiment": sentiment_label
    }

# ----- Chat History -----
@app.get("/history/{user_id}")
async def get_history(user_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.user_id == user_id))
    chats = result.scalars().all()
    return [
        {
            "message": chat.message,
            "sentiment": chat.sentiment,
            "timestamp": chat.timestamp
        }
        for chat in chats
    ]

# ----- Manual Autoscaling Trigger -----
@app.get("/test-autoscale")
async def test_autoscale():
    try:
        instance_name = f"chatbot-instance-{uuid.uuid4().hex[:6]}"
        result = create_vm(instance_name)
        return {"status": "success", "operation": result}
    except Exception as e:
        return {"status": "error", "details": str(e)}
