import tkinter as tk
from tkinter import ttk

def create_tooltip(widget, text):
    """Create a tooltip for a given widget"""
    
    def show_tooltip(event=None):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
        
        label = ttk.Label(
            tooltip, 
            text=text, 
            justify='left',
            background="#ffffe0", 
            relief='solid', 
            borderwidth=1
        )
        label.pack()
        
        def hide_tooltip():
            tooltip.destroy()
            
        tooltip.bind('<Leave>', lambda e: hide_tooltip())
        widget.bind('<Leave>', lambda e: hide_tooltip())
        
    widget.bind('<Enter>', show_tooltip)

def configure_tree_style():
    """Configure ttk style for treeview"""
    style = ttk.Style()
    style.configure(
        "Treeview",
        background="#ffffff",
        foreground="#000000",
        rowheight=25,
        fieldbackground="#ffffff"
    )
    style.configure(
        "Treeview.Heading",
        background="#f0f0f0",
        font=('TkDefaultFont', 9, 'bold')
    )
    return style