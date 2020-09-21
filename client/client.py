import socket
import tqdm
import os
import sys

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096

def main(argv):
    # Handling the wrong number of arguments
    if len(argv) != 3:
        print("You are specifed wrong number of arguments.")
        print("You should launch this app in the following way:")
        print("python client.py FILE_NAME SERVER_NAME SERVER_PORT\n")
        print("Here is an example:")
        print("python client.py test.file 127.0.0.1 5000")
    else:
        # Parsing command line options
        filename = argv[0]
        host = argv[1]
        port = int(argv[2])

        # Get file size
        filesize = os.path.getsize(filename)
        s = socket.socket()

        # Connecting to remote host
        print(f"[+] Connecting to {host}:{port}")
        s.connect((host, port))
        print("[+] Connected.")

        # Seneing file name and file size
        s.send(f"{filename}{SEPARATOR}{filesize}".encode())

        # Creating progress bar
        progress = tqdm.tqdm(range(filesize), f"[*] Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024, leave=False)

        with open(filename, "rb") as f:
            for _ in progress:
                # Read the file
                bytes_read = f.read(BUFFER_SIZE)

                # Stop if full file was read
                if not bytes_read:
                    break

                # Send buffer data
                s.sendall(bytes_read)
                # Update progress bar state
                progress.update(len(bytes_read))

            print(f"[+] File {filename} was sent.")
            s.close()

if __name__ == "__main__":
    main(sys.argv[1:])
