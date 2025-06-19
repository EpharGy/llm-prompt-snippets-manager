import tkinter as tk
from tkinter import ttk
from utils.logger import get_logger

logger = get_logger(__name__)


class ScrollableBubbleFrame(ttk.Frame):
    """Scrollable frame for bubble buttons with max 4 rows"""
    
    def __init__(self, parent, max_rows=4, **kwargs):
        super().__init__(parent, **kwargs)
        self.max_rows = max_rows
        self.child_widgets = []
        self._calculate_row_height()  # Calculate initial row height dynamically
        self._layout_in_progress = False
        self._last_width = 0
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Pack canvas (scrollbar will be packed dynamically)
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Start with minimum height (1 row) and disable pack propagation for height control
        self.configure(height=self.row_height, width=200)  # Set minimum width
        self.pack_propagate(False)
        
    def _calculate_row_height(self):
        """Calculate row height based on current font size"""
        try:
            # Get the current font size from the parent's font manager
            # Default to a reasonable size if font manager is not available
            base_font_size = 8  # Default bubble font size
            
            # Try to get font manager from SnippetList parent
            parent = self.master
            while parent and not hasattr(parent, 'font_manager'):
                parent = parent.master
                
            if parent and hasattr(parent, 'font_manager'):
                try:
                    base_font_size = parent.font_manager._calculate_font_size('default') - 1  # type: ignore
                    base_font_size = max(6, base_font_size)
                except AttributeError as e:
                    logger.debug(f"Font manager access failed, using default base size: {e}")
                    
            # Calculate row height with progressive scaling from Small's perfect spacing
            # Button height: font_size + internal padding (borders, etc.)
            button_height = base_font_size + 12
            
            # Dynamic padding that scales proportionally with any base font size
            # Ratios calculated to produce our perfect spacing values, accounting for int() truncation
            # This ensures consistent visual proportions regardless of user's base font setting
            if base_font_size <= 7:  # Small font
                padding_ratio = 0.72   # ~5px at 7px font (5/7 = 0.714, rounded up for int() truncation) 
            elif base_font_size <= 9:  # Normal font
                padding_ratio = 0.78   # ~7px at 9px font (7/9 = 0.778)
            elif base_font_size <= 11:  # Large font  
                padding_ratio = 0.82   # ~9px at 11px font (9/11 = 0.818)
            else:  # Extra Large font
                padding_ratio = 0.85   # ~11px at 13px font (11/13 = 0.846)
            
            # Calculate dynamic padding based on actual font size
            vertical_padding = max(2, int(base_font_size * padding_ratio))
            
            self.row_height = max(22, button_height + vertical_padding)
            
        except Exception as e:
            logger.debug(f"Error calculating row height, using default: {e}")
            # Fallback to default
            self.row_height = 29
    
    def update_row_height(self):
        """Update row height and relayout (call when font changes)"""
        self._calculate_row_height()
        self.after_idle(self._relayout)
        
    def add_child(self, widget):
        """Add a child widget to be wrapped"""
        self.child_widgets.append(widget)
        self.after_idle(self._relayout)
        
    def clear_children(self):
        """Clear all child widgets"""
        for widget in self.child_widgets:
            widget.destroy()
        self.child_widgets.clear()
        # Reset to minimum height
        self.configure(height=self.row_height)
        self.scrollbar.pack_forget()
        self._update_scroll_region()
        
    def _relayout(self):
        """Relayout all children with wrapping"""
        if self._layout_in_progress:
            return
            
        self._layout_in_progress = True
        
        try:
            if not self.child_widgets:
                self.configure(height=self.row_height)
                self.scrollbar.pack_forget()
                self._update_scroll_region()
                return
                
            # Get available width from parent instead of canvas
            self.update_idletasks()
            parent_width = self.winfo_width()
            canvas_width = self.canvas.winfo_width()
            
            # Use the larger of the two (sometimes parent width is more accurate)
            effective_width = max(parent_width - 40, canvas_width - 20)  # Buffer for scrollbar
            available_width = max(200, effective_width)  # Minimum 200px width
            
            # If width is still too small, retry later
            if available_width < 200:
                self.after(50, self._relayout)
                return
            
            # Calculate positions
            current_row = 0
            current_x = 0
            
            for widget in self.child_widgets:
                widget.update_idletasks()
                widget_width = widget.winfo_reqwidth()
                
                # Check if widget fits on current row
                if current_x + widget_width > available_width and current_x > 0:
                    current_row += 1
                    current_x = 0
                    
                # Place widget
                widget.place(x=current_x, y=current_row * self.row_height)
                current_x += widget_width + 4  # 4px spacing
                
            # Calculate total rows needed
            total_rows = current_row + 1
            content_height = total_rows * self.row_height
            
            # Update scrollable frame height
            self.scrollable_frame.configure(height=content_height)
            
            # Determine visible height and scrollbar visibility
            if total_rows <= self.max_rows:
                # Content fits within max rows - no scrollbar needed
                visible_height = content_height
                if self.scrollbar.winfo_viewable():
                    self.scrollbar.pack_forget()
            else:
                # Content exceeds max rows - show scrollbar
                visible_height = self.max_rows * self.row_height
                if not self.scrollbar.winfo_viewable():
                    self.scrollbar.pack(side="right", fill="y")
                    
            # Update container height and width
            current_width = self.winfo_width()
            
            if current_width < available_width:
                self.configure(height=visible_height, width=available_width)
            else:
                self.configure(height=visible_height)
            
            # Make sure canvas window is properly sized
            self.canvas.itemconfig(self.canvas_window, width=self.canvas.winfo_width())
            
            self._update_scroll_region()
            
        finally:
            self._layout_in_progress = False
        
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        if self._layout_in_progress:
            return
            
        # Only relayout if width actually changed significantly
        if abs(event.width - self._last_width) > 10:
            self._last_width = event.width
            # Update the canvas window width
            canvas_width = event.width
            if self.scrollbar.winfo_viewable():
                canvas_width -= self.scrollbar.winfo_reqwidth()
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            # Schedule relayout
            self.after_idle(self._relayout)
        
    def _update_scroll_region(self):
        """Update the scroll region"""
        self.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if self.scrollbar.winfo_viewable():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
