# Nudging Kimi in Gas Town (tmux send-keys)

## The Problem

When Gas Town starts agent sessions (`gt crew at <name>`), it passes a startup "beacon" prompt as a bare positional argument:

```
kimigas --yolo "SessionStart: beacon text here..."
```

This works for Claude (which accepts bare positional args as prompts), but **breaks kimi** in two ways:

1. **Kimi doesn't accept bare positional args** -- it interprets them as subcommands and crashes with `No such command 'SessionStart...'`
2. **Even with `-p` flag, kimi exits after one turn** -- `kimi --yolo -p "text"` processes the prompt and exits, but crew sessions need to stay alive for follow-up messages

## The Solution

The `kimigas` wrapper handles this with a **tmux send-keys** mechanism:

### For one-shot modes (polecats)

Bare positional args are converted to `-p` flags. Exit after completion is expected.

```
kimigas --print "do something"
# becomes: kimi --print -p "do something"
```

### For interactive modes (crew sessions in tmux)

The prompt is delivered AFTER kimi starts, via tmux:

```bash
# 1. kimigas detects: bare positional arg + interactive mode + inside tmux
# 2. Spawns a background process to deliver the prompt later:
(sleep 4 && tmux send-keys -t $PANE_ID -- "$PROMPT" Enter) &
disown
# 3. Starts kimi interactively (no -p, stays alive):
exec kimi --yolo
# 4. After 4 seconds, the background process types the prompt into kimi's input
```

This way:
- Kimi starts interactively and owns the TTY
- The startup beacon is delivered as if a human typed it
- Kimi stays alive after processing it, waiting for more input

## Nudging a Running Session

Once kimi is running in a tmux session, you can send messages from anywhere:

```bash
# Find the session name
tmux list-sessions | grep crew

# Send a message (nudge)
tmux send-keys -t gt-myrig-crew-uitester "Run the UI tests and report results" Enter

# Watch what happens
tmux capture-pane -t gt-myrig-crew-uitester -p
```

### From another agent or script

```bash
# Any process on the system can nudge kimi
tmux send-keys -t gt-villaChatToShop-crew-uitester "Check if dark mode works" Enter

# Poll for completion
while true; do
  output=$(tmux capture-pane -t gt-villaChatToShop-crew-uitester -p | tail -3)
  if echo "$output" | grep -q "type to queue"; then
    echo "Kimi is idle, ready for next nudge"
    break
  fi
  sleep 5
done
```

### From Gas Town mayor/coordinator

```bash
# Mayor can dispatch work to any crew member
tmux send-keys -t gt-myrig-crew-uitester "Run smoke tests on port 5174" Enter
tmux send-keys -t gt-myrig-crew-koder "Fix the failing unit test in App.test.tsx" Enter
```

## How It Looks in Practice

```
# 1. Start the crew session
$ gt crew at uitester -d
  Created session for villaChatToShop/uitester
  Started villaChatToShop/uitester.

# 2. Kimi boots up, processes the startup beacon automatically
#    (delivered via tmux send-keys after 4s delay)

# 3. Send a nudge
$ tmux send-keys -t gt-villaChatToShop-crew-uitester \
    "Test the login page loads correctly" Enter

# 4. Watch kimi work
$ tmux capture-pane -t gt-villaChatToShop-crew-uitester -p | tail -20
  Used Shell (curl -s http://localhost:5174/)
  Used ReadMediaFile (login-screenshot.png)
  Login page loads correctly...

# 5. Send another nudge when ready
$ tmux send-keys -t gt-villaChatToShop-crew-uitester \
    "Now test the checkout flow" Enter
```

## Diagram

```
gt crew at uitester
       |
       v
  [tmux new-session]
       |
       v
  [respawn-pane with: exec env GT_ROLE=crew ... kimigas --yolo "beacon"]
       |
       v
  kimigas wrapper detects: bare arg + interactive + tmux
       |
       +---> (background) sleep 4 && tmux send-keys "beacon" Enter
       |
       v
  exec kimi --yolo     <-- kimi starts, owns TTY, stays alive
       |
       v
  [4s later: beacon text appears as input]
       |
       v
  kimi processes beacon, stays at prompt
       |
       v
  [nudge via tmux send-keys] --> kimi processes --> stays at prompt --> repeat
```

## Troubleshooting

### Session dies immediately after creation
- **Check auth**: `kimi --print -p "hello"` -- if this fails with 401, run `kimi login`
- **Check the wrapper**: `kimigas --yolo "test"` -- should start interactive, not crash

### Message not being picked up
- Kimi might be busy processing. Check: `tmux capture-pane -t <session> -p | tail -5`
- Look for the spinner: `Using Shell (...)` means kimi is working
- Look for `type to queue next message...` means kimi is idle and ready

### Session exits after first prompt
- This means kimi got `-p` flag (one-shot mode) instead of the tmux send-keys delivery
- Check if `$TMUX` is set in the session environment
- Verify the kimigas wrapper has the interactive mode fix (check for `tmux send-keys` in the script)

## Requirements

- **tmux** must be installed and the session must run inside tmux
- The `kimigas` wrapper (not raw `kimi`) must be used
- Gas Town sets this up automatically via `gt crew at`
