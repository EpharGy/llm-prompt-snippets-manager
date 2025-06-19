import tkinter as tk
from tkinter import ttk
from utils.ui_utils import create_tooltip, set_app_icon
from utils.logger import get_logger

logger = get_logger(__name__)

class PromptWindow(tk.Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        
        self.parent = parent
        self.on_close_callback = on_close_callback
        
        self.title("Prompt Preview")
        self.geometry("600x300")
        self.resizable(True, True)
        
        # Set application icon
        set_app_icon(self)
        
        # Configure window to stay on top but not be modal
        self.transient(parent)
        # Remove grab_set() to allow interaction with main window
        
        # Position window relative to parent
        self.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
          # Create header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        header_label = ttk.Label(
            header_frame, 
            text="Prompt Preview", 
            font=('TkDefaultFont', 12, 'bold')
        )
        header_label.pack(side='left')
        
        # Create copy button in header (right side)
        self.copy_btn = ttk.Button(
            header_frame,
            text="📋 Copy",
            command=self._copy_to_clipboard
        )
        self.copy_btn.pack(side='right')
        create_tooltip(self.copy_btn, "Copy prompt text to clipboard")
          # Create frame for text and scrollbar with proper padding
        text_frame = ttk.Frame(self)
        text_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Create scrollbar FIRST (always visible)
        scrollbar = ttk.Scrollbar(
            text_frame, 
            orient='vertical'
        )
        scrollbar.pack(side='right', fill='y')
        
        # Create text widget
        self.text_widget = tk.Text(
            text_frame,
            wrap='word',
            font=('TkDefaultFont', 11),
            padx=15,  # Increased internal padding
            pady=10,  # Increased internal padding
            bg='white',
            relief='sunken',
            borderwidth=1,
            yscrollcommand=scrollbar.set
        )
        self.text_widget.pack(side='left', fill='both', expand=True)
          # Connect scrollbar to text widget
        scrollbar.configure(command=self.text_widget.yview)
        
        # Set text widget to disabled state initially
        self.text_widget.configure(state='disabled')
        
        # Add tooltip to text widget
        create_tooltip(
            self.text_widget, 
            "Full prompt text preview\nResize window to see more content"
        )
        
        # Set initial content
        self.update_prompt("No Snippets Selected")
          # Handle window close event properly
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _on_window_close(self):
        """Handle window close event"""
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def update_prompt(self, text: str):
        """Update the prompt text"""
        # Ensure text is clean with no trailing whitespace
        clean_text = text.strip() if text else ""
        
        self.text_widget.configure(state='normal')
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', clean_text)
        self.text_widget.configure(state='disabled')
        
        # Store clean text for copying
        self.current_text = clean_text
        
        # Enable/disable copy button based on content
        has_content = clean_text and clean_text != "No Snippets Selected"
        self.copy_btn.configure(state='normal' if has_content else 'disabled')

    def _copy_to_clipboard(self):
        """Copy prompt text to clipboard"""
        # Use stored clean text instead of reading from widget
        if hasattr(self, 'current_text') and self.current_text:
            self.clipboard_clear()
            self.clipboard_append(self.current_text)
            
            logger.info(f"📋 Copied {len(self.current_text)} characters from prompt preview")
            
            # Brief visual feedback - same as main window
            original_text = self.copy_btn.cget('text')
            self.copy_btn.configure(text="✓ Copied!")
            self.after(1000, lambda: self.copy_btn.configure(text=original_text))
