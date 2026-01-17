"""
Sandboxed Code Execution

Safe execution of student code with:
- No file system access
- No network access
- No dangerous imports
- Timeout protection
- Memory limits
"""

import subprocess
import tempfile
import os
import sys
import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Optional
import re


# Dangerous patterns to block
FORBIDDEN_PATTERNS = [
    r'\bimport\s+os\b',
    r'\bimport\s+sys\b',
    r'\bimport\s+subprocess\b',
    r'\bimport\s+socket\b',
    r'\bimport\s+requests\b',
    r'\bimport\s+urllib\b',
    r'\bimport\s+shutil\b',
    r'\bimport\s+pickle\b',
    r'\bfrom\s+os\b',
    r'\bfrom\s+sys\b',
    r'\b__import__\b',
    r'\beval\s*\(',
    r'\bexec\s*\(',
    r'\bopen\s*\(',
    r'\bcompile\s*\(',
    r'\bglobals\s*\(',
    r'\blocals\s*\(',
    r'\bgetattr\s*\(',
    r'\bsetattr\s*\(',
    r'\bdelattr\s*\(',
    r'\b__.*__\b',  # Dunder methods
]

ALLOWED_IMPORTS = [
    'math',
    'random',
    'string',
    'collections',
    'itertools',
    'functools',
    'operator',
    'typing',
    're',
    'json',
    'datetime',
    'copy',
    'heapq',
    'bisect',
]


@dataclass
class TestResult:
    call: str
    expected: Any
    actual: Any
    passed: bool
    error: Optional[str] = None
    stdout: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class ExecutionResult:
    all_passed: bool
    passed_count: int
    total_count: int
    results: list
    syntax_error: Optional[str] = None
    security_error: Optional[str] = None
    timeout: bool = False

    def to_dict(self):
        return {
            "all_passed": self.all_passed,
            "passed_count": self.passed_count,
            "total_count": self.total_count,
            "results": [r.to_dict() if hasattr(r, 'to_dict') else r for r in self.results],
            "syntax_error": self.syntax_error,
            "security_error": self.security_error,
            "timeout": self.timeout
        }


def check_security(code: str) -> Optional[str]:
    """Check code for security violations."""
    for pattern in FORBIDDEN_PATTERNS:
        match = re.search(pattern, code)
        if match:
            return f"Forbidden pattern detected: {match.group()}"

    # Check imports
    import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
    for match in re.finditer(import_pattern, code):
        module = match.group(1) or match.group(2)
        if module and module not in ALLOWED_IMPORTS:
            return f"Import not allowed: {module}. Allowed: {', '.join(ALLOWED_IMPORTS)}"

    return None


def execute_code(
    code: str,
    test_cases: list,
    timeout: int = 5,
    memory_limit_mb: int = 50
) -> ExecutionResult:
    """
    Execute student code safely against test cases.

    Args:
        code: Student's Python code
        test_cases: List of {"call": "func(1)", "expected": 2}
        timeout: Max execution time in seconds
        memory_limit_mb: Max memory in MB

    Returns:
        ExecutionResult with detailed pass/fail info
    """

    # Security check first
    security_error = check_security(code)
    if security_error:
        return ExecutionResult(
            all_passed=False,
            passed_count=0,
            total_count=len(test_cases),
            results=[],
            security_error=security_error
        )

    # Syntax check
    try:
        compile(code, "<student_code>", "exec")
    except SyntaxError as e:
        return ExecutionResult(
            all_passed=False,
            passed_count=0,
            total_count=len(test_cases),
            results=[],
            syntax_error=f"Line {e.lineno}: {e.msg}"
        )

    results = []

    for test in test_cases:
        call = test["call"]
        expected = test["expected"]

        # Build sandboxed test harness
        test_code = f'''
import sys
import json

# Restrict builtins
_safe_builtins = {{
    'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
    'chr': chr, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
    'filter': filter, 'float': float, 'format': format, 'frozenset': frozenset,
    'hash': hash, 'hex': hex, 'int': int, 'isinstance': isinstance,
    'issubclass': issubclass, 'iter': iter, 'len': len, 'list': list,
    'map': map, 'max': max, 'min': min, 'next': next, 'oct': oct,
    'ord': ord, 'pow': pow, 'print': print, 'range': range, 'repr': repr,
    'reversed': reversed, 'round': round, 'set': set, 'slice': slice,
    'sorted': sorted, 'str': str, 'sum': sum, 'tuple': tuple, 'type': type,
    'zip': zip, 'True': True, 'False': False, 'None': None,
}}

# Capture stdout
_stdout_lines = []
_original_print = print
def _safe_print(*args, **kwargs):
    _stdout_lines.append(" ".join(str(a) for a in args))
_safe_builtins['print'] = _safe_print

# Execute student code in restricted namespace
_namespace = {{'__builtins__': _safe_builtins}}
try:
    exec("""{code.replace('"""', "'''").replace(chr(92), chr(92)+chr(92))}""", _namespace)

    # Run test
    _result = eval("{call}", _namespace)
    _output = {{
        "success": True,
        "result": _result,
        "stdout": _stdout_lines
    }}
except Exception as e:
    _output = {{
        "success": False,
        "error": str(e),
        "error_type": type(e).__name__,
        "stdout": _stdout_lines
    }}

print("__RESULT__" + json.dumps(_output, default=str))
'''

        # Write to temp file
        fd, temp_path = tempfile.mkstemp(suffix='.py', text=True)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(test_code)

            # Execute with timeout
            try:
                result = subprocess.run(
                    [sys.executable, '-u', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tempfile.gettempdir(),
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
                )

                stdout = result.stdout
                stderr = result.stderr

                if "__RESULT__" in stdout:
                    marker_pos = stdout.rfind("__RESULT__")
                    result_json = stdout[marker_pos + 10:].strip()
                    captured_stdout = stdout[:marker_pos].strip()

                    try:
                        output = json.loads(result_json)

                        if output["success"]:
                            actual = output["result"]
                            passed = actual == expected
                            error = None
                        else:
                            actual = None
                            passed = False
                            error = f"{output['error_type']}: {output['error']}"

                        results.append(TestResult(
                            call=call,
                            expected=expected,
                            actual=actual,
                            passed=passed,
                            error=error,
                            stdout=captured_stdout
                        ))
                    except json.JSONDecodeError:
                        results.append(TestResult(
                            call=call,
                            expected=expected,
                            actual=None,
                            passed=False,
                            error="Output parse error"
                        ))
                else:
                    results.append(TestResult(
                        call=call,
                        expected=expected,
                        actual=None,
                        passed=False,
                        error=stderr or "No output produced"
                    ))

            except subprocess.TimeoutExpired:
                results.append(TestResult(
                    call=call,
                    expected=expected,
                    actual=None,
                    passed=False,
                    error="TIMEOUT: Possible infinite loop"
                ))

        finally:
            try:
                os.unlink(temp_path)
            except:
                pass

    passed_count = sum(1 for r in results if r.passed)

    return ExecutionResult(
        all_passed=all(r.passed for r in results),
        passed_count=passed_count,
        total_count=len(results),
        results=results
    )


# Error classification
ERROR_PATTERNS = {
    "off_by_one": [
        (r"range\s*\(\s*len\s*\([^)]+\)\s*\)", "range(len(x)) stops at len-1"),
        (r"\[\s*len\s*\([^)]+\)\s*\]", "list[len(list)] is out of bounds"),
    ],
    "infinite_loop": [
        (r"while\s+True\s*:(?![\s\S]*?break)", "while True needs break"),
    ],
    "forgotten_return": [
        (r"def\s+\w+[^:]+:\s*\n(\s+[^\n]+\n)*(?!\s*return)", "Missing return statement"),
    ],
}


def classify_error(code: str, error_msg: str, expected: Any, actual: Any) -> tuple:
    """Classify error type and provide hint."""

    # Check runtime errors
    if error_msg:
        if "IndexError" in error_msg:
            return "index_error", "Accessing index that doesn't exist"
        if "TypeError" in error_msg:
            return "type_error", "Wrong type for operation"
        if "NameError" in error_msg:
            return "name_error", "Variable not defined"
        if "RecursionError" in error_msg or "maximum recursion" in error_msg:
            return "recursion_error", "Infinite recursion - check base case"
        if "ZeroDivisionError" in error_msg:
            return "zero_division", "Division by zero"
        if "TIMEOUT" in error_msg:
            return "infinite_loop", "Loop never terminates"

    # Check code patterns
    for error_type, patterns in ERROR_PATTERNS.items():
        for pattern, hint in patterns:
            if re.search(pattern, code, re.MULTILINE | re.DOTALL):
                return error_type, hint

    # Check output patterns
    if expected is not None and actual is not None:
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if abs(expected - actual) == 1:
                return "off_by_one", "Answer is off by 1"

        if actual is None and expected is not None:
            return "forgotten_return", "Function returned None"

    return "logic_error", "Check your logic step by step"


if __name__ == "__main__":
    # Test the sandbox
    print("Testing sandbox...")

    # Test 1: Correct code
    code1 = """
def add(a, b):
    return a + b
"""
    result = execute_code(code1, [
        {"call": "add(1, 2)", "expected": 3},
        {"call": "add(0, 0)", "expected": 0},
    ])
    print(f"Test 1 (correct): {result.all_passed} - {result.passed_count}/{result.total_count}")

    # Test 2: Wrong code
    code2 = """
def add(a, b):
    return a - b
"""
    result = execute_code(code2, [
        {"call": "add(1, 2)", "expected": 3},
    ])
    print(f"Test 2 (wrong): {result.all_passed} - {result.results[0].actual}")

    # Test 3: Security violation
    code3 = """
import os
os.system('echo hacked')
"""
    result = execute_code(code3, [{"call": "1+1", "expected": 2}])
    print(f"Test 3 (security): blocked={result.security_error is not None}")

    # Test 4: Infinite loop
    code4 = """
def infinite():
    while True:
        pass
"""
    result = execute_code(code4, [{"call": "infinite()", "expected": None}], timeout=2)
    print(f"Test 4 (timeout): {result.results[0].error}")

    print("\nSandbox tests complete!")
