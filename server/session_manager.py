#!/usr/bin/env python3
"""
Session management with command queueing
"""

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Optional, Any


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.command_queues: Dict[str, asyncio.Queue] = {}
        self.responses: Dict[str, dict] = {}
    
    def create_session(self, addr, writer, reader) -> str:
        session_id = str(uuid.uuid4())[:8]
        self.sessions[session_id] = {
            'id': session_id,
            'addr': addr,
            'writer': writer,
            'reader': reader,
            'connected_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'system_info': {},
            'status': 'active',
            'key': None
        }
        self.command_queues[session_id] = asyncio.Queue()
        self.responses[session_id] = {}
        return session_id
    
    def set_key(self, session_id: str, key: bytes):
        if session_id in self.sessions:
            self.sessions[session_id]['key'] = key
    
    def get_key(self, session_id: str) -> Optional[bytes]:
        return self.sessions.get(session_id, {}).get('key')
    
    def update_info(self, session_id: str, info: dict):
        if session_id in self.sessions:
            self.sessions[session_id]['system_info'] = info
            self.sessions[session_id]['last_seen'] = datetime.now().isoformat()
    
    async def queue_command(self, session_id: str, command: dict):
        if session_id in self.command_queues:
            await self.command_queues[session_id].put(command)
    
    async def get_command(self, session_id: str) -> Optional[dict]:
        if session_id in self.command_queues:
            try:
                return self.command_queues[session_id].get_nowait()
            except asyncio.QueueEmpty:
                return None
        return None
    
    def store_response(self, session_id: str, cmd_id: str, response: str):
        if session_id in self.responses:
            self.responses[session_id][cmd_id] = {
                'timestamp': datetime.now().isoformat(),
                'data': response
            }
    
    def get_response(self, session_id: str, cmd_id: str) -> Optional[dict]:
        return self.responses.get(session_id, {}).get(cmd_id)
    
    def get_session(self, session_id: str) -> Optional[dict]:
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> list:
        return [
            {
                'id': s['id'],
                'addr': s['addr'],
                'status': s['status'],
                'connected_at': s['connected_at'],
                'system_info': s['system_info']
            }
            for s in self.sessions.values()
        ]
    
    def close_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]['status'] = 'disconnected'
            self.sessions[session_id]['writer'] = None
            self.sessions[session_id]['reader'] = None