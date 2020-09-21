import socket
import sys
import os
import operator
from threading import Thread

# Server host name
SERVER_HOST = "0.0.0.0"

# Default port (can be cahnged via command line option)
DEFAULT_PORT = 4000

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

# Separate folder to store recived files
RECEIVE_FOLDER = "received"

class ClientListener(Thread):
    def __init__(self, sock, addr):
        super().__init__(daemon=True)
        self.sock = sock
        self.addr = addr

    # Checking whether file exist or not
    def _is_file_exist(self, filename):
        return os.path.isfile(f"{RECEIVE_FOLDER}/{filename}")

    # Add copy suffix
    def _add_copy_suffix(self, filename, n):
        components = filename.split(".")

        if(len(components) == 1):
            return f"{filename}_copy{n}"

        head, *tail = components

        tail = ".".join(tail)

        return f"{head}_copy{n}.{tail}"

    # Add copy suffix if needed
    def _get_valid_filename(self, filename):
        if(not self._is_file_exist(filename)):
            return filename

        n = 1

        while(self._is_file_exist(self._add_copy_suffix(filename, n))):
            n += 1

        return self._add_copy_suffix(filename, n)

    def run(self):
        # Get file name
        received = self.sock.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filename = self._get_valid_filename(filename)

        # Create path to file
        file_path = f"{RECEIVE_FOLDER}/{filename}"

        filesize = int(filesize)

        # Recieve the file
        with open(file_path, "wb") as f:
            while(True):
                # Read from socket
                bytes_read = self.sock.recv(BUFFER_SIZE)

                # Stop if file fully recieved
                if not bytes_read:
                    break

                # Write to file
                f.write(bytes_read)

            print(f"[+] File received: {filename}")
            self._close()

    def _close(self):
        # Close connection
        self.sock.close()
        print(f"[+] {self.addr[0]}:{self.addr[1]} is disconnected.")


def main(argv):
    # Change default port if needed
    SERVER_PORT = int(argv[0]) if len(argv) == 1 else DEFAULT_PORT

    # Setting socket options
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind socket
    sock.bind((SERVER_HOST, SERVER_PORT))
    sock.listen()

    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    while True:
        con, addr = sock.accept()

        print(f"[+] {addr[0]}:{addr[1]} is connected.")

        # Start new thread for new user
        ClientListener(con, addr).start()


if __name__ == "__main__":
    main(sys.argv[1:])
