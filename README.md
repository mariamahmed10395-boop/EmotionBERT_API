# 🧠 DistilBERT Emotion API

A robust, high-performance REST API built with **FastAPI** that integrates a fine-tuned **DistilBERT** Transformer model for emotion classification. This project features a fully functional authentication system (JWT) to secure the ML prediction endpoints.

## ✨ Features
* **AI Emotion Classification:** Uses a fine-tuned DistilBERT model to classify text into 6 emotions (Sadness, Joy, Love, Anger, Fear, Surprise).
* **Secure Authentication:** JWT-based user authentication system.
* **Email Verification:** UUID-based email verification flow for new registrations.
* **Fast & Scalable:** Built with FastAPI, ensuring high performance and automatic interactive API documentation (Swagger UI).

## 🛠️ Tech Stack
* **Machine Learning:** PyTorch, Hugging Face Transformers (DistilBERT), Datasets
* **Backend:** FastAPI, Uvicorn, Python 3.x
* **Security & Auth:** PyJWT, Passlib (Bcrypt)
* **Database:** SQLite / SQLAlchemy (Configurable)

## 🔀 API Endpoints Architecture

Based on the core system design, the API exposes the following endpoints:

| Method | Endpoint | Description | Input (IN) | Output (OUT) |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user | `email`, `password` | `UUID` (Response) |
| `POST` | `/auth/verify-email` | Verify user email | `UUID` | `"Success"` message |
| `POST` | `/auth/login` | Authenticate user | `email`, `password` | `"Success"` + `JWT Token` |
| `POST` | `/ml/classify` | Emotion prediction | `Text` (Requires JWT) | `Category` (e.g., Joy, Anger) |

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/mariamahmed10395-boop/EmotionBERT_API.git](https://github.com/mariamahmed10395-boop/EmotionBERT_API.git)
   cd DistilBERT-Emotion-API