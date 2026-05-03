#!/bin/bash
# Start script for the Knowledge Management API
# This script ensures PYTHONPATH is set correctly for imports

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set PYTHONPATH to include the src directory
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
RELOAD=${RELOAD:-true}

# Run uvicorn with the correct module path
cd "${SCRIPT_DIR}"
if [ "$RELOAD" = "true" ]; then
    uvicorn src.main:app --reload --host "${HOST}" --port "${PORT}"
else
    uvicorn src.main:app --host "${HOST}" --port "${PORT}"
fi
