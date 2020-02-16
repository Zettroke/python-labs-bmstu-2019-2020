##
# Табличка
# Медяновский Олег
#

import math
line_y = 37

# st = 1.5
# en = 10

# def f1(x):
#     return x**2 - math.cos(math.pi * x)
#
#
# def f2(x):
#     return -14.5*x**2 + 60.69*x - 70.9 + x**3


st, step, en = map(float, input('Введите начальное значение х, шаг, и конечное значение х: ').split())

if step == 0:
    print('Некорректное значение шага')
else:
    r1_in_range_cnt = 0
    l1 = []
    l2 = []
    x = st
    print('_' * 40)
    print('|{:^12}|{:^12}|{:^12}|'.format('x', 'f1(x)', 'f2(x)'))
    print('_' * 40)
    while x < en:
        r1 = x**2 - math.cos(math.pi * x)  # f1(x)
        r2 = -14.5*x**2 + 60.69*x - 70.9 + x**3  # f2(x)
        l1.append((x, r1))
        l2.append((x, r2))
        print('|{:^12.5}|{:^12.5}|{:^12.5}|'.format(x, r1, r2))
        if -0.4 <= r1 <= 0.6:
            r1_in_range_cnt += 1
        x += step
        
    print('_' * 40)
    print('Количество R1 в диапозоне -0.4 <= R1 <= 0.6:', r1_in_range_cnt)

    x_l = en-st
    col = round((en-st) / step)

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
    y_l = y_max - y_min
    
    graph = [[' ']*col for i in range(line_y)]

    if y_min <= 0:
        y = max(round(line_y - (-y_min)/y_l * line_y), 0)
        graph[y] = ['-']*col

    for p in l:
        y = max(line_y - round(((p[1] - y_min) / y_l) * line_y) - 1, 0)
        x = min(round(((p[0] - st) / x_l) * col), col-1)
        graph[y][x] = '*'

    for row_ind in range(len(graph)):
        row = graph[row_ind]
        print('{:>7.4}|'.format(((line_y-row_ind)/line_y) * y_l + y_min), end='')
        print(''.join(row))
