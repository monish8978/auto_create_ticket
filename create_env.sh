#!/bin/bash

# Setting up the directory
cd /Czentrix/apps/auto_create_ticket/
cdir="$(pwd)/venv/bin/"

# Printing the directory for debugging
echo "Virtual environment directory: $cdir"

# Creating virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
virtualenv venv -p /opt/python3.6.7/bin/python3
echo "Virtual environment created."

# Activating the virtual environment
source venv/bin/activate

# Installing requirements
echo "Installing requirements..."
pip install -r requirements.txt
echo "Requirements installed."
