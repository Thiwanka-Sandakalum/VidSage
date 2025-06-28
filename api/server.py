#!/usr/bin/env python3
"""
VidSage API Server Startup Script

This script provides an easy way to start the VidSage API server with proper configuration.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import google.genai
        import whisper
        import chromadb
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_api_key():
    """Check if Google API key is configured"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'YOUR_API_KEY':
        print("⚠️  Google API key not configured")
        print("Set GOOGLE_API_KEY environment variable or add to .env file")
        return False
    print("✅ Google API key configured")
    return True

def create_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    subdirs = ['audio', 'video', 'subtitles', 'thumbnails', 'info', 'transcripts', 'summaries', 'embeddings']
    for subdir in subdirs:
        (data_dir / subdir).mkdir(exist_ok=True)
    print("✅ Data directories created")

def main():
    """Main function to start the API server"""
    parser = argparse.ArgumentParser(description="VidSage API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], 
                       help="Log level (default: info)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    parser.add_argument("--skip-checks", action="store_true", help="Skip dependency and API key checks")
    
    args = parser.parse_args()
    
    print("🚀 Starting VidSage API Server...")
    print("=" * 50)
    
    # Perform checks unless skipped
    if not args.skip_checks:
        print("🔍 Performing startup checks...")
        
        if not check_dependencies():
            sys.exit(1)
        
        if not check_api_key():
            print("⚠️  API will have limited functionality without Google API key")
            input("Press Enter to continue anyway or Ctrl+C to exit...")
    
    # Create data directories
    create_data_directory()
    
    # Import and start the server
    try:
        import uvicorn
        
        # Add the parent directory to Python path for proper imports
        parent_dir = current_dir.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        # Try to import the app to verify it works
        try:
            from api.main import app
            print("✅ API module imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import API module: {e}")
            print("Make sure you're running from the VidSage root directory")
            sys.exit(1)
        
        print(f"🌐 Server starting on http://{args.host}:{args.port}")
        print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
        print(f"🏥 Health Check: http://{args.host}:{args.port}/health")
        print("=" * 50)
        
        # Start the server with the correct module path
        uvicorn.run(
            "api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers if not args.reload else 1,  # Workers don't work with reload
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
