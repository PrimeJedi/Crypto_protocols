import random


def power_mod(base, exponent, modulus):
    result = 1
    while exponent > 0:
        # Если показатель степени нечетный, то умножаем результат на основание и берем остаток от деления на модуль.
        if exponent % 2 == 1:
            result = (result * base) % modulus
        # В остальных случаях, основание возводится в квадрат и берется остаток от деления на модуль.
        base = (base * base) % modulus
        # Показатель степени уменьшается вдвое.
        exponent = exponent // 2
    return result


def gcd(a, b):
    while b != 0:
        # Если b не равно 0, то значение a присваивается b, а значение b присваивается остатку от деления a на b.
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    if a == 0:
        # Если a равно 0, то возвращается кортеж (b, 0, 1).
        return b, 0, 1
    else:
        # В остальных случаях, рекурсивно вызывается функция extended_gcd с аргументами (b % a, a)
        gcd, x, y = extended_gcd(b % a, a)
        # Возвращается кортеж (gcd, y - (b // a) * x, x), где gcd - наибольший общий делитель, x и y - коэффициенты Безу
        return gcd, y - (b // a) * x, x


def is_prime(n, k=5):
    if n <= 1 or n == 4:
        # Если число n меньше или равно 1 или равно 4, то возвращается False.
        return False
    if n <= 3:
        # Если число n меньше или равно 3, то возвращается True.
        return True

    # Вложенная функция check_composite(a, d, s, n) проверяет, является ли число n составным для данного значения a, d и s.
    def check_composite(a, d, s, n):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(s - 1):
            # Генерируется случайное число a от 2 до n - 2.
            x = pow(x, 2, n)
            if x == n - 1:
                # Если check_composite(a, d, s, n) возвращает True, то возвращается False.
                return False
        return True

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(k):
        a = random.randint(2, n - 2)
        if check_composite(a, d, s, n):
            return False

    return True


while True:
    print("Меню программы\n"
          "[1]. Возведение целого числа в степень в кольце вычетов;\n"
          "[2]. Алгоритм Евклида;\n"
          "[3]. Расширенный алгоритм Евклида;\n"
          "[4]. Тест Рабина-Миллера;\n"
          "[0]. Выход из программы\n")
    try:
        # Считываем выбор пользователя и выполняем соответствующую операцию
        choice = int(input("Выберите пункт меню -> : "))
        if choice == 1:
            base = int(input("Введите основание: "))
            exponent = int(input("Введите показатель степени: "))
            modulus = int(input("Введите модуль: "))
            result = power_mod(base, exponent, modulus)
            print(f"Результат: {result}\n")
        elif choice == 2:
            a = int(input("Введите первое число: "))
            b = int(input("Введите второе число: "))
            result = gcd(a, b)
            print(f"НОД: {result}\n")
        elif choice == 3:
            a = int(input("Введите первое число: "))
            b = int(input("Введите второе число: "))
            result = extended_gcd(a, b)
            print(f"НОД: {result[0]}, x: {result[1]}, y: {result[2]}\n")
        elif choice == 4:
            n = int(input("Введите число для проверки на простоту: "))
            result = is_prime(n)
            if result:
                print("Число простое\n")
            else:
                print("Число составное\n")
        elif choice == 0:
            break
    except ValueError:
        print("Некорректный ввод.")
