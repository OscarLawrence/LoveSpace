"""
Session management for Axiom PWA
Handles session state, WebSocket connections, and collaboration stages
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from fastapi import WebSocket
from tools.executor import ToolExecutor
from tools.parser import ToolCallParser

from core.anthropic_client import AnthropicClient
from core.contracts import ComplexityClass, coherence_contract, contract_enforced


class CollaborationStage(Enum):
    """Stages of AI-human collaboration"""

    VISION = "vision"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a task in the collaboration workflow"""

    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    subtasks: list["Task"] = field(default_factory=list)
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """Represents a message in the conversation"""

    role: str  # user/assistant/system
    content: str
    tool_calls: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Session:
    """Represents a collaboration session"""

    id: str
    stage: CollaborationStage = CollaborationStage.VISION
    messages: list[Message] = field(default_factory=list)
    active_tasks: list[Task] = field(default_factory=list)
    project_context: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class SessionManager:
    """Manages collaboration sessions and WebSocket connections"""

    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self.websockets: dict[str, list[WebSocket]] = {}
        self.anthropic_client = AnthropicClient()
        self.tool_parser = ToolCallParser()
        self.tool_executor = ToolExecutor()

    @contract_enforced(
        postconditions=["returns valid session with unique ID"],
        description="Create new collaboration session",
    )
    def create_session(self) -> Session:
        """Create a new collaboration session"""
        session_id = str(uuid.uuid4())
        session = Session(id=session_id)
        self.sessions[session_id] = session
        self.websockets[session_id] = []
        return session

    @contract_enforced(
        preconditions=["session_id exists in sessions"], description="Get session by ID"
    )
    def get_session(self, session_id: str) -> Session | None:
        """Get session by ID"""
        return self.sessions.get(session_id)

    @contract_enforced(description="Add WebSocket connection to session")
    def add_websocket(self, session_id: str, websocket: WebSocket):
        """Add WebSocket connection to session"""
        if session_id not in self.websockets:
            self.websockets[session_id] = []
        self.websockets[session_id].append(websocket)

    @contract_enforced(description="Remove WebSocket connection from session")
    def remove_websocket(self, session_id: str, websocket: WebSocket):
        """Remove WebSocket connection from session"""
        if session_id in self.websockets:
            self.websockets[session_id].remove(websocket)

    @contract_enforced(
        description="Broadcast message to all WebSocket connections in session"
    )
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast message to all WebSocket connections in session"""
        if session_id in self.websockets:
            for websocket in self.websockets[session_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    # Remove disconnected WebSocket
                    self.websockets[session_id].remove(websocket)

    @coherence_contract(
        input_types={"session_id": "str", "content": "str"},
        requires=["len(content.strip()) > 0"],
        complexity_time=ComplexityClass.LINEAR,
        description="Handle incoming WebSocket message with coherence validation",
    )
    async def handle_websocket_message(
        self, session_id: str, content: str, websocket: WebSocket
    ):
        """Handle incoming WebSocket message with coherence validation"""
        session = self.get_session(session_id)
        if not session:
            await websocket.send_json({"type": "error", "content": "Session not found"})
            return

        # Input validation removed - proceeding with message processing

        # Add user message to session
        user_message = Message(role="user", content=content)
        session.messages.append(user_message)

        # Prepare messages for Claude
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
            if msg.role in ["user", "assistant"]
        ]

        # Get system prompt based on collaboration stage
        system_prompt = self._get_system_prompt(session.stage)

        try:
            # Stream response from Claude
            response_content = ""
            async for chunk in self.anthropic_client.stream_message(
                claude_messages, system_prompt
            ):
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {}).get("text", "")
                    response_content += delta

                    # Send streaming update to client
                    await websocket.send_json(
                        {"type": "message_delta", "content": delta}
                    )

            # Output validation removed - proceeding with response

            # Parse tool calls from response
            tool_calls = self.tool_parser.parse_tool_calls(response_content)

            # Execute tool calls if any
            if tool_calls:
                for tool_call in tool_calls:
                    result = await self.tool_executor.execute_tool(tool_call)
                    response_content += f"\n\nTool result: {result}"

            # Add assistant message to session
            assistant_message = Message(
                role="assistant",
                content=response_content,
                tool_calls=[str(call) for call in tool_calls],
            )
            session.messages.append(assistant_message)

            # Send final message to client
            await websocket.send_json(
                {
                    "type": "message",
                    "content": response_content,
                    "tool_calls": [str(call) for call in tool_calls],
                }
            )

        except Exception as e:
            await websocket.send_json(
                {"type": "error", "content": f"Error processing message: {str(e)}"}
            )

    @contract_enforced(description="Change collaboration stage for session")
    async def change_stage(self, session_id: str, new_stage: CollaborationStage):
        """Change collaboration stage for session"""
        session = self.get_session(session_id)
        if session:
            session.stage = new_stage
            await self.broadcast_to_session(
                session_id, {"type": "stage_change", "stage": new_stage.value}
            )

    @contract_enforced(description="Interrupt running task")
    async def interrupt_task(self, session_id: str, task_id: str, websocket: WebSocket):
        """Interrupt a running task"""
        session = self.get_session(session_id)
        if not session:
            return

        # Find and interrupt task
        for task in session.active_tasks:
            if task.id == task_id:
                task.status = TaskStatus.FAILED
                await websocket.send_json(
                    {
                        "type": "task_update",
                        "task": {
                            "id": task.id,
                            "description": task.description,
                            "status": task.status.value,
                            "progress": task.progress,
                        },
                    }
                )
                break

    def _get_system_prompt(self, stage: CollaborationStage) -> str:
        """Get system prompt based on collaboration stage"""
        prompts = {
            CollaborationStage.VISION: """
You are Axiom, a coherent AI collaboration assistant. You are in the VISION stage.

Focus on:
- Understanding the user's problem and goals
- Exploring possibilities and constraints
- Asking clarifying questions
- Building shared understanding

Use simple function calls when needed:
- read_file("/path/to/file")
- list_files("/path/to/directory")

Keep responses focused and avoid over-engineering.
""",
            CollaborationStage.ARCHITECTURE: """
You are Axiom, a coherent AI collaboration assistant. You are in the ARCHITECTURE stage.

Focus on:
- Designing clean, simple solutions
- Breaking down into micro-modules (<200 LOC)
- Defining clear interfaces and contracts
- Validating architectural decisions

Use function calls for exploration:
- read_file("/path/to/file")
- write_file("/path/to/file", "content")

Prioritize coherence over complexity.
""",
            CollaborationStage.IMPLEMENTATION: """
You are Axiom, a coherent AI collaboration assistant. You are in the IMPLEMENTATION stage.

Focus on:
- Implementing the designed architecture
- Writing clean, focused code
- Following the established contracts
- Providing real-time progress updates

Use function calls for implementation:
- write_file("/path/to/file", "content")
- edit_file("/path/to/file", "old_content", "new_content")
- bash_exec("command")

Work systematically and report progress.
""",
            CollaborationStage.REVIEW: """
You are Axiom, a coherent AI collaboration assistant. You are in the REVIEW stage.

Focus on:
- Evaluating implementation quality
- Testing functionality
- Identifying improvements
- Documenting decisions

Use function calls for validation:
- read_file("/path/to/file")
- bash_exec("test_command")

Provide honest, constructive feedback.
""",
        }
        return prompts.get(stage, prompts[CollaborationStage.VISION])

    def _enhance_system_prompt_for_contracts(self, original_prompt: str) -> str:
        """Add contract requirements to system prompt"""
        contract_requirements = """

IMPORTANT: You MUST include formal contracts for all functions using @coherence_contract decorator.

Example:
@coherence_contract(
    input_types={"items": "List[int]"},
    output_type="List[int]",
    requires=["len(items) >= 0"],
    ensures=["len(result) == len(items)", "is_sorted(result)"],
    complexity_time="O(n log n)",
    pure=True
)
def sort_list(items: List[int]) -> List[int]:
    return sorted(items)

Always specify:
- input_types and output_type
- requires (preconditions) 
- ensures (postconditions)
- complexity_time (O(1), O(n), O(n log n), etc.)
- pure=True if function has no side effects
"""
        return original_prompt + contract_requirements

    async def _regenerate_with_contracts(
        self, claude_messages, enhanced_prompt: str, websocket
    ) -> str:
        """Regenerate AI response with contract requirements"""
        response_content = ""

        try:
            async for chunk in self.anthropic_client.stream_message(
                claude_messages, enhanced_prompt
            ):
                if chunk.get("type") == "content_block_delta":
                    delta = chunk.get("delta", {}).get("text", "")
                    response_content += delta

                    # Send regeneration update to client
                    await websocket.send_json(
                        {"type": "regeneration_delta", "content": delta}
                    )
        except Exception as e:
            response_content = f"Error during regeneration: {str(e)}"

        return response_content
