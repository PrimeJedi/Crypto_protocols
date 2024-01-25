import socket
import threading
import traceback
import os
import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
import tkinter as tk
from tkinter import scrolledtext

SERVER_ADDRESS = 'localhost'
BOB_PORT = 2222
ALICE_PORT = 2223
BUFFER_SIZE = 4096

def verify_signature(public_key_obj, signature, data):
    try:
        public_key_obj.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Подпись верна")
    except Exception as e:
        print(f"Подпись не верна: {e}")

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

def create_gui(receive_func, send_func):
    root = tk.Tk()
    root.title("Chat")

    # Создаем виджет для отображения сообщений
    messages_text = scrolledtext.ScrolledText(root, width=50, height=20, wrap=tk.WORD)
    messages_text.grid(column=0, row=0, padx=10, pady=10, columnspan=2)

    # Создаем виджет для ввода сообщений
    entry_var = tk.StringVar()
    entry = tk.Entry(root, textvariable=entry_var, width=40)
    entry.grid(column=0, row=1, padx=10, pady=10)

    # Функция для отправки сообщений при нажатии Enter
    def send_message(event):
        message = entry_var.get()
        send_func(message)
        entry_var.set("")

        # Отображение отправленного сообщения у отправителя
        messages_text.insert(tk.END, f"You: {message}\n")
        messages_text.see(tk.END)  # Прокрутка вниз

    root.bind("<Return>", send_message)

    send_button = tk.Button(root, text="Send", command=lambda: send_message(None))
    send_button.grid(column=1, row=1, padx=10, pady=10)

    def display_message(sender, message):
        if sender == "You":
            messages_text.insert(tk.END, f"{sender}: {message}\n")
        else:
            messages_text.insert(tk.END, f"Bob: {message}\n")
        messages_text.see(tk.END)

    # Запуск потока для приема сообщений
    receive_thread = threading.Thread(target=receive_func, args=(display_message,))
    receive_thread.start()

    root.protocol("WM_DELETE_WINDOW", root.quit)  # Закрытие окна приложения

    root.mainloop()

def gui_communicate_with_partner(conn, session_key, display_message_func):
    try:
        while True:
            message = input("You: ")
            encrypted_message = encrypt_message(message.encode(), session_key)
            conn.send(encrypted_message)
            display_message_func("You", message)
    except Exception as e:
        print(f"Ошибка при отправке сообщений: {e}")
        traceback.print_exc()
    finally:
        conn.close()

def gui_receive_and_print_messages(conn, sender, session_key, display_message_func):
    try:
        while True:
            received_message = conn.recv(BUFFER_SIZE)
            if not received_message:
                break
            decrypted_message = decrypt_message(received_message, session_key)
            display_message_func(sender, decrypted_message.decode())
    except Exception as e:
        print(f"Ошибка при приеме сообщений от {sender}: {e}")
        traceback.print_exc()
    finally:
        conn.close()

def create_gui_threads(conn, session_key):
    # Функции для использования в графическом интерфейсе
    def send_func(message):
        encrypted_message = encrypt_message(message.encode(), session_key)
        conn.send(encrypted_message)

    def receive_func(display_message_func):
        while True:
            received_message = conn.recv(BUFFER_SIZE)
            if not received_message:
                break
            decrypted_message = decrypt_message(received_message, session_key)
            display_message_func("Bob", decrypted_message.decode())

    # Запуск графического интерфейса
    create_gui(receive_func, send_func)

def main():
    try:
        # Установка соединения Алиса-Трент
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as alice_socket:
            alice_socket.connect((SERVER_ADDRESS, BOB_PORT))

            # Получение публичного ключа Трента
            trent_public_key = alice_socket.recv(BUFFER_SIZE)
            trent_public_key_obj = serialization.load_pem_public_key(trent_public_key)

            # Генерация ключей для Алисы
            alice_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            alice_public_key_bytes = alice_private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Отправка публичного ключа Алисы и получение подписи
            alice_socket.send(alice_public_key_bytes)
            signature_alice = alice_socket.recv(BUFFER_SIZE)
            signature_bob = alice_socket.recv(BUFFER_SIZE)
            bob_public_key_bytes = alice_socket.recv(BUFFER_SIZE)
            bob_public_key_obj = serialization.load_pem_public_key(bob_public_key_bytes)

            # Проверка подписей
            verify_signature(trent_public_key_obj, signature_alice, alice_public_key_bytes)
            verify_signature(trent_public_key_obj, signature_bob, bob_public_key_bytes)

        # Установка соединения Боб-Алиса
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bob_socket:
            bob_socket.connect((SERVER_ADDRESS, BOB_PORT))

            # Генерация сессионного ключа и временной метки
            session_key = os.urandom(16)

            timestamp = datetime.datetime.now().isoformat()

            # Подпись сообщения Алисы и шифрование для Боба
            message = session_key + timestamp.encode()
            signed_message = alice_private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            encrypted_message = bob_public_key_obj.encrypt(
                message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Отправка публичного ключа Алисы, зашифрованного сообщения и подписи
            bob_socket.send(alice_public_key_bytes)
            bob_socket.send(encrypted_message)
            bob_socket.send(signed_message)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as alice_socket:
                alice_socket.connect((SERVER_ADDRESS, ALICE_PORT))
                create_gui_threads(alice_socket, session_key)
    except Exception as e:
        print(f"Ошибка: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
