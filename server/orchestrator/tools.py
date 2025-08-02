"""
Orchestrator Tool/Skill Registry and Interface
"""
import subprocess
import requests
from typing import Any, Dict, Callable, List

# Tool interface
def tool_interface(func: Callable) -> Callable:
    func.is_tool = True
    return func

# Tool registry
tool_registry: Dict[str, Callable] = {}

def register_tool(name: str, func: Callable):
    tool_registry[name] = func

# SECURITY: Code execution disabled for safety
@tool_interface  
def execute_code(code: str, lang: str = "python") -> Dict[str, Any]:
    """
    SECURITY WARNING: Direct code execution is disabled to prevent arbitrary code execution.
    Consider implementing a secure sandbox environment if code execution is required.
    """
    return {
        "error": "Code execution disabled for security reasons. Use a secure sandbox environment.",
        "success": False,
        "security_note": "exec() calls are dangerous and can lead to arbitrary code execution vulnerabilities"
    }

register_tool("execute_code", execute_code)

# Example tool: web search (stub)
@tool_interface
def web_search(query: str) -> Dict[str, Any]:
    # In production, integrate with a real search API
    return {"result": f"Search results for '{query}' (stub)", "success": True}

register_tool("web_search", web_search)

# Tool invocation logic
def call_tool(tool_name: str, **kwargs) -> Any:
    tool = tool_registry.get(tool_name)
    if not tool:
        return {"error": f"Tool '{tool_name}' not found", "success": False}
    return tool(**kwargs)

# List available tools
def list_tools() -> List[str]:
    return list(tool_registry.keys())
