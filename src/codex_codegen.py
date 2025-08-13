import json, subprocess, tempfile, os
from .config import Settings

def run_codex(prompt_text: str) -> int:
    # Non-interactive execution. Requires OPENAI_API_KEY or prior auth.
    env = os.environ.copy()
    if Settings.OPENAI_API_KEY:
        env["OPENAI_API_KEY"] = Settings.OPENAI_API_KEY

    # Write prompt to a temp file; codex can take a string arg directly too.
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
        f.write(prompt_text)
        path = f.name

    # --full-auto lets Codex execute planned edits/commands; consider reducing for safety.
    cmd = ["codex", "exec", "--full-auto", f"run codegen from file:{path}"]
    return subprocess.call(cmd, env=env)
