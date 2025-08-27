"""
Modal dialogs for WaveTerm TUI
Provides reusable modal components for settings, help, file selection, etc.
"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, Grid
from textual.screen import ModalScreen
from textual.widgets import (
    Button, Label, Static, Input, Select, Switch,
    DirectoryTree, ListItem, ListView, Markdown
)
from textual.binding import Binding
from rich.text import Text
from typing import Optional, Dict, Any, List, Callable

from ..core.logger import get_logger

logger = get_logger('tui.modals')


class BaseModal(ModalScreen):
    """Base modal dialog with common styling and behavior"""
    
    CSS = """
    BaseModal {
        align: center middle;
    }
    
    #modal_container {
        width: 80%;
        height: 80%; 
        max-width: 120;
        max-height: 40;
        background: $surface;
        border: thick $primary;
        padding: 1;
    }
    
    #modal_header {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        content-align: center middle;
    }
    
    #modal_content {
        height: 1fr;
        padding: 1;
    }
    
    #modal_buttons {
        dock: bottom;
        height: 3;
        background: $surface;
    }
    
    .button_group {
        align: center middle;
        height: 100%;
    }
    """
    
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel", priority=True),
        Binding("enter", "confirm", "OK", priority=True),
    ]
    
    def __init__(self, title: str = "Dialog", **kwargs):
        super().__init__(**kwargs)
        self.modal_title = title
        self.result = None
    
    def compose(self) -> ComposeResult:
        """Compose the modal layout"""
        with Container(id="modal_container"):
            yield Static(self.modal_title, id="modal_header")
            yield Container(id="modal_content")
            with Horizontal(id="modal_buttons"):
                with Container(classes="button_group"):
                    yield Button("Cancel", variant="default", id="cancel_btn")
                    yield Button("OK", variant="primary", id="ok_btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "ok_btn":
            self.action_confirm()
        elif event.button.id == "cancel_btn":
            self.action_dismiss()
    
    def action_dismiss(self) -> None:
        """Cancel/dismiss the modal"""
        self.result = None
        self.dismiss(self.result)
    
    def action_confirm(self) -> None:
        """Confirm/OK the modal"""
        # Override in subclasses to set result
        self.dismiss(self.result)


class HelpModal(BaseModal):
    """Help dialog showing keyboard shortcuts and usage"""
    
    def __init__(self):
        super().__init__("🚀 WaveTerm Help & Shortcuts")
        
    def compose(self) -> ComposeResult:
        """Compose help modal content"""
        yield from super().compose()
        
        help_content = """
# 🌊 WaveTerm Interactive Controls

## 🎹 Keyboard Shortcuts
- **Q** or **Ctrl+C**: Quit application
- **Space**: Pause/Resume visualization  
- **S**: Open Settings dialog
- **H** or **?**: Show this help
- **1-9**: Switch visualization modes quickly
  - **1**: Frequency Bars
  - **2**: Waveform
  - **3**: Matrix Rain
  - **4**: Particle Field
  - **5**: Circular Wave
  - **6**: Starfield Warp
  - **7**: Fire Flames
  - **8**: Ocean Waves
  - **9**: DNA Helix

## 🎛️ Interface Elements
- **Mode Selector**: Click to change visualization
- **Input Selector**: Switch audio sources
- **Settings**: Adjust sensitivity, colors, FPS
- **Status Bar**: Shows audio levels and performance

## 🎵 Audio Sources
- **Simulation**: No audio required, generates test patterns
- **Microphone**: Real-time audio from mic input
- **File**: Play audio files (MP3, WAV, FLAC, etc.)

## 💡 Tips
- Use simulation mode on servers without audio
- Adjust sensitivity for better visualization
- Try different modes with different music genres
- Export visualizations as GIF or video
        """
        
        # Replace modal content with help text
        content_container = self.query_one("#modal_content")
        content_container.mount(Markdown(help_content.strip()))
    
    def action_confirm(self) -> None:
        """Just close on OK"""
        self.dismiss(True)


class SettingsModal(BaseModal):
    """Settings configuration dialog"""
    
    def __init__(self, current_config: Dict[str, Any]):
        super().__init__("⚙️ WaveTerm Settings")
        self.config = current_config.copy()
        
    def compose(self) -> ComposeResult:
        """Compose settings modal content"""
        with Container(id="modal_container"):
            yield Static(self.modal_title, id="modal_header")
            with Container(id="modal_content"):
                with Vertical():
                    # Audio Settings
                    yield Label("🎵 Audio Settings", classes="section_header")
                    with Horizontal():
                        yield Label("Sensitivity:")
                        yield Input(
                            value=str(self.config.get('sensitivity', 1.0)),
                            placeholder="1.0",
                            id="sensitivity_input"
                        )
                    
                    # Visual Settings  
                    yield Label("🎨 Visual Settings", classes="section_header")
                    with Horizontal():
                        yield Label("FPS Target:")
                        yield Input(
                            value=str(self.config.get('fps', 30)),
                            placeholder="30",
                            id="fps_input"
                        )
                    
                    with Horizontal():
                        yield Label("Enable Colors:")
                        yield Switch(
                            value=self.config.get('colors', True),
                            id="colors_switch"
                        )
                    
                    # Advanced Settings
                    yield Label("🔧 Advanced Settings", classes="section_header")
                    with Horizontal():
                        yield Label("Buffer Size:")
                        yield Select(
                            [(str(size), size) for size in [1024, 2048, 4096, 8192]],
                            value=self.config.get('buffer_size', 2048),
                            id="buffer_select"
                        )
            with Horizontal(id="modal_buttons"):
                with Horizontal(classes="button_group"):
                    yield Button("Cancel", id="cancel_button", variant="error")
                    yield Button("Save", id="save_button", variant="primary")
    
    def action_confirm(self) -> None:
        """Save settings and close"""
        try:
            # Gather form values
            sensitivity = float(self.query_one("#sensitivity_input", Input).value or "1.0")
            fps = int(self.query_one("#fps_input", Input).value or "30")
            colors = self.query_one("#colors_switch", Switch).value
            buffer_size = self.query_one("#buffer_select", Select).value
            
            self.result = {
                'sensitivity': sensitivity,
                'fps': fps, 
                'colors': colors,
                'buffer_size': buffer_size
            }
            
            logger.info(f"Settings updated: {self.result}")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            self.result = None
            
        self.dismiss(self.result)


class ModeSelectModal(BaseModal):
    """Visualization mode selection dialog"""
    
    def __init__(self, current_mode: str, available_modes: List[Dict[str, str]]):
        super().__init__("🎨 Select Visualization Mode")
        self.current_mode = current_mode
        self.modes = available_modes
        self.selected_mode = current_mode
        
    def compose(self) -> ComposeResult:
        """Compose mode selection content"""
        with Container(id="modal_container"):
            yield Static(self.modal_title, id="modal_header")
            with Container(id="modal_content"):
                with ListView(id="mode_list"):
                    for mode_id, mode_info in self.modes:
                        is_current = "👈 CURRENT" if mode_id == self.current_mode else ""
                        yield ListItem(
                            Label(f"🎭 {mode_info} {is_current}"),
                            id=f"mode_{mode_id}"
                        )
            with Horizontal(id="modal_buttons"):
                with Horizontal(classes="button_group"):
                    yield Button("Cancel", id="cancel_button", variant="error")
                    yield Button("Select", id="select_button", variant="primary")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle mode selection"""
        if event.item and event.item.id:
            mode_id = event.item.id.replace("mode_", "")
            self.selected_mode = mode_id
            logger.info(f"Mode selected: {mode_id}")
    
    def action_confirm(self) -> None:
        """Return selected mode"""
        self.result = self.selected_mode
        self.dismiss(self.result)


class FilePickerModal(BaseModal):
    """File picker for audio file selection"""
    
    def __init__(self, initial_path: str = "."):
        super().__init__("📁 Select Audio File")
        self.initial_path = initial_path
        self.selected_file = None
        
    def compose(self) -> ComposeResult:
        """Compose file picker content"""
        with Container(id="modal_container"):
            yield Static(self.modal_title, id="modal_header")
            with Container(id="modal_content"):
                yield DirectoryTree(self.initial_path, id="file_tree")
            with Horizontal(id="modal_buttons"):
                with Horizontal(classes="button_group"):
                    yield Button("Cancel", id="cancel_button", variant="error")
                    yield Button("Select", id="select_button", variant="primary")
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection"""
        file_path = str(event.path)
        # Check if it's an audio file
        audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
        if any(file_path.lower().endswith(ext) for ext in audio_extensions):
            self.selected_file = file_path
            logger.info(f"Audio file selected: {file_path}")
        else:
            logger.warning(f"Invalid audio file selected: {file_path}")
    
    def action_confirm(self) -> None:
        """Return selected file"""
        self.result = self.selected_file
        self.dismiss(self.result)


class ExportModal(BaseModal):
    """Export configuration dialog"""
    
    def __init__(self):
        super().__init__("📹 Export Visualization")
        
    def compose(self) -> ComposeResult:
        """Compose export configuration content"""
        with Container(id="modal_container"):
            yield Static(self.modal_title, id="modal_header")
            with Container(id="modal_content"):
                with Vertical():
                    # Output file
                    yield Label("📁 Output File:")
                    yield Input(placeholder="export.gif", id="output_input")
                    
                    # Format selection
                    yield Label("🎞️ Format:")
                    yield Select(
                        [("GIF", "gif"), ("MP4", "mp4"), ("Images", "images")],
                        value="gif",
                        id="format_select"
                    )
                    
                    # Duration and FPS
                    with Horizontal():
                        yield Label("Duration (s):")
                        yield Input(value="10", id="duration_input")
                        
                    with Horizontal():
                        yield Label("FPS:")
                        yield Input(value="20", id="fps_input")
            with Horizontal(id="modal_buttons"):
                with Horizontal(classes="button_group"):
                    yield Button("Cancel", id="cancel_button", variant="error")
                    yield Button("Export", id="export_button", variant="primary")
    
    def action_confirm(self) -> None:
        """Return export settings"""
        try:
            output_file = self.query_one("#output_input", Input).value or "export.gif"
            format_type = self.query_one("#format_select", Select).value
            duration = int(self.query_one("#duration_input", Input).value or "10")
            fps = int(self.query_one("#fps_input", Input).value or "20")
            
            self.result = {
                'output_file': output_file,
                'format': format_type,
                'duration': duration,
                'fps': fps
            }
            
            logger.info(f"Export settings: {self.result}")
            
        except Exception as e:
            logger.error(f"Error reading export settings: {e}")
            self.result = None
            
        self.dismiss(self.result)