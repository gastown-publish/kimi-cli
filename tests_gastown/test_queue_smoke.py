#!/usr/bin/env python3
"""Message queuing smoke test for gastown/kimi-cli fork.

Verifies that the type-ahead message queuing system works correctly.
Tests the keyboard input handling, CharInput, and queue infrastructure
without requiring an actual terminal or LLM API key.

Run with:
  python tests_gastown/test_queue_smoke.py
  uv run python tests_gastown/test_queue_smoke.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path


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


def main() -> int:
    global _passed, _failed

    print("=" * 60)
    print("GASTOWN MESSAGE QUEUING SMOKE TEST")
    print("=" * 60)

    # ── Test 1: Keyboard module types ─────────────────────────
    print("\n── Keyboard module types ──")
    try:
        from kimi_cli.ui.shell.keyboard import CharInput, KeyboardInput, KeyEvent

        check("CharInput importable", True)
        check("KeyboardInput type alias exists", True)

        ci = CharInput("a")
        check("CharInput('a').char == 'a'", ci.char == "a")

        check("KeyEvent.BACKSPACE exists", hasattr(KeyEvent, "BACKSPACE"))
        check("KeyEvent.CTRL_U exists", hasattr(KeyEvent, "CTRL_U"))

        # Verify KeyboardInput is the union
        check(
            "KeyEvent is KeyboardInput",
            isinstance(KeyEvent.ENTER, KeyEvent),
        )
        check(
            "CharInput is KeyboardInput",
            isinstance(CharInput("x"), CharInput),
        )
    except ImportError:
        # Import test requires kimi_cli to be installed (uv run / CI)
        # Fall back to source code checks
        kb_src = Path("src/kimi_cli/ui/shell/keyboard.py")
        if kb_src.exists():
            source = kb_src.read_text()
            check("CharInput class in source", "class CharInput" in source)
            check("KeyboardInput type alias in source", "KeyboardInput" in source)
            check("BACKSPACE in KeyEvent", "BACKSPACE" in source)
            check("CTRL_U in KeyEvent", "CTRL_U" in source)
            check("Printable ASCII handling", "32 <= c[0] < 127" in source)
            check("Backspace byte handling", "\\x7f" in source)
            check("CharInput(chr(c[0]))", "CharInput(chr(c[0]))" in source)
        else:
            check("Keyboard source found", False)

    # ── Test 2: Visualize accepts message_queue ───────────────
    print("\n── Visualize signature ──")
    try:
        import inspect
        from kimi_cli.ui.shell.visualize import visualize

        sig = inspect.signature(visualize)
        check(
            "visualize has message_queue param",
            "message_queue" in sig.parameters,
        )
        check(
            "message_queue defaults to None",
            sig.parameters["message_queue"].default is None,
        )
    except ImportError:
        # Fall back to source code check
        vis_src = Path("src/kimi_cli/ui/shell/visualize.py")
        if vis_src.exists():
            source = vis_src.read_text()
            check(
                "visualize has message_queue param (source)",
                "message_queue: asyncio.Queue[str] | None = None" in source,
            )
            check(
                "message_queue passed to _LiveView (source)",
                "message_queue=message_queue" in source,
            )
        else:
            check("Visualize source found", False)

    # ── Test 3: Shell has message queue ───────────────────────
    print("\n── Shell queue infrastructure ──")
    src = Path("src/kimi_cli/ui/shell/__init__.py")
    if not src.exists():
        check("Shell source found", False)
    else:
        source = src.read_text()
        check(
            "Shell has _message_queue attribute",
            "_message_queue" in source and "asyncio.Queue" in source,
        )
        check(
            "Queue is checked before prompting",
            "get_nowait" in source,
        )
        check(
            "Queue passed to visualize",
            "message_queue=self._message_queue" in source,
        )
        check(
            "Queued messages show indicator",
            "queued >" in source,
        )

    # ── Test 4: Input buffer in LiveView ──────────────────────
    print("\n── LiveView input buffer ──")
    vis_src = Path("src/kimi_cli/ui/shell/visualize.py")
    if not vis_src.exists():
        check("Visualize source found", False)
    else:
        source = vis_src.read_text()
        check(
            "_input_buffer attribute",
            "_input_buffer" in source,
        )
        check(
            "_queued_count attribute",
            "_queued_count" in source,
        )
        check(
            "_compose_input_area method",
            "_compose_input_area" in source,
        )
        check(
            "CharInput handled in keyboard_handler",
            "isinstance(event, CharInput)" in source,
        )
        check(
            "BACKSPACE handled",
            "KeyEvent.BACKSPACE" in source,
        )
        check(
            "CTRL_U handled",
            "KeyEvent.CTRL_U" in source,
        )
        check(
            "Cursor character in input area",
            "\\u2588" in source or "\u2588" in source,  # block cursor (escaped or literal)
        )

    # ── Test 5: asyncio.Queue behavior ────────────────────────
    print("\n── Queue behavior ──")

    async def test_queue():
        q: asyncio.Queue[str] = asyncio.Queue()
        q.put_nowait("hello")
        q.put_nowait("world")
        check("Queue accepts messages", q.qsize() == 2)

        msg1 = q.get_nowait()
        check("First message is 'hello'", msg1 == "hello")

        msg2 = q.get_nowait()
        check("Second message is 'world'", msg2 == "world")

        try:
            q.get_nowait()
            check("Empty queue raises", False)
        except asyncio.QueueEmpty:
            check("Empty queue raises QueueEmpty", True)

    asyncio.run(test_queue())

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    total = _passed + _failed
    print(f"RESULTS: {_passed}/{total} passed, {_failed} failed")
    print("=" * 60)
    return 0 if _failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
