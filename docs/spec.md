# agent-suppie — Desired Behavior Specification

This document describes the desired behavior of the `agent-suppie` AI agent.

## Overview

`agent-suppie` is a conversational AI agent (codenamed "Suppie") that helps users manage their supermarket shopping list through natural language. It is registered with the Gale Broker and uses LangChain to orchestrate LLM-driven conversations with tool use.

## Agent Identity

- **Agent ID**: `suppie`
- **Type**: Conversational
- **Human-Friendly Name**: Suppie
- **Description**: Shopping-list assistant that helps users manage their supermarket list.

## Conversational Behavior

When the user sends a message, the agent:

1. Acknowledges receipt with a streaming message ("Got your message, working on it!")
2. Processes the user's intent using the LLM with available tools
3. Returns a final response via streaming

The agent should be concise but friendly, keeping answers short and to the point.

## Tool Usage

The agent uses two categories of tools: **MCP tools** (remote, from `toto-ms-supermarket`) and **local tools** (implemented within the agent itself).

### MCP Tools (from toto-ms-supermarket)

The agent connects to the `toto-ms-supermarket` MCP endpoint to access:

- **`addItemsToSupermarketList`**: Adds multiple items to the shopping list in bulk. This is the primary tool for adding items — it replaces any mocked/local add functionality.
- **`getSupermarketListItems`**: Retrieves the current items in the shopping list. Used for duplicate detection and for answering user queries about the list contents.

The agent does **not** use the `getCommonItems` MCP tool. Common items are handled through local caching instead (see below).

### Local Tools

- **`getCommonItems` (from local cache)**: Returns the list of common supermarket items from a local in-memory cache. This tool is used by the LLM to cross-reference user input against known items for spell-checking and matching.

## Common Items Caching

The agent maintains an in-memory cache of common supermarket item names:

- **Source**: The cache is populated by calling the `toto-ms-supermarket` REST API endpoint `GET /names`.
- **Refresh Policy**: The cache is refreshed once every **2 weeks**. If the cache is empty or expired, it is refreshed before serving the first request that needs it.
- **Purpose**: The cached common items are used to:
  - Correct misspelled item names (especially from speech-to-text transcriptions in English, Danish, or Italian)
  - Match user input to known items with the highest similarity

## Duplicate Detection

Before adding items to the shopping list, the agent must:

1. Retrieve the current shopping list items (using `getSupermarketListItems`)
2. Check each item the user wants to add against the existing list
3. Skip items that are already in the list
4. Only add items that are not duplicates
5. Inform the user if any items were skipped due to being already present

## Spell-Checking and Item Matching

When the user wants to add items:

1. Cross-reference the requested items against the cached common items list
2. If an item appears misspelled or unusual, find the closest match from common items
3. Use the best-matching common item name instead of the misspelled version
4. This is especially important for speech-to-text input that may contain Danish or Italian words incorrectly transcribed

## LLM Configuration

The agent supports multiple LLM providers based on the `HYPERSCALER` environment variable:

- **GCP**: Google Gemini (via Vertex AI), with extended thinking enabled
- **AWS**: AWS Bedrock (Claude), with thinking budget enabled

## Integration Points

- **Gale Broker**: The agent is registered with Gale Broker for discovery and message routing.
- **toto-ms-supermarket MCP**: Remote tool access for list operations (add items, get items).
- **toto-ms-supermarket REST API**: Direct HTTP call to `GET /names` for populating the common items cache.
- **Authorization**: The agent captures the `Authorization` header from incoming requests and propagates it to MCP tool calls and REST API calls.

## System Prompt Rules

The agent follows these rules when processing user requests:

1. When adding items, double-check against the common items list for misspellings and pick the closest match.
2. Always avoid adding duplicate items to the shopping list. Check the current list before adding.
