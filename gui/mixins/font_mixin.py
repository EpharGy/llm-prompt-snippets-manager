import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING
from utils.logger import get_logger

# Type checking imports to avoid circular imports
if TYPE_CHECKING:
    from utils.font_manager import FontManager
    from gui.components.scrollable_bubble_frame import ScrollableBubbleFrame

logger = get_logger(__name__)


class FontMixin:
    """Mixin providing font management functionality for GUI components
    
    Classes using this mixin should have:
    - self.font_manager: FontManager instance
    - self._header_label: ttk.Label (optional)
    - self._search_entry: ttk.Entry (optional)
    - self.filter_frame: ttk.Frame (optional)
    - self.categories_bubble_frame: ScrollableBubbleFrame (optional)
    - self.labels_bubble_frame: ScrollableBubbleFrame (optional)
    """
    
    def _apply_fonts(self):
        """Apply font manager fonts to all UI components"""
        try:
            font_manager = getattr(self, 'font_manager', None)
            if not font_manager:
                logger.debug("No font_manager found, skipping font application")
                return
                
            # Apply font to tree view
            if hasattr(self, 'tree'):
                tree_font = font_manager.get_font_tuple('tree')
                style = ttk.Style()
                style.configure('Normal.Treeview', font=tree_font)
                style.configure('Normal.Treeview.Heading', font=font_manager.get_font_tuple('tree', 'bold'))
                
            # Apply font to header label
            header_label = getattr(self, '_header_label', None)
            if header_label:
                header_font = font_manager.get_font('heading', 'bold')
                header_label.configure(font=header_font)
                
            # Apply font to search entry
            search_entry = getattr(self, '_search_entry', None)
            if search_entry:
                default_font = font_manager.get_font_tuple('default')
                search_entry.configure(font=default_font)
            
            # Apply fonts to filter section elements
            default_font = font_manager.get_font_tuple('default')
              
            # Get centralized static font for buttons (bubbles use dynamic fonts)
            static_button_font = font_manager.get_static_font('button')
            
            # Skip button font updates to avoid type checker issues
            # Regular UI buttons use centralized static fonts which work well across displays
            logger.debug(f"Regular UI buttons using static fonts (type-safe): {static_button_font}")
              
            # Apply fonts to filter labels (these work without type issues)
            self._apply_fonts_to_filter_labels()
            
            # Apply dynamic fonts to filter bubbles (tk.Button widgets support this)
            self._apply_fonts_to_bubbles()
                
            logger.debug("Fonts applied to component")
            
        except Exception as e:
            logger.error(f"Error applying fonts: {str(e)}")
    
    def _apply_fonts_to_filter_labels(self):
        """Apply fonts to filter section labels"""
        try:
            font_manager = getattr(self, 'font_manager', None)
            if not font_manager:
                return
                
            default_font = font_manager.get_font_tuple('default')
            
            # Find and update filter labels recursively
            filter_frame = getattr(self, 'filter_frame', None)
            if filter_frame:
                for widget in filter_frame.winfo_children():
                    self._update_labels_recursive(widget, default_font)
                    
        except Exception as e:
            logger.debug(f"Error applying fonts to filter labels: {str(e)}")
    
    def _update_labels_recursive(self, widget, font_tuple):
        """Recursively update label fonts"""
        try:
            if isinstance(widget, ttk.Label):
                try:
                    widget.configure(font=font_tuple)
                except tk.TclError:
                    pass  # Widget doesn't support font option
            # Recurse to children
            for child in widget.winfo_children():
                self._update_labels_recursive(child, font_tuple)
                
        except tk.TclError as e:
            logger.debug(f"TclError updating labels: {e}")
            pass
        except Exception as e:
            logger.debug(f"Unexpected error updating labels: {e}")
            pass
    
    def _apply_fonts_to_bubbles(self):
        """Apply dynamic fonts to bubble filter buttons"""
        try:
            font_manager = getattr(self, 'font_manager', None)
            if not font_manager:
                return
                
            # Get dynamic font size for bubbles (slightly smaller than default)
            bubble_size = font_manager._calculate_font_size('default') - 1
            bubble_size = max(6, bubble_size)  # Minimum size of 6
            bubble_font = ('TkDefaultFont', bubble_size)
              
            # Update all bubble buttons in both containers
            categories_frame = getattr(self, 'categories_bubble_frame', None)
            if categories_frame:
                self._update_bubble_fonts_recursive(categories_frame, bubble_font)
                categories_frame.update_row_height()
                
            labels_frame = getattr(self, 'labels_bubble_frame', None)
            if labels_frame:
                self._update_bubble_fonts_recursive(labels_frame, bubble_font)
                labels_frame.update_row_height()
            
            logger.debug(f"Filter bubble buttons updated to dynamic font: {bubble_font}")
                    
        except Exception as e:
            logger.debug(f"Error applying fonts to bubble buttons: {str(e)}")
    
    def _update_bubble_fonts_recursive(self, container, font_tuple):
        """Recursively update fonts for all tk.Button widgets in container"""
        try:
            for child in container.winfo_children():
                if isinstance(child, tk.Button):
                    child.configure(font=font_tuple)
                elif hasattr(child, 'winfo_children'):
                    # Recurse into child containers
                    self._update_bubble_fonts_recursive(child, font_tuple)
        except tk.TclError as e:
            logger.debug(f"TclError updating bubble fonts: {e}")
            pass  # Skip widgets that don't support font configuration
        except Exception as e:
            logger.debug(f"Unexpected error updating bubble fonts: {e}")
            pass
    
    def refresh_fonts(self):
        """Public method to refresh fonts (called from main app)"""
        self._apply_fonts()
