#!/usr/bin/env python3
"""
SchemeScout - Startup Script
Starts both the FastAPI backend and serves the frontend
Team: Bit-Wise 4
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
BACKEND_DIR = PROJECT_ROOT / 'backend'
FRONTEND_DIR = PROJECT_ROOT / 'public'


def check_python_dependencies():
    """Check and install Python dependencies"""
    print("Checking Python dependencies...")
    requirements_file = BACKEND_DIR / 'requirements.txt'
    
    if requirements_file.exists():
        # Install with visible output instead of quiet mode
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
        ])
        print("Dependencies installed.")
    else:
        print("Warning: requirements.txt not found")


def start_backend():
    """Start the FastAPI backend server"""
    print("Starting FastAPI backend on http://localhost:8000")
    os.chdir(BACKEND_DIR)
    subprocess.run([
        sys.executable, '-m', 'uvicorn', 'main:app', 
        '--host', '0.0.0.0', 
        '--port', '8000', 
        '--reload'
    ])


def start_frontend():
    """Start a simple HTTP server for the frontend"""
    print("Starting frontend server on http://localhost:3000")
    os.chdir(FRONTEND_DIR)
    subprocess.run([
        sys.executable, '-m', 'http.server', '3000'
    ])


def open_browser():
    """Open the default browser after servers start"""
    time.sleep(3)  # Wait for servers to start
    webbrowser.open('http://localhost:3000')


def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║                   SchemeScout                         ║
    ║         Punjab Government Welfare Finder              ║
    ║                  by Bit-Wise 4                        ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    # Check dependencies
    check_python_dependencies()
    
    # Create data directory if it doesn't exist
    data_dir = BACKEND_DIR / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # Start servers in separate threads
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    
    try:
        backend_thread.start()
        time.sleep(2)  # Give backend time to start
        frontend_thread.start()
        browser_thread.start()
        
        print("\n" + "="*55)
        print("SchemeScout is running!")
        print("="*55)
        print(f"Frontend: http://localhost:3000")
        print(f"Backend API: http://localhost:8000")
        print(f"API Docs: http://localhost:8000/docs")
        print("="*55)
        print("Press Ctrl+C to stop all servers")
        print("="*55 + "\n")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nShutting down SchemeScout...")
        print("Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
