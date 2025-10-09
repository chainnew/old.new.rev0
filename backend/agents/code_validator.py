"""
Code Validator - Validate generated code before marking complete
Run syntax checks, type checks, basic validation
"""
import subprocess
import json
import tempfile
import os
from typing import Dict, List, Any
from pathlib import Path


class CodeValidator:
    """Validate code - catch errors before user sees them"""

    def __init__(self):
        self.validation_levels = ['syntax', 'types', 'imports']

    async def validate_output(self, files: List[Dict[str, Any]], project_path: str = None) -> Dict:
        """
        Validate generated code files

        Returns:
            {
                'valid': bool,
                'errors': List[Dict],
                'warnings': List[Dict],
                'validations': Dict (syntax, types, imports results)
            }
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'validations': {}
        }

        if not files:
            return results

        # Create temp directory for validation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write files to temp dir
            written_files = []
            for file_data in files:
                filepath = os.path.join(temp_dir, file_data.get('filename', 'generated.ts'))
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                with open(filepath, 'w') as f:
                    f.write(file_data.get('code', ''))

                written_files.append(filepath)

            # Run validations
            syntax_result = self.validate_syntax(written_files)
            results['validations']['syntax'] = syntax_result

            if not syntax_result['passed']:
                results['valid'] = False
                results['errors'].extend(syntax_result['errors'])

            # Type checking (TypeScript)
            ts_files = [f for f in written_files if f.endswith(('.ts', '.tsx'))]
            if ts_files:
                types_result = self.validate_types(ts_files, temp_dir)
                results['validations']['types'] = types_result

                if not types_result['passed']:
                    results['valid'] = False
                    results['errors'].extend(types_result['errors'])

            # Import validation
            imports_result = self.validate_imports(written_files)
            results['validations']['imports'] = imports_result

            if not imports_result['passed']:
                results['warnings'].extend(imports_result['warnings'])

        return results

    def validate_syntax(self, files: List[str]) -> Dict:
        """Quick syntax check - does it parse?"""
        errors = []

        for filepath in files:
            ext = Path(filepath).suffix

            try:
                with open(filepath, 'r') as f:
                    code = f.read()

                # JavaScript/TypeScript - check with Node
                if ext in ['.js', '.jsx', '.ts', '.tsx']:
                    result = subprocess.run(
                        ['node', '--check', filepath],
                        capture_output=True,
                        timeout=5
                    )

                    if result.returncode != 0:
                        errors.append({
                            'file': filepath,
                            'type': 'syntax_error',
                            'message': result.stderr.decode('utf-8')
                        })

                # Python - compile check
                elif ext == '.py':
                    try:
                        compile(code, filepath, 'exec')
                    except SyntaxError as e:
                        errors.append({
                            'file': filepath,
                            'type': 'syntax_error',
                            'message': f'Line {e.lineno}: {e.msg}'
                        })

            except Exception as e:
                errors.append({
                    'file': filepath,
                    'type': 'validation_error',
                    'message': str(e)
                })

        return {
            'passed': len(errors) == 0,
            'errors': errors
        }

    def validate_types(self, ts_files: List[str], project_dir: str) -> Dict:
        """
        TypeScript type checking
        Run tsc --noEmit to check types without generating output
        """
        errors = []

        try:
            # Create minimal tsconfig.json
            tsconfig = {
                'compilerOptions': {
                    'target': 'ES2020',
                    'module': 'commonjs',
                    'jsx': 'react',
                    'strict': False,  # Not too strict for quick validation
                    'noEmit': True,
                    'skipLibCheck': True,
                    'esModuleInterop': True
                },
                'include': ['**/*.ts', '**/*.tsx']
            }

            tsconfig_path = os.path.join(project_dir, 'tsconfig.json')
            with open(tsconfig_path, 'w') as f:
                json.dump(tsconfig, f)

            # Run tsc
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit', '--project', tsconfig_path],
                capture_output=True,
                timeout=30,
                cwd=project_dir
            )

            if result.returncode != 0:
                # Parse tsc errors
                error_output = result.stdout.decode('utf-8')
                for line in error_output.split('\n'):
                    if line.strip() and ': error TS' in line:
                        errors.append({
                            'type': 'type_error',
                            'message': line.strip()
                        })

        except subprocess.TimeoutExpired:
            errors.append({
                'type': 'timeout',
                'message': 'Type checking timed out (> 30s)'
            })
        except FileNotFoundError:
            # tsc not available - skip type checking
            return {'passed': True, 'errors': [], 'skipped': 'tsc not available'}
        except Exception as e:
            errors.append({
                'type': 'validation_error',
                'message': f'Type checking failed: {str(e)}'
            })

        return {
            'passed': len(errors) == 0,
            'errors': errors
        }

    def validate_imports(self, files: List[str]) -> Dict:
        """
        Check for obvious import issues
        - Relative imports that don't exist
        - Common typos
        """
        warnings = []

        for filepath in files:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()

                # Check for common import issues
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Check for relative imports
                    if 'import' in line and ('./' in line or '../' in line):
                        # Extract import path
                        import_match = line.split("from '")[1].split("'")[0] if "from '" in line else None
                        if import_match and not import_match.startswith('@'):
                            warnings.append({
                                'file': filepath,
                                'line': i,
                                'type': 'relative_import',
                                'message': f'Relative import: {import_match} (verify file exists)'
                            })

                    # Check for common typos in imports
                    typos = ['reqiure', 'improt', 'form ', 'impor from']
                    for typo in typos:
                        if typo in line.lower():
                            warnings.append({
                                'file': filepath,
                                'line': i,
                                'type': 'typo',
                                'message': f'Possible typo: {line.strip()}'
                            })

            except Exception as e:
                pass  # Ignore import validation errors

        return {
            'passed': True,  # Warnings don't fail validation
            'warnings': warnings
        }

    def create_fix_suggestions(self, validation_result: Dict) -> List[str]:
        """
        Generate actionable fix suggestions from validation errors
        """
        suggestions = []

        for error in validation_result.get('errors', []):
            error_type = error.get('type')
            message = error.get('message', '')

            if error_type == 'syntax_error':
                suggestions.append(f"Fix syntax error: {message}")
            elif error_type == 'type_error':
                suggestions.append(f"Fix type error: {message}")
            elif error_type == 'import_error':
                suggestions.append(f"Fix import: {message}")

        return suggestions

    def should_retry_with_fixes(self, validation_result: Dict) -> bool:
        """
        Should we ask agent to regenerate with fixes?
        """
        # If syntax or type errors, definitely retry
        error_types = [e.get('type') for e in validation_result.get('errors', [])]

        critical_errors = ['syntax_error', 'type_error']
        has_critical = any(t in critical_errors for t in error_types)

        return has_critical and len(validation_result.get('errors', [])) <= 5  # Max 5 errors to fix


# Global singleton
_validator = None


def get_code_validator() -> CodeValidator:
    """Get or create global validator"""
    global _validator
    if _validator is None:
        _validator = CodeValidator()
    return _validator
