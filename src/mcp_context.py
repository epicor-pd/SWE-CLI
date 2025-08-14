import logging

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
    repo_lines = []
    for r in ado_repos:
        repo_lines.append(
            f"""
For repo **{r}** (project: {ado_project}):
- repo_get_repo_by_name_or_id (project: {ado_project}, repo: {r})
- repo_list_branches_by_repo
- repo_list_pull_requests_by_project
- search_code (target modules/tests)
- wit_get_work_item / wit_list_work_item_comments if linked
"""
        )
    instructions = (
        "\n".join(repo_lines)
        + """
Summarize: recent PRs, touched modules, risk areas, and tests to update before coding.
"""
    )
    return instructions
