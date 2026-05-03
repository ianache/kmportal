"""Entry point for running the API with proper PYTHONPATH setup.

This module ensures the src directory is in the Python path before importing
application modules. This fixes the 'ModuleNotFoundError' when running uvicorn
directly.

Usage:
    python -m start
    
Or:
    python start.py
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now import and run the application
from src.main import app

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"Starting Knowledge Management API...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Python path: {sys.path[0]}")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload
    )
