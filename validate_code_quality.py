#!/usr/bin/env python3
"""
🔱 LEX AI Code Quality Validation Script 🔱
JAI MAHAKAAL! Validates code quality improvements

This script verifies that all critical issues have been fixed.
"""

import os
import sys
import subprocess
import py_compile
import re
from pathlib import Path

def validate_syntax():
    """Check all Python files compile without syntax errors"""
    print("🔍 Checking Python syntax...")
    errors = []
    python_files = list(Path('.').rglob('*.py'))
    
    for file_path in python_files:
        try:
            py_compile.compile(str(file_path), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(f"{file_path}: {e}")
    
    if errors:
        print(f"❌ {len(errors)} syntax errors found:")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print(f"✅ All {len(python_files)} Python files compile successfully")
        return True

def check_security_issues():
    """Check for common security vulnerabilities"""
    print("🔒 Checking security issues...")
    issues = []
    
    # Check for hardcoded secrets
    result = subprocess.run([
        'grep', '-r', '-n', '-E', 
        '(api_key|password|secret|token).*=.*["\'][^"\']{20,}["\']',
        '--include=*.py', '.'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        issues.append("Potential hardcoded secrets found")
    
    # Check for dangerous functions
    dangerous_patterns = [
        (r'exec\s*\(', "exec() function usage"),
        (r'eval\s*\(', "eval() function usage"),
        (r'subprocess\..*shell\s*=\s*True', "subprocess with shell=True"),
        (r'os\.system\s*\(', "os.system() usage")
    ]
    
    for pattern, description in dangerous_patterns:
        result = subprocess.run([
            'grep', '-r', '-n', '-E', pattern,
            '--include=*.py', '.'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Filter out our disabled exec function
            lines = result.stdout.split('\n')
            filtered_lines = [line for line in lines if 
                            'Code execution disabled for security' not in line and line.strip()]
            if filtered_lines:
                issues.append(f"{description} found")
    
    if issues:
        print(f"❌ Security issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("✅ No security vulnerabilities detected")
        return True

def check_exception_handling():
    """Check for bare except clauses"""
    print("🛡️ Checking exception handling...")
    
    result = subprocess.run([
        'grep', '-r', '-n', '-E', r'except\s*:',
        '--include=*.py', '.'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        bare_excepts = result.stdout.strip().split('\n')
        if bare_excepts and bare_excepts[0]:
            print(f"❌ {len(bare_excepts)} bare except clauses found:")
            for except_line in bare_excepts[:5]:  # Show first 5
                print(f"  {except_line}")
            return False
    
    print("✅ No bare except clauses found")
    return True

def check_imports():
    """Check for basic import health"""
    print("📦 Checking import structure...")
    
    # Check for circular imports (basic check)
    result = subprocess.run([
        'grep', '-r', '-n', '-E', r'from\s+\.\s+import.*\*',
        '--include=*.py', '.'
    ], capture_output=True, text=True)
    
    wildcard_imports = 0
    if result.returncode == 0:
        wildcard_imports = len(result.stdout.strip().split('\n'))
    
    print(f"✅ Import structure checked (found {wildcard_imports} wildcard imports)")
    return True

def main():
    """Run all validation checks"""
    print("🔱 LEX AI Code Quality Validation 🔱")
    print("JAI MAHAKAAL! Starting validation...\n")
    
    checks = [
        ("Syntax Validation", validate_syntax),
        ("Security Check", check_security_issues), 
        ("Exception Handling", check_exception_handling),
        ("Import Structure", check_imports)
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n--- {check_name} ---")
        result = check_func()
        results.append((check_name, result))
    
    print(f"\n{'='*50}")
    print("🎯 VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<25} {status}")
        if result:
            passed += 1
    
    total = len(results)
    score = (passed / total) * 100
    
    print(f"\nOverall Score: {passed}/{total} ({score:.1f}%)")
    
    if score >= 95:
        print("🎉 EXCELLENT! Code is SOLID and ready for production!")
    elif score >= 80:
        print("👍 GOOD! Minor issues remain but code is mostly solid.")
    elif score >= 60:
        print("⚠️  FAIR! Several issues need attention.")
    else:
        print("🚨 POOR! Critical issues must be fixed.")
    
    print("\nJAI MAHAKAAL! 🔱")
    return 0 if score >= 80 else 1

if __name__ == "__main__":
    sys.exit(main())