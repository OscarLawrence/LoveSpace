# MomoAI Monorepo Structure

## Overview

This monorepo contains all components of the MomoAI proof of concept system, organized by functional domains.

## Project Structure

### Core Components
- **`core/knowledge/`** - Knowledge representation and management
- **`core/protocols/`** - Communication protocols and interfaces

### Parsers
- **`parsers/docs-parser/`** - Documentation parsing and analysis
- **`parsers/code-parser/`** - Code parsing and analysis

### Tools
- **`tools/om/`** - Operational management tools

### Bootstrap Components
- **`axiom/`** - Clean CLI code assistant with coherent tools (Phase 1 bootstrap)
- **`coherence/`** - Coherence validation and monitoring engine

### Main System
- **`momo/interface/`** - Chat interface with dual-mode human input routing
- **`momo/cycles/`** - Four autonomous AI cycles:
  - Problem Identification Cycle
  - Solution Generation Cycle  
  - Implementation Cycle
  - Optimization Cycle

## Development Workflow

1. **Phase 1**: Build Axiom (clean CLI assistant)
2. **Phase 2**: Use Axiom to build coherence validation tools
3. **Phase 3**: Implement the four autonomous cycles
4. **Phase 4**: Build Momo interface and connect all components

## Dependencies

Each project is independently managed with its own `pyproject.toml`. Use `uv` for workspace management:

```bash
# Install all workspace dependencies
uv sync

# Work on specific project
cd projects/axiom
uv run python -m pytest
```