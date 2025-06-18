"""
Metadata Manager for Categories and Labels

Handles creation, validation, and management of categories and labels
for the LLM Prompt Snippets Manager application.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from utils.logger import get_logger

# Initialize logger for this module
logger = get_logger("MetadataManager")


class MetadataManager:
    """Manages categories and labels metadata for snippets."""
    
    def __init__(self, metadata_file_path: str = "data/metadata.json"):
        """Initialize the metadata manager.
        
        Args:
            metadata_file_path: Path to the metadata JSON file
        """
        self.metadata_file_path = Path(metadata_file_path)
        self._metadata_cache = None
        
    def _ensure_metadata_file_exists(self) -> None:
        """Create empty metadata file if it doesn't exist."""
        if not self.metadata_file_path.exists():
            # Create directory if needed
            self.metadata_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty metadata structure
            empty_metadata = {
                "categories": {
                    "items": {}
                },
                "labels": {
                    "items": {}
                }
            }
            
            with open(self.metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(empty_metadata, f, indent=2)
                
            self._metadata_cache = empty_metadata
    
    def _load_metadata(self) -> Dict:
        """Load metadata from file, creating if necessary."""
        if self._metadata_cache is None:
            self._ensure_metadata_file_exists()
            
            with open(self.metadata_file_path, 'r', encoding='utf-8') as f:
                self._metadata_cache = json.load(f)
        
        return self._metadata_cache
    
    def _save_metadata(self, metadata: Dict) -> None:
        """Save metadata to file and update cache."""
        with open(self.metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        self._metadata_cache = metadata
    
    def _generate_uuid(self) -> str:
        """Generate a new UUID string."""
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat() + 'Z'
    
    def ensure_category_exists(self, category_name: str, sort_order: int = 5, 
                              color: Optional[str] = None) -> str:
        """Ensure a category exists, creating it if necessary.
        
        Args:
            category_name: Name of the category
            sort_order: Sort order for the category (default: 5)
            color: Hex color code (optional)
            
        Returns:
            UUID of the category (existing or newly created)
        """
        metadata = self._load_metadata()
        
        # Check if category already exists by name
        for cat_id, cat_data in metadata["categories"]["items"].items():
            if cat_data["name"] == category_name:
                return cat_id
        
        # Create new category
        new_id = self._generate_uuid()
        new_category = {
            "name": category_name,
            "id": new_id,
            "sort_order": sort_order,
            "color": color,
            "dt_created": self._get_current_timestamp(),
            "usage_count": 0
        }
        
        metadata["categories"]["items"][new_id] = new_category
        self._save_metadata(metadata)
        
        return new_id
    
    def ensure_label_exists(self, label_name: str) -> str:
        """Ensure a label exists, creating it if necessary.
        
        Args:
            label_name: Name of the label
            
        Returns:
            UUID of the label (existing or newly created)
        """
        metadata = self._load_metadata()
        
        # Check if label already exists by name
        for label_id, label_data in metadata["labels"]["items"].items():
            if label_data["name"] == label_name:
                return label_id
        
        # Create new label
        new_id = self._generate_uuid()
        new_label = {
            "name": label_name,
            "id": new_id,
            "dt_created": self._get_current_timestamp(),
            "usage_count": 0
        }
        
        metadata["labels"]["items"][new_id] = new_label
        self._save_metadata(metadata)
        
        return new_id
    
    def ensure_labels_exist(self, label_names: List[str]) -> List[str]:
        """Ensure multiple labels exist, creating them if necessary.
        
        Args:
            label_names: List of label names
            
        Returns:
            List of UUIDs for the labels
        """
        return [self.ensure_label_exists(name) for name in label_names]
    
    def increment_snippet_count(self, item_type: str, item_id: str) -> None:
        """Increment snippet count for a category or label.
        
        Args:
            item_type: Either 'categories' or 'labels'
            item_id: UUID of the item
        """
        metadata = self._load_metadata()
        
        if item_id in metadata[item_type]["items"]:
            metadata[item_type]["items"][item_id]["usage_count"] += 1
            self._save_metadata(metadata)
    
    def decrement_snippet_count(self, item_type: str, item_id: str) -> None:
        """Decrement snippet count for a category or label.
        
        Args:
            item_type: Either 'categories' or 'labels'
            item_id: UUID of the item
        """
        metadata = self._load_metadata()
        
        if item_id in metadata[item_type]["items"]:
            current_count = metadata[item_type]["items"][item_id]["usage_count"]
            metadata[item_type]["items"][item_id]["usage_count"] = max(0, current_count - 1)
            self._save_metadata(metadata)
    
    def update_snippet_counts_for_snippet(self, category_name: str, label_names: List[str], 
                                         increment: bool = True) -> Tuple[str, List[str]]:
        """Update snippet counts and ensure category/labels exist for a snippet.
        
        Args:
            category_name: Name of the category
            label_names: List of label names
            increment: True to increment counts, False to decrement
            
        Returns:
            Tuple of (category_id, list_of_label_ids)
        """
        # Ensure items exist
        category_id = self.ensure_category_exists(category_name)
        label_ids = self.ensure_labels_exist(label_names)
        
        # Update snippet counts
        if increment:
            self.increment_snippet_count("categories", category_id)
            for label_id in label_ids:
                self.increment_snippet_count("labels", label_id)
        else:
            self.decrement_snippet_count("categories", category_id)
            for label_id in label_ids:
                self.decrement_snippet_count("labels", label_id)
        
        return category_id, label_ids
    
    def get_all_categories(self) -> Dict[str, Dict]:
        """Get all categories.
        
        Returns:
            Dictionary of category_id -> category_data
        """
        metadata = self._load_metadata()
        return metadata["categories"]["items"]
    
    def get_all_labels(self) -> Dict[str, Dict]:
        """Get all labels.
        
        Returns:
            Dictionary of label_id -> label_data
        """
        metadata = self._load_metadata()
        return metadata["labels"]["items"]
    
    def get_category_by_name(self, category_name: str) -> Optional[Dict]:
        """Get category data by name.
        
        Args:
            category_name: Name of the category
            
        Returns:
            Category data dictionary or None if not found
        """
        categories = self.get_all_categories()
        for cat_data in categories.values():
            if cat_data["name"] == category_name:
                return cat_data
        return None
    
    def get_labels_by_names(self, label_names: List[str]) -> List[Optional[Dict]]:
        """Get label data by names.
        
        Args:
            label_names: List of label names
            
        Returns:
            List of label data dictionaries (None for not found)
        """
        labels = self.get_all_labels()
        result = []
        
        for name in label_names:
            found = None
            for label_data in labels.values():
                if label_data["name"] == name:
                    found = label_data
                    break
            result.append(found)
        
        return result
    
    def clear_cache(self) -> None:
        """Clear the metadata cache to force reload from file."""
        self._metadata_cache = None
    
    def refresh_usage_counts(self, snippets_data: List[Dict]) -> None:
        """Refresh usage counts based on current snippet data.
        
        Args:
            snippets_data: List of snippet dictionaries (new format with category_id/label_ids)
        """
        logger.debug("Starting usage count refresh")
        
        metadata = self._load_metadata()
        
        # Reset all usage counts to 0
        for category in metadata["categories"]["items"].values():
            category["usage_count"] = 0
        for label in metadata["labels"]["items"].values():
            label["usage_count"] = 0
        
        # Count actual usage from snippets
        for snippet in snippets_data:
            # Count category usage
            category_id = snippet.get('category_id')
            if category_id and category_id in metadata["categories"]["items"]:
                metadata["categories"]["items"][category_id]["usage_count"] += 1
            
            # Count label usage
            label_ids = snippet.get('label_ids', [])
            for label_id in label_ids:
                if label_id in metadata["labels"]["items"]:
                    metadata["labels"]["items"][label_id]["usage_count"] += 1
        
        # Save updated metadata
        self._save_metadata(metadata)
        
        # Report results
        total_categories = len(metadata["categories"]["items"])
        total_labels = len(metadata["labels"]["items"])
        used_categories = len([c for c in metadata["categories"]["items"].values() if c["usage_count"] > 0])
        used_labels = len([l for l in metadata["labels"]["items"].values() if l["usage_count"] > 0])
        
        logger.info(f"Usage counts refreshed: {used_categories}/{total_categories} categories, {used_labels}/{total_labels} labels in use")
    
    def validate_metadata_references(self, snippets_data: List[Dict]) -> None:
        """Validate that all category_id and label_ids in snippets have corresponding metadata entries.
        
        Creates 'Unknown' entries for orphaned references.
        
        Args:
            snippets_data: List of snippet dictionaries (new format)
        """
        print("🔍 Validating metadata references...")
        
        metadata = self._load_metadata()
        orphaned_categories = set()
        orphaned_labels = set()
        
        # Check all snippet references
        for snippet in snippets_data:
            # Check category reference
            category_id = snippet.get('category_id')
            if category_id and category_id not in metadata["categories"]["items"]:
                orphaned_categories.add(category_id)
            
            # Check label references
            label_ids = snippet.get('label_ids', [])
            for label_id in label_ids:
                if label_id not in metadata["labels"]["items"]:
                    orphaned_labels.add(label_id)
        
        # Create entries for orphaned references
        for category_id in orphaned_categories:
            print(f"⚠️  Creating metadata for orphaned category ID: {category_id}")
            new_category = {
                "name": "Unknown Category",
                "id": category_id,
                "sort_order": 5,
                "color": None,
                "dt_created": self._get_current_timestamp(),
                "usage_count": 0
            }
            metadata["categories"]["items"][category_id] = new_category
        
        for label_id in orphaned_labels:
            print(f"⚠️  Creating metadata for orphaned label ID: {label_id}")
            new_label = {
                "name": "Unknown Label",
                "id": label_id,
                "dt_created": self._get_current_timestamp(),
                "usage_count": 0
            }
            metadata["labels"]["items"][label_id] = new_label
        
        # Save if we made changes
        if orphaned_categories or orphaned_labels:
            self._save_metadata(metadata)
            print(f"✅ Created {len(orphaned_categories)} categories and {len(orphaned_labels)} labels for orphaned references")
        else:
            print("✅ All references are valid")

    def validate_and_refresh_from_snippets(self, snippets_data: List[Dict]) -> None:
        """Complete validation and refresh of metadata from snippets.
        
        This method should be called on app startup to ensure data integrity.
        
        Args:
            snippets_data: List of snippet dictionaries (new format)
        """
        logger.debug("Starting complete metadata validation and refresh")
        
        # Ensure metadata file exists
        self._ensure_metadata_file_exists()
        
        # First validate references (creates missing entries)
        self.validate_metadata_references(snippets_data)
        
        # Then refresh usage counts
        self.refresh_usage_counts(snippets_data)
        
        logger.info("Metadata validation and refresh completed successfully")
    
    def cleanup_unused_metadata(self, keep_unused: bool = True) -> Dict:
        """Remove categories and labels that aren't used by any snippets.
        
        Args:
            keep_unused: If True, keep unused items but mark them. If False, delete them.
            
        Returns:
            Dictionary with cleanup statistics
        """
        metadata = self._load_metadata()
        
        categories_removed = 0
        labels_removed = 0
        
        if not keep_unused:
            # Remove categories with 0 usage
            categories_to_remove = [
                cat_id for cat_id, cat_data in metadata["categories"]["items"].items()
                if cat_data["usage_count"] == 0
            ]
            
            for cat_id in categories_to_remove:
                del metadata["categories"]["items"][cat_id]
                categories_removed += 1
            
            # Remove labels with 0 usage
            labels_to_remove = [
                label_id for label_id, label_data in metadata["labels"]["items"].items()
                if label_data["usage_count"] == 0
            ]
            
            for label_id in labels_to_remove:
                del metadata["labels"]["items"][label_id]
                labels_removed += 1
            
            # Save if we made changes
            if categories_removed > 0 or labels_removed > 0:
                self._save_metadata(metadata)
        
        return {
            "categories_removed": categories_removed,
            "labels_removed": labels_removed,
            "categories_unused": len([
                cat for cat in metadata["categories"]["items"].values()
                if cat["usage_count"] == 0
            ]),
            "labels_unused": len([
                label for label in metadata["labels"]["items"].values()
                if label["usage_count"] == 0
            ])
        }


# Convenience instance for easy importing
metadata_manager = MetadataManager()
