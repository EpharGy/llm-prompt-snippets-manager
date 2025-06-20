# 🎀 Reusable Functions & Components Guide

*Quick reference for AI developers: Check here BEFORE building new functionality!*

---

## 🔍 QUICK LOOKUP: "I need to..."

| **I need to...** | **Use This Function** | **Location** |
|------------------|----------------------|--------------|
| Refresh display after data changes | `_refresh_tree_view(preserve_selections=False)` | gui/snippet_list.py |
| Update filter bubbles after metadata changes | `filter_controls.refresh_bubble_filters()` | gui/components/filter_controls.py |
| Add/update/delete snippets | `DataManager` methods | models/data_manager.py |
| Manage selection state | `SnippetStateManager` | models/snippet_state.py |
| Create/edit snippet dialog | `SnippetDialog` | gui/snippet_dialog.py |
| Create scrollable button container | `ScrollableBubbleFrame` | gui/components/scrollable_bubble_frame.py |
| Create filter controls component | `FilterControls` | gui/components/filter_controls.py |
| Add tooltips to widgets | `create_tooltip(widget, text)` | utils/ui_utils.py |
| Style treeview consistently | `configure_tree_style()` | utils/ui_utils.py |
| Filter snippets by text search | `filter_snippets_by_search()` | utils/state_utils.py |
| Create styled filter buttons with mouse wheel | `FilterControls.create_bubble_button()` | gui/components/filter_controls.py |
| Add debug-only development tools | `get_debug_mode()` | utils/debug_utils.py |
| Detect if running as EXE | `is_exe_build()` | utils/debug_utils.py |
| Get app path (script or EXE) | `get_app_path()` | utils/debug_utils.py |
| Log user-facing operations | `logger.info("✅ message")` | utils/logger.py |
| Sanitize category/label input | `sanitize_category_label(text, is_category)` | models/data_manager.py |
| Manage dynamic font scaling | `FontManager` | utils/font_manager.py |
| Handle exceptions properly | See Exception Handling Patterns | REUSABLE_FUNCTIONS.md §🚨 |

---

## 🎯 CRITICAL FUNCTIONS (Use These!)

### `_refresh_tree_view(preserve_selections=True)`
**Location**: `gui/snippet_list.py`  
**Purpose**: THE master refresh function - handles ALL display updates  
**Parameters**:
- `preserve_selections=True` - Set False to avoid phantom highlighting during data operations

**✅ USE WHEN**:
- Any snippet data changes (add/update/delete) - use `preserve_selections=False`
- Need to preserve user selections and filters - use default `True`
- Want consistent refresh behavior

**⚠️ CRITICAL**: Use `preserve_selections=False` for data modification operations to prevent phantom highlighting

**Example**:
```python
# After snippet update/add/delete:
self.all_snippets[snippet['id']] = snippet.copy()
self._refresh_tree_view(preserve_selections=False)  # Prevents phantom highlighting

# For filter changes or general refresh:
self._refresh_tree_view()  # Preserves selections
```

### `_refresh_bubble_filters()`
**Location**: `gui/snippet_list.py`  
**Purpose**: Rebuild category/label filter buttons from current snippets  

**✅ USE WHEN**:
- After adding/updating/deleting snippets
- Categories or labels might have changed
- Need to show new filter options

**Example**:
```python
# Always pair with tree refresh:
self._refresh_tree_view()
self._refresh_bubble_filters()
```

### `DataManager.load_snippets_for_gui()`
**Location**: `models/data_manager.py`  
**Purpose**: Load snippets in GUI format (strings not UUIDs)  

**✅ USE WHEN**:
- Loading snippets for display in GUI
- Need category/label names as strings

**❌ DON'T USE** `load_snippets()` for GUI - that returns UUID format!

---

## 📊 STATE MANAGEMENT

### `SnippetStateManager`
**Location**: `models/snippet_state.py`  

**Key Properties**:
- `selected_ids` - List of selected snippet IDs
- `is_filtered` - Boolean if any filtering active
- `filtered_ids` - List of IDs matching current filters

**Key Methods**:
```python
state_manager.set_state(snippet_id, SnippetState.SELECTED, category, exclusive)
state_manager.clear_selections(snippet_ids)  # Clear specific IDs
state_manager.clear_search_filter()  # Clear text search only
```

---

## 🔄 DATA OPERATIONS

### `sanitize_category_label(text: str, is_category: bool = False)`
**Location**: `models/data_manager.py`  
**Purpose**: Sanitize category/label text to consistent format (lowercase, underscores)  
**Parameters**:
- `text` - The raw category or label text to sanitize
- `is_category=False` - Set True for categories (validates no commas allowed)

**✅ USE WHEN**:
- Processing user input for categories/labels
- Ensuring consistent category/label formatting
- Validating category text (no commas)

**❌ THROWS ERROR**: If `is_category=True` and text contains commas

**Example**:
```python
# For labels (commas OK, will be trimmed/formatted):
clean_label = sanitize_category_label("My Cool Label")
# Returns: "my_cool_label"

# For categories (validates no commas):
try:
    clean_category = sanitize_category_label("Business Writing", is_category=True) 
    # Returns: "business_writing"
except ValueError as e:
    logger.error(f"Invalid category: {e}")
```

### `DataManager` Methods
**Location**: `models/data_manager.py`  

```python
# Loading (GUI format with string categories/labels):
snippets = data_manager.load_snippets_for_gui()

# Adding (expects string format):
success = data_manager.add_snippet({
    'name': 'Test', 'category': 'TestCat', 
    'labels': ['label1', 'label2'], 'prompt_text': '...'
})

# Updating (expects string format):
success = data_manager.update_snippet(snippet_dict)

# Deleting:
success = data_manager.delete_snippets([id1, id2, id3])
```

---

## 🎨 UI COMPONENTS

### `ScrollableBubbleFrame(parent, max_rows=4)`
**Location**: `gui/snippet_list.py`  
**Purpose**: Auto-wrapping scrollable container for buttons with dynamic row height scaling  

**✨ NEW: Perfect Dynamic Spacing System**:
- Automatically calculates row height based on font size
- Progressive padding: Small (5px), Normal (7px), Large (9px), Extra Large (11px)
- Scales proportionally with any user base font size setting
- Call `update_row_height()` when font changes

```python
bubble_frame = ScrollableBubbleFrame(parent, max_rows=4)
bubble_frame.add_child(button_widget)
bubble_frame.update_row_height()  # Call after font changes
bubble_frame.clear_children()  # Remove all buttons
```

### `SnippetDialog(parent, snippet=None, is_edit=False)`
**Location**: `gui/snippet_dialog.py`  
**Returns**: `dialog.result` (dict) or None if cancelled  

### `create_tooltip(widget, text)`
**Location**: `utils/ui_utils.py`  
**Purpose**: Add hover tooltips to any widget  

```python
create_tooltip(self.button, "This button does something cool")
```

### `configure_tree_style()`
**Location**: `utils/ui_utils.py`  
**Purpose**: Apply consistent styling to treeview widgets  

```python
style = configure_tree_style()  # Returns configured ttk.Style
```

### Bubble Button Creation Pattern
**Location**: `gui/snippet_list.py` (`_create_bubble_button()`)  
**Purpose**: Create styled, scrollable filter buttons  

```python
btn = self._create_bubble_button(parent, "Label Text", "category", "value")
# Returns configured tk.Button with scroll wheel forwarding
```

---

## 🎨 UI UTILITIES

### `FontManager` - Centralized Font Scaling System
**Location**: `utils/font_manager.py`  
**Purpose**: Provides consistent, scalable font management with dynamic DPI detection

**Font Scale Options**:
- `small` - Compact fonts for small displays
- `normal` - Standard font sizes (default)
- `large` - Larger fonts for readability
- `extra_large` - Extra large fonts for accessibility
- `auto` - **DPI-aware automatic scaling with multi-monitor support**

**Auto Scaling Features**:
- **Launch Detection**: Detects DPI on app startup when "Auto" is selected
- **Dynamic Updates**: Monitors window movement between monitors with different DPIs
- **Caching**: Caches DPI scale factor until window moves or setting changes
- **Multi-Monitor**: Uses main window reference for accurate DPI detection

**Usage**:
```python
from utils.font_manager import get_font_manager, setup_window_dpi_monitoring

# Setup DPI monitoring for main window (do this once on startup)
font_mgr = setup_window_dpi_monitoring(main_window)

# Set font scale (persists to settings)
font_mgr.set_font_scale('auto')  # Enable auto-scaling

# Get fonts for UI elements
tree_font = font_mgr.get_font('tree', 'normal')
heading_font = font_mgr.get_font('heading', 'bold')
font_tuple = font_mgr.get_font_tuple('button')

# Force refresh when needed (usually automatic)
from utils.font_manager import refresh_auto_fonts
refresh_auto_fonts()  # Call if you detect monitor changes manually
```

**Auto Scaling Triggers**:
1. **App Launch** - Detects initial DPI when FontManager is created
2. **Scale Selection** - When user selects "Auto" from dropdown
3. **Window Movement** - Automatically detects when window moves between monitors
4. **Manual Refresh** - Can be triggered programmatically

**Font Types**:
- `default` - General UI text
- `heading` - Section headings, titles
- `button` - Button text
- `tree` - Tree view items
- `dialog` - Dialog content

**✅ USE WHEN**:
- Setting fonts for any UI element
- Need consistent scaling across components
- Supporting high-DPI displays (4K, etc.)
- Handling multi-monitor setups with different scaling
- Adding accessibility features

**Features**:
- Persistent settings in `data/ui_settings.json`
- Real-time DPI detection for multi-monitor setups
- Font caching for performance
- Easy integration with existing widgets
- Automatic refresh when moving between monitors

### `set_app_icon(window)`
**Location**: `gui/snippet_list.py`  
**Purpose**: Set the application icon for the main window  

**Parameters**:
- `window` - The Tkinter window instance to set the icon for

**✅ USE WHEN**:
- You need to set a custom icon for the application
- Changing the icon at runtime

**Example**:
```python
from gui.snippet_list import set_app_icon

# In your main application code:
set_app_icon(self.root)
```

---

## 📝 LOGGING PATTERNS

### User-Facing Operations
```python
logger.info("➕ Adding new snippet: 'Name' (Category: Cat)")
logger.info("✏️ Updating snippet: 'Name'")  
logger.info("🗑️ Deleting snippet: 'Name'")
logger.info("✅ Successfully completed operation")
logger.info("📋 Copied 45 characters to clipboard")
```

### Debug/Internal Operations
```python
logger.debug("Refreshing view with smart state preservation")
logger.debug("Updating filter options after changes")
logger.error("Failed to save snippet: {error_details}")
```

---

## ⚠️ COMMON MISTAKES TO AVOID

1. **DON'T** call `_clear_search()` when you want smart refresh - use `_refresh_tree_view()`
2. **DON'T** use `load_snippets()` for GUI - use `load_snippets_for_gui()`  
3. **DON'T** forget to call `_refresh_bubble_filters()` after metadata changes
4. **DON'T** manually manage selections - let `_refresh_tree_view()` handle it
5. **DON'T** use print statements - use the logger system

---

## �️ STANDARD PATTERN FOR DATA MODIFICATIONS

```python
# 1. Modify data via DataManager
success = self.data_manager.add_snippet(snippet_data)
if not success:
    logger.error("Failed to save snippet")
    return False

# 2. Update local collections  
self.all_snippets[snippet['id']] = snippet.copy()

# 3. Smart refresh (preserves selections/filters)
logger.debug("Refreshing display with state preservation")
self._refresh_tree_view()

# 4. Update filter options if metadata changed
logger.debug("Updating filter options")
self._refresh_bubble_filters()

# 5. User feedback
logger.info("✅ Successfully added snippet: 'Name'")
```

---

## 🔍 FILTER & SEARCH UTILITIES

### `filter_snippets_by_search(snippets, search_terms)`
**Location**: `utils/state_utils.py`  
**Purpose**: Filter snippets by text search terms  
**Returns**: Set of matching snippet IDs  

```python
matching_ids = filter_snippets_by_search(all_snippets.values(), ["search", "terms"])
```

### `get_category_selections(state_manager, snippets)`
**Location**: `utils/state_utils.py`  
**Purpose**: Group selected snippets by category  
**Returns**: Dict mapping categories to snippet lists  

### `_get_bubble_filtered_ids()`
**Location**: `gui/snippet_list.py`  
**Purpose**: Get IDs matching current bubble filters (AND/OR logic)  

### `_toggle_bubble_filter(filter_type, filter_value, button)`
**Location**: `gui/snippet_list.py`  
**Purpose**: Toggle category/label filters with visual feedback  

---

## 🧪 DEBUG MODE PATTERN

### Launching Debug Mode
### 🐛 Unified Debug System
**Locations**: `utils/debug_utils.py`, `utils/logger.py`, `debug.py`  
**Purpose**: Consistent debug mode detection across all components with multiple activation methods

**✨ Multiple Ways to Enable Debug Mode**:
```bash
# Method 1: Debug launcher (recommended for development)
python debug.py

# Method 2: Command line flags (EXE-ready)
python main.py --debug
python main.py -d

# Method 3: Environment variables  
PROMPT_SNIPPETS_DEBUG=true python main.py
DEBUG=true python main.py  # Generic fallback
```

**Usage in Code**:
```python
from utils.debug_utils import get_debug_mode, debug_print, is_exe_build

# Check debug mode anywhere
if get_debug_mode():
    # Add debug-only features
    self.test_button = ttk.Button(frame, text="Test", command=self._test_function)

# Debug-only printing
debug_print("This only shows in debug mode")

# EXE detection (useful for installers)
if is_exe_build():
    # Handle executable-specific logic
    app_path = get_app_path()  # Works for both script and EXE
```

**Legacy Pattern (still works)**:
```python
import os
DEBUG_MODE = os.environ.get('PROMPT_SNIPPETS_DEBUG', 'False').lower() == 'true'

if DEBUG_MODE:
    # Add development tools that shouldn't appear for end users
    self.test1_btn = ttk.Button(button_frame, text="T1", width=3, command=self._add_test_snippet_1)
    self.test2_btn = ttk.Button(button_frame, text="T2", width=3, command=self._add_test_snippet_2)
```

**✅ FEATURES**:
- **EXE-Ready**: Command line flags work with compiled executables
- **Multiple Methods**: Environment variables, CLI flags, launcher script
- **Unified Detection**: All components use same debug state
- **Source Tracking**: Logs which method activated debug mode

---

## 🚨 EXCEPTION HANDLING PATTERNS

### **✅ GOOD: Specific Exception Types**
**Always use specific exception types instead of bare `except:`**

```python
# ✅ GOOD - Specific exceptions with proper logging
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except FileNotFoundError as e:
    logger.debug(f"Settings file not found, using defaults: {e}")
    return default_settings
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in settings file: {e}")
    return default_settings
except OSError as e:
    logger.error(f"Failed to read settings file: {e}")
    return default_settings
```

### **❌ BAD: Bare Except Clauses**
```python
# ❌ BAD - Hides all errors, makes debugging impossible
try:
    risky_operation()
except:
    pass  # This hides ALL errors including KeyboardInterrupt!
```

### **✅ GOOD: Logger Pattern (Our Custom Logger)**
**Our custom logger doesn't support `logger.exception()` - use alternatives:**

```python
# ✅ GOOD - Use logger.debug() or logger.error() with exception details
try:
    operation_that_might_fail()
except SpecificError as e:
    logger.debug(f"Expected error during operation: {e}")
    # Continue gracefully
except UnexpectedError as e:
    logger.error(f"Unexpected error in operation: {str(e)}")
    return False
```

### **❌ BAD: Unsupported Logger Methods**
```python
# ❌ BAD - logger.exception() not supported in our custom logger
try:
    operation()
except Exception as e:
    logger.exception("This will fail!")  # Method doesn't exist
```

### **✅ GOOD: Tkinter-Specific Patterns**
```python
# ✅ GOOD - Handle Tkinter widget destruction gracefully  
try:
    widget.configure(font=new_font)
except tk.TclError as e:
    logger.debug(f"Widget doesn't support font configuration: {e}")
    pass  # Expected for certain widget types
except Exception as e:
    logger.debug(f"Unexpected error updating widget font: {e}")
    pass
```

### **Exception Handling Guidelines**
1. **Be Specific**: Use specific exception types (FileNotFoundError, json.JSONDecodeError, etc.)
2. **Log Appropriately**: Use `logger.debug()` for expected/minor errors, `logger.error()` for serious issues
3. **Include Context**: Add meaningful error messages with context about what was being attempted
4. **Don't Hide Errors**: Avoid bare `except:` - it catches system interrupts and makes debugging impossible
5. **Fail Gracefully**: Provide fallback behavior or default values when possible

---

## 📋 UPDATE CHECKLIST

When adding new reusable functions to this project:

- [ ] Add function signature to "QUICK LOOKUP" table
- [ ] Document when to USE and when NOT to use
- [ ] Include code example
- [ ] Note any functions it should be paired with
- [ ] Add to appropriate section (State/Data/UI/etc.)

When you discover reusable patterns:
- [ ] Document the pattern in appropriate section
- [ ] Add examples and usage notes
- [ ] Update the quick lookup table

---

*Last Updated: 2025-06-19 by Maki-chan* 🎀
