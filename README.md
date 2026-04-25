# 🤖 IA Service (FastAPI) – Project Documentation

## 📌 Overview

This service is the **AI (Intelligence) backend** of the system.
It is responsible for:

* 🎯 Face recognition processing
* 📷 Capturing frames from cameras (IP camera or USB camera)
* 🔍 Matching detected faces with stored user data
* 🔗 Sending recognition results to the Express backend

This service is part of a **multi-container Docker architecture** inside the main project:

```id="kz3q1m"
gestAbss/
├── backend         # Express.js API
├── ia              # FastAPI AI service (this service)
├── mobile_app      # Mobile client
└── docker-compose.yml
```

---

## ⚠️ Environment Setup (VERY IMPORTANT)

Before running the project, each team member **must create their own `.env` file**.

### ✅ Step:

Inside the `ia` folder:

```bash 
cp .env.example .env
```

Then update values if needed.

👉 Without this step, the service **will not connect to the database**.

---

## 🏗️ Project Structure

```
ia/
├── Dockerfile
├── main.py
├── requirements.txt
├── src
│   ├── controllers
│   ├── core
│   │   └── database.py
│   ├── models
│   ├── routes
│   │   └── base.py
│   ├── schemas
│   └── utils
└── uploads
```

---

## ⚙️ How It Works

### 🔄 Workflow

1. 📷 Camera (IP or USB) captures frames
2. 🤖 IA service processes the image
3. 🔍 Face recognition is performed
4. 📤 Result is sent to Express backend
5. 📊 Express handles attendance / logic

---

## 🐳 Docker Integration

All services run together using Docker.

### 🔗 Connected Services

| Service         | Role             | Hostname  |
| --------------- | ---------------- | --------- |
| PostgreSQL      | Database         | `db`      |
| Express Backend | Main API         | `backend` |
| IA Service      | Face recognition | `ia`      |

---

## 🌐 Inter-Container Communication

Docker provides internal networking:

* Use **service names as hostnames**
* Never use `localhost` inside containers

### Example:

```env 
DATABASE_URL=postgresql+psycopg2://mobile:password@db:5432/mobile_back_express
```

👉 `db` = PostgreSQL container

---

## 🚀 Running the Project

From the root folder (`your route folder`):

```bash
docker-compose up --build
```

---

## 📡 Access

* FastAPI:

```
http://localhost:8000
```

* Swagger Docs:
* 
```
http://localhost:8000/docs
```

---

## 🧠 Database

Configured in:

```
src/core/database.py
```

Uses:

* SQLAlchemy
* PostgreSQL
* Connection pooling

---

## 📡 API Routes

Defined in:

```
src/routes/*.py
```

Examples:

* `/health` → services status
---

## 📷 Face Recognition Logic

Located in:

```
src/controllers/
```

Handles:

* Image processing
* Face matching
* Result formatting

---

## 🔁 Communication with Express Backend

After matching:

* IA sends result to Express backend
* Express processes attendance logic

---

## 🧪 Logs & Debugging

View logs:

```bash
docker logs <ia_container_name>
```

---

## ⚠️ Important Notes

* Always copy `.env.example` → `.env` before running
* Use `db` as database host (NOT localhost)
* Ensure PostgreSQL container is running
* Use absolute imports (`from src...`)
* Do not commit `.env` files

---

## 👥 Team Workflow

1. Clone repository
2. Setup env files:

   ```bash
   cp ia/.env.example ia/.env
   ```
3. Run project:

   ```bash
   docker-compose up --build
   ```
4. Start developing 🚀

---

## 📦 Requirements

Defined in:

```
requirements.txt
```

Main dependencies:

* fastapi
* uvicorn
* sqlalchemy
* psycopg2-binary

---

## ✅ Summary

This IA service:

* Handles face recognition
* Connects to PostgreSQL
* Communicates with Express backend
* Runs fully inside Docker
* Ready for team collaboration
