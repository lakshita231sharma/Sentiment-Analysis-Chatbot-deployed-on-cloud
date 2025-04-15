import time
import uuid
import psutil
import traceback
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from textblob import TextBlob
from models import Chat
from database import get_db
from services.autoscaler import create_vm
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# ----- Enable CORS ----- 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Request Model -----
class ChatRequest(BaseModel):
    user_id: str
    message: str

# ----- Root Endpoint -----
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
    # Perform sentiment analysis
    analysis = TextBlob(request.message)
    polarity = analysis.sentiment.polarity
    sentiment_label = (
        "Positive 😊" if polarity > 0
        else "Negative 😞" if polarity < 0
        else "Neutral 😐"
    )

    # Monitor CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"[DEBUG] CPU usage: {cpu_percent}%")

    # Trigger autoscaling if CPU usage is high
    if cpu_percent > 10:
        timestamp = int(time.time())
        vm_name = f"chatbot-vm-{timestamp}"
        print(f"🚨 High CPU: {cpu_percent}% — Creating VM: {vm_name}")
        try:
            result = create_vm(vm_name)
            print(f"[✅] VM creation requested: {vm_name}")
        except Exception as e:
            print("❌ Error creating VM:", str(e))

    # Save chat to database
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
        print("❌ ERROR in /chat route:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

    return {
        "response": sentiment_label
    }

# ----- Chat History Endpoint -----
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
        print(f"[TEST] Manually triggering VM creation: {instance_name}")
        result = create_vm(instance_name)
        return {"status": "success", "vm_name": instance_name, "operation": str(result)}
    except Exception as e:
        print("❌ Error in test-autoscale:", str(e))
        return {"status": "error", "details": str(e)}
