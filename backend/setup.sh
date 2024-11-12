#!/bin/bash

# Create virtual environment
python3 -m venv minorvenv

# Activate virtual environment
source minorvenv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Deactivate the venv
deactivate

echo "Setup complete."
