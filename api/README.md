# Knowledge Management API

Core API for the Knowledge Management Center built with FastAPI.

## ⚠️ IMPORTANT: How to Run

The API uses absolute imports (e.g., `from db.database import ...`) which require proper path configuration.

### ✅ CORRECT Ways to Run

#### Option 1: Using the start script (Recommended)
```bash
cd api
python start.py
```

#### Option 2: Using start.bat (Windows)
```cmd
cd api
start.bat
```

#### Option 3: Direct Uvicorn with --app-dir
```bash
cd api
uvicorn main:app --app-dir src --reload --host 0.0.0.0 --port 8000
```

**CRITICAL**: Notice `--app-dir src` - this tells uvicorn to look for modules in the `src/` directory.

### ❌ INCORRECT (Will Fail)

```bash
# WRONG - Don't do this!
uvicorn src.main:app --reload  # ❌ ModuleNotFoundError

# WRONG - Don't do this!  
uv run uvicorn src.main:app --reload  # ❌ ModuleNotFoundError
```

## Why This Happens

The project structure is:
```
api/
├── src/
│   ├── main.py
│   ├── db/
│   ├── api/
│   └── ...
```

When you run `uvicorn src.main:app`, Python tries to import `src.main` and then `src` becomes the top-level package. But the code uses imports like `from db.database import ...` expecting `db` to be at the top level.

Using `--app-dir src` tells uvicorn: "Look for `main:app` inside the `src/` directory", making the imports work correctly.

## Quick Start

### 1. Install Dependencies

```bash
cd api
uv pip install -e ".[dev]"
```

Or with pip:
```bash
cd api
pip install -e ".[dev]"
```

### 2. Set Up Environment

Copy the example environment file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run the API

```bash
python start.py
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Development Commands

```bash
# Run with auto-reload
python start.py

# Run linting
ruff check src/

# Run type checking
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## Docker

Build and run with Docker:

```bash
# Build
docker build -t knowledge-api .

# Run
docker run -p 8000:8000 --env-file .env knowledge-api
```

## Troubleshooting

### ModuleNotFoundError: No module named 'db'

**Cause**: Running uvicorn without `--app-dir src` or not using the start script.

**Fix**: Use one of the ✅ CORRECT methods above.

### Import errors for other modules (api, core, mcp, etc.)

Same issue - use `--app-dir src` or the start script.

### "No module named 'src'"

You may have run `uvicorn src.main:app` from inside the `src/` directory. Run it from the `api/` directory instead.

## Environment Variables

Required variables (see `.env.example` for full list):

- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - For embeddings (optional for development)
- `KEYCLOAK_URL` - Authentication server (optional for development)

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

## Project Structure

```
api/
├── src/
│   ├── main.py           # FastAPI app entry point
│   ├── api/              # REST API routes
│   ├── core/             # Core utilities, logging, auth
│   ├── db/               # Database configuration
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── adapters/         # External service adapters
│   ├── ports/            # Abstract interfaces
│   └── mcp/              # MCP server for AI agents
├── tests/                # Test files
├── start.py             # Entry point script
├── start.bat            # Windows batch script
├── start.sh             # Unix shell script
└── pyproject.toml       # Project configuration
```
