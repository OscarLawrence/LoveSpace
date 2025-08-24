#!/usr/bin/env python3
"""
Axiom PWA Startup Script
Simple script to start the FastAPI backend server
"""

import os
import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ required")
        return False
    
    # Check if in virtual environment (recommended)
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment (recommended)")
    
    # API key validation handled by backend (supports PWA key input)
    
    print("✅ Requirements check passed")
    return True

def install_dependencies():
    """Install dependencies if needed"""
    print("📦 Installing dependencies...")
    
    try:
        # Use uv for dependency installation (respects uv.lock)
        subprocess.run(["uv", "sync"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed with uv")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  UV installation failed, trying pip fallback: {e}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                          check=True, capture_output=True)
            print("✅ Dependencies installed with pip")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"⚠️  Both uv and pip failed (may already be installed): {e2}")
            return True  # Continue anyway

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Axiom PWA server...")
    
    # Change to backend directory
    backend_dir = Path("axiom/backend")
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        print(f"Current directory: {os.getcwd()}")
        print("Available directories:", [d.name for d in Path(".").iterdir() if d.is_dir()])
        return False
    
    # Start uvicorn server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ], check=True, cwd=backend_dir)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return True

def main():
    """Main startup function"""
    print("⚡ Axiom PWA - Coherent AI Collaboration Platform")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Install dependencies (skip if fails - dependencies might already be installed)
    install_dependencies()
    
    # Start server
    print("\n🌐 Axiom PWA will be available at:")
    print("   http://localhost:8000")
    print("   http://127.0.0.1:8000")
    print("\n📋 Features enabled:")
    print("   • Real-time coherence validation")  
    print("   • Formal contract system")
    print("   • AI-human collaboration stages")
    print("   • Progressive Web App interface")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()