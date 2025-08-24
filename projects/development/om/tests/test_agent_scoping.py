"""Tests for Agent Tool Scoping System.

Validates Phase 1: Agent Tool Scoping implementation.
"""

import pytest
from pathlib import Path
import tempfile
import json
from unittest.mock import patch, MagicMock

from om.agent_scoping import (
    AutoScoper, ScopedToolProvider, ScopeManager, ScopeContext, 
    ScopeResult, create_scope_context
)


class TestAutoScoper:
    """Test automatic scope determination."""
    
    def setup_method(self):
        self.scoper = AutoScoper()
    
    def test_direct_command_mapping(self):
        """Test direct command to scope mapping."""
        context = create_scope_context("docs search", ["python", "ast.parse"])
        result = self.scoper.determine_scope(context)
        
        assert "docs" in result.scopes
        assert result.confidence >= 0.8
        assert "direct_map:docs→['docs']" in result.reasoning
    
    def test_pattern_based_detection(self):
        """Test pattern-based scope detection."""
        context = create_scope_context(
            "help", 
            task="I need to analyze the architecture of this codebase"
        )
        result = self.scoper.determine_scope(context)
        
        assert "analysis" in result.scopes
        assert "pattern:analysis:analyze" in result.reasoning
    
    def test_module_context_influence(self):
        """Test module context affecting scope determination."""
        context = create_scope_context(
            "unknown command",
            module="docs_parser"
        )
        result = self.scoper.determine_scope(context)
        
        assert "docs" in result.scopes
        assert "module:docs_parser→['docs']" in result.reasoning
    
    def test_command_history_analysis(self):
        """Test command history influencing scope."""
        history = ["memory stats", "session save", "memory inject"]
        context = create_scope_context("help", history=history)
        result = self.scoper.determine_scope(context)
        
        assert "memory" in result.scopes
        assert "history→['memory']" in result.reasoning
    
    def test_multiple_scope_detection(self):
        """Test detection of multiple relevant scopes."""
        context = create_scope_context(
            "context inject",
            task="analyze memory patterns and generate documentation"
        )
        result = self.scoper.determine_scope(context)
        
        # Should detect both analysis and memory scopes
        assert len(result.scopes) >= 2
        assert any(scope in ["analysis", "memory"] for scope in result.scopes)
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # High confidence case - direct mapping
        context = create_scope_context("docs search")
        result = self.scoper.determine_scope(context)
        assert result.confidence >= 0.8
        
        # Lower confidence case - weak patterns
        context = create_scope_context("unknown", task="vague task")
        result = self.scoper.determine_scope(context)
        assert result.confidence <= 0.8


class TestScopedToolProvider:
    """Test scoped tool filtering."""
    
    def setup_method(self):
        self.provider = ScopedToolProvider()
    
    def test_filter_commands_single_scope(self):
        """Test filtering commands for single scope."""
        commands = self.provider.filter_commands(["docs"])
        
        assert "docs search" in commands
        assert "python parse" in commands
        assert "memory stats" not in commands
        assert "code parse" not in commands
    
    def test_filter_commands_multiple_scopes(self):
        """Test filtering commands for multiple scopes."""
        commands = self.provider.filter_commands(["docs", "memory"])
        
        assert "docs search" in commands
        assert "memory stats" in commands
        assert "session save" in commands
        assert "code parse" not in commands
    
    def test_filter_commands_empty_scopes(self):
        """Test filtering with no scopes returns all commands."""
        commands = self.provider.filter_commands([])
        
        # Should return all available commands
        assert len(commands) > 10
        assert "docs search" in commands
        assert "memory stats" in commands
        assert "code parse" in commands
    
    def test_get_scope_for_command(self):
        """Test getting scope for specific command."""
        assert self.provider.get_scope_for_command("docs search") == "docs"
        assert self.provider.get_scope_for_command("memory stats") == "memory"
        assert self.provider.get_scope_for_command("analyze patterns") == "analysis"
        assert self.provider.get_scope_for_command("unknown command") is None
    
    def test_scope_command_coverage(self):
        """Test that all scopes have commands defined."""
        expected_scopes = ["docs", "memory", "analysis", "code", "parsing"]
        
        for scope in expected_scopes:
            commands = self.provider.filter_commands([scope])
            assert len(commands) > 0, f"Scope {scope} has no commands"


class TestScopeManager:
    """Test scope state management."""
    
    def setup_method(self):
        # Use temporary file for session
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = ScopeManager(Path(self.temp_file.name))
    
    def teardown_method(self):
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_update_scope_auto(self):
        """Test automatic scope update."""
        context = create_scope_context("docs search")
        result = self.manager.update_scope(context)
        
        assert "docs" in result.scopes
        assert self.manager.current_scopes == result.scopes
        assert len(self.manager.scope_history) == 1
    
    def test_update_scope_forced(self):
        """Test forced scope update."""
        context = create_scope_context("any command")
        result = self.manager.update_scope(context, force_scopes=["memory", "analysis"])
        
        assert result.scopes == ["memory", "analysis"]
        assert result.confidence == 1.0
        assert result.reasoning == "user_explicit"
    
    def test_get_available_commands(self):
        """Test getting available commands for current scope."""
        context = create_scope_context("docs search")
        self.manager.update_scope(context)
        
        commands = self.manager.get_available_commands()
        assert "docs search" in commands
        assert "memory stats" not in commands
    
    def test_is_command_in_scope(self):
        """Test checking if command is in current scope."""
        context = create_scope_context("docs search")
        self.manager.update_scope(context)
        
        assert self.manager.is_command_in_scope("docs search")
        assert self.manager.is_command_in_scope("python parse")
        assert not self.manager.is_command_in_scope("memory stats")
    
    def test_suggest_scope_for_command(self):
        """Test suggesting scope for unavailable command."""
        context = create_scope_context("docs search")
        self.manager.update_scope(context)  # Sets scope to docs
        
        suggestion = self.manager.suggest_scope_for_command("memory stats")
        assert suggestion == "memory"
    
    def test_scope_history_management(self):
        """Test scope history tracking and limits."""
        # Add many scope changes
        for i in range(25):
            context = create_scope_context(f"command_{i}")
            self.manager.update_scope(context)
        
        # Should keep only last 20
        assert len(self.manager.scope_history) == 20
    
    def test_session_persistence(self):
        """Test scope session save/load."""
        context = create_scope_context("docs search")
        self.manager.update_scope(context)
        
        # Create new manager with same session file
        new_manager = ScopeManager(Path(self.temp_file.name))
        
        assert new_manager.current_scopes == self.manager.current_scopes
        assert len(new_manager.scope_history) == len(self.manager.scope_history)
    
    def test_get_scope_stats(self):
        """Test scope usage statistics."""
        # Add some scope changes
        contexts = [
            create_scope_context("docs search"),
            create_scope_context("memory stats"),
            create_scope_context("docs dense"),
        ]
        
        for context in contexts:
            self.manager.update_scope(context)
        
        stats = self.manager.get_scope_stats()
        
        assert stats["total_changes"] == 3
        assert stats["avg_confidence"] > 0
        assert "docs" in stats["most_used_scopes"]
        assert stats["current_scopes"] == self.manager.current_scopes


class TestScopeContext:
    """Test scope context creation and handling."""
    
    def test_create_scope_context_basic(self):
        """Test basic scope context creation."""
        context = create_scope_context("docs search", ["python"], "parse documentation")
        
        assert context.command == "docs search"
        assert context.args == ["python"]
        assert context.task_description == "parse documentation"
        assert context.current_module is None
        assert context.command_history == []
    
    def test_create_scope_context_full(self):
        """Test full scope context creation."""
        context = create_scope_context(
            command="analyze gaps",
            args=["--verbose"],
            task="find missing tests",
            module="test_module",
            history=["code parse", "analyze architecture"]
        )
        
        assert context.command == "analyze gaps"
        assert context.args == ["--verbose"]
        assert context.task_description == "find missing tests"
        assert context.current_module == "test_module"
        assert context.command_history == ["code parse", "analyze architecture"]


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def setup_method(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        self.manager = ScopeManager(Path(self.temp_file.name))
    
    def teardown_method(self):
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_documentation_workflow(self):
        """Test typical documentation workflow scoping."""
        # Start with docs command
        context1 = create_scope_context("docs search", ["python", "ast"])
        result1 = self.manager.update_scope(context1)
        assert "docs" in result1.scopes
        
        # Follow up with related docs command
        context2 = create_scope_context("python parse", ["ast.parse"])
        result2 = self.manager.update_scope(context2)
        assert "docs" in result2.scopes
        
        # All docs commands should be available
        available = self.manager.get_available_commands()
        assert "docs search" in available
        assert "python parse" in available
        assert "docs generate" in available
    
    def test_analysis_workflow(self):
        """Test typical analysis workflow scoping."""
        # Start with analysis task
        context = create_scope_context(
            "help", 
            task="I need to analyze the codebase architecture and find gaps"
        )
        result = self.manager.update_scope(context)
        assert "analysis" in result.scopes
        
        # Analysis commands should be available
        available = self.manager.get_available_commands()
        assert "analyze architecture" in available
        assert "analyze patterns" in available
        assert "context inject" in available
    
    def test_mixed_workflow_scope_switching(self):
        """Test scope switching in mixed workflows."""
        # Start with docs
        context1 = create_scope_context("docs search")
        self.manager.update_scope(context1)
        assert "docs" in self.manager.current_scopes
        
        # Switch to memory context
        context2 = create_scope_context("memory stats")
        self.manager.update_scope(context2)
        assert "memory" in self.manager.current_scopes
        
        # Verify scope history tracking
        assert len(self.manager.scope_history) == 2
    
    def test_cognitive_load_reduction(self):
        """Test that scoping reduces cognitive load."""
        # Without scoping - all commands available
        all_commands = self.manager.tool_provider.all_commands
        
        # With docs scoping
        context = create_scope_context("docs search")
        self.manager.update_scope(context)
        scoped_commands = self.manager.get_available_commands()
        
        # Should have significantly fewer commands
        assert len(scoped_commands) < len(all_commands) / 2
        assert len(scoped_commands) <= 10  # Target: 3-5 relevant commands per scope


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def setup_method(self):
        self.scoper = AutoScoper()
        self.provider = ScopedToolProvider()
    
    def test_empty_context(self):
        """Test handling of empty context."""
        context = create_scope_context("")
        result = self.scoper.determine_scope(context)
        
        assert isinstance(result.scopes, list)
        assert isinstance(result.confidence, float)
        assert 0 <= result.confidence <= 1
    
    def test_invalid_scope_filtering(self):
        """Test filtering with invalid scopes."""
        commands = self.provider.filter_commands(["invalid_scope"])
        assert commands == []  # Should return empty list
    
    def test_malformed_session_file(self):
        """Test handling of malformed session file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        temp_file.write("invalid json content")
        temp_file.close()
        
        # Should handle gracefully and start fresh
        manager = ScopeManager(Path(temp_file.name))
        assert manager.current_scopes == []
        assert manager.scope_history == []
        
        Path(temp_file.name).unlink()


# Integration test with CLI (if available)
def test_cli_integration():
    """Test integration with CLI system."""
    try:
        from om.scoped_cli import ScopedCLI, scoped_cli
        
        # Test basic CLI functionality
        assert hasattr(scoped_cli, 'scope_manager')
        assert hasattr(scoped_cli, 'auto_scope_enabled')
        
        # Test scoped help
        scoped_cli.show_scoped_help(['docs'])
        
    except ImportError:
        pytest.skip("CLI integration not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])