"""
Professional Logging System for LLM Prompt Snippets Manager

Provides clean, configurable logging with different verbosity levels
and elegant output formatting.
"""

import os
import sys
from enum import Enum
from typing import Optional
from datetime import datetime


class LogLevel(Enum):
    """Log levels in order of severity."""
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


class Logger:
    """A clean, elegant logger with emoji prefixes and color support."""
    
    # Color codes for terminal output
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'RESET': '\033[0m',     # Reset
        'BOLD': '\033[1m',      # Bold
        'DIM': '\033[2m'        # Dim
    }
    
    # Emoji prefixes for different log levels
    EMOJIS = {
        LogLevel.DEBUG: '🔧',
        LogLevel.INFO: '✅', 
        LogLevel.WARNING: '⚠️',
        LogLevel.ERROR: '❌'
    }
    
    def __init__(self, name: str, level: LogLevel = LogLevel.INFO):
        """Initialize logger with a name and minimum log level.
        
        Args:
            name: Logger name (usually module/class name)
            level: Minimum log level to display
        """
        self.name = name
        self.level = level
        self.use_colors = self._supports_color()
    
    def _supports_color(self) -> bool:
        """Check if terminal supports color output."""
        # Check if we're in a terminal and not redirecting output
        if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
            return False
        
        # Check common environment variables
        term = os.getenv('TERM', '').lower()
        colorterm = os.getenv('COLORTERM', '').lower()
        
        return (
            'color' in term or 
            'xterm' in term or 
            'screen' in term or
            colorterm in ['truecolor', '24bit']
        )
    
    def _format_message(self, level: LogLevel, message: str) -> str:
        """Format a log message with colors and prefixes.
        
        Args:
            level: Log level
            message: Message to format
            
        Returns:
            Formatted message string
        """
        # Get emoji and color
        emoji = self.EMOJIS.get(level, '•')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if self.use_colors:
            color = self.COLORS.get(level.name, '')
            reset = self.COLORS['RESET']
            dim = self.COLORS['DIM']
            bold = self.COLORS['BOLD']
            
            # Format: [timestamp] emoji [ModuleName] message
            formatted = f"{dim}[{timestamp}]{reset} {emoji} {bold}[{self.name}]{reset} {color}{message}{reset}"
        else:
            # No color version
            formatted = f"[{timestamp}] {emoji} [{self.name}] {message}"
        
        return formatted
    
    def _log(self, level: LogLevel, message: str) -> None:
        """Internal logging method.
        
        Args:
            level: Log level
            message: Message to log
        """
        if level.value >= self.level.value:
            formatted = self._format_message(level, message)
            print(formatted)
    
    def debug(self, message: str) -> None:
        """Log a debug message (only in DEBUG mode)."""
        self._log(LogLevel.DEBUG, message)
    
    def info(self, message: str) -> None:
        """Log an info message (user-facing feedback)."""
        self._log(LogLevel.INFO, message)
    
    def warning(self, message: str) -> None:
        """Log a warning message (always shown)."""
        self._log(LogLevel.WARNING, message)
    
    def error(self, message: str) -> None:
        """Log an error message (always shown)."""
        self._log(LogLevel.ERROR, message)
    
    def set_level(self, level: LogLevel) -> None:
        """Change the minimum log level."""
        self.level = level


class LogManager:
    """Manages logger instances and global log level."""
    
    _instance: Optional['LogManager'] = None
    _global_level: LogLevel = LogLevel.INFO
    _loggers: dict[str, Logger] = {}
    
    def __new__(cls) -> 'LogManager':
        """Singleton pattern for log manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def set_global_level(cls, level: LogLevel) -> None:
        """Set global log level for all loggers.
        
        Args:
            level: Minimum log level to display globally
        """
        cls._global_level = level
        # Update existing loggers
        for logger in cls._loggers.values():
            logger.set_level(level)
    
    @classmethod
    def get_logger(cls, name: str) -> Logger:
        """Get or create a logger with the given name.
        
        Args:
            name: Logger name (usually module/class name)
            
        Returns:
            Logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = Logger(name, cls._global_level)
        return cls._loggers[name]


def get_logger(name: str) -> Logger:
    """Convenience function to get a logger.
    
    Args:
        name: Logger name (usually module/class name)
        
    Returns:
        Logger instance
    """
    return LogManager.get_logger(name)


def set_debug_mode(enabled: bool = True) -> None:
    """Enable or disable debug mode globally.
    
    Args:
        enabled: True to enable debug mode, False for standard mode
    """
    level = LogLevel.DEBUG if enabled else LogLevel.INFO
    LogManager.set_global_level(level)


def is_debug_mode() -> bool:
    """Check if debug mode is currently enabled.
    
    Returns:
        bool: True if debug mode is active, False otherwise
    """
    return LogManager._global_level == LogLevel.DEBUG


def configure_logging_from_environment() -> None:
    """Configure logging based on environment variables and command line args."""
    # Check our app-specific environment variable
    debug_env = os.getenv('PROMPT_SNIPPETS_DEBUG', '').lower() in ['true', '1', 'yes', 'on']
    
    # Check generic debug environment variable (fallback)
    debug_generic = os.getenv('DEBUG', '').lower() in ['true', '1', 'yes', 'on']
    
    # Check command line arguments
    debug_arg = '--debug' in sys.argv or '-d' in sys.argv
    
    # Enable debug mode if any method is used
    if debug_env or debug_generic or debug_arg:
        set_debug_mode(True)
        logger = get_logger("LogManager")
        logger.info("🐛 Debug mode enabled")
        
        # Log which method triggered debug mode
        if debug_arg:
            logger.debug("Debug enabled via command line flag")
        elif debug_env:
            logger.debug("Debug enabled via PROMPT_SNIPPETS_DEBUG environment variable")
        elif debug_generic:
            logger.debug("Debug enabled via DEBUG environment variable")
    else:
        set_debug_mode(False)


# Initialize logging based on environment on import
configure_logging_from_environment()


# Example usage and testing
if __name__ == "__main__":
    # Test the logging system
    print("🎹 Testing Maki's Elegant Logging System 💜")
    print("=" * 50)
    
    # Test different loggers
    metadata_logger = get_logger("MetadataManager")
    data_logger = get_logger("DataManager")
    ui_logger = get_logger("UI")
    
    print("\n📝 Testing INFO mode (default):")
    metadata_logger.debug("This debug message should be hidden")
    metadata_logger.info("Metadata system initialized successfully")
    data_logger.info("Loaded 5 snippets from storage")
    ui_logger.warning("Category 'Unknown' has no snippets assigned")
    ui_logger.error("Failed to save snippet: permission denied")
    
    print("\n📝 Testing DEBUG mode:")
    set_debug_mode(True)
    metadata_logger.debug("Creating UUID for new category: Writing Style")
    metadata_logger.debug("Incrementing usage count for category ID: abc-123")
    data_logger.debug("Validating snippet data structure")
    metadata_logger.info("All validation checks passed")
    
    print("\n📝 Testing back to INFO mode:")
    set_debug_mode(False)
    metadata_logger.debug("This debug message should be hidden again")
    metadata_logger.info("System ready for user interaction")
    
    print("\n✅ Logging system test complete!")
    print("💜 Maki says: 'Now our code will look professional!'")
