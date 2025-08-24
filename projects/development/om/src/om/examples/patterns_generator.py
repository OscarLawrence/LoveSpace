"""
Integration patterns generator
"""

import textwrap
from typing import List
from .data_models import IntegrationExample


class PatternsGenerator:
    """Generates common integration patterns"""
    
    def generate_examples(self) -> List[IntegrationExample]:
        """Generate common integration patterns."""
        examples = []
        
        examples.append(self._create_cli_integration())
        examples.append(self._create_api_integration())
        examples.append(self._create_ci_integration())
        
        return examples
    
    def _create_cli_integration(self) -> IntegrationExample:
        """Create CLI integration pattern example"""
        return IntegrationExample(
            title="Custom CLI Integration Pattern",
            description="Integrate Om documentation generation into custom CLI tools",
            category="integration",
            difficulty="intermediate",
            code=textwrap.dedent("""
                # custom_cli.py - Integrate Om into custom tools
                import click
                import subprocess
                from pathlib import Path
                
                @click.group()
                def cli():
                    \"\"\"Custom CLI with Om integration.\"\"\"
                    pass
                
                @cli.command()
                @click.option('--source', default='src', help='Source directory')
                @click.option('--quality-gate', is_flag=True, help='Enforce quality gate')
                def docs(source, quality_gate):
                    \"\"\"Generate documentation using Om.\"\"\"
                    
                    # Generate documentation
                    result = subprocess.run([
                        'om', 'docs', 'generate', 
                        '--source', source,
                        '--output', 'docs',
                        '--build-html'
                    ], capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        click.echo(f\"Documentation generation failed: {result.stderr}\")
                        return
                    
                    click.echo(\"Documentation generated successfully\")
                    
                    # Optional quality gate
                    if quality_gate:
                        gate_result = subprocess.run([
                            'om', 'docs', 'coverage', 'gate', source,
                            '--min-coverage', '80'
                        ], capture_output=True, text=True)
                        
                        if gate_result.returncode == 0:
                            click.echo(\"✓ Quality gate passed\")
                        else:
                            click.echo(\"✗ Quality gate failed\")
                            click.echo(gate_result.stdout)
                
                @cli.command()
                def validate_schemas():
                    \"\"\"Validate all generated schemas.\"\"\"
                    schemas_dir = Path('schemas')
                    
                    if not schemas_dir.exists():
                        click.echo(\"No schemas directory found\")
                        return
                    
                    for schema_file in schemas_dir.glob('*.json'):
                        result = subprocess.run([
                            'om', 'docs', 'schema', 'validate', str(schema_file)
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            click.echo(f\"✓ {schema_file.name}\")
                        else:
                            click.echo(f\"✗ {schema_file.name}: {result.stderr}\")
                
                if __name__ == '__main__':
                    cli()
            """).strip(),
            explanation=textwrap.dedent("""
                This pattern shows how to integrate Om into custom CLI tools:
                
                1. **Subprocess integration**: Call Om commands from Python
                2. **Error handling**: Proper error checking and reporting
                3. **Quality gates**: Optional quality enforcement
                4. **Batch operations**: Process multiple files/schemas
                5. **User feedback**: Clear success/failure indicators
                
                Enables embedding Om's documentation capabilities in larger tools.
            """).strip(),
            prerequisites=["Click library", "Om CLI installed"],
            related_commands=["docs generate", "docs coverage gate", "docs schema validate"],
            expected_output="Custom CLI with integrated Om documentation features",
            tags=["integration", "cli", "subprocess", "custom_tools"]
        )
    
    def _create_api_integration(self) -> IntegrationExample:
        """Create API integration pattern example"""
        return IntegrationExample(
            title="Programmatic API Integration",
            description="Use Om components programmatically in Python applications",
            category="integration",
            difficulty="advanced",
            code=textwrap.dedent("""
                # api_integration.py - Programmatic Om usage
                from pathlib import Path
                from typing import Dict, List, Any
                
                try:
                    from om.docs.coverage_analyzer import CoverageAnalyzer
                    from om.docs.sphinx_builder import SphinxBuilder
                    from om.docs.schema_generator import SchemaGenerator
                except ImportError:
                    print(\"Om modules not available - using mock implementations\")
                    # Mock implementations for demonstration
                    
                    class CoverageAnalyzer:
                        def analyze_directory(self, path): return {\"coverage\": 0.85}
                    
                    class SphinxBuilder:
                        def build_docs(self, source, output): return True
                    
                    class SchemaGenerator:
                        def generate_schemas(self, source): return [\"schema1.json\"]
                
                class DocumentationService:
                    \"\"\"Service for automated documentation generation.\"\"\"
                    
                    def __init__(self):
                        self.coverage_analyzer = CoverageAnalyzer()
                        self.sphinx_builder = SphinxBuilder()
                        self.schema_generator = SchemaGenerator()
                    
                    def generate_complete_docs(self, source_dir: Path, 
                                             output_dir: Path) -> Dict[str, Any]:
                        \"\"\"Generate complete documentation with analysis.\"\"\"
                        results = {
                            \"success\": False,
                            \"coverage\": {},
                            \"docs_built\": False,
                            \"schemas_generated\": [],
                            \"errors\": []
                        }
                        
                        try:
                            # Step 1: Analyze coverage
                            coverage = self.coverage_analyzer.analyze_directory(source_dir)
                            results[\"coverage\"] = coverage
                            
                            # Step 2: Build documentation
                            docs_success = self.sphinx_builder.build_docs(
                                source_dir, output_dir
                            )
                            results[\"docs_built\"] = docs_success
                            
                            # Step 3: Generate schemas
                            schemas = self.schema_generator.generate_schemas(source_dir)
                            results[\"schemas_generated\"] = schemas
                            
                            results[\"success\"] = (
                                docs_success and 
                                coverage.get(\"coverage\", 0) > 0.8
                            )
                            
                        except Exception as e:
                            results[\"errors\"].append(str(e))
                        
                        return results
                
                # Usage example
                if __name__ == \"__main__\":
                    service = DocumentationService()
                    result = service.generate_complete_docs(
                        Path(\"src\"), Path(\"docs\")
                    )
                    
                    print(f\"Success: {result['success']}\")
                    print(f\"Coverage: {result['coverage']}\")
                    print(f\"Schemas: {len(result['schemas_generated'])}\")
            """).strip(),
            explanation=textwrap.dedent("""
                This pattern demonstrates programmatic Om usage:
                
                1. **Direct API usage**: Import and use Om components directly
                2. **Service abstraction**: Wrap Om functionality in services
                3. **Error handling**: Comprehensive error management
                4. **Result aggregation**: Combine multiple operations
                5. **Fallback handling**: Graceful degradation when modules unavailable
                
                Enables embedding Om in larger applications and services.
            """).strip(),
            prerequisites=["Om Python modules", "Python application framework"],
            related_commands=["docs coverage", "docs generate", "docs schema"],
            expected_output="Integrated documentation service with programmatic control",
            tags=["api", "programmatic", "service", "integration"]
        )
    
    def _create_ci_integration(self) -> IntegrationExample:
        """Create CI/CD integration pattern example"""
        return IntegrationExample(
            title="CI/CD Pipeline Integration",
            description="Integrate Om into continuous integration workflows",
            category="integration",
            difficulty="intermediate",
            code=textwrap.dedent("""
                # .github/workflows/docs.yml - GitHub Actions integration
                name: Documentation Quality Check
                
                on:
                  push:
                    branches: [ main, develop ]
                  pull_request:
                    branches: [ main ]
                
                jobs:
                  docs-quality:
                    runs-on: ubuntu-latest
                    
                    steps:
                    - uses: actions/checkout@v3
                    
                    - name: Set up Python
                      uses: actions/setup-python@v4
                      with:
                        python-version: '3.11'
                    
                    - name: Install dependencies
                      run: |
                        pip install om-cli sphinx
                    
                    - name: Generate documentation
                      run: |
                        om docs generate --source src --output docs --build-html
                    
                    - name: Check documentation coverage
                      run: |
                        om docs coverage gate src \
                          --min-coverage 85.0 \
                          --min-quality 7.5 \
                          --max-errors 0
                    
                    - name: Generate and validate schemas
                      run: |
                        om docs schema batch src --output-dir schemas --format json
                        find schemas -name \"*.json\" -exec om docs schema validate {} \;
                    
                    - name: Upload documentation artifacts
                      uses: actions/upload-artifact@v3
                      if: success()
                      with:
                        name: documentation
                        path: |
                          docs/
                          schemas/
                    
                    - name: Comment PR with coverage
                      if: github.event_name == 'pull_request'
                      run: |
                        coverage=$(om docs coverage analyze src --format json | jq '.coverage')
                        echo \"Documentation coverage: $coverage%\" >> $GITHUB_STEP_SUMMARY
            """).strip(),
            explanation=textwrap.dedent("""
                This pattern shows CI/CD integration:
                
                1. **Automated validation**: Documentation quality checked on every push
                2. **Quality gates**: Fail builds on coverage/quality violations
                3. **Artifact generation**: Store documentation and schemas
                4. **PR feedback**: Report coverage in pull request comments
                5. **Multi-format output**: Generate both HTML docs and JSON schemas
                
                Ensures documentation quality is maintained across development.
            """).strip(),
            prerequisites=["GitHub Actions", "Om CLI in CI environment"],
            related_commands=["docs generate", "docs coverage gate", "docs schema batch"],
            expected_output="Automated documentation quality enforcement in CI/CD",
            tags=["ci_cd", "github_actions", "automation", "quality_gates"]
        )
