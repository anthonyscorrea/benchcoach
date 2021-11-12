#!/bin/bash
PROJECT_PATH="/Users/asc/PycharmProjects_Local/benchcoach"
PYTHON_PATH="$PROJECT_PATH/venv/bin/python"
FIXTURES="2021cmba"
MANAGE_PY_PATH="$PROJECT_PATH/manage.py"
bash -cl "$PYTHON_PATH $MANAGE_PY_PATH flush --no-input"
bash -cl "$PYTHON_PATH $MANAGE_PY_PATH loaddata $FIXTURES"
