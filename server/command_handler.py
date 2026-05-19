#!/usr/bin/env python3
"""
Command definitions and validation
"""

import uuid
from typing import Dict, Any


class CommandHandler:
    COMMANDS = {
        'shell': {
            'description': 'Execute shell command',
            'args': ['command'],
            'danger': 'medium'
        },
        'download': {
            'description': 'Download file from target',
            'args': ['remote_path'],
            'danger': 'low'
        },
        'upload': {
            'description': 'Upload file to target',
            'args': ['local_path', 'remote_path'],
            'danger': 'medium'
        },
        'screenshot': {
            'description': 'Capture screenshot',
            'args': [],
            'danger': 'low'
        },
        'keylog_start': {
            'description': 'Start keylogger',
            'args': [],
            'danger': 'high'
        },
        'keylog_stop': {
            'description': 'Stop keylogger and retrieve logs',
            'args': [],
            'danger': 'high'
        },
        'info': {
            'description': 'Get system information',
            'args': [],
            'danger': 'none'
        },
        'processes': {
            'description': 'List running processes',
            'args': [],
            'danger': 'low'
        },
        'kill': {
            'description': 'Kill process by PID',
            'args': ['pid'],
            'danger': 'high'
        },
        'cd': {
            'description': 'Change directory',
            'args': ['path'],
            'danger': 'none'
        },
        'pwd': {
            'description': 'Print working directory',
            'args': [],
            'danger': 'none'
        },
        'ls': {
            'description': 'List directory contents',
            'args': ['path'],
            'danger': 'none'
        },
        'exit': {
            'description': 'Close session',
            'args': [],
            'danger': 'none'
        }
    }
    
    def create_command(self, cmd_type: str, **kwargs) -> Dict[str, Any]:
        if cmd_type not in self.COMMANDS:
            raise ValueError(f"Unknown command: {cmd_type}")
        
        return {
            'id': str(uuid.uuid4())[:12],
            'type': cmd_type,
            'args': kwargs,
            'timestamp': None  # Set by server
        }
    
    def validate_command(self, cmd_type: str, args: dict) -> tuple:
        if cmd_type not in self.COMMANDS:
            return False, f"Unknown command: {cmd_type}"
        
        spec = self.COMMANDS[cmd_type]
        for arg in spec['args']:
            if arg not in args:
                return False, f"Missing required arg: {arg}"
        
        return True, "Valid"
    
    def get_help(self) -> dict:
        return self.COMMANDS