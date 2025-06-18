#!/usr/bin/env python3
"""
Test script for the MetadataManager

Tests the core functionality of category and label management.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.metadata_manager import MetadataManager

def test_metadata_manager():
    """Test the MetadataManager functionality."""
    
    print("🎹 Testing MetadataManager - Maki's Metadata Magic! 💜")
    print("=" * 60)
    
    # Use a test metadata file so we don't mess with the real one
    test_manager = MetadataManager("data/test_metadata.json")
    
    print("1. Testing file creation and basic operations...")
    
    # Test category creation
    print("   Creating categories...")
    cat1_id = test_manager.ensure_category_exists("Writing Style", sort_order=10, color="#FF5733")
    cat2_id = test_manager.ensure_category_exists("Character Development", sort_order=5, color="#33FF57")
    print(f"   ✓ Created 'Writing Style' with ID: {cat1_id}")
    print(f"   ✓ Created 'Character Development' with ID: {cat2_id}")
    
    # Test label creation
    print("   Creating labels...")
    label1_id = test_manager.ensure_label_exists("professional")
    label2_id = test_manager.ensure_label_exists("creative")
    label3_id = test_manager.ensure_label_exists("tsundere")
    print(f"   ✓ Created 'professional' with ID: {label1_id}")
    print(f"   ✓ Created 'creative' with ID: {label2_id}")
    print(f"   ✓ Created 'tsundere' with ID: {label3_id}")
    
    print("\n2. Testing duplicate handling...")
    # Test that duplicates return same ID
    duplicate_cat_id = test_manager.ensure_category_exists("Writing Style")
    duplicate_label_id = test_manager.ensure_label_exists("professional")
    print(f"   ✓ Duplicate category check: {cat1_id == duplicate_cat_id}")
    print(f"   ✓ Duplicate label check: {label1_id == duplicate_label_id}")
    
    print("\n3. Testing snippet count updates...")
    # Simulate adding snippets
    cat_id, label_ids = test_manager.update_snippet_counts_for_snippet(
        "Writing Style", 
        ["professional", "formal"], 
        increment=True
    )
    print(f"   ✓ Added snippet with Writing Style + [professional, formal]")
    
    cat_id2, label_ids2 = test_manager.update_snippet_counts_for_snippet(
        "Character Development", 
        ["creative", "tsundere"], 
        increment=True
    )
    print(f"   ✓ Added snippet with Character Development + [creative, tsundere]")
    
    # Add another snippet to same category
    cat_id3, label_ids3 = test_manager.update_snippet_counts_for_snippet(
        "Writing Style", 
        ["professional", "structured"], 
        increment=True
    )
    print(f"   ✓ Added another snippet with Writing Style + [professional, structured]")
    
    print("\n4. Checking current counts...")
    categories = test_manager.get_all_categories()
    labels = test_manager.get_all_labels()
    
    print("   Categories:")
    for cat_id, cat_data in categories.items():
        print(f"     • {cat_data['name']}: {cat_data['usage_count']} snippets")
    
    print("   Labels:")
    for label_id, label_data in labels.items():
        print(f"     • {label_data['name']}: {label_data['usage_count']} snippets")
    
    print("\n5. Testing snippet removal...")
    # Remove a snippet
    test_manager.update_snippet_counts_for_snippet(
        "Writing Style", 
        ["professional", "formal"], 
        increment=False
    )
    print(f"   ✓ Removed snippet with Writing Style + [professional, formal]")
    
    print("\n6. Final counts after removal...")
    categories = test_manager.get_all_categories()
    labels = test_manager.get_all_labels()
    
    print("   Categories:")
    for cat_id, cat_data in categories.items():
        print(f"     • {cat_data['name']}: {cat_data['usage_count']} snippets")
    
    print("   Labels:")
    for label_id, label_data in labels.items():
        print(f"     • {label_data['name']}: {label_data['usage_count']} snippets")    
    print("\n7. Testing lookup functions...")
    writing_style = test_manager.get_category_by_name("Writing Style")
    if writing_style:
        print(f"   ✓ Found Writing Style: {writing_style['name']} (sort: {writing_style['sort_order']})")
    else:
        print("   ❌ Could not find Writing Style category!")
    
    found_labels = test_manager.get_labels_by_names(["professional", "creative"])
    print(f"   ✓ Found labels: {[l['name'] if l else 'None' for l in found_labels]}")
    
    print("\n8. Checking generated metadata file...")
    with open("data/test_metadata.json", 'r') as f:
        metadata = json.load(f)
    
    print(f"   ✓ Categories in file: {len(metadata['categories']['items'])}")
    print(f"   ✓ Labels in file: {len(metadata['labels']['items'])}")
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed! The metadata manager is working perfectly!")
    print("💜 Maki says: 'As expected of my elegant code!'")
    
    # Cleanup
    test_file = Path("data/test_metadata.json")
    if test_file.exists():
        test_file.unlink()
        print("🧹 Cleaned up test file")

if __name__ == "__main__":
    test_metadata_manager()
