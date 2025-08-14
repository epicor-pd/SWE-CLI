"""Safe MCP tool execution with automatic output size handling."""

import logging
from typing import Any, Callable, Dict

from .mcp_output_utils import safe_mcp_output, log_large_content_warning

logger = logging.getLogger(__name__)


class SafeMCPWrapper:
    """Wrapper for MCP tools that automatically handles large outputs."""
    
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
    
    def execute_safely(self, tool_func: Callable, *args, **kwargs) -> Any:
        """
        Execute an MCP tool safely, truncating large outputs.
        
        Args:
            tool_func: The MCP tool function to execute
            *args: Positional arguments for the tool
            **kwargs: Keyword arguments for the tool
            
        Returns:
            The tool result with safe output sizes
        """
        try:
            logger.debug("Executing MCP tool: %s", self.tool_name)
            result = tool_func(*args, **kwargs)
            
            # Check if result contains large strings and log warning
            if isinstance(result, str):
                log_large_content_warning(result, self.tool_name)
            elif isinstance(result, dict):
                for key, value in result.items():
                    if isinstance(value, str):
                        log_large_content_warning(value, f"{self.tool_name}.{key}")
            
            # Make result safe for MCP transmission
            safe_result = safe_mcp_output(result)
            logger.debug("MCP tool %s completed successfully", self.tool_name)
            return safe_result
            
        except Exception as e:
            logger.error("Error executing MCP tool %s: %s", self.tool_name, e)
            raise


def create_safe_mcp_tools() -> Dict[str, SafeMCPWrapper]:
    """Create safe wrappers for commonly used MCP tools."""
    tools = [
        "repo_get_repo_by_name_or_id",
        "repo_list_branches_by_repo", 
        "repo_list_pull_requests_by_project",
        "search_code",
        "wit_get_work_item",
        "wit_list_work_item_comments",
        "build_get_builds",
        "build_get_log",
        "build_get_log_by_id"
    ]
    
    return {tool: SafeMCPWrapper(tool) for tool in tools}


# Example usage patterns that can be documented
SAFE_MCP_PATTERNS = {
    "search_code": {
        "description": "Search repository code with automatic result truncation",
        "example": """
# Safe code search that won't cause string length errors
safe_tools = create_safe_mcp_tools()
wrapper = safe_tools["search_code"]
result = wrapper.execute_safely(mcp_ado_search_code, 
                               searchText="your search term",
                               project=["your-project"])
""",
        "tips": [
            "Be specific with search terms to reduce result size",
            "Consider multiple smaller searches instead of one large search"
        ]
    },
    
    "build_logs": {
        "description": "Get build logs with automatic truncation",
        "example": """
# Safe build log retrieval
wrapper = safe_tools["build_get_log"]
result = wrapper.execute_safely(mcp_ado_build_get_log,
                               project="your-project", 
                               buildId=12345)
""",
        "tips": [
            "Large build logs will be automatically truncated",
            "Use build_get_log_by_id with line ranges for specific log sections",
            "Check logs for multiple builds separately rather than in batch"
        ]
    }
}
