"""
WaveTerm - Terminal Music Visualizer
====================================

A modern terminal-based music visualizer with stunning ASCII art effects.

Features:
- 15+ stunning visualizations
- Real-time audio input (microphone, files, system audio)  
- Headless mode with simulated audio
- Plugin architecture for custom visualizations
- Export to images, GIFs, and videos
- Modern Python packaging with optional dependencies

Example usage:
    >>> from waveterm import WaveApp
    >>> app = WaveApp()
    >>> app.run()

Or from command line:
    $ waveterm --mode matrix --input mic
    $ waveterm-demo  # No audio required
"""

__version__ = "0.6.3"
__author__ = "espadonne (mfw)"
__email__ = "espadonne@outlook.com"

try:
    from .core.app import WaveApp
    from .core.config import WaveConfig
    __all__ = ["WaveApp", "WaveConfig"]
except ImportError:
    # Allow partial imports during development
    __all__ = []