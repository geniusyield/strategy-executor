#!/bin/bash
echo "=====[TRADING STRATEGY EXECUTOR]====="
echo "Startup checks...."
if [ -z "$BACKEND_URL" ]; then
    echo "Error: BACKEND_URL environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
if [ -z "$SERVER_API_KEY" ]; then
    echo "Error: SERVER_API_KEY environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
if [ -z "$EXECUTION_DELAY" ]; then
    echo "Error: EXECUTION_DELAY environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
if [ -z "$STARTUP_DELAY" ]; then
    echo "Error: STARTUP_DELAY environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
if [ -z "$RETRY_DELAY" ]; then
    echo "Error: RETRY_DELAY environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
if [ -z "$STRATEGY" ]; then
    echo "Error: STRATEGY environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
if [ -z "$CONFIG" ]; then
    echo "Error: CONFIG environment variable is not set." >&2
    exit 1 # Exit code 1 for unset variable
fi
echo " [OK] Config is valid"
echo "==============[CONFIG]==============="
echo " BACKEND_URL        : $BACKEND_URL"
echo " EXECUTION_DELAY    : $EXECUTION_DELAY seconds"
echo " STARTUP_DELAY      : $STARTUP_DELAY seconds"
echo " RETRY_DELAY        : $RETRY_DELAY seconds"
echo " CONFIRMATION_DELAY : $CONFIRMATION_DELAY seconds"
echo " STRATEGY           : $STRATEGY"
echo "====================================="
echo "Starting trading strategy executor..."
set -x
gunicorn --bind=0.0.0.0:8080 --workers=1 app:app
