"""
Logging system for WaveTerm
Provides structured logging to replace print statements throughout the application
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class WaveTermLogger:
    """Centralized logging system for WaveTerm"""
    
    _instance: Optional['WaveTermLogger'] = None
    _initialized = False
    
    def __new__(cls) -> 'WaveTermLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self.setup_logging()
    
    def setup_logging(self, level: str = "INFO", log_file: Optional[str] = None):
        """Setup logging configuration"""
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Get root logger for waveterm
        self.logger = logging.getLogger('waveterm')
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Console handler - only warnings and errors by default
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            try:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                console_handler.setLevel(logging.ERROR)  # Show this error
                self.logger.error(f"Failed to setup file logging: {e}")
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific module"""
        return logging.getLogger(f'waveterm.{name}')
    
    def set_console_level(self, level: str):
        """Set console output level (DEBUG, INFO, WARNING, ERROR)"""
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stderr:
                handler.setLevel(getattr(logging, level.upper()))
                break
    
    def enable_debug_console(self):
        """Enable debug output to console (useful for development)"""
        self.set_console_level('DEBUG')
    
    def disable_console(self):
        """Disable all console output (useful for clean visualization)"""
        self.set_console_level('CRITICAL')


# Convenience functions for easy importing
_logger_instance = WaveTermLogger()

def get_logger(name: str) -> logging.Logger:
    """Get a logger for a module - convenience function"""
    return _logger_instance.get_logger(name)

def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration - convenience function"""
    _logger_instance.setup_logging(level, log_file)

def enable_debug():
    """Enable debug output to console"""
    _logger_instance.enable_debug_console()

def disable_console():
    """Disable console output for clean visualizations"""
    _logger_instance.disable_console()