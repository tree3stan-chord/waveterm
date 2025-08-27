#!/usr/bin/env python3
"""
Wave Demo - Shows off visualizations without audio input
Perfect for testing and showcasing the terminal visualizer
"""

import time
import sys
import math
import numpy as np
from src.render.terminal import TerminalRenderer, VisualizationData
from src.visualizations.basic import BasicVisualizations
from src.visualizations.advanced import AdvancedVisualizations

class MockAudioData:
    """Generate dynamic mock audio data for demo"""
    def __init__(self, time_offset=0):
        # Simulate audio data with time-based variation
        self.frequencies = np.linspace(0, 22050, 1024)
        
        # Create dynamic amplitude data
        base_amps = np.random.random(1024) * 0.3
        
        # Add some frequency-based patterns
        for i in range(1024):
            freq_normalized = i / 1024.0
            # Add bass boost
            if freq_normalized < 0.1:
                base_amps[i] += 0.4 * math.sin(time_offset * 2)
            # Mid frequencies
            elif freq_normalized < 0.5:
                base_amps[i] += 0.3 * math.sin(time_offset * 3 + i * 0.01)
            # Treble
            else:
                base_amps[i] += 0.2 * math.sin(time_offset * 5 + i * 0.005)
        
        # Normalize
        self.amplitudes = np.clip(base_amps, 0, 1)
        
        # Generate realistic waveform
        waveform = np.zeros(2048)
        for i in range(len(waveform)):
            t = i / 2048.0
            waveform[i] = (0.3 * math.sin(2 * math.pi * 440 * t * 5) +  # A4
                          0.2 * math.sin(2 * math.pi * 880 * t * 3) +    # A5
                          0.1 * math.sin(2 * math.pi * 220 * t * 7))     # A3
            waveform[i] *= (1 + 0.3 * math.sin(time_offset * 2))  # Volume variation
            
        self.waveform = np.clip(waveform, -1, 1)
        self.sample_rate = 44100
        
        # Frequency band analysis
        bass_end = int(len(self.amplitudes) * 0.1)
        mid_start = bass_end
        mid_end = int(len(self.amplitudes) * 0.5)
        treble_start = mid_end
        
        self.bass = np.mean(self.amplitudes[:bass_end])
        self.mid = np.mean(self.amplitudes[mid_start:mid_end])
        self.treble = np.mean(self.amplitudes[treble_start:])
        self.overall_amplitude = np.mean(self.amplitudes)

def run_demo():
    """Run the Wave visualization demo"""
    print("🌊 Wave Terminal Music Visualizer Demo")
    print("=====================================")
    print()
    
    # Available modes
    modes = [
        ("bars", "Frequency Bars", BasicVisualizations().frequency_bars),
        ("wave", "Waveform", BasicVisualizations().waveform),
        ("matrix", "Matrix Rain", BasicVisualizations().matrix_rain),
        ("particles", "Particle Field", BasicVisualizations().particle_field),
        ("circle", "Circular Wave", BasicVisualizations().circular_wave),
        ("starfield", "Starfield Warp", AdvancedVisualizations().starfield_warp),
        ("fire", "Fire Flames", AdvancedVisualizations().fire_flames),
        ("ocean", "Ocean Waves", AdvancedVisualizations().ocean_waves),
        ("dna", "DNA Helix", AdvancedVisualizations().dna_helix),
        ("neural", "Neural Network", AdvancedVisualizations().neural_network),
    ]
    
    # Initialize renderer
    renderer = TerminalRenderer()
    renderer.initialize()
    
    try:
        mode_index = 0
        start_time = time.time()
        last_switch = start_time
        
        print(f"Starting demo with {len(modes)} visualization modes...")
        print("Each mode will run for 5 seconds")
        print("Press Ctrl+C to exit\n")
        
        time.sleep(2)  # Let user read the message
        
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Switch modes every 5 seconds
            if current_time - last_switch > 5:
                mode_index = (mode_index + 1) % len(modes)
                last_switch = current_time
                
            mode_id, mode_name, mode_func = modes[mode_index]
            
            # Create canvas and audio data
            canvas = renderer.create_canvas()
            audio_data = MockAudioData(elapsed)
            
            # Generate visualization
            mode_func(canvas, audio_data, elapsed)
            
            # Add mode info
            info = f"Mode: {mode_name} | Bass: {audio_data.bass:.2f} | Overall: {audio_data.overall_amplitude:.2f}"
            for i, char in enumerate(info[:canvas.width]):
                if i < canvas.width:
                    canvas.set_char(i, 0, char, 'white')
            
            # Render frame
            renderer.render(canvas)
            
            # Control frame rate
            time.sleep(1/30)  # 30 FPS
            
    except KeyboardInterrupt:
        pass
    finally:
        renderer.cleanup()
        print("\n🎵 Wave demo ended. Thanks for watching!")
        print("\nTo install audio dependencies for full functionality:")
        print("  sudo apt-get install portaudio19-dev  # Ubuntu/Debian")
        print("  brew install portaudio               # macOS")
        print("  pip install sounddevice librosa")

if __name__ == "__main__":
    run_demo()