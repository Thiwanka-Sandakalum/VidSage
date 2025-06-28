#!/usr/bin/env python3
"""
VidSage Setup Script

This script helps set up all dependencies for VidSage API.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, capture_output=True, shell=False):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=True, shell=shell, check=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, "Command not found"

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_pip():
    """Check if pip is available"""
    success, output = run_command([sys.executable, '-m', 'pip', '--version'])
    if success:
        print("✅ pip is available")
        return True
    else:
        print("❌ pip is not available")
        return False

def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    success, output = run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
    if success:
        print("✅ Python requirements installed")
        return True
    else:
        print(f"❌ Failed to install requirements: {output}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    success, output = run_command(['ffmpeg', '-version'])
    if success:
        print("✅ FFmpeg is installed")
        return True
    else:
        print("❌ FFmpeg is not installed")
        return False

def install_ffmpeg_instructions():
    """Show FFmpeg installation instructions"""
    system = platform.system().lower()
    
    print("\n📺 FFmpeg Installation Instructions:")
    print("=" * 40)
    
    if system == "windows":
        print("Windows:")
        print("  Option 1 - Chocolatey (Recommended):")
        print("    choco install ffmpeg")
        print("  Option 2 - winget:")
        print("    winget install FFmpeg")
        print("  Option 3 - Manual:")
        print("    1. Download from https://ffmpeg.org/download.html")
        print("    2. Extract to C:\\ffmpeg")
        print("    3. Add C:\\ffmpeg\\bin to PATH")
    elif system == "darwin":  # macOS
        print("macOS:")
        print("  brew install ffmpeg")
    else:  # Linux
        print("Linux:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  CentOS/RHEL: sudo yum install ffmpeg")
        print("  Arch: sudo pacman -S ffmpeg")

def setup_env_file():
    """Set up environment file"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    elif env_example.exists():
        print("📝 Creating .env file from template...")
        env_example.rename(env_file)
        print("✅ .env file created")
        print("⚠️  Please edit .env file and set your GOOGLE_API_KEY")
        return True
    else:
        print("⚠️  No .env.example file found")
        return False

def create_data_directories():
    """Create necessary data directories"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    subdirs = ['audio', 'video', 'subtitles', 'thumbnails', 'info', 'transcripts', 'summaries', 'embeddings']
    for subdir in subdirs:
        (data_dir / subdir).mkdir(exist_ok=True)
    
    print("✅ Data directories created")

def main():
    """Main setup function"""
    print("🛠️  VidSage Setup")
    print("=" * 50)
    
    # Check basic requirements
    print("🔍 Checking system requirements...")
    
    python_ok = check_python()
    pip_ok = check_pip()
    
    if not (python_ok and pip_ok):
        print("❌ Basic requirements not met. Please fix the above issues.")
        return 1
    
    # Set up environment
    setup_env_file()
    
    # Create directories
    create_data_directories()
    
    # Install Python packages
    if not install_requirements():
        print("❌ Failed to install Python requirements")
        return 1
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        install_ffmpeg_instructions()
    
    print("\n🎉 Setup Summary:")
    print("=" * 30)
    print(f"✅ Python: {'OK' if python_ok else 'FAIL'}")
    print(f"✅ pip: {'OK' if pip_ok else 'FAIL'}")
    print(f"✅ Python packages: OK")
    print(f"{'✅' if ffmpeg_ok else '⚠️ '} FFmpeg: {'OK' if ffmpeg_ok else 'Missing (see instructions above)'}")
    print(f"✅ Environment: OK")
    print(f"✅ Data directories: OK")
    
    if ffmpeg_ok:
        print("\n🚀 All set! You can now start the API server:")
        print("   python start_api.py")
    else:
        print("\n⚠️  Please install FFmpeg, then start the server:")
        print("   python start_api.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
