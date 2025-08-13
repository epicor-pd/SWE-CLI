import json, subprocess, tempfile, os, logging
from pathlib import Path
from .config import Settings
logger = logging.getLogger(__name__)

def run_codex(prompt_text: str, workspace: str | Path) -> int:
    env = os.environ.copy()
    if Settings.OPENAI_API_KEY:
        env["OPENAI_API_KEY"] = Settings.OPENAI_API_KEY

    # with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
    #     f.write(prompt_text)
    #     path = f.name

    cmd = ["codex", "exec", "--full-auto", "--sandbox", "danger-full-access", f"{prompt_text}"]
    logger.info("Launching Codex CLI (non-interactive)")
    logger.debug("Codex command: %s", " ".join(cmd))
    rc = subprocess.call(cmd, env=env, cwd=workspace)
    logger.info("Codex finished with exit code=%s", rc)
    return rc
