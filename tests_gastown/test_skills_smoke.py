#!/usr/bin/env python3
"""Skills discovery smoke test for gastown/kimi-cli fork.

Verifies that kimi discovers skills from ~/.kimi/skills/ and
that the compound-engineering skills are available as /skill:*
slash commands via the wire protocol.

Run with:
  python tests_gastown/test_skills_smoke.py
  uv run python tests_gastown/test_skills_smoke.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import uuid


PASS = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
_passed = 0
_failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global _passed, _failed
    if condition:
        print(f"  {PASS} {name}")
        _passed += 1
    else:
        print(f"  {FAIL} {name} {detail}")
        _failed += 1


def _find_kimi() -> list[str]:
    """Find the kimi command — prefer kimi from PATH, fall back to uv run."""
    if shutil.which("kimi"):
        return ["kimi"]
    if os.path.exists("pyproject.toml") and shutil.which("uv"):
        return ["uv", "run", "kimi"]
    return [sys.executable, "-m", "kimi_cli"]


def main() -> int:
    global _passed, _failed

    print("=" * 60)
    print("GASTOWN SKILLS DISCOVERY SMOKE TEST")
    print("=" * 60)

    kimi_cmd = _find_kimi()
    print(f"Using: {' '.join(kimi_cmd)}")

    # ── Test 1: Wire handshake and skill enumeration ─────────
    print("\n── Wire handshake for skill discovery ──")

    proc = subprocess.Popen(
        [*kimi_cmd, "--wire"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    time.sleep(1)
    if proc.poll() is not None:
        stderr = proc.stderr.read() if proc.stderr else ""
        print(f"  kimi --wire exited immediately (code {proc.returncode})")
        print(f"  stderr: {stderr[:500]}")
        check("Wire server starts", False)
        print(f"\nRESULTS: {_passed}/{_passed + _failed} passed, {_failed} failed")
        return 1

    check("Wire server starts", True)

    try:
        init_id = str(uuid.uuid4())
        init_req = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": init_id,
            "params": {
                "protocol_version": "1.1",
                "client": {"name": "gastown-skills-test", "version": "0.1.0"},
            },
        }

        line = json.dumps(init_req) + "\n"
        assert proc.stdin is not None
        assert proc.stdout is not None
        try:
            proc.stdin.write(line)
            proc.stdin.flush()
        except BrokenPipeError:
            check("Initialize request sent", False, "BrokenPipeError")
            return 1

        resp = None
        for _ in range(50):
            try:
                raw = proc.stdout.readline()
            except (BrokenPipeError, OSError):
                break
            if not raw:
                break
            raw = raw.strip()
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if "id" in msg and msg["id"] == init_id:
                resp = msg
                break

        check("Initialize response received", resp is not None)

        if resp and "result" in resp:
            result = resp["result"]
            commands = result.get("slash_commands", [])
            command_names = [cmd["name"] for cmd in commands]

            print(f"\n  Total slash commands: {len(command_names)}")

            # ── Test 2: Core gastown skills present ──────────
            print("\n── Core workflow skills ──")

            core_skills = [
                "skill:workflows-plan",
                "skill:workflows-work",
                "skill:workflows-review",
                "skill:workflows-compound",
                "skill:workflows-brainstorm",
                "skill:lfg",
                "skill:deepen-plan",
                "skill:technical-review",
                "skill:triage",
            ]

            for skill_name in core_skills:
                check(
                    f"/{skill_name} available",
                    skill_name in command_names,
                    f"not found in {len(command_names)} commands",
                )

            # ── Test 3: Compound-engineering plugin skills ────
            print("\n── Compound-engineering plugin skills ──")

            plugin_skills = [
                "skill:brainstorming",
                "skill:compound-docs",
                "skill:frontend-design",
                "skill:git-worktree",
                "skill:orchestrating-swarms",
                "skill:file-todos",
                "skill:document-review",
            ]

            for skill_name in plugin_skills:
                check(
                    f"/{skill_name} available",
                    skill_name in command_names,
                    f"not found in {len(command_names)} commands",
                )

            # ── Test 4: Minimum skill count ──────────────────
            print("\n── Skill count ──")
            skill_commands = [n for n in command_names if n.startswith("skill:")]
            print(f"  Skills discovered: {len(skill_commands)}")
            check(
                "At least 20 skills discovered",
                len(skill_commands) >= 20,
                f"got {len(skill_commands)}",
            )

            # ── Test 5: Built-in commands still present ──────
            print("\n── Built-in commands preserved ──")
            builtins = ["clear", "init", "compact"]
            for cmd_name in builtins:
                check(
                    f"/{cmd_name} available",
                    cmd_name in command_names,
                    f"not found",
                )

    finally:
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except BrokenPipeError:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    total = _passed + _failed
    print(f"RESULTS: {_passed}/{total} passed, {_failed} failed")
    print("=" * 60)
    return 0 if _failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
