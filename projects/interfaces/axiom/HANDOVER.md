# Axiom Development Handover

## Current Status

**Working System:**
- Basic chat interface with Claude Sonnet 4
- Function calling system with `read_file()` tool
- Comprehensive error handling and logging
- Static frontend serving

## Implementation Complete

### 1. Function Calling Architecture
- Claude responds with natural Python syntax: `read_file('/absolute/path')`
- Backend parses with regex: `r"read_file\(['\"]([^'\"]+)['\"]\)"`
- Executes identical function to system message definition
- Returns processed results to Claude for analysis

### 2. System Message Structure
```python
# Complete function definitions in system_message.txt
def read_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()
```
- No descriptions needed - function name + code = complete understanding
- Ensures coherence between Claude's understanding and backend implementation

### 3. Error Handling
- Comprehensive logging throughout
- Graceful degradation on failures
- Specific error messages instead of generic 500s
- Security: Path validation prevents directory traversal

## Technical Decisions Made

### Path Strategy
**Decision:** Absolute paths only (`/full/path/to/file`)
**Reason:** No hidden state, always unambiguous, prevents incoherence

### Function Definition Strategy  
**Decision:** Complete functions in system message
**Reason:** True coherence - Claude knows exactly what happens, no interpretation gaps

### Tool Calling Strategy
**Decision:** Natural Python syntax over JSON schemas
**Reason:** Coherent with how functions actually work, easier to validate

## Current Limitations

1. Only `read_file()` tool implemented
2. File access restricted to project directory
3. No dynamic tool creation yet
4. In-memory message storage only

## Next Logical Steps

1. **Test more files** - Verify system works across different file types
2. **Add second tool** - Follow same pattern (complete function in system message)
3. **Dynamic tool creation** - Long-term goal for self-expanding capabilities

## Files Modified

- `backend/main.py` - Added function calling, error handling
- `backend/system_message.txt` - Added read_file function definition  
- `backend/models.py` - Enhanced validation
- `README.md` - Fixed to match reality (removed false claims)

## Critical Notes

- System IS working correctly - Claude reads files and provides analysis
- Take small incremental steps - avoid feature creep
- Maintain coherence between system message and backend implementation
- All documentation must match implementation reality