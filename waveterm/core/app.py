"""
Main application class for Wave terminal music visualizer
Modern architecture with configuration and simulation support
"""

import time
import threading
from typing import Optional
from pathlib import Path

try:
    from ..audio.processor import AudioProcessor
except ImportError:
    AudioProcessor = None
    
from ..audio.simulator import AudioSimulator
from ..render.terminal import TerminalRenderer
from ..visualizations.manager import VisualizationManager
from ..config.config import WaveConfig
from .logger import get_logger

logger = get_logger('core.app')

class WaveApp:
    def __init__(self, mode: str = "bars", input_source: str = "sim", 
                 file_path: Optional[str] = None, fps: int = 30, 
                 sensitivity: float = 1.0, config: Optional[WaveConfig] = None,
                 headless: bool = False, export_dir: Optional[str] = None):
        
        # Configuration
        self.config = config or WaveConfig()
        
        # App settings
        self.current_mode = mode
        self.input_source = input_source
        self.file_path = file_path
        self.fps = fps
        self.sensitivity = sensitivity
        self.headless = headless
        self.export_dir = export_dir
        self.running = False
        
        # Initialize components
        self.renderer = TerminalRenderer()
        self.viz_manager = VisualizationManager()
        
        # Audio system (processor or simulator)
        if input_source == "sim" or headless or not AudioProcessor:
            self.audio_simulator = AudioSimulator('electronic')
            self.audio_processor = None
        else:
            try:
                self.audio_processor = AudioProcessor(
                    source=input_source,
                    file_path=file_path,
                    sensitivity=sensitivity
                )
                self.audio_simulator = None
            except Exception as e:
                logger.warning(f"Audio system unavailable, falling back to simulation: {e}")
                self.audio_simulator = AudioSimulator('electronic')
                self.audio_processor = None
        
        # Threading
        self.audio_thread: Optional[threading.Thread] = None
        
    def run(self):
        """Main application loop"""
        try:
            self.running = True
            
            # Initialize renderer
            self.renderer.initialize()
            
            # Initialize audio if using real audio
            if self.audio_processor:
                self.audio_processor.initialize()
                
                # Start audio processing in separate thread
                self.audio_thread = threading.Thread(target=self.audio_processor.start_processing)
                self.audio_thread.daemon = True
                self.audio_thread.start()
            
            # Main render loop
            target_frame_time = 1.0 / self.fps
            
            while self.running:
                frame_start = time.time()
                
                # Get audio data (real or simulated)
                if self.audio_processor:
                    audio_data = self.audio_processor.get_current_data()
                else:
                    audio_data = self.audio_simulator.generate_audio_data()
                
                if audio_data is not None:
                    # Generate visualization
                    viz_data = self.viz_manager.generate(self.current_mode, audio_data)
                    
                    # Export frame if requested
                    if self.export_dir:
                        self._export_frame(viz_data, frame_start)
                    
                    # Render to terminal (unless pure export mode)
                    if not self.export_dir or not self.headless:
                        self.renderer.render(viz_data)
                
                # Handle input (non-blocking)
                self._handle_input()
                
                # Frame rate limiting
                frame_time = time.time() - frame_start
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)
                    
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.cleanup()
    
    def _handle_input(self):
        """Handle keyboard input for mode switching and quit"""
        # TODO: Implement non-blocking keyboard input
        # For now, this is handled by the CLI layer
        pass
    
    def _export_frame(self, viz_data, timestamp):
        """Export frame to file (basic implementation)"""
        # TODO: Implement proper export system
        pass
    
    def set_mode(self, mode: str) -> bool:
        """Change visualization mode"""
        if self.viz_manager.set_mode(mode):
            self.current_mode = mode
            return True
        return False
    
    def set_audio_pattern(self, pattern: str) -> bool:
        """Change audio simulation pattern"""
        if self.audio_simulator:
            return self.audio_simulator.set_pattern(pattern)
        return False
    
    def get_available_modes(self) -> list:
        """Get available visualization modes"""
        return self.viz_manager.get_available_modes()
    
    def get_available_patterns(self) -> list:
        """Get available audio patterns"""
        if self.audio_simulator:
            return self.audio_simulator.get_available_patterns()
        return []
    
    def cleanup(self):
        """Clean up resources"""
        self.running = False
        
        if self.audio_processor:
            self.audio_processor.stop()
            
        if self.renderer:
            self.renderer.cleanup()
            
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)