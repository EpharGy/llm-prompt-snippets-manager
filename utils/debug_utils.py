"""
Debug utilities for LLM Prompt Snippets Manager

Provides unified debug mode detection and utilities for development.
"""

import os
import sys
from utils.logger import is_debug_mode, get_logger

logger = get_logger(__name__)

def get_debug_mode() -> bool:
    """
    Get current debug mode status from the unified debug system.
    
    Returns:
        bool: True if debug mode is active, False otherwise
    """
    return is_debug_mode()

def debug_print(*args, **kwargs):
    """
    Print debug information only when debug mode is active.
    
    Args:
        *args: Arguments to print
        **kwargs: Keyword arguments for print()
    """
    if get_debug_mode():
        print("🐛 DEBUG:", *args, **kwargs)

def log_debug_info():
    """Log information about how debug mode was activated."""
    if not get_debug_mode():
        return
        
    debug_sources = []
    
    # Check environment variables
    if os.getenv('PROMPT_SNIPPETS_DEBUG', '').lower() in ['true', '1', 'yes', 'on']:
        debug_sources.append("PROMPT_SNIPPETS_DEBUG environment variable")
    
    if os.getenv('DEBUG', '').lower() in ['true', '1', 'yes', 'on']:
        debug_sources.append("DEBUG environment variable")
    
    # Check command line arguments
    if '--debug' in sys.argv or '-d' in sys.argv:
        debug_sources.append("command line flag")
    
    if debug_sources:
        logger.info(f"🐛 Debug mode active via: {', '.join(debug_sources)}")
    else:
        logger.info("🐛 Debug mode active (source unknown)")

def is_exe_build() -> bool:
    """
    Detect if the application is running as a compiled executable.
    
    Returns:
        bool: True if running as exe, False if running as Python script
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_app_path() -> str:
    """
    Get the application's base path, whether running as script or exe.
    
    Returns:
        str: Base path of the application
    """
    if is_exe_build():
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))  # type: ignore
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))
