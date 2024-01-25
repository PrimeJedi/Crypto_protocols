import socket, threading, time

shutdown = False
join = False


# Функция для приема сообщений от сервера
def receving(name, sock):
    while not shutdown:
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                print(data.decode("utf-8")) # Выводим полученное сообщение на экран
                time.sleep(0.2)
        except:
            break


host = socket.gethostbyname(socket.gethostname())
port = 0

server = ('192.168.56.1', 1111) # Адрес и порт сервера

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

alias = input("Name: ") # Запрашиваем имя пользователя

rT = threading.Thread(target=receving, args=("RecvThread", s))
rT.start()


while shutdown == False:
    if join == False:
        s.sendto(("[" + alias + "] => join chat ").encode("utf-8"), server) # Отправляем сообщение о присоединении к чату на сервер
        join = True
    else:
        try:
            message = input() # Запрашиваем ввод сообщения от пользователя

            if message != "":
                s.sendto(("[" + alias + "] :: " + message).encode("utf-8"), server) # Отправляем сообщение на сервер

            time.sleep(0.2)
        except:
            s.sendto(("[" + alias + "] <= left chat ").encode("utf-8"), server) # Отправляем сообщение о выходе из чата на сервер
            shutdown = True

rT.join()
s.close() # Закрываем сокет
