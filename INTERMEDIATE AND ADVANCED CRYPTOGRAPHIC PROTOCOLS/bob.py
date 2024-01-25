import random
import socket


def pow(num, degree, module):
    # Модульное возведение в степень
    bin_str = bin(degree)[2:][::-1]

    y, s = 1, num

    for val in bin_str:
        if val == "1":
            y = y * s % module
        s = s * s % module
    return y

sock = socket.socket()
sock.bind(('localhost', 2222))
sock.listen(5)
conn, addr = sock.accept()
print('Подключен к:', addr)

n = int(conn.recv(1024).decode())
v = int(conn.recv(1024))
print('n =', n, "   v =", v)


round_ = 0

while True:
    round_ += 1
    print('\nРаунд:', round_)

    x = int(conn.recv(1024).decode())
    print('Принял число X:', x)

    e = random.randint(0, 1)
    conn.send(str(e).encode())
    print('Случайное число от 0 до 1:', e)

    y = int(conn.recv(1024))
    print('y от клиента =', y)

    if y == 0:
        print(False)
        break

    y2 = pow(y, 2, n)
    print('y^2 =', y2)

    x_mod_n = x % n
    v_e_mod_n = pow(v, e, n)
    checking = (x_mod_n * v_e_mod_n) % n
    print('Проверка =', checking)
    if int(y2) == int(checking) and round_ == 3:
        print('Раунд успешно пройден')
        message_done = '\nАвторизация прошла успешно'
        print(message_done)
        conn.send(message_done.encode())
        break

    if int(y2) == int(checking):
        message_round_ok = 'Раунд успешно пройден'
        print(message_round_ok)
        conn.send(message_round_ok.encode())

    if int(y2) != int(checking):
        message_fail = 'Конец\nАвторизация не прошла'
        print(message_fail)
        conn.send(message_fail.encode())

conn.close()
sock.close()
