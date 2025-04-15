from locust import HttpUser, task, between
import uuid

class ChatbotUser(HttpUser):
    wait_time = between(1, 2)
    host = "https://sentiment-analysis-chatbot-k5q8.onrender.com"  # 👈 Use your cloud URL

    @task
    def send_message(self):
        payload = {
            "user_id": str(uuid.uuid4()),
            "message": "Hey! I need a room in the hostel."
        }
        with self.client.post("/chat", json=payload, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status {response.status_code}: {response.text}")
