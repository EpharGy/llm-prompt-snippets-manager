from typing import List, Dict, Set
from models.snippet_state import SnippetState, SnippetStateManager

def filter_snippets_by_search(snippets: List[Dict], search_terms: List[str]) -> Set[str]:
    """Filter snippets based on search terms and return matching IDs"""
    matching_ids = set()
    
    for snippet in snippets:
        searchable_text = (
            f"{snippet['name']} {' '.join(snippet['labels'])} "
            f"{snippet['category']} {snippet['prompt_text']}"
        ).lower()
        
        if all(term.lower() in searchable_text for term in search_terms):
            matching_ids.add(snippet['id'])
            
    return matching_ids

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