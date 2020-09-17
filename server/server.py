import socket
import tqdm
import os
import operator
from functools import reduce
from threading import Thread

# device's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001

# receive 4096 bytes each time
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
        # remove absolute path if there is
        filename = os.path.basename(filename)
        filename = self._get_valid_filename(filename)

        file_path = f"{RECEIVE_FOLDER}/{filename}"

        # convert to integer
        filesize = int(filesize)

        # start receiving the file from the socket
        # and writing to the file stream
        progress = tqdm.tqdm(range(filesize), f"[*] Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024, leave=False)
        with open(file_path, "wb") as f:
            for _ in progress:
                # read 1024 bytes from the socket (receive)
                bytes_read = self.sock.recv(BUFFER_SIZE)
                if not bytes_read:
                    # nothing is received
                    # file transmitting is done
                    break
                # write to the file the bytes we just received
                f.write(bytes_read)
                # update the progress bar
                progress.update(len(bytes_read))

            print(f"[+] File received: {filename}")
            self._close()

    def _close(self):
        self.sock.close()
        print(f"[+] {self.addr[0]}:{self.addr[1]} is disconnected.")


def main():
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
    main()
