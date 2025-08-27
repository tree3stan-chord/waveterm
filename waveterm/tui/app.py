"""
Main Textual TUI application for WaveTerm
Provides interactive terminal interface for music visualization
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static
from textual.binding import Binding

from ..core.logger import get_logger
from .widgets import VisualizationDisplay, ControlPanel, StatusBar, ModeSelector
from .modals import HelpModal, SettingsModal, ModeSelectModal, FilePickerModal, ExportModal
from ..core.app import WaveApp

logger = get_logger('tui.app')


class WaveTermTUI(App):
    """Modern TUI application for WaveTerm using Textual"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #control_panel {
        dock: top;
        height: 3;
        background: $surface;
        border: solid $primary;
    }
    
    #visualization_area {
        height: 1fr;
        background: $background;
        border: solid $accent;
    }
    
    #status_bar {
        dock: bottom;
        height: 1;
        background: $surface;
    }
    
    ModeSelector {
        width: 20;
    }
    
    .control_group {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("1", "mode_1", "1-9 Mode", priority=True, show=True),
        Binding("2", "mode_2", "", priority=True, show=False),
        Binding("3", "mode_3", "", priority=True, show=False),
        Binding("4", "mode_4", "", priority=True, show=False),
        Binding("5", "mode_5", "", priority=True, show=False),
        Binding("6", "mode_6", "", priority=True, show=False),
        Binding("7", "mode_7", "", priority=True, show=False),
        Binding("8", "mode_8", "", priority=True, show=False),
        Binding("9", "mode_9", "", priority=True, show=False),
        Binding("space", "pause", "Pause/Resume", priority=True),
        Binding("h", "help", "Help", priority=True),
        Binding("?", "help", "Help", priority=True, show=False),
    ]
    
    def __init__(self, mode: str = "bars", input_source: str = "sim", file_path: str = None, **kwargs):
        super().__init__(**kwargs)
        self.viz_mode = mode
        self.audio_input = input_source
        self.audio_file_path = file_path
        self.wave_app: WaveApp = None
        self.paused = False
        
        # Initialize the core WaveTerm app
        self._init_wave_app()
    
    def _init_wave_app(self):
        """Initialize the core WaveTerm application"""
        try:
            self.wave_app = WaveApp(
                mode=self.viz_mode,
                input_source=self.audio_input,
                file_path=self.audio_file_path,
                headless=True,  # We'll handle the rendering in TUI
                fps=30
            )
            logger.info(f"Initialized WaveApp with mode={self.viz_mode}, input={self.audio_input}")
        except Exception as e:
            logger.error(f"Failed to initialize WaveApp: {e}")
    
    def compose(self) -> ComposeResult:
        """Create the TUI layout"""
        yield Header(show_clock=True)
        
        # Removed redundant and broken control panel
        
        yield VisualizationDisplay(self.wave_app, id="visualization_area")
        yield StatusBar(id="status_bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted"""
        logger.info("WaveTerm TUI mounted successfully")
        self.title = f"WaveTerm v0.6.7 - {self.viz_mode.title()} Mode"
        
        # Start visualization updates at much slower rate for responsiveness
        self.set_interval(1/5, self._update_visualization)  # 5 FPS to reduce input lag
    
    def _update_visualization(self) -> None:
        """Update the visualization display"""
        if not self.paused and self.wave_app:
            try:
                viz_display = self.query_one("#visualization_area", VisualizationDisplay)
                viz_display.update_visualization()
                
                # Skip frequent status bar updates to reduce lag
                # Only update status occasionally
                import time
                if not hasattr(self, '_last_status_update'):
                    self._last_status_update = 0
                
                if time.time() - self._last_status_update > 2:  # Update status every 2 seconds only
                    status_bar = self.query_one("#status_bar", StatusBar)
                    status_bar.update_status(self.wave_app, self.viz_mode)
                    self._last_status_update = time.time()
            except Exception as e:
                logger.error(f"Visualization update error: {e}")
                # Don't crash the TUI, just log the error
    
    def action_quit(self) -> None:
        """Handle quit action"""
        logger.info("TUI quit requested")
        if self.wave_app:
            self.wave_app.cleanup()
        self.exit()
    
    def action_pause(self) -> None:
        """Handle pause/resume action"""
        self.paused = not self.paused
        status = "Paused" if self.paused else "Resumed" 
        logger.info(f"Visualization {status}")
        
        # Update title to show paused state
        pause_indicator = " [PAUSED]" if self.paused else ""
        self.title = f"WaveTerm v0.6.7 - {self.viz_mode.title()} Mode{pause_indicator}"
    
    def action_mode_1(self) -> None: self.change_mode("bars")
    def action_mode_2(self) -> None: self.change_mode("wave") 
    def action_mode_3(self) -> None: self.change_mode("matrix")
    def action_mode_4(self) -> None: self.change_mode("particles")
    def action_mode_5(self) -> None: self.change_mode("circle")
    def action_mode_6(self) -> None: self.change_mode("starfield")
    def action_mode_7(self) -> None: self.change_mode("fire")
    def action_mode_8(self) -> None: self.change_mode("ocean")
    def action_mode_9(self) -> None: self.change_mode("dna")
    
    def change_mode(self, new_mode: str) -> None:
        """Change visualization mode"""
        if self.wave_app and self.wave_app.set_mode(new_mode):
            self.viz_mode = new_mode
            self.title = f"WaveTerm v0.6.6 - {new_mode.title()} Mode"
            logger.info(f"Changed mode to: {new_mode}")
            self.notify(f"Switched to {new_mode.title()} mode", timeout=2)
        else:
            logger.warning(f"Failed to change mode to: {new_mode}")
            self.notify(f"Failed to switch to {new_mode}", severity="error")
    
    def change_input(self, new_input: str) -> None:
        """Change audio input source"""
        # This would require reinitializing the WaveApp
        logger.info(f"Input change requested: {new_input} (requires restart)")
        
    # Removed settings modal - too slow and unresponsive
    
    def action_help(self) -> None:
        """Show help overlay"""
        help_text = """🌊 WaveTerm v0.6.6 - Help

🎹 Visualization Modes:
  1 - Bars        2 - Wave        3 - Matrix
  4 - Particles   5 - Circle      6 - Starfield  
  7 - Fire        8 - Ocean       9 - DNA

🎛️ Controls:
  SPACE - Pause/Resume
  H / ? - Show this help
  Q     - Quit

📡 Audio Input: Simulated (headless mode)
🎨 Current Mode: """ + self.viz_mode.title() + """

Press any key to continue..."""
        
        self.notify(help_text, title="Help", timeout=10)
    
    # Removed all modal actions - they were too slow and unresponsive
    
    def _apply_settings(self, settings: dict) -> None:
        """Apply settings changes to the running app"""
        try:
            # Update sensitivity
            if 'sensitivity' in settings and self.wave_app:
                if self.wave_app.audio_processor:
                    self.wave_app.audio_processor.sensitivity = settings['sensitivity']
                elif self.wave_app.audio_simulator:
                    # Simulators can also have sensitivity adjustments
                    pass
            
            # Update FPS (by changing update interval)
            if 'fps' in settings:
                fps = settings['fps']
                if hasattr(self, '_visualization_timer'):
                    # Update the timer interval
                    self.set_interval(1/fps, self._update_visualization)
            
            logger.info("Settings applied successfully")
            self.notify("Settings updated!", severity="information")
            
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            self.notify("Failed to apply settings", severity="error")
    
    def _start_export(self, export_config: dict) -> None:
        """Start export process with given configuration"""
        try:
            # This would integrate with the export system
            self.notify(f"Export started: {export_config['output_file']}", severity="information")
            logger.info(f"Export process started: {export_config}")
            # TODO: Implement actual export functionality
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            self.notify("Export failed", severity="error")
    
    # Removed modal click handlers - using direct key bindings only