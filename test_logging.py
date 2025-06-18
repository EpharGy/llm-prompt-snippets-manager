#!/usr/bin/env python3
"""
Test our new logging system with the metadata manager
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.metadata_manager import metadata_manager
from utils.logger import set_debug_mode

def test_logging_integration():
    """Test the integrated logging system."""
    
    print("🎹 Testing Integrated Logging System - Maki's Polish! 💜")
    print("=" * 60)
    
    # Test in standard mode first
    print("\n📝 Testing STANDARD mode (clean output):")
    set_debug_mode(False)
    
    # Create some test data
    test_snippets = [
        {
            "id": "test-1",
            "category_id": "cat-1", 
            "label_ids": ["label-1", "label-2"],
            "name": "Test Snippet"
        }
    ]
    
    # This should show minimal, clean output
    metadata_manager.validate_and_refresh_from_snippets(test_snippets)
    
    print("\n📝 Testing DEBUG mode (detailed output):")
    set_debug_mode(True)
    
    # Same operation but with debug info
    metadata_manager.validate_and_refresh_from_snippets(test_snippets)
    
    print("\n📝 Back to STANDARD mode:")
    set_debug_mode(False)
    metadata_manager.refresh_usage_counts(test_snippets)
    
    print("\n✅ Logging integration test complete!")
    print("💜 Maki says: 'Now our system is production-ready!'")
    
    # Cleanup
    test_metadata = Path("data/metadata.json")
    if test_metadata.exists():
        test_metadata.unlink()

if __name__ == "__main__":
    test_logging_integration()
