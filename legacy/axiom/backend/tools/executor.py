"""
Tool executor for Axiom PWA
Executes parsed tool calls safely and efficiently
"""

import asyncio
import os
from pathlib import Path

from core.contracts import contract_enforced

from tools.parser import ToolCall


class ToolExecutor:
    """Executes tool calls safely"""

    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()

        # Tool function mapping
        self.tools = {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "edit_file": self._edit_file,
            "list_files": self._list_files,
            "bash_exec": self._bash_exec,
            "create_directory": self._create_directory,
            "delete_file": self._delete_file,
        }

    @contract_enforced(
        preconditions=["tool_call has valid function_name"],
        description="Execute a tool call and return result",
    )
    async def execute_tool(self, tool_call: ToolCall) -> str:
        """
        Execute a tool call and return result

        Args:
            tool_call: Parsed tool call to execute

        Returns:
            String result of tool execution
        """
        if tool_call.function_name not in self.tools:
            return f"Error: Unknown tool function '{tool_call.function_name}'"

        try:
            tool_func = self.tools[tool_call.function_name]
            result = await tool_func(*tool_call.args)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_call.function_name}: {str(e)}"

    @contract_enforced(description="Read file contents")
    async def _read_file(self, file_path: str) -> str:
        """Read file contents"""
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            return f"Error: File '{file_path}' does not exist"

        if not full_path.is_file():
            return f"Error: '{file_path}' is not a file"

        try:
            with open(full_path, encoding="utf-8") as f:
                content = f.read()
            return f"File contents of '{file_path}':\n{content}"
        except UnicodeDecodeError:
            return f"Error: Cannot read '{file_path}' - binary file or encoding issue"

    @contract_enforced(description="Write content to file")
    async def _write_file(self, file_path: str, content: str) -> str:
        """Write content to file"""
        full_path = self._resolve_path(file_path)

        # Create parent directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to '{file_path}'"
        except Exception as e:
            return f"Error writing to '{file_path}': {str(e)}"

    @contract_enforced(
        description="Edit file by replacing old content with new content"
    )
    async def _edit_file(
        self, file_path: str, old_content: str, new_content: str
    ) -> str:
        """Edit file by replacing old content with new content"""
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            return f"Error: File '{file_path}' does not exist"

        try:
            with open(full_path, encoding="utf-8") as f:
                current_content = f.read()

            if old_content not in current_content:
                return f"Error: Old content not found in '{file_path}'"

            updated_content = current_content.replace(old_content, new_content)

            with open(full_path, "w", encoding="utf-8") as f:
                f.write(updated_content)

            return f"Successfully edited '{file_path}'"
        except Exception as e:
            return f"Error editing '{file_path}': {str(e)}"

    @contract_enforced(description="List files in directory")
    async def _list_files(self, directory_path: str = ".") -> str:
        """List files in directory"""
        full_path = self._resolve_path(directory_path)

        if not full_path.exists():
            return f"Error: Directory '{directory_path}' does not exist"

        if not full_path.is_dir():
            return f"Error: '{directory_path}' is not a directory"

        try:
            items = []
            for item in sorted(full_path.iterdir()):
                if item.is_dir():
                    items.append(f"📁 {item.name}/")
                else:
                    items.append(f"📄 {item.name}")

            if not items:
                return f"Directory '{directory_path}' is empty"

            return f"Contents of '{directory_path}':\n" + "\n".join(items)
        except Exception as e:
            return f"Error listing '{directory_path}': {str(e)}"

    @contract_enforced(description="Execute bash command")
    async def _bash_exec(self, command: str) -> str:
        """Execute bash command"""
        try:
            # Run command in workspace root
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=self.workspace_root,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            result = f"Command: {command}\n"
            result += f"Exit code: {process.returncode}\n"

            if stdout:
                result += f"Output:\n{stdout.decode('utf-8')}\n"

            if stderr:
                result += f"Error:\n{stderr.decode('utf-8')}\n"

            return result
        except Exception as e:
            return f"Error executing command '{command}': {str(e)}"

    @contract_enforced(description="Create directory")
    async def _create_directory(self, directory_path: str) -> str:
        """Create directory"""
        full_path = self._resolve_path(directory_path)

        try:
            full_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory '{directory_path}'"
        except Exception as e:
            return f"Error creating directory '{directory_path}': {str(e)}"

    @contract_enforced(description="Delete file")
    async def _delete_file(self, file_path: str) -> str:
        """Delete file"""
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            return f"Error: File '{file_path}' does not exist"

        try:
            if full_path.is_file():
                full_path.unlink()
                return f"Successfully deleted file '{file_path}'"
            else:
                return f"Error: '{file_path}' is not a file"
        except Exception as e:
            return f"Error deleting '{file_path}': {str(e)}"

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace root"""
        if os.path.isabs(path):
            # For absolute paths, ensure they're within workspace
            abs_path = Path(path).resolve()
            if not str(abs_path).startswith(str(self.workspace_root)):
                raise ValueError(f"Path '{path}' is outside workspace")
            return abs_path
        else:
            # For relative paths, resolve relative to workspace root
            return (self.workspace_root / path).resolve()
