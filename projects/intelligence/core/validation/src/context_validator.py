"""Context completeness validation - 200 LOC max"""

import re
from typing import Dict, List, Set, Optional, Any
from .models import ContextCompleteness, ValidationResult, ValidationStatus


class ContextValidator:
    """Validates context completeness for operations"""
    
    def __init__(self):
        self.required_patterns = {
            'file_operation': {
                'patterns': [r'file', r'path', r'directory'],
                'required': ['file_path', 'operation_type'],
                'optional': ['backup', 'permissions']
            },
            'code_analysis': {
                'patterns': [r'analyze', r'parse', r'review'],
                'required': ['source_code', 'analysis_type'],
                'optional': ['language', 'framework']
            },
            'data_processing': {
                'patterns': [r'process', r'transform', r'clean'],
                'required': ['data_source', 'output_format'],
                'optional': ['schema', 'validation_rules']
            },
            'system_integration': {
                'patterns': [r'integrate', r'connect', r'api'],
                'required': ['target_system', 'credentials'],
                'optional': ['timeout', 'retry_policy']
            }
        }
        
        self.completeness_thresholds = {
            'critical': 0.9,
            'important': 0.7,
            'moderate': 0.5
        }
    
    def validate_context(self, request: str, context: Dict[str, Any]) -> ContextCompleteness:
        """Validate context completeness for given request"""
        
        operation_type = self._detect_operation_type(request)
        
        if not operation_type:
            return ContextCompleteness(
                required_elements=set(),
                present_elements=set(),
                missing_elements=set(),
                completeness_score=1.0
            )
        
        requirements = self.required_patterns[operation_type]
        required_elements = set(requirements['required'])
        optional_elements = set(requirements.get('optional', []))
        
        present_elements = self._extract_present_elements(context, required_elements | optional_elements)
        missing_elements = required_elements - present_elements
        
        score = self._calculate_completeness_score(
            required_elements, present_elements, optional_elements
        )
        
        critical_missing = self._identify_critical_missing(missing_elements, operation_type)
        
        return ContextCompleteness(
            required_elements=required_elements,
            present_elements=present_elements,
            missing_elements=missing_elements,
            completeness_score=score,
            critical_missing=critical_missing
        )
    
    def check_prerequisites(self, request: str, context: Dict[str, Any]) -> ValidationResult:
        """Check if all prerequisites are met"""
        
        completeness = self.validate_context(request, context)
        
        if completeness.completeness_score >= self.completeness_thresholds['critical']:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                message="All prerequisites met",
                score=completeness.completeness_score
            )
        elif completeness.completeness_score >= self.completeness_thresholds['important']:
            return ValidationResult(
                status=ValidationStatus.WARNING,
                message="Some optional elements missing",
                score=completeness.completeness_score,
                recommendations=[f"Consider providing: {', '.join(completeness.missing_elements)}"]
            )
        else:
            critical_missing = completeness.critical_missing or []
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message="Critical elements missing",
                score=completeness.completeness_score,
                details={'missing_critical': critical_missing},
                recommendations=[f"Must provide: {', '.join(critical_missing)}"]
            )
    
    def _detect_operation_type(self, request: str) -> Optional[str]:
        """Detect the type of operation from request"""
        
        request_lower = request.lower()
        
        for op_type, config in self.required_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, request_lower):
                    return op_type
        
        return None
    
    def _extract_present_elements(self, context: Dict[str, Any], all_elements: Set[str]) -> Set[str]:
        """Extract which required elements are present in context"""
        
        present = set()
        context_str = str(context).lower()
        
        for element in all_elements:
            # Check direct key presence
            if element in context:
                present.add(element)
                continue
            
            # Check for similar keys
            element_variations = self._get_element_variations(element)
            for variation in element_variations:
                if variation in context or variation in context_str:
                    present.add(element)
                    break
        
        return present
    
    def _get_element_variations(self, element: str) -> List[str]:
        """Get variations of element names to check"""
        
        variations = [element]
        
        # Add underscore/camelCase variations
        if '_' in element:
            variations.append(element.replace('_', ''))
            # Convert to camelCase
            parts = element.split('_')
            camel_case = parts[0] + ''.join(p.capitalize() for p in parts[1:])
            variations.append(camel_case)
        
        # Add with common prefixes/suffixes
        variations.extend([
            f"current_{element}",
            f"{element}_config",
            f"{element}_data",
            f"input_{element}",
            f"output_{element}"
        ])
        
        return variations
    
    def _calculate_completeness_score(self, required: Set[str], present: Set[str], optional: Set[str]) -> float:
        """Calculate completeness score"""
        
        if not required:
            return 1.0
        
        # Base score from required elements
        required_score = len(required & present) / len(required)
        
        # Bonus from optional elements
        optional_present = len(optional & present)
        optional_bonus = min(0.2, optional_present * 0.05) if optional else 0
        
        return min(1.0, required_score + optional_bonus)
    
    def _identify_critical_missing(self, missing: Set[str], operation_type: str) -> List[str]:
        """Identify which missing elements are critical"""
        
        critical_elements = {
            'file_operation': ['file_path'],
            'code_analysis': ['source_code'],
            'data_processing': ['data_source'],
            'system_integration': ['target_system', 'credentials']
        }
        
        critical_for_type = set(critical_elements.get(operation_type, []))
        return list(missing & critical_for_type)
    
    def suggest_completions(self, request: str, context: Dict[str, Any]) -> List[str]:
        """Suggest what to add for complete context"""
        
        completeness = self.validate_context(request, context)
        suggestions = []
        
        for missing in completeness.missing_elements:
            suggestion = self._generate_suggestion(missing, request)
            if suggestion:
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_suggestion(self, missing_element: str, request: str) -> str:
        """Generate specific suggestion for missing element"""
        
        suggestions_map = {
            'file_path': "Specify the file path to operate on",
            'source_code': "Provide the source code to analyze",
            'data_source': "Specify the data source location",
            'target_system': "Identify the target system for integration",
            'credentials': "Provide authentication credentials",
            'operation_type': "Clarify what operation to perform",
            'analysis_type': "Specify the type of analysis needed",
            'output_format': "Define the desired output format"
        }
        
        return suggestions_map.get(missing_element, f"Provide {missing_element.replace('_', ' ')}")
    
    def validate_file_references(self, request: str) -> ValidationResult:
        """Validate that file references in request exist"""
        
        file_patterns = [
            r'file[:\s]+([^\s,]+)',
            r'path[:\s]+([^\s,]+)',
            r'([/\w.-]+\.\w+)',
            r'in\s+([/\w.-]+)'
        ]
        
        referenced_files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, request, re.IGNORECASE)
            referenced_files.update(matches)
        
        missing_files = []
        for file_ref in referenced_files:
            if file_ref and not self._file_exists(file_ref):
                missing_files.append(file_ref)
        
        if missing_files:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                message=f"Referenced files not found: {', '.join(missing_files)}",
                score=0.0,
                details={'missing_files': missing_files}
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            message="All file references validated",
            score=1.0
        )
    
    def _file_exists(self, file_path: str) -> bool:
        """Check if file exists (simplified)"""
        import os
        return os.path.exists(file_path)
