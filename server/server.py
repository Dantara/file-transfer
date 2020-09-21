import socket
import sys
import os
import operator
from threading import Thread

SERVER_HOST = "0.0.0.0"
DEFAULT_PORT = 4000

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

RECEIVE_FOLDER = "received"

class ClientListener(Thread):
    def __init__(self, sock, addr):
        super().__init__(daemon=True)
        self.sock = sock
        self.addr = addr

    def _is_file_exist(self, filename):
        return os.path.isfile(f"{RECEIVE_FOLDER}/{filename}")

    def _add_copy_suffix(self, filename, n):
        components = filename.split(".")

        if(len(components) == 1):
            return f"{filename}_copy{n}"

        head, *tail = components

        tail = ".".join(tail)

        return f"{head}_copy{n}.{tail}"

    def _get_valid_filename(self, filename):
        if(not self._is_file_exist(filename)):
            return filename

        n = 1

        while(self._is_file_exist(self._add_copy_suffix(filename, n))):
            n += 1

        return self._add_copy_suffix(filename, n)

    def run(self):
        received = self.sock.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filename = self._get_valid_filename(filename)

        file_path = f"{RECEIVE_FOLDER}/{filename}"

        filesize = int(filesize)

        with open(file_path, "wb") as f:
            while(True):
                bytes_read = self.sock.recv(BUFFER_SIZE)

                if not bytes_read:
                    break

                f.write(bytes_read)

            print(f"[+] File received: {filename}")
            self._close()

    def _close(self):
        self.sock.close()
        print(f"[+] {self.addr[0]}:{self.addr[1]} is disconnected.")


def main(argv):
    SERVER_PORT = int(argv[0]) if len(argv) == 1 else DEFAULT_PORT

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((SERVER_HOST, SERVER_PORT))
    sock.listen()

    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

    while True:
        con, addr = sock.accept()

        print(f"[+] {addr[0]}:{addr[1]} is connected.")

        ClientListener(con, addr).start()


if __name__ == "__main__":
    main(sys.argv[1:])
