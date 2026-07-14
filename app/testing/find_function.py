#!/usr/bin/env python3
"""
Function Finder Script
Searches for function definitions in a Python project and displays their location,
module path, and how to import them.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_functions(search_term: str, root_dir: str = ".") -> List[Tuple[str, int, str]]:
    """
    Search for function definitions matching the search term.
    
    Args:
        search_term: Function name to search for (supports regex patterns)
        root_dir: Root directory to search from
        
    Returns:
        List of tuples: (file_path, line_number, function_signature)
    """
    results = []
    # Pattern to match function definitions: def function_name(...)
    pattern = re.compile(rf"^\s*def\s+{re.escape(search_term)}\s*\(")
    
    root_path = Path(root_dir)
    
    # Walk through all Python files
    for py_file in root_path.rglob("*.py"):
        # Skip common directories
        if any(skip in py_file.parts for skip in [".venv", "venv", "__pycache__", ".git", "node_modules"]):
            continue
            
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if pattern.match(line):
                        # Extract the full function signature
                        signature = line.strip()
                        results.append((str(py_file), line_num, signature))
        except (UnicodeDecodeError, PermissionError):
            # Skip files that can't be read
            pass
    
    return results


def get_import_statement(file_path: str, root_dir: str = ".") -> str:
    """
    Generate the import statement needed to use the function.
    
    Args:
        file_path: Path to the file containing the function
        root_dir: Root directory of the project
        
    Returns:
        Import statement string
    """
    root_path = Path(root_dir).resolve()
    file_path_resolved = Path(file_path).resolve()
    
    try:
        # Get relative path from root
        rel_path = file_path_resolved.relative_to(root_path)
        
        # Convert path to module notation
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        module_path = ".".join(module_parts)
        
        return module_path
    except ValueError:
        return file_path


def format_results(results: List[Tuple[str, int, str]], search_term: str, root_dir: str = ".") -> str:
    """
    Format the search results nicely.
    
    Args:
        results: List of result tuples
        search_term: The function that was searched for
        root_dir: Root directory used for search
        
    Returns:
        Formatted string for display
    """
    if not results:
        return f"[!] No functions named '{search_term}' found."
    
    output = f"\n[+] Found {len(results)} function(s) named '{search_term}':\n"
    output += "=" * 80 + "\n"
    
    for file_path, line_num, signature in results:
        module_path = get_import_statement(file_path, root_dir)
        func_name = search_term
        
        output += f"\n[*] File: {file_path}\n"
        output += f"    Line: {line_num}\n"
        output += f"    Signature: {signature}\n"
        output += f"\n    [>] Import as:\n"
        output += f"        from {module_path} import {func_name}\n"
        output += f"    Or:\n"
        output += f"        import {module_path}\n"
        output += f"        {module_path}.{func_name}(...)\n"
        output += "-" * 80
    
    return output


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_function.py <function_name> [root_directory]")
        print("\nExamples:")
        print("  python find_function.py init_user_db")
        print("  python find_function.py table_exists .")
        print("  python find_function.py my_function ./src")
        sys.exit(1)
    
    search_term = sys.argv[1]
    root_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # Validate root directory
    if not Path(root_dir).exists():
        print(f"[ERROR] Directory '{root_dir}' does not exist.")
        sys.exit(1)
    
    results = find_functions(search_term, root_dir)
    output = format_results(results, search_term, root_dir)
    print(output)


if __name__ == "__main__":
    main()
