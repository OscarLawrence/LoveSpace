# Axiom PWA Implementation Plan

## Architecture Overview

**Core Entities:**
```python
class Session:
    id: str
    stage: CollaborationStage  # vision/architecture/implementation/review
    messages: list[Message]
    active_tasks: list[Task]
    project_context: dict

class Message:
    role: str  # user/assistant/system
    content: str
    tool_calls: list[str]  # ["read_file('x')", "edit_file('y')"]
    timestamp: datetime

class Task:
    id: str
    description: str
    status: TaskStatus  # pending/running/completed/failed
    subtasks: list[Task]
    progress: float
```

**REST Endpoints:**
```
POST /sessions                    # Create new session
GET  /sessions/{id}              # Get session state
POST /sessions/{id}/messages     # Send message
GET  /sessions/{id}/tasks        # Get task tree
POST /sessions/{id}/stage        # Change collaboration stage
```

**WebSocket Events:**
```
# Client → Server
{ "type": "message", "content": "..." }
{ "type": "interrupt_task", "task_id": "..." }

# Server → Client  
{ "type": "message", "content": "...", "tool_calls": [...] }
{ "type": "task_update", "task": {...} }
{ "type": "stage_change", "stage": "..." }
```

**Tool System:**
```python
# AI responds with: read_file("/path/file.txt")
# Parser extracts: [("read_file", ["/path/file.txt"])]
# Executor calls: tools.read_file("/path/file.txt") 
# Result injected back to conversation
```

## Implementation Phases

### Phase 1: Backend Foundation
```
axiom/
├── backend/
│   ├── main.py              # FastAPI app + WebSocket
│   ├── api/
│   │   ├── sessions.py      # Session management endpoints
│   │   └── messages.py      # Message handling
│   ├── core/
│   │   ├── anthropic_client.py  # Reuse existing
│   │   ├── contracts.py         # Reuse existing 
│   │   └── session_manager.py   # New: session state
│   └── tools/
│       ├── parser.py        # Function call parser
│       └── executor.py      # Tool execution
```

### Phase 2: Basic Frontend
```
├── frontend/
│   ├── index.html           # Main app shell
│   ├── manifest.json        # PWA manifest
│   ├── sw.js               # Service worker
│   ├── js/
│   │   ├── api.js          # WebSocket + REST client
│   │   ├── ui.js           # DOM manipulation
│   │   └── stages.js       # Stage transitions
│   └── css/
│       └── app.css         # Clean, responsive styling
```

### Phase 3: Integration & Polish
- Tool system integration
- Real-time task progress
- Stage management UI
- Error handling
- Local startup script

## Validation Strategy
- Build MomoAI components using Axiom itself
- Immediate dogfooding for rapid iteration

## Priority Order
1. Basic chat with WebSocket
2. Simple tool calls (read_file, write_file)
3. Task progress visualization
4. Stage transitions

## Key Features
- **Universal Access**: PWA works on any device
- **Future-Proof**: Local/remote server compatibility
- **Simple Tool System**: Natural function calls instead of complex JSON
- **Real-time Collaboration**: WebSocket for live updates
- **Stage-based Workflow**: Vision → Architecture → Implementation → Review