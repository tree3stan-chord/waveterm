#!/usr/bin/env python3
"""
Wave - Terminal Music Visualizer
A Python-based music visualizer for the terminal inspired by web-based audio visualizers.
"""

import argparse
import sys
import os
from src.core.app import WaveApp

def main():
    parser = argparse.ArgumentParser(description="Wave - Terminal Music Visualizer")
    parser.add_argument("-m", "--mode", default="bars", 
                       help="Visualization mode (bars, wave, matrix, particles, circle)")
    parser.add_argument("-i", "--input", choices=["mic", "file"], default="mic",
                       help="Audio input source")
    parser.add_argument("-f", "--file", help="Audio file path (when using file input)")
    parser.add_argument("--fps", type=int, default=30, help="Target FPS")
    parser.add_argument("--sensitivity", type=float, default=1.0, help="Audio sensitivity")
    
    args = parser.parse_args()
    
    try:
        app = WaveApp(args)
        app.run()
    except KeyboardInterrupt:
        print("\nWave terminated by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()