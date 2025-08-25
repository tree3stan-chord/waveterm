"""
Visualization registry system for Wave
Central registration and discovery of all visualization modes
"""

from typing import Dict, Any, Callable, Optional
from ..render.terminal import VisualizationData
try:
    from ..audio.processor import AudioData
except ImportError:
    pass

from .basic import BasicVisualizations
from .advanced import AdvancedVisualizations  
from .extreme import ExtremeVisualizations

class VisualizationRegistry:
    """Central registry for all visualization modes"""
    
    def __init__(self):
        self._modes: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, Any] = {}
        self._register_builtin_modes()
    
    def register(self, mode_id: str, name: str, func: Callable, 
                category: str = "custom", description: str = "") -> None:
        """Register a visualization mode"""
        self._modes[mode_id] = {
            "name": name,
            "function": func,
            "category": category,
            "description": description
        }
    
    def get_mode(self, mode_id: str) -> Optional[Callable]:
        """Get visualization function by mode ID"""
        mode_info = self._modes.get(mode_id)
        return mode_info["function"] if mode_info else None
    
    def get_all_modes(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered modes"""
        return self._modes.copy()
    
    def get_modes_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get modes filtered by category"""
        return {
            mode_id: info 
            for mode_id, info in self._modes.items() 
            if info["category"] == category
        }
    
    def list_categories(self) -> list:
        """Get all available categories"""
        return list(set(info["category"] for info in self._modes.values()))
    
    def _register_builtin_modes(self):
        """Register all built-in visualization modes"""
        # Create instances
        basic = BasicVisualizations()
        advanced = AdvancedVisualizations()
        extreme = ExtremeVisualizations()
        
        # Store instances for reuse
        self._instances['basic'] = basic
        self._instances['advanced'] = advanced
        self._instances['extreme'] = extreme
        
        # Basic visualizations
        self.register("bars", "Frequency Bars", basic.frequency_bars, 
                     "basic", "Classic frequency spectrum bars")
        self.register("wave", "Waveform", basic.waveform,
                     "basic", "Oscilloscope-style waveform display")
        self.register("matrix", "Matrix Rain", basic.matrix_rain,
                     "basic", "Matrix-style falling character rain")
        self.register("particles", "Particle Field", basic.particle_field,
                     "basic", "ASCII particle field that reacts to audio")
        self.register("circle", "Circular Wave", basic.circular_wave,
                     "basic", "Circular frequency display radiating from center")
        
        # Advanced visualizations
        self.register("starfield", "Starfield Warp", advanced.starfield_warp,
                     "advanced", "Stars flying toward screen, faster with audio")
        self.register("fire", "Fire Flames", advanced.fire_flames,
                     "advanced", "ASCII fire effect that reacts to audio")
        self.register("ocean", "Ocean Waves", advanced.ocean_waves,
                     "advanced", "Wave interference patterns")
        self.register("dna", "DNA Helix", advanced.dna_helix,
                     "advanced", "Rotating DNA double helix")
        self.register("neural", "Neural Network", advanced.neural_network,
                     "advanced", "Neural network with pulsing connections")
        
        # Extreme visualizations
        self.register("glitch", "Glitch Art", extreme.glitch_art,
                     "extreme", "Digital glitch effects with corruption")
        self.register("void", "Void Tentacles", extreme.void_tentacles,
                     "extreme", "Lovecraftian tentacles from the void")
        self.register("hypercube", "4D Hypercube", extreme.hypercube_4d,
                     "extreme", "4D tesseract projection")
        self.register("fractal", "ASCII Fractal", extreme.ascii_fractal,
                     "extreme", "Recursive fractal tree generation")
        self.register("portal", "Dimensional Portal", extreme.dimensional_portal,
                     "extreme", "Swirling interdimensional portal")

# Global registry instance
_registry = VisualizationRegistry()

def register_mode(mode_id: str, name: str, func: Callable, 
                 category: str = "custom", description: str = "") -> None:
    """Register a visualization mode globally"""
    _registry.register(mode_id, name, func, category, description)

def get_mode(mode_id: str) -> Optional[Callable]:
    """Get visualization function by mode ID"""
    return _registry.get_mode(mode_id)

def get_all_modes() -> Dict[str, Dict[str, Any]]:
    """Get all registered visualization modes"""
    return _registry.get_all_modes()

def get_modes_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Get modes filtered by category"""
    return _registry.get_modes_by_category(category)

def list_categories() -> list:
    """Get all available categories"""
    return _registry.list_categories()