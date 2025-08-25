"""
Terminal rendering system for Wave
Handles drawing to the terminal using ASCII characters and colors
"""

import os
import sys
import shutil
import time
from typing import List, Tuple, Optional, Dict, Any
from rich.console import Console
from rich.text import Text
from rich import color
import numpy as np

class VisualizationData:
    """Container for visualization data to be rendered"""
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.buffer: List[List[str]] = [[' ' for _ in range(width)] for _ in range(height)]
        self.colors: List[List[Optional[str]]] = [[None for _ in range(width)] for _ in range(height)]
        
    def set_char(self, x: int, y: int, char: str, color: Optional[str] = None):
        """Set character and color at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[y][x] = char
            if color:
                self.colors[y][x] = color
                
    def get_char(self, x: int, y: int) -> str:
        """Get character at position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.buffer[y][x]
        return ' '
        
    def clear(self):
        """Clear the buffer"""
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = ' '
                self.colors[y][x] = None

class TerminalRenderer:
    """Handles rendering visualization data to terminal"""
    
    # ASCII character sets for different intensity levels
    ASCII_CHARS = ' .·:¦|=+*#%@█'
    ASCII_BLOCKS = ' ░▒▓█'
    ASCII_INTENSITY = ' .:-=+*#%@'
    
    def __init__(self):
        self.console = Console()
        self.width = 0
        self.height = 0
        self.last_render_time = 0
        
        # Color palette
        self.colors = {
            'red': 'red',
            'green': 'green', 
            'blue': 'blue',
            'cyan': 'cyan',
            'magenta': 'magenta',
            'yellow': 'yellow',
            'white': 'white',
            'bright_red': 'bright_red',
            'bright_green': 'bright_green',
            'bright_blue': 'bright_blue',
            'bright_cyan': 'bright_cyan',
            'bright_magenta': 'bright_magenta',
            'bright_yellow': 'bright_yellow'
        }
        
    def initialize(self):
        """Initialize terminal for rendering"""
        self._update_terminal_size()
        
        # Hide cursor and clear screen
        self.console.print('\033[?25l', end='')  # Hide cursor
        self.console.clear()
        
    def _update_terminal_size(self):
        """Get current terminal dimensions"""
        size = shutil.get_terminal_size()
        self.width = size.columns
        self.height = size.lines - 2  # Reserve lines for info/controls
        
    def create_canvas(self) -> VisualizationData:
        """Create a new visualization canvas"""
        self._update_terminal_size()
        return VisualizationData(self.width, self.height)
        
    def render(self, viz_data: VisualizationData):
        """Render visualization data to terminal"""
        # Move cursor to top-left
        self.console.print('\033[H', end='')
        
        # Render each line
        for y in range(min(viz_data.height, self.height)):
            line_text = Text()
            
            for x in range(min(viz_data.width, self.width)):
                char = viz_data.get_char(x, y)
                color = viz_data.colors[y][x] if y < len(viz_data.colors) and x < len(viz_data.colors[y]) else None
                
                if color and color in self.colors:
                    line_text.append(char, style=self.colors[color])
                else:
                    line_text.append(char)
                    
            self.console.print(line_text, end='')
            
            # Add newline except for last line
            if y < min(viz_data.height, self.height) - 1:
                self.console.print()
                
        # Force flush output
        self.console.file.flush()
        
    def cleanup(self):
        """Restore terminal state"""
        self.console.print('\033[?25h', end='')  # Show cursor
        self.console.clear()
        
    @staticmethod
    def intensity_to_char(intensity: float, char_set: str = None) -> str:
        """Convert intensity (0-1) to ASCII character"""
        if char_set is None:
            char_set = TerminalRenderer.ASCII_CHARS
            
        if intensity <= 0:
            return char_set[0]
        if intensity >= 1:
            return char_set[-1]
            
        index = int(intensity * (len(char_set) - 1))
        return char_set[index]
        
    @staticmethod
    def frequency_to_color(frequency: float, max_freq: float = 22050) -> str:
        """Map frequency to color (bass=red, mid=green, treble=blue)"""
        normalized = frequency / max_freq
        
        if normalized < 0.3:  # Bass frequencies
            return 'red'
        elif normalized < 0.7:  # Mid frequencies
            return 'green'
        else:  # Treble frequencies
            return 'blue'
            
    @staticmethod
    def amplitude_to_color(amplitude: float) -> str:
        """Map amplitude to color intensity"""
        if amplitude > 0.8:
            return 'bright_white'
        elif amplitude > 0.6:
            return 'white'
        elif amplitude > 0.4:
            return 'bright_yellow'
        elif amplitude > 0.2:
            return 'yellow'
        else:
            return 'dim'
            
    def draw_text(self, canvas: VisualizationData, x: int, y: int, 
                  text: str, color: Optional[str] = None):
        """Draw text at position"""
        for i, char in enumerate(text):
            canvas.set_char(x + i, y, char, color)
            
    def draw_line(self, canvas: VisualizationData, x1: int, y1: int, 
                  x2: int, y2: int, char: str = '█', color: Optional[str] = None):
        """Draw line using Bresenham's algorithm"""
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        
        while True:
            canvas.set_char(x, y, char, color)
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
                
    def draw_circle(self, canvas: VisualizationData, cx: int, cy: int, 
                    radius: int, char: str = '█', color: Optional[str] = None):
        """Draw circle outline"""
        for angle in range(0, 360, 5):  # Every 5 degrees
            x = int(cx + radius * np.cos(np.radians(angle)))
            y = int(cy + radius * np.sin(np.radians(angle)))
            canvas.set_char(x, y, char, color)
            
    def draw_bar(self, canvas: VisualizationData, x: int, height: int, 
                 max_height: int, char: str = '█', color: Optional[str] = None):
        """Draw vertical bar"""
        for y in range(max_height - height, max_height):
            if y >= 0:
                canvas.set_char(x, y, char, color)
                
    def get_fps(self) -> float:
        """Calculate current FPS"""
        current_time = time.time()
        if self.last_render_time > 0:
            fps = 1.0 / (current_time - self.last_render_time)
        else:
            fps = 0.0
        self.last_render_time = current_time
        return fps