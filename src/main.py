import argparse, json
from .config import Settings
from .jira_fetch import fetch_issue
from .mcp_context import build_context_instructions
from .codex_codegen import run_codex
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jira", required=True, help="Jira issue key, e.g., EP-1234")
    ap.add_argument("--ado-org", default=Settings.ADO_ORG)
    ap.add_argument("--ado-project", default=Settings.ADO_PROJECT)
    ap.add_argument("--ado-repo", default=Settings.ADO_REPO)
    args = ap.parse_args()

    issue = fetch_issue(args.jira)
    ctx = build_context_instructions(args.ado_org, args.ado_project, args.ado_repo)

    # Build the final prompt
    prompt = Path("prompts/codegen.md").read_text()
    prompt = prompt.replace("{{JIRA_JSON}}", json.dumps(issue, indent=2))
    prompt = prompt.replace("{{CONTEXT_INSTRUCTIONS}}", ctx)

    exit(run_codex(prompt))

if __name__ == "__main__":
    main()
