"""
Coverage reporting in various formats
"""

import json
from pathlib import Path
from typing import List

from .data_models import CoverageMetrics


class CoverageReporter:
    """Generates coverage reports in various formats."""
    
    def generate_text_report(self, metrics: CoverageMetrics) -> str:
        """Generate human-readable text report."""
        lines = [
            "Documentation Coverage Report",
            "=" * 40,
            f"Total Elements: {metrics.total_elements}",
            f"Documented: {metrics.documented_elements}",
            f"Coverage: {metrics.coverage_percentage:.1f}%",
            f"Quality Score: {metrics.quality_score}/10",
            ""
        ]
        
        if metrics.missing_docs:
            lines.extend([
                "Missing Documentation:",
                "-" * 25
            ])
            for missing in metrics.missing_docs[:10]:  # Limit to first 10
                lines.append(f"  {missing}")
            
            if len(metrics.missing_docs) > 10:
                lines.append(f"  ... and {len(metrics.missing_docs) - 10} more")
            lines.append("")
        
        if metrics.issues:
            lines.extend([
                "Quality Issues:",
                "-" * 15
            ])
            
            # Group issues by severity
            errors = [i for i in metrics.issues if i['severity'] == 'error']
            warnings = [i for i in metrics.issues if i['severity'] == 'warning']
            
            if errors:
                lines.append(f"Errors ({len(errors)}):")
                for issue in errors[:5]:  # Limit to first 5
                    lines.append(f"  {issue['element_name']}: {issue['description']}")
                if len(errors) > 5:
                    lines.append(f"  ... and {len(errors) - 5} more errors")
                lines.append("")
            
            if warnings:
                lines.append(f"Warnings ({len(warnings)}):")
                for issue in warnings[:5]:  # Limit to first 5
                    lines.append(f"  {issue['element_name']}: {issue['description']}")
                if len(warnings) > 5:
                    lines.append(f"  ... and {len(warnings) - 5} more warnings")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_json_report(self, metrics: CoverageMetrics) -> str:
        """Generate JSON report."""
        from dataclasses import asdict
        return json.dumps(asdict(metrics), indent=2)
    
    def generate_html_report(self, metrics: CoverageMetrics) -> str:
        """Generate HTML report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Documentation Coverage Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .issues {{ margin: 20px 0; }}
                .error {{ color: #d32f2f; }}
                .warning {{ color: #f57c00; }}
                .good {{ color: #388e3c; }}
            </style>
        </head>
        <body>
            <h1>Documentation Coverage Report</h1>
            
            <div class="metric">
                <h2>Coverage Metrics</h2>
                <p>Total Elements: {metrics.total_elements}</p>
                <p>Documented Elements: {metrics.documented_elements}</p>
                <p>Coverage: <span class="{'good' if metrics.coverage_percentage >= 80 else 'warning'}">{metrics.coverage_percentage:.1f}%</span></p>
                <p>Quality Score: <span class="{'good' if metrics.quality_score >= 7 else 'warning'}">{metrics.quality_score}/10</span></p>
            </div>
        """
        
        if metrics.missing_docs:
            html += """
            <div class="issues">
                <h3>Missing Documentation</h3>
                <ul>
            """
            for missing in metrics.missing_docs[:20]:  # Limit for HTML
                html += f"<li>{missing}</li>"
            html += "</ul></div>"
        
        if metrics.issues:
            html += """
            <div class="issues">
                <h3>Quality Issues</h3>
                <ul>
            """
            for issue in metrics.issues[:20]:  # Limit for HTML
                severity_class = issue['severity']
                html += f'<li class="{severity_class}">{issue["element_name"]}: {issue["description"]}</li>'
            html += "</ul></div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def save_report(self, metrics: CoverageMetrics, output_path: Path, format_type: str = "text"):
        """Save report to file."""
        if format_type == "json":
            content = self.generate_json_report(metrics)
        elif format_type == "html":
            content = self.generate_html_report(metrics)
        else:
            content = self.generate_text_report(metrics)
        
        with open(output_path, 'w') as f:
            f.write(content)
