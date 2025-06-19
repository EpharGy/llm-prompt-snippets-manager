#!/usr/bin/env python3
"""
Debug launcher for LLM Prompt Snippets Manager

This script provides an easy way to launch the application in debug mode
by setting the PROMPT_SNIPPETS_DEBUG environment variable.

Usage:
    python debug.py                 # Launch with debug mode enabled
    
Alternative debug methods:
    python main.py --debug          # Command line flag
    python main.py -d               # Short flag
    PROMPT_SNIPPETS_DEBUG=true python main.py  # Environment variable

Debug mode enables:
- Test buttons in the snippet list (Add Test Snippet 1/2)
- Verbose logging output
- Additional debug information in console
"""

import os
import sys

# Set debug mode via environment variable
os.environ['PROMPT_SNIPPETS_DEBUG'] = 'true'

# Run the main application
if __name__ == "__main__":
    print("🐛 Debug mode enabled via debug.py launcher")
    from gui.app import PromptSnippetsApp
    app = PromptSnippetsApp()
    app.run()
