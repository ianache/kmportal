#!/bin/bash
# Start script for the Knowledge Management API
# This script uses --app-dir to properly resolve imports

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Default values
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
RELOAD=${RELOAD:-true}

# Run uvicorn with --app-dir to resolve imports correctly
cd "${SCRIPT_DIR}"
echo "Starting Knowledge Management API..."
echo "App directory: ${SCRIPT_DIR}/src"
echo "Host: ${HOST}"
echo "Port: ${PORT}"

if [ "$RELOAD" = "true" ]; then
    uvicorn main:app --app-dir src --reload --host "${HOST}" --port "${PORT}"
else
    uvicorn main:app --app-dir src --host "${HOST}" --port "${PORT}"
fi
