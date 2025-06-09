#!/usr/bin/env python3
"""
HiDream-I1-nf4 Web Interface Launcher

Simple launcher script to start the HiDream web interface.
Run this file directly: python app.py
"""

import subprocess
import sys
import os

def main():
    """Main function to start the HiDream web interface"""
    print("Starting HiDream-I1-nf4 Web Interface...")
    
    # Run the web module as if it were called directly
    # This ensures all the global variables and main block execute properly
    try:
        subprocess.run([sys.executable, "-m", "hdi1.web"], check=True)
    except KeyboardInterrupt:
        print("\nWeb interface stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 