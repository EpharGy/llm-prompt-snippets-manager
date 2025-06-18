#!/usr/bin/env python3
"""
Debug wrapper for LLM Prompt Snippets Manager
Sets DEBUG environment and runs the main application
"""

import os
import sys

# Set debug mode
os.environ['PROMPT_SNIPPETS_DEBUG'] = 'true'

# Run the main application
if __name__ == "__main__":
    from gui.app import PromptSnippetsApp
    app = PromptSnippetsApp()
    app.run()
