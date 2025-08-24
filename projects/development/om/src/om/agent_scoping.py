"""Agent Tool Scoping System.

Reduces agent cognitive load by filtering available tools based on task context.
Maintains logical coherence through domain-focused tool sets.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import re
import json
from datetime import datetime


@dataclass
class ScopeContext:
    """Context information for scope determination."""
    command: str
    args: List[str]
    task_description: str
    current_module: Optional[str] = None
    command_history: List[str] = None
    
    def __post_init__(self):
        if self.command_history is None:
            self.command_history = []


@dataclass
class ScopeResult:
    """Result of scope determination."""
    scopes: List[str]
    confidence: float
    reasoning: str
    filtered_commands: List[str]


class AutoScoper:
    """Automatically determines appropriate tool scopes based on context."""
    
    def __init__(self):
        self.scope_patterns = {
            "docs": [
                r"document|doc|help|reference|api|guide",
                r"sphinx|generate.*docs|auto.*doc",
                r"coverage|lint.*doc|validate.*doc"
            ],
            "memory": [
                r"session|remember|recall|context|state",
                r"preference|setting|config|persist",
                r"feedback|learn|adapt|improve"
            ],
            "analysis": [
                r"analyze|examine|inspect|review|audit",
                r"architecture|dependency|pattern|gap",
                r"metric|benchmark|performance|quality"
            ],
            "code": [
                r"parse|extract|function|class|method",
                r"execute|run|test|validate|check",
                r"find|search|locate|discover"
            ],
            "parsing": [
                r"populate.*pattern|pattern.*library",
                r"module.*isolation|workspace.*setup",
                r"scaffold|template|generate.*code"
            ]
        }
        
        self.command_scope_map = {
            # Docs domain
            "docs": ["docs"],
            "python": ["docs"],
            
            # Memory domain  
            "memory": ["memory"],
            "session": ["memory"],
            "preferences": ["memory"],
            "isolate": ["memory"],
            
            # Analysis domain
            "analyze": ["analysis"],
            "context": ["analysis", "memory"],
            
            # Code domain
            "code": ["code"],
            "find": ["code"],
            
            # Parsing domain
            "populate-patterns": ["parsing"],
            "modules": ["parsing"],
            "scaffold": ["parsing"],
            "workspace": ["parsing"]
        }
    
    def determine_scope(self, context: ScopeContext) -> ScopeResult:
        """Determine appropriate scopes for given context."""
        scopes = set()
        confidence_scores = {}
        reasoning_parts = []
        
        # 1. Direct command mapping
        base_command = context.command.split()[0] if context.command else ""
        if base_command in self.command_scope_map:
            direct_scopes = self.command_scope_map[base_command]
            scopes.update(direct_scopes)
            confidence_scores.update({s: 0.9 for s in direct_scopes})
            reasoning_parts.append(f"direct_map:{base_command}→{direct_scopes}")
        
        # 2. Pattern-based detection
        full_text = f"{context.command} {' '.join(context.args)} {context.task_description}"
        for scope, patterns in self.scope_patterns.items():
            for pattern in patterns:
                if re.search(pattern, full_text, re.IGNORECASE):
                    scopes.add(scope)
                    confidence_scores[scope] = max(confidence_scores.get(scope, 0), 0.7)
                    reasoning_parts.append(f"pattern:{scope}:{pattern}")
        
        # 3. Module context influence
        if context.current_module:
            module_scopes = self._infer_module_scopes(context.current_module)
            scopes.update(module_scopes)
            confidence_scores.update({s: confidence_scores.get(s, 0) + 0.3 for s in module_scopes})
            reasoning_parts.append(f"module:{context.current_module}→{module_scopes}")
        
        # 4. Command history analysis
        if context.command_history:
            history_scopes = self._analyze_command_history(context.command_history)
            scopes.update(history_scopes)
            confidence_scores.update({s: confidence_scores.get(s, 0) + 0.2 for s in history_scopes})
            reasoning_parts.append(f"history→{history_scopes}")
        
        # Calculate overall confidence
        final_scopes = list(scopes)
        avg_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.5
        
        # Get filtered commands
        filtered_commands = self._get_scoped_commands(final_scopes)
        
        return ScopeResult(
            scopes=final_scopes,
            confidence=min(avg_confidence, 1.0),
            reasoning=" | ".join(reasoning_parts),
            filtered_commands=filtered_commands
        )
    
    def _infer_module_scopes(self, module: str) -> List[str]:
        """Infer scopes based on module name/path."""
        module_lower = module.lower()
        
        if any(term in module_lower for term in ["doc", "sphinx", "reference"]):
            return ["docs"]
        elif any(term in module_lower for term in ["memory", "session", "preference"]):
            return ["memory"]
        elif any(term in module_lower for term in ["analysis", "metric", "benchmark"]):
            return ["analysis"]
        elif any(term in module_lower for term in ["parser", "code", "ast"]):
            return ["code"]
        elif any(term in module_lower for term in ["scaffold", "template", "pattern"]):
            return ["parsing"]
        
        return []
    
    def _analyze_command_history(self, history: List[str]) -> List[str]:
        """Analyze recent command history for scope hints."""
        recent_commands = history[-5:]  # Last 5 commands
        scope_counts = {}
        
        for cmd in recent_commands:
            base_cmd = cmd.split()[0] if cmd else ""
            if base_cmd in self.command_scope_map:
                for scope in self.command_scope_map[base_cmd]:
                    scope_counts[scope] = scope_counts.get(scope, 0) + 1
        
        # Return scopes that appear more than once
        return [scope for scope, count in scope_counts.items() if count > 1]
    
    def _get_scoped_commands(self, scopes: List[str]) -> List[str]:
        """Get commands available for given scopes."""
        scoped_tool_provider = ScopedToolProvider()
        return scoped_tool_provider.filter_commands(scopes)


class ScopedToolProvider:
    """Provides filtered command sets based on active scopes."""
    
    def __init__(self):
        self.scope_commands = {
            "docs": [
                "docs search", "docs generate", "docs coverage",
                "python parse", "python warm"
            ],
            "memory": [
                "memory stats", "memory inject",
                "session save", "session restore",
                "preferences set"
            ],
            "analysis": [
                "analyze architecture", "analyze dependencies",
                "analyze patterns", "context inject"
            ],
            "code": [
                "code parse", "code execute", "code test",
                "find class", "find function"
            ],
            "parsing": [
                "populate-patterns", "modules list",
                "workspace status"
            ]
        }
        
        # All available commands for fallback
        self.all_commands = []
        for commands in self.scope_commands.values():
            self.all_commands.extend(commands)
    
    def filter_commands(self, scopes: List[str]) -> List[str]:
        """Filter available commands based on active scopes."""
        if not scopes:
            return self.all_commands
        
        filtered = set()
        for scope in scopes:
            if scope in self.scope_commands:
                filtered.update(self.scope_commands[scope])
        
        return sorted(list(filtered))
    
    def get_scope_for_command(self, command: str) -> Optional[str]:
        """Get the primary scope for a given command."""
        for scope, commands in self.scope_commands.items():
            if any(command.startswith(cmd) for cmd in commands):
                return scope
        return None


class ScopeManager:
    """Manages scope state and transitions during agent sessions."""
    
    def __init__(self, session_file: Optional[Path] = None):
        self.session_file = session_file or Path(".om_scope_session.json")
        self.current_scopes: List[str] = []
        self.scope_history: List[Tuple[str, List[str], float]] = []  # (timestamp, scopes, confidence)
        self.auto_scoper = AutoScoper()
        self.tool_provider = ScopedToolProvider()
        
        self._load_session()
    
    def update_scope(self, context: ScopeContext, force_scopes: Optional[List[str]] = None) -> ScopeResult:
        """Update current scope based on context or forced scopes."""
        if force_scopes:
            result = ScopeResult(
                scopes=force_scopes,
                confidence=1.0,
                reasoning="user_explicit",
                filtered_commands=self.tool_provider.filter_commands(force_scopes)
            )
        else:
            result = self.auto_scoper.determine_scope(context)
        
        # Update state
        self.current_scopes = result.scopes
        self.scope_history.append((
            datetime.now().isoformat(),
            result.scopes.copy(),
            result.confidence
        ))
        
        # Keep only last 20 scope changes
        if len(self.scope_history) > 20:
            self.scope_history = self.scope_history[-20:]
        
        self._save_session()
        return result
    
    def get_available_commands(self) -> List[str]:
        """Get commands available in current scope."""
        return self.tool_provider.filter_commands(self.current_scopes)
    
    def is_command_in_scope(self, command: str) -> bool:
        """Check if command is available in current scope."""
        available = self.get_available_commands()
        return any(command.startswith(cmd) for cmd in available)
    
    def suggest_scope_for_command(self, command: str) -> Optional[str]:
        """Suggest scope needed for unavailable command."""
        return self.tool_provider.get_scope_for_command(command)
    
    def get_scope_stats(self) -> Dict:
        """Get statistics about scope usage."""
        if not self.scope_history:
            return {"total_changes": 0, "avg_confidence": 0, "most_used_scopes": []}
        
        scope_counts = {}
        confidences = []
        
        for _, scopes, confidence in self.scope_history:
            confidences.append(confidence)
            for scope in scopes:
                scope_counts[scope] = scope_counts.get(scope, 0) + 1
        
        most_used = sorted(scope_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_changes": len(self.scope_history),
            "avg_confidence": sum(confidences) / len(confidences),
            "most_used_scopes": [scope for scope, _ in most_used[:3]],
            "current_scopes": self.current_scopes
        }
    
    def _load_session(self):
        """Load scope session from file."""
        if self.session_file.exists():
            try:
                with open(self.session_file) as f:
                    data = json.load(f)
                self.current_scopes = data.get("current_scopes", [])
                self.scope_history = data.get("scope_history", [])
            except Exception:
                pass  # Start fresh on error
    
    def _save_session(self):
        """Save scope session to file."""
        try:
            data = {
                "current_scopes": self.current_scopes,
                "scope_history": self.scope_history,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.session_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Non-critical if save fails


def create_scope_context(command: str, args: List[str] = None, task: str = "", 
                        module: str = None, history: List[str] = None) -> ScopeContext:
    """Convenience function to create scope context."""
    return ScopeContext(
        command=command,
        args=args or [],
        task_description=task,
        current_module=module,
        command_history=history or []
    )