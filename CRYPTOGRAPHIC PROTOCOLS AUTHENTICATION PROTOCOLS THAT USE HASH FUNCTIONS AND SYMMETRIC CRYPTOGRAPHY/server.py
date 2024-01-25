# Импорт необходимых библиотек
import socket  # Для сетевых соединений
import hashlib  # Для хеширования данных
import secrets  # Для генерации случайных чисел
import threading  # Для многозадачности
import tkinter as tk  # Для создания графического интерфейса

# Задание глобальных констант
HOST = '192.168.56.1'  # IP-адрес хоста
PORT = 2222  # Порт для соединения
SECRET_KEY = b"most_secret_key"  # Секретный ключ для хеширования

# Определение класса ChatClient
class ChatClient:
    def __init__(self, root):
        # Инициализация объекта класса
        self.root = root
        self.server_conn = None

        # Настройка GUI
        self.chat_log = tk.Text(root, width=50, height=20)  # Поле вывода чата
        self.chat_log.pack()

        self.message_entry = tk.Entry(root, width=50)  # Поле ввода сообщения
        self.message_entry.pack()

        self.send_button = tk.Button(root, text="Отправить", command=self.send_messages)  # Кнопка отправки сообщения
        self.send_button.pack()

        # Запуск инициации соединения
        self.initiate_connection()

    def md5_hash(self, data):
        # Вычисление MD5 хэша от данных с использованием секретного ключа
        hash_object = hashlib.md5(SECRET_KEY + data.encode())
        return hash_object.hexdigest()

    def receive_message(self, conn):
        # Получение сообщения от другой стороны через сокет
        return conn.recv(1024).decode()

    def send_message(self, conn, message):
        # Отправка сообщения другой стороне через сокет
        conn.sendall(message.encode())

    def send_messages(self, event=None):
        # Отправка сообщения при нажатии кнопки
        message_to_send = self.message_entry.get()
        self.chat_log.insert(tk.END, "Алиса: " + message_to_send + "\n")
        self.send_message(self.server_conn, message_to_send)
        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        # Бесконечный цикл для приема сообщений
        while True:
            received_message = self.receive_message(self.server_conn)
            self.chat_log.insert(tk.END, "Боб: " + received_message + "\n")

    def initiate_connection(self):
        # Инициация сетевого соединения
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))  # Привязка сокета к адресу и порту
            s.listen()  # Ожидание входящего соединения

            conn, addr = s.accept()  # Принятие соединения
            self.server_conn = conn

            random_alica = self.receive_message(self.server_conn)
            random_bob = str(secrets.randbelow(1000))
            self.send_message(self.server_conn, random_bob)
            B = "Алиса"

            hash_value = self.md5_hash(f"{random_alica}{random_bob}{B}")
            self.send_message(self.server_conn, hash_value)

            received_hash_Alice = self.receive_message(self.server_conn)
            calculated_hash_value = self.md5_hash(f"{random_bob}Bob")
            if received_hash_Alice == calculated_hash_value:
                print("Успешное соединение с Бобом")

            # Запуск потоков для отправки и приема сообщений
            send_thread = threading.Thread(target=self.send_messages)
            receive_thread = threading.Thread(target=self.receive_messages)

            send_thread.start()
            receive_thread.start()

# Точка входа в программу
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Чат с Бобом")

    # Создание экземпляра класса ChatClient
    chat_client = ChatClient(root)

    # Запуск основного цикла обработки событий GUI
    root.mainloop()
