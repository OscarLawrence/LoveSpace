"""CLI Reference Generation System.

Generates comprehensive CLI documentation from Click commands.
"""

import click
from pathlib import Path
from typing import Dict, List, Optional, Any
import inspect
import re


class CLIDocumentationGenerator:
    """Generates documentation for Click CLI commands."""
    
    def __init__(self):
        self.commands_data = {}
    
    def extract_command_info(self, command: click.Command, parent_path: str = "") -> Dict[str, Any]:
        """Extract comprehensive information from Click command."""
        full_name = f"{parent_path} {command.name}".strip()
        
        info = {
            'name': command.name,
            'full_name': full_name,
            'help': command.help or "No description available",
            'short_help': command.short_help,
            'usage': self._get_command_usage(command, full_name),
            'options': self._extract_options(command),
            'arguments': self._extract_arguments(command),
            'examples': self._extract_examples(command),
            'scopes': self._extract_scopes(command),
            'aliases': getattr(command, 'aliases', [])
        }
        
        # Handle groups (commands with subcommands)
        if isinstance(command, click.Group):
            info['type'] = 'group'
            info['subcommands'] = {}
            
            for sub_name, sub_command in command.commands.items():
                info['subcommands'][sub_name] = self.extract_command_info(
                    sub_command, full_name
                )
        else:
            info['type'] = 'command'
        
        return info
    
    def _get_command_usage(self, command: click.Command, full_name: str) -> str:
        """Generate usage string for command."""
        ctx = click.Context(command)
        formatter = ctx.make_formatter()
        command.format_usage(ctx, formatter)
        usage = formatter.getvalue().strip()
        
        # Replace 'Usage:' prefix and command name with full name
        usage = re.sub(r'^Usage:\s*\S+', f'om {full_name}', usage)
        return usage
    
    def _extract_options(self, command: click.Command) -> List[Dict[str, Any]]:
        """Extract option information from command."""
        options = []
        
        for param in command.params:
            if isinstance(param, click.Option):
                option_info = {
                    'names': param.opts,
                    'secondary_names': param.secondary_opts,
                    'help': param.help or "No description",
                    'type': self._get_param_type_info(param),
                    'default': param.default,
                    'required': param.required,
                    'multiple': param.multiple,
                    'is_flag': param.is_flag,
                    'flag_value': getattr(param, 'flag_value', None),
                    'choices': getattr(param.type, 'choices', None) if hasattr(param.type, 'choices') else None,
                    'metavar': param.metavar
                }
                options.append(option_info)
        
        return options
    
    def _extract_arguments(self, command: click.Command) -> List[Dict[str, Any]]:
        """Extract argument information from command."""
        arguments = []
        
        for param in command.params:
            if isinstance(param, click.Argument):
                arg_info = {
                    'name': param.name,
                    'help': param.help or f"Argument: {param.name}",
                    'type': self._get_param_type_info(param),
                    'required': param.required,
                    'nargs': param.nargs,
                    'metavar': param.metavar
                }
                arguments.append(arg_info)
        
        return arguments
    
    def _get_param_type_info(self, param: click.Parameter) -> Dict[str, Any]:
        """Get detailed type information for parameter."""
        param_type = param.type
        
        type_info = {
            'name': param_type.name,
            'python_type': type(param_type).__name__
        }
        
        # Add specific type information
        if isinstance(param_type, click.Choice):
            type_info['choices'] = param_type.choices
            type_info['case_sensitive'] = param_type.case_sensitive
        elif isinstance(param_type, click.IntRange):
            type_info['min'] = param_type.min
            type_info['max'] = param_type.max
        elif isinstance(param_type, click.FloatRange):
            type_info['min'] = param_type.min
            type_info['max'] = param_type.max
        elif isinstance(param_type, click.Path):
            type_info['exists'] = param_type.exists
            type_info['file_okay'] = param_type.file_okay
            type_info['dir_okay'] = param_type.dir_okay
            type_info['readable'] = param_type.readable
            type_info['writable'] = param_type.writable
        
        return type_info
    
    def _extract_examples(self, command: click.Command) -> List[str]:
        """Extract usage examples from command help or docstring."""
        examples = []
        
        # Look for examples in help text
        if command.help:
            example_patterns = [
                r'Example[s]?:\s*\n(.*?)(?=\n\n|\Z)',
                r'Usage:\s*\n(.*?)(?=\n\n|\Z)',
                r'```\s*\n(.*?)\n```'
            ]
            
            for pattern in example_patterns:
                matches = re.findall(pattern, command.help, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    # Clean up the example text
                    example_lines = [line.strip() for line in match.split('\n') if line.strip()]
                    if example_lines:
                        examples.extend(example_lines)
        
        # Look for examples in callback docstring
        if hasattr(command, 'callback') and command.callback:
            docstring = inspect.getdoc(command.callback)
            if docstring:
                # Extract examples from docstring
                example_section = re.search(r'Examples?:\s*\n(.*?)(?=\n\n|\Z)', docstring, re.DOTALL | re.IGNORECASE)
                if example_section:
                    example_lines = [line.strip() for line in example_section.group(1).split('\n') if line.strip()]
                    examples.extend(example_lines)
        
        return examples[:5]  # Limit to 5 examples
    
    def _extract_scopes(self, command: click.Command) -> List[str]:
        """Extract scope information from command."""
        scopes = []
        
        # Check for scope decorators or attributes
        if hasattr(command, 'callback') and command.callback:
            if hasattr(command.callback, '_om_scopes'):
                scopes = command.callback._om_scopes
        
        return scopes
    
    def generate_markdown_reference(self, root_command: click.Group, title: str = "CLI Reference") -> str:
        """Generate complete Markdown CLI reference."""
        command_info = self.extract_command_info(root_command)
        
        lines = [
            f"# {title}",
            "",
            "Complete reference for all CLI commands and options.",
            ""
        ]
        
        # Generate table of contents
        lines.extend(self._generate_toc(command_info))
        lines.append("")
        
        # Generate detailed documentation
        lines.extend(self._generate_command_docs(command_info))
        
        return "\n".join(lines)
    
    def _generate_toc(self, command_info: Dict[str, Any], level: int = 2) -> List[str]:
        """Generate table of contents."""
        lines = []
        
        if level == 2:
            lines.append("## Table of Contents")
            lines.append("")
        
        # Add current command
        indent = "  " * (level - 2)
        anchor = command_info['full_name'].replace(' ', '-').lower()
        lines.append(f"{indent}- [{command_info['full_name']}](#{anchor})")
        
        # Add subcommands
        if command_info.get('subcommands'):
            for sub_info in command_info['subcommands'].values():
                lines.extend(self._generate_toc(sub_info, level + 1))
        
        return lines
    
    def _generate_command_docs(self, command_info: Dict[str, Any], level: int = 2) -> List[str]:
        """Generate detailed command documentation."""
        lines = []
        
        # Command header
        header_level = "#" * level
        lines.append(f"{header_level} {command_info['full_name']}")
        lines.append("")
        
        # Description
        lines.append(command_info['help'])
        lines.append("")
        
        # Usage
        lines.append("### Usage")
        lines.append("")
        lines.append(f"```bash")
        lines.append(command_info['usage'])
        lines.append("```")
        lines.append("")
        
        # Arguments
        if command_info['arguments']:
            lines.append("### Arguments")
            lines.append("")
            
            for arg in command_info['arguments']:
                lines.append(f"- **{arg['name']}** ({arg['type']['name']})")
                lines.append(f"  - {arg['help']}")
                if not arg['required']:
                    lines.append(f"  - Optional")
                lines.append("")
        
        # Options
        if command_info['options']:
            lines.append("### Options")
            lines.append("")
            
            for option in command_info['options']:
                # Format option names
                names = ", ".join([f"`{name}`" for name in option['names']])
                if option['secondary_names']:
                    names += ", " + ", ".join([f"`{name}`" for name in option['secondary_names']])
                
                lines.append(f"- {names}")
                lines.append(f"  - {option['help']}")
                
                # Add type information
                type_info = option['type']
                if type_info['choices']:
                    lines.append(f"  - Choices: {', '.join(type_info['choices'])}")
                
                if option['default'] is not None:
                    lines.append(f"  - Default: `{option['default']}`")
                
                if option['required']:
                    lines.append(f"  - Required")
                
                lines.append("")
        
        # Scopes
        if command_info['scopes']:
            lines.append("### Scopes")
            lines.append("")
            lines.append(f"This command belongs to scopes: {', '.join(command_info['scopes'])}")
            lines.append("")
        
        # Examples
        if command_info['examples']:
            lines.append("### Examples")
            lines.append("")
            
            for example in command_info['examples']:
                lines.append(f"```bash")
                lines.append(example)
                lines.append("```")
                lines.append("")
        
        # Subcommands
        if command_info.get('subcommands'):
            lines.append("### Subcommands")
            lines.append("")
            
            for sub_name, sub_info in command_info['subcommands'].items():
                lines.append(f"- **{sub_name}**: {sub_info['help']}")
            
            lines.append("")
            
            # Generate docs for subcommands
            for sub_info in command_info['subcommands'].values():
                lines.extend(self._generate_command_docs(sub_info, level + 1))
        
        return lines
    
    def generate_json_reference(self, root_command: click.Group) -> str:
        """Generate JSON CLI reference."""
        command_info = self.extract_command_info(root_command)
        
        import json
        return json.dumps(command_info, indent=2, default=str)
    
    def generate_completion_data(self, root_command: click.Group) -> Dict[str, Any]:
        """Generate shell completion data."""
        completion_data = {
            'commands': {},
            'options': {},
            'arguments': {}
        }
        
        def collect_completion_data(cmd_info: Dict[str, Any], path: str = ""):
            full_path = f"{path} {cmd_info['name']}".strip()
            
            # Store command
            completion_data['commands'][full_path] = {
                'help': cmd_info['help'],
                'options': [opt['names'][0] for opt in cmd_info['options']],
                'arguments': [arg['name'] for arg in cmd_info['arguments']]
            }
            
            # Store options
            for option in cmd_info['options']:
                for name in option['names']:
                    completion_data['options'][name] = {
                        'help': option['help'],
                        'type': option['type']['name'],
                        'choices': option['choices']
                    }
            
            # Recurse for subcommands
            if cmd_info.get('subcommands'):
                for sub_info in cmd_info['subcommands'].values():
                    collect_completion_data(sub_info, full_path)
        
        command_info = self.extract_command_info(root_command)
        collect_completion_data(command_info)
        
        return completion_data