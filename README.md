# Agent Suppie

**Suppie** is a conversational AI agent for the [Toto](https://github.com/nicolasances/toto) platform. It helps users manage their supermarket shopping list through natural-language conversation.

## What it does

Suppie receives messages from [Gale Broker](https://github.com/nicolasances/gale-broker), processes them using a LangChain agent, and returns responses via the Gale conversation protocol. It:

- Adds items to the user's supermarket list, deduplicating against what's already there
- Normalises item names using a known-items list (useful for speech-to-text input with misspellings in English, Danish, or Italian)
- Exposes its chain-of-thought reasoning (thinking blocks) alongside the final text response

## LLM support

The LLM is selected via the `HYPERSCALER` environment variable:

| Value | Provider | Model |
|-------|----------|-------|
| `aws` | AWS Bedrock | Claude (configurable via `BEDROCK_MODEL_ID`) |
| `gcp` | Google Vertex AI | Gemini (configurable via `GEMINI_MODEL`) |

Both providers are configured with extended thinking/reasoning enabled.

## Tools

Suppie uses two categories of tools:

- **MCP tools** — `addItemsToSupermarketList` and `getSupermarketListItems`, served by [toto-ms-supermarket](https://github.com/nicolasances/toto-ms-supermarket) over Streamable HTTP.
- **Local tools** — `getCommonItems`, a cached lookup of known item names used for normalisation.

## Architecture

```
Gale Broker → HTTP → SuppieAgent → LangChain agent → LLM (Bedrock / Gemini)
                                         ↓
                               MCP tools (toto-ms-supermarket)
```

Suppie extends `GaleConversationalAgent` from the [toto-microservice-sdk](https://github.com/nicolasances/toto-microservice-sdk) and is registered with Gale Broker via a manifest.
