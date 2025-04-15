# 💬 Cloud-Based Sentiment Analysis Chatbot with Autoscaling

This project is a cloud-deployed, sentiment-aware chatbot built with FastAPI. 
It analyzes user input, stores conversations in a PostgreSQL database, and auto-scales by provisioning new VM instances on Google Cloud based on CPU usage.

## 🚀 Features

- ⚡ FastAPI-based chatbot backend
- 😊 Sentiment analysis using TextBlob
- 🗄️ Persistent message storage in PostgreSQL (Render)
- 📈 CPU-based autoscaler using `psutil` and GCP Compute Engine
- ☁️ On-demand VM provisioning using Google Cloud API
- 📊 Full conversation history per user

## 🧱 Tech Stack

- **Backend**: Python, FastAPI
- **Sentiment Analysis**: TextBlob
- **Database**: PostgreSQL (Render)
- **Cloud Provider**: Google Cloud Platform (GCP)
- **Infrastructure Monitoring**: psutil
- **GCP SDK**: `google-api-python-client`, `google-auth`


