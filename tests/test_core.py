"""
Tests for WaveTerm core functionality
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from waveterm.core.app import WaveApp
from waveterm.core.config import WaveConfig


class TestWaveApp(unittest.TestCase):
    """Test WaveApp functionality"""
    
    def test_app_creation(self):
        """Test that WaveApp can be created with default parameters"""
        app = WaveApp()
        self.assertEqual(app.current_mode, "bars")
        self.assertEqual(app.input_source, "sim")
        self.assertIsNotNone(app.audio_simulator)
    
    def test_app_with_custom_mode(self):
        """Test WaveApp creation with custom visualization mode"""
        app = WaveApp(mode="matrix", fps=60)
        self.assertEqual(app.current_mode, "matrix")
        self.assertEqual(app.fps, 60)
    
    def test_mode_switching(self):
        """Test visualization mode switching"""
        app = WaveApp()
        result = app.set_mode("glitch")
        self.assertTrue(result)
        self.assertEqual(app.current_mode, "glitch")
        
        # Test invalid mode
        result = app.set_mode("nonexistent")
        self.assertFalse(result)
    
    def test_available_modes(self):
        """Test getting available visualization modes"""
        app = WaveApp()
        modes = app.get_available_modes()
        self.assertIsInstance(modes, list)
        self.assertIn("bars", modes)
        self.assertIn("matrix", modes)
        self.assertIn("glitch", modes)
        self.assertIn("hypercube", modes)
        # Should have 15 modes total
        self.assertEqual(len(modes), 15)


class TestWaveConfig(unittest.TestCase):
    """Test WaveConfig functionality"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = WaveConfig()
        self.assertEqual(config.default_mode, "bars")
        self.assertEqual(config.default_input, "sim")
        self.assertEqual(config.version, "0.2.0")
    
    def test_audio_config(self):
        """Test audio configuration"""
        config = WaveConfig()
        self.assertEqual(config.audio.sample_rate, 44100)
        self.assertEqual(config.audio.buffer_size, 2048)
        self.assertEqual(config.audio.sensitivity, 1.0)
    
    def test_visual_config(self):
        """Test visual configuration"""
        config = WaveConfig()
        self.assertEqual(config.visual.fps, 30)
        self.assertTrue(config.visual.colors)
        self.assertIsNone(config.visual.width)
        self.assertIsNone(config.visual.height)
    
    def test_plugin_config(self):
        """Test plugin configuration"""
        config = WaveConfig()
        self.assertTrue(config.plugins.enabled)
        self.assertTrue(config.plugins.auto_load)
        self.assertIn("~/.waveterm/plugins", config.plugins.directories)


if __name__ == '__main__':
    unittest.main()