#!/usr/bin/env python
"""
Simple script to start the REST API server with proper encoding handling.
"""
import os
import sys
import subprocess

# Set environment variable for UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

# Change to mud_analyzer directory
mud_analyzer_dir = os.path.join(parent_dir, 'mud_analyzer')
os.chdir(mud_analyzer_dir)

# Add to sys.path
sys.path.insert(0, mud_analyzer_dir)
sys.path.insert(0, parent_dir)

# Import and start the REST API server directly
try:
    # Try to import the necessary modules
    from api.rest_server import app
    import uvicorn
    
    print("Starting REST API server on http://localhost:8000")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're in the correct directory and all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
