import math
st, step, en = map(float, input('Введите начальное значение х, шаг, и конечное значение х: ').split())
line_y = 120
if step == 0:
    print('Некорректное значение шага')
else:
    r1_in_range_cnt = 0
    l1 = []
    l2 = []
    x = st
    print('_' * 40)
    print('|{:^12}|{:^12}|{:^12}|'.format('x', 'f1(x)', 'f2(x)'))  # Заголовок таблицы.
    print('_' * 40)
    while x <= en:
        r1 = x ** 2 - math.cos(math.pi * x)  # f1(x)
        r2 = -14.5 * x ** 2 + 60.69 * x - 70.9 + x ** 3  # f2(x)
        l1.append((x, r1))
        l2.append((x, r2))
        print('|{:^12.5}|{:^12.5}|{:^12.5}|'.format(x, r1, r2))  # Ряд таблицы значений
        if -0.4 <= r1 <= 0.6:
            r1_in_range_cnt += 1
        x += step

    print('_' * 40)
    print('Количество R1 в диапозоне -0.4 <= R1 <= 0.6:', r1_in_range_cnt)

    n = int(input('Число засечек: '))
    # line_y = (n-1) * 14
    number_width = round(line_y / (n-1))
    fomratter = str(number_width) + '.4}'
    x_l = en - st  # Длина отрезка x
    col = round((en - st) / step)  # Число колнок

    l = []
    # l.extend(l1)
    l.extend(l2)
    y_min = l[0][1]
    y_max = l[0][1]
    for i in l:
        if i[1] > y_max:
            y_max = i[1]
        if i[1] < y_min:
            y_min = i[1]
    y_l = y_max - y_min  # Длина отрезка y
    print(' '*12, end='')
    y_axis = (('{:<' + str(round(number_width / 2)) + '.4}') + ('{:^' + fomratter) * (n - 2) + ('{:>' + str(round(number_width / 2)) + '.4}'))\
        .format(*[i/(n-1)*y_l + y_min for i in range(n)])

    print(y_axis)  # Значения оси Y

    print(' ' * 12, end='')
    print(('└' + '─' * (round(number_width / 2) - 1) + ('{0:─^' + fomratter) * (n-2) + '─' * (round(number_width / 2) - 1) + '┘ Y').format('┴'))  # Ось Y

    line_y = len(y_axis)
    if y_min > 0 or y_max < 0:  # График не пересекает ось Х
        for v in l:
            y = min(round((v[1] - y_min) / y_l * line_y), line_y) - 1
            print('{:>11.5}:{}*'.format(round(v[0], 5), ' ' * y))
    else:  # График пересекает ось X
        for v in l:
            y_base = max(round((-y_min) / y_l * line_y) - 1, 0)  #
            y = max(min(round((v[1] - y_min) / y_l * line_y), line_y) - 1, 0)
            print('{:>11.5}:'.format(round(v[0], 5)), end='')
            if y == y_base:
                print('{}*'.format(' ' * y))
            elif y > y_base:
                print('{}|{}*'.format(' '*y_base, ' ' * (y - y_base - 1)))
            else:
                print('{}*{}|'.format(' '*y, ' ' * (y_base - y - 1)))

    print('{:>10}'.format('X'))
