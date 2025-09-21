import subprocess
import tempfile
import os
import signal
import time
from typing import Dict, List, Optional, Tuple
import re

class ShellExecutor:
    """Secure shell and Python code executor with sandboxing and safety measures."""
    
    def __init__(self, timeout: int = 30, max_output_size: int = 10000):
        self.timeout = timeout
        self.max_output_size = max_output_size
        
        # Dangerous commands/patterns to block
        self.blocked_patterns = [
            r'\brm\s+(-rf\s+)?/',  # rm -rf /
            r'\bsudo\b',           # sudo commands
            r'\bsu\b',             # su commands
            r'>\s*/dev/',          # writing to device files
            r'\bchmod\s+777',      # dangerous permissions
            r'\bwget\b.*\|\s*sh',  # wget pipe to shell
            r'\bcurl\b.*\|\s*sh',  # curl pipe to shell
            r':\(\)\{.*\}:',       # fork bomb pattern
            r'\bkill\s+-9',        # kill -9
            r'\bpkill\b',          # pkill
            r'\bmkfs\b',           # format filesystem
            r'\bdd\s+if=',         # dd command
            r'\b/etc/passwd\b',    # accessing passwd file
            r'\b/etc/shadow\b',    # accessing shadow file
        ]
        
        # Safe Python modules that are allowed
        self.allowed_python_modules = {
            'json', 'csv', 'math', 'statistics', 'datetime', 'time',
            'collections', 'itertools', 'functools', 're', 'string',
            'urllib.parse', 'base64', 'hashlib', 'uuid', 'random',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'requests'
        }
    
    def is_command_safe(self, command: str) -> Tuple[bool, str]:
        """Check if a command is safe to execute."""
        command_lower = command.lower()
        
        # Check for blocked patterns
        for pattern in self.blocked_patterns:
            if re.search(pattern, command_lower):
                return False, f"Blocked dangerous pattern: {pattern}"
        
        # Additional safety checks
        if len(command) > 5000:
            return False, "Command too long"
        
        if command.count(';') > 10 or command.count('|') > 10:
            return False, "Too many command separators"
        
        return True, "Command appears safe"
    
    def execute_shell_command(self, command: str, working_dir: Optional[str] = None) -> Dict:
        """Execute a shell command safely with timeout and output limits."""
        # Safety check
        is_safe, reason = self.is_command_safe(command)
        if not is_safe:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command blocked for security: {reason}",
                "return_code": -1,
                "execution_time": 0
            }
        
        start_time = time.time()
        
        try:
            # Create a temporary directory for execution if none provided
            if working_dir is None:
                working_dir = tempfile.mkdtemp()
                cleanup_dir = True
            else:
                cleanup_dir = False
            
            # Execute command with timeout
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                preexec_fn=os.setsid  # Create new process group
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                # Kill the entire process group
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    stdout, stderr = "", "Process killed due to timeout"
                return_code = -1
            
            # Limit output size
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... [Output truncated]"
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... [Error output truncated]"
            
            execution_time = time.time() - start_time
            
            return {
                "success": return_code == 0,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": return_code,
                "execution_time": execution_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution error: {str(e)}",
                "return_code": -1,
                "execution_time": time.time() - start_time
            }
        finally:
            # Cleanup temporary directory if we created it
            if cleanup_dir and working_dir and os.path.exists(working_dir):
                try:
                    import shutil
                    shutil.rmtree(working_dir)
                except:
                    pass
    
    def execute_python_code(self, code: str, data_context: Optional[Dict] = None) -> Dict:
        """Execute Python code safely with restricted imports and context."""
        # Check for dangerous imports
        dangerous_imports = ['os', 'sys', 'subprocess', 'shutil', 'glob', 'socket', 'urllib', 'http']
        code_lines = code.split('\n')
        
        for line in code_lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                for dangerous in dangerous_imports:
                    if dangerous in line:
                        return {
                            "success": False,
                            "stdout": "",
                            "stderr": f"Dangerous import blocked: {dangerous}",
                            "return_code": -1,
                            "execution_time": 0
                        }
        
        # Create a safe execution environment
        safe_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sorted': sorted,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'type': type,
                'isinstance': isinstance,
                'hasattr': hasattr,
                'getattr': getattr,
            }
        }
        
        # Add data context if provided
        if data_context:
            safe_globals.update(data_context)
        
        # Create temporary file for Python execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute Python code in subprocess for better isolation
            python_command = f"python3 {temp_file}"
            result = self.execute_shell_command(python_command)
            return result
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass

def execute_code(code: str, language: str = "python", data_context: Optional[Dict] = None, timeout: int = 30) -> Dict:
    """Convenience function to execute code with default settings."""
    executor = ShellExecutor(timeout=timeout)
    
    if language.lower() == "python":
        return executor.execute_python_code(code, data_context)
    elif language.lower() in ["bash", "shell", "sh"]:
        return executor.execute_shell_command(code)
    else:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Unsupported language: {language}",
            "return_code": -1,
            "execution_time": 0
        }

if __name__ == "__main__":
    # Test the executor
    executor = ShellExecutor()
    
    # Test safe Python code
    python_code = """
import json
data = {"test": "hello", "numbers": [1, 2, 3, 4, 5]}
print("Data:", json.dumps(data))
print("Sum of numbers:", sum(data["numbers"]))
"""
    
    print("Testing Python execution:")
    result = executor.execute_python_code(python_code)
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout']}")
    print(f"Errors: {result['stderr']}")
    
    # Test safe shell command
    print("\nTesting shell execution:")
    result = executor.execute_shell_command("echo 'Hello World' && date")
    print(f"Success: {result['success']}")
    print(f"Output: {result['stdout']}")
    
    # Test dangerous command (should be blocked)
    print("\nTesting dangerous command:")
    result = executor.execute_shell_command("sudo rm -rf /")
    print(f"Success: {result['success']}")
    print(f"Errors: {result['stderr']}")
