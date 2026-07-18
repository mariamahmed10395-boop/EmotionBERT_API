# 🧠 DistilBERT Emotion API

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.x](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange)
![Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97_Hugging_Face-Transformers-yellow)

A robust, high-performance REST API built with **FastAPI** that integrates a fine-tuned **DistilBERT** Transformer model for emotion classification. This project features a fully functional authentication system (JWT) to secure the ML prediction endpoints.

## ✨ Features
* **AI Emotion Classification:** Uses a fine-tuned DistilBERT model to classify text into 6 emotions (Sadness 😢, Joy 😃, Love 🥰, Anger 😠, Fear 😨, Surprise 😲).
* **Secure Authentication:** JWT-based user authentication system.
* **Email Verification:** UUID-based email verification flow for new registrations.
* **Fast & Scalable:** Built with FastAPI, ensuring high performance and automatic interactive API documentation (Swagger UI).
* **Local Database:** Uses SQLite and SQLAlchemy for easy and standalone database management.

## 🛠️ Tech Stack
* **Machine Learning:** PyTorch, Hugging Face Transformers (DistilBERT), Datasets
* **Backend:** FastAPI, Uvicorn, Python 3.x
* **Security & Auth:** PyJWT, Passlib, bcrypt, python-multipart
* **Database:** SQLite / SQLAlchemy

## 🔀 API Endpoints Architecture

Based on the core system design, the API exposes the following endpoints:

| Method | Endpoint | Description | Input (Body/Form/Query) | Output (JSON) |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | Register a new user | `{"email": "...", "password": "..."}` | `message`, `verification_token` |
| `POST` | `/auth/verify-email` | Verify user email | `token` (Query param) | `message` |
| `POST` | `/auth/login` | Authenticate user | `username`, `password` (Form data) | `access_token`, `token_type` |
| `POST` | `/ml/classify` | Emotion prediction | `text` (Query param) + JWT Header | `Category`, `Confidence` |

## 🚀 How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/mariamahmed10395-boop/EmotionBERT_API.git
cd EmotionBERT_API
```

### 2. Create a Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
Make sure you have the required packages installed. Run the following command:
```bash
pip install fastapi uvicorn sqlalchemy bcrypt pyjwt transformers torch pydantic[email] python-multipart
```

### 4. Run the API Server
Navigate to the folder containing `main.py` and start the server:
```bash
cd DistilBERT
uvicorn main:app --reload
```

### 5. Access the API
* **Swagger UI (Interactive API Docs):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## 📖 Usage Examples

### Register a User
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "user@example.com",
  "password": "strongpassword123"
}'
```

### Verify Email
Copy the `verification_token` from the registration response and verify the account:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/verify-email?token=YOUR_VERIFICATION_TOKEN' \
  -H 'accept: application/json'
```

### Login to Get JWT Token
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user%40example.com&password=strongpassword123'
```

### Predict Emotion
Use the `access_token` from the login response to classify text:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/ml/classify?text=I%20am%20so%20happy%20today!' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'
```

## 📂 Project Structure
```text
EmotionBERT_API/
├── DistilBERT/
│   ├── distilbert_emotion_model/ # Fine-tuned DistilBERT model weights
│   ├── Fine_Tunning.ipynb        # Jupyter notebook for model fine-tuning
│   ├── main.py                   # FastAPI application & endpoints
│   └── users.db                  # SQLite database for users
├── LICENSE                       # Project License
└── README.md                     # Project documentation
```

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.