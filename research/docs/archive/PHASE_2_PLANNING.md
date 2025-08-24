# Axiom Phase 2 Development Plan

## Critical Priority Order

### 1. Formal Contract Integration ⭐⭐⭐
**Goal**: All AI-generated code uses formal contracts
**Implementation**: 
- Modify system prompts to always include `@contract_enforced` decorators
- Add contract validation before code execution
- Reject/regenerate responses without proper contracts

### 2. Essential Tool Expansion
**High Priority Tools:**
- **Vector code search** - Most requested developer feature
- **Git operations** - Essential for real development workflow  
- **Test execution** - Validation of generated code

**Medium Priority:**
- Documentation access
- Package management

### 3. Stage System Simplification
**New approach based on user research:**
- **Default**: Vision → Implementation (skip architecture for most users)
- **Developer mode**: Full 4-stage workflow when explicitly requested
- **Always interruptible**: Stop/redirect during any stage

### 4. Tool Organization Categories
**Structure for expanding tool set:**
- **File ops** (read, write, edit, list, delete)
- **Code ops** (search, test, analyze, format)  
- **System ops** (git, bash, packages, environment)
- **Research ops** (docs, web search, vector search)

## Current Issues to Address
- .env loading problem in startup script
- Import path issues (avoid sys.path.append anti-patterns)
- Contract system integration across all components

## Success Metrics
- All generated code includes formal contracts
- Seamless tool execution workflow
- Simplified user experience for non-developers
- Robust developer features for advanced users