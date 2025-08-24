# Implementation Plan: Direct HTTP API Calls

## Problem
The Anthropic SDK likely adds hidden system instructions that create behavioral inconsistencies:
- Excessive agreeableness ("you are absolutely right")
- Politeness over directness 
- Hedging instead of confident solutions
- Constitutional AI behaviors that override custom system messages

## Solution
Replace Anthropic SDK with direct HTTP requests to gain complete control over API calls.

## Changes Required

### 1. Remove Anthropic SDK Dependency
- Remove `anthropic` from requirements.txt
- Remove `import anthropic` from backend/main.py
- Add `httpx` for HTTP requests (likely already present)

### 2. Implement Direct API Client
Create `backend/anthropic_client.py`:
- Direct HTTP streaming to `https://api.anthropic.com/v1/messages`
- Custom headers with API key and anthropic-version
- JSON payload with exact parameters (no hidden additions)
- Stream parsing for real-time responses

### 3. Update main.py
Replace `client.messages.stream()` call with:
- Direct HTTP POST to Anthropic API
- Custom stream parsing
- Same tool execution logic (no changes needed)

### 4. Configuration
- Keep model name: "claude-sonnet-4-20250514" 
- Keep system message building (works correctly)
- Keep tool execution system (works correctly)

## Expected Outcome
Pure Axiom behavior without SDK interference:
- Direct answers without excessive politeness
- Confident solutions without hedging
- Minimal responses focused on solving problems
- No hidden system message pollution

## Files to Modify
1. `requirements.txt` - Remove anthropic, ensure httpx
2. `backend/main.py` - Replace SDK calls
3. `backend/anthropic_client.py` - New direct API client

## Risk Assessment
- Low risk: API format is well documented
- Same functionality, just direct HTTP instead of SDK wrapper
- Tool execution system remains unchanged')