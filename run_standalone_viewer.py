#!/usr/bin/env python3
"""
Script to run the standalone PDF viewer on a separate port.
This allows the main RAG app and the document viewer to run simultaneously.
"""

import subprocess
import sys
import os

def main():
    # Set the port for the standalone viewer
    viewer_port = 8503
    
    # Set environment variables for Streamlit
    env = os.environ.copy()
    env['STREAMLIT_SERVER_PORT'] = str(viewer_port)
    env['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    print(f"Starting standalone PDF viewer on port {viewer_port}...")
    print(f"Viewer will be available at: http://localhost:{viewer_port}")
    
    try:
        # Run the standalone viewer
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "standalone_pdf_viewer.py",
            "--server.port", str(viewer_port),
            "--server.headless", "true"
        ], env=env)
    except KeyboardInterrupt:
        print("\nShutting down standalone PDF viewer...")
    except Exception as e:
        print(f"Error running standalone viewer: {e}")

if __name__ == "__main__":
    main() 