import argparse, json, logging, os
from pathlib import Path
from .config import Settings
from .logging_setup import configure_logging
from .jira_fetch import fetch_issue
from .mcp_context import build_context_instructions
from .codex_codegen import run_codex

def _parse_repos(val: str) -> list[str]:
    # comma-or-space separated list
    parts = [p.strip() for p in val.replace(",", " ").split()]
    return [p for p in parts if p]

def main():
    configure_logging()
    logger = logging.getLogger(__name__)

    ap = argparse.ArgumentParser()
    ap.add_argument("--jira", required=True, help="Jira issue key, e.g., EP-1234")
    ap.add_argument("--ado-org", default=Settings.ADO_ORG)
    ap.add_argument("--ado-project", default=Settings.ADO_PROJECT)
    ap.add_argument("--ado-repo", required=False, help="One or more repos (comma or space separated)")
    ap.add_argument("--workspace", required=False, default=os.getcwd(), help="Directory where code changes should be applied")
    args = ap.parse_args()

    ado_repos = _parse_repos(args.ado_repo or Settings.ADO_REPO or "")
    if not ado_repos:
        raise SystemExit("Provide at least one repo via --ado-repo or ADO_REPO env var")

    logger.info("Starting run for issue=%s org=%s project=%s repos=%s",
                args.jira, args.ado_org, args.ado_project, ",".join(ado_repos))

    issue = fetch_issue(args.jira)
    ctx = build_context_instructions(args.ado_org, args.ado_project, ado_repos)

    prompt = Path("prompts/codegen.md").read_text()
    prompt = prompt.replace("{{JIRA_JSON}}", json.dumps(issue, indent=2))
    prompt = prompt.replace("{{CONTEXT_INSTRUCTIONS}}", ctx)

    ws = Path(args.workspace).expanduser().resolve()
    exit(run_codex(prompt, ws))

if __name__ == "__main__":
    main()
