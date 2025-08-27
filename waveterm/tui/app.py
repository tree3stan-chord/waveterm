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
        Binding("1", "mode('1')", "1-9 Mode", priority=True, show=True),
        Binding("2", "mode('2')", "", priority=True, show=False),
        Binding("3", "mode('3')", "", priority=True, show=False),
        Binding("4", "mode('4')", "", priority=True, show=False),
        Binding("5", "mode('5')", "", priority=True, show=False),
        Binding("6", "mode('6')", "", priority=True, show=False),
        Binding("7", "mode('7')", "", priority=True, show=False),
        Binding("8", "mode('8')", "", priority=True, show=False),
        Binding("9", "mode('9')", "", priority=True, show=False),
        Binding("space", "pause", "Pause/Resume", priority=True),
        Binding("s", "settings", "Settings", priority=True),
        Binding("h", "help", "Help", priority=True),
        Binding("?", "help", "Help", priority=True, show=False),
        Binding("m", "mode_select", "Select Mode", priority=True),
        Binding("f", "file_picker", "File Picker", priority=True),
        Binding("e", "export", "Export", priority=True),
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
        
        with Container(id="control_panel"):
            with Horizontal():
                yield ModeSelector(self.viz_mode, id="mode_selector")
                yield ControlPanel(self.audio_input, id="controls")
        
        yield VisualizationDisplay(self.wave_app, id="visualization_area")
        yield StatusBar(id="status_bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when the app is mounted"""
        logger.info("WaveTerm TUI mounted successfully")
        self.title = f"WaveTerm v0.6.3 - {self.viz_mode.title()} Mode"
        
        # Start visualization updates
        self.set_interval(1/30, self._update_visualization)  # 30 FPS
    
    def _update_visualization(self) -> None:
        """Update the visualization display"""
        if not self.paused and self.wave_app:
            viz_display = self.query_one("#visualization_area", VisualizationDisplay)
            viz_display.update_visualization()
            
            # Update status bar
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(self.wave_app, self.viz_mode)
    
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
        self.title = f"WaveTerm v0.6.3 - {self.viz_mode.title()} Mode{pause_indicator}"
    
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
            self.viz_mode = new_mode
            self.title = f"WaveTerm v0.6.3 - {new_mode.title()} Mode"
            
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
        current_config = {
            'sensitivity': getattr(self.wave_app, 'sensitivity', 1.0) if self.wave_app else 1.0,
            'fps': 30,  # From the update interval
            'colors': True,
            'buffer_size': getattr(self.wave_app.audio_processor, 'buffer_size', 2048) if self.wave_app and self.wave_app.audio_processor else 2048
        }
        
        def handle_settings_result(result):
            if result:
                logger.info(f"Applying settings: {result}")
                self._apply_settings(result)
        
        self.push_screen(SettingsModal(current_config), handle_settings_result)
    
    def action_help(self) -> None:
        """Show help dialog"""
        self.push_screen(HelpModal())
    
    def action_mode_select(self) -> None:
        """Show mode selection dialog"""
        if self.wave_app:
            # Get available modes from registry
            from ..visualizations.registry import get_all_modes
            all_modes = get_all_modes()
            
            available_modes = [(mode_id, info["name"]) for mode_id, info in all_modes.items()]
            # Sort by category and name for better organization
            available_modes.sort(key=lambda x: (all_modes[x[0]]["category"], x[1]))
            
            def handle_mode_result(result):
                if result and result != self.viz_mode:
                    self.change_mode(result)
            
            self.push_screen(ModeSelectModal(self.viz_mode, available_modes), handle_mode_result)
    
    def action_file_picker(self) -> None:
        """Show file picker dialog"""
        def handle_file_result(result):
            if result:
                logger.info(f"Audio file selected: {result}")
                # TODO: Switch to file input mode with selected file
                self.notify(f"Selected: {result}")
        
        self.push_screen(FilePickerModal(), handle_file_result)
    
    def action_export(self) -> None:
        """Show export dialog"""
        def handle_export_result(result):
            if result:
                logger.info(f"Export requested: {result}")
                self._start_export(result)
        
        self.push_screen(ExportModal(), handle_export_result)
    
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
    
    def on_mode_selector_mode_clicked(self, event: ModeSelector.ModeClicked) -> None:
        """Handle mode selector click"""
        self.action_mode_select()
    
    def on_control_panel_settings_clicked(self, event: ControlPanel.SettingsClicked) -> None:
        """Handle settings button click"""
        self.action_settings()
    
    def on_control_panel_help_clicked(self, event: ControlPanel.HelpClicked) -> None:
        """Handle help button click"""
        self.action_help()