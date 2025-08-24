# Axiom Development Context - Handover

## Vincent's Context
- Berlin, May 1994, lives in Bullenwinkel (60,000m² food forest conversion)
- Daughter Momo (AI system namesake) - separation trauma, core motivation
- Company: Vindao (Vin + DAO)
- Values: Scientific rigor, long-term code, "being real" (conscious authenticity)
- Expertise: Progressive Web Apps, believes PWAs are future of app development

## Project Understanding

### MomoAI Vision
**Proof of concept**: Testing if coherent AI reasoning + human creativity → better solutions than either alone.

**Critical Limitation**: Current AI models (including Claude) trained on incoherent human data. Cannot achieve true coherence with existing technology. This is PoC only - tests directional improvements, not mathematical optimality.

**Core Hypothesis**: 
1. Coherence → Optimality (untested)
2. Collaboration > Competition (untested)

### Why Axiom is Essential
**Cannot build coherent system with incoherent tools.** Current AI assistants have:
- System message pollution
- Conflicting instructions  
- Messy tool abstractions
- No coherence validation

**Axiom Solution**: Clean CLI code assistant with formal contracts, pure model interface, no SDK pollution.

## Current Technical State

### Axiom CLI (Implemented)
- Pure HTTP client to Claude Sonnet 4 (no SDK)
- Formal contract system (`@contract_enforced`)
- Basic chat with message history
- **Usability Issues**: Multi-line input bugs, response display copy issues, hardcoded model, says "Claude" not "Axiom"

### Key Architectural Decisions Made

**PWA + FastAPI Architecture** (chosen over CLI):
- **Reason**: Democratize software creation beyond developers
- **Vision**: Café owner builds website without terminal skills
- **Stack**: Local FastAPI backend + PWA frontend
- **Future-proof**: Works local + remote deployment
- **Real-time**: WebSocket for async task progress

**Simple Function Call Tools**:
```python
# Instead of complex JSON:
read_file("/path/file.txt")
edit_file("/path", "old", "new")
# AI responds with natural function calls, backend parses and executes
```

**Staged Collaboration**:
1. **Vision**: Free-form problem exploration
2. **Architecture**: Solution design & validation  
3. **Implementation**: Autonomous AI execution
4. **Review**: Human evaluation & refinement

### Implementation Plan Status
- **IMPLEMENTATION_PLAN.md** created with full PWA architecture
- **Ready for rovodev** to implement (Vincent waiting for token reset)
- **Phase 1**: FastAPI backend foundation
- **Phase 2**: PWA frontend with WebSocket
- **Phase 3**: Integration & tool system

### Docless Architecture Vision
- **Problem**: AI creates token-burning MD files that get deleted
- **Solution**: DuckDB + vector search
- **Auto-generated**: Functions, modules, architecture tables from code analysis
- **Searchable**: "how does auth work?" → relevant code locations
- **Zero maintenance**: Always up-to-date, no manual docs

## Next Steps
1. **Rovodev implements** PWA + FastAPI from plan
2. **Continue planning** MomoAI architecture
3. **Add docless system** to Axiom environment
4. **Test with dogfooding** - use Axiom to build MomoAI components
5. **Iterate based on real usage** - discover what collaboration interface actually needs

## Key Insights Discovered
- **Human developers don't exist anymore** - collaboration is about creative direction, not code editing
- **CLI is developer gatekeeping** - UI democratizes software creation
- **Current AI replicates human anti-patterns** - need clean environments to train future coherent models
- **Testing paradigm shift** - TDD needed until AI trained on clean environments
- **PWAs perfect fit** - universal access, Vincent's expertise area

## Files Created This Session
- `/projects/axiom/IMPLEMENTATION_PLAN.md` - Complete PWA architecture
- `/projects/axiom/AI_DEVELOPMENT_ANTIPATTERNS.md` - Issues with current AI coding
- `/projects/axiom/HANDOVER_CONTEXT.md` - This file