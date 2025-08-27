#!/usr/bin/env python3
"""
Test script to verify Wave structure without audio dependencies
"""

import sys
import numpy as np

# Mock audio data for testing
class MockAudioData:
    def __init__(self):
        # Generate some test data
        self.frequencies = np.linspace(0, 22050, 1024)
        self.amplitudes = np.random.random(1024) * 0.5
        self.waveform = np.sin(np.linspace(0, 4*np.pi, 2048)) * 0.5
        self.sample_rate = 44100
        self.bass = 0.3
        self.mid = 0.5
        self.treble = 0.2
        self.overall_amplitude = 0.4

def test_visualizations():
    """Test visualization modules"""
    print("Testing Wave visualization modules...")
    
    from src.render.terminal import TerminalRenderer, VisualizationData
    from src.visualizations.basic import BasicVisualizations
    from src.visualizations.advanced import AdvancedVisualizations
    
    # Create test canvas
    renderer = TerminalRenderer()
    renderer.initialize()
    canvas = renderer.create_canvas()
    
    # Create mock audio data
    audio_data = MockAudioData()
    
    # Test basic visualizations
    print("✓ Testing basic visualizations...")
    basic_viz = BasicVisualizations()
    
    basic_viz.frequency_bars(canvas, audio_data, 1.0)
    print("  ✓ Frequency bars")
    
    canvas.clear()
    basic_viz.waveform(canvas, audio_data, 1.0)
    print("  ✓ Waveform")
    
    canvas.clear()
    basic_viz.matrix_rain(canvas, audio_data, 1.0)
    print("  ✓ Matrix rain")
    
    canvas.clear()
    basic_viz.particle_field(canvas, audio_data, 1.0)
    print("  ✓ Particle field")
    
    canvas.clear()
    basic_viz.circular_wave(canvas, audio_data, 1.0)
    print("  ✓ Circular wave")
    
    # Test advanced visualizations
    print("✓ Testing advanced visualizations...")
    advanced_viz = AdvancedVisualizations()
    
    canvas.clear()
    advanced_viz.starfield_warp(canvas, audio_data, 1.0)
    print("  ✓ Starfield warp")
    
    canvas.clear()
    advanced_viz.fire_flames(canvas, audio_data, 1.0)
    print("  ✓ Fire flames")
    
    canvas.clear()
    advanced_viz.ocean_waves(canvas, audio_data, 1.0)
    print("  ✓ Ocean waves")
    
    canvas.clear()
    advanced_viz.dna_helix(canvas, audio_data, 1.0)
    print("  ✓ DNA helix")
    
    canvas.clear()
    advanced_viz.neural_network(canvas, audio_data, 1.0)
    print("  ✓ Neural network")
    
    renderer.cleanup()
    
    print("\n🎉 All visualization tests passed!")
    print("Wave structure is working correctly!")
    
    print(f"\nCanvas size: {canvas.width}x{canvas.height}")
    print(f"Audio data: {len(audio_data.amplitudes)} frequency bins")
    
if __name__ == "__main__":
    test_visualizations()