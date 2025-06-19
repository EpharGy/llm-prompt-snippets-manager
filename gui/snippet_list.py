from uuid import uuid4
import os
import tkinter as tk
from tkinter import ttk, messagebox
import traceback
from typing import List, Dict, Optional, Set
from copy import deepcopy

from models.snippet_state import SnippetState, SnippetStateManager
from utils.ui_utils import create_tooltip, configure_tree_style
from utils.font_manager import get_font_manager
from gui.snippet_dialog import SnippetDialog
from utils.logger import get_logger

logger = get_logger(__name__)

# Debug mode flag - set PROMPT_SNIPPETS_DEBUG=true to enable test buttons
DEBUG_MODE = os.environ.get('PROMPT_SNIPPETS_DEBUG', 'False').lower() == 'true'

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
                except Exception:                    pass            # Calculate row height with progressive scaling from Small's perfect spacing
            # Button height: font_size + internal padding (borders, etc.)
            button_height = base_font_size + 12            # Dynamic padding that scales proportionally with any base font size
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
            
        except Exception:
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

class SnippetList(ttk.Frame):
    """Widget for displaying and managing snippets in a tree view"""
    
    # Symbol constants
    SYMBOL_UNSELECTED = "➕"  # Plus sign
    SYMBOL_SELECTED = "✖"     # Bold X
    
    def __init__(self, parent, on_selection_changed=None, on_snippet_edit=None, on_snippets_delete=None):
        super().__init__(parent)
        self.on_selection_changed = on_selection_changed
        self.on_snippet_edit = on_snippet_edit
        self.on_snippets_delete = on_snippets_delete
        
        # Initialize state
        self.state_manager = SnippetStateManager.create()
        self.all_snippets = {}  # Complete list of all snippets
        self.snippets = {}      # Currently displayed snippets (may be filtered)
        self.delete_mode = False
        self.delete_selections = set()  # Snippets selected for deletion
        
        # Initialize bubble filter state
        self.active_category_filters = set()
        self.active_label_filters = set()
        self.category_buttons = {}
        self.label_buttons = {}
        self.filter_mode_var = tk.StringVar(value="AND")  # Initialize immediately
        
        # Create UI variables
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_changed)
        
        # Create outer frame for border control
        self.delete_frame = tk.Frame(
            self,
            bd=1,  # Border width
            relief='flat'  # No additional relief effects
        )
        self.delete_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.delete_frame)
        self.content_frame.pack(fill='both', expand=True)
          # Set initial border color
        self._set_frame_border('gray20')
        
        # Initialize font manager
        self.font_manager = get_font_manager()
        
        # Create UI
        self._create_ui()
        
        # Apply initial fonts
        self._apply_fonts()
        
        # Configure custom button styles for bubbles
        self._configure_bubble_styles()

    def _set_frame_border(self, color):
        """Helper to set border color consistently"""
        self.delete_frame.configure(bg=color)  # Border color

    def _add_test_snippet_1(self):
        """Add a test snippet with basic fields"""
        test_snippet = {
            'id': str(uuid4()),
            'name': 'Test Snippet 1',
            'category': 'Test',
            'labels': ['test', 'basic'],
            'prompt_text': 'This is a test prompt 1',
            'exclusive': False,
            'description': 'A basic test snippet'
        }
        self._add_new_snippet(test_snippet)
            
    def _add_test_snippet_2(self):
        """Add a test snippet with all fields"""
        test_snippet = {
            'id': str(uuid4()),
            'name': 'Test Snippet 2',
            'category': 'Test Advanced',
            'labels': ['test', 'advanced', 'example'],
            'prompt_text': 'This is a test prompt 2\nWith multiple lines\nAnd formatting',
            'exclusive': True,
            'description': 'A more complex test snippet with multiple lines and exclusive flag'        }
        self._add_new_snippet(test_snippet)
        
    def _create_ui(self):
        """Create all UI elements"""
        self._create_header_frame()
        self._create_tree_view()
        self._create_search_frame()
        self._create_filter_section()
        self._create_tooltips()
        
    def _create_header_frame(self):
        """Create header with title and buttons"""
        header_frame = ttk.Frame(self.content_frame)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        # Title
        header = ttk.Label(header_frame, text="Snippet List", font=('TkDefaultFont', 10, 'bold'))
        header.pack(side='left')
        self._header_label = header  # Save reference for font applying
        
        # Buttons frame
        button_frame = ttk.Frame(header_frame)
        button_frame.pack(side='right')
        
        # Test buttons (only in debug mode)
        if DEBUG_MODE:
            self.test1_btn = ttk.Button(button_frame, text="T1", width=3, command=self._add_test_snippet_1)
            self.test1_btn.pack(side='left', padx=2)
            
            self.test2_btn = ttk.Button(button_frame, text="T2", width=3, command=self._add_test_snippet_2)
            self.test2_btn.pack(side='left', padx=2)
            
            logger.info("🧪 DEBUG MODE: Test buttons enabled")
        
        # Add New Snippet button
        self.add_btn = ttk.Button(button_frame, text="➕", width=3, command=self._show_snippet_dialog)
        self.add_btn.pack(side='left', padx=2)
        
        # Clear Selection button
        self.clear_btn = ttk.Button(button_frame, text="🧹", width=3, command=self._clear_selections)
        self.clear_btn.pack(side='left', padx=2)
        
        # Delete button (rightmost) with gap separator
        ttk.Frame(button_frame, width=10).pack(side='left')  # Add a small gap
        self.delete_btn = ttk.Button(
            button_frame, 
            text="🗑️", 
            width=3,
            command=self._on_delete_button_click
        )
        self.delete_btn.pack(side='left', padx=2)

    def _create_search_frame(self):
        """Create search entry"""
        search_frame = ttk.Frame(self.content_frame)
        search_frame.pack(fill='x', padx=5, pady=(10, 5))
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.insert(0, "Search snippets...")
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        self.search_entry.pack(fill='x')
        self._search_entry = self.search_entry  # Save reference for font applying
        
    def _create_tree_view(self):
        """Create tree view with scrollbar"""
        container = ttk.Frame(self.content_frame)
        container.pack(fill='both', expand=True, padx=5)
        
        # Create tree with initial style
        self.tree = ttk.Treeview(
            container,
            columns=('Symbol', 'Name', 'Category', 'Exclusive', 'Labels'),
            show='headings',
            style='Normal.Treeview',
            selectmode='browse'  # Single selection mode
        )
        
        # Configure columns
        self.tree.heading('Symbol', text='')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Exclusive', text='Excl')
        self.tree.heading('Labels', text='Labels')
        
        self.tree.column('Symbol', width=30, stretch=False)
        self.tree.column('Exclusive', width=40, stretch=False)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Bind events - using <Button-1> instead of <ButtonRelease-1> for more immediate response
        self.tree.bind('<Button-1>', self._on_tree_click)
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        
    def _create_tooltips(self):
        """Create tooltips for UI elements"""
        if DEBUG_MODE:
            create_tooltip(self.test1_btn, "Add Test Snippet 1")
            create_tooltip(self.test2_btn, "Add Test Snippet 2")
        create_tooltip(self.add_btn, "Add new snippet")
        create_tooltip(self.delete_btn, "Delete selected snippet (double-click to edit/delete)")
        create_tooltip(self.clear_btn, "Clear all selections")
        create_tooltip(self.search_entry, "Search by name, category, labels, or prompt text")
        create_tooltip(self.filter_mode_btn, "Toggle between AND (all selected) and OR (any selected) filter mode")
        create_tooltip(self.clear_filters_btn, "Clear all active filters")

    def _create_filter_section(self):
        """Create the filter bubbles section"""
        # Main filter frame with standardized padding
        self.filter_frame = ttk.Frame(self.content_frame)
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
            
        # Re-apply filters with new mode
        self._apply_bubble_filters()
        
    def _clear_all_filters(self):
        """Clear all active bubble filters"""
        self.active_category_filters.clear()
        self.active_label_filters.clear()
        
        # Update button states to unselected style
        for btn in self.category_buttons.values():
            btn.configure(
                bg="#f0f0f0",
                fg="#333333", 
                activebackground="#e0e0e0",
                activeforeground="#000000",
                relief="raised",
                borderwidth=2          # Keep consistent border
            )
        for btn in self.label_buttons.values():
            btn.configure(
                bg="#f0f0f0",
                fg="#333333",
                activebackground="#e0e0e0", 
                activeforeground="#000000",
                relief="raised",
                borderwidth=2          # Keep consistent border
            )
              # Clear any existing search and show all snippets
        self._clear_search()
        self._apply_bubble_filters()
    
    def _create_bubble_button(self, parent, text, filter_type, filter_value):
        """Create a clickable bubble button with custom styling"""
        # Calculate initial font size based on current scale
        bubble_size = self.font_manager._calculate_font_size('default') - 1
        bubble_size = max(6, bubble_size)  # Minimum size of 6
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
            borderwidth=2,          # Keep consistent border width
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
                    except:
                        pass
                # Check if it's our WrappingFrame with scrollable_canvas
                elif hasattr(widget, 'scrollable_canvas'):
                    try:
                        scrollable_canvas = getattr(widget, 'scrollable_canvas', None)
                        if scrollable_canvas and hasattr(scrollable_canvas, 'yview_scroll'):
                            scrollable_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                            break
                    except:
                        pass
                widget = widget.master
            return "break"
        
        # Bind both Windows and Linux scroll wheel events
        btn.bind("<MouseWheel>", on_scroll)        # Windows
        btn.bind("<Button-4>", lambda e: on_scroll(type('obj', (object,), {'delta': 120})()))  # Linux scroll up
        btn.bind("<Button-5>", lambda e: on_scroll(type('obj', (object,), {'delta': -120})()))  # Linux scroll down
        
        # Don't pack here - WrappingFrame will handle positioning
        return btn
        
    def _toggle_bubble_filter(self, filter_type, filter_value, button):
        """Toggle a bubble filter on/off with visual feedback"""
        if filter_type == 'category':
            if filter_value in self.active_category_filters:
                self.active_category_filters.remove(filter_value)
                # Reset to unselected style
                button.configure(
                    bg="#f0f0f0", 
                    fg="#333333",
                    activebackground="#e0e0e0",
                    activeforeground="#000000",
                    relief="raised",
                    borderwidth=2          # Keep consistent border
                )
            else:
                self.active_category_filters.add(filter_value)
                # Set to selected category style (blue)
                button.configure(
                    bg="#2196F3",
                    fg="white", 
                    activebackground="#1976D2",
                    activeforeground="white",
                    relief="raised",       # Use raised relief for selected
                    borderwidth=2          # Keep consistent border
                )
        elif filter_type == 'label':
            if filter_value in self.active_label_filters:
                self.active_label_filters.remove(filter_value)
                # Reset to unselected style
                button.configure(
                    bg="#f0f0f0",
                    fg="#333333",
                    activebackground="#e0e0e0", 
                    activeforeground="#000000",
                    relief="raised",
                    borderwidth=2          # Keep consistent border
                )
            else:
                self.active_label_filters.add(filter_value)
                # Set to selected label style (green)
                button.configure(
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#388E3C",
                    activeforeground="white", 
                    relief="raised",       # Use raised relief for selected
                    borderwidth=2          # Keep consistent border
                )
                
        self._apply_bubble_filters()
        
    def _apply_bubble_filters(self):
        """Apply current bubble filters to snippet list"""
        # Check if we have active text search
        search_text = self.search_var.get().strip().lower()
        has_text_search = search_text and search_text != "search snippets..."
          # If no bubble filters are active
        if not self.active_category_filters and not self.active_label_filters:
            if has_text_search:
                # Let text search handle filtering
                self._on_search_changed()
            else:
                # Show all snippets - clear visual selection to avoid multi-highlighting during filter transitions
                self.state_manager.clear_search_filter()
                self._refresh_tree_view(preserve_selections=False)
            return
            
        # Get bubble filtered IDs
        bubble_matching_ids = self._get_bubble_filtered_ids()
        
        # If we have text search, combine the filters
        if has_text_search:
            text_matching_ids = set()
            for snippet in self.all_snippets.values():
                if (search_text in snippet['name'].lower() or
                    search_text in snippet['category'].lower() or
                    search_text in snippet.get('prompt_text', '').lower() or
                    any(search_text in label.lower() for label in snippet['labels'])):
                    text_matching_ids.add(snippet['id'])
            
            final_matching_ids = bubble_matching_ids.intersection(text_matching_ids)
            filter_desc = f"Text: '{search_text}' + {self._get_filter_description()}"
        else:
            final_matching_ids = bubble_matching_ids
            filter_desc = self._get_filter_description()
          # Apply filter - clear visual selection since we're filtering
        self.state_manager.set_search_filter(filter_desc, final_matching_ids)
        self._refresh_tree_view(preserve_selections=False)
        
    def _get_filter_description(self):
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
        
    def _refresh_bubble_filters(self):
        """Refresh the bubble filter buttons based on current snippets"""
        # Clear existing buttons using WrappingFrame methods
        self.categories_bubble_frame.clear_children()
        self.labels_bubble_frame.clear_children()
            
        self.category_buttons.clear()
        self.label_buttons.clear()
        
        # Collect all categories and labels
        all_categories = set()
        all_labels = set()
        
        for snippet in self.all_snippets.values():
            all_categories.add(snippet['category'])
            all_labels.update(snippet['labels'])
        
        # Create category buttons
        for category in sorted(all_categories):
            btn = self._create_bubble_button(
                self.categories_bubble_frame.scrollable_frame, 
                category, 
                'category', 
                category
            )
            self.categories_bubble_frame.add_child(btn)
            self.category_buttons[category] = btn
            
            # Restore active state if this category was previously selected
            if category in self.active_category_filters:
                btn.configure(
                    bg="#2196F3",
                    fg="white",
                    activebackground="#1976D2", 
                    activeforeground="white",
                    relief="raised",       # Use raised relief for selected
                    borderwidth=2          # Keep consistent border
                )
        
        # Create label buttons
        for label in sorted(all_labels):
            btn = self._create_bubble_button(
                self.labels_bubble_frame.scrollable_frame, 
                label, 
                'label', 
                label
            )
            self.labels_bubble_frame.add_child(btn)
            self.label_buttons[label] = btn
            
            # Restore active state if this label was previously selected
            if label in self.active_label_filters:
                btn.configure(
                    bg="#4CAF50",
                    fg="white",
                    activebackground="#388E3C",
                    activeforeground="white",
                    relief="raised",       # Use raised relief for selected
                    borderwidth=2          # Keep consistent border
                )

    def _on_tree_click(self, event):
        """Handle single click on tree item"""
        region = self.tree.identify("region", event.x, event.y)
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        
        if not item:
            return
            
        if self.delete_mode:
            # In delete mode, handle selection differently
            return self._handle_delete_mode_click(item)
            
        try:
            snippet = self.snippets.get(item)
            if not snippet:
                return
                
            # Handle state changes only when clicking symbol column
            if region == "cell" and column == '#1':
                # Check for exclusivity conflicts
                current_state = self.state_manager.get_state(snippet['id'])
                is_selecting = current_state != SnippetState.SELECTED
                
                if is_selecting and self._has_selection_conflict(snippet):
                    messagebox.showwarning(
                        "Selection Conflict",
                        f"Cannot select this snippet: An exclusive snippet is already selected in category '{snippet['category']}'.\n\n"
                        "You must deselect the existing snippet first."
                    )
                    return
                    
                # Toggle selection state
                new_state = (SnippetState.SELECTED 
                           if current_state != SnippetState.SELECTED 
                           else SnippetState.UNSELECTED)
                
                self.state_manager.set_state(
                    snippet['id'], 
                    new_state,
                    snippet['category'],
                    snippet['exclusive']
                )
                self._update_item_display(item)
                self._notify_selection_changed()
                    
        except Exception as e:
            print(f"Error handling click: {str(e)}")
            print(traceback.format_exc())

    def _has_selection_conflict(self, snippet: Dict) -> bool:
        """Check if selecting this snippet would violate exclusivity rules"""
        # If this snippet isn't exclusive and we're not trying to select it, no conflict
        if not snippet['exclusive']:
            return False
            
        # Check for any other selected snippets in the same category using all_snippets
        for existing in self.all_snippets.values():
            if (existing['category'] == snippet['category'] and 
                existing['id'] != snippet['id'] and
                existing['id'] in self.state_manager.selected_ids):
                return True
                
        return False

    def _on_tree_double_click(self, event):
        """Handle double click for editing"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        snippet = self.snippets.get(item)
        if not snippet:
            print(f"Warning: No snippet found for item {item}")  # Debug
            return
            
        print(f"Double-clicked snippet: {snippet['name']} ({snippet['id']})")  # Debug
        self._edit_snippet(snippet)

    def _edit_snippet(self, snippet: Dict):
        """Show edit dialog for snippet"""
        try:
            print(f"Editing snippet: {snippet['name']} ({snippet['id']})")  # Debug
            
            # Make sure we're using the latest version from all_snippets
            snippet_id = snippet['id']
            edit_snippet = self.all_snippets.get(snippet_id)
            
            if not edit_snippet:
                raise Exception(f"Snippet with id {snippet_id} not found in all_snippets")
                
            dialog = SnippetDialog(self, edit_snippet.copy(), is_edit=True)
            self.wait_window(dialog)
            
            if dialog.result:
                if dialog.result.get('delete'):
                    print(f"Deleting snippet: {snippet_id}")  # Debug
                    self._delete_snippets([snippet_id])
                elif dialog.save_as_new:
                    print("Saving as new snippet")  # Debug
                    new_snippet = dialog.result
                    new_snippet['id'] = str(uuid4())
                    self._add_new_snippet(new_snippet)
                else:
                    print(f"Updating snippet: {snippet_id}")  # Debug
                    self._update_snippet(dialog.result)
                    
        except Exception as e:
            print(f"Error editing snippet: {str(e)}")
            traceback.print_exc()  # Add stack trace
            messagebox.showerror("Error", "Failed to edit snippet")

    def _on_search_changed(self, *args):
        """Handle search text changes"""
        search_text = self.search_var.get().strip().lower()
        
        if search_text == "search snippets...":
            return
                      # Handle empty search - check if we have bubble filters
        if not search_text:
            # If we have active bubble filters, reapply them, otherwise show all
            if self.active_category_filters or self.active_label_filters:
                self._apply_bubble_filters()
            else:
                # No search text and no bubble filters - but this is a transition from search, so clear visual selection
                self.state_manager.set_search_filter('', set(self.all_snippets.keys()))
                self._refresh_tree_view(preserve_selections=False)
            return
                    
        # Combine text search with bubble filters
        text_matching_ids = set()
        for snippet in self.all_snippets.values():
            # Create searchable versions of text fields (convert underscores to spaces for better matching)
            searchable_name = snippet['name'].lower().replace('_', ' ')
            searchable_category = snippet['category'].lower().replace('_', ' ')
            searchable_prompt = snippet.get('prompt_text', '').lower().replace('_', ' ')
            searchable_labels = [label.lower().replace('_', ' ') for label in snippet['labels']]
            
            # Check if search text matches any field (supports both underscore and space versions)
            if (search_text in searchable_name or
                search_text in searchable_category or
                search_text in searchable_prompt or
                any(search_text in label for label in searchable_labels) or
                # Also check original versions with underscores
                search_text in snippet['name'].lower() or
                search_text in snippet['category'].lower() or
                search_text in snippet.get('prompt_text', '').lower() or
                any(search_text in label.lower() for label in snippet['labels'])):
                text_matching_ids.add(snippet['id'])
        
        # If we have bubble filters, intersect with bubble filter results
        if self.active_category_filters or self.active_label_filters:
            bubble_matching_ids = self._get_bubble_filtered_ids()
            final_matching_ids = text_matching_ids.intersection(bubble_matching_ids)
        else:
            final_matching_ids = text_matching_ids
        
        print(f"Found {len(final_matching_ids)} matching snippets")  # Debug print

        # Create combined filter description
        filter_desc = f"Text: '{search_text}'"
        if self.active_category_filters or self.active_label_filters:
            bubble_desc = self._get_filter_description()
            filter_desc += f" + {bubble_desc}"        # Update state and refresh - clear visual selection since we're searching
        self.state_manager.set_search_filter(filter_desc, final_matching_ids)
        self._refresh_tree_view(preserve_selections=False)
        
    def _get_bubble_filtered_ids(self):
        """Get snippet IDs that match current bubble filters"""
        if not self.active_category_filters and not self.active_label_filters:
            return set(self.all_snippets.keys())
            
        is_and_mode = self.filter_mode_var.get() == "AND"
        matching_ids = set()
        
        for snippet in self.all_snippets.values():
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

    def _on_search_focus_in(self, event):
        """Handle search entry focus"""
        if self.search_var.get().strip() == "Search snippets...":
            self.search_entry.delete(0, tk.END)
            self.search_var.set('')
            self.search_entry.config(foreground='black')

    def _on_search_focus_out(self, event):
        """Handle search entry blur"""
        current_text = self.search_var.get().strip()
        if not current_text:
            self.search_var.set("Search snippets...")
            self.search_entry.config(foreground='gray')            # Clear any lingering filter
            self.state_manager.set_search_filter('', set())
            self._refresh_tree_view(preserve_selections=False)  # Clear visual selection on focus out

    def _refresh_tree_view(self, preserve_selections=True):
        """Refresh tree view display
        
        Args:
            preserve_selections: If True, restore visual selection highlighting (default)
        """
        
        # Store current selections from state manager
        selected_ids = set(self.state_manager.selected_ids)
        
        # Clear tree and snippet mapping
        self.tree.delete(*self.tree.get_children())
        self.snippets.clear()
        
        # Clear any existing visual selection
        self.tree.selection_remove(self.tree.selection())
        
        # Determine which snippets to display
        display_snippets = {}
        if self.state_manager.is_filtered:
            # Show only filtered snippets
            for snippet_id in self.state_manager.filtered_ids:
                if snippet_id in self.all_snippets:
                    display_snippets[snippet_id] = self.all_snippets[snippet_id]
            print(f"Showing {len(display_snippets)} filtered snippets")  # Debug
        else:
            # Show all snippets
            display_snippets = dict(self.all_snippets)  # Make a copy
            print(f"Showing all snippets ({len(display_snippets)} total)")  # Debug
        
        # Add snippets to tree
        for snippet_id, snippet in display_snippets.items():
            item_id = self._add_snippet_to_tree(snippet)
            self.snippets[item_id] = snippet
            
            # Only restore visual selection if not clearing it
            if preserve_selections and snippet_id in selected_ids:
                self.tree.selection_add(item_id)
                
        # Update all item displays to show correct state
        for item_id in self.tree.get_children():
            snippet = self.snippets.get(item_id)
            if snippet and snippet['id'] in selected_ids:
                self.state_manager.set_state(
                    snippet['id'],
                    SnippetState.SELECTED,
                    snippet['category'],
                    snippet['exclusive']
                )
            self._update_item_display(item_id)

    def _update_item_display(self, item_id: str):
        """Update display of a single tree item"""
        snippet = self.snippets.get(item_id)
        if not snippet:
            return
            
        state = self.state_manager.get_state(snippet['id'])
        values = list(self.tree.item(item_id)['values'])
        values[0] = self._get_symbol_for_state(state)
        self.tree.item(item_id, values=values)
        
    def _get_symbol_for_state(self, state: SnippetState) -> str:
        """Get display symbol for state"""
        return self.SYMBOL_SELECTED if state == SnippetState.SELECTED else self.SYMBOL_UNSELECTED

    def _add_snippet_to_tree(self, snippet: Dict) -> str:
        """Add single snippet to tree and return item ID"""
        state = self.state_manager.get_state(snippet['id'])
        symbol = self._get_symbol_for_state(state)
        
        item_id = self.tree.insert('', 'end', values=(
            symbol,
            snippet['name'],
            snippet['category'],
            '✓' if snippet['exclusive'] else '',
            ', '.join(snippet['labels'])
        ))
        
        return item_id

    def _edit_selected(self):
        """Edit currently selected snippet"""
        selected = [s for s in self.snippets.values() 
                   if s['id'] in self.state_manager.selected_ids]
        
        if not selected:
            messagebox.showinfo("Info", "Select a snippet to edit")
            return
            
        if len(selected) > 1:
            messagebox.showinfo("Info", "Select only one snippet to edit")
            return
            
        self._show_snippet_dialog(selected[0])

    def _clear_selections(self):
        """Clear all selections"""
        # Clear state manager
        self.state_manager.clear_all_selections()
        
        # Reset all tree items to unselected state
        for item_id in self.tree.get_children():
            self._update_item_display(item_id)
        
        # Clear tree selection
        self.tree.selection_remove(*self.tree.selection())
        
        # Update preview
        self._notify_selection_changed()

    def _clear_search(self):
        """Clear search and restore view"""
        was_filtered = self.state_manager.is_filtered
        
        # Reset search entry widget
        self.search_entry.delete(0, tk.END)
        self.search_var.set('Search snippets...')
        self.search_entry.config(foreground='gray')
        
        # Clear filter state
        self.state_manager.clear_search_filter()
        
        # Refresh view and notify if needed
        self._refresh_tree_view()
        if was_filtered:
            self._notify_selection_changed()

    def _notify_selection_changed(self):
        """Notify parent of selection changes"""
        if self.on_selection_changed:
            # Get currently selected snippets from all_snippets
            selected = [
                snippet for snippet in self.all_snippets.values()
                if snippet['id'] in self.state_manager.selected_ids
            ]
            
            if len(selected) > 0:
                snippet_names = [s['name'] for s in selected]
                logger.debug(f"🎯 Selected {len(selected)} snippets: {', '.join(snippet_names)}")
            else:
                logger.debug("🎯 No snippets selected")
                
            self.on_selection_changed(selected)

    def load_snippets(self, snippets: List[Dict]):
        """Load snippets into view"""
        # Store current selected IDs before clearing
        selected_ids = set(self.state_manager.selected_ids)
        
        # Clear collections
        self.all_snippets.clear()
        self.snippets.clear()
        self.tree.delete(*self.tree.get_children())
        
        # First store all snippets
        for snippet in snippets:
            self.all_snippets[snippet['id']] = snippet
            
        # Then display them and restore selections
        for snippet in snippets:
            item_id = self._add_snippet_to_tree(snippet)
            self.snippets[item_id] = snippet
            
            # If this snippet was selected, restore its state
            if snippet['id'] in selected_ids:
                self.state_manager.set_state(
                    snippet['id'],
                    SnippetState.SELECTED,
                    snippet['category'],
                    snippet['exclusive']
                )
                self._update_snippet_display(item_id)
                
        # Refresh bubble filters with new snippets
        self._refresh_bubble_filters()

    def _show_snippet_dialog(self, snippet: Optional[Dict] = None):
        """Show dialog for creating/editing snippet"""
        try:
            print("Opening snippet dialog")  # Debug
            dialog = SnippetDialog(self, snippet)
            self.wait_window(dialog)
            
            if dialog.result:
                if not dialog.result.get('id'):
                    dialog.result['id'] = str(uuid4())
                    print(f"Creating new snippet with ID: {dialog.result['id']}")  # Debug
                    self._add_new_snippet(dialog.result)
                else:
                    print(f"Updating snippet with ID: {dialog.result['id']}")  # Debug
                    self._update_snippet(dialog.result)
        except Exception as e:
            print(f"Error in snippet dialog: {str(e)}")
            traceback.print_exc()  # Add stack trace
            messagebox.showerror("Error", "Failed to process snippet")
    
    def _add_new_snippet(self, snippet: Dict):
        """Add new snippet"""
        try:
            logger.info(f"➕ Adding new snippet: '{snippet['name']}' (Category: {snippet.get('category', 'None')})")
            logger.debug(f"Snippet ID: {snippet['id']}")
            
            # Call parent handler for storage update
            if self.on_snippet_edit:
                if not self.on_snippet_edit(snippet):
                    raise Exception("Failed to save to storage")
                
            # Store in our collections
            self.all_snippets[snippet['id']] = snippet.copy()

            # Always use the smart refresh logic that preserves state properly
            logger.debug("Refreshing view with smart state preservation")
            self._refresh_tree_view()
            
            # Always refresh bubble filters to include any new categories/labels
            logger.debug("Updating filter options with new categories/labels")
            self._refresh_bubble_filters()
            
            logger.info(f"✅ Successfully added snippet: '{snippet['name']}'")
            return True
            
        except Exception as e:
            print(f"Error in _add_new_snippet: {str(e)}")
            traceback.print_exc()
            messagebox.showerror("Error", "Failed to Save Snippet")
            return False

    def _update_snippet(self, snippet: Dict):
        """Update existing snippet"""
        try:
            logger.info(f"✏️ Updating snippet: '{snippet['name']}' (Category: {snippet.get('category', 'None')})")
            logger.debug(f"Snippet ID: {snippet['id']}")
            
            # Call parent handler for storage update
            if self.on_snippet_edit:
                if not self.on_snippet_edit(snippet):
                    raise Exception("Failed to update in storage")
            
            # Update our collections
            self.all_snippets[snippet['id']] = snippet.copy()
            
            # Update any tree items showing this snippet
            for item_id, tree_snippet in self.snippets.items():
                if tree_snippet['id'] == snippet['id']:
                    self.snippets[item_id] = snippet.copy()
                    
            # Refresh view and notify about selection changes
            logger.debug("Refreshing display and selection state")
            self._refresh_tree_view()
            self._notify_selection_changed()  # Ensure preview updates
            
            # Refresh bubble filters in case categories/labels changed
            logger.debug("Updating filter options after changes")
            self._refresh_bubble_filters()
            
            logger.info(f"✅ Successfully updated snippet: '{snippet['name']}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update snippet: {str(e)}")
            traceback.print_exc()  # Add stack trace
            messagebox.showerror("Error", "Failed to Update Snippet")
            return False

    def _delete_snippets(self, snippet_ids: List[str]) -> bool:
        """Delete snippets by their IDs"""
        try:
            # Get snippet names for better logging
            snippet_names = [
                self.all_snippets[sid]['name'] for sid in snippet_ids 
                if sid in self.all_snippets
            ]
            
            if len(snippet_names) == 1:
                logger.info(f"🗑️ Deleting snippet: '{snippet_names[0]}'")
            else:
                logger.info(f"🗑️ Deleting {len(snippet_names)} snippets: {', '.join(snippet_names)}")
            
            logger.debug(f"Snippet IDs: {snippet_ids}")
            
            # Call parent handler with delete request
            if self.on_snippets_delete:  # Use on_snippets_delete for bulk deletion
                # Get the actual snippet objects for the callback
                snippets_to_delete = [
                    self.all_snippets[sid] for sid in snippet_ids 
                    if sid in self.all_snippets
                ]
                self.on_snippets_delete(snippets_to_delete)
            
            # Clear selections in state manager
            self.state_manager.clear_selections(snippet_ids)
            
            # Remove from all collections
            for snippet_id in snippet_ids:
                if snippet_id in self.all_snippets:
                    self.all_snippets.pop(snippet_id)
                    # Remove from snippets dict by finding tree items with this snippet ID
                    items_to_remove = []
                    for item_id, snippet in self.snippets.items():
                        if snippet['id'] == snippet_id:
                            items_to_remove.append(item_id)
                    for item_id in items_to_remove:
                        self.snippets.pop(item_id, None)
            
            # Refresh display and notify any selection changes
            logger.debug("Refreshing display after deletion")
            self._refresh_tree_view()
            self._notify_selection_changed()
            
            # Refresh bubble filters in case categories/labels are no longer used
            logger.debug("Updating filter options after deletion")
            self._refresh_bubble_filters()
            
            if len(snippet_names) == 1:
                logger.info(f"✅ Successfully deleted snippet: '{snippet_names[0]}'")
            else:
                logger.info(f"✅ Successfully deleted {len(snippet_names)} snippets")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete snippets: {str(e)}")
            traceback.print_exc()
            return False

    def _toggle_delete_mode(self):
        """Toggle delete mode on/off"""
        self.delete_mode = not self.delete_mode
        
        if self.delete_mode:
            # Enter delete mode
            self.delete_btn.configure(text="✔️")  # Change to checkmark
            create_tooltip(self.delete_btn, "Confirm deletion (click to delete selected snippets)")
            # Update visual feedback
            self.delete_frame.configure(background='#ffebeb')  # Light red background
            for child in self.delete_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(background='#ffebeb')
            
            # Disable other interactions
            self.search_entry.configure(state='disabled')
            self.add_btn.configure(state='disabled')
            self.clear_btn.configure(state='disabled')
            if DEBUG_MODE:
                self.test1_btn.configure(state='disabled')
                self.test2_btn.configure(state='disabled')
            
            # Clear any existing selections
            self._clear_selections()
            self.delete_selections.clear()
            
            # Clear tree selection
            self.tree.selection_remove(self.tree.selection())
            
        else:
            # Exit delete mode
            self.delete_btn.configure(text="🗑️")
            create_tooltip(self.delete_btn, "Delete selected snippet (double-click to edit/delete)")
            # Update visual feedback
            self.delete_frame.configure(background='#ffffff')  # White background
            for child in self.delete_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    child.configure(background='#ffffff')
            
            # Re-enable interactions
            self.search_entry.configure(state='normal')
            self.add_btn.configure(state='normal')
            self.clear_btn.configure(state='normal')
            if DEBUG_MODE:
                self.test1_btn.configure(state='normal')
                self.test2_btn.configure(state='normal')
            
            # Clear delete selections
            self.delete_selections.clear()
            # Clear visual selections in tree
            self.tree.selection_remove(self.tree.selection())
            
        # Force the whole widget to update
        self.update()

    def _confirm_delete(self):
        """Show confirmation dialog and delete selected snippets if confirmed"""
        print(f"Confirming delete with {len(self.delete_selections)} selections")
        
        # If no selections, just exit delete mode
        if not self.delete_selections:
            print("No selections, exiting delete mode")
            self._exit_delete_mode()
            return
            
        # Get snippets to delete - convert tree item IDs to snippet IDs
        snippets_to_delete = []
        names_to_delete = []
        snippet_ids_to_delete = []
        
        for item_id in self.delete_selections:
            snippet = self.snippets.get(item_id)
            if snippet:
                snippets_to_delete.append(snippet)
                names_to_delete.append(f"- {snippet['name']}")
                snippet_ids_to_delete.append(snippet['id'])
        
        # Show confirmation dialog
        msg = f"Are you sure you want to delete these snippets?\n\n" + "\n".join(names_to_delete)
        if messagebox.askyesno("Confirm Delete", msg, icon='warning'):
            print(f"Deleting {len(snippets_to_delete)} snippets...")
            success = self._delete_snippets(snippet_ids_to_delete)
            
            if success:
                print(f"Successfully deleted {len(snippet_ids_to_delete)} snippets")
            else:
                messagebox.showerror("Error", "Failed to delete some or all snippets")
        
        # Always exit delete mode
        self._exit_delete_mode()

    def _handle_delete_mode_click(self, item):
        """Handle click events when in delete mode"""
        if not item:
            return
            
        try:
            snippet = self.snippets.get(item)
            if not snippet:
                return
                
            # Toggle selection
            if item in self.tree.selection():
                # Deselect
                self.tree.selection_remove(item)
                self.delete_selections.discard(item)  # Store the item id for deletion
            else:
                # Select
                self.tree.selection_add(item)
                self.delete_selections.add(item)  # Store the item id for deletion
                
            print(f"Delete selections updated: {len(self.delete_selections)} items")
            # Prevent normal selection handling from interfering
            return "break"
            
        except Exception as e:
            print(f"Error in delete mode click handling: {e}")

    def _on_delete_button_click(self):
        """Handle delete button click event"""
        print(f"Delete button clicked. Current mode: {self.delete_mode}")
        
        if self.delete_mode:
            # Already in delete mode, handle confirmation
            self._confirm_delete()
        else:
            # Enter delete mode - change visuals first
            print("Entering delete mode, changing visuals...")
            
            # Update frame appearance
            self._set_frame_border('#ff3333')  # Bright red border
            
            # Force immediate visual update
            self.delete_frame.update()
            self.update_idletasks()
            
            self.delete_mode = True
            
            # Update button and tooltip
            self.delete_btn.configure(text="✔️")
            create_tooltip(self.delete_btn, "Confirm Deletion / Cancel")
            
            # Disable other interactions
            self.search_entry.configure(state='disabled')
            self.add_btn.configure(state='disabled')
            self.clear_btn.configure(state='disabled')
            if DEBUG_MODE:
                self.test1_btn.configure(state='disabled')
                self.test2_btn.configure(state='disabled')
            
            # Clear delete selections but preserve normal selections
            self.delete_selections.clear()
            self.tree.selection_remove(*self.tree.selection())
            
            # Final force update of entire widget
            self.update()
            
    def _exit_delete_mode(self):
        """Exit delete mode and restore normal state"""
        print("Exiting delete mode...")
        
        # Restore normal visuals
        self._set_frame_border('gray20')  # Dark border
        
        # Force immediate visual update
        self.delete_frame.update()
        self.update_idletasks()
        
        self.delete_mode = False
        
        # Restore button and tooltip
        self.delete_btn.configure(text="🗑️")
        create_tooltip(self.delete_btn, "Delete selected snippet (double-click to edit/delete)")
        
        # Re-enable interactions
        self.search_entry.configure(state='normal')
        self.add_btn.configure(state='normal')
        self.clear_btn.configure(state='normal')
        if DEBUG_MODE:
            self.test1_btn.configure(state='normal')
            self.test2_btn.configure(state='normal')
        
        # Clear delete selections
        self.delete_selections.clear()
        self.tree.selection_remove(*self.tree.selection())
        
        # Final force update of entire widget
        self.update()
        
    def _refresh_ui(self):
        """Refresh the UI after state changes"""
        selected_before = set(self.tree.selection())
        
        # Clear and repopulate tree
        self.tree.delete(*self.tree.get_children())
        self._populate_tree()
        
        # Restore selections that still exist
        for item_id in selected_before:
            if item_id in self.snippets:
                self.tree.selection_add(item_id)
                
    def _populate_tree(self):
        """Populate the tree with current snippets"""
        # Sort snippets by category and name
        sorted_snippets = sorted(
            self.snippets.values(),
            key=lambda x: (x.get('category', ''), x.get('name', ''))
        )
        
        # Add to tree
        for snippet in sorted_snippets:
            values = (
                self.SYMBOL_SELECTED if snippet['id'] in self.state_manager.selected_ids 
                else self.SYMBOL_UNSELECTED,
                snippet.get('name', ''),
                snippet.get('category', ''),
                '✓' if snippet.get('exclusive') else '',
                ', '.join(snippet.get('labels', []))
            )
            self.tree.insert('', 'end', iid=snippet['id'], values=values)

    def get_selected_snippets(self):
        """Get currently selected snippets"""
        return [s for s in self.all_snippets.values() 
                if s['id'] in self.state_manager.selected_ids]

    def _update_snippet_display(self, item_id: str):
        """Update the display of a snippet item in the tree view based on its current state"""
        if not item_id or item_id not in self.snippets:
            return

        # Check if the tree item still exists (it might have been deleted)
        try:
            if not self.tree.exists(item_id):
                return
        except tk.TclError:
            # Tree item doesn't exist anymore
            return

        snippet = self.snippets[item_id]
        state = self.state_manager.get_state(snippet['id'])

        # Update the symbol based on state
        symbol = self.SYMBOL_SELECTED if state == SnippetState.SELECTED else self.SYMBOL_UNSELECTED
        
        # Update the item in the tree view - use column name 'Symbol', not 'state'
        try:
            self.tree.set(item_id, 'Symbol', symbol)
        except tk.TclError as e:
            print(f"Error updating tree item {item_id}: {e}")
            return
        
        # If we're in delete mode, handle highlighting for deletion
        if self.delete_mode:
            try:
                if item_id in self.delete_selections:
                    self.tree.item(item_id, tags=('delete_selected',))
                else:
                    self.tree.item(item_id, tags=())
            except tk.TclError:
                # Tree item might have been deleted, ignore
                pass

    def _configure_bubble_styles(self):
        """Configure custom styles for bubble buttons"""
        style = ttk.Style()
        
        # Unselected bubble style - light gray/neutral
        style.configure("Bubble.Unselected.TButton",
            background="#f0f0f0",
            foreground="#333333",
            borderwidth=1,
            relief="raised",
            padding=(8, 4),
            focuscolor="none"
        )
        
        # Selected category bubble style - blue theme
        style.configure("Bubble.Category.TButton", 
            background="#2196F3",  # Material Blue
            foreground="white",
            borderwidth=2,
            relief="solid",
            padding=(8, 4),
            focuscolor="none"
        )
        
        # Selected label bubble style - green theme  
        style.configure("Bubble.Label.TButton",
            background="#4CAF50",  # Material Green
            foreground="white", 
            borderwidth=2,
            relief="solid",
            padding=(8, 4),
            focuscolor="none"
        )
        
        # Map all states for unselected bubbles
        style.map("Bubble.Unselected.TButton",
            background=[('active', '#e0e0e0'), ('pressed', '#d0d0d0'), ('!active', '#f0f0f0')],
            foreground=[('active', '#000000'), ('pressed', '#000000'), ('!active', '#333333')],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        # Map all states for selected category bubbles - force background color
        style.map("Bubble.Category.TButton",
            background=[('active', '#1976D2'), ('pressed', '#1565C0'), ('!active', '#2196F3')],
            foreground=[('active', 'white'), ('pressed', 'white'), ('!active', 'white')],
            relief=[('pressed', 'sunken'), ('!pressed', 'solid')]
        )
        
        # Map all states for selected label bubbles - force background color
        style.map("Bubble.Label.TButton", 
            background=[('active', '#388E3C'), ('pressed', '#2E7D32'), ('!active', '#4CAF50')],
            foreground=[('active', 'white'), ('pressed', 'white'), ('!active', 'white')],
            relief=[('pressed', 'sunken'), ('!pressed', 'solid')]
        )
    
    def _apply_fonts(self):
        """Apply font manager fonts to all UI components"""
        try:
            # Apply font to tree view
            if hasattr(self, 'tree'):
                tree_font = self.font_manager.get_font_tuple('tree')
                style = ttk.Style()
                style.configure('Normal.Treeview', font=tree_font)
                style.configure('Normal.Treeview.Heading', font=self.font_manager.get_font_tuple('tree', 'bold'))
                
            # Apply font to header label
            if hasattr(self, '_header_label'):
                header_font = self.font_manager.get_font('heading', 'bold')
                self._header_label.configure(font=header_font)
                
            # Apply font to search entry
            if hasattr(self, '_search_entry'):
                default_font = self.font_manager.get_font_tuple('default')
                self._search_entry.configure(font=default_font)            # Apply fonts to filter section elements
            default_font = self.font_manager.get_font_tuple('default')
            
            # Get centralized static font for buttons
            static_button_font = self.font_manager.get_static_font('button')
            static_bubble_font = self.font_manager.get_static_font('bubble')
            
            # Apply font to search entry
            if hasattr(self, '_search_entry'):
                self._search_entry.configure(font=default_font)
            
            # Skip button font updates to avoid type checker issues
            # Buttons use centralized static fonts which work well across displays
            logger.debug(f"Button fonts using static configuration: {static_button_font}")
            logger.debug(f"Bubble fonts using static configuration: {static_bubble_font}")
              # Apply fonts to filter labels (these work without type issues)
            self._apply_fonts_to_filter_labels()
            
            # Apply dynamic fonts to filter bubbles (tk.Button widgets support this)
            self._apply_fonts_to_bubbles()
                
            logger.debug("Fonts applied to SnippetList components")
            
        except Exception as e:
            logger.error(f"Error applying fonts to SnippetList: {str(e)}")
    
    def _apply_fonts_to_filter_labels(self):
        """Apply fonts to filter section labels"""
        try:
            default_font = self.font_manager.get_font_tuple('default')
            
            # Find and update filter labels recursively
            if hasattr(self, 'filter_frame'):
                for widget in self.filter_frame.winfo_children():
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
                
        except Exception:
            pass
    
    def _apply_fonts_to_bubbles(self):
        """Apply dynamic fonts to bubble filter buttons"""
        try:
            # Get dynamic font size for bubbles (slightly smaller than default)
            bubble_size = self.font_manager._calculate_font_size('default') - 1
            bubble_size = max(6, bubble_size)  # Minimum size of 6
            bubble_font = ('TkDefaultFont', bubble_size)
              # Update all bubble buttons in both containers
            self._update_bubble_fonts_recursive(self.categories_bubble_frame, bubble_font)
            self._update_bubble_fonts_recursive(self.labels_bubble_frame, bubble_font)
            
            # Update bubble container row heights to match new font size
            if hasattr(self, 'categories_bubble_frame'):
                self.categories_bubble_frame.update_row_height()
            if hasattr(self, 'labels_bubble_frame'):
                self.labels_bubble_frame.update_row_height()
            
            logger.debug(f"Bubble fonts updated to dynamic size: {bubble_font}")
                    
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
        except Exception:
            pass  # Skip widgets that don't support font configuration
    
    def refresh_fonts(self):
        """Public method to refresh fonts (called from main app)"""
        self._apply_fonts()