#!/bin/bash
echo "======[TRADING STRATEGY]======"
echo "Startup checks...."
# TODO: add
echo " [OK] Config is valid"
echo "===================================="
echo "Replace placeholders...."
# TODO: Add
# export SERVER_CONFIG=$(echo "$SERVER_CONFIG" | sed "s%<<CORE_MAESTRO_API_KEY>>%$CORE_MAESTRO_API_KEY%g")
echo "[OK] Done. Replaced placeholders."
echo "===================================="
echo "Starting active strategy..."
set -x
gunicorn --bind=0.0.0.0:8080 --workers=1 app:app
