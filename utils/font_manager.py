"""
Font Management System for LLM Prompt Snippets Manager

Provides centralized font sizing and scaling for consistent UI appearance
across different display DPIs and user preferences.

Enhanced with dynamic DPI detection for multi-monitor setups.
"""

import tkinter as tk
from tkinter import font
from typing import Dict, Tuple, Optional, Literal
import os
import json

class FontManager:
    """Centralized font management with user-configurable scaling and dynamic DPI detection"""
    
    # Base font size - user can adjust this to scale everything proportionally
    DEFAULT_BASE_SIZE = 10
    
    # Scale factors for different size levels (multiplicative)
    SCALE_FACTORS = {
        'small': 0.8,       # 80% of base
        'normal': 1.0,      # 100% of base
        'large': 1.2,       # 120% of base  
        'extra_large': 1.4, # 140% of base
        'auto': 1.0         # Will be calculated based on DPI
    }
    
    # Different element types can have their own relative scaling
    ELEMENT_MODIFIERS = {
        'default': 1.0,     # Base size
        'heading': 1.2,     # 20% larger than base
        'button': 1.0,      # Same as base
        'tree': 0.95,       # Slightly smaller
        'dialog': 1.0       # Same as base
    }
    
    # Static font offsets relative to the base 'default' size for each scale
    # These are used for widgets that can't use dynamic font scaling (buttons, bubbles)
    # Positive values = larger than default, negative = smaller than default
    STATIC_FONT_OFFSETS = {
        'button': 0,        # Same size as default
        'bubble': -1,       # 1 point smaller than default  
        'small_button': -1  # 1 point smaller than default
    }
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.settings_file = os.path.join(data_dir, "ui_settings.json")
        self.current_scale = 'normal'  # Default
        self._fonts_cache: Dict[str, font.Font] = {}
        self._cached_dpi_scale = None  # Cache DPI scale factor
        self._main_window_ref = None  # Reference to main window for DPI detection
        
        # Load saved settings
        self._load_settings()
    
    def set_main_window(self, window):
        """Set reference to main window for DPI detection when window moves"""
        self._main_window_ref = window
        # Clear cached DPI when window reference changes
        self._cached_dpi_scale = None
        if self.current_scale == 'auto':
            self.update_fonts()
    
    def refresh_auto_scaling(self):
        """Force refresh of auto scaling (call when window moves between monitors)"""
        if self.current_scale == 'auto':
            self._cached_dpi_scale = None  # Clear cache
            self.update_fonts()  # Force font recreation
    
    def _load_settings(self):
        """Load UI settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.current_scale = settings.get('font_scale', 'normal')
        except Exception:
            # Use default if loading fails
            self.current_scale = 'normal'
    
    def _save_settings(self):
        """Save UI settings to file"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            settings = {
                'font_scale': self.current_scale
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception:            # Silently ignore save errors
            pass
    
    def set_font_scale(self, scale: str):
        """Set the font scale and save preference"""
        if scale in self.SCALE_FACTORS:
            self.current_scale = scale
            self._fonts_cache.clear()  # Clear cache to force recreation
            # Clear DPI cache when switching to/from auto mode
            if scale == 'auto' or self._cached_dpi_scale is not None:
                self._cached_dpi_scale = None
            self._save_settings()
            return True
        return False
    
    def update_fonts(self):
        """Force update of all cached fonts (useful for dynamic updates)"""
        self._fonts_cache.clear()
    
    def get_font_scale(self) -> str:
        """Get current font scale setting"""
        return self.current_scale
    
    def get_available_scales(self) -> Dict[str, str]:
        """Get available font scale options for UI"""
        return {
            'small': 'Small',
            'normal': 'Normal',
            'large': 'Large', 
            'extra_large': 'Extra Large',
            'auto': 'Auto'
        }
    
    def _get_dpi_scale_factor(self) -> float:
        """
        Detect system DPI and return appropriate scale factor
        Uses cached value unless forced refresh or using main window reference
        Returns 1.0 for normal DPI, higher values for high DPI displays
        """
        # Return cached value if available
        if self._cached_dpi_scale is not None:
            return self._cached_dpi_scale
            
        try:
            # Use main window if available (better for multi-monitor setups)
            if self._main_window_ref and hasattr(self._main_window_ref, 'winfo_fpixels'):
                dpi = self._main_window_ref.winfo_fpixels('1i')
            else:
                # Fallback: Create temporary window for DPI detection
                temp_root = tk.Tk()
                temp_root.withdraw()  # Hide the window
                dpi = temp_root.winfo_fpixels('1i')
                temp_root.destroy()
            
            # Standard DPI is 96, calculate scale factor
            scale_factor = dpi / 96.0
            
            # Clamp to reasonable values and cache result
            self._cached_dpi_scale = max(0.8, min(2.0, scale_factor))
            return self._cached_dpi_scale
            
        except Exception:
            # Fallback to normal scale if DPI detection fails
            self._cached_dpi_scale = 1.0
            return 1.0
    
    def _get_auto_font_size(self, base_size: int) -> int:
        """Calculate font size for auto scaling based on DPI"""
        scale_factor = self._get_dpi_scale_factor()
        return max(8, int(base_size * scale_factor))  # Minimum size of 8
    
    def _calculate_font_size(self, element_type: str = 'default', base_size: Optional[int] = None) -> int:
        """Calculate font size using multiplicative scaling"""
        if base_size is None:
            base_size = self.DEFAULT_BASE_SIZE
            
        # Get scale factor for current scale level
        scale_factor = self.SCALE_FACTORS.get(self.current_scale, 1.0)
        
        # Apply auto scaling if enabled
        if self.current_scale == 'auto':
            scale_factor = self._get_dpi_scale_factor()
            
        # Get element modifier
        element_modifier = self.ELEMENT_MODIFIERS.get(element_type, 1.0)
        
        # Calculate final size: base × scale × element_modifier
        final_size = base_size * scale_factor * element_modifier
        
        return max(6, int(round(final_size)))  # Minimum size of 6, rounded to int
    
    def get_font(self, font_type: str = 'default', weight: Literal['normal', 'bold'] = 'normal') -> font.Font:
        """
        Get a font object for the specified type and weight
        
        Args:
            font_type: Type of font ('default', 'heading', 'button', 'tree', 'dialog')
            weight: Font weight ('normal', 'bold')
          Returns:
            tkinter.font.Font object
        """
        cache_key = f"{font_type}_{weight}_{self.current_scale}"
        
        if cache_key not in self._fonts_cache:
            size = self._calculate_font_size(font_type)
            
            self._fonts_cache[cache_key] = font.Font(
                family='TkDefaultFont',
                size=size,
                weight=weight
            )
            
        return self._fonts_cache[cache_key]
    
    def get_font_tuple(self, font_type: str = 'default', weight: Literal['normal', 'bold'] = 'normal') -> Tuple[str, int, str]:
        """
        Get font as tuple (family, size, weight) for tkinter widgets
        
        Args:
            font_type: Type of font ('default', 'heading', 'button', 'tree', 'dialog')
            weight: Font weight ('normal', 'bold')
          Returns:
            Tuple of (family, size, weight)
        """
        size = self._calculate_font_size(font_type)
        return ('TkDefaultFont', size, weight)
    
    def get_static_font(self, font_type: str = 'button') -> Tuple[str, int, str]:
        """
        Get a static font tuple that scales with the base font size.
        
        Used for buttons and filter bubbles to avoid type checker issues.
        These fonts use the current scale's base 'default' size plus an offset.
        
        Args:
            font_type: Type of static font ('button', 'bubble', 'small_button')
          Returns:
            Tuple of (family, size, weight) - calculated from base + offset
        """
        # Calculate base size using the new system
        base_size = self._calculate_font_size('default')
        
        # Apply the offset for this font type
        offset = self.STATIC_FONT_OFFSETS.get(font_type, 0)
        final_size = max(6, base_size + offset)  # Minimum size of 6
        
        return ('Segoe UI', final_size, 'normal')

# Global font manager instance
_font_manager: Optional[FontManager] = None

def get_font_manager(data_dir: str = "data") -> FontManager:
    """Get the global font manager instance"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager(data_dir)
    return _font_manager

def get_font(font_type: str = 'default', weight: Literal['normal', 'bold'] = 'normal') -> font.Font:
    """Convenience function to get a font from the global manager"""
    return get_font_manager().get_font(font_type, weight)

def get_font_tuple(font_type: str = 'default', weight: Literal['normal', 'bold'] = 'normal') -> Tuple[str, int, str]:
    """Convenience function to get a font tuple from the global manager"""
    return get_font_manager().get_font_tuple(font_type, weight)

def get_static_font(font_type: str = 'button') -> Tuple[str, int, str]:
    """Convenience function to get a static font tuple from the global manager"""
    return get_font_manager().get_static_font(font_type)

def setup_window_dpi_monitoring(window):
    """
    Setup DPI monitoring for a window (call this for main window)
    This should be called after creating the main window to enable
    dynamic DPI detection when moving between monitors
    """
    font_mgr = get_font_manager()
    font_mgr.set_main_window(window)
    
    # Bind to window configuration events to detect monitor changes
    def on_configure(event):
        # Only respond to window position changes, not size changes
        if event.widget == window:
            font_mgr.refresh_auto_scaling()
    
    window.bind('<Configure>', on_configure)
    return font_mgr

def refresh_auto_fonts():
    """
    Force refresh of auto-scaled fonts
    Call this when you detect the window has moved to a different monitor
    """
    get_font_manager().refresh_auto_scaling()
