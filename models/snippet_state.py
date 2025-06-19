from enum import Enum
from dataclasses import dataclass
from typing import Dict, Set, Optional, List
from models.snippet import Snippet
from utils.logger import get_logger

logger = get_logger(__name__)

class SnippetState(Enum):
    UNSELECTED = "unselected"
    SELECTED = "selected"

@dataclass
class SnippetStateManager:
    # Core state tracking
    state_map: Dict[str, SnippetState]
    selected_ids: Set[str]
    category_selections: Dict[str, str]
    
    # Search/filter state
    is_filtered: bool
    search_text: str
    filtered_ids: Set[str]
    
    @classmethod
    def create(cls):
        return cls(
            state_map={},
            selected_ids=set(),
            category_selections={},
            is_filtered=False,
            search_text="",
            filtered_ids=set()
        )
    
    def get_state(self, snippet_id: str) -> SnippetState:
        return self.state_map.get(snippet_id, SnippetState.UNSELECTED)
    
    def set_state(self, snippet_id: str, state: Optional[SnippetState], 
                 category: Optional[str] = None, exclusive: bool = False) -> None:
        """Set state with proper None handling"""
        if state is None:
            self.state_map.pop(snippet_id, None)
            self.selected_ids.discard(snippet_id)
            return
        
        old_state = self.get_state(snippet_id)
        self.state_map[snippet_id] = state
          # Handle selection state
        if state == SnippetState.SELECTED:
            self.selected_ids.add(snippet_id)
            if exclusive and category:
                self.category_selections[category] = snippet_id
        else:
            self.selected_ids.discard(snippet_id)
            if category and self.category_selections.get(category) == snippet_id:
                self.category_selections.pop(category)

    def can_select_snippet(self, snippet_id: str, category: str, exclusive: bool) -> bool:
        if exclusive:
            current_selection = self.category_selections.get(category)
            return current_selection is None or current_selection == snippet_id
        return True
    
    def clear_all_selections(self):
        self.selected_ids.clear()
        self.category_selections.clear()
        for snippet_id in list(self.state_map.keys()):
            if self.state_map[snippet_id] == SnippetState.SELECTED:
                self.set_state(snippet_id, SnippetState.UNSELECTED)

    def set_search_filter(self, search_text: str, filtered_ids: Set[str]) -> None:
        """Set search filter state"""
        self.search_text = search_text
        self.filtered_ids = filtered_ids
        self.is_filtered = bool(search_text)  # Only filtered if there's search text
        logger.debug(f"🔍 Filter state - text: '{search_text}', filtered: {len(filtered_ids)} items")
        
    def clear_search_filter(self) -> None:
        """Clear search filter state without affecting selections"""
        self.search_text = ""
        self.filtered_ids = set()
        self.is_filtered = False

    def clear_selections(self, snippet_ids: List[str]) -> None:
        """Clear selections for specific snippet IDs"""
        for snippet_id in snippet_ids:
            self.state_map.pop(snippet_id, None)
            self.selected_ids.discard(snippet_id)
            # Clean up category selections if needed
            for category, selected_id in list(self.category_selections.items()):
                if selected_id == snippet_id:
                    self.category_selections.pop(category)

    def get_all_snippets(self) -> Dict[str, Dict]:
        """Get all tracked snippets"""
        return {
            snippet_id: {
                'id': snippet_id,
                'state': state
            }
            for snippet_id, state in self.state_map.items()
        }