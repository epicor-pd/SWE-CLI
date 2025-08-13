from jira import JIRA
from .config import Settings
import logging
logger = logging.getLogger(__name__)

def get_jira_client():
    logger.debug("Initializing Jira client for server=%s user=%s", Settings.JIRA_SERVER, Settings.JIRA_USER)
    options = {"server": Settings.JIRA_SERVER}
    return JIRA(options=options, basic_auth=(Settings.JIRA_USER, Settings.JIRA_API_TOKEN))

def fetch_issue(issue_key: str) -> dict:
    logger.info("Fetching Jira issue: %s", issue_key)
    jira = get_jira_client()
    issue = jira.issue(issue_key)
    fields = issue.fields
    logger.debug("Fetched issue fields for %s; issuetype=%s project=%s labels=%s",
                 issue.key,
                 getattr(fields.issuetype, "name", None),
                 getattr(fields.project, "key", None),
                 list(getattr(fields, "labels", []) or []))
    return {
        "key": issue.key,
        "summary": fields.summary,
        "description": getattr(fields, "description", None),
        "labels": list(getattr(fields, "labels", []) or []),
        "issuetype": fields.issuetype.name if getattr(fields, "issuetype", None) else None,
        "project": fields.project.key if getattr(fields, "project", None) else None,
        "raw": issue.raw,
    }
