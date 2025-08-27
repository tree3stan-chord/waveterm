# WaveTerm 🌊

A modern terminal-based music visualizer with stunning ASCII art effects.

## ✨ Features

- **15+ stunning visualizations** - Basic, Advanced, and Extreme modes
- **Perfect for headless servers** - No audio hardware required
- **Multiple input sources**: microphone, audio files, or simulated audio
- **Modern CLI interface** with Rich formatting
- **Plugin architecture** for custom visualizations  
- **Export capabilities** - Save frames, GIFs, and videos
- **Cross-platform**: Linux, macOS, Windows

## 🚀 Quick Start

```bash
# Install WaveTerm
pip install waveterm

# Run demo (no audio required)
waveterm-demo

# Run with microphone input  
waveterm run --mode matrix --input mic

# Run with simulated audio (perfect for servers)
waveterm run --mode glitch --input sim

# Run with audio file
waveterm run --input file --file song.mp3 --mode fire
```

## 🎨 Visualization Modes

### Basic (5 modes)
- `bars` - Frequency spectrum bars
- `wave` - Oscilloscope waveform  
- `matrix` - Matrix-style falling rain
- `particles` - ASCII particle field
- `circle` - Circular frequency display

### Advanced (5 modes)  
- `starfield` - Starfield warp effect
- `fire` - ASCII flame simulation
- `ocean` - Wave interference patterns
- `dna` - Rotating DNA helix
- `neural` - Neural network visualization

### Extreme (5 modes)
- `glitch` - Digital glitch art effects
- `void` - Lovecraftian tentacles  
- `hypercube` - 4D tesseract projection
- `fractal` - Recursive ASCII fractals
- `portal` - Swirling dimensional portal

## 📋 CLI Commands

```bash
# List all available modes
waveterm modes

# Run diagnostics
waveterm doctor

# Create configuration  
waveterm config

# Export visualization
waveterm export output.gif --mode hypercube --duration 10
```

## 🏗️ Architecture

```
waveterm/
├── cli.py              # Modern Click CLI
├── core/
│   ├── app.py         # Main application  
│   ├── config.py      # Configuration system
│   └── diagnostics.py # System diagnostics
├── audio/
│   ├── processor.py   # Real audio processing
│   └── simulator.py   # Audio simulation
├── render/
│   └── terminal.py    # Terminal rendering
├── visualizations/
│   ├── registry.py    # Plugin registry
│   ├── basic.py       # Basic visualizations
│   ├── advanced.py    # Advanced visualizations
│   └── extreme.py     # Extreme visualizations
└── config/
    └── config.py      # Pydantic configurations
```

## 🖥️ Perfect for Servers

WaveTerm works great on headless servers with **simulated audio patterns**:

```bash
# Electronic music simulation
waveterm run --mode neural --input sim

# Multiple realistic audio patterns available:
# electronic, rock, ambient, dubstep, classical, techno, chill
```

## ⚙️ Configuration

```bash
# Create config file
waveterm config

# Config location: ~/.waveterm/config.toml
```

## 🔧 Development

```bash
# Install in development mode
git clone https://github.com/espadonne/waveterm
cd waveterm  
pip install -e .

# Run tests
pytest

# Install with audio support
pip install waveterm[audio]

# Install with export capabilities  
pip install waveterm[export]

# Install everything
pip install waveterm[all]
```