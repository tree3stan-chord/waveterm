"""
Tests for WaveTerm visualization functionality
"""

import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from waveterm.visualizations.registry import get_all_modes, get_mode, register_mode
from waveterm.visualizations.manager import VisualizationManager
from waveterm.render.terminal import TerminalRenderer, VisualizationData
from waveterm.audio.simulator import AudioSimulator


class TestVisualizationRegistry(unittest.TestCase):
    """Test visualization registry functionality"""
    
    def test_get_all_modes(self):
        """Test getting all registered visualization modes"""
        modes = get_all_modes()
        self.assertIsInstance(modes, dict)
        
        # Check that all expected modes are present
        expected_basic = ['bars', 'wave', 'matrix', 'particles', 'circle']
        expected_advanced = ['starfield', 'fire', 'ocean', 'dna', 'neural']
        expected_extreme = ['glitch', 'void', 'hypercube', 'fractal', 'portal']
        
        for mode in expected_basic + expected_advanced + expected_extreme:
            self.assertIn(mode, modes)
            self.assertIn('name', modes[mode])
            self.assertIn('category', modes[mode])
            self.assertIn('description', modes[mode])
            self.assertIn('function', modes[mode])
    
    def test_get_mode(self):
        """Test getting individual visualization modes"""
        # Test valid mode
        bars_func = get_mode('bars')
        self.assertIsNotNone(bars_func)
        self.assertTrue(callable(bars_func))
        
        # Test invalid mode
        invalid_func = get_mode('nonexistent')
        self.assertIsNone(invalid_func)
    
    def test_mode_categories(self):
        """Test that modes are properly categorized"""
        modes = get_all_modes()
        
        basic_count = sum(1 for mode in modes.values() if mode['category'] == 'basic')
        advanced_count = sum(1 for mode in modes.values() if mode['category'] == 'advanced')
        extreme_count = sum(1 for mode in modes.values() if mode['category'] == 'extreme')
        
        self.assertEqual(basic_count, 5)
        self.assertEqual(advanced_count, 5)
        self.assertEqual(extreme_count, 5)


class TestVisualizationManager(unittest.TestCase):
    """Test VisualizationManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = VisualizationManager()
        self.simulator = AudioSimulator('electronic')
    
    def test_manager_creation(self):
        """Test VisualizationManager creation"""
        self.assertIsNotNone(self.manager.renderer)
        self.assertEqual(self.manager.current_mode, 'bars')
    
    def test_available_modes(self):
        """Test getting available modes from manager"""
        modes = self.manager.get_available_modes()
        self.assertIsInstance(modes, list)
        self.assertEqual(len(modes), 15)
    
    def test_mode_setting(self):
        """Test setting visualization modes"""
        result = self.manager.set_mode('matrix')
        self.assertTrue(result)
        self.assertEqual(self.manager.current_mode, 'matrix')
        
        result = self.manager.set_mode('nonexistent')
        self.assertFalse(result)
    
    def test_visualization_generation(self):
        """Test visualization generation"""
        audio_data = self.simulator.generate_audio_data()
        viz_data = self.manager.generate('bars', audio_data)
        
        self.assertIsInstance(viz_data, VisualizationData)
        self.assertGreater(viz_data.width, 0)
        self.assertGreater(viz_data.height, 0)
    
    def test_mode_info(self):
        """Test getting mode information"""
        info = self.manager.get_mode_info('glitch')
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'Glitch Art')
        self.assertEqual(info['category'], 'extreme')


class TestTerminalRenderer(unittest.TestCase):
    """Test TerminalRenderer functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.renderer = TerminalRenderer()
    
    def test_renderer_creation(self):
        """Test TerminalRenderer creation"""
        self.assertIsNotNone(self.renderer.console)
        self.assertGreaterEqual(self.renderer.width, 0)
        self.assertGreaterEqual(self.renderer.height, 0)
    
    def test_canvas_creation(self):
        """Test visualization canvas creation"""
        canvas = self.renderer.create_canvas()
        self.assertIsInstance(canvas, VisualizationData)
        self.assertGreater(canvas.width, 0)
        self.assertGreater(canvas.height, 0)
    
    def test_intensity_to_char(self):
        """Test intensity to character conversion"""
        # Test boundary values
        char = TerminalRenderer.intensity_to_char(0.0)
        self.assertEqual(char, ' ')
        
        char = TerminalRenderer.intensity_to_char(1.0)
        self.assertEqual(char, '█')
        
        # Test middle value
        char = TerminalRenderer.intensity_to_char(0.5)
        self.assertIn(char, TerminalRenderer.ASCII_CHARS)
    
    def test_frequency_to_color(self):
        """Test frequency to color mapping"""
        # Test bass frequencies
        color = TerminalRenderer.frequency_to_color(100, 22050)
        self.assertEqual(color, 'red')
        
        # Test mid frequencies
        color = TerminalRenderer.frequency_to_color(10000, 22050)
        self.assertEqual(color, 'green')
        
        # Test treble frequencies
        color = TerminalRenderer.frequency_to_color(18000, 22050)
        self.assertEqual(color, 'blue')


class TestVisualizationData(unittest.TestCase):
    """Test VisualizationData functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.canvas = VisualizationData(80, 24)
    
    def test_canvas_creation(self):
        """Test VisualizationData creation"""
        self.assertEqual(self.canvas.width, 80)
        self.assertEqual(self.canvas.height, 24)
        self.assertEqual(len(self.canvas.buffer), 24)
        self.assertEqual(len(self.canvas.buffer[0]), 80)
    
    def test_char_setting_and_getting(self):
        """Test setting and getting characters"""
        self.canvas.set_char(10, 10, '█', 'red')
        char = self.canvas.get_char(10, 10)
        self.assertEqual(char, '█')
        
        # Test boundary conditions
        char = self.canvas.get_char(-1, -1)
        self.assertEqual(char, ' ')
        
        char = self.canvas.get_char(100, 100)
        self.assertEqual(char, ' ')
    
    def test_canvas_clear(self):
        """Test canvas clearing"""
        # Set some characters
        self.canvas.set_char(5, 5, '█', 'red')
        self.canvas.set_char(10, 10, '▓', 'blue')
        
        # Clear canvas
        self.canvas.clear()
        
        # Check that it's cleared
        self.assertEqual(self.canvas.get_char(5, 5), ' ')
        self.assertEqual(self.canvas.get_char(10, 10), ' ')


if __name__ == '__main__':
    unittest.main()