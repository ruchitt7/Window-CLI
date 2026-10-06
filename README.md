# Window CLI Quick Setup

## Project

- Kali Linux = Server
- Windows = Client
- Protocol = TCP + TLS
- Port = 8444
- Final Windows file = `client.exe`

> Use only on systems you own or are authorized to test.

## 1. Kali Setup

Create folders:

```bash
mkdir -p ~/Window-cli/server
mkdir -p ~/Window-cli/logs
cd ~/Window-cli/server
```

Generate TLS files:

```bash
openssl genrsa -out server.key 2048
```

Generate a token:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Put the same token in `server.py` and `client.py`.

## 2. IP Configuration

Find Kali IP:

```bash
ip addr
```

Example:

```text
Kali = 192.168.3.31
```

In `client.py`:

```python
SERVER_HOST = "192.168.3.31"
SERVER_PORT = 8444
```

Replace the example with your current Kali IP.

In `server.py` keep:

```python
HOST = "0.0.0.0"
PORT = 8444
```

Do not put the Windows IP in `server.py`.

## 3. Start Kali Server

```bash
cd ~/Window-cli/server
python3 server.py
```

Expected:

```text
[*] Listening on 0.0.0.0:8444
[*] Waiting for authorized client...
```

Check:

```bash
sudo ss -lntp | grep 8444
```

## 4. Test Windows to Kali

PowerShell:

```powershell
ping 192.168.3.31
```

Then:

```powershell
Test-NetConnection 192.168.3.31 -Port 8444
```

Expected:

```text
TcpTestSucceeded : True
```

Replace the IP if Kali's IP changed.

## 5. Build Windows EXE

On the Windows development machine:

```powershell
pip install pyinstaller
```

Build:

```powershell
pyinstaller --onefile --noconsole --clean client.py
```

The executable is:

```text
dist\client.exe
```

Copy only `client.exe` to the authorized Windows test machine.

## 6. Run

### Kali

```bash
python3 ~/Window-cli/server/server.py
```

### Windows

Run:

```text
client.exe
```

The final Windows machine does not need Python.

## 7. Use the CLI

After connection:

```text
secure-cli>
```

Type:

```text
help
```

Example allowed commands:

```text
hostname
whoami
ipconfig
systeminfo
dir
date
tasklist
netstat
arp
route
exit
```

Example:

```text
secure-cli> hostname
```

The command is sent through TLS, executed by the Windows client, and the output is returned to Kali.

Exit:

```text
secure-cli> exit
```

## 8. Command Flow

```text
Kali
  |
  | secure-cli> hostname
  v
server.py
  |
  | TCP + TLS
  v
client.exe
  |
  | execute authorized command
  v
Windows
  |
  | output
  v
client.exe
  |
  | TCP + TLS
  v
Kali
```

## 9. Logs

Kali:

```bash
cat ~/Window-cli/logs/server.log
```

Windows client activity is recorded in `client.log`.

## 10. Final Setup

```text
KALI
├── server.py
├── server.crt
├── server.key
└── logs/
    └── server.log

WINDOWS
└── client.exe
```

This project demonstrates TCP sockets, TLS encryption, authentication, allowlisted remote commands, command output handling, logging, and Windows executable packaging.
