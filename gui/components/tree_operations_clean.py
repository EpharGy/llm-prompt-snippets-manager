import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Set, Optional, Callable
from utils.logger import get_logger

logger = get_logger(__name__)


class TreeOperations:
    """Component for handling treeview operations and interactions"""
    
    def __init__(self, tree_widget: ttk.Treeview, 
                 on_selection_changed: Optional[Callable] = None,
                 on_snippet_edit: Optional[Callable] = None):
        self.tree = tree_widget
        self.on_selection_changed = on_selection_changed
        self.on_snippet_edit = on_snippet_edit
        
        # Symbol constants
        self.SYMBOL_UNSELECTED = "➕"  # Plus sign
        self.SYMBOL_SELECTED = "✖"     # Bold X
        
        # Set up tree bindings
        self._setup_tree_bindings()
        
    def _setup_tree_bindings(self):
        """Set up tree event bindings"""
        self.tree.bind('<Button-1>', self._on_tree_click)
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        
    def _on_tree_click(self, event):
        """Handle single click on tree item"""
        region = self.tree.identify("region", event.x, event.y)
        item = self.tree.identify_row(event.y)
        
        if not item:
            return
            
        # Regular selection handling
        if region == "cell":
            self.tree.selection_set(item)
            self.tree.focus(item)
            
        # Notify parent of selection change
        if self.on_selection_changed:
            self.on_selection_changed()
            
    def _on_tree_double_click(self, event):
        """Handle double click on tree item"""
        item = self.tree.identify_row(event.y)
        
        if not item:
            return
            
        # Trigger edit callback if available
        if self.on_snippet_edit:
            snippet_data = self.tree.item(item)
            if snippet_data.get('tags'):
                snippet_id = snippet_data['tags'][0]
                self.on_snippet_edit(snippet_id)
                
        # Notify of selection change
        if self.on_selection_changed:
            self.on_selection_changed()
    
    def add_snippet_to_tree(self, snippet: Dict, is_selected: bool = False) -> str:
        """Add a snippet to the tree and return the item ID"""
        try:
            # Determine selection symbol based on snippet state
            selection_symbol = self.SYMBOL_SELECTED if is_selected else self.SYMBOL_UNSELECTED
                
            # Prepare values for tree columns
            values = [
                selection_symbol,  # Symbol column
                snippet['name'],
                snippet['category'],
                "Yes" if snippet.get('exclusive', False) else "No",
                ', '.join(snippet['labels']),
                snippet.get('description', '')[:100] + ('...' if len(snippet.get('description', '')) > 100 else '')
            ]
            
            # Insert into tree
            item_id = self.tree.insert('', 'end', values=values, tags=(snippet['id'],))
            
            logger.debug(f"Added snippet to tree: {snippet['name']} (ID: {snippet['id']})")
            return item_id
            
        except Exception as e:
            logger.error(f"Failed to add snippet to tree: {str(e)}")
            return ""
            
    def populate_tree(self, snippets: Dict, selected_ids: Optional[Set[str]] = None):
        """Populate tree with all snippets"""
        try:
            if selected_ids is None:
                selected_ids = set()
                
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Add all snippets
            for snippet in snippets.values():
                is_selected = snippet['id'] in selected_ids
                self.add_snippet_to_tree(snippet, is_selected)
                
            logger.debug(f"Populated tree with {len(snippets)} snippets")
            
        except Exception as e:
            logger.error(f"Failed to populate tree: {str(e)}")
            
    def refresh_tree_view(self, snippets: Dict, preserve_selections: bool = True, selected_ids: Optional[Set[str]] = None):
        """Refresh the tree view with current snippets"""
        if selected_ids is None:
            selected_ids = set()
            
        # Store current selections if preserving
        selected_items = set()
        if preserve_selections:
            for item in self.tree.selection():
                snippet_data = self.tree.item(item)
                if snippet_data.get('tags'):
                    selected_items.add(snippet_data['tags'][0])
                    
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add snippets to tree
        for snippet in snippets.values():
            # Check if snippet is selected (either from state manager or visual selection)
            is_selected = snippet['id'] in selected_ids
            item_id = self.add_snippet_to_tree(snippet, is_selected)
            
            # Restore selection if needed
            if preserve_selections and snippet['id'] in selected_items:
                self.tree.selection_add(item_id)
                
        # Notify of selection change
        if self.on_selection_changed:
            self.on_selection_changed()
            
    def get_selected_snippets(self) -> List[str]:
        """Get currently selected snippet IDs"""
        selected_ids = []
        for item in self.tree.selection():
            snippet_data = self.tree.item(item)
            if snippet_data.get('tags'):
                selected_ids.append(snippet_data['tags'][0])
        return selected_ids
