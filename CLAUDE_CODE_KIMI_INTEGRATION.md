# Claude Code with Kimi Engine

A guide to running Claude Code with Moonshot AI's Kimi K2.5 as the underlying LLM engine.

## Overview

This setup uses **Claude Code** (Anthropic's CLI coding agent) with **Kimi K2.5** as the LLM backend. Claude Code handles the UI, tool orchestration, and agentic workflow, while Kimi provides the language model capabilities.

**Key Insight**: Kimi provides a native Anthropic-compatible API endpoint, so Claude Code can connect directly without any proxy or translation layer.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE + KIMI DIRECT SETUP                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    HTTP (Anthropic API format)    ┌─────────────────┐ │
│  │             │ ◄────────────────────────────────► │                 │ │
│  │ Claude Code │         (Native compatibility)     │  Kimi K2.5 API  │ │
│  │   (CLI)     │                                    │                 │ │
│  │             │    ANTHROPIC_BASE_URL=             │  • Reasoning    │ │
│  │  • Tools    │    https://api.kimi.com/coding/    │  • Generation   │ │
│  │  • UI       │                                    │  • 128k context │ │
│  │  • Agent    │    ANTHROPIC_API_KEY=              │                 │ │
│  │             │    sk-kimi-...                     │                 │ │
│  └─────────────┘                                    └─────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## How It Works

### 1. Claude Code (The Frontend)

Claude Code provides:
- **Interactive shell UI** with syntax highlighting
- **Tool orchestration** (file read/write, shell commands, web search)
- **Agentic workflow** (planning, execution, self-correction)
- **Context management** (conversation history, compaction)
- **Approval system** for dangerous operations

### 2. Kimi's Anthropic-Compatible API

Kimi offers a native Anthropic-compatible endpoint at:
```
https://api.kimi.com/coding/
```

This endpoint:
- Accepts the same request format as Anthropic's API
- Returns responses in Anthropic format
- Supports tool calling
- Supports streaming
- Handles reasoning models

### 3. Configuration via Environment Variables

Claude Code reads these environment variables:

```bash
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_API_KEY="sk-kimi-YOUR_API_KEY_HERE"
```

When these are set, Claude Code connects to Kimi instead of Anthropic.

## Installation & Setup

### Prerequisites

1. **Claude Code** installed
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Kimi API Key**
   - Get from: https://platform.moonshot.cn/
   - Or: https://www.kimi.com/code

### Method 1: Direct Environment Variables

```bash
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_API_KEY="sk-kimi-YOUR_API_KEY_HERE"

# Run Claude Code
claude --dangerously-skip-permissions
```

### Method 2: Using the `kimigas` Wrapper Script

The `kimigas` script handles configuration automatically:

```bash
#!/usr/bin/env bash
# kimigas - Claude Code with Kimi K2.5 backend

# Kimi's native Anthropic-compatible endpoint
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_API_KEY="${KIMI_API_KEY:-${ANTHROPIC_API_KEY:-}}"

# Run Claude Code
exec claude --dangerously-skip-permissions "$@"
```

Save as `~/bin/kimigas`, make executable:
```bash
chmod +x ~/bin/kimigas
```

Then use:
```bash
kimigas --yolo
```

### Method 3: Full Featured Setup (as used in this server)

The production `kimigas` script includes additional features:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Kimi's native Anthropic-compatible endpoint
export ANTHROPIC_BASE_URL="https://api.kimi.com/coding/"
export ANTHROPIC_API_KEY="${KIMI_API_KEY:-${ANTHROPIC_API_KEY:-sk-kimi-...}}"
export DISABLE_COST_WARNINGS="true"

# Use separate config dir to avoid OAuth conflicts
KIMIGAS_CONFIG="${HOME}/.claude-kimigas"

# Setup config directory if needed
if [[ ! -d "$KIMIGAS_CONFIG" ]]; then
    mkdir -p "$KIMIGAS_CONFIG"

    # Copy essential config from main Claude config
    for f in .claude.json settings.json keybindings.json; do
        [[ -f "${HOME}/.claude/$f" ]] && cp "${HOME}/.claude/$f" "$KIMIGAS_CONFIG/$f" 2>/dev/null || true
    done

    # Empty credentials (forces API key auth instead of OAuth)
    echo '{}' > "$KIMIGAS_CONFIG/.credentials.json"

    # Mark onboarding complete and pre-approve API key
    # ... (Node.js setup script) ...
fi

export CLAUDE_CONFIG_DIR="$KIMIGAS_CONFIG"

# Map flags
ARGS=()
for arg in "$@"; do
    case "$arg" in
        --yolo|--yes|-y)
            ARGS+=("--dangerously-skip-permissions")
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
done

exec claude "${ARGS[@]}"
```

## Why Use a Separate Config Directory?

Claude Code prefers OAuth authentication. To force API key authentication, we use a separate config directory (`~/.claude-kimigas`) that:

1. **Has empty credentials** - No OAuth tokens, forcing API key use
2. **Pre-approves the API key** - Skips the "approve this API key" prompt
3. **Marks onboarding complete** - Skips the welcome wizard
4. **Isolates settings** - Doesn't interfere with regular Claude Code usage

## How Tool Execution Works

```
User: "Find all Python files and count lines"

┌─────────────┐      Anthropic API format      ┌─────────────┐
│ Claude Code │ ─────────────────────────────► │  Kimi K2.5  │
│             │                                │             │
│             │ ◄───────────────────────────── │             │
└─────────────┘     tool_call: Glob(...)       └─────────────┘
       │
       ▼
Execute Glob tool
       │
       ▼
┌─────────────┐      tool_result: [...]        ┌─────────────┐
│ Claude Code │ ─────────────────────────────► │  Kimi K2.5  │
│             │                                │             │
│             │ ◄───────────────────────────── │             │
└─────────────┘    "Found 5 files..."          └─────────────┘
```

## Available Endpoints

| Endpoint | URL | Use Case |
|----------|-----|----------|
| **KimiCode API** | `https://api.kimi.com/coding/` | Coding-optimized Kimi K2.5 |
| **Moonshot Platform** | `https://api.moonshot.cn/v1` | General Kimi models |

## Comparison: CCR vs Direct API

| Approach | Pros | Cons |
|----------|------|------|
| **Direct API** (this setup) | Simple, no proxy, lower latency | Single provider |
| **CCR** | Multiple providers, transformers, local vLLM | More complex, extra hop |

## Gas Town Integration

This server uses `kimigas` as the default agent:

```bash
# Set as default
gt config agent set kimigas "kimigas --yolo"

# Use with crew
gt crew start myrig myname --agent kimigas

# Use with sling
gt sling gt-abc myrig --agent kimigas
```

## Troubleshooting

### Issue: Claude Code still tries to use OAuth

**Solution**: Use separate config directory:
```bash
export CLAUDE_CONFIG_DIR="$HOME/.claude-kimigas"
```

### Issue: API key not recognized

**Solution**: Verify key format:
```bash
curl https://api.kimi.com/coding/v1/models \
  -H "Authorization: Bearer $ANTHROPIC_API_KEY"
```

### Issue: Tool calling not working

**Solution**: KimiCode API supports tool calling natively. If issues occur, check:
- API endpoint is `api.kimi.com/coding/` (not moonshot.cn)
- Model supports tools (`kimi-for-coding`, `kimi-k2.5`)

## Resources

- **Claude Code**: https://docs.anthropic.com/en/docs/claude-code/overview
- **Kimi Code**: https://www.kimi.com/code
- **Moonshot Platform**: https://platform.moonshot.cn/

---

*This setup uses Kimi's native Anthropic-compatible API for seamless integration with Claude Code.*
