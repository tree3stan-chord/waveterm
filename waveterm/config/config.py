"""
Configuration management for WaveTerm
"""

import toml
from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from rich.table import Table
from ..core.logger import get_logger

logger = get_logger('config')

class AudioConfig(BaseModel):
    """Audio processing configuration"""
    sample_rate: int = Field(default=44100, description="Audio sample rate")
    buffer_size: int = Field(default=2048, description="Audio buffer size")
    hop_length: int = Field(default=512, description="FFT hop length")
    sensitivity: float = Field(default=1.0, description="Audio sensitivity multiplier")
    
class VisualConfig(BaseModel):
    """Visualization configuration"""
    fps: int = Field(default=30, description="Target frames per second")
    width: Optional[int] = Field(default=None, description="Force canvas width")
    height: Optional[int] = Field(default=None, description="Force canvas height")
    colors: bool = Field(default=True, description="Enable colors")
    ascii_set: str = Field(default=" .·:¦|=+*#%@█", description="ASCII character set")
    
class ExportConfig(BaseModel):
    """Export configuration"""
    default_format: str = Field(default="gif", description="Default export format")
    quality: int = Field(default=80, description="Export quality (1-100)")
    fps: int = Field(default=20, description="Export FPS")
    
class PluginConfig(BaseModel):
    """Plugin system configuration"""
    enabled: bool = Field(default=True, description="Enable plugin system")
    directories: List[str] = Field(default_factory=lambda: ["~/.waveterm/plugins"], description="Plugin directories")
    auto_load: bool = Field(default=True, description="Auto-load plugins on startup")

class WaveConfig(BaseModel):
    """Main WaveTerm configuration"""
    
    # Core settings
    version: str = Field(default="0.5.0", description="Config format version")
    default_mode: str = Field(default="bars", description="Default visualization mode")
    default_input: str = Field(default="sim", description="Default input source")
    
    # Component configs
    audio: AudioConfig = Field(default_factory=AudioConfig)
    visual: VisualConfig = Field(default_factory=VisualConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    
    # Advanced settings
    headless: bool = Field(default=False, description="Run in headless mode")
    debug: bool = Field(default=False, description="Enable debug output")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Presets
    presets: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Named configuration presets")
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "WaveConfig":
        """Load configuration from file"""
        if config_path is None:
            config_path = Path.home() / ".waveterm" / "config.toml"
            
        if isinstance(config_path, str):
            config_path = Path(config_path)
            
        if not config_path.exists():
            return cls()
            
        try:
            with open(config_path, 'r') as f:
                data = toml.load(f)
            return cls(**data)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return cls()
    
    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to file"""
        if config_path is None:
            config_path = Path.home() / ".waveterm" / "config.toml"
            
        if isinstance(config_path, str):
            config_path = Path(config_path)
            
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict and save
        data = self.model_dump()
        
        with open(config_path, 'w') as f:
            toml.dump(data, f)
    
    def get_preset(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a named preset"""
        return self.presets.get(name)
    
    def save_preset(self, name: str, config_override: Dict[str, Any]) -> None:
        """Save current config as a preset"""
        self.presets[name] = config_override
    
    def apply_preset(self, name: str) -> bool:
        """Apply a named preset"""
        preset = self.get_preset(name)
        if not preset:
            return False
            
        # Update configuration with preset values
        for key, value in preset.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        return True
    
    def to_table(self) -> Table:
        """Convert configuration to Rich table for display"""
        table = Table(title="WaveTerm Configuration")
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        table.add_column("Description", style="white")
        
        # Flatten config for display
        config_items = [
            ("default_mode", self.default_mode, "Default visualization mode"),
            ("default_input", self.default_input, "Default input source"),
            ("headless", self.headless, "Headless mode enabled"),
            ("audio.sample_rate", self.audio.sample_rate, "Audio sample rate"),
            ("audio.sensitivity", self.audio.sensitivity, "Audio sensitivity"),
            ("visual.fps", self.visual.fps, "Target FPS"),
            ("visual.colors", self.visual.colors, "Colors enabled"),
            ("export.default_format", self.export.default_format, "Default export format"),
            ("plugins.enabled", self.plugins.enabled, "Plugins enabled"),
        ]
        
        for key, value, description in config_items:
            table.add_row(key, str(value), description)
            
        return table
    
    @classmethod
    def create_default_presets(cls) -> Dict[str, Dict[str, Any]]:
        """Create default preset configurations"""
        return {
            "performance": {
                "visual": {"fps": 15},
                "audio": {"buffer_size": 4096}
            },
            "quality": {
                "visual": {"fps": 60},
                "audio": {"buffer_size": 1024}
            },
            "headless": {
                "headless": True,
                "default_input": "sim"
            },
            "export": {
                "export": {"fps": 30, "quality": 95},
                "visual": {"fps": 30}
            }
        }