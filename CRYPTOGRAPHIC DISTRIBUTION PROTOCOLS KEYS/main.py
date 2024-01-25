import rsa
import threading
import socket
import tkinter as tk


# Получение выбора от пользователя
choise = input("Меню:\n"
      "1. Режим хоста\n"
      "2. Режим клиента\n"
      "Выберите пункт меню: ")

# Генерация ключей RSA
public_key, private_key = rsa.newkeys(1024)
public_partner = None

# Логика в зависимости от выбора
if choise == "1":
    # Режим хоста: создание сервера, прослушивание и ожидание подключения клиента
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("192.168.56.1", 2222))
    server.listen()
    client, _ = server.accept()
    
    # Отправка открытого ключа клиенту и получение его открытого ключа
    client.send(public_key.save_pkcs1("PEM"))
    public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))

elif choise == "2":
    # Режим клиента: подключение к серверу и обмен открытыми ключами с сервером
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("192.168.56.1", 2222))
    
    # Получение открытого ключа хоста и отправка своего открытого ключа
    public_partner = rsa.PublicKey.load_pkcs1(client.recv(1024))
    client.send(public_key.save_pkcs1("PEM"))

else:
    # Если выбрано что-то отличное от 1 или 2, выход из программы
    exit()

# Функция отправки сообщений
def sending_encript_message(c):
    while True:
        message = input("")
        encrypted_message = rsa.encrypt(message.encode(), pub_key=public_partner)
        c.send(encrypted_message)

# Функция приема сообщений
def recv_encript_message(c):
    while True:
        encrypted_message = c.recv(1024)
        decrypted_message = rsa.decrypt(encrypted_message, private_key).decode()
        display_message("Bob", decrypted_message)

# Функция отображения сообщения в окне чата
def display_message(sender, message):
    chat_log.insert("end", f"{sender}: {message}\n")

# Запуск двух потоков для отправки и приема сообщений
threading.Thread(target=sending_encript_message, args=(client,)).start()
threading.Thread(target=recv_encript_message, args=(client,)).start()

# Функция для отправки сообщения из окна ввода
def send_message():
    message = entry.get()
    encrypted_message = rsa.encrypt(message.encode(), pub_key=public_partner)
    client.send(encrypted_message)
    display_message("Alisa", message)
    entry.delete(0, "end")

# Создание графического интерфейса с использованием tkinter
root = tk.Tk()
root.title("Чат для клиентов")

frame = tk.Frame(root)
frame.pack(pady=10)

chat_log = tk.Text(frame, width=40, height=10)
chat_log.grid(row=0, column=0, columnspan=2)

entry = tk.Entry(frame, width=40)
entry.grid(row=1, column=0)

send_button = tk.Button(frame, text="Отправить\n сообщение", command=send_message)
send_button.grid(row=1, column=1)

root.mainloop()
