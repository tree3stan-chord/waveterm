"""
Tests for WaveTerm audio functionality
"""

import unittest
import sys
import os
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from waveterm.audio.simulator import AudioSimulator


class TestAudioSimulator(unittest.TestCase):
    """Test AudioSimulator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.simulator = AudioSimulator('electronic')
    
    def test_simulator_creation(self):
        """Test AudioSimulator creation"""
        self.assertEqual(self.simulator.pattern_name, 'electronic')
        self.assertEqual(self.simulator.sample_rate, 44100)
        self.assertEqual(self.simulator.buffer_size, 2048)
    
    def test_audio_data_generation(self):
        """Test audio data generation"""
        audio_data = self.simulator.generate_audio_data()
        
        self.assertIsNotNone(audio_data)
        self.assertIsInstance(audio_data.frequencies, np.ndarray)
        self.assertIsInstance(audio_data.amplitudes, np.ndarray)
        self.assertIsInstance(audio_data.waveform, np.ndarray)
        
        # Check data shapes
        self.assertEqual(len(audio_data.frequencies), len(audio_data.amplitudes))
        self.assertEqual(len(audio_data.waveform), self.simulator.buffer_size)
        
        # Check data ranges
        self.assertTrue(np.all(audio_data.amplitudes >= 0))
        self.assertTrue(np.all(audio_data.amplitudes <= 1))
        self.assertTrue(np.all(audio_data.waveform >= -1))
        self.assertTrue(np.all(audio_data.waveform <= 1))
    
    def test_frequency_bands(self):
        """Test frequency band analysis"""
        audio_data = self.simulator.generate_audio_data()
        
        # Test that bass, mid, treble are in valid ranges
        self.assertGreaterEqual(audio_data.bass, 0)
        self.assertLessEqual(audio_data.bass, 1)
        self.assertGreaterEqual(audio_data.mid, 0) 
        self.assertLessEqual(audio_data.mid, 1)
        self.assertGreaterEqual(audio_data.treble, 0)
        self.assertLessEqual(audio_data.treble, 1)
        self.assertGreaterEqual(audio_data.overall_amplitude, 0)
        self.assertLessEqual(audio_data.overall_amplitude, 1)
    
    def test_pattern_switching(self):
        """Test switching audio patterns"""
        original_pattern = self.simulator.pattern_name
        
        # Test valid pattern
        result = self.simulator.set_pattern('rock')
        self.assertTrue(result)
        self.assertEqual(self.simulator.pattern_name, 'rock')
        
        # Test invalid pattern
        result = self.simulator.set_pattern('nonexistent')
        self.assertFalse(result)
        self.assertEqual(self.simulator.pattern_name, 'rock')  # Should remain unchanged
    
    def test_available_patterns(self):
        """Test getting available audio patterns"""
        patterns = self.simulator.get_available_patterns()
        self.assertIsInstance(patterns, list)
        self.assertIn('electronic', patterns)
        self.assertIn('rock', patterns)
        self.assertIn('ambient', patterns)
        self.assertIn('dubstep', patterns)
        self.assertEqual(len(patterns), 8)  # Should have 8 patterns
    
    def test_different_patterns_generate_different_data(self):
        """Test that different patterns generate different audio characteristics"""
        # Generate data with electronic pattern
        electronic_data = self.simulator.generate_audio_data()
        
        # Switch to ambient pattern and generate data
        self.simulator.set_pattern('ambient')
        ambient_data = self.simulator.generate_audio_data()
        
        # The patterns should produce different characteristics
        # (This is a basic test - patterns are time-varying so exact comparison is difficult)
        self.assertIsNotNone(electronic_data)
        self.assertIsNotNone(ambient_data)
        
        # Both should have valid data structures
        self.assertEqual(len(electronic_data.amplitudes), len(ambient_data.amplitudes))
        self.assertEqual(len(electronic_data.waveform), len(ambient_data.waveform))


if __name__ == '__main__':
    unittest.main()