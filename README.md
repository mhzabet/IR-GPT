
# IR-GPT 🤖  
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-5.x-green?style=flat&logo=django)](https://www.djangoproject.com/) ![Django Channels](https://img.shields.io/badge/Django%20Channels-3.x-0A66C2?style=flat&logo=django) ![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-FF6C37?style=flat&logo=websocket) [![React](https://img.shields.io/badge/React-18-blue?style=flat&logo=react)](https://react.dev/) ![Celery](https://img.shields.io/badge/Celery-Enabled-37814A?style=flat&logo=celery) ![Redis](https://img.shields.io/badge/Redis-Enabled-DC382D?style=flat&logo=redis) [![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat&logo=docker)](https://www.docker.com/)  [![OpenAI](https://img.shields.io/badge/OpenAI-API-black?style=flat&logo=openai)](https://openai.com/)  

---

## 📌 Overview
IR-GPT is an **AI-powered chatbot for Persian speakers**, built on **OpenAI API**. It provides a ChatGPT-like experience fully optimized for **Farsi** with a responsive and modern UI.

---

## ✅ Features
- Chat in **Persian** (and multi-language support)
- Save **conversation history**
- User authentication (**JWT or Session-based**)
- Adjustable model settings (temperature, max tokens)
- Modern **React UI** with TailwindCSS

---

## 🛠 Tech Stack
**Backend:**
- Django 5.x
- Django Rest Framework
- Django Channels (realtime)
- PostgreSQL
- Celery + Redis (async tasks)

**Frontend:**
- React 18
- Tailwind CSS
- Axios

**Others:**
- OpenAI GPT API (Free)
- Docker for containerization

---

## 📦 Installation & Setup

## ⚙️ Environment Variables
Create a `.env` file inside **backend/** and add:

| Variable         | Description                | Example                        |
|------------------|----------------------------|--------------------------------|
| `OPENAI_API_KEY` | Your OpenAI API Key        | ``                             |
| `DEBUG`          | Django Debug Mode          | `True` or `False`              |
| `DATABASE_URL`   | PostgreSQL Connection      | `postgres://user:pass@host/db` |

---

## 🏗 Project Structure
```
ir-gpt/
│
├── backend/
│   ├── manage.py
│   ├── ir_gpt/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── api/
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── tasks.py
│
└── frontend/
    ├── src/
        ├── components/
        ├── pages/
        ├── services/
```

---


## 🧪 Running Tests


---

## 🐳 Docker Setup


---

## 👨‍💻 Contribution Guide
We welcome contributions!  
1. Fork the project
2. Create a branch:  


## 📸 Screenshots

**Demo GIF:**  

---

## 🔐 Security Notes
- Keep your `OPENAI_API_KEY` secret
- Implement **Rate Limiting** to avoid abuse

---

## 📄 License
This project is licensed under the **MIT License**.

---
