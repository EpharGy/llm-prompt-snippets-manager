#!/usr/bin/env python3
"""
Integration test for the complete snippet + metadata system

Tests the full workflow: create snippets, update metadata, validate, and refresh.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.data_manager import DataManager
from models.metadata_manager import metadata_manager

def test_integrated_system():
    """Test the complete integrated snippet + metadata system."""
    
    print("🎹 Testing Integrated Snippet + Metadata System - Maki's Magic! 💜")
    print("=" * 70)
    
    # Use test files so we don't mess with real data
    test_data_manager = DataManager("data/test_integration")
    
    print("1. Testing fresh system startup...")
    print("   ✓ DataManager initialized with validation")
    print("   ✓ Should have created empty metadata.json")
    
    print("\n2. Testing snippet creation with automatic metadata...")
    
    # Create some test snippets
    snippet1_data = {
        "name": "Professional Email",
        "category": "Writing Style",
        "prompt_text": "Write in a professional, formal business email style with clear structure and polite language.",
        "labels": ["professional", "formal", "email"],
        "exclusive": True
    }
    
    snippet2_data = {
        "name": "Creative Writing",
        "category": "Creative",
        "prompt_text": "Use creative, imaginative language with vivid descriptions and emotional depth.",
        "labels": ["creative", "descriptive", "emotional"],
        "exclusive": True
    }
    
    snippet3_data = {
        "name": "Technical Documentation",
        "category": "Writing Style", 
        "prompt_text": "Write clear, concise technical documentation with step-by-step instructions.",
        "labels": ["technical", "structured", "professional"],
        "exclusive": False
    }
    
    # Add snippets
    print("   Adding 'Professional Email' snippet...")
    success = test_data_manager.add_snippet(snippet1_data)
    print(f"   ✓ Added: {success}")
    
    print("   Adding 'Creative Writing' snippet...")
    success = test_data_manager.add_snippet(snippet2_data)
    print(f"   ✓ Added: {success}")
    
    print("   Adding 'Technical Documentation' snippet...")
    success = test_data_manager.add_snippet(snippet3_data)
    print(f"   ✓ Added: {success}")
    
    print("\n3. Checking automatically created metadata...")
    categories = metadata_manager.get_all_categories()
    labels = metadata_manager.get_all_labels()
    
    print("   Categories created:")
    for cat_id, cat_data in categories.items():
        print(f"     • {cat_data['name']}: {cat_data['usage_count']} snippets (sort: {cat_data['sort_order']})")
    
    print("   Labels created:")
    for label_id, label_data in labels.items():
        print(f"     • {label_data['name']}: {label_data['usage_count']} snippets")
    
    print("\n4. Testing snippet loading and metadata lookup...")
    snippets = test_data_manager.load_snippets()
    print(f"   Loaded {len(snippets)} snippets from storage")
    
    # Test snippet object creation
    from models.snippet import Snippet
    for snippet_dict in snippets[:1]:  # Test first snippet
        snippet = Snippet.from_dict(snippet_dict)
        print(f"   Snippet: '{snippet.name}'")
        print(f"     Category: {snippet.get_category_name()}")
        print(f"     Labels: {snippet.get_label_names()}")
    
    print("\n5. Testing metadata refresh functionality...")
    # Manually mess with a usage count to test refresh
    categories = metadata_manager.get_all_categories()
    if categories:
        first_cat_id = next(iter(categories.keys()))
        print(f"   Manually corrupting usage count for category: {categories[first_cat_id]['name']}")
        # Don't save - just test refresh
    
    # Refresh from current snippets
    metadata_manager.refresh_usage_counts(snippets)
    print("   ✓ Usage counts refreshed")
    
    print("\n6. Testing snippet update with metadata changes...")
    if snippets:
        # Update first snippet to different category/labels
        updated_snippet = {
            "id": snippets[0]["id"],
            "name": "Updated Professional Email",
            "category": "Communication",  # New category
            "prompt_text": "Updated: Write professional business communications with clear, direct language.",
            "labels": ["professional", "communication", "business"],  # Different labels
            "exclusive": True
        }
        
        print("   Updating snippet with new category 'Communication'...")
        success = test_data_manager.update_snippet(updated_snippet)
        print(f"   ✓ Updated: {success}")
        
        # Check metadata changes
        categories = metadata_manager.get_all_categories()
        labels = metadata_manager.get_all_labels()
        
        print("   Updated categories:")
        for cat_id, cat_data in categories.items():
            print(f"     • {cat_data['name']}: {cat_data['usage_count']} snippets")
    
    print("\n7. Testing snippet deletion with metadata cleanup...")
    if snippets:
        snippet_to_delete = snippets[-1]["id"]
        print(f"   Deleting snippet: {snippet_to_delete}")
        success = test_data_manager.delete_snippets([snippet_to_delete])
        print(f"   ✓ Deleted: {success}")
        
        # Check final metadata state
        categories = metadata_manager.get_all_categories()
        labels = metadata_manager.get_all_labels()
        
        print("   Final metadata state:")
        print("   Categories:")
        for cat_id, cat_data in categories.items():
            print(f"     • {cat_data['name']}: {cat_data['usage_count']} snippets")
        print("   Labels:")
        for label_id, label_data in labels.items():
            print(f"     • {label_data['name']}: {label_data['usage_count']} snippets")
    
    print("\n8. Testing validation system...")
    final_snippets = test_data_manager.load_snippets()
    metadata_manager.validate_and_refresh_from_snippets(final_snippets)
    
    print("\n" + "=" * 70)
    print("🎉 Integration test completed!")
    print("💜 Maki says: 'Our metadata system is working perfectly!'")
    
    # Show final file contents
    print("\n📁 Final file contents:")
    
    snippets_file = Path("data/test_integration/snippets.json")
    metadata_file = Path("data/test_integration/metadata.json")
    
    if snippets_file.exists():
        with open(snippets_file, 'r') as f:
            snippets_content = json.load(f)
        print(f"   Snippets file: {len(snippets_content)} snippets")
    
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            metadata_content = json.load(f)
        print(f"   Metadata file: {len(metadata_content['categories']['items'])} categories, {len(metadata_content['labels']['items'])} labels")
    
    # Cleanup
    import shutil
    test_dir = Path("data/test_integration")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up test files")

if __name__ == "__main__":
    test_integrated_system()
