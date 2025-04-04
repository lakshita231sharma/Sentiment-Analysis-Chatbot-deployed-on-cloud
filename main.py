from fastapi import FastAPI, Request
from pydantic import BaseModel
from textblob import TextBlob
import os
import uvicorn

app = FastAPI()

# Store chat history (context) for each user
user_context = {}

# Define a request model
class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    message = data.get("message")

    # Sentiment Analysis
    sentiment_score = TextBlob(message).sentiment.polarity
    if sentiment_score > 0:
        mood = "happy"
    elif sentiment_score < 0:
        mood = "sad"
    else:
        mood = "neutral"

    # Context Management
    if user_id not in user_context:
        user_context[user_id] = []

    user_context[user_id].append(message)

    # Example response with context and mood
    if "pizza" in message.lower():
        response = f"Sure! What toppings would you like? (I can tell you're feeling {mood}!)"
    elif "thanks" in message.lower():
        response = "You're welcome! 😊"
    else:
        response = f"I remember you said: {', '.join(user_context[user_id])}. You seem {mood}."

    return {"response": response}

# Run the app (Make it compatible with cloud deployments)
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Get port from environment or use default
    uvicorn.run(app, host="0.0.0.0", port=port)
