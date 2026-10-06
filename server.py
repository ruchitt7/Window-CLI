import socket
import ssl
import json
import secrets
import datetime
import os


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "0.0.0.0"
PORT = 8443

CERT_FILE = "server.crt"
KEY_FILE = "server.key"

# CHANGE THIS
AUTH_TOKEN = "fSwscUi04xXkA9bP7PxT5jThHPwqzCyhWpIgPBSN17Q"

LOG_DIR = "../logs"
LOG_FILE = os.path.join(LOG_DIR, "server.log")


# ============================================================
# ALLOWED COMMANDS
# ============================================================

ALLOWED_COMMANDS = {
    "whoami",
    "hostname",
    "ipconfig",
    "systeminfo",
    "dir",
    "date"
}


# ============================================================
# LOGGING
# ============================================================

def log(message):

    os.makedirs(LOG_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().isoformat()

    with open(LOG_FILE, "a", encoding="utf-8") as file:

        file.write(
            f"[{timestamp}] {message}\n"
        )


# ============================================================
# SEND JSON
# ============================================================

def send_json(connection, data):

    message = json.dumps(
        data
    ).encode("utf-8")

    length = len(message).to_bytes(
        4,
        "big"
    )

    connection.sendall(
        length + message
    )


# ============================================================
# RECEIVE JSON
# ============================================================

def receive_json(connection):

    length_data = b""

    while len(length_data) < 4:

        chunk = connection.recv(
            4 - len(length_data)
        )

        if not chunk:

            return None

        length_data += chunk

    length = int.from_bytes(
        length_data,
        "big"
    )

    data = b""

    while len(data) < length:

        chunk = connection.recv(
            length - len(data)
        )

        if not chunk:

            raise ConnectionError(
                "Connection closed"
            )

        data += chunk

    return json.loads(
        data.decode("utf-8")
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate(connection):

    send_json(
        connection,
        {
            "type": "auth_request"
        }
    )

    response = receive_json(
        connection
    )

    if not response:

        return False

    if response.get("type") != "auth":

        return False

    received_token = response.get(
        "token",
        ""
    )

    if secrets.compare_digest(
        received_token,
        AUTH_TOKEN
    ):

        send_json(
            connection,
            {
                "type": "auth_response",
                "status": "success"
            }
        )

        return True

    send_json(
        connection,
        {
            "type": "auth_response",
            "status": "failed"
        }
    )

    return False


# ============================================================
# CLIENT HANDLER
# ============================================================

def handle_client(
    connection,
    address
):

    log(
        f"Connection from {address}"
    )

    print(
        f"\n[+] TCP/TLS connection from {address}"
    )

    try:

        authenticated = authenticate(
            connection
        )

        if not authenticated:

            print(
                "[!] Authentication failed"
            )

            log(
                f"Authentication failed: {address}"
            )

            return

        print(
            "[+] Client authenticated"
        )

        log(
            f"Authentication successful: {address}"
        )

        print(
            "\nType 'help' to see commands."
        )

        while True:

            command = input(
                "\nsecure-cli> "
            ).strip().lower()

            # --------------------------------------------
            # HELP
            # --------------------------------------------

            if command == "help":

                print(
                    "\nAllowed commands:"
                )

                for item in sorted(
                    ALLOWED_COMMANDS
                ):

                    print(
                        f"  {item}"
                    )

                print(
                    "  help"
                )

                print(
                    "  exit"
                )

                continue

            # --------------------------------------------
            # EXIT
            # --------------------------------------------

            if command == "exit":

                send_json(
                    connection,
                    {
                        "type": "command",
                        "command": "exit"
                    }
                )

                log(
                    f"Session closed by server: {address}"
                )

                break

            # --------------------------------------------
            # COMMAND VALIDATION
            # --------------------------------------------

            if command not in ALLOWED_COMMANDS:

                print(
                    "[!] Command is not allowed."
                )

                continue

            # --------------------------------------------
            # SEND COMMAND
            # --------------------------------------------

            send_json(
                connection,
                {
                    "type": "command",
                    "command": command
                }
            )

            log(
                f"Command sent: {command}"
            )

            # --------------------------------------------
            # RECEIVE RESULT
            # --------------------------------------------

            response = receive_json(
                connection
            )

            if not response:

                print(
                    "[!] No response received."
                )

                break

            output = response.get(
                "output",
                ""
            )

            print(
                "\n" + output
            )

            log(
                f"Result received for: {command}"
            )

    except Exception as error:

        print(
            f"\n[!] Client error: {error}"
        )

        log(
            f"Client error {address}: {error}"
        )

    finally:

        try:
            connection.shutdown(
                socket.SHUT_RDWR
            )
        except Exception:
            pass

        connection.close()

        log(
            f"Connection closed: {address}"
        )

        print(
            "\n[*] Connection closed."
        )


# ============================================================
# MAIN SERVER
# ============================================================

def main():

    print("=" * 60)
    print("       SECURE REMOTE CLI SERVER")
    print("=" * 60)

    print(
        f"[*] Server IP : {HOST}"
    )

    print(
        f"[*] Port      : {PORT}"
    )

    print(
        "[*] Protocol  : TCP + TLS"
    )

    print(
        "[*] Commands  : Allowlisted"
    )

    print("=" * 60)

    # --------------------------------------------------------
    # TLS SERVER CONFIGURATION
    # --------------------------------------------------------

    tls_context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_SERVER
    )

    tls_context.minimum_version = (
        ssl.TLSVersion.TLSv1_2
    )

    tls_context.load_cert_chain(
        certfile=CERT_FILE,
        keyfile=KEY_FILE
    )

    # --------------------------------------------------------
    # TCP SOCKET
    # --------------------------------------------------------

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen(5)

    print(
        f"\n[*] Listening on {HOST}:{PORT}"
    )

    print(
        "[*] Waiting for authorized client..."
    )

    log(
        f"Server started on port {PORT}"
    )

    try:

        while True:

            raw_connection, address = (
                server_socket.accept()
            )

            try:

                tls_connection = (
                    tls_context.wrap_socket(
                        raw_connection,
                        server_side=True
                    )
                )

                handle_client(
                    tls_connection,
                    address
                )

            except ssl.SSLError as error:

                print(
                    f"[!] TLS error: {error}"
                )

                log(
                    f"TLS error: {error}"
                )

                raw_connection.close()

    except KeyboardInterrupt:

        print(
            "\n[*] Server stopped."
        )

    finally:

        server_socket.close()

        log(
            "Server stopped"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()
