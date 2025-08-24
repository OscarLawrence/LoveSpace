# OM Tool Analysis - Extractable Functionality

## Overview
Analysis of `projects/tools/om` for functionality that could be extracted and properly implemented in Axiom with formal contracts.

## Key Components Found

### 1. Documentation Access
**Location**: `projects/parsers/docs-parser/`
- **Python stdlib parser** (`python_stdlib.py`) - Parses docs.python.org
- **Universal parser** (`universal_parser.py`) - Uses docling for any HTML/PDF
- **Web search** (`search.py`) - Tavily/Serper API integration for finding docs
- **Batch parser** - Pre-cache popular functions

**CLI Commands**:
```bash
om docs search "query"           # Search code patterns
om docs dense "path"             # Show dense documentation  
om docs url "url" --function f   # Parse docs from URL
om docs search-docs "query"      # Web search for docs
om python parse "module.func"    # Parse Python stdlib docs
om python warm                   # Pre-cache popular functions
```

### 2. File Operations
**Location**: `projects/tools/om/src/om/`
- **Coherent API** (`coherent_api.py`) - Direct Anthropic API with validation
- **File updater** (`coherent_file_updater.py`) - Multi-file atomic updates
- **Code execution** (`cli/code.py`) - Safe Python interpreter with timeout
- **Bash execution** (`cli/code.py`) - Shell commands with timeout

**CLI Commands**:
```bash
om code execute "code" --timeout 30    # Execute Python safely
om code bash "command" --timeout 30    # Execute bash safely
om coherence update file1.py "request" # Update files coherently
```

### 3. Code Analysis
**Location**: `projects/core/knowledge/`
- **DB manager** (`db_manager.py`) - SQLite-based code indexing
- **Query interface** (`query_interface.py`) - High-level search API
- **Pattern detection** - Find architectural patterns
- **Function/class search** - Find code elements by name

**CLI Commands**:
```bash
om find analyze              # Analyze codebase structure
om find architecture         # Show architectural overview
om find dependencies         # Show dependency analysis
om find patterns             # Show detected patterns
om find class "ClassName"    # Find class by name
om find function "func_name" # Find function by name
om code parse --full         # Parse codebase with patterns
om code stats                # Show analysis statistics
```

### 4. CLI Structure
**Location**: `projects/tools/om/src/om/cli/`
- **Modular commands** - Separate files per command group
- **Scoping system** - Focus on specific modules/directories
- **Utils** - Common functionality checks

## Key Issues Found

### ❌ Not Battle-Tested
- Many functions have basic error handling but no comprehensive testing
- Complex dependencies (langchain, docling, etc.) that could fail
- No formal verification of coherence claims

### ❌ Not 100% Coherent
- **Mixed abstractions** - Some use direct API, others use langchain
- **Inconsistent error handling** - Different patterns across modules
- **No formal contracts** - Functions lack coherence validation
- **Hidden dependencies** - Complex import chains
- **System message pollution** - Uses anthropic SDK with hidden prompts

### ❌ Architectural Issues
- **Tight coupling** - Hard to extract individual components
- **Environment assumptions** - Hardcoded paths, specific directory structures
- **Configuration complexity** - Multiple config files and env vars
- **No isolation** - Components depend on each other

## Recommended Extraction Strategy

### Phase 1: Core File Operations (Immediate)
Build from scratch with formal contracts:
1. **File read/write** - With coherence validation
2. **Bash execution** - Safe shell commands with contracts
3. **Python execution** - Safe interpreter with formal validation

### Phase 2: Documentation Access
Extract and clean:
1. **Python stdlib parser** - Rewrite with formal contracts
2. **URL parser** - Simple HTTP-based parsing (no docling dependency)
3. **Search integration** - Direct API calls (no langchain)

### Phase 3: Code Analysis (Optional)
Build minimal version:
1. **Simple AST parsing** - Basic function/class detection
2. **Pattern matching** - Regex-based pattern detection
3. **Knowledge storage** - Simple JSON/SQLite with contracts

## Key Principles for Axiom Implementation

1. **Formal contracts first** - Every function must have coherence validation
2. **Minimal dependencies** - Direct API calls, no frameworks
3. **Test-driven development** - Write tests first, then implement
4. **Clean separation** - Each tool independent and composable
5. **No hidden behavior** - Complete transparency in all operations
6. **Fail-safe defaults** - Unknown conditions should fail, not pass

## Conclusion

The OM tool has useful functionality but needs complete rewrite with formal contracts to be truly coherent. The file operations and documentation access are the most valuable components to extract and rebuild properly.

**Priority**: Start with file operations (read/write/bash) as these are essential for building other coherent tools.