# LLM Chain-of-Thought Tracking

## Overview

When thinking/reasoning is enabled on the LLM, `agent-suppie` captures the complete response from the LLM provider — including all thinking/reasoning blocks — and includes it as `chainOfThought` in the final response sent to Gale Broker. This enables full traceability of the agent's reasoning chain.

## Response Fields

- **`message`**: Always contains only the user-visible answer as a plain text string (the content of the `text` block from the LLM response).
- **`chainOfThought`**: Contains the raw, complete list of content blocks as returned by the LLM provider, preserving all provider-specific data (thinking steps, signatures, tool-use details, etc.). This field is `null` when the LLM returns a plain string response (i.e., when thinking is not enabled).

## LLM Content Block Format

When thinking is enabled, the LLM returns a list of content blocks, for example:

```json
[
    {"type": "thinking", "thinking": "Okay, the user wants their list..."},
    {"type": "text", "text": "Your market list contains: Bread, Bacon, avocado..."}
]
```

The agent extracts the `text` block for the `message` field and includes the full list as `chainOfThought`.

## Provider Support

This applies to both supported LLM providers:

- **AWS Bedrock (Claude)**: Thinking is enabled via `model_kwargs` with `"thinking": {"type": "enabled", "budget_tokens": 4096}`. The LLM returns a list of content blocks including `thinking` and `text` types.
- **GCP (Gemini)**: Thinking is enabled via `include_thoughts=True` and `thinking_budget=-1`. The LLM returns a list of content blocks including thought and text types.

## Streaming Behaviour

Only the **final response** (the last streaming message, with `last=True`) includes `chainOfThought`. The intermediate acknowledgement message ("Got your message, working on it!") does not include `chainOfThought`.
