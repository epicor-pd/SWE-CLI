import json, subprocess, tempfile, os, logging
from .config import Settings
logger = logging.getLogger(__name__)

def run_codex(prompt_text: str) -> int:
    env = os.environ.copy()
    if Settings.OPENAI_API_KEY:
        env["OPENAI_API_KEY"] = Settings.OPENAI_API_KEY

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write(prompt_text)
        path = f.name

    cmd = ["codex", "exec", "--full-auto", f"run codegen from file:{path}"]
    logger.info("Launching Codex CLI (non-interactive)")
    logger.debug("Codex command: %s", " ".join(cmd))
    rc = subprocess.call(cmd, env=env)
    logger.info("Codex finished with exit code=%s", rc)
    return rc
