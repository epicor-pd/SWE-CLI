import logging

from .mcp_output_utils import get_content_size_info, summarize_large_content

logger = logging.getLogger(__name__)


def build_context_instructions(
    ado_org: str, ado_project: str, ado_repos: list[str]
) -> str:
    logger.info(
        "Building MCP context instructions for org=%s project=%s repos=%s",
        ado_org,
        ado_project,
        ",".join(ado_repos),
    )
    
    # Build more focused, token-efficient instructions
    repo_count = len(ado_repos)
    if repo_count == 1:
        repo_section = f"""
**Repository Analysis** (project: {ado_project}):
Target repo: **{ado_repos[0]}**

Essential MCP commands (use selectively):
- `mcp_ado_repo_get_repo_by_name_or_id` (project: {ado_project}, repo: {ado_repos[0]})
- `mcp_ado_repo_search_commits` - Recent changes analysis  
- `mcp_ado_repo_list_pull_requests_by_repo` - PR patterns
- `mcp_ado_search_code` - Target specific modules/tests only
- `mcp_ado_wit_get_work_item` - If work items linked
"""
    else:
        repo_names = ", ".join(f"**{r}**" for r in ado_repos[:3])  # Limit displayed repos
        if repo_count > 3:
            repo_names += f" and {repo_count - 3} more"
            
        repo_section = f"""
**Multi-Repository Analysis** (project: {ado_project}):
Repos: {repo_names}

MCP Strategy (be selective to avoid token limits):
- Focus on primary repo from Jira context
- Use `mcp_ado_search_code` with specific search terms
- Limit `repo_list_pull_requests_by_repo` results  
- Check `repo_get_repo_by_name_or_id` for key repos only
"""

    instructions = f"""{repo_section}

**CRITICAL - Context Window Management**:
- Be highly selective with MCP tool usage
- Use specific search terms, not broad queries
- Limit result counts (top=5-10 for lists)
- Focus on files/modules mentioned in Jira
- If tools return large outputs, request summaries

**Analysis Priority**:
1. Understand Jira requirement specifics
2. Search for existing similar implementations  
3. Identify test patterns and conventions
4. Review recent PRs in target area
5. Check for related work items

**Before Implementation**:
Summarize: key findings, affected modules, risks, and testing approach.
"""
    
    # Log if instructions are getting large and apply intelligent truncation
    size_info = get_content_size_info(instructions)
    if size_info['character_count'] > 3000:  # Reduced threshold
        logger.warning(
            "Context instructions are large: %d characters for %d repos, applying truncation",
            size_info['character_count'], len(ado_repos)
        )
        # Apply truncation to keep instructions concise
        instructions = summarize_large_content(instructions, max_length=2500)
    
    return instructions
