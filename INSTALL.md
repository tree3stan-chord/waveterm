# Wave Installation Guide

## Quick Demo (No Audio Required)

To see Wave's visualizations without audio input:

```bash
python demo.py
```

## Full Installation with Audio Support

### 1. System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev python3-dev
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum install portaudio-devel python3-devel
# OR (newer systems)
sudo dnf install portaudio-devel python3-devel
```

**macOS:**
```bash
brew install portaudio
```

**Windows:**
```bash
# PortAudio is included with sounddevice on Windows
# No additional system packages needed
```

### 2. Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Test Installation

```bash
# Test basic structure
python test_structure.py

# Test with audio (requires working microphone)
python wave.py -m bars

# Test with audio file
python wave.py -i file -f your_audio_file.mp3
```

## Usage

```bash
# Basic usage - microphone input with frequency bars
python wave.py

# Choose visualization mode
python wave.py -m matrix     # Matrix rain
python wave.py -m fire       # Fire flames
python wave.py -m starfield  # Starfield warp

# Use audio file as input
python wave.py -i file -f song.mp3 -m circle

# Adjust sensitivity
python wave.py --sensitivity 2.0

# Custom FPS
python wave.py --fps 60
```

## Available Modes

### Basic Visualizations
- `bars` - Frequency spectrum bars
- `wave` - Oscilloscope waveform
- `matrix` - Matrix-style falling characters
- `particles` - ASCII particle field
- `circle` - Circular frequency display

### Advanced Visualizations
- `starfield` - Starfield warp effect
- `fire` - ASCII flame simulation
- `ocean` - Wave interference patterns
- `dna` - Rotating DNA helix
- `neural` - Neural network visualization

## Troubleshooting

### "PortAudio library not found"
Install the system PortAudio library (see step 1 above).

### "No module named sounddevice"
```bash
pip install sounddevice
```

### "Permission denied" for microphone
- **Linux**: Add your user to the `audio` group
- **macOS**: Grant microphone permission in System Preferences
- **Windows**: Check privacy settings for microphone access

### Low audio sensitivity
Use the `--sensitivity` parameter:
```bash
python wave.py --sensitivity 3.0
```

### Performance issues
- Lower FPS: `--fps 15`
- Smaller terminal window
- Close other applications