# Импорт необходимых библиотек
import socket  # Для сетевых соединений
import hashlib  # Для хеширования данных
import secrets  # Для генерации случайных чисел
import threading  # Для многозадачности
import tkinter as tk  # Для создания графического интерфейса

# Определение класса ChatClient
class ChatClient:
    def __init__(self, root, host, port, secret_key):
        # Инициализация объекта класса
        self.root = root
        self.client_socket = None
        self.host = host
        self.port = port
        self.secret_key = secret_key

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
        hash_object = hashlib.md5(self.secret_key + data.encode())
        return hash_object.hexdigest()

    def receive_message(self):
        # Получение сообщения от другой стороны через сокет
        return self.client_socket.recv(1024).decode()

    def send_message(self, message):
        # Отправка сообщения другой стороне через сокет
        self.client_socket.sendall(message.encode())

    def send_messages(self, event=None):
        # Отправка сообщения при нажатии кнопки
        message_to_send = self.message_entry.get()
        self.chat_log.insert(tk.END, "Боб: " + message_to_send + "\n")
        self.send_message(message_to_send)
        self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        # Бесконечный цикл для приема сообщений
        while True:
            received_message = self.receive_message()
            self.chat_log.insert(tk.END, "Алиса: " + received_message + "\n")

    def initiate_connection(self):
        # Инициация сетевого соединения
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

        random_alica = str(secrets.randbelow(1000))
        self.send_message(random_alica)

        random_bob = self.receive_message()
        A = "Боб"

        hash_value_Alice = self.md5_hash(f"{random_bob}{A}")
        self.send_message(hash_value_Alice)

        received_hash_Alice = self.receive_message()
        hash_value = self.md5_hash(f"{random_alica}{random_bob}Алиса")
        if hash_value == received_hash_Alice:
            print("Успешное соединение с Алисой")

        # Запуск потоков для отправки и приема сообщений
        send_thread = threading.Thread(target=self.send_messages)
        receive_thread = threading.Thread(target=self.receive_messages)

        send_thread.start()
        receive_thread.start()

# Точка входа в программу
if __name__ == "__main__":
    HOST = '192.168.56.1'
    PORT = 2222
    SECRET_KEY = b"most_secret_key"

    root = tk.Tk()
    root.title("Чат с Алисой")

    # Создание экземпляра класса ChatClient
    chat_client = ChatClient(root, HOST, PORT, SECRET_KEY)

    # Запуск основного цикла обработки событий GUI
    root.mainloop()
