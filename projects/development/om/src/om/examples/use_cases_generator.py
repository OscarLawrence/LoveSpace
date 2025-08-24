"""
Use case examples generator
"""

import textwrap
from typing import List
from .data_models import IntegrationExample


class UseCasesGenerator:
    """Generates specific use case examples"""
    
    def generate_examples(self) -> List[IntegrationExample]:
        """Generate specific use case examples."""
        examples = []
        
        examples.append(self._create_open_source_setup())
        examples.append(self._create_enterprise_setup())
        examples.append(self._create_library_docs())
        
        return examples
    
    def _create_open_source_setup(self) -> IntegrationExample:
        """Create open source project setup example"""
        return IntegrationExample(
            title="Open Source Project Documentation Setup",
            description="Complete documentation setup for open source Python projects",
            category="use_case",
            difficulty="basic",
            code=textwrap.dedent("""
                # setup_docs.sh - Open source project documentation setup
                
                echo "Setting up documentation for open source project..."
                
                # Step 1: Initialize documentation structure
                mkdir -p docs schemas reports
                
                # Step 2: Generate initial documentation
                om docs generate \
                   --source src \
                   --output docs \
                   --patterns "**/*.py" \
                   --build-html
                
                # Step 3: Set up quality standards (relaxed for open source)
                om docs coverage init-config quality_gate.json \
                   --min-coverage 70 \
                   --min-quality 6.0 \
                   --max-errors 5 \
                   --max-warnings 20
                
                # Step 4: Generate type documentation for API users
                om docs schema batch src \
                   --output-dir schemas \
                   --format json
                
                # Step 5: Generate GitHub Pages compatible structure
                echo "baseurl: /your-project" > docs/_config.yml
                echo "theme: minima" >> docs/_config.yml
                
                # Step 6: Create documentation badge data
                om docs coverage analyze src --format json --output reports/coverage.json
                
                echo "Documentation setup complete!"
                echo "- Docs: docs/_build/html/index.html"
                echo "- Schemas: schemas/"
                echo "- Quality config: quality_gate.json"
            """).strip(),
            explanation=textwrap.dedent("""
                This setup is optimized for open source projects:
                
                1. **Relaxed standards**: Lower coverage requirements for community projects
                2. **API documentation**: Type schemas help library users
                3. **GitHub Pages**: Compatible structure for free hosting
                4. **Badge integration**: Coverage data for README badges
                5. **Community friendly**: Clear documentation for contributors
                
                Balances quality with open source project realities.
            """).strip(),
            prerequisites=["Python project", "GitHub repository"],
            related_commands=["docs generate", "docs coverage", "docs schema"],
            expected_output="Complete documentation site ready for GitHub Pages",
            tags=["open_source", "github_pages", "community", "api_docs"]
        )
    
    def _create_enterprise_setup(self) -> IntegrationExample:
        """Create enterprise project setup example"""
        return IntegrationExample(
            title="Enterprise Documentation Standards",
            description="High-quality documentation setup for enterprise environments",
            category="use_case",
            difficulty="advanced",
            code=textwrap.dedent("""
                # enterprise_setup.sh - Enterprise documentation standards
                
                echo "Setting up enterprise documentation standards..."
                
                # Step 1: Strict quality configuration
                om docs coverage init-config enterprise_quality.json \
                   --min-coverage 95.0 \
                   --min-quality 9.0 \
                   --max-errors 0 \
                   --max-warnings 2
                
                # Step 2: Generate comprehensive documentation
                om docs generate \
                   --source src \
                   --output docs \
                   --include-private \
                   --build-html \
                   --build-pdf
                
                # Step 3: Enforce quality gate
                om docs coverage gate src \
                   --config enterprise_quality.json \
                   --fail-on-violations
                
                # Step 4: Generate complete API schemas
                om docs schema batch src \
                   --output-dir api_schemas \
                   --format json \
                   --include-private \
                   --validate-all
                
                # Step 5: Generate compliance reports
                om docs coverage analyze src \
                   --format html \
                   --output compliance/coverage_report.html \
                   --include-metrics
                
                # Step 6: Create security documentation
                om docs security-scan src \
                   --output security/security_report.html
                
                echo "Enterprise documentation setup complete!"
                echo "All quality gates passed - ready for production"
            """).strip(),
            explanation=textwrap.dedent("""
                Enterprise setup enforces strict quality standards:
                
                1. **High coverage**: 95% documentation coverage required
                2. **Quality enforcement**: 9.0/10 minimum quality score
                3. **Comprehensive docs**: Include private APIs and generate PDF
                4. **Compliance reports**: Detailed metrics for auditing
                5. **Security scanning**: Documentation security analysis
                6. **Zero tolerance**: Fail builds on quality violations
                
                Ensures enterprise-grade documentation quality.
            """).strip(),
            prerequisites=["Enterprise environment", "Compliance requirements"],
            related_commands=["docs coverage gate", "docs generate", "docs security-scan"],
            expected_output="Enterprise-grade documentation with compliance reports",
            tags=["enterprise", "compliance", "quality", "security"]
        )
    
    def _create_library_docs(self) -> IntegrationExample:
        """Create library documentation example"""
        return IntegrationExample(
            title="Python Library API Documentation",
            description="Comprehensive API documentation for Python libraries",
            category="use_case",
            difficulty="intermediate",
            code=textwrap.dedent("""
                # library_docs.sh - Python library API documentation
                
                echo "Generating comprehensive library documentation..."
                
                # Step 1: Generate API documentation with examples
                om docs generate \
                   --source src \
                   --output api_docs \
                   --api-mode \
                   --include-examples \
                   --build-html
                
                # Step 2: Generate interactive API schemas
                om docs schema batch src \
                   --output-dir schemas \
                   --format openapi \
                   --interactive
                
                # Step 3: Create usage examples
                om docs examples generate src \
                   --output examples \
                   --include-notebooks
                
                # Step 4: Generate package documentation
                om docs package src \
                   --output package_docs \
                   --include-changelog \
                   --include-installation
                
                # Step 5: Create API reference
                om docs api-reference src \
                   --output reference \
                   --group-by-module \
                   --include-source-links
                
                # Step 6: Build unified documentation site
                om docs combine \
                   --inputs api_docs examples package_docs reference \
                   --output unified_docs \
                   --theme library
                
                echo "Library documentation complete!"
                echo "- API docs: unified_docs/"
                echo "- Schemas: schemas/"
                echo "- Examples: examples/"
            """).strip(),
            explanation=textwrap.dedent("""
                Library documentation focuses on API usability:
                
                1. **API-first**: Generated documentation optimized for API usage
                2. **Interactive schemas**: OpenAPI specs with interactive testing
                3. **Usage examples**: Real code examples and Jupyter notebooks
                4. **Package info**: Installation, changelog, and package details
                5. **Reference docs**: Complete API reference with source links
                6. **Unified site**: Combined documentation in library theme
                
                Creates comprehensive documentation for library users.
            """).strip(),
            prerequisites=["Python library", "Type hints", "Docstrings"],
            related_commands=["docs generate", "docs schema", "docs examples"],
            expected_output="Complete library documentation with API reference",
            tags=["library", "api", "examples", "reference"]
        )
