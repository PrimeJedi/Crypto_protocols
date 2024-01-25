import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import traceback
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa

SERVER_ADDRESS = 'localhost'
BOB_PORT = 2222
ALICE_PORT = 2223
MESSAGE_LENGTH = 4096

# Шифрование сообщения побитовым сложением с session_key
def encrypt_message(message, session_key):
    encrypted_message = bytearray()
    for i in range(len(message)):
        encrypted_message.append(message[i] ^ session_key[i % len(session_key)])
    return encrypted_message

# Расшифрование сообщения побитовым сложением с session_key
def decrypt_message(encrypted_message, session_key):
    decrypted_message = bytearray()
    for i in range(len(encrypted_message)):
        decrypted_message.append(encrypted_message[i] ^ session_key[i % len(session_key)])
    return decrypted_message

def send_message(conn, session_key, message_entry, send_event, message_history):
    try:
        while True:
            send_event.wait()
            message = message_entry.get()
            if message:
                encrypted_message = encrypt_message(message.encode(), session_key)
                conn.send(encrypted_message)
                message_history.insert(tk.END, f"You: {message}\n")
                message_entry.delete(0, tk.END)
                send_event.clear()
    except Exception as e:
        print(f"Error sending messages: {e}")
        traceback.print_exc()
    finally:
        conn.close()

def receive_message(conn, session_key, message_history):
    try:
        while True:
            received_message = conn.recv(MESSAGE_LENGTH)
            if not received_message:
                break
            decrypted_message = decrypt_message(received_message, session_key)
            message_history.insert(tk.END, f"Alice: {decrypted_message.decode()}\n")
    except Exception as e:
        print(f"Error receiving messages: {e}")
        traceback.print_exc()
    finally:
        conn.close()

class ChatGUI:
    def __init__(self, root, send_func):
        self.root = root
        self.root.title("Chat")

        self.message_history = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.message_history.pack(expand=True, fill='both')

        self.message_entry = tk.Entry(root, width=40)
        self.message_entry.pack(expand=True, fill='x', side='left')

        self.send_event = threading.Event()
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(side='right')

        self.send_func = send_func

    def send_message(self):
        self.send_event.set()
        self.send_func(self.message_entry.get())  # Передача сообщения в функцию отправки
        self.message_entry.delete(0, tk.END)

def main():
    def send_message_to_alice(message):
        try:
            encrypted_message = encrypt_message(message.encode(), session_key)
            alice_conn.send(encrypted_message)
            chat_gui.message_history.insert(tk.END, f"You: {message}\n")
        except Exception as e:
            print(f"Error sending messages: {e}")
            traceback.print_exc()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bob_socket:
            bob_socket.connect((SERVER_ADDRESS, BOB_PORT))
            trent_public_key = bob_socket.recv(MESSAGE_LENGTH)

            bob_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            bob_public_key = bob_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            bob_socket.send(bob_public_key)
            trent_public_key = bob_socket.recv(MESSAGE_LENGTH)
            # Ожидание и прием подписей
            # Создание сессионного ключа и временной метки

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bob_socket:
            bob_socket.bind((SERVER_ADDRESS, BOB_PORT))
            bob_socket.listen(1)

            print("Waiting for Alice's connection...")
            alice_conn, alice_addr = bob_socket.accept()

            # Создание сессионного ключа и временной метки
            # Подпись сообщения и отправка Алисе

            print(f"Connected to Alice: {alice_addr}")

            alice_public_key = alice_conn.recv(MESSAGE_LENGTH)
            encrypted_message = receive_complete_message(alice_conn)
            signature = receive_complete_message(alice_conn)

            alice_public_key_obj = serialization.load_pem_public_key(alice_public_key)

            try:
                decrypted_message = bob_private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                alice_public_key_obj.verify(
                    signature,
                    decrypted_message,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
                print("Signature verified")
                session_key = decrypted_message[:32]
                timestamp = decrypted_message[32:]
                print(f"Session Key: {session_key}")
                print(f"Timestamp: {timestamp.decode()}")
            except Exception as e:
                print(f"Signature not verified: {e}")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bob_socket:
            bob_socket.bind((SERVER_ADDRESS, ALICE_PORT))
            bob_socket.listen(1)

            print("Waiting for Alice's connection...")
            alice_conn, alice_addr = bob_socket.accept()
            print(f"Connection with Alice established: {alice_addr}")

            root = tk.Tk()
            chat_gui = ChatGUI(root, send_message_to_alice)

            receive_thread = threading.Thread(target=receive_message, args=(alice_conn, session_key, chat_gui.message_history))
            send_thread = threading.Thread(target=send_message, args=(alice_conn, session_key, chat_gui.message_entry, chat_gui.send_event, chat_gui.message_history))

            receive_thread.start()
            send_thread.start()

            root.mainloop()


    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

def receive_complete_message(conn):
    received_message = b""
    while True:
        chunk = conn.recv(MESSAGE_LENGTH)
        received_message += chunk
        if len(chunk) < MESSAGE_LENGTH:
            break
    return received_message

if __name__ == "__main__":
    main()
