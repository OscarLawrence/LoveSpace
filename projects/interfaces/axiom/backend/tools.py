import os
import subprocess
from pathlib import Path

def read_file(path: str) -> str:
    """Read contents of a file at the given absolute path"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    """Write content to a file at the given absolute path"""
    # Create parent directories if they don't exist
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Written {len(content)} bytes to {path}"

def list_dir(path: str = '.') -> str:
    """List contents of a directory"""
    items = []
    for item in sorted(os.listdir(path)):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            items.append(f"[DIR]  {item}/")
        else:
            size = os.path.getsize(item_path)
            items.append(f"[FILE] {item} ({size} bytes)")
    return '\n'.join(items)

def execute(command: str) -> str:
    """Execute a shell command and return its output"""
    result = subprocess.run(
        command, 
        shell=True, 
        capture_output=True, 
        text=True,
        timeout=30
    )
    output = []
    if result.stdout:
        output.append(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        output.append(f"STDERR:\n{result.stderr}")
    output.append(f"Return code: {result.returncode}")
    return '\n'.join(output)