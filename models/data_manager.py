import os
import json
from typing import List, Dict, Optional

class DataManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.snippets_file = os.path.join(data_dir, "snippets.json")
        self.sample_file = os.path.join(data_dir, "sample_snippets.json")
        print(f"Data directory: {self.data_dir}")  # Debug
        print(f"Snippets file: {self.snippets_file}")  # Debug
        
        # Ensure data directory exists
        if not os.path.exists(data_dir):
            print(f"Creating data directory: {data_dir}")  # Debug
            os.makedirs(data_dir)
        
        # Initialize with sample data if no user data exists
        self._initialize_sample_data_if_needed()

    def add_snippet(self, snippet: Dict) -> bool:
        """Add new snippet to storage"""
        try:
            # Load current snippets
            current_snippets = self.load_snippets()
            if current_snippets is None:
                current_snippets = []
            print(f"Current snippets in storage: {len(current_snippets)}")

            # Simply append and save
            current_snippets.append(snippet)
            
            # Save to file
            return self.save_snippets(current_snippets)
            
        except Exception as e:
            print(f"Error in add_snippet: {str(e)}")
            return False

    def save_snippets(self, snippets: List[Dict]) -> bool:
        """Save snippets to JSON file with consistent ordering"""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.snippets_file), exist_ok=True)
            
            # Reorder each snippet's keys to match desired format
            ordered_snippets = []
            for snippet in snippets:
                ordered_snippet = {
                    'id': snippet['id'],
                    'name': snippet['name'],
                    'category': snippet['category'],
                    'labels': snippet['labels'],
                    'prompt_text': snippet['prompt_text'],
                    'exclusive': snippet['exclusive']
                }
                ordered_snippets.append(ordered_snippet)
        
            print(f"Saving {len(ordered_snippets)} snippets to {self.snippets_file}")
            with open(self.snippets_file, 'w', encoding='utf-8') as f:
                json.dump(ordered_snippets, f, indent=2, ensure_ascii=False)
        
            return True
            
        except Exception as e:
            print(f"Error saving snippets: {str(e)}")
            return False

    def load_snippets(self) -> List[Dict]:
        """Load snippets from JSON file"""
        try:
            if not os.path.exists(self.snippets_file):
                print(f"Snippets file not found at {self.snippets_file}")
                return []

            with open(self.snippets_file, 'r', encoding='utf-8') as f:
                snippets = json.load(f)
                
            print(f"Successfully loaded {len(snippets)} snippets")
            return snippets

        except Exception as e:
            print(f"Error loading snippets: {str(e)}")
            return []

    def update_snippet(self, snippet: Dict) -> bool:
        """Update existing snippet"""
        try:
            current_snippets = self.load_snippets()
            
            # Find and update snippet
            updated = False
            for i, s in enumerate(current_snippets):
                if s['id'] == snippet['id']:
                    current_snippets[i] = snippet
                    updated = True
                    break
                    
            if not updated:
                print(f"Snippet with id {snippet['id']} not found")
                return False
                
            # Save updated list
            success = self.save_snippets(current_snippets)
            if not success:
                raise Exception("Failed to write to storage")
                
            return True
            
        except Exception as e:
            print(f"Error updating snippet: {str(e)}")
            return False

    def delete_snippets(self, snippet_ids: List[str]) -> bool:
        """Delete snippets by their IDs"""
        try:
            print(f"DataManager: Starting deletion of IDs: {snippet_ids}")  # Debug
            current_snippets = self.load_snippets()
            print(f"DataManager: Loaded {len(current_snippets)} current snippets")  # Debug
            
            # Filter out deleted snippets
            updated_snippets = [
                s for s in current_snippets 
                if s['id'] not in snippet_ids
            ]
            
            print(f"DataManager: After filtering, {len(updated_snippets)} snippets remain")  # Debug
            print(f"DataManager: Deleted {len(current_snippets) - len(updated_snippets)} snippets")  # Debug
            
            # Save updated list
            success = self.save_snippets(updated_snippets)
            if not success:
                raise Exception("Failed to write to storage")
            
            print("DataManager: Successfully saved updated snippets to file")  # Debug
            return True
            
        except Exception as e:
            print(f"Error deleting snippets: {str(e)}")
            return False

    def _initialize_sample_data_if_needed(self):
        """Copy sample data to user data file if user data doesn't exist"""
        try:
            # If user data already exists, do nothing
            if os.path.exists(self.snippets_file):
                return
            
            # If sample file exists, copy it to user data
            if os.path.exists(self.sample_file):
                print("Initializing with sample data for first-time users")
                with open(self.sample_file, 'r', encoding='utf-8') as f:
                    sample_data = json.load(f)
                
                # Save sample data as user data
                self.save_snippets(sample_data)
                print(f"Copied {len(sample_data)} sample snippets to user data file")
            else:
                print("No sample data file found, starting with empty data")
                
        except Exception as e:
            print(f"Error initializing sample data: {str(e)}")
            # Continue without sample data if there's an error