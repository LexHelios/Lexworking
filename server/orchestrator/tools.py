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

# Example tool: code execution
@tool_interface
def execute_code(code: str, lang: str = "python") -> Dict[str, Any]:
    if lang == "python":
        try:
            exec_globals = {}
            exec(code, exec_globals)
            return {"result": exec_globals.get("result", None), "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    return {"error": "Unsupported language", "success": False}

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
