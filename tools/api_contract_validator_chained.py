#!/usr/bin/env python3
"""
API Contract Validator for Chained
Created by @bridge-master for Mission idea:30

Validates API responses against OpenAPI 3.0 specifications to ensure
contract compliance and prevent breaking changes.

Usage:
    python api_contract_validator_chained.py spec.yaml --endpoint /users/{id} --method GET --response response.json
    python api_contract_validator_chained.py spec.yaml --test-suite tests.json
"""

import json
import yaml
import argparse
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path


class APIContractValidator:
    """
    Validates API responses against OpenAPI specifications
    
    Inspired by @bridge-master's principle: Clear contracts prevent bridge collapses.
    """
    
    def __init__(self, spec_path: str):
        """Load and validate OpenAPI specification"""
        self.spec_path = Path(spec_path)
        self.spec = self._load_spec()
        self._validate_spec_structure()
    
    def _load_spec(self) -> Dict:
        """Load OpenAPI spec from YAML or JSON"""
        with open(self.spec_path) as f:
            if self.spec_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def _validate_spec_structure(self):
        """Ensure spec has required OpenAPI fields"""
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in self.spec:
                raise ValueError(f"Invalid OpenAPI spec: missing '{field}' field")
        
        version = self.spec['openapi']
        if not version.startswith('3.'):
            raise ValueError(f"Only OpenAPI 3.x supported, got {version}")
    
    def validate_response(
        self,
        path: str,
        method: str,
        status_code: int,
        response_data: Any,
        headers: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Validate a response against the OpenAPI spec
        
        Args:
            path: API endpoint path (e.g., '/users/{id}')
            method: HTTP method (e.g., 'GET', 'POST')
            status_code: HTTP status code (e.g., 200, 404)
            response_data: The actual response data to validate
            headers: Optional response headers to validate
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Find the path in spec (handle path parameters)
        path_spec = self._find_path_spec(path)
        if not path_spec:
            return [f"Path '{path}' not found in OpenAPI spec"]
        
        # Get method spec
        method_lower = method.lower()
        if method_lower not in path_spec:
            return [f"Method '{method}' not defined for path '{path}'"]
        
        method_spec = path_spec[method_lower]
        
        # Get response spec
        status_str = str(status_code)
        responses_spec = method_spec.get('responses', {})
        
        # Try exact status code, then 'default'
        response_spec = responses_spec.get(status_str)
        if not response_spec:
            response_spec = responses_spec.get('default')
        
        if not response_spec:
            return [f"Status code {status_code} not defined for {method} {path}"]
        
        # Validate response content
        content_spec = response_spec.get('content', {})
        if 'application/json' in content_spec:
            schema = content_spec['application/json'].get('schema')
            if schema:
                schema_errors = self._validate_schema(response_data, schema)
                errors.extend(schema_errors)
        
        # Validate headers if provided
        if headers and 'headers' in response_spec:
            header_errors = self._validate_headers(headers, response_spec['headers'])
            errors.extend(header_errors)
        
        return errors
    
    def _find_path_spec(self, path: str) -> Optional[Dict]:
        """Find path spec, handling path parameters"""
        paths = self.spec.get('paths', {})
        
        # Try exact match first
        if path in paths:
            return paths[path]
        
        # Try matching with path parameters
        path_parts = path.strip('/').split('/')
        
        for spec_path, spec in paths.items():
            spec_parts = spec_path.strip('/').split('/')
            
            if len(spec_parts) != len(path_parts):
                continue
            
            # Check if paths match (considering {param} placeholders)
            match = True
            for spec_part, path_part in zip(spec_parts, path_parts):
                if spec_part.startswith('{') and spec_part.endswith('}'):
                    # Parameter placeholder, matches anything
                    continue
                elif spec_part != path_part:
                    match = False
                    break
            
            if match:
                return spec
        
        return None
    
    def _validate_schema(self, data: Any, schema: Dict) -> List[str]:
        """
        Recursively validate data against JSON schema
        
        Supports:
        - Type validation
        - Required properties
        - Property validation
        - Array validation
        - $ref resolution
        """
        errors = []
        
        # Resolve $ref if present
        if '$ref' in schema:
            schema = self._resolve_ref(schema['$ref'])
        
        # Type validation
        expected_type = schema.get('type')
        if expected_type:
            if not self._check_type(data, expected_type):
                errors.append(
                    f"Type mismatch: expected {expected_type}, "
                    f"got {type(data).__name__}"
                )
                return errors  # Don't continue if type is wrong
        
        # Validate based on type
        if expected_type == 'object':
            errors.extend(self._validate_object(data, schema))
        elif expected_type == 'array':
            errors.extend(self._validate_array(data, schema))
        elif expected_type == 'string':
            errors.extend(self._validate_string(data, schema))
        elif expected_type in ['number', 'integer']:
            errors.extend(self._validate_number(data, schema))
        
        # OneOf, anyOf, allOf validation
        if 'oneOf' in schema:
            errors.extend(self._validate_one_of(data, schema['oneOf']))
        if 'anyOf' in schema:
            errors.extend(self._validate_any_of(data, schema['anyOf']))
        if 'allOf' in schema:
            errors.extend(self._validate_all_of(data, schema['allOf']))
        
        return errors
    
    def _validate_object(self, data: Any, schema: Dict) -> List[str]:
        """Validate object against schema"""
        errors = []
        
        if not isinstance(data, dict):
            return [f"Expected object, got {type(data).__name__}"]
        
        # Required properties
        required = schema.get('required', [])
        for prop in required:
            if prop not in data:
                errors.append(f"Missing required property: '{prop}'")
        
        # Validate properties
        properties = schema.get('properties', {})
        for prop, value in data.items():
            if prop in properties:
                prop_schema = properties[prop]
                prop_errors = self._validate_schema(value, prop_schema)
                for error in prop_errors:
                    errors.append(f"Property '{prop}': {error}")
            elif not schema.get('additionalProperties', True):
                errors.append(f"Unexpected property: '{prop}'")
        
        # Min/max properties
        if 'minProperties' in schema:
            if len(data) < schema['minProperties']:
                errors.append(
                    f"Too few properties: {len(data)} < {schema['minProperties']}"
                )
        if 'maxProperties' in schema:
            if len(data) > schema['maxProperties']:
                errors.append(
                    f"Too many properties: {len(data)} > {schema['maxProperties']}"
                )
        
        return errors
    
    def _validate_array(self, data: Any, schema: Dict) -> List[str]:
        """Validate array against schema"""
        errors = []
        
        if not isinstance(data, list):
            return [f"Expected array, got {type(data).__name__}"]
        
        # Min/max items
        if 'minItems' in schema:
            if len(data) < schema['minItems']:
                errors.append(f"Too few items: {len(data)} < {schema['minItems']}")
        if 'maxItems' in schema:
            if len(data) > schema['maxItems']:
                errors.append(f"Too many items: {len(data)} > {schema['maxItems']}")
        
        # Validate items
        if 'items' in schema:
            item_schema = schema['items']
            for i, item in enumerate(data):
                item_errors = self._validate_schema(item, item_schema)
                for error in item_errors:
                    errors.append(f"Item[{i}]: {error}")
        
        # Unique items
        if schema.get('uniqueItems', False):
            # Convert to JSON strings for comparison
            json_items = [json.dumps(item, sort_keys=True) for item in data]
            if len(json_items) != len(set(json_items)):
                errors.append("Array items must be unique")
        
        return errors
    
    def _validate_string(self, data: Any, schema: Dict) -> List[str]:
        """Validate string against schema"""
        errors = []
        
        if not isinstance(data, str):
            return [f"Expected string, got {type(data).__name__}"]
        
        # Min/max length
        if 'minLength' in schema:
            if len(data) < schema['minLength']:
                errors.append(f"String too short: {len(data)} < {schema['minLength']}")
        if 'maxLength' in schema:
            if len(data) > schema['maxLength']:
                errors.append(f"String too long: {len(data)} > {schema['maxLength']}")
        
        # Pattern matching
        if 'pattern' in schema:
            import re
            pattern = schema['pattern']
            if not re.match(pattern, data):
                errors.append(f"String doesn't match pattern: {pattern}")
        
        # Format validation
        if 'format' in schema:
            format_errors = self._validate_format(data, schema['format'])
            errors.extend(format_errors)
        
        # Enum validation
        if 'enum' in schema:
            if data not in schema['enum']:
                errors.append(f"Value not in enum: {schema['enum']}")
        
        return errors
    
    def _validate_number(self, data: Any, schema: Dict) -> List[str]:
        """Validate number against schema"""
        errors = []
        
        expected_type = schema.get('type')
        if expected_type == 'integer':
            if not isinstance(data, int) or isinstance(data, bool):
                return [f"Expected integer, got {type(data).__name__}"]
        else:  # number
            if not isinstance(data, (int, float)) or isinstance(data, bool):
                return [f"Expected number, got {type(data).__name__}"]
        
        # Min/max
        if 'minimum' in schema:
            if data < schema['minimum']:
                errors.append(f"Number too small: {data} < {schema['minimum']}")
        if 'maximum' in schema:
            if data > schema['maximum']:
                errors.append(f"Number too large: {data} > {schema['maximum']}")
        
        # Exclusive min/max
        if 'exclusiveMinimum' in schema:
            if data <= schema['exclusiveMinimum']:
                errors.append(f"Number must be > {schema['exclusiveMinimum']}")
        if 'exclusiveMaximum' in schema:
            if data >= schema['exclusiveMaximum']:
                errors.append(f"Number must be < {schema['exclusiveMaximum']}")
        
        # Multiple of
        if 'multipleOf' in schema:
            if data % schema['multipleOf'] != 0:
                errors.append(f"Number must be multiple of {schema['multipleOf']}")
        
        return errors
    
    def _validate_format(self, data: str, format_type: str) -> List[str]:
        """Validate string format (email, uri, date, etc.)"""
        import re
        from datetime import datetime
        
        errors = []
        
        if format_type == 'email':
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, data):
                errors.append(f"Invalid email format: {data}")
        
        elif format_type == 'uri':
            pattern = r'^https?://.+'
            if not re.match(pattern, data):
                errors.append(f"Invalid URI format: {data}")
        
        elif format_type == 'date':
            try:
                datetime.strptime(data, '%Y-%m-%d')
            except ValueError:
                errors.append(f"Invalid date format: {data} (expected YYYY-MM-DD)")
        
        elif format_type == 'date-time':
            try:
                datetime.fromisoformat(data.replace('Z', '+00:00'))
            except ValueError:
                errors.append(f"Invalid date-time format: {data}")
        
        elif format_type == 'uuid':
            pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if not re.match(pattern, data.lower()):
                errors.append(f"Invalid UUID format: {data}")
        
        return errors
    
    def _validate_headers(self, headers: Dict[str, str], header_spec: Dict) -> List[str]:
        """Validate response headers"""
        errors = []
        
        for header_name, spec in header_spec.items():
            if spec.get('required', False):
                if header_name.lower() not in {k.lower() for k in headers.keys()}:
                    errors.append(f"Missing required header: {header_name}")
        
        return errors
    
    def _validate_one_of(self, data: Any, schemas: List[Dict]) -> List[str]:
        """Validate data matches exactly one schema"""
        valid_count = 0
        all_errors = []
        
        for schema in schemas:
            errors = self._validate_schema(data, schema)
            if not errors:
                valid_count += 1
            else:
                all_errors.append(errors)
        
        if valid_count == 0:
            return [f"Data doesn't match any oneOf schemas. Errors: {all_errors}"]
        elif valid_count > 1:
            return [f"Data matches multiple oneOf schemas (must match exactly one)"]
        
        return []
    
    def _validate_any_of(self, data: Any, schemas: List[Dict]) -> List[str]:
        """Validate data matches at least one schema"""
        for schema in schemas:
            errors = self._validate_schema(data, schema)
            if not errors:
                return []  # Valid if matches any
        
        return [f"Data doesn't match any anyOf schemas"]
    
    def _validate_all_of(self, data: Any, schemas: List[Dict]) -> List[str]:
        """Validate data matches all schemas"""
        all_errors = []
        
        for schema in schemas:
            errors = self._validate_schema(data, schema)
            all_errors.extend(errors)
        
        return all_errors
    
    def _resolve_ref(self, ref: str) -> Dict:
        """Resolve $ref pointer"""
        if not ref.startswith('#/'):
            raise ValueError(f"External refs not supported: {ref}")
        
        parts = ref[2:].split('/')
        current = self.spec
        
        for part in parts:
            current = current[part]
        
        return current
    
    def _check_type(self, data: Any, expected_type: str) -> bool:
        """Check if data matches expected JSON type"""
        type_map = {
            'string': str,
            'number': (int, float),
            'integer': int,
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if not expected_python_type:
            return False
        
        # Special case: bool is subclass of int in Python
        if expected_type == 'integer' and isinstance(data, bool):
            return False
        if expected_type == 'number' and isinstance(data, bool):
            return False
        
        return isinstance(data, expected_python_type)
    
    def validate_test_suite(self, test_suite_path: str) -> Dict[str, Any]:
        """
        Run a suite of test cases
        
        Test suite format:
        {
            "tests": [
                {
                    "name": "Get user success",
                    "path": "/users/123",
                    "method": "GET",
                    "status_code": 200,
                    "response": {...}
                }
            ]
        }
        """
        with open(test_suite_path) as f:
            test_suite = json.load(f)
        
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        for test in test_suite.get('tests', []):
            results['total'] += 1
            
            errors = self.validate_response(
                path=test['path'],
                method=test['method'],
                status_code=test['status_code'],
                response_data=test['response'],
                headers=test.get('headers')
            )
            
            test_result = {
                'name': test['name'],
                'passed': len(errors) == 0,
                'errors': errors
            }
            
            results['tests'].append(test_result)
            
            if test_result['passed']:
                results['passed'] += 1
            else:
                results['failed'] += 1
        
        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Validate API responses against OpenAPI specifications'
    )
    parser.add_argument(
        'spec',
        help='Path to OpenAPI specification (YAML or JSON)'
    )
    parser.add_argument(
        '--endpoint',
        help='API endpoint path (e.g., /users/{id})'
    )
    parser.add_argument(
        '--method',
        help='HTTP method (e.g., GET, POST)',
        default='GET'
    )
    parser.add_argument(
        '--status',
        type=int,
        help='HTTP status code',
        default=200
    )
    parser.add_argument(
        '--response',
        help='Path to response JSON file'
    )
    parser.add_argument(
        '--test-suite',
        help='Path to test suite JSON file'
    )
    
    args = parser.parse_args()
    
    try:
        validator = APIContractValidator(args.spec)
        
        if args.test_suite:
            # Run test suite
            results = validator.validate_test_suite(args.test_suite)
            
            print(f"\n{'='*60}")
            print(f"API Contract Validation Results")
            print(f"{'='*60}\n")
            print(f"Total Tests: {results['total']}")
            print(f"Passed: {results['passed']} ✅")
            print(f"Failed: {results['failed']} ❌")
            print(f"Success Rate: {results['passed'] / results['total'] * 100:.1f}%\n")
            
            for test in results['tests']:
                status = '✅' if test['passed'] else '❌'
                print(f"{status} {test['name']}")
                if not test['passed']:
                    for error in test['errors']:
                        print(f"    → {error}")
            
            sys.exit(0 if results['failed'] == 0 else 1)
        
        elif args.endpoint and args.response:
            # Validate single endpoint
            with open(args.response) as f:
                response_data = json.load(f)
            
            errors = validator.validate_response(
                path=args.endpoint,
                method=args.method,
                status_code=args.status,
                response_data=response_data
            )
            
            if errors:
                print(f"❌ Validation failed for {args.method} {args.endpoint}")
                print(f"\nErrors:")
                for error in errors:
                    print(f"  → {error}")
                sys.exit(1)
            else:
                print(f"✅ {args.method} {args.endpoint} - Contract valid!")
                sys.exit(0)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
