# Simple Social

A minimal social app with:
- FastAPI backend (JWT auth via fastapi-users, posts feed, upload, delete)
- Streamlit frontend (login/sign-up, upload, feed)
- ImageKit for media storage and delivery

## Tech stack
- Python 3.11
- FastAPI, fastapi-users, SQLAlchemy
- Streamlit
- ImageKit (imagekitio)
- python-dotenv

## Project structure
```
fp/
├─ app/
│  ├─ app.py            # FastAPI app (module path likely: app.app:app)
│  ├─ db.py             # DB models/session
│  ├─ users.py          # fastapi-users config (JWT)
│  ├─ schemas.py        # Pydantic schemas
│  ├─ images.py         # ImageKit SDK client
│  ├─ frontend.py       # Streamlit UI
│  └─ __pycache__/
└─ ...
```

## Prerequisites
- Python 3.11.x
- An ImageKit account (for public_key, private_key, and url_endpoint)

## Setup (Windows PowerShell)

1) Clone and enter the project directory:
```powershell
git clone <your-repo-url> fp
cd fp
```

2) Create and activate a virtual environment:
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Install dependencies

Using uv (recommended):
```powershell
# If uv is not installed: pip install uv
uv sync
# If you need to add ImageKit SDK explicitly:
uv add imagekitio
```

Using pip:
```powershell
pip install fastapi uvicorn[standard] fastapi-users[sqlalchemy] sqlalchemy python-dotenv streamlit requests imagekitio
```

4) Configure environment variables  
Create a `.env` file in the project root:
```env
# ImageKit
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_URL=https://ik.imagekit.io/your_imagekit_id

# Optional: database URL if your db.py reads it (e.g., SQLite/Postgres)
# DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/dbname
```

Important: In `app/users.py`, `SECRET` is currently hardcoded. Replace `"YOUR_SECRET_KEY_HERE"` with a strong secret (or refactor to read from an env var).

## Run

Terminal 1 — start the API:
```powershell
# Adjust module path if needed (module:variable)
uvicorn app.app:app --reload --port 8000
```

Terminal 2 — start the Streamlit frontend:
```powershell
streamlit run app/frontend.py
```

Frontend will call the backend at `http://localhost:8000`.

## API overview (used by the frontend)
- POST /auth/jwt/login — form data: username, password
- POST /auth/register — json: { email, password }
- GET  /users/me — bearer token required
- POST /upload — multipart form: file + caption
- GET  /feed — returns { posts: [...] }
- DELETE /posts/{id} — owner-only

## Troubleshooting
- Package name: the ImageKit Python SDK on PyPI is `imagekitio` (not `imagekit`).
```powershell
uv add imagekitio
# or
pip install imagekitio
```
- uv flag usage: pass flags to the command, e.g. `uv add imagekitio --frozen` (do not run `--frozen` alone).
- Python version: use Python 3.11. If a resolver complains about unsupported versions, constrain Python in your pyproject (`requires-python = ">=3.11, <3.14"`).

## License
Add a license file if you plan to open source this project.
