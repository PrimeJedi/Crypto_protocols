# Импортируем модули socket и time
import socket, time

# Получаем IP-адрес хоста и порт
host = socket.gethostbyname(socket.gethostname())
port = 1111

# Создаем список для хранения клиентов
clients = []

# Создаем сокет
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

# Устанавливаем флаг выхода из программы в False
quit = False

# Выводим сообщение о запуске сервера
print("[ ---- Server Started ---- ]")

# Запускаем бесконечный цикл обработки сообщений
while not quit:
    try:
        # Принимаем данные и адрес отправителя
        data, addr = s.recvfrom(1024)

        # Если адрес отправителя не находится в списке клиентов, добавляем его
        if addr not in clients:
            clients.append(addr)

        # Получаем текущее время
        itsatime = time.strftime("%Y-%m-%d-%H.%M.%S", time.localtime())

        # Выводим информацию об отправителе и сообщение
        print("[" + addr[0] + "]=[" + str(addr[1]) + "]=[" + itsatime + "]/", end="")
        print(data.decode("utf-8"))

        # Отправляем сообщение всем клиентам, кроме отправителя
        for client in clients:
            if addr != client:
                s.sendto(data, client)
    except:
        # В случае ошибки выводим сообщение о завершении работы сервера
        print("\n[ ---- Server Stopped ---- ]")
        quit = True

# Закрываем сокет
s.close()
