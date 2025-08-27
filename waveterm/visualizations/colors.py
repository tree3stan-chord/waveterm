"""
Color palette system for WaveTerm visualizations
Provides rich color themes and ASCII character sets for enhanced visual effects
"""

from typing import Dict, List, Tuple
from enum import Enum


class ColorPalette(Enum):
    """Available color palettes for visualizations"""
    DEFAULT = "default"
    NEON = "neon" 
    MATRIX = "matrix"
    FIRE = "fire"
    OCEAN = "ocean"
    CYBERPUNK = "cyberpunk"
    RETRO = "retro"
    RAINBOW = "rainbow"
    MONOCHROME = "monochrome"


class ASCIISet(Enum):
    """ASCII character sets for different visual densities"""
    BASIC = "basic"
    DENSE = "dense" 
    BLOCKS = "blocks"
    DOTS = "dots"
    EXPLOSION = "explosion"
    ORGANIC = "organic"
    GEOMETRIC = "geometric"


class VisualizationColors:
    """Color and character management for visualizations"""
    
    # ASCII character sets by density
    ASCII_SETS = {
        ASCIISet.BASIC: " .·:¦|=+*#%@█",
        ASCIISet.DENSE: " .'`^\",:;Il!i><~+_-?][}{1)(|\\+@#$%&*0123456789",
        ASCIISet.BLOCKS: " ░▒▓█",
        ASCIISet.DOTS: " ·°∘○●◉◎◇◆◯⬤",
        ASCIISet.EXPLOSION: "*+×÷±°∘•◦‧∴∵∶∷⁂⁎⁕⁖⁙⁛⁜⁝⁞",
        ASCIISet.ORGANIC: " .,·:;~^\"'`°∘•◦◌○●◉⬤☼☽☾✦✧✨✩✪✫✬✭✮✯✰",
        ASCIISet.GEOMETRIC: " .-=≡|¦‖▌▐█▄▀▬▭▮▯◢◣◤◥◀▶▲▼◆◇○◯□■△▽"
    }
    
    # Color palettes with Rich color names and styles
    COLOR_PALETTES = {
        ColorPalette.DEFAULT: {
            'bg': 'black',
            'primary': 'white', 
            'secondary': 'bright_white',
            'accent': 'blue',
            'highlight': 'bright_blue',
            'low': 'dim white',
            'med': 'white',
            'high': 'bright_white bold'
        },
        
        ColorPalette.NEON: {
            'bg': 'black',
            'primary': 'bright_green',
            'secondary': 'bright_cyan', 
            'accent': 'bright_magenta',
            'highlight': 'bright_yellow',
            'low': 'green',
            'med': 'bright_green',
            'high': 'bright_cyan bold'
        },
        
        ColorPalette.MATRIX: {
            'bg': 'black',
            'primary': 'green',
            'secondary': 'bright_green',
            'accent': 'white',
            'highlight': 'bright_white',
            'low': 'dim green',
            'med': 'green',
            'high': 'bright_green bold'
        },
        
        ColorPalette.FIRE: {
            'bg': 'black',
            'primary': 'red',
            'secondary': 'bright_red',
            'accent': 'yellow', 
            'highlight': 'bright_yellow',
            'low': 'red',
            'med': 'bright_red',
            'high': 'bright_yellow bold'
        },
        
        ColorPalette.OCEAN: {
            'bg': 'black',
            'primary': 'blue',
            'secondary': 'bright_blue',
            'accent': 'cyan',
            'highlight': 'bright_cyan', 
            'low': 'blue',
            'med': 'bright_blue',
            'high': 'bright_cyan bold'
        },
        
        ColorPalette.CYBERPUNK: {
            'bg': 'black',
            'primary': 'bright_magenta',
            'secondary': 'bright_cyan',
            'accent': 'bright_yellow',
            'highlight': 'bright_white',
            'low': 'magenta',
            'med': 'bright_magenta',
            'high': 'bright_cyan bold'
        },
        
        ColorPalette.RETRO: {
            'bg': 'black',
            'primary': 'yellow',
            'secondary': 'bright_yellow',
            'accent': 'magenta',
            'highlight': 'bright_magenta',
            'low': 'dim yellow',
            'med': 'yellow', 
            'high': 'bright_yellow bold'
        },
        
        ColorPalette.RAINBOW: {
            'bg': 'black',
            'primary': 'red',
            'secondary': 'yellow', 
            'accent': 'green',
            'highlight': 'bright_blue',
            'low': 'red',
            'med': 'yellow',
            'high': 'bright_blue bold'
        },
        
        ColorPalette.MONOCHROME: {
            'bg': 'black',
            'primary': 'bright_black',
            'secondary': 'white',
            'accent': 'bright_white',
            'highlight': 'bright_white bold',
            'low': 'bright_black',
            'med': 'white',
            'high': 'bright_white bold'
        }
    }
    
    def __init__(self, palette: ColorPalette = ColorPalette.DEFAULT):
        self.palette = palette
        self.colors = self.COLOR_PALETTES[palette]
        self.current_ascii_set = ASCIISet.BASIC
    
    def get_chars(self, ascii_set: ASCIISet = None) -> str:
        """Get ASCII character set"""
        if ascii_set is None:
            ascii_set = self.current_ascii_set
        return self.ASCII_SETS[ascii_set]
    
    def get_chars_reversed(self, ascii_set: ASCIISet = None) -> str:
        """Get ASCII character set in reverse (for intensity mapping)"""
        return self.get_chars(ascii_set)[::-1]
    
    def get_color_for_intensity(self, intensity: float, layer: str = 'primary') -> str:
        """Get color based on intensity level (0.0 to 1.0)"""
        if intensity < 0.3:
            return self.colors['low']
        elif intensity < 0.7:
            return self.colors['med'] 
        else:
            return self.colors['high']
    
    def get_char_for_intensity(self, intensity: float, ascii_set: ASCIISet = None) -> str:
        """Get ASCII character based on intensity"""
        chars = self.get_chars_reversed(ascii_set)
        if len(chars) == 0:
            return ' '
        index = min(int(intensity * len(chars)), len(chars) - 1)
        return chars[index]
    
    def set_ascii_set(self, ascii_set: ASCIISet):
        """Change the current ASCII character set"""
        self.current_ascii_set = ascii_set
    
    def set_palette(self, palette: ColorPalette):
        """Change the color palette"""
        self.palette = palette
        self.colors = self.COLOR_PALETTES[palette]
    
    def get_palette_info(self) -> Dict[str, str]:
        """Get current palette information"""
        return {
            'name': self.palette.value,
            'colors': self.colors,
            'ascii_set': self.current_ascii_set.value
        }


# Global color manager instance
_color_manager = VisualizationColors()

def get_color_manager() -> VisualizationColors:
    """Get the global color manager instance"""
    return _color_manager

def set_global_palette(palette: ColorPalette):
    """Set the global color palette"""
    _color_manager.set_palette(palette)

def set_global_ascii_set(ascii_set: ASCIISet):
    """Set the global ASCII character set"""
    _color_manager.set_ascii_set(ascii_set)

def get_chars(ascii_set: ASCIISet = None) -> str:
    """Convenience function to get ASCII chars"""
    return _color_manager.get_chars(ascii_set)

def get_chars_reversed(ascii_set: ASCIISet = None) -> str:
    """Convenience function to get reversed ASCII chars"""
    return _color_manager.get_chars_reversed(ascii_set)

def get_color_for_intensity(intensity: float, layer: str = 'primary') -> str:
    """Convenience function to get color for intensity"""
    return _color_manager.get_color_for_intensity(intensity, layer)

def get_char_for_intensity(intensity: float, ascii_set: ASCIISet = None) -> str:
    """Convenience function to get char for intensity"""
    return _color_manager.get_char_for_intensity(intensity, ascii_set)