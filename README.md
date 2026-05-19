# RAT-Lite Educational

> **⚠️ EDUCATIONAL & AUTHORIZED TESTING ONLY**
> 
> This project is strictly for **educational purposes** and **authorized penetration testing**.
> Unauthorized access to computer systems is **illegal** under the Computer Fraud and Abuse Act (CFAA)
> and similar laws worldwide. The author assumes **no liability** for misuse.

---

## Overview

**RAT-Lite Educational** is an **asynchronous, encrypted remote administration tool** built in Python for learning
network security, cryptography, and systems programming. It demonstrates real-world C2 (Command & Control)
architecture concepts in a **controlled, sandboxed environment**.

### Why This Project?

| Learning Goal | What You Get |
|--------------|-------------|
| **Asyncio & Networking** | Production-grade async socket handling |
| **Cryptography** | RSA + AES hybrid encryption implementation |
| **C2 Architecture** | Session management, command queuing, response handling |
| **Web Development** | aiohttp-based control panel |
| **OS Internals** | Process management, file I/O, screenshot capture |

---

## Architecture

```
┌─────────────────┐     RSA Key Exchange      ┌─────────────────┐
│   C2 Server     │ ◄────────────────────────► │    Client       │
│  (main.py)      │                           │  (main.py)      │
├─────────────────┤                           ├─────────────────┤
│ • Session Mgmt  │     AES Encrypted Traffic   │ • Auto-Reconnect│
│ • Command Queue │ ◄────────────────────────► │ • Command Exec  │
│ • Web Panel     │                           │ • File Transfer │
│ • CLI Control   │                           │ • Screenshot    │
└─────────────────┘                           └─────────────────┘
        │
        ▼
┌─────────────────┐
│  Web Panel      │
│  (localhost)    │
└─────────────────┘
```

---

## Features

### Security
- **RSA-2048** asymmetric key exchange
- **AES-256-CBC** symmetric traffic encryption (PKCS7 padding)
- **Auto-reconnect** with exponential backoff
- **Session isolation** — each client gets unique AES key

### Commands

| Command | Description | Danger Level |
|---------|-------------|--------------|
| `shell <cmd>` | Execute shell command | Medium |
| `screenshot` | Capture target screen | Low |
| `download <path>` | Download file from target | Low |
| `upload <data> <path>` | Upload file to target | Medium |
| `keylog_start` | Start keystroke capture | High |
| `keylog_stop` | Stop & retrieve keystrokes | High |
| `processes` | List running processes | Low |
| `kill <pid>` | Terminate process by PID | High |
| `cd <path>` | Change working directory | None |
| `ls [path]` | List directory contents | None |
| `pwd` | Print working directory | None |
| `info` | Get system information | None |
| `exit` | Close client session | None |

### Interfaces
- **Web Panel** (`http://localhost:8080`) — Browser-based terminal with session management
- **CLI Controller** — Terminal-based interactive control

---

## Installation

### Prerequisites
- Python 3.10+
- pip

### Server Setup

```bash
git clone https://github.com/yos1mitsu/rat-lite-educational.git
cd rat-lite-educational/server
pip install -r requirements.txt
python main.py
```

### Client Setup

```bash
cd rat-lite-educational/client
pip install -r requirements.txt
```

**Edit `client/main.py` and set your server IP:**

```python
SERVER_HOST = "192.168.1.10"  # Change to your server IP
SERVER_PORT = 8443
```

```bash
python main.py
```

---

## Usage

### Web Panel
1. Open `http://localhost:8080` after starting server
2. Select active session from sidebar
3. Type commands or click action buttons
4. Responses appear in terminal output

### CLI Controller
```python
from cli_controller import CLIController
from session_manager import SessionManager
from command_handler import CommandHandler

sessions = SessionManager()
commands = CommandHandler()
cli = CLIController(sessions, commands)

# Run in async context
await cli.run()
```

---

## Project Structure

```
rat-lite-educational/
├── server/
│   ├── main.py              # Asyncio C2 server entry point
│   ├── crypto_manager.py    # RSA + AES hybrid encryption
│   ├── session_manager.py   # Session & command queue management
│   ├── command_handler.py   # Command definitions & validation
│   ├── web_panel.py         # aiohttp web control panel
│   ├── cli_controller.py    # Terminal-based controller
│   ├── requirements.txt
│   └── static/
├── client/
│   ├── main.py              # Asyncio client with auto-reconnect
│   ├── crypto_manager.py    # Client-side encryption
│   ├── command_executor.py  # Command execution engine
│   └── requirements.txt
└── README.md
```

---

## Technical Details

### Encryption Flow
```
1. Server generates RSA-2048 keypair
2. Server sends public key to client
3. Client generates random AES-256 key
4. Client encrypts AES key with RSA public key
5. Client sends encrypted AES key to server
6. All subsequent traffic encrypted with AES-CBC
```

### Protocol
```
[4 bytes: length][encrypted payload]
```
- Length prefix: big-endian unsigned int
- Payload: base64(AES-encrypted data)
- AES: CBC mode, random IV per message, PKCS7 padding

---

## Legal & Ethical Guidelines

### ✅ Acceptable Use
- Testing on **your own** machines and VMs
- **Authorized** penetration testing with written permission
- Educational demonstrations in **controlled environments**
- Security research in **sandboxed/isolated networks**

### ❌ Prohibited Use
- Unauthorized access to any system you don't own
- Deployment on public networks without explicit consent
- Use against individuals, organizations, or infrastructure without authorization
- Any activity violating local, national, or international laws

### Compliance
- Always obtain **written authorization** before testing
- Document all testing activities
- Respect scope boundaries defined in authorization
- Report findings responsibly

---

## Disclaimer

> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
> INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
> PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
> LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
> TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
> OR OTHER DEALINGS IN THE SOFTWARE.
>
> **THIS TOOL IS FOR EDUCATIONAL AND AUTHORIZED TESTING PURPOSES ONLY.**
> **THE AUTHOR ASSUMES NO RESPONSIBILITY FOR ILLEGAL OR MALICIOUS USE.**

---

## Contributing

Contributions focused on **security education** are welcome:
- Bug fixes
- Documentation improvements
- Additional educational features
- Test coverage

Please ensure all contributions maintain the educational and ethical focus of this project.

---

## License

MIT License — See [LICENSE](LICENSE) file for details.

---

## Author

**yos1mitsu**

- GitHub: [@yos1mitsu](https://github.com/yos1mitsu)
- Cybersecurity enthusiast & developer

---

## Acknowledgments

- [cryptography](https://cryptography.io/) library for robust encryption
- [aiohttp](https://docs.aiohttp.org/) for async web framework
- [OWASP](https://owasp.org/) for security best practices

---

<p align="center">
  <sub>Built for learning. Use responsibly.</sub>
</p>
