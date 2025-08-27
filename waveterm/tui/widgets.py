"""
Custom Textual widgets for WaveTerm TUI
"""

import time
from typing import Optional

from textual.widgets import Static, Select, Button, Label, ProgressBar
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.text import Text

from ..core.logger import get_logger

logger = get_logger('tui.widgets')


class ModeSelector(Static):
    """Widget for selecting visualization modes"""
    
    current_mode = reactive("bars")
    
    def __init__(self, initial_mode: str = "bars", **kwargs):
        super().__init__(**kwargs)
        self.current_mode = initial_mode
        self.modes = [
            ("bars", "Frequency Bars"),
            ("waveform", "Waveform"),  
            ("matrix", "Matrix Rain"),
            ("particles", "Particle Field"),
            ("circle", "Circular Wave"),
            ("starfield", "Starfield Warp"),
            ("fire", "Fire Flames"),
            ("ocean", "Ocean Waves"),
            ("dna", "DNA Helix"),
        ]
    
    def render(self) -> RenderableType:
        """Render the mode selector"""
        current_name = dict(self.modes).get(self.current_mode, self.current_mode.title())
        
        text = Text()
        text.append("Mode: ", style="bold blue")
        text.append(f"[{current_name}]", style="bold cyan")
        text.append(" ▼", style="dim")
        
        return Panel(text, height=3, title="Visualization")
    
    def set_mode(self, mode: str) -> None:
        """Set the current mode"""
        self.current_mode = mode
        self.refresh()


class ControlPanel(Static):
    """Widget for audio input and general controls"""
    
    def __init__(self, input_source: str = "sim", **kwargs):
        super().__init__(**kwargs)
        self.input_source = input_source
        self.inputs = [
            ("sim", "Simulation"),
            ("mic", "Microphone"),
            ("file", "Audio File"),
        ]
    
    def render(self) -> RenderableType:
        """Render the control panel"""
        input_name = dict(self.inputs).get(self.input_source, self.input_source.title())
        
        text = Text()
        text.append("Input: ", style="bold green")
        text.append(f"[{input_name}]", style="bold yellow")
        text.append("  ", style="dim")
        text.append("[Settings]", style="bold magenta")
        text.append("  ", style="dim")
        text.append("[Help]", style="bold white")
        
        return Panel(text, height=3, title="Controls")


class VisualizationDisplay(Static):
    """Main visualization display area"""
    
    def __init__(self, wave_app, **kwargs):
        super().__init__(**kwargs)
        self.wave_app = wave_app
        self.last_update = time.time()
        self.frame_count = 0
        
    def render(self) -> RenderableType:
        """Render the visualization"""
        if not self.wave_app:
            return Panel(
                Text("Initializing visualization...", justify="center", style="dim"),
                height=self.size.height,
                title="🌊 WaveTerm Visualization"
            )
        
        # Get current audio data
        try:
            if self.wave_app.audio_processor:
                audio_data = self.wave_app.audio_processor.get_current_data()
            else:
                audio_data = self.wave_app.audio_simulator.generate_audio_data()
            
            if audio_data is None:
                return Panel(
                    Text("No audio data available", justify="center", style="red"),
                    height=self.size.height,
                    title="🌊 WaveTerm Visualization"
                )
            
            # Generate visualization
            viz_data = self.wave_app.viz_manager.generate(
                self.wave_app.current_mode, 
                audio_data
            )
            
            # Convert visualization canvas to Rich renderable
            viz_content = self._canvas_to_rich(viz_data)
            
            return Panel(
                viz_content,
                height=self.size.height,
                title=f"🌊 {self.wave_app.current_mode.title()} Visualization",
                border_style="bright_blue"
            )
            
        except Exception as e:
            logger.error(f"Visualization render error: {e}")
            return Panel(
                Text(f"Visualization Error: {e}", justify="center", style="red"),
                height=self.size.height,
                title="🌊 WaveTerm Visualization"
            )
    
    def _canvas_to_rich(self, canvas) -> Text:
        """Convert visualization canvas to Rich Text object"""
        text = Text()
        
        # Check if it's a VisualizationData object
        if hasattr(canvas, 'buffer') and hasattr(canvas, 'colors'):
            # Standard VisualizationData format
            for y in range(canvas.height):
                line_text = Text()
                for x in range(canvas.width):
                    char = canvas.buffer[y][x]
                    color = canvas.colors[y][x]
                    if color:
                        line_text.append(char, style=color)
                    else:
                        line_text.append(char)
                text.append_text(line_text)
                if y < canvas.height - 1:  # Don't add newline after last row
                    text.append("\n")
        elif hasattr(canvas, 'data'):
            # Alternative canvas format
            for row in canvas.data:
                line = ""
                for char_data in row:
                    if isinstance(char_data, dict) and 'char' in char_data:
                        line += char_data['char']
                    elif isinstance(char_data, str):
                        line += char_data
                    else:
                        line += " "
                text.append(line + "\n")
        else:
            # Fallback - show debug info
            text.append("Canvas format: " + str(type(canvas)), style="dim")
            if hasattr(canvas, '__dict__'):
                text.append("\nAttributes: " + str(list(canvas.__dict__.keys())), style="dim")
        
        return text
    
    def update_visualization(self) -> None:
        """Update the visualization display"""
        self.frame_count += 1
        current_time = time.time()
        
        # Refresh the display
        self.refresh()
        
        # Update timing info
        if current_time - self.last_update >= 1.0:
            self.last_update = current_time
            self.frame_count = 0


class StatusBar(Static):
    """Bottom status bar with audio level and controls"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_level = 0.0
        self.fps = 0
        self.last_fps_update = time.time()
        self.frame_count = 0
    
    def render(self) -> RenderableType:
        """Render the status bar"""
        # Audio level bar
        level_bars = int(self.audio_level * 20)
        level_display = "█" * level_bars + "░" * (20 - level_bars)
        
        text = Text()
        text.append("Audio: ", style="bold")
        text.append(level_display, style="green")
        text.append(f" {int(self.audio_level * 100)}%", style="bright_green")
        text.append("  │  ", style="dim")
        text.append(f"FPS: {self.fps:02d}", style="bold blue")
        text.append("  │  ", style="dim") 
        text.append("[SPACE] Pause", style="dim")
        text.append("  │  ", style="dim")
        text.append("[Q] Quit", style="dim")
        
        return text
    
    def update_status(self, wave_app, current_mode: str) -> None:
        """Update status information"""
        current_time = time.time()
        self.frame_count += 1
        
        # Update FPS counter
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_update = current_time
        
        # Update audio level
        if wave_app:
            try:
                if wave_app.audio_processor:
                    audio_data = wave_app.audio_processor.get_current_data()
                else:
                    audio_data = wave_app.audio_simulator.generate_audio_data()
                
                if audio_data:
                    self.audio_level = min(1.0, audio_data.overall_amplitude)
            except Exception as e:
                logger.debug(f"Status update error: {e}")
        
        self.refresh()