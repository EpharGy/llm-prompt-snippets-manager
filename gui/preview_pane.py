import tkinter as tk
from tkinter import ttk
from models.snippet_state import SnippetStateManager
from utils.ui_utils import create_tooltip

class PreviewPane(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Create header
        header = ttk.Label(
            self, 
            text="Preview", 
            font=('TkDefaultFont', 10, 'bold')
        )
        header.pack(fill='x', padx=5, pady=5)        # Create frame for text and scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        # Create preview text area
        self.preview_text = tk.Text(
            text_frame,
            wrap='word',
            font=('TkDefaultFont', 10),
            padx=8,
            pady=5
        )
        self.preview_text.pack(side='left', fill='both', expand=True)

        # Add tooltip
        create_tooltip(self.preview_text, "Preview of Selected Snippets")

        # Create scrollbar in the frame (not inside the text widget)
        scrollbar = ttk.Scrollbar(
            text_frame, 
            orient='vertical', 
            command=self.preview_text.yview
        )
        scrollbar.pack(side='right', fill='y')
        
        self.preview_text.configure(
            yscrollcommand=scrollbar.set,
            state='disabled'
        )

        # Create copy button
        self.copy_btn = ttk.Button(
            self,
            text="📋 Copy",
            command=self._copy_to_clipboard
        )
        self.copy_btn.pack(side='right', padx=5, pady=(0, 5))

        # Add tooltips
        create_tooltip(self.copy_btn, "Copy preview text to clipboard")
        create_tooltip(
            self.preview_text, 
            "Preview of selected snippets\nThe text will be combined in this order"
        )

        # Set initial text
        self.update_preview("No Snippets Selected")

    def update_preview(self, text: str):
        """Update the preview text"""
        self.preview_text.configure(state='normal')
        self.preview_text.delete('1.0', tk.END)
        self.preview_text.insert('1.0', text)
        self.preview_text.configure(state='disabled')
        
        # Enable/disable copy button based on content
        self.copy_btn.configure(
            state='normal' if text != "No Snippets Selected" else 'disabled'
        )

    def _copy_to_clipboard(self):
        """Copy preview text to clipboard"""
        text = self.preview_text.get('1.0', tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)