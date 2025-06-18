from typing import List, Dict, Set
from models.snippet_state import SnippetState, SnippetStateManager

def get_category_selections(state_manager: SnippetStateManager, snippets: List[Dict]) -> Dict[str, List[Dict]]:
    """Get selected snippets grouped by category"""
    selections = {}
    
    for snippet in snippets:
        if snippet['id'] in state_manager.selected_ids:
            category = snippet['category']
            if category not in selections:
                selections[category] = []
            selections[category].append(snippet)
            
    return selections