# Axiom - Minimal AI Chat Interface

## What This Is

Basic chat interface for direct communication with Claude Sonnet 4. Clean, minimal implementation without SDK pollution or complex abstractions.

**Core Problem**: Cannot build coherent systems with incoherent tools. Most AI interfaces have system message pollution, conflicting instructions, and messy abstractions.

**Axiom Solution**: Direct API calls to Claude Sonnet 4 with minimal, focused system message.

## Implementation

### FastAPI + Static Frontend
- **FastAPI backend** with direct HTTP client to Anthropic API
- **Static HTML/CSS/JS frontend** 
- **In-memory message storage** for chat history
- **Minimal system message** loaded from file

### Current Features
- Direct chat with Claude Sonnet 4
- Chat history persistence (session-based)
- Clean system message from file
- Basic web interface

## Quick Start

### Option 1: Docker (Recommended for Production)
```bash
# Start with Docker
./docker-start.sh start

# Or using docker-compose directly
docker-compose up -d
```

### Option 2: Direct Python (Development)
```bash
# Start directly
python start.py
```

Open http://localhost:8000 for the chat interface.

### Docker Commands
```bash
./docker-start.sh start    # Start the application
./docker-start.sh stop     # Stop the application  
./docker-start.sh logs     # View logs
./docker-start.sh status   # Check status
./docker-start.sh restart  # Restart application
./docker-start.sh help     # Show all commands
```

## Status

**Current**: Working minimal chat interface
- ✅ Direct Claude Sonnet 4 API integration
- ✅ Basic chat history
- ✅ Clean system message loading
- ✅ Static frontend

**Next**: Add coherence validation and tool capabilities incrementally.