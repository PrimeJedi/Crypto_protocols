import socket
import random
from math import isqrt

# Константы для генерации случайных чисел
RANDOM_MIN_NUM = 0
RANDOM_MAX_NUM = 7
RANDOM_DEGREE = 5

def my_gcd(a, b):
    # Нахождение наибольшего общего делителя
    while b:
        a, b = b, a % b
    return a

def create_prime_number():
    # Генерация простого числа
    while True:
        p = random.randint(RANDOM_MIN_NUM, RANDOM_MAX_NUM ** RANDOM_DEGREE)
        if is_prime(p):
            return p

def is_prime(num):
    # Проверка числа на простоту
    for n in range(2, isqrt(num) + 1):
        if num % n == 0:
            return False
    return True

def pow(num, degree, module):
    # Модульное возведение в степень
    result = 1
    num = num % module
    while degree > 0:
        if degree % 2 == 1:
            result = (result * num) % module
        degree //= 2
        num = (num ** 2) % module
    return result


# Создание сокета и подключение к localhost на порту 2222
sock = socket.socket()
sock.connect(('localhost', 2222))

q, p = 0, 0
status = False

while not status:
    # Генерация простого числа p и q
    q = create_prime_number()
    p = 2 * q + 1
    status = is_prime(p)

n = p * q
sock.send(str(n).encode())
print('Отправлено n')

s = random.randint(1, n - 1)
while my_gcd(s, n) != 1:
    s = random.randint(1, n - 1)

v = pow(s, 2, n)
sock.send(str(v).encode())
print('Отправлено V')
print(f's = {s} v = {v} p = {p} q = {q} n = {n}')

rounds = 3

for i in range(rounds):
    print(f'\nРаунд № {i + 1}')
    r = random.randint(1, n - 1)
    x = pow(r, 2, n)
    sock.send(str(x).encode())
    print('Отправлен x = ', x)

    str_e = sock.recv(1024)
    e = int(str_e)
    print(f'Получено случайное число: {e}')
    print(f'r = {r} x = {x} n = {n}')

    if e == 0:
        y = r
    else:
        r_mod_n = r % n
        s_e_mod_n = pow(s, e, n)
        y = r_mod_n * s_e_mod_n % n

    sock.send(str(y).encode())
    print('Отправлен y')

    message_from_server = sock.recv(1024)
    print(message_from_server.decode('utf-8'))

sock.close()
