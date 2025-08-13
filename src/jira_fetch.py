from jira import JIRA
from .config import Settings

def get_jira_client():
    options = {"server": Settings.JIRA_SERVER}
    return JIRA(options=options, basic_auth=(Settings.JIRA_USER, Settings.JIRA_API_TOKEN))

def fetch_issue(issue_key: str) -> dict:
    jira = get_jira_client()
    issue = jira.issue(issue_key)  # GET /rest/api/3/issue/{key}
    fields = issue.fields
    return {
        "key": issue.key,
        "summary": fields.summary,
        "description": getattr(fields, "description", None),
        "labels": list(getattr(fields, "labels", []) or []),
        "issuetype": fields.issuetype.name if getattr(fields, "issuetype", None) else None,
        "project": fields.project.key if getattr(fields, "project", None) else None,
        "raw": issue.raw,
    }
