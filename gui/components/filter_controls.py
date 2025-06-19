import tkinter as tk
from tkinter import ttk
from typing import Dict, Set, Callable, Optional
from gui.components.scrollable_bubble_frame import ScrollableBubbleFrame
from utils.logger import get_logger

logger = get_logger(__name__)


class FilterControls(ttk.Frame):
    """Component for managing filter bubbles and controls"""
    
    def __init__(self, parent, on_filter_changed: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_filter_changed = on_filter_changed
        
        # Filter state
        self.active_category_filters: Set[str] = set()
        self.active_label_filters: Set[str] = set()
        self.category_buttons: Dict[str, tk.Button] = {}
        self.label_buttons: Dict[str, tk.Button] = {}
        self.filter_mode_var = tk.StringVar(value="AND")
        
        # Font manager reference (will be set by parent)
        self.font_manager = None
        
        self._create_ui()
        
    def set_font_manager(self, font_manager):
        """Set the font manager reference"""
        self.font_manager = font_manager
        
    def _create_ui(self):
        """Create the filter UI components"""
        # Main filter frame with standardized padding
        self.filter_frame = ttk.Frame(self)
        self.filter_frame.pack(fill='x', padx=5, pady=(5, 8))
        
        # Filter header with AND/OR toggle
        filter_header = ttk.Frame(self.filter_frame)
        filter_header.pack(fill='x', pady=(0, 8))
        
        # Filter title
        ttk.Label(filter_header, text="Filters:", font=('TkDefaultFont', 9, 'bold')).pack(side='left')
        
        # AND/OR toggle button
        self.filter_mode_btn = ttk.Button(
            filter_header, 
            text="AND", 
            width=5,
            command=self._toggle_filter_mode
        )
        self.filter_mode_btn.pack(side='left', padx=(10, 5))
        
        # Clear filters button
        self.clear_filters_btn = ttk.Button(
            filter_header,
            text="Clear All",
            command=self._clear_all_filters
        )
        self.clear_filters_btn.pack(side='left', padx=5)
        
        # Categories section
        categories_frame = ttk.Frame(self.filter_frame)
        categories_frame.pack(fill='x', pady=(0, 6))
        ttk.Label(categories_frame, text="Categories:", font=('TkDefaultFont', 8)).pack(side='left', padx=(0, 5))
        
        self.categories_bubble_frame = ScrollableBubbleFrame(categories_frame, max_rows=4)
        self.categories_bubble_frame.pack(side='left', fill='both', expand=True)
        
        # Labels section  
        labels_frame = ttk.Frame(self.filter_frame)
        labels_frame.pack(fill='x', pady=(0, 6))
        ttk.Label(labels_frame, text="Labels:", font=('TkDefaultFont', 8)).pack(side='left', padx=(0, 5))
        
        self.labels_bubble_frame = ScrollableBubbleFrame(labels_frame, max_rows=4)
        self.labels_bubble_frame.pack(side='left', fill='both', expand=True)
        
    def _toggle_filter_mode(self):
        """Toggle between AND and OR filter mode"""
        current_mode = self.filter_mode_var.get()
        new_mode = "OR" if current_mode == "AND" else "AND"
        self.filter_mode_var.set(new_mode)
        self.filter_mode_btn.configure(text=new_mode)
        
        # Update button color to indicate mode
        if new_mode == "AND":
            self.filter_mode_btn.configure(style="Default.TButton")
        else:
            self.filter_mode_btn.configure(style="Accent.TButton")
            
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed()
        
    def _clear_all_filters(self):
        """Clear all active bubble filters"""
        self.active_category_filters.clear()
        self.active_label_filters.clear()
        
        # Update button states to unselected style
        for btn in self.category_buttons.values():
            self._set_button_unselected(btn)
        for btn in self.label_buttons.values():
            self._set_button_unselected(btn)
              
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed()
    
    def _set_button_unselected(self, btn: tk.Button):
        """Set button to unselected style"""
        btn.configure(
            bg="#f0f0f0",
            fg="#333333", 
            activebackground="#e0e0e0",
            activeforeground="#000000",
            relief="raised",
            borderwidth=2
        )
    
    def _set_button_selected_category(self, btn: tk.Button):
        """Set button to selected category style (blue)"""
        btn.configure(            bg="#2196F3",
            fg="white", 
            activebackground="#1976D2",
            activeforeground="white",
            relief="raised",
            borderwidth=2
        )
    
    def _set_button_selected_label(self, btn: tk.Button):
        """Set button to selected label style (green)"""
        btn.configure(
            bg="#4CAF50",
            fg="white",
            activebackground="#388E3C",
            activeforeground="white", 
            relief="raised",
            borderwidth=2
        )
    
    def create_bubble_button(self, parent, text, filter_type, filter_value):
        """Create a clickable bubble button with custom styling"""
        # Calculate initial font size based on current scale
        if self.font_manager:
            bubble_size = self.font_manager._calculate_font_size('default') - 1
            bubble_size = max(6, bubble_size)  # Minimum size of 6
        else:
            bubble_size = 8  # Default fallback
        initial_font = ('TkDefaultFont', bubble_size)
        
        # Use tk.Button instead of ttk.Button for better color control
        btn = tk.Button(
            parent,
            text=text,
            width=len(text) + 2,
            bg="#f0f0f0",           # Unselected background
            fg="#333333",           # Unselected text
            activebackground="#e0e0e0",  # Hover background
            activeforeground="#000000",  # Hover text
            relief="raised",
            borderwidth=2,
            font=initial_font,
            cursor="hand2",
            command=lambda: self._toggle_bubble_filter(filter_type, filter_value, btn)
        )
        
        # Bind scroll wheel events to forward to parent scrollable container
        def on_scroll(event):
            # Find the scrollable container by traversing up the parent hierarchy
            widget = btn
            while widget:
                # Check if it's a scrollable widget
                if hasattr(widget, 'yview_scroll'):
                    try:
                        yview_scroll = getattr(widget, 'yview_scroll', None)
                        if yview_scroll:
                            yview_scroll(int(-1 * (event.delta / 120)), "units")
                            break
                    except (AttributeError, tk.TclError) as e:
                        logger.debug(f"Scroll handling failed for widget: {e}")
                        pass
                # Check if it's our WrappingFrame with scrollable_canvas
                elif hasattr(widget, 'scrollable_canvas'):
                    try:
                        scrollable_canvas = getattr(widget, 'scrollable_canvas', None)
                        if scrollable_canvas and hasattr(scrollable_canvas, 'yview_scroll'):
                            scrollable_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            break
                    except (AttributeError, tk.TclError) as e:
                        logger.debug(f"Scrollable canvas handling failed: {e}")
                        pass
                widget = widget.master
            return "break"
        
        # Bind both Windows and Linux scroll wheel events
        btn.bind("<MouseWheel>", on_scroll)        # Windows
        btn.bind("<Button-4>", lambda e: on_scroll(type('obj', (object,), {'delta': 120})()))  # Linux scroll up
        btn.bind("<Button-5>", lambda e: on_scroll(type('obj', (object,), {'delta': -120})()))  # Linux scroll down
        
        # Don't pack here - parent component will handle positioning
        return btn
        
    def _toggle_bubble_filter(self, filter_type: str, filter_value: str, button: tk.Button):
        """Toggle a bubble filter on/off with visual feedback"""
        if filter_type == 'category':
            if filter_value in self.active_category_filters:
                self.active_category_filters.remove(filter_value)
                self._set_button_unselected(button)
            else:
                self.active_category_filters.add(filter_value)
                self._set_button_selected_category(button)
        elif filter_type == 'label':
            if filter_value in self.active_label_filters:
                self.active_label_filters.remove(filter_value)
                self._set_button_unselected(button)
            else:
                self.active_label_filters.add(filter_value)
                self._set_button_selected_label(button)
                
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed()
        
    def refresh_bubble_filters(self, all_snippets: Dict):
        """Refresh the bubble filter buttons based on current snippets"""
        # Clear existing buttons
        self.categories_bubble_frame.clear_children()
        self.labels_bubble_frame.clear_children()
        self.category_buttons.clear()
        self.label_buttons.clear()
        
        # Collect all categories and labels
        all_categories = set()
        all_labels = set()
        
        for snippet in all_snippets.values():
            all_categories.add(snippet['category'])
            all_labels.update(snippet['labels'])
        
        # Create category buttons
        for category in sorted(all_categories):
            btn = self.create_bubble_button(
                self.categories_bubble_frame.scrollable_frame, 
                category, 
                'category', 
                category
            )
            self.categories_bubble_frame.add_child(btn)
            self.category_buttons[category] = btn
            
            # Restore active state if this category was previously selected
            if category in self.active_category_filters:
                self._set_button_selected_category(btn)
        
        # Create label buttons
        for label in sorted(all_labels):
            btn = self.create_bubble_button(
                self.labels_bubble_frame.scrollable_frame, 
                label, 
                'label', 
                label
            )
            self.labels_bubble_frame.add_child(btn)
            self.label_buttons[label] = btn
            
            # Restore active state if this label was previously selected
            if label in self.active_label_filters:
                self._set_button_selected_label(btn)
                
    def get_filter_description(self):
        """Get a description of current filters for display"""
        parts = []
        if self.active_category_filters:
            parts.append(f"Categories: {', '.join(sorted(self.active_category_filters))}")
        if self.active_label_filters:
            parts.append(f"Labels: {', '.join(sorted(self.active_label_filters))}")
        
        if not parts:
            return ""
            
        mode = self.filter_mode_var.get()
        return f"[{mode}] " + f" {mode} ".join(parts)
        
    def get_filtered_ids(self, all_snippets: Dict) -> Set[str]:
        """Get snippet IDs that match current bubble filters"""
        if not self.active_category_filters and not self.active_label_filters:
            return set(all_snippets.keys())
            
        is_and_mode = self.filter_mode_var.get() == "AND"
        matching_ids = set()
        
        for snippet in all_snippets.values():
            snippet_categories = {snippet['category']}
            snippet_labels = set(snippet['labels'])
            
            if is_and_mode:
                # AND mode: snippet must match ALL active filters
                category_match = (not self.active_category_filters or 
                                self.active_category_filters.issubset(snippet_categories))
                label_match = (not self.active_label_filters or 
                             self.active_label_filters.issubset(snippet_labels))
                
                if category_match and label_match:
                    matching_ids.add(snippet['id'])
            else:
                # OR mode: snippet must match ANY active filter
                category_match = bool(self.active_category_filters.intersection(snippet_categories))
                label_match = bool(self.active_label_filters.intersection(snippet_labels))
                
                if category_match or label_match:
                    matching_ids.add(snippet['id'])
                    
        return matching_ids
        
    def has_active_filters(self) -> bool:
        """Check if any filters are currently active"""
        return bool(self.active_category_filters or self.active_label_filters)
