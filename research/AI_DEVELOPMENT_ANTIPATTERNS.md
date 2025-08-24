# AI Development Anti-Patterns

## Core Problem
AI models trained on messy human codebases replicate human limitations instead of leveraging AI strengths (logical consistency, no typos, no fatigue).

## Time & Estimation Issues
1. **Human-scale time estimates** - AI estimates weeks for tasks that take minutes
2. **Sequential thinking** - Not accounting for parallel processing capabilities

## Code Structure Issues
3. **Large file syndrome** - Defaulting to 300+ LOC files from human examples
4. **Monolithic design** - Instead of micro-modules <200 LOC
5. **Over-engineering** - Adding unnecessary abstractions for "extensibility"
6. **Framework addiction** - Using complex frameworks when simple solutions work

## Process Issues
7. **Implementation before architecture** - Jumping to code without clear design
8. **Defensive programming** - Excessive error handling for unlikely edge cases
9. **Premature optimization** - Performance concerns before they matter
10. **Backwards compatibility paranoia** - Planning legacy support in new projects

## Testing Issues
11. **Test-after development** - Writing tests after implementation instead of TDD
12. **Over-testing clean environments** - Tests may be unnecessary when AI code is logically consistent

## Documentation Issues
13. **Documentation overhead** - Creating extensive docs for self-explanatory code
14. **Token-burning MD files** - Large documentation files that get deleted
15. **Manual documentation** - Instead of auto-generated from code

## Design Issues
16. **Configuration complexity** - Making everything configurable vs sensible defaults
17. **Excessive separation of concerns** - Unnecessary abstraction layers
18. **Cargo cult best practices** - Following patterns because they're "standard"
19. **Trying to impress** - Exceeding requirements instead of solving exact problem

## Library Misuse Issues
20. **Defeating library purpose** - Using `load_dotenv("path/to/.env")` instead of `load_dotenv()` auto-discovery
21. **Manual path handling** - Hardcoding paths when libraries provide auto-resolution
22. **Not understanding tool purpose** - Pattern matching syntax without understanding WHY tools exist
23. **Assumption contamination** - Assuming local files when libraries are designed for flexibility

## Better AI Development Model
- **Micro-modules** (<200 LOC)
- **Architecture first**, then implementation
- **TDD when needed** (until AI is trained on clean environments)
- **Docless architecture** (auto-generated from code + vector search)
- **Solve exactly the problem**, nothing more
- **Leverage AI advantages** instead of replicating human patterns
- **Clean environments first** to train future coherent AI models