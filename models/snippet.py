from dataclasses import dataclass
from typing import List, Dict
import uuid
from .metadata_manager import metadata_manager

@dataclass
class Snippet:
    id: str
    name: str
    category_id: str  # UUID reference to category
    prompt_text: str
    label_ids: List[str]  # List of UUID references to labels
    exclusive: bool

    @classmethod
    def create(cls, name: str, category: str, prompt_text: str, labels: List[str], exclusive: bool):
        """Create a new snippet with automatic metadata management."""
        # Use metadata manager to ensure category and labels exist
        category_id, label_ids = metadata_manager.update_snippet_counts_for_snippet(
            category, labels, increment=True
        )
        
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            category_id=category_id,
            prompt_text=prompt_text,
            label_ids=label_ids,
            exclusive=exclusive
        )
    
    @classmethod 
    def from_dict(cls, data: Dict):
        """Create snippet from dictionary (new format only)."""
        return cls(
            id=data['id'],
            name=data['name'],
            category_id=data['category_id'],
            prompt_text=data['prompt_text'],
            label_ids=data.get('label_ids', []),
            exclusive=data.get('exclusive', False)
        )
    
    def get_category_name(self) -> str:
        """Get the category name from metadata."""
        categories = metadata_manager.get_all_categories()
        if self.category_id in categories:
            return categories[self.category_id]['name']
        return "Unknown Category"
    
    def get_label_names(self) -> List[str]:
        """Get the label names from metadata."""
        labels = metadata_manager.get_all_labels()
        label_names = []
        for label_id in self.label_ids:
            if label_id in labels:
                label_names.append(labels[label_id]['name'])
        return label_names

    def to_dict(self):
        """Convert snippet to dictionary for JSON storage."""
        return {
            "id": self.id,
            "name": self.name,
            "category_id": self.category_id,
            "prompt_text": self.prompt_text,
            "label_ids": self.label_ids,
            "exclusive": self.exclusive
        }

    def matches_search(self, search_terms: List[str]) -> bool:
        """Check if snippet matches all search terms"""
        searchable_text = (
            f"{self.name} {' '.join(self.get_label_names())} {self.get_category_name()} {self.prompt_text}"
        ).lower()
        return all(term in searchable_text for term in search_terms)
        
    def update_category_and_labels(self, new_category: str, new_labels: List[str]):
        """Update the category and labels, managing metadata counts."""
        # Decrement old counts
        metadata_manager.update_snippet_counts_for_snippet(
            self.get_category_name(), self.get_label_names(), increment=False
        )
        
        # Update to new category and labels
        self.category_id, self.label_ids = metadata_manager.update_snippet_counts_for_snippet(
            new_category, new_labels, increment=True
        )
        
    def delete(self):
        """Handle cleanup when snippet is deleted."""
        # Decrement usage counts
        metadata_manager.update_snippet_counts_for_snippet(
            self.get_category_name(), self.get_label_names(), increment=False
        )