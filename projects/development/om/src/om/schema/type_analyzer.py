"""
Type annotation analysis for schema generation
"""

import re
from typing import Any, Dict, List, Union, get_type_hints

from .data_models import TypeSchema


class TypeAnalyzer:
    """Analyzes Python type hints and generates schemas."""
    
    def __init__(self):
        self.primitive_types = {
            'str': {'type': 'string'},
            'int': {'type': 'integer'},
            'float': {'type': 'number'},
            'bool': {'type': 'boolean'},
            'bytes': {'type': 'string', 'format': 'byte'},
            'datetime': {'type': 'string', 'format': 'date-time'},
            'date': {'type': 'string', 'format': 'date'},
            'time': {'type': 'string', 'format': 'time'},
            'uuid': {'type': 'string', 'format': 'uuid'},
            'Path': {'type': 'string', 'format': 'path'}
        }
    
    def analyze_type_annotation(self, annotation: Any) -> TypeSchema:
        """Analyze a type annotation and generate schema."""
        if annotation is None or annotation == type(None):
            return TypeSchema(
                name='null',
                type_kind='primitive',
                base_type='null',
                properties={'type': 'null'},
                required=[],
                description='Null value',
                examples=[None]
            )
        
        # Handle string annotations (forward references)
        if isinstance(annotation, str):
            return self._analyze_string_annotation(annotation)
        
        # Handle typing module types
        origin = getattr(annotation, '__origin__', None)
        args = getattr(annotation, '__args__', ())
        
        if origin is Union:
            return self._analyze_union_type(args)
        elif origin is list or origin is List:
            return self._analyze_list_type(args)
        elif origin is dict or origin is Dict:
            return self._analyze_dict_type(args)
        elif origin is tuple:
            return self._analyze_tuple_type(args)
        elif hasattr(annotation, '__name__'):
            # Regular class or primitive type
            return self._analyze_class_type(annotation)
        else:
            # Fallback for complex types
            return TypeSchema(
                name=str(annotation),
                type_kind='unknown',
                base_type='object',
                properties={'type': 'object'},
                required=[],
                description=f'Complex type: {annotation}',
                examples=[]
            )
    
    def _analyze_string_annotation(self, annotation: str) -> TypeSchema:
        """Analyze string type annotation."""
        # Handle common patterns
        if annotation in self.primitive_types:
            return TypeSchema(
                name=annotation,
                type_kind='primitive',
                base_type=annotation,
                properties=self.primitive_types[annotation],
                required=[],
                description=f'{annotation} value',
                examples=[]
            )
        
        # Handle Optional[Type] pattern
        optional_match = re.match(r'Optional\[(.*)\]', annotation)
        if optional_match:
            inner_type = optional_match.group(1)
            inner_schema = self._analyze_string_annotation(inner_type)
            inner_schema.properties['nullable'] = True
            return inner_schema
        
        # Handle List[Type] pattern
        list_match = re.match(r'List\[(.*)\]', annotation)
        if list_match:
            item_type = list_match.group(1)
            return TypeSchema(
                name=f'List[{item_type}]',
                type_kind='generic',
                base_type='array',
                properties={
                    'type': 'array',
                    'items': self._analyze_string_annotation(item_type).properties
                },
                required=[],
                description=f'List of {item_type}',
                examples=[]
            )
        
        # Default to object type
        return TypeSchema(
            name=annotation,
            type_kind='class',
            base_type='object',
            properties={'type': 'object'},
            required=[],
            description=f'Custom type: {annotation}',
            examples=[]
        )
    
    def _analyze_union_type(self, args: tuple) -> TypeSchema:
        """Analyze Union type annotation."""
        # Check if it's Optional (Union with None)
        if len(args) == 2 and type(None) in args:
            non_none_type = args[0] if args[1] is type(None) else args[1]
            schema = self.analyze_type_annotation(non_none_type)
            schema.properties['nullable'] = True
            schema.name = f'Optional[{schema.name}]'
            return schema
        
        # Multiple type union
        schemas = [self.analyze_type_annotation(arg) for arg in args]
        return TypeSchema(
            name=f'Union[{", ".join(s.name for s in schemas)}]',
            type_kind='union',
            base_type='union',
            properties={
                'oneOf': [s.properties for s in schemas]
            },
            required=[],
            description=f'One of: {", ".join(s.name for s in schemas)}',
            examples=[]
        )
    
    def _analyze_list_type(self, args: tuple) -> TypeSchema:
        """Analyze List type annotation."""
        if args:
            item_schema = self.analyze_type_annotation(args[0])
            return TypeSchema(
                name=f'List[{item_schema.name}]',
                type_kind='generic',
                base_type='array',
                properties={
                    'type': 'array',
                    'items': item_schema.properties
                },
                required=[],
                description=f'List of {item_schema.name}',
                examples=[]
            )
        else:
            return TypeSchema(
                name='List',
                type_kind='generic',
                base_type='array',
                properties={'type': 'array'},
                required=[],
                description='List of any type',
                examples=[]
            )
    
    def _analyze_dict_type(self, args: tuple) -> TypeSchema:
        """Analyze Dict type annotation."""
        if len(args) >= 2:
            key_schema = self.analyze_type_annotation(args[0])
            value_schema = self.analyze_type_annotation(args[1])
            return TypeSchema(
                name=f'Dict[{key_schema.name}, {value_schema.name}]',
                type_kind='generic',
                base_type='object',
                properties={
                    'type': 'object',
                    'additionalProperties': value_schema.properties
                },
                required=[],
                description=f'Dictionary with {key_schema.name} keys and {value_schema.name} values',
                examples=[]
            )
        else:
            return TypeSchema(
                name='Dict',
                type_kind='generic',
                base_type='object',
                properties={'type': 'object'},
                required=[],
                description='Dictionary of any type',
                examples=[]
            )
    
    def _analyze_tuple_type(self, args: tuple) -> TypeSchema:
        """Analyze Tuple type annotation."""
        if args:
            item_schemas = [self.analyze_type_annotation(arg) for arg in args]
            return TypeSchema(
                name=f'Tuple[{", ".join(s.name for s in item_schemas)}]',
                type_kind='generic',
                base_type='array',
                properties={
                    'type': 'array',
                    'items': [s.properties for s in item_schemas],
                    'minItems': len(args),
                    'maxItems': len(args)
                },
                required=[],
                description=f'Tuple of {len(args)} items',
                examples=[]
            )
        else:
            return TypeSchema(
                name='Tuple',
                type_kind='generic',
                base_type='array',
                properties={'type': 'array'},
                required=[],
                description='Tuple of any length',
                examples=[]
            )
    
    def _analyze_class_type(self, cls: type) -> TypeSchema:
        """Analyze a class type."""
        type_name = cls.__name__
        
        # Handle primitive types
        if type_name in self.primitive_types:
            return TypeSchema(
                name=type_name,
                type_kind='primitive',
                base_type=type_name,
                properties=self.primitive_types[type_name],
                required=[],
                description=f'{type_name} value',
                examples=[]
            )
        
        # Handle dataclass types
        if hasattr(cls, '__dataclass_fields__'):
            return self._analyze_dataclass(cls)
        
        # Generic class type
        return TypeSchema(
            name=type_name,
            type_kind='class',
            base_type='object',
            properties={'type': 'object'},
            required=[],
            description=f'{type_name} instance',
            examples=[]
        )
    
    def _analyze_dataclass(self, cls: type) -> TypeSchema:
        """Analyze a dataclass type."""
        properties = {}
        required = []
        
        # Get type hints for the dataclass
        try:
            hints = get_type_hints(cls)
        except (NameError, AttributeError):
            hints = {}
        
        # Analyze each field
        for field_name, field in cls.__dataclass_fields__.items():
            field_type = hints.get(field_name, field.type)
            field_schema = self.analyze_type_annotation(field_type)
            properties[field_name] = field_schema.properties
            
            # Check if field is required (no default value)
            if field.default is field.default_factory is field.default:
                required.append(field_name)
        
        return TypeSchema(
            name=cls.__name__,
            type_kind='class',
            base_type='object',
            properties={
                'type': 'object',
                'properties': properties,
                'required': required
            },
            required=required,
            description=f'{cls.__name__} dataclass',
            examples=[]
        )
