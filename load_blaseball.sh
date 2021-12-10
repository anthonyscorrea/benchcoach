#!/bin/bash
PROJECT_PATH="."
PYTHON_PATH="$PROJECT_PATH/venv/bin/python"
FIXTURES="blaseball"
MANAGE_PY_PATH="$PROJECT_PATH/manage.py"
bash -cl "$PYTHON_PATH $MANAGE_PY_PATH flush --no-input"
bash -cl "$PYTHON_PATH $MANAGE_PY_PATH loaddata $FIXTURES"
