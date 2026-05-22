# Agent Execution Guidelines

## Strict Protocol: Execution over Narrative

### 1. No Intentions Without Action
- NEVER say "I will now...", "I'm about to...", or "I plan to..." unless the corresponding tool calls are included in the same response.
- Move from "Planning Mode" to "Execution Mode" immediately.

### 2. Action-First Workflow
- Execute `write`, `edit`, or `bash` calls first.
- Provide the summary of what was done AFTER the tool calls.
- When moving between OpenSpec phases, emit the file creation/update tools immediately.

### 3. Tool Call Syntax Accuracy
- Ensure every tool call follows the exact JSON/system format required by the harness.
- If a tool call fails due to syntax, immediately correct the format in the next turn.
- Double-check that every promised action has an associated tool call before ending the turn.

### 4. Verification Loop
- Before ending a turn, verify: "Did I actually emit the tool call for the action I described?"
- If a file was promised, verify the `write` or `edit` tool was actually emitted.
