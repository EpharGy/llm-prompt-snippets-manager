# roleplay-snippets/roleplay-snippets/README.md

# Prompt Snippets Manager

A simple Python desktop application built with Tkinter for managing LLM prompt snippets. This application allows users to store, organize, and combine text snippets into complete prompts for AI interactions.

## Features

- Add new snippets with fields: name, category, prompt text, labels, and an exclusive checkbox.
- View a scrollable list of all snippets with advanced filtering capabilities.
- Combine selected snippets and display them in a separate preview window.
- Copy the combined text to the clipboard for easy use elsewhere.
- Filter snippets by categories, labels, or text search with AND/OR logic.
- Clean, modern UI with clickable filter bubbles and visual feedback.

## Project Structure

```
Prompt Snippets/
├── main.py                    # Entry point of the application
├── gui/                       # Contains GUI components
│   ├── __init__.py
│   ├── app.py                 # Main application window
│   ├── snippet_list.py        # Advanced snippet list with filtering
│   ├── snippet_dialog.py      # Modal dialog for add/edit
│   ├── prompt_window.py       # Separate prompt preview window
│   ├── preview_pane.py        # Preview pane component
│   └── __pycache__/           # Python compiled bytecode files
├── models/                    # Contains data models and state management
│   ├── __init__.py
│   ├── snippet.py             # Snippet data model
│   ├── data_manager.py        # JSON data persistence
│   ├── snippet_state.py       # Selection state management
│   └── __pycache__/           # Python compiled bytecode files
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── ui_utils.py            # UI helper functions
│   ├── state_utils.py         # State utility functions
│   └── __pycache__/           # Python compiled bytecode files
├── data/                      # Data storage
│   ├── snippets.json          # Stores snippet data in JSON format
│   └── snippets copy.json     # Backup copy of snippet data
├── __pycache__/               # Python compiled bytecode files
├── requirements.txt           # Lists required Python packages
├── Prompt Snippets.code-workspace # VS Code workspace configuration
└── README.md                  # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd "Prompt Snippets"
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage Guidelines

- Use the form to add new snippets.
- Select snippets from the list to combine them.
- View the combined result and copy it to your clipboard for use in your roleplay sessions.

## License

This project is licensed under the MIT License.