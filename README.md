# 🎓 Student Management App

FastAPI + MongoDB (Atlas) backend with a plain HTML/CSS/JS frontend.

## Project Structure

```
student-mgmt/
├── backend/
│   ├── main.py              # FastAPI app — all routes
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Copy → .env and fill in MONGO_URI
└── frontend/
    ├── pages/
    │   ├── index.html       # Page 1 – Home (list all students)
    │   ├── add.html         # Page 2 – Add student form
    │   └── edit.html        # Page 3 – Edit / Delete student
    ├── css/
    │   └── style.css        # Shared styles
    └── js/
        └── api.js           # Fetch helpers + toast + query-param utils
```

## API Endpoints

| Method | Path                  | Description          |
|--------|-----------------------|----------------------|
| GET    | /students             | List all students    |
| GET    | /students/{id}        | Get one student      |
| POST   | /students             | Create a student     |
| PUT    | /students/{id}        | Update a student     |
| DELETE | /students/{id}        | Delete a student     |

## Setup & Run

### 1. MongoDB Atlas
1. Create a free cluster at https://cloud.mongodb.com
2. Create a database user and whitelist your IP
3. Copy the connection string

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from template and paste your connection string
cp .env.example .env

uvicorn main:app --reload
# API is now at http://127.0.0.1:8000
# Swagger docs at http://127.0.0.1:8000/docs
```

> **Important**: `main.py` reads `MONGO_URI` from the `.env` file via `os.getenv()`.
> Make sure your `.env` has the correct value before starting the server.

### 3. Frontend
Open `frontend/pages/index.html` directly in your browser, or serve it with any static server:

```bash
# Quick option (Python)
cd frontend
python -m http.server 5500
# Open http://localhost:5500/pages/index.html
```

The frontend talks to `http://127.0.0.1:8000` by default. If you change the backend port, update `API_BASE` in `frontend/js/api.js`.