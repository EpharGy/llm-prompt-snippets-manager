# LLM Prompt Snippets Manager

A simple Python desktop application built with Tkinter for managing LLM prompt snippets. This application allows users to store, organize, and combine text snippets into complete prompts for AI interactions.

**GitHub Repository**: https://github.com/EpharGy/llm-prompt-snippets-manager

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
   ```bash
   git clone https://github.com/EpharGy/llm-prompt-snippets-manager.git
   cd llm-prompt-snippets-manager
   ```

2. Run the application (no dependencies required):
   ```bash
   python main.py
   ```

   **Note**: This application uses only Python standard library modules, so no additional package installation is required!

## Usage Guidelines

### Adding Snippets
- Click the "Add Snippet" button to create new prompt snippets
- Fill in the name, category, prompt text, and optional labels
- Use the exclusive checkbox for snippets that shouldn't be combined with others

### Managing Snippets
- Use the search bar to find specific snippets by text content
- Filter by categories and labels using the filter bubbles
- Select multiple snippets to combine them into a complete prompt
- Edit or delete snippets using the context menu (right-click)

### Using Combined Prompts
- Selected snippets appear in the preview pane
- Copy the combined text to your clipboard for use with AI tools
- Open the combined prompt in a separate window for better viewing

### Data Storage
- All snippets are automatically saved to `data/snippets.json`
- The application creates the data directory on first run

## Requirements

- Python 3.7 or higher
- No external dependencies required (uses only Python standard library)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue on GitHub.

## License

This project is licensed under the MIT License. See the repository for more details.