"""
Visualization manager for Wave
Coordinates different visualization modes and effects using the registry system
"""

import time
from typing import Optional
try:
    from ..audio.processor import AudioData
except ImportError:
    pass
from ..render.terminal import VisualizationData, TerminalRenderer
from .registry import get_mode, get_all_modes

class VisualizationManager:
    """Manages and coordinates different visualization modes using registry"""
    
    def __init__(self):
        self.renderer = TerminalRenderer()
        self.current_mode = 'bars'
        self.start_time = time.time()
        
    def generate(self, mode: str, audio_data: 'AudioData') -> VisualizationData:
        """Generate visualization for given mode and audio data"""
        # Get visualization function from registry
        viz_func = get_mode(mode)
        
        if viz_func is None:
            # Fallback to bars
            viz_func = get_mode('bars')
            if viz_func is None:
                raise RuntimeError("No visualizations available!")
            
        # Create canvas
        canvas = self.renderer.create_canvas()
        
        # Calculate time elapsed for time-based effects
        elapsed_time = time.time() - self.start_time
        
        # Call visualization function
        try:
            viz_func(canvas, audio_data, elapsed_time)
        except Exception as e:
            # Fallback to bars on error
            print(f"Visualization error in {mode}: {e}")
            fallback_func = get_mode('bars')
            if fallback_func:
                fallback_func(canvas, audio_data, elapsed_time)
            
        return canvas
        
    def get_available_modes(self) -> list:
        """Get list of available visualization modes"""
        return list(get_all_modes().keys())
        
    def set_mode(self, mode: str) -> bool:
        """Set current visualization mode"""
        if get_mode(mode) is not None:
            self.current_mode = mode
            return True
        return False
    
    def get_mode_info(self, mode: str) -> Optional[dict]:
        """Get information about a specific mode"""
        all_modes = get_all_modes()
        return all_modes.get(mode)