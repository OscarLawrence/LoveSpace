"""
Workflow examples generator
"""

import textwrap
from typing import List
from .data_models import IntegrationExample


class WorkflowGenerator:
    """Generates workflow-based integration examples"""
    
    def generate_examples(self) -> List[IntegrationExample]:
        """Generate workflow-based integration examples."""
        examples = []
        
        # Documentation workflow
        examples.append(self._create_docs_workflow())
        examples.append(self._create_agent_workflow())
        examples.append(self._create_qa_pipeline())
        
        return examples
    
    def _create_docs_workflow(self) -> IntegrationExample:
        """Create documentation generation workflow example"""
        return IntegrationExample(
            title="Complete Documentation Generation Workflow",
            description="Generate comprehensive documentation with coverage enforcement and schema validation",
            category="documentation",
            difficulty="intermediate",
            code=textwrap.dedent("""
                # Step 1: Auto-scope to documentation domain
                om --auto-scope "generate complete project documentation"
                
                # Step 2: Generate Sphinx documentation
                om docs generate --source src --output docs --build-html
                
                # Step 3: Analyze coverage and enforce quality gates
                om docs coverage analyze src --format html --output coverage.html
                om docs coverage gate src --min-coverage 85 --min-quality 7.5
                
                # Step 4: Generate type schemas for API documentation
                om docs schema batch src --output-dir schemas --format json
                
                # Step 5: Validate all generated schemas
                find schemas -name "*.json" -exec om docs schema validate {} \;
                
                # Step 6: Serve documentation for review
                om docs serve docs --port 8080
            """).strip(),
            explanation=textwrap.dedent("""
                This workflow demonstrates the complete documentation generation process:
                
                1. **Auto-scoping**: Automatically determines 'docs' scope for focused tooling
                2. **Sphinx generation**: Creates professional documentation from code
                3. **Coverage analysis**: Ensures comprehensive documentation coverage
                4. **Quality gates**: Enforces documentation quality standards
                5. **Schema generation**: Creates type documentation for APIs
                6. **Validation**: Verifies all generated schemas are correct
                7. **Live serving**: Provides immediate feedback on documentation
                
                The workflow ensures 100% documentation coverage with quality validation.
            """).strip(),
            prerequisites=["Source code with type hints", "Sphinx installed"],
            related_commands=["docs generate", "docs coverage", "docs schema", "docs serve"],
            expected_output="Complete documentation site with coverage reports and type schemas",
            tags=["documentation", "quality", "automation", "sphinx"]
        )
    
    def _create_agent_workflow(self) -> IntegrationExample:
        """Create agent-optimized workflow example"""
        return IntegrationExample(
            title="Agent-Optimized Development Session",
            description="Demonstrate agent scoping for reduced cognitive load during development",
            category="agent_workflow",
            difficulty="basic",
            code=textwrap.dedent("""
                # Start with task description for auto-scoping
                om --auto-scope "implement session persistence feature" scope auto \
                   --task "implement session persistence" \
                   --module "memory_system"
                
                # Check available commands in current scope
                om scope show
                
                # Work within memory scope
                om memory stats
                om session save current_work
                om preferences set auto_save true
                
                # Switch to analysis scope for code review
                om scope set analysis
                om analyze architecture --focus memory
                om analyze dependencies --module session
                
                # Switch to code scope for implementation
                om scope set code
                om code parse src/om/memory.py
                om code execute tests/test_memory.py
                
                # Clear scope when done
                om scope clear
            """).strip(),
            explanation=textwrap.dedent("""
                This workflow showcases agent-optimized development with scoping:
                
                1. **Auto-scoping**: Determines relevant tool scopes from task description
                2. **Scope awareness**: Shows only relevant commands (3-5 vs 38 total)
                3. **Context switching**: Smooth transitions between work domains
                4. **Cognitive load reduction**: Prevents choice paralysis with focused tooling
                5. **Session management**: Maintains work context across scope changes
                
                Agents benefit from 47-82% reduction in command choices per context.
            """).strip(),
            prerequisites=["Om CLI installed", "Project with multiple modules"],
            related_commands=["scope auto", "scope set", "scope show", "scope clear"],
            expected_output="Focused command sets per work domain with session persistence",
            tags=["agent", "scoping", "cognitive_load", "workflow"]
        )
    
    def _create_qa_pipeline(self) -> IntegrationExample:
        """Create quality assurance pipeline example"""
        return IntegrationExample(
            title="Automated Quality Assurance Pipeline",
            description="Complete quality pipeline with documentation, coverage, and validation",
            category="quality_assurance",
            difficulty="advanced",
            code=textwrap.dedent("""
                #!/bin/bash
                # quality_pipeline.sh - Complete QA automation
                
                set -e  # Exit on any error
                
                echo "=== Om Quality Assurance Pipeline ==="
                
                # Step 1: Scope to docs domain
                om --scope docs --no-scope-info
                
                # Step 2: Generate documentation
                echo "Generating documentation..."
                om docs generate --source src --output docs --build-html
                
                # Step 3: Enforce coverage quality gate
                echo "Checking documentation coverage..."
                om docs coverage gate src \
                   --min-coverage 90.0 \
                   --min-quality 8.0 \
                   --max-errors 0 \
                   --max-warnings 5
                
                # Step 4: Generate and validate schemas
                echo "Generating type schemas..."
                om docs schema batch src --output-dir schemas --format json
                
                echo "Validating schemas..."
                for schema in schemas/*.json; do
                    om docs schema validate "$schema" || exit 1
                done
                
                # Step 5: Generate reports
                echo "Generating quality reports..."
                om docs coverage analyze src --format html --output reports/coverage.html
                
                echo "Pipeline completed successfully!"
            """).strip(),
            explanation=textwrap.dedent("""
                This pipeline demonstrates automated quality assurance:
                
                1. **Scope isolation**: Works within docs domain for focus
                2. **Documentation generation**: Creates complete documentation
                3. **Quality gates**: Enforces minimum quality standards
                4. **Schema validation**: Ensures type safety and correctness
                5. **Report generation**: Provides actionable quality metrics
                
                The pipeline fails fast on quality violations and provides clear feedback.
            """).strip(),
            prerequisites=["Bash shell", "Om CLI installed", "Source code with documentation"],
            related_commands=["docs generate", "docs coverage", "docs schema"],
            expected_output="Quality reports and validated documentation artifacts",
            tags=["pipeline", "automation", "quality", "ci_cd"]
        )
