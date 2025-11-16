#!/usr/bin/env python3
"""
API Contract Validator - Validate API responses against OpenAPI specifications

This tool validates API responses against OpenAPI 3.0 specifications to ensure
APIs adhere to their documented contracts. Essential for preventing breaking
changes and maintaining API reliability.

Created by: @investigate-champion
Mission: idea:19 - Web API Innovation Investigation
Date: 2025-11-16
"""

import json
import sys
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import argparse


class APIContractValidator:
    """Validate API responses against OpenAPI specifications."""
    
    def __init__(self, spec_path: str):
        """
        Initialize validator with OpenAPI specification.
        
        Args:
            spec_path: Path to OpenAPI 3.0 JSON or YAML file
        """
        self.spec_path = Path(spec_path)
        self.spec = self._load_spec()
        
    def _load_spec(self) -> Dict:
        """Load OpenAPI specification from file."""
        if not self.spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {self.spec_path}")
        
        with open(self.spec_path, 'r') as f:
            if self.spec_path.suffix == '.json':
                return json.load(f)
            elif self.spec_path.suffix in ['.yaml', '.yml']:
                try:
                    import yaml
                    return yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML required for YAML specs: pip install pyyaml")
            else:
                raise ValueError(f"Unsupported spec format: {self.spec_path.suffix}")
    
    def validate_response(
        self, 
        endpoint: str, 
        method: str, 
        status_code: int,
        response: Dict
    ) -> List[str]:
        """
        Validate response against spec.
        
        Args:
            endpoint: API endpoint path (e.g., '/users/{id}')
            method: HTTP method (GET, POST, etc.)
            status_code: HTTP status code
            response: Response body (parsed JSON)
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Find endpoint in spec
        path_spec = self.spec.get('paths', {}).get(endpoint)
        if not path_spec:
            # Try to find with path parameters replaced
            path_spec = self._find_path_with_params(endpoint)
            if not path_spec:
                errors.append(f"Endpoint not found in spec: {endpoint}")
                return errors
        
        # Get method spec
        method_spec = path_spec.get(method.lower())
        if not method_spec:
            errors.append(f"Method {method} not found for endpoint {endpoint}")
            return errors
        
        # Get response spec for status code
        responses = method_spec.get('responses', {})
        response_spec = responses.get(str(status_code))
        if not response_spec:
            # Try default response
            response_spec = responses.get('default')
            if not response_spec:
                errors.append(
                    f"Status code {status_code} not documented for "
                    f"{method} {endpoint}"
                )
                return errors
        
        # Validate response body
        if 'content' in response_spec:
            content_spec = response_spec['content'].get('application/json')
            if content_spec and 'schema' in content_spec:
                schema = content_spec['schema']
                errors.extend(self._validate_schema(response, schema, path='response'))
        
        return errors
    
    def _find_path_with_params(self, endpoint: str) -> Optional[Dict]:
        """Find endpoint spec accounting for path parameters."""
        endpoint_parts = endpoint.split('/')
        
        for spec_path in self.spec.get('paths', {}).keys():
            spec_parts = spec_path.split('/')
            
            if len(spec_parts) != len(endpoint_parts):
                continue
            
            match = True
            for spec_part, endpoint_part in zip(spec_parts, endpoint_parts):
                if spec_part.startswith('{') and spec_part.endswith('}'):
                    # Path parameter, matches any value
                    continue
                if spec_part != endpoint_part:
                    match = False
                    break
            
            if match:
                return self.spec['paths'][spec_path]
        
        return None
    
    def _validate_schema(
        self, 
        data: Any, 
        schema: Dict, 
        path: str = 'root'
    ) -> List[str]:
        """
        Recursively validate data against JSON schema.
        
        Args:
            data: Data to validate
            schema: JSON Schema definition
            path: Current path in data structure (for error messages)
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Resolve $ref if present
        if '$ref' in schema:
            ref_path = schema['$ref']
            schema = self._resolve_ref(ref_path)
        
        # Check type
        expected_type = schema.get('type')
        if expected_type:
            if not self._check_type(data, expected_type):
                errors.append(
                    f"Type mismatch at {path}: "
                    f"expected {expected_type}, got {type(data).__name__}"
                )
                return errors  # Can't continue validation if type is wrong
        
        # Validate based on type
        if expected_type == 'object' or isinstance(data, dict):
            errors.extend(self._validate_object(data, schema, path))
        elif expected_type == 'array' or isinstance(data, list):
            errors.extend(self._validate_array(data, schema, path))
        elif expected_type == 'string':
            errors.extend(self._validate_string(data, schema, path))
        elif expected_type in ['integer', 'number']:
            errors.extend(self._validate_number(data, schema, path))
        
        return errors
    
    def _validate_object(self, data: Dict, schema: Dict, path: str) -> List[str]:
        """Validate object against schema."""
        errors = []
        
        # Check required properties
        required = schema.get('required', [])
        for prop in required:
            if prop not in data:
                errors.append(f"Missing required property at {path}.{prop}")
        
        # Validate properties
        properties = schema.get('properties', {})
        for prop, prop_schema in properties.items():
            if prop in data:
                prop_path = f"{path}.{prop}"
                errors.extend(
                    self._validate_schema(data[prop], prop_schema, prop_path)
                )
        
        # Check for additional properties
        if schema.get('additionalProperties') is False:
            allowed_props = set(properties.keys())
            actual_props = set(data.keys())
            extra_props = actual_props - allowed_props
            if extra_props:
                errors.append(
                    f"Unexpected properties at {path}: {', '.join(extra_props)}"
                )
        
        return errors
    
    def _validate_array(self, data: List, schema: Dict, path: str) -> List[str]:
        """Validate array against schema."""
        errors = []
        
        # Check min/max items
        min_items = schema.get('minItems')
        if min_items is not None and len(data) < min_items:
            errors.append(
                f"Array at {path} has {len(data)} items, "
                f"minimum is {min_items}"
            )
        
        max_items = schema.get('maxItems')
        if max_items is not None and len(data) > max_items:
            errors.append(
                f"Array at {path} has {len(data)} items, "
                f"maximum is {max_items}"
            )
        
        # Validate items
        items_schema = schema.get('items')
        if items_schema:
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                errors.extend(self._validate_schema(item, items_schema, item_path))
        
        return errors
    
    def _validate_string(self, data: str, schema: Dict, path: str) -> List[str]:
        """Validate string against schema."""
        errors = []
        
        # Check pattern
        pattern = schema.get('pattern')
        if pattern:
            import re
            if not re.match(pattern, data):
                errors.append(
                    f"String at {path} does not match pattern: {pattern}"
                )
        
        # Check length
        min_length = schema.get('minLength')
        if min_length is not None and len(data) < min_length:
            errors.append(
                f"String at {path} is too short: {len(data)} < {min_length}"
            )
        
        max_length = schema.get('maxLength')
        if max_length is not None and len(data) > max_length:
            errors.append(
                f"String at {path} is too long: {len(data)} > {max_length}"
            )
        
        # Check enum
        enum = schema.get('enum')
        if enum and data not in enum:
            errors.append(
                f"String at {path} is not in allowed values: {enum}"
            )
        
        return errors
    
    def _validate_number(self, data: Union[int, float], schema: Dict, path: str) -> List[str]:
        """Validate number against schema."""
        errors = []
        
        # Check minimum
        minimum = schema.get('minimum')
        if minimum is not None and data < minimum:
            errors.append(f"Number at {path} is too small: {data} < {minimum}")
        
        # Check maximum
        maximum = schema.get('maximum')
        if maximum is not None and data > maximum:
            errors.append(f"Number at {path} is too large: {data} > {maximum}")
        
        # Check multiple of
        multiple_of = schema.get('multipleOf')
        if multiple_of and data % multiple_of != 0:
            errors.append(
                f"Number at {path} is not a multiple of {multiple_of}"
            )
        
        return errors
    
    def _check_type(self, data: Any, expected_type: str) -> bool:
        """Check if data matches expected type."""
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if not expected_python_type:
            return True  # Unknown type, assume valid
        
        return isinstance(data, expected_python_type)
    
    def _resolve_ref(self, ref_path: str) -> Dict:
        """Resolve JSON schema $ref."""
        if not ref_path.startswith('#/'):
            raise ValueError(f"Only local refs supported: {ref_path}")
        
        parts = ref_path[2:].split('/')
        result = self.spec
        
        for part in parts:
            result = result.get(part, {})
        
        return result
    
    def validate_multiple(
        self, 
        test_cases: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Validate multiple test cases.
        
        Args:
            test_cases: List of dicts with keys:
                - endpoint: API endpoint
                - method: HTTP method
                - status_code: Expected status code
                - response: Response body
                
        Returns:
            Dict mapping test case identifiers to error lists
        """
        results = {}
        
        for i, test_case in enumerate(test_cases):
            identifier = test_case.get('name', f"test_{i}")
            errors = self.validate_response(
                test_case['endpoint'],
                test_case['method'],
                test_case.get('status_code', 200),
                test_case['response']
            )
            results[identifier] = errors
        
        return results


def main():
    """CLI interface for API contract validation."""
    parser = argparse.ArgumentParser(
        description='Validate API responses against OpenAPI specifications'
    )
    parser.add_argument(
        'spec',
        help='Path to OpenAPI specification file (JSON or YAML)'
    )
    parser.add_argument(
        '--endpoint',
        required=True,
        help='API endpoint path (e.g., /users/{id})'
    )
    parser.add_argument(
        '--method',
        default='GET',
        help='HTTP method (default: GET)'
    )
    parser.add_argument(
        '--status',
        type=int,
        default=200,
        help='HTTP status code (default: 200)'
    )
    parser.add_argument(
        '--response',
        help='Response JSON file or JSON string'
    )
    parser.add_argument(
        '--test-suite',
        help='JSON file with multiple test cases'
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    try:
        validator = APIContractValidator(args.spec)
        print(f"✅ Loaded OpenAPI spec: {args.spec}")
    except Exception as e:
        print(f"❌ Error loading spec: {e}", file=sys.stderr)
        return 1
    
    # Single test case
    if args.response:
        try:
            # Try to load as file first
            response_path = Path(args.response)
            if response_path.exists():
                with open(response_path) as f:
                    response = json.load(f)
            else:
                # Try to parse as JSON string
                response = json.loads(args.response)
            
            errors = validator.validate_response(
                args.endpoint,
                args.method,
                args.status,
                response
            )
            
            if errors:
                print(f"\n❌ Validation failed for {args.method} {args.endpoint}:")
                for error in errors:
                    print(f"  - {error}")
                return 1
            else:
                print(f"\n✅ Validation passed for {args.method} {args.endpoint}")
                return 0
                
        except Exception as e:
            print(f"❌ Error validating response: {e}", file=sys.stderr)
            return 1
    
    # Test suite
    elif args.test_suite:
        try:
            with open(args.test_suite) as f:
                test_cases = json.load(f)
            
            results = validator.validate_multiple(test_cases)
            
            failed = 0
            passed = 0
            
            print("\n📊 Test Results:")
            print("=" * 60)
            
            for name, errors in results.items():
                if errors:
                    failed += 1
                    print(f"\n❌ {name}:")
                    for error in errors:
                        print(f"  - {error}")
                else:
                    passed += 1
                    print(f"✅ {name}")
            
            print("\n" + "=" * 60)
            print(f"Passed: {passed}, Failed: {failed}, Total: {passed + failed}")
            
            return 1 if failed > 0 else 0
            
        except Exception as e:
            print(f"❌ Error running test suite: {e}", file=sys.stderr)
            return 1
    
    else:
        print("❌ Either --response or --test-suite must be provided", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
