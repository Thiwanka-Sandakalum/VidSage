#!/usr/bin/env python3
"""
VidSage API Startup Script

Simple script to start the VidSage API server from the root directory.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Start the VidSage API server"""
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting VidSage API Server...")
    print("=" * 50)
    
    # Check if .env file exists
    if not Path('.env').exists() and Path('.env.example').exists():
        print("⚠️  No .env file found. You may want to create one from .env.example")
    
    # Check for FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  FFmpeg not found. Please install FFmpeg for audio processing.")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        print("   Or use chocolatey: choco install ffmpeg")
        print("   Or use winget: winget install FFmpeg")
        print("   Note: Some features may not work without FFmpeg")
        print()
    
    try:
        # Start the server using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        
        print("🌐 Server will start on http://0.0.0.0:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🏥 Health Check: http://localhost:8000/health")
        print("=" * 50)
        
        # Run the command
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
