def build_context_instructions(ado_org: str, ado_project: str, ado_repo: str) -> str:
    return f"""
When planning changes, first use the Azure DevOps MCP tools:
- repo_get_repo_by_name_or_id (project: {ado_project}, repo: {ado_repo})
- repo_list_branches_by_repo
- repo_list_pull_requests_by_project
- search_code (for relevant modules/tests)
- wit_get_work_item / wit_list_work_item_comments if linked

Summarize key findings (recent PRs, affected modules, test coverage) before coding.
"""
