# Axiom Development Roadmap

## Core Philosophy
**Axiom = Development tool** (PWA for coding)  
**MomoAI = Research project** (built WITH Axiom, not using it)

## Phase 2 Development Priorities

### 1. Formal Contract Integration ⭐⭐⭐
**Goal**: All Axiom-generated code uses formal contracts  
**Why**: Ensures consistency and prevents incoherent code generation  
**Implementation**: Force all AI responses to include `@contract_enforced` decorators

### 2. Essential Tools Expansion
**Current tools available**: WebSearch, WebFetch, Bash, Read/Write, Grep, Glob, Task, TodoWrite

**Missing critical tools needed:**
- **Vector code search** - Semantic search through codebase
- **Documentation access** - Live docs from URLs/APIs  
- **Test execution** - Run tests, show results
- **Git operations** - Commit, branch, status
- **Package management** - Install deps, check versions

### 3. Stage System Refinement
**Current**: Fixed 4-stage workflow  
**Needed**: Flexible workflow based on user type

**Stage Modes:**
- **Vision-only mode**: Most users just want implementation (default)
- **Full workflow**: Only when developers request architecture phase  
- **Interruptible implementation**: Developer can stop/redirect anytime during coding

### 4. Tool Structure Philosophy
**Problem**: TodoWrite tool is useful but needs better organization  
**Solution**: Think through tool categorization and workflow integration

### 5. Docless Architecture Implementation
**Pipeline**: Sphinx → DuckDB → Vector search  
**Goal**: Auto-generated searchable knowledge base  
**Benefit**: Zero maintenance documentation that stays current

## Technical Notes
- Keep micro-modules <200 LOC (following Vincent's standards)
- Use formal contracts for all functions
- TDD approach for reliable code
- No token-burning documentation files

## Integration with MomoAI
Axiom builds MomoAI components, then MomoAI operates independently for research.
Clear separation: Axiom = tool, MomoAI = research subject.