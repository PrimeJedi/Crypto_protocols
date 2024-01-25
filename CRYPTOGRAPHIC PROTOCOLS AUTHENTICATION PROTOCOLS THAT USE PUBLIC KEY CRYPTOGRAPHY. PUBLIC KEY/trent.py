import socket
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def establish_connection():
    trent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trent_socket.bind(('localhost', 2222))
    trent_socket.listen(2)
    print("Trent is waiting for connections...")

    alice_conn, alice_addr = trent_socket.accept()
    print(f"Connected to Alice: {alice_addr}")
    bob_conn, bob_addr = trent_socket.accept()
    print(f"Connected to Bob: {bob_addr}")

    return trent_socket, alice_conn, bob_conn


def generate_and_send_public_key(connection, public_key):
    connection.send(public_key)


def receive_public_keys(connection):
    public_key_data = connection.recv(4096)
    public_key = serialization.load_pem_public_key(public_key_data, backend=default_backend())
    return public_key


def create_signature(private_key, public_key):
    signature = private_key.sign(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def send_signature(connection, signature):
    connection.send(signature)


def main():
    trent_socket, alice_conn, bob_conn = establish_connection()

    trent_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    trent_public_key_obj = trent_private_key.public_key()
    trent_public_key = trent_public_key_obj.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    generate_and_send_public_key(alice_conn, trent_public_key)
    generate_and_send_public_key(bob_conn, trent_public_key)

    alice_public_key = receive_public_keys(alice_conn)
    bob_public_key = receive_public_keys(bob_conn)

    signature_alice = create_signature(trent_private_key, alice_public_key)
    signature_bob = create_signature(trent_private_key, bob_public_key)

    send_signature(alice_conn, signature_alice)
    send_signature(alice_conn, signature_bob)
    alice_conn.send(bob_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))
    print("Signed keys for Alice and Bob sent to Alice")

    alice_conn.close()
    bob_conn.close()
    trent_socket.close()


if __name__ == "__main__":
    main()
