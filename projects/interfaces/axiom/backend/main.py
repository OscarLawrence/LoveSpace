import os
import ast
import json
import asyncio
import subprocess
from typing import List, Dict, Any
from pathlib import Path

import anthropic
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Import tools and build system message
from .tools import read_file, write_file, list_dir, execute
import inspect

def build_system_message():
    """Build system message with tool functions included"""
    base_message = Path('/home/vincent/Documents/Momo/MomoAI/MomoAI/projects/axiom/backend/system_message.txt').read_text()
    
    # Get source code of all tool functions
    tools_source = []
    for func in [read_file, write_file, list_dir, execute]:
        tools_source.append(inspect.getsource(func))
    
    tools_text = "\n".join(tools_source)
    
    return f"{base_message}\n\n# Available Tools (execute with @@exec...@@end blocks):\n\n{tools_text}"

class Session:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

def extract_tool_calls(text: str):
    """Extract and parse tool calls from @@exec...@@end blocks"""
    tool_calls = []
    
    # Find all exec blocks
    import re
    pattern = r'@@exec\n(.*?)\n@@end'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            # Parse the Python code
            tree = ast.parse(match)
            
            # Extract function calls
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    
                    # Only process our known tools
                    if func_name in ['read_file', 'write_file', 'list_dir', 'execute']:
                        args = []
                        
                        # Extract arguments
                        for arg in node.args:
                            if isinstance(arg, ast.Constant):
                                args.append(arg.value)
                            elif isinstance(arg, ast.Str):  # Python 3.7 compatibility
                                args.append(arg.s)
                        
                        tool_calls.append({
                            'function': func_name,
                            'args': args
                        })
        except:
            # If parsing fails, skip this block
            continue
    
    return tool_calls

def execute_tool_call(call: Dict[str, Any]) -> str:
    """Execute a single tool call and return result"""
    func_name = call['function']
    args = call['args']
    
    try:
        if func_name == 'read_file':
            return read_file(args[0])
        elif func_name == 'write_file':
            return write_file(args[0], args[1])
        elif func_name == 'list_dir':
            return list_dir(args[0] if args else '.')
        elif func_name == 'execute':
            return execute(args[0])
    except Exception as e:
        return f"Error executing {func_name}: {str(e)}"

async def stream_response(websocket: WebSocket, session: Session, user_message: str):
    """Stream Claude response with tool execution"""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    session.add_message("user", user_message)
    
    try:
        # Start streaming
        await websocket.send_json({"type": "start"})
        
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=build_system_message(),
            messages=session.messages
        ) as stream:
            accumulated = ""
            
            for text in stream.text_stream:
                accumulated += text
                await websocket.send_json({"type": "token", "content": text})
                
                # Check for complete tool blocks
                if '@@exec' in accumulated and '@@end' in accumulated:
                    # We might have complete tool calls
                    tool_calls = extract_tool_calls(accumulated)
                    
                    if tool_calls:
                        # Stop streaming to execute tools
                        stream.close()
                        
                        # Execute all tool calls
                        results = []
                        for call in tool_calls:
                            result = execute_tool_call(call)
                            results.append(f"{call['function']}({', '.join(repr(a) for a in call['args'])}) returned:\n{result}")
                        
                        # Send tool results to client
                        tool_output = "\n\n".join(results)
                        await websocket.send_json({"type": "tool_result", "content": tool_output})
                        
                        # Add to conversation
                        session.add_message("assistant", accumulated)
                        session.add_message("user", f"Tool execution results:\n{tool_output}\n\nContinue with your response.")
                        
                        # Continue with new stream
                        await stream_response(websocket, session, "")
                        return
            
            # No tool calls, complete normal message
            session.add_message("assistant", accumulated)
            await websocket.send_json({"type": "complete"})
            
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = Session()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'message':
                await stream_response(websocket, session, message['content'])
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})

@app.get("/")
async def serve_frontend():
    # For development: ../frontend/index.html
    # For docker: ./frontend/index.html  
    import os
    if os.path.exists("../frontend/index.html"):
        return FileResponse("../frontend/index.html")
    else:
        return FileResponse("./frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)