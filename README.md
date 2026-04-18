# ✅ Task Manager — FastAPI + Vanilla JS

A full-stack Task Manager web application built with **FastAPI** (backend) and **plain HTML/CSS/JS** (frontend). Features JWT authentication, CRUD task management, pagination, and filtering.

---

## 🌐 Live Demo

> **Deployed at:** `https://your-app.onrender.com`  
> **API Docs:** `https://your-app.onrender.com/docs`

---

## 📁 Project Structure

```
task-manager/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS + static files
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   ├── models.py        # DB models (User, Task)
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── auth.py          # JWT & bcrypt utilities
│   │   ├── dependencies.py  # get_current_user dependency
│   │   └── routes/
│   │       ├── auth.py      # /auth/register  /auth/login
│   │       └── tasks.py     # /tasks CRUD endpoints
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── index.html           # Single-page UI (JS + CSS inline)
├── tests/
│   └── test_tasks.py        # pytest test suite
├── Dockerfile
└── README.md
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable                    | Description                          | Example                    |
|-----------------------------|--------------------------------------|----------------------------|
| `SECRET_KEY`                | JWT signing secret (keep private)    | `supersecretrandomstring`  |
| `ALGORITHM`                 | JWT algorithm                        | `HS256`                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes          | `30`                       |
| `DATABASE_URL`              | SQLAlchemy database URL              | `sqlite:///./taskmanager.db` |

```bash
cp backend/.env.example backend/.env
# Then edit backend/.env with your values
```

---

## 🚀 Running Locally

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/your-username/task-manager.git
cd task-manager

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env — set a strong SECRET_KEY

# 5. Run the server
cd backend
uvicorn app.main:app --reload --port 8000
```

- **Frontend:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

## 🧪 Running Tests

```bash
cd backend
pytest ../tests/ -v
```

---

## 🐳 Docker

```bash
# Build image
docker build -t task-manager .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret \
  -e DATABASE_URL=sqlite:///./taskmanager.db \
  task-manager
```

---

## 📡 API Reference

### Authentication

| Method | Endpoint         | Description              |
|--------|-----------------|--------------------------|
| POST   | `/auth/register` | Register a new user      |
| POST   | `/auth/login`    | Login and receive JWT    |

### Tasks *(JWT required)*

| Method | Endpoint         | Description                       |
|--------|-----------------|-----------------------------------|
| POST   | `/tasks/`        | Create a new task                 |
| GET    | `/tasks/`        | Get all tasks (paginated/filtered)|
| GET    | `/tasks/{id}`    | Get a specific task               |
| PUT    | `/tasks/{id}`    | Update task (title/desc/complete) |
| DELETE | `/tasks/{id}`    | Delete a task                     |

#### Query Parameters for `GET /tasks/`
- `page` — page number (default: 1)
- `page_size` — items per page (default: 10, max: 100)
- `completed` — `true` or `false` to filter by status

---

## 🚢 Deployment (Render)

1. Push your code to GitHub (ensure `.env` is NOT committed)
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your repository
4. Set:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables in the Render dashboard
6. Deploy!

---

## ✅ Features

- JWT authentication (register / login)
- Secure password hashing with bcrypt
- Full task CRUD — create, read, update, delete
- Mark tasks complete / undo completion
- Task filtering (`?completed=true/false`)
- Pagination support
- Users can only access their own tasks
- Interactive Swagger docs at `/docs`
- Pytest test suite
- Docker support
- Responsive single-page frontend
