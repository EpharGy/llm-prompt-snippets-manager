# LLM Prompt Snippets Manager - Development TODO

## 📖 DEVELOPER REFERENCE
**🆕 NEW**: Before implementing features, check `REUSABLE_FUNCTIONS.md` for existing components!

## 🎯 CURRENT FOCUS: 🐛 BUG FIXES & POLISH - Production Stabilization

### ✅ PHASE 2 COMPLETED: Data Architecture & GUI Integration
1. **✅ COMPLETED: UUID-based metadata system**
   - Combined metadata.json file (categories + labels)
   - UUID-based IDs with no import conflicts
   - Categories: name, id(UUID), sort_order(5), color(hex/null), dt_created, usage_count(0)
   - Labels: name, id(UUID), dt_created, usage_count(0)
2. **✅ COMPLETED: Robust backend integration**
   - MetadataManager with validation/auto-creation
   - DataManager with proper GUI format loading
   - Snippet class with clean category_id/label_ids
3. **✅ COMPLETED: Professional GUI with smart state management**
   - Unified refresh system preserving selections/filters
   - Filter bubble updates after metadata changes
   - Clean prompt preview/copy functionality
4. **✅ COMPLETED: Comprehensive logging system**
   - Structured, emoji-rich logging throughout
   - User-facing and debug-level messages
   - Replaced all print statements with proper logging
5. **✅ COMPLETED: Maintainable codebase**
   - Documented reusable functions and patterns
   - Smart state preservation patterns
   - Professional error handling and user feedback

### 🐛 CURRENT PHASE: Production Stabilization & Bug Fixes
**Status**: In Progress - Post-release refinement and bug fixes

1. **Bug Fixes & Edge Cases**
   - [x] **HIGH PRIORITY**: Fix selection highlighting bug - all snippets appear highlighted after clearing filters
   - [x] **CRITICAL**: Fix phantom selection highlighting after snippet operations (update, add, delete)
   - [x] **UI Enhancement**: Fix mouse wheel scrolling over filter bubble buttons
   - [x] **Font System**: Fix dynamic font scaling for filter bubble buttons
   - [x] **UI Layout**: Move search box below snippet list for logical grouping of filter controls
   - [x] **Icon Consistency**: Apply custom app icon to all windows (main, prompt preview, add/edit dialog)
   - [x] **State Management**: Fix preview updates when editing selected snippets
   - [ ] Fix any user-reported issues from initial release
   - [ ] Handle edge cases in data validation
   - [ ] Improve error messaging and user feedback
   - [ ] Validate all UI interactions work correctly

2. **Code Polish & Cleanup**   - [x] **HIGH PRIORITY**: Add font size scaling/settings for 4K displays and accessibility
     - ✅ Created `utils/font_manager.py` with centralized font management
     - ✅ Font scale options: Small, Normal, Large, Extra Large, Auto (DPI-aware)
     - ✅ Persistent settings saved to `data/ui_settings.json`
     - ✅ DPI detection for auto-scaling on high-DPI displays
     - ✅ Enhanced with multi-monitor DPI detection and dynamic updates
     - ✅ **COMPLETED**: Integrated font scale dropdown into main app UI     - ✅ **COMPLETED**: Applied font manager to ALL UI components
       - ✅ SnippetList: Tree view, headers, search box, filter labels, all buttons, bubble filters
       - ✅ PromptWindow: Header, copy button, and text content font scaling  
       - ✅ SnippetDialog: All form elements font scaling
       - ✅ Main App: Font dropdown, show prompt button, copy button
       - ✅ Dynamic font refresh when user changes scale setting
       - ✅ Robust error handling for widgets that don't support fonts
     - ✅ **COMPLETED**: Perfect dynamic bubble spacing system
       - ✅ Implemented progressive, ratio-based row height calculation
       - ✅ Small: 5px padding (perfect baseline), Normal: 7px, Large: 9px, Extra Large: 11px
       - ✅ Fully dynamic scaling works with any user base font size setting
       - ✅ Maintains consistent visual proportions across all font scales
       - ✅ Professional, polished appearance with optimal breathing room
   - [ ] Final cleanup of any remaining print statements
   - [ ] Optimize performance for larger snippet collections
   - [ ] Ensure consistent styling and UX patterns
   - [ ] Complete any remaining documentation gaps

3. **Testing & Validation**
   - [ ] Test with various data sizes and edge cases
   - [ ] Validate import/export functionality thoroughly
   - [ ] Confirm cross-platform compatibility
   - [ ] User acceptance testing with real workflows

4. **UI/UX Critical Issues**
   - [ ] **Font scaling system** - User-configurable font sizes for 4K/high-DPI displays
   - [ ] **Selection highlighting bug** - Fix incorrect highlighting after filter clearing
   - [ ] **Visual state consistency** - Ensure all UI state changes are properly reflected
   - [ ] **Accessibility improvements** - Consider contrast, readability, keyboard navigation

5. **Technical Debt & Code Quality**
   - ✅ **DEBUG MODE COMPLETED** - Unified debug system with multiple activation methods
     - ✅ `debug.py` launcher (environment variable method)
     - ✅ `--debug` and `-d` command line flags  
     - ✅ `PROMPT_SNIPPETS_DEBUG=true` environment variable
     - ✅ Unified debug detection across all components
     - ✅ EXE-ready: Command line flags work for future installers
     - ✅ Added `utils/debug_utils.py` with EXE detection helpers   - ✅ **COMPLETED: Exception Handling Cleanup** - Replaced all bare `except:` with specific exception types
     - ✅ Removed unsupported `logger.exception()` calls, replaced with `logger.debug()`/`logger.error()`
     - ✅ Fixed indentation and concatenation issues from automated edits
     - ✅ Improved error specificity and logging consistency across codebase
     - ✅ Application tested and verified to run without errors after changes
   - [ ] **Print Statement Cleanup** - Replace remaining print() calls with proper logging
   - [ ] **CODE ARCHITECTURE: Large File Refactoring** - Break down oversized files for maintainability
     - [ ] **HIGH PRIORITY**: Split `snippet_list.py` (1699 lines) into focused modules:
       - [ ] `gui/snippet_list.py` (main component, ~400-500 lines)
       - [ ] `gui/components/scrollable_bubble_frame.py` (bubble container, ~200-300 lines)
       - [ ] `gui/components/filter_controls.py` (filtering logic, ~300-400 lines)
       - [ ] `gui/components/tree_operations.py` (treeview operations, ~300-400 lines)
       - [ ] `gui/mixins/font_mixin.py` (font management methods, ~200-300 lines)
   - [ ] **Centralized Styling** - Move hardcoded UI colors/styles to theme system
   - [ ] **Complex Filter Logic** - Break down `_apply_bubble_filters()` into smaller functions
   - [ ] **Scroll Wheel Handling** - Replace manual widget tree traversal with proper event delegation

### 🎯 NEXT PRIORITIES: Advanced Management Features
1. **Category/Label Management UI**
   - [ ] Create management interface (view, rename, delete with protection)
   - [ ] Add delete protection (block if category/label in use)
   - [ ] Implement sort number editing for categories
   - [ ] Add color coding support for categories and labels

2. **Merge & Consolidation Tools**
   - [ ] Multi-select interface for categories/labels
   - [ ] Merge operation (consolidate duplicates/typos)
   - [ ] Update all affected snippets during merge
   - [ ] Clean up unused entries after merge

3. **Enhanced Snippet Creation**
   - [ ] Autocomplete dropdown with filtering for categories/labels
   - [ ] Create new category/label during snippet creation
   - [ ] Default sort number assignment for new categories

4. **Import/Export & Data Migration**
   - [ ] Handle category/label conflicts during import
   - [ ] Auto-generate missing references
   - [ ] Profile/dataset switching system

### �🎹 Usage Count Management Strategy
- Update on: snippet create/delete, category/label changes, merge ops, imports
- Helper functions: increment_usage(), decrement_usage(), recalculate_usage()
- Called from: snippet operations, merge operations, import operations

---

## Phase 1: Foundation & Core Improvements ✅
- [x] Application icon support (multi-resolution .ico)
- [x] Professional sample snippets for distribution
- [x] Privacy setup (.gitignore for persona files)
- [x] Clean repo structure and dev branch workflow

## Phase 2: Data Architecture & Advanced Management ✅
### Category/Label System Integration ✅ COMPLETED
#### 1. Data Structure Design ✅
- [x] Combined metadata.json with UUID-based IDs
- [x] JSON schema template and validation system
- [x] Snippet linking with category_id/label_ids fields

#### 2. Validation & Data Integrity ✅
- [x] Auto-ID generation and validation system
- [x] Referential integrity checks
- [x] Startup validation and refresh

#### 3. GUI Integration ✅
- [x] Smart state management with selection/filter preservation
- [x] Filter bubble updates after metadata changes
- [x] Clean prompt preview and copy functionality
- [x] Structured logging system throughout

#### 4. Documentation & Maintainability ✅
- [x] Comprehensive reusable functions documentation
- [x] Standard patterns for data modifications
- [x] Error handling and user feedback systems

### 🚀 READY FOR: Advanced Management Features
#### 4. Enhanced Management Interface
- [ ] Create category/label management UI (view, rename, delete)
- [ ] Add delete protection (block if category/label in use)
- [ ] Implement sort number editing for categories
- [ ] Add color coding support for categories and labels

#### 5. Merge Functionality
- [ ] Multi-select interface for categories/labels
- [ ] Merge operation (consolidate duplicates/typos)
- [ ] Update all affected snippets during merge
- [ ] Clean up unused entries after merge

#### 6. Snippet Creation Integration
- [ ] Autocomplete dropdown with filtering for categories/labels
- [ ] Create new category/label during snippet creation
- [ ] Default sort number assignment for new categories
- [ ] UI state management (only allow editing when no selections)

#### 7. Import/Export & Migration
- [ ] Handle category/label conflicts during import
- [ ] Auto-generate missing references
- [ ] Manual data migration from current format (one-time task)

#### 8. Enhanced Organization Views
- [ ] Category-based organization and filtering in snippet list
- [ ] Visual category grouping in UI
- [ ] Sort snippets by category priority numbers

### Profile/Dataset Switching
- [ ] Design profile system architecture
- [ ] Implement quick profile switching (Professional, RP, Maki-themed, etc.)
- [ ] Profile-specific settings and preferences
- [ ] Import/export profile data
- [ ] Profile backup and versioning

## Phase 3: Enhanced User Experience
### UI/UX Improvements
- [ ] Advanced search and filtering
- [ ] Snippet preview improvements
- [ ] Keyboard shortcuts and hotkeys
- [ ] Dark/light theme support

### Snippet Management
- [ ] Bulk operations (delete, move, copy)
- [ ] Snippet templates and quick creation
- [ ] Snippet versioning/history
- [ ] Advanced snippet metadata (usage stats, etc.)
- [ ] Drag-and-drop snippet reordering (after category system is stable)

## Phase 4: Analytics & Intelligence
### Usage Tracking
- [ ] Snippet usage analytics
- [ ] Most-used snippets dashboard
- [ ] Usage patterns and insights
- [ ] Export usage reports

### Smart Features
- [ ] AI-powered snippet suggestions
- [ ] Auto-categorization of new snippets
- [ ] Duplicate snippet detection
- [ ] Smart snippet combinations/chaining

## Phase 5: Distribution & Extensibility
### Packaging & Distribution
- [ ] PyInstaller standalone executable
- [ ] Installer creation
- [ ] Auto-updater system
- [ ] Cross-platform compatibility testing

### Advanced Features
- [ ] Plugin/extension system
- [ ] API for external integrations
- [ ] Cloud sync capabilities
- [ ] Team collaboration features
- [ ] Snippet sharing marketplace

## Technical Debt & Maintenance
- [x] Code refactoring and optimization (Phase 2 complete)
- [x] Comprehensive logging system implementation
- [x] Documentation updates - Created REUSABLE_FUNCTIONS.md
- [ ] Comprehensive testing suite
- [ ] Performance profiling and optimization
- [ ] Error handling improvements (basic implemented)

## Development Guidelines
- **📖 Always check `REUSABLE_FUNCTIONS.md` before implementing new features**
- Keep persona files and development notes in .gitignore
- Batch documentation updates for main branch merges
- Focus on professional use cases while maintaining creative flexibility
- Consider both personal and team/enterprise use cases
- **🔄 Update REUSABLE_FUNCTIONS.md when creating new reusable patterns**

## Ideas & Future Considerations
- [ ] Integration with popular IDEs (VS Code extension?)
- [ ] Mobile companion app
- [ ] Web-based version
- [ ] AI model fine-tuning on user snippets
- [ ] Natural language snippet search
- [ ] Snippet recommendation engine

---
*Last updated: June 19, 2025*
*Phase 2 complete! Currently stabilizing production release with bug fixes. 🎀*
*Maki says: "Time to polish everything to perfection!" 💜*
