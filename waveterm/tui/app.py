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
        Binding("1,2,3,4,5,6,7,8,9", "mode", "Mode", priority=True),
        Binding("space", "pause", "Pause/Resume", priority=True),
        Binding("s", "settings", "Settings", priority=True),
        Binding("h,?", "help", "Help", priority=True),
    ]
    
    def __init__(self, mode: str = "bars", input_source: str = "sim", **kwargs):
        super().__init__(**kwargs)
        self.current_mode = mode
        self.input_source = input_source
        self.wave_app: WaveApp = None
        self.paused = False
        
        # Initialize the core WaveTerm app
        self._init_wave_app()
    
    def _init_wave_app(self):
        """Initialize the core WaveTerm application"""
        try:
            self.wave_app = WaveApp(
                mode=self.current_mode,
                input_source=self.input_source,
                headless=True,  # We'll handle the rendering in TUI
                fps=30
            )
            logger.info(f"Initialized WaveApp with mode={self.current_mode}, input={self.input_source}")
        except Exception as e:
            logger.error(f"Failed to initialize WaveApp: {e}")
    
    def compose(self) -> ComposeResult:
        """Create the TUI layout"""
        yield Header(show_clock=True)
        
        with Container(id="control_panel"):
            with Horizontal():
                yield ModeSelector(self.current_mode, id="mode_selector")
                yield ControlPanel(self.input_source, id="controls")
        
        yield VisualizationDisplay(self.wave_app, id="visualization_area")
        yield StatusBar(id="status_bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted"""
        logger.info("WaveTerm TUI mounted successfully")
        self.title = f"WaveTerm v0.3.0 - {self.current_mode.title()} Mode"
        
        # Start visualization updates
        self.set_interval(1/30, self._update_visualization)  # 30 FPS
    
    def _update_visualization(self) -> None:
        """Update the visualization display"""
        if not self.paused and self.wave_app:
            viz_display = self.query_one("#visualization_area", VisualizationDisplay)
            viz_display.update_visualization()
            
            # Update status bar
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(self.wave_app, self.current_mode)
    
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
        self.title = f"WaveTerm v0.3.0 - {self.current_mode.title()} Mode{pause_indicator}"
    
    def action_mode(self, mode_key: str) -> None:
        """Handle mode switching via number keys"""
        mode_map = {
            "1": "bars", "2": "waveform", "3": "matrix", "4": "particles",
            "5": "circle", "6": "starfield", "7": "fire", "8": "ocean", "9": "dna"
        }
        
        if mode_key in mode_map:
            new_mode = mode_map[mode_key]
            self.change_mode(new_mode)
    
    def change_mode(self, new_mode: str) -> None:
        """Change visualization mode"""
        if self.wave_app and self.wave_app.set_mode(new_mode):
            self.current_mode = new_mode
            self.title = f"WaveTerm v0.3.0 - {new_mode.title()} Mode"
            
            # Update mode selector
            mode_selector = self.query_one("#mode_selector", ModeSelector)
            mode_selector.set_mode(new_mode)
            
            logger.info(f"Changed mode to: {new_mode}")
        else:
            logger.warning(f"Failed to change mode to: {new_mode}")
    
    def change_input(self, new_input: str) -> None:
        """Change audio input source"""
        # This would require reinitializing the WaveApp
        logger.info(f"Input change requested: {new_input} (requires restart)")
        
    def action_settings(self) -> None:
        """Show settings dialog"""
        # TODO: Implement settings modal
        logger.info("Settings requested")
    
    def action_help(self) -> None:
        """Show help dialog"""  
        # TODO: Implement help modal
        logger.info("Help requested")