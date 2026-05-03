# Knowledge Management API

Core API for the Knowledge Management Center built with FastAPI.

## Quick Start

### Option 1: Using UV Scripts (Recommended)

If you have `uv` installed:

```bash
# Development mode with auto-reload
uv run dev

# Production mode
uv run start
```

### Option 2: Using Start Scripts

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### Option 3: Direct Uvicorn (requires --app-dir)

```bash
cd api
uvicorn main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

**Important**: You MUST use `--app-dir src` flag so uvicorn can find the modules correctly.

### Option 4: Python Module

```bash
cd api
python start.py
```

## Common Issues

### ModuleNotFoundError: No module named 'db'

This error occurs when Python can't find the local modules. Solutions:

1. **Use the provided scripts**: They handle the path configuration automatically
2. **Use --app-dir flag**: Always include `--app-dir src` when running uvicorn directly
3. **Install in editable mode**: Run `uv pip install -e "."` from the api directory

### Docker

```bash
docker build -t knowledge-api .
docker run -p 8000:8000 knowledge-api
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
GEMINI_API_KEY=your_key_here
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
