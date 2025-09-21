#!/usr/bin/env python3
"""
Startup script for the Rockfall Prediction System backend
"""

import os
import sys
import uvicorn

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    # Change to backend directory
    os.chdir(backend_path)
    
    # Start the server
    uvicorn.run(
        "backend_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )