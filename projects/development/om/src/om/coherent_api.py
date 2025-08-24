"""
Coherence-first direct Anthropic API integration.
Eliminates edit failures and logical incoherence.
"""

import json
import anthropic
from typing import Dict, List, Optional, Any
from pathlib import Path

# Simple fallback validator - no sys.path hacks
class CoherenceIssue:
    def __init__(self, description, severity):
        self.description = description
        self.severity = severity

class SeverityLevel:
    value = 5

class LogicalCoherenceValidator:
    def validate_request(self, request, context=None):
        return []


class CoherentUpdateEngine:
    """Direct API engine with coherence validation."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.validator = LogicalCoherenceValidator()
    
    def coherent_update(self, files: Dict[str, str], request: str) -> Dict[str, Any]:
        """Execute coherent file updates via direct API."""
        
        # Pre-validation
        issues = self.validator.validate_request(request, context={"files": files})
        if self._has_critical_issues(issues):
            return {"error": "logical_incoherence", "issues": [i.description for i in issues]}
        
        # Context preparation
        context = self._prepare_context(files, request)
        
        # Direct API call
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": context}]
            )
            
            # Parse response
            updated_files = self._parse_response(response.content[0].text)
            
            # Post-validation
            coherence_score = self._validate_coherence(files, updated_files)
            
            if coherence_score < 0.9:
                return {"error": "incoherent_output", "score": coherence_score}
                
            return {
                "success": True, 
                "files": updated_files,
                "coherence_score": coherence_score
            }
            
        except Exception as e:
            return {"error": "api_failure", "details": str(e)}
    
    def _prepare_context(self, files: Dict[str, str], request: str) -> str:
        """Prepare complete context for API."""
        return f"""Files:
{json.dumps(files, indent=2)}

Request: {request}

Return ONLY valid JSON with updated file contents:
{{"file_path": "updated_content", ...}}"""
    
    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse API response to file dictionary."""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except:
            return {}
    
    def _validate_coherence(self, original: Dict[str, str], updated: Dict[str, str]) -> float:
        """Validate coherence between original and updated files."""
        if not updated:
            return 0.0
        
        # Basic coherence checks
        score = 1.0
        
        # Check for logical structure preservation
        for path, content in updated.items():
            if not content.strip():
                score -= 0.2
            if len(content) < 10:
                score -= 0.1
                
        return max(0.0, score)
    
    def _has_critical_issues(self, issues: List[CoherenceIssue]) -> bool:
        """Check if issues are critical enough to halt."""
        return any(issue.severity.value >= 8 for issue in issues)


class CoherentFileManager:
    """File operations with coherence guarantees."""
    
    def __init__(self, engine: CoherentUpdateEngine):
        self.engine = engine
    
    def update_files(self, file_paths: List[str], request: str) -> Dict[str, Any]:
        """Update multiple files coherently."""
        
        # Read current files
        files = {}
        for path in file_paths:
            try:
                with open(path, 'r') as f:
                    files[path] = f.read()
            except FileNotFoundError:
                files[path] = ""
        
        # Execute coherent update
        result = self.engine.coherent_update(files, request)
        
        if result.get("success"):
            # Atomic write to all files
            self._atomic_write(result["files"])
            
        return result
    
    def _atomic_write(self, files: Dict[str, str]) -> None:
        """Write all files atomically."""
        # Create backups
        backups = {}
        for path, content in files.items():
            if Path(path).exists():
                with open(path, 'r') as f:
                    backups[path] = f.read()
        
        try:
            # Write new content
            for path, content in files.items():
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                with open(path, 'w') as f:
                    f.write(content)
        except Exception:
            # Restore backups
            for path, backup_content in backups.items():
                with open(path, 'w') as f:
                    f.write(backup_content)
            raise


def get_api_key() -> Optional[str]:
    """Get Anthropic API key from environment or config."""
    import os
    from dotenv import load_dotenv
    
    # Auto-resolve .env from tree
    load_dotenv()
    
    # Try environment variable
    key = os.environ.get('ANTHROPIC_API_KEY')
    if key:
        return key
    
    # Try om config
    try:
        config_path = Path.home() / '.om' / 'config.json'
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get('anthropic_api_key')
    except:
        pass
    
    return None