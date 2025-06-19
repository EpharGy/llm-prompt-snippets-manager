import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional, Union
from uuid import uuid4

from gui.snippet_list import SnippetList
from gui.prompt_window import PromptWindow
from models.data_manager import DataManager
from models.snippet_state import SnippetStateManager
from utils.state_utils import get_category_selections
from utils.ui_utils import create_tooltip, set_app_icon
from utils.font_manager import get_font_manager, setup_window_dpi_monitoring
from utils.logger import get_logger

logger = get_logger(__name__)

class PromptSnippetsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("LLM Prompt Snippets Manager")
        self.geometry("1200x800")
        
        # Set application icon
        set_app_icon(self)
        
        # Remove fullscreen
        # self.state('zoomed')  # Remove this line
          # Initialize managers
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        self.data_manager = DataManager(data_dir)
        self.state_manager = SnippetStateManager.create()
        
        # Setup font manager with DPI monitoring
        self.font_manager = setup_window_dpi_monitoring(self)
        
        # Create main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create snippet list container
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Create and configure snippet list
        self.snippet_list = SnippetList(
            list_frame,
            on_selection_changed=self._on_selection_changed,
            on_snippet_edit=self._on_snippet_edit,
            on_snippets_delete=self._on_snippets_delete
        )
        self.snippet_list.pack(fill='both', expand=True)
          # Create right button panel
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='right', fill='y', padx=(0, 0))
        
        # Create font controls section
        font_frame = ttk.LabelFrame(button_frame, text="Font Size", padding=5)
        font_frame.pack(fill='x', pady=(0, 15))
          # Font scale dropdown
        current_scale = self.font_manager.get_font_scale()
        current_display_name = self.font_manager.get_available_scales()[current_scale]
        self.font_scale_var = tk.StringVar(value=current_display_name)
        self.font_scale_combo = ttk.Combobox(
            font_frame,
            textvariable=self.font_scale_var,
            values=list(self.font_manager.get_available_scales().values()),
            state='readonly',
            width=12
        )
        self.font_scale_combo.pack(pady=(0, 5))
        self.font_scale_combo.bind('<<ComboboxSelected>>', self._on_font_scale_changed)
        
        # Add tooltip for font dropdown
        create_tooltip(self.font_scale_combo, "Adjust font size for all text\nAuto: Automatic scaling based on display DPI")
        
        # Create buttons with proper spacing
        self.show_prompt_btn = ttk.Button(
            button_frame,
            text="👁 Show Prompt",
            command=self._toggle_prompt_window,
            width=15
        )
        self.show_prompt_btn.pack(pady=(0, 10))
        
        self.copy_btn = ttk.Button(
            button_frame,
            text="📋 Copy",
            command=self._copy_to_clipboard,
            width=15
        )
        self.copy_btn.pack(pady=(0, 10))
        
        # Add tooltips
        create_tooltip(self.show_prompt_btn, "Show/hide prompt preview window")
        create_tooltip(self.copy_btn, "Copy selected snippets to clipboard")
        
        # Initialize prompt window state
        self.prompt_window = None
        self.current_prompt_text = "No Snippets Selected"
        
        # Load initial data
        self._load_snippets()
        
        # Set up close handler
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_snippets(self) -> None:
        """Load snippets from data manager"""
        try:
            snippets = self.data_manager.load_snippets_for_gui()
            self.snippet_list.load_snippets(snippets)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load snippets: {str(e)}")

    def _on_selection_changed(self, selected_snippets: List[Dict]) -> None:
        """Handle snippet selection changes"""
        try:
            logger.debug(f"Generating preview for {len(selected_snippets)} snippets")
            self.current_prompt_text = self._generate_preview(selected_snippets)
            logger.debug(f"Preview text: {self.current_prompt_text}")
            
            # Update copy button state
            has_content = self.current_prompt_text != "No Snippets Selected"
            self.copy_btn.configure(state='normal' if has_content else 'disabled')
            
            # Update prompt window if it's open
            if self.prompt_window:
                try:
                    if self.prompt_window.winfo_exists():
                        self.prompt_window.update_prompt(self.current_prompt_text)
                except tk.TclError:
                    # Window was destroyed but reference still exists
                    self.prompt_window = None
                    self.show_prompt_btn.configure(text="👁 Show Prompt")
                
        except Exception as e:
            logger.error(f"Error updating preview: {str(e)}")
            messagebox.showerror("Error", f"Failed to update preview: {str(e)}")

    def _on_snippet_edit(self, snippet: Dict) -> Union[bool, List[Dict]]:
        """Handle snippet edits, additions, and deletions"""
        try:
            if snippet.get('reload'):
                # Handle reload request
                return self.data_manager.load_snippets_for_gui()
                
            if snippet.get('delete'):
                # Handle deletion
                return self.data_manager.delete_snippets(snippet['ids'])
                
            # Handle add/update
            if snippet.get('id') in self._get_snippet_ids():
                return self.data_manager.update_snippet(snippet)
            else:
                return self.data_manager.add_snippet(snippet)
                
        except Exception as e:
            logger.error(f"Error in snippet edit handler: {str(e)}")
            return False

    def _get_snippet_ids(self) -> set:
        """Get set of existing snippet IDs"""
        try:
            snippets = self.data_manager.load_snippets_for_gui()
            return {s['id'] for s in snippets}
        except Exception:
            return set()

    def _on_snippets_delete(self, snippets: List[Dict]) -> None:
        """Handle snippet deletion"""
        try:
            # Extract snippet IDs from the snippet objects
            snippet_ids = [snippet['id'] for snippet in snippets]
            logger.debug(f"Deleting snippet IDs: {snippet_ids}")
            
            if self.data_manager.delete_snippets(snippet_ids):
                logger.info("Successfully deleted from storage, reloading...")
                remaining_snippets = self.data_manager.load_snippets_for_gui()
                self.snippet_list.load_snippets(remaining_snippets)
                logger.info(f"Reloaded {len(remaining_snippets)} remaining snippets")
            else:
                raise Exception("Failed to delete snippets from storage")
        except Exception as e:
            logger.error(f"Error in _on_snippets_delete: {str(e)}")
            messagebox.showerror("Error", f"Error deleting snippets: {str(e)}")

    def _on_clone_snippet(self, snippet_id: str) -> None:
        """Handle snippet cloning"""
        try:
            snippets = self.data_manager.load_snippets_for_gui()
            original = next((s for s in snippets if s['id'] == snippet_id), None)
            
            if original:
                cloned = {**original}
                cloned['id'] = str(uuid4())
                cloned['name'] = f"{original['name']} (Copy)"
                
                if self.data_manager.add_snippet(cloned):
                    self._load_snippets()
                else:
                    raise Exception("Failed to save cloned snippet")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error cloning snippet: {str(e)}")

    def _generate_preview(self, selected_snippets: List[Dict]) -> str:
        """Generate preview text from selected snippets"""
        if not selected_snippets:
            return "No Snippets Selected"
        
        # Collect all prompt texts
        prompts = []
        for snippet in selected_snippets:
            prompt_text = snippet.get('prompt_text', '').strip()
            if prompt_text:
                prompts.append(prompt_text)
        
        # Join with semicolons
        return "; ".join(prompts) if prompts else "No Snippets Selected"

    def _toggle_prompt_window(self) -> None:
        """Toggle the prompt preview window"""
        try:
            # Check if window exists and is still valid
            window_exists = False
            if self.prompt_window:
                try:
                    window_exists = self.prompt_window.winfo_exists()
                except tk.TclError:
                    # Window was destroyed but reference still exists
                    window_exists = False
                    self.prompt_window = None
            
            if window_exists:
                # Window exists, close it
                if self.prompt_window:  # Double check before calling destroy
                    self.prompt_window.destroy()
                self.prompt_window = None
                self.show_prompt_btn.configure(text="👁 Show Prompt")
            else:
                # Window doesn't exist, create it
                def on_close():
                    self.prompt_window = None
                    self.show_prompt_btn.configure(text="👁 Show Prompt")
                
                self.prompt_window = PromptWindow(self, on_close_callback=on_close)
                self.prompt_window.update_prompt(self.current_prompt_text)
                self.show_prompt_btn.configure(text="👁 Hide Prompt")
                
        except Exception as e:
            logger.error(f"Error toggling prompt window: {str(e)}")
            # Reset state in case of error
            self.prompt_window = None
            self.show_prompt_btn.configure(text="👁 Show Prompt")
            messagebox.showerror("Error", f"Failed to toggle prompt window: {str(e)}")

    def _copy_to_clipboard(self) -> None:
        """Copy current prompt text to clipboard"""
        try:
            if self.current_prompt_text and self.current_prompt_text != "No Snippets Selected":
                self.clipboard_clear()
                self.clipboard_append(self.current_prompt_text)
                
                logger.info(f"📋 Copied {len(self.current_prompt_text)} characters to clipboard")
                
                # Brief visual feedback
                original_text = self.copy_btn.cget('text')
                self.copy_btn.configure(text="✓ Copied!")
                self.after(1000, lambda: self.copy_btn.configure(text=original_text))
                
        except Exception as e:
            logger.error(f"Error copying to clipboard: {str(e)}")
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

    def _on_font_scale_changed(self, event=None) -> None:
        """Handle font scale changes"""
        try:
            # Get selected scale display name and convert to internal name
            display_name = self.font_scale_var.get()
            scale_map = {v: k for k, v in self.font_manager.get_available_scales().items()}
            scale_key = scale_map.get(display_name)
            
            if scale_key and self.font_manager.set_font_scale(scale_key):
                logger.info(f"Font scale changed to: {display_name} ({scale_key})")
                # Force refresh of UI components that use fonts
                self._refresh_ui_fonts()
            else:
                logger.warning(f"Failed to set font scale: {display_name}")
                
        except Exception as e:
            logger.error(f"Error changing font scale: {str(e)}")
            messagebox.showerror("Error", f"Failed to change font scale: {str(e)}")
    
    def _refresh_ui_fonts(self) -> None:
        """Refresh fonts for all UI components"""
        try:            # Skip button font updates - default button fonts work well across displays
            # and avoid type checker issues with font configuration
            
            # Update snippet list fonts
            if hasattr(self.snippet_list, 'refresh_fonts'):
                self.snippet_list.refresh_fonts()
              # Update prompt window fonts if open
            if self.prompt_window and hasattr(self.prompt_window, 'refresh_fonts'):
                try:
                    if self.prompt_window.winfo_exists():
                        self.prompt_window.refresh_fonts()
                except tk.TclError:
                    # Window was destroyed
                    self.prompt_window = None
            
            logger.debug("UI fonts refreshed successfully")
            
        except Exception as e:
            logger.error(f"Error refreshing UI fonts: {str(e)}")

    def run(self) -> None:
        """Start the application"""
        self.mainloop()
        
    def _on_closing(self) -> None:
        """Handle application closing"""
        logger.info("👋 Application closing...")
        self.destroy()