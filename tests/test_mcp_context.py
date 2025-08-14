"""Unit tests for MCP context module."""
import pytest

from src.mcp_context import build_context_instructions


class TestMCPContext:
    """Test MCP context generation functionality."""
    
    def test_build_context_instructions_single_repo(self):
        """Test building context instructions for a single repository."""
        result = build_context_instructions(
            ado_org="test-org",
            ado_project="test-project", 
            ado_repos=["test-repo"]
        )
        
        assert "test-org" not in result  # org not included in output
        assert "test-project" in result
        assert "test-repo" in result
        assert "mcp_ado_repo_get_repo_by_name_or_id" in result
        assert "mcp_ado_repo_search_commits" in result
        assert "mcp_ado_search_code" in result
        assert "mcp_ado_wit_get_work_item" in result
        assert "Summarize: key findings" in result
        # Check for new context window guidance
        assert "CRITICAL - Context Window Management" in result
    
    def test_build_context_instructions_multiple_repos(self):
        """Test building context instructions for multiple repositories."""
        result = build_context_instructions(
            ado_org="test-org",
            ado_project="test-project",
            ado_repos=["repo1", "repo2", "repo3"]
        )
        
        assert "repo1" in result
        assert "repo2" in result  
        assert "repo3" in result
        # With new format, it's a strategy section, not individual commands per repo
        assert "Multi-Repository Analysis" in result
        assert "test-project" in result
    
    def test_build_context_instructions_empty_repos(self):
        """Test building context instructions with empty repository list."""
        result = build_context_instructions(
            ado_org="test-org",
            ado_project="test-project",
            ado_repos=[]
        )
        
        # Should still have the summary section
        assert "Summarize: key findings" in result
        # Should have context window guidance even with no repos
        assert "CRITICAL - Context Window Management" in result
        # Should handle empty repo list gracefully
        assert "Multi-Repository Analysis" in result
    
    def test_build_context_instructions_formatting(self):
        """Test that context instructions are properly formatted."""
        result = build_context_instructions(
            ado_org="test-org",
            ado_project="my-project",
            ado_repos=["my-repo"]
        )
        
        lines = result.split('\n')
        
        # Should have proper markdown formatting
        assert any("**my-repo**" in line for line in lines)
        assert any("(project: my-project)" in line for line in lines)
        
        # Should have bullet points in MCP commands section
        assert any(line.strip().startswith('- ') for line in lines)
        
        # Should end with summary instructions
        assert "Summarize:" in result
        assert "testing approach" in result
