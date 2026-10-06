# Secure Remote CLI — Quick Setup

## Project

- Kali Linux = Server
- Windows = Client
- Protocol = TCP + TLS
- Port = 8443
- Final Windows file = `client.exe`

> Use only on systems you own or are authorized to test.

## 1. Kali Setup

Create folders:

```bash
mkdir -p ~/secure-remote-cli/server
mkdir -p ~/secure-remote-cli/logs
cd ~/secure-remote-cli/server
```

Generate TLS files:

```bash
openssl genrsa -out server.key 2048
```

```bash
openssl req -new -x509 -key server.key -out server.crt -days 365 -subj "/CN=SecureRemoteCLI"
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
Kali = 192.168.31.251
```

In `client.py`:

```python
SERVER_HOST = "192.168.31.251"
SERVER_PORT = 8443
```

Replace the example with your current Kali IP.

In `server.py` keep:

```python
HOST = "0.0.0.0"
PORT = 8443
```

Do not put the Windows IP in `server.py`.

## 3. Start Kali Server

```bash
cd ~/secure-remote-cli/server
python3 server.py
```

Expected:

```text
[*] Listening on 0.0.0.0:8443
[*] Waiting for authorized client...
```

Check:

```bash
sudo ss -lntp | grep 8443
```

## 4. Test Windows to Kali

PowerShell:

```powershell
ping 192.168.31.251
```

Then:

```powershell
Test-NetConnection 192.168.31.251 -Port 8443
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
python3 ~/secure-remote-cli/server/server.py
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
cat ~/secure-remote-cli/logs/server.log
```

Windows client activity is recorded in `client.log`.

## 10. Troubleshooting

Kali IP:

```bash
ip addr
```

Server port:

```bash
sudo ss -lntp | grep 8443
```

Windows connection:

```powershell
Test-NetConnection <KALI_IP> -Port 8443
```

If Kali's IP changes:

1. Update `SERVER_HOST` in `client.py`.
2. Rebuild:

```powershell
pyinstaller --onefile --noconsole --clean client.py
```

3. Copy the new `dist\client.exe` to Windows.

## 11. Final Setup

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
