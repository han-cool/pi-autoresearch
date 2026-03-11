# Branch: `tree-on-experiment-log`

## Summary

This branch adds **auto-checkpointing** to the autoresearch extension: after every `log_experiment` call, the session automatically navigates the conversation tree to that experiment's entry, summarizes the abandoned branch using Groq Llama 3.3 70B, and sends a follow-up message to resume the loop — all without any manual intervention.

It also adds **live experiment state injection** so the LLM always sees the current dashboard (baseline, best, delta %, recent runs) at the start of every turn.

---

## Changes

### File: `extensions/pi-autoresearch/index.ts`

The entire feature is contained in one commit (`9229b9cb`) to this file. The file grew from **1,178 → 1,450 lines** (+272 lines).

---

### 1. New imports

```ts
// Before
import { truncateTail } from "@mariozechner/pi-coding-agent";
import { StringEnum } from "@mariozechner/pi-ai";

// After
import { truncateTail, convertToLlm, serializeConversation } from "@mariozechner/pi-coding-agent";
import { StringEnum, complete, getModel } from "@mariozechner/pi-ai";
```

`convertToLlm` and `serializeConversation` are used to serialise the conversation history for the Groq summarizer. `complete` and `getModel` are the low-level primitives for calling an arbitrary model.

---

### 2. New extension-level state variables

```ts
let checkpointInFlight = false;
let checkpointTriggerToolCallId: string | null = null;
let useSummaryModelForNextTreeNav = false;
```

| Variable | Purpose |
|---|---|
| `checkpointInFlight` | Prevents the checkpoint from being queued more than once per experiment (re-entrancy guard) |
| `checkpointTriggerToolCallId` | Captures the exact `toolCallId` of the `log_experiment` call that triggered the checkpoint, so the tree navigation lands on *that* entry even if more experiments ran in the same turn |
| `useSummaryModelForNextTreeNav` | Flag that enables the custom Groq summarizer only for auto-triggered checkpoints — prevents hijacking manual `/tree` usage |

---

### 3. `before_agent_start` — experiment state injection (refactored)

The existing `before_agent_start` handler (which added the autoresearch system prompt note) was extended to **also inject a hidden `CustomMessage`** containing the current experiment dashboard state on every LLM turn:

```
## Autoresearch State
- Primary metric: sort_µs (lower is better)
- Baseline: 9,578µs
- Best: 0µs (-100.0% from baseline)
- Experiments: 8 total — 7 kept, 0 discarded, 1 crashed

### Recent experiments
  4. [keep] In-place arr.sort() → 9,578µs
  5. [keep] Cache sorted result → 354µs
  ...
```

The message is sent with `display: false` so it's invisible in the UI but present in the LLM's context. This ensures the model always knows the current state even after a tree navigation compacts the history.

---

### 4. `tool_execution_end` — auto-checkpoint trigger

```ts
pi.on("tool_execution_end", async (event, _ctx) => {
  if (event.toolName !== "log_experiment") return;
  if (event.isError) return;
  if (checkpointInFlight) return;

  checkpointInFlight = true;
  checkpointTriggerToolCallId = event.toolCallId;
  pi.sendUserMessage("/autoresearch-checkpoint", { deliverAs: "followUp" });
});
```

After every successful `log_experiment`, this queues `/autoresearch-checkpoint` as a follow-up. The `checkpointInFlight` guard ensures only one checkpoint is queued at a time even if multiple experiments ran in one agent turn.

---

### 5. `session_before_tree` — Groq Llama branch summarization

```ts
const SUMMARY_MODEL_PROVIDER = "groq";
const SUMMARY_MODEL_ID = "llama-3.3-70b-versatile";

pi.on("session_before_tree", async (event, ctx) => {
  if (!event.preparation.userWantsSummary) return;
  if (event.preparation.entriesToSummarize.length === 0) return;
  if (!useSummaryModelForNextTreeNav) return; // Only for auto-checkpoints
  useSummaryModelForNextTreeNav = false;
  // ...
});
```

When triggered, it:
1. Serializes the conversation entries being abandoned into plain text
2. Truncates to 100k characters (with a `[...earlier conversation truncated]` prefix) to stay within Groq's context limits
3. Calls Groq Llama 3.3 70B with an autoresearch-focused system prompt asking for: what was optimized, which experiments were tried, what worked/failed, and promising next directions
4. Returns the summary to pi's tree navigation machinery
5. Falls back to the default summarizer (returns `undefined`) on any error

**Why Groq Llama?** It's cheap, fast, and has a large context — ideal for throwaway summarization work that doesn't need the main model's quality.

---

### 6. New `/autoresearch-checkpoint` command

An internal command (no `description` → invisible in autocomplete) with this flow:

```
1. Guard: reject if not called by tool_execution_end (checkpointInFlight must be true)
2. Find the target entry in the session tree:
   a. Primary: look for the toolResult entry matching checkpointTriggerToolCallId
   b. Fallback: find the last log_experiment toolResult in the branch
3. Set useSummaryModelForNextTreeNav = true
4. Call ctx.navigateTree(targetId, { summarize: true, label: "checkpoint-N" })
5. On success: send continuation follow-up message to resume the loop
6. Finally: reset checkpointInFlight and checkpointTriggerToolCallId
```

The key design decision here is navigating to the **specific** `log_experiment` that triggered the checkpoint, not just "the last one." This is important because an agent turn may contain multiple tool calls — by anchoring to the trigger, the tree navigation correctly abandons any later experiments in the same turn and summarizes them.

The **continuation message** sent after a successful checkpoint:
> *"Continue the autoresearch experiment loop. The branch was summarized and context was trimmed. Read the branch summary above for what was tried. Think of a new experiment idea and go."*

This makes the loop fully autonomous: after checkpointing, the agent immediately resumes without waiting for user input.

---

## How it all fits together

```
Agent runs experiment
  → run_experiment
  → log_experiment
      ↓
tool_execution_end fires
  → queues /autoresearch-checkpoint as followUp
      ↓
/autoresearch-checkpoint runs
  → sets useSummaryModelForNextTreeNav = true
  → calls ctx.navigateTree(targetId, { summarize: true })
      ↓
session_before_tree fires
  → serializes abandoned branch conversation
  → calls Groq Llama 3.3 70B to summarize it
  → returns autoresearch-focused summary
      ↓
Tree navigation completes (branch summarized, context trimmed)
  → /autoresearch-checkpoint sends continuation followUp
      ↓
Agent resumes loop autonomously
```

---

## Test artifacts (not shipped)

The branch also contains `test-research/` — a throwaway autoresearch session used to validate the feature. It ran 8 experiments optimizing Python sort speed from a 9,578 µs baseline down to 0 µs (by monkey-patching `tracemalloc` to a no-op and eventually pre-computing the result at import time). These files are not part of the extension itself.
