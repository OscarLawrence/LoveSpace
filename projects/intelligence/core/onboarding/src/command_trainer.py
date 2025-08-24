"""OM command training system - 200 LOC max"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CommandExample:
    """Example of OM command usage"""
    command: str
    args: List[str]
    description: str
    expected_output: str
    difficulty: str  # basic, intermediate, advanced


@dataclass
class TrainingModule:
    """Training module for command category"""
    category: str
    description: str
    commands: List[CommandExample]
    prerequisites: List[str]


class CommandTrainer:
    """Trains agents on OM command usage"""
    
    def __init__(self):
        self.training_modules = self._initialize_training_modules()
        self.command_hierarchy = {
            'basic': ['workspace', 'memory'],
            'intermediate': ['code', 'scaffold'],
            'advanced': ['isolate', 'session']
        }
    
    def get_training_path(self, agent_level: str = 'beginner') -> List[str]:
        """Get recommended training path"""
        
        if agent_level == 'beginner':
            return ['workspace_basics', 'memory_management', 'code_operations']
        elif agent_level == 'intermediate':
            return ['workspace_advanced', 'scaffold_operations', 'integration_commands']
        else:
            return ['advanced_workflows', 'session_management', 'custom_operations']
    
    def get_training_module(self, module_name: str) -> Optional[TrainingModule]:
        """Get specific training module"""
        return self.training_modules.get(module_name)
    
    def practice_command(self, command: str, args: List[str]) -> Tuple[bool, str, str]:
        """Practice command with validation"""
        
        # Find matching example
        example = self._find_command_example(command, args)
        
        if not example:
            return False, "Command not found in training examples", ""
        
        # Validate command structure
        is_valid, feedback = self._validate_command_structure(command, args, example)
        
        return is_valid, feedback, example.expected_output
    
    def get_command_help(self, command: str) -> Optional[str]:
        """Get help for specific command"""
        
        help_text = {
            'workspace': 'Analyze and manage workspace structure',
            'memory': 'Context and memory management operations',
            'code': 'Code parsing, analysis, and execution',
            'scaffold': 'Project scaffolding and structure creation',
            'isolate': 'Isolate and focus on specific code sections',
            'session': 'Session management and state control'
        }
        
        return help_text.get(command)
    
    def _initialize_training_modules(self) -> Dict[str, TrainingModule]:
        """Initialize all training modules"""
        
        modules = {}
        
        # Workspace basics
        modules['workspace_basics'] = TrainingModule(
            category='workspace',
            description='Basic workspace operations',
            commands=[
                CommandExample(
                    command='workspace',
                    args=['status'],
                    description='Check workspace health and module status',
                    expected_output='Module status overview with health indicators',
                    difficulty='basic'
                ),
                CommandExample(
                    command='workspace',
                    args=['list'],
                    description='List all modules in workspace',
                    expected_output='Hierarchical list of workspace modules',
                    difficulty='basic'
                )
            ],
            prerequisites=[]
        )
        
        # Memory management
        modules['memory_management'] = TrainingModule(
            category='memory',
            description='Context and memory operations',
            commands=[
                CommandExample(
                    command='memory',
                    args=['context'],
                    description='Show current context state',
                    expected_output='Current context summary and active elements',
                    difficulty='basic'
                ),
                CommandExample(
                    command='memory',
                    args=['inject', 'context_data'],
                    description='Inject context into memory',
                    expected_output='Context injection confirmation',
                    difficulty='intermediate'
                )
            ],
            prerequisites=['workspace_basics']
        )
        
        # Code operations
        modules['code_operations'] = TrainingModule(
            category='code',
            description='Code analysis and execution',
            commands=[
                CommandExample(
                    command='code',
                    args=['parse'],
                    description='Parse codebase structure',
                    expected_output='Parsed code structure and dependencies',
                    difficulty='intermediate'
                ),
                CommandExample(
                    command='code',
                    args=['stats'],
                    description='Generate code statistics',
                    expected_output='Line counts, complexity metrics, and quality scores',
                    difficulty='basic'
                ),
                CommandExample(
                    command='code',
                    args=['execute', 'safe_mode'],
                    description='Execute code in safe environment',
                    expected_output='Execution results with safety checks',
                    difficulty='advanced'
                )
            ],
            prerequisites=['workspace_basics', 'memory_management']
        )
        
        # Scaffold operations
        modules['scaffold_operations'] = TrainingModule(
            category='scaffold',
            description='Project scaffolding and structure',
            commands=[
                CommandExample(
                    command='scaffold',
                    args=['info'],
                    description='Get scaffolding system information',
                    expected_output='Available templates and scaffolding options',
                    difficulty='basic'
                ),
                CommandExample(
                    command='scaffold',
                    args=['create', 'micro_module'],
                    description='Create new micro module structure',
                    expected_output='Generated module files and structure',
                    difficulty='intermediate'
                )
            ],
            prerequisites=['code_operations']
        )
        
        return modules
    
    def _find_command_example(self, command: str, args: List[str]) -> Optional[CommandExample]:
        """Find matching command example"""
        
        for module in self.training_modules.values():
            for example in module.commands:
                if (example.command == command and 
                    len(example.args) <= len(args) and
                    all(arg in args for arg in example.args[:len(example.args)])):
                    return example
        
        return None
    
    def _validate_command_structure(self, command: str, args: List[str], 
                                   example: CommandExample) -> Tuple[bool, str]:
        """Validate command structure against example"""
        
        # Check command matches
        if command != example.command:
            return False, f"Expected command '{example.command}', got '{command}'"
        
        # Check required args are present
        required_args = example.args
        if len(args) < len(required_args):
            return False, f"Missing required arguments: {required_args[len(args):]}"
        
        # Check arg order and content
        for i, required_arg in enumerate(required_args):
            if i >= len(args) or args[i] != required_arg:
                return False, f"Expected argument '{required_arg}' at position {i}"
        
        return True, "Command structure valid"
    
    def generate_practice_session(self, difficulty: str = 'basic') -> List[CommandExample]:
        """Generate practice session for given difficulty"""
        
        practice_commands = []
        
        for module in self.training_modules.values():
            for command in module.commands:
                if command.difficulty == difficulty:
                    practice_commands.append(command)
        
        return practice_commands
    
    def assess_command_knowledge(self, completed_commands: List[str]) -> Dict[str, float]:
        """Assess agent's command knowledge"""
        
        assessment = {
            'basic_commands': 0.0,
            'intermediate_commands': 0.0,
            'advanced_commands': 0.0,
            'overall_score': 0.0
        }
        
        total_by_difficulty = {'basic': 0, 'intermediate': 0, 'advanced': 0}
        completed_by_difficulty = {'basic': 0, 'intermediate': 0, 'advanced': 0}
        
        # Count total commands by difficulty
        for module in self.training_modules.values():
            for command in module.commands:
                total_by_difficulty[command.difficulty] += 1
        
        # Count completed commands
        for module in self.training_modules.values():
            for command in module.commands:
                command_id = f"{command.command}_{'-'.join(command.args)}"
                if command_id in completed_commands:
                    completed_by_difficulty[command.difficulty] += 1
        
        # Calculate scores
        for difficulty in ['basic', 'intermediate', 'advanced']:
            if total_by_difficulty[difficulty] > 0:
                score = completed_by_difficulty[difficulty] / total_by_difficulty[difficulty]
                assessment[f'{difficulty}_commands'] = score
        
        # Overall score (weighted: basic=30%, intermediate=40%, advanced=30%)
        overall = (
            assessment['basic_commands'] * 0.3 +
            assessment['intermediate_commands'] * 0.4 +
            assessment['advanced_commands'] * 0.3
        )
        assessment['overall_score'] = overall
        
        return assessment
