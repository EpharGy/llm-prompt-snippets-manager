# 🎀 Reusable Functions & Components Guide

*Quick reference for AI developers: Check here BEFORE building new functionality!*

---

## 🔍 QUICK LOOKUP: "I need to..."

| **I need to...** | **Use This Function** | **Location** |
|------------------|----------------------|--------------|
| Refresh display after data changes | `_refresh_tree_view()` | gui/snippet_list.py |
| Update filter bubbles after metadata changes | `_refresh_bubble_filters()` | gui/snippet_list.py |
| Add/update/delete snippets | `DataManager` methods | models/data_manager.py |
| Manage selection state | `SnippetStateManager` | models/snippet_state.py |
| Create/edit snippet dialog | `SnippetDialog` | gui/snippet_dialog.py |
| Create scrollable button container | `ScrollableBubbleFrame` | gui/snippet_list.py |
| Add tooltips to widgets | `create_tooltip(widget, text)` | utils/ui_utils.py |
| Style treeview consistently | `configure_tree_style()` | utils/ui_utils.py |
| Filter snippets by text search | `filter_snippets_by_search()` | utils/state_utils.py |
| Create styled filter buttons | `_create_bubble_button()` | gui/snippet_list.py |
| Add debug-only development tools | `DEBUG_MODE` pattern | gui/snippet_list.py |
| Log user-facing operations | `logger.info("✅ message")` | utils/logger.py |
| Sanitize category/label input | `sanitize_category_label(text, is_category)` | models/data_manager.py |

---

## 🎯 CRITICAL FUNCTIONS (Use These!)

### `_refresh_tree_view(clear_visual_selection=False)`
**Location**: `gui/snippet_list.py`  
**Purpose**: THE master refresh function - handles ALL display updates  
**Parameters**:
- `clear_visual_selection=False` - Set True to clear visual highlighting  

**✅ USE WHEN**:
- Any snippet data changes (add/update/delete)
- Need to preserve user selections and filters
- Want consistent refresh behavior

**❌ DON'T USE `_clear_search()` INSTEAD** - that only clears text search!

**Example**:
```python
# After any data modification:
self.all_snippets[snippet['id']] = snippet.copy()
self._refresh_tree_view()  # Preserves everything smartly
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
**Purpose**: Auto-wrapping scrollable container for buttons  

```python
bubble_frame = ScrollableBubbleFrame(parent, max_rows=4)
bubble_frame.add_child(button_widget)
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

## ⚠️ JANKY BITS TO FIX (Technical Debt)

### 🧪 Debug Mode Pattern ✅ IMPLEMENTED
**Purpose**: Development tools that only appear in debug mode  
**Location**: `gui/snippet_list.py` (T1/T2 test buttons)  
**Usage**: Set environment variable `PROMPT_SNIPPETS_DEBUG=true`  

```python
# Pattern for debug-only features:
import os
DEBUG_MODE = os.environ.get('PROMPT_SNIPPETS_DEBUG', 'False').lower() == 'true'

if DEBUG_MODE:
    self.test1_btn = ttk.Button(button_frame, text="T1", width=3, command=self._add_test_snippet_1)
    self.test2_btn = ttk.Button(button_frame, text="T2", width=3, command=self._add_test_snippet_2)
    # Add tooltips and state management for debug buttons
```

**✅ USE WHEN**: Adding development/testing tools that shouldn't appear for end users

### 📝 Print Statements vs Logging
**Problem**: Mix of print() and logger calls throughout codebase  
**Location**: Multiple files (snippet_list.py, data_manager.py)  
**Fix When**: Next logging cleanup pass  

```python
# REPLACE:
print(f"Delete button clicked. Current mode: {self.delete_mode}")
# WITH:
logger.debug(f"Delete button clicked. Current mode: {self.delete_mode}")
```

### 🎨 Hardcoded Styling Scattered
**Problem**: UI colors/styles repeated throughout code  
**Location**: `gui/snippet_list.py` bubble button creation  
**Fix When**: Creating centralized theme system  

```python
# CENTRALIZE THESE:
bg="#f0f0f0", fg="#333333", activebackground="#e0e0e0"
```

### 🔄 Complex Filter Logic
**Problem**: `_apply_bubble_filters()` doing too many things  
**Location**: `gui/snippet_list.py` lines 548-585  
**Fix When**: Adding more filter features - break into smaller functions  

### 🖱️ Brittle Scroll Wheel Handling
**Problem**: Manual widget tree traversal for scroll events  
**Location**: `gui/snippet_list.py` `_create_bubble_button()`  
**Fix When**: UI refactoring - use proper event delegation  

### 🔄 Inconsistent Error Handling
**Problem**: Mix of bool returns, exceptions, and silent failures  
**Location**: `models/data_manager.py`, various GUI methods  
**Fix When**: Adding comprehensive error handling system  

---

## 📋 UPDATE CHECKLIST

When adding new reusable functions to this project:

- [ ] Add function signature to "QUICK LOOKUP" table
- [ ] Document when to USE and when NOT to use
- [ ] Include code example
- [ ] Note any functions it should be paired with
- [ ] Add to appropriate section (State/Data/UI/etc.)
- [ ] Check if it fixes any items in "JANKY BITS TO FIX"

When you spot janky code:
- [ ] Add to "JANKY BITS TO FIX" section with location
- [ ] Note when it should be fixed (which feature addition)
- [ ] Include example of proper replacement

---

*Last Updated: 2025-06-19 by Maki-chan* 🎀
