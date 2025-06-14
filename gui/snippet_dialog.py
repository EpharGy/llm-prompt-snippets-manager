import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
from uuid import uuid4

class SnippetDialog(tk.Toplevel):
    def __init__(self, parent, snippet: Optional[Dict] = None, is_edit: bool = False):
        super().__init__(parent)
        self.snippet = snippet
        self.result = None
        self.save_as_new = False
        self.is_edit = is_edit
        self.save_new_btn = None  # Initialize button reference
        
        # Store original values for comparison
        self.original_values = {
            'name': snippet.get('name', '') if snippet else '',
            'category': snippet.get('category', '') if snippet else '',
            'labels': ', '.join(snippet.get('labels', [])) if snippet else '',
            'prompt_text': snippet.get('prompt_text', '') if snippet else '',
            'exclusive': snippet.get('exclusive', False) if snippet else False
        } if is_edit else {}
        
        # Initialize variables before creating UI
        self.name_var = tk.StringVar(value=self.original_values.get('name', ''))
        self.category_var = tk.StringVar(value=self.original_values.get('category', ''))
        self.labels_var = tk.StringVar(value=self.original_values.get('labels', ''))
        self.prompt_var = tk.StringVar(value=self.original_values.get('prompt_text', ''))
        self.exclusive_var = tk.BooleanVar(value=self.original_values.get('exclusive', False))
        
        # Configure window
        self.title("Edit Snippet" if is_edit else "New Snippet")
        self.geometry("300x250")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, False)
        
        # Bind variables to change detection
        if is_edit:
            self.name_var.trace_add('write', self._on_field_change)
            self.category_var.trace_add('write', self._on_field_change)
            self.labels_var.trace_add('write', self._on_field_change)
            self.prompt_var.trace_add('write', self._on_field_change)
            self.exclusive_var.trace_add('write', self._on_field_change)
        
        self._create_ui()
        self._position_window()

    def _on_field_change(self, *args):
        """Handle field changes"""
        if not self.is_edit or not self.save_new_btn:
            return
            
        current_values = {
            'name': self.name_var.get().strip(),
            'category': self.category_var.get().strip(),
            'labels': self.labels_var.get().strip(),
            'prompt_text': self.prompt_var.get().strip(),
            'exclusive': self.exclusive_var.get()
        }
        
        has_changes = any(
            current_values[key] != self.original_values[key]
            for key in self.original_values
        )
        
        self.save_new_btn.configure(
            state='normal' if has_changes else 'disabled'
        )

    def _position_window(self):
        """Center dialog on parent window"""
        self.update_idletasks()
        parent = self.master
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.geometry(f"+{x}+{y}")
        self.focus_force()  # Ensure dialog gets focus

    def _create_ui(self):
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill='both', expand=True)
        
        # Create form fields using the already initialized variables
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, sticky='ew', pady=5)
        
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=self.category_var).grid(row=1, column=1, sticky='ew', pady=5)
        
        ttk.Label(form_frame, text="Labels:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(form_frame, textvariable=self.labels_var).grid(row=2, column=1, sticky='ew', pady=5)
        
        ttk.Checkbutton(form_frame, text="Exclusive", variable=self.exclusive_var).grid(
            row=3, column=1, sticky='w', pady=(5, 2)
        )
        
        ttk.Label(form_frame, text="Prompt:").grid(row=4, column=0, sticky='w', pady=(2, 5))
        ttk.Entry(form_frame, textvariable=self.prompt_var).grid(row=4, column=1, sticky='ew', pady=(2, 5))
        
        # Button frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(2, 5))
        
        if self.is_edit:
            # Left-side buttons (Update and Save as New)
            left_buttons = ttk.Frame(button_frame)
            left_buttons.pack(side='left', fill='x', expand=True)
            
            ttk.Button(
                left_buttons, 
                text="Update Snippet", 
                command=self._on_update
            ).pack(side='left', padx=5)
            
            self.save_new_btn = ttk.Button(
                left_buttons, 
                text="Save as New", 
                command=self._on_save_as_new,
                state='disabled'
            )
            self.save_new_btn.pack(side='left', padx=5)
            
            # Right-side buttons (Delete and Cancel)
            right_buttons = ttk.Frame(button_frame)
            right_buttons.pack(side='right')
            
            ttk.Button(
                right_buttons,
                text="Delete",
                command=self._on_delete,
                style='Danger.TButton'  # Custom style for delete button
            ).pack(side='left', padx=5)
            
            ttk.Button(
                right_buttons,
                text="Cancel",
                command=self.destroy
            ).pack(side='left', padx=5)
        else:
            ttk.Button(
                button_frame,
                text="Save",
                command=self._on_save
            ).pack(side='left', padx=5)
            
            ttk.Button(
                button_frame,
                text="Cancel",
                command=self.destroy
            ).pack(side='left', padx=5)

        form_frame.columnconfigure(1, weight=1)

    def _on_close(self):
        """Handle window close button"""
        self.grab_release()  # Release modal state
        self.destroy()       # Close dialog
        
    def _on_update(self):
        """Update existing snippet"""
        self._prepare_result()
        self.save_as_new = False
        self.destroy()

    def _on_save_as_new(self):
        """Save as new snippet"""
        self._prepare_result()
        self.save_as_new = True
        self.destroy()

    def _on_save(self):
        """Save new snippet"""
        self._prepare_result()
        self.save_as_new = False
        self.destroy()

    def _prepare_result(self) -> bool:
        """Prepare snippet data with validation"""
        if not self._validate_fields():
            return False
            
        # Get and trim all text values
        name = self.name_var.get().strip()
        category = self.category_var.get().strip()
        labels = [l.strip() for l in self.labels_var.get().split(',') if l.strip()]
        prompt_text = self.prompt_var.get().strip()
        
        # Check for semicolons in prompt
        if ';' in prompt_text:
            messagebox.showerror(
                "Invalid Input", 
                "Prompt text cannot contain semicolons (;) as this is used as a delimiter."
            )
            return False
        
        self.result = {
            'id': self.snippet.get('id') if self.snippet else None,
            'name': name,
            'category': category,
            'labels': labels,
            'prompt_text': prompt_text,
            'exclusive': self.exclusive_var.get()
        }
        return True

    def _validate_fields(self) -> bool:
        """Validate form fields"""
        required_fields = {
            'Name': self.name_var.get().strip(),
            'Category': self.category_var.get().strip(),
            'Prompt': self.prompt_var.get().strip()
        }
        
        # Check for empty required fields
        missing = [k for k, v in required_fields.items() if not v]
        if missing:
            messagebox.showerror(
                "Error", 
                f"Please fill in required fields: {', '.join(missing)}"
            )
            return False
        
        # Additional validation for prompt text
        if ';' in required_fields['Prompt']:
            messagebox.showerror(
                "Invalid Input", 
                "Prompt text cannot contain semicolons (;)"
            )
            return False
            
        return True

    def _on_delete(self):
        """Handle snippet deletion"""
        if not self.snippet or not self.snippet.get('id'):
            return
            
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{self.snippet['name']}'?"
        ):
            self.result = {'delete': True, 'id': self.snippet['id']}
            self.destroy()