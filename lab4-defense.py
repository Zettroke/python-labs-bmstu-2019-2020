st, step, en = map(float, input('Введите начальное значение х, шаг, и конечное значение х: ').split())

show = True
x = st
l = []

while x <= en:
    y = x**2-2*x

    l.append((round(x, 5), y))
    x += step

y_min = l[0][1]
y_max = l[0][1]

for i in l:
    if y_min > i[1]:
        y_min = i[1]
    if y_max < i[1]:
        y_max = i[1]

y_l = y_max - y_min
line_y = 130

for i in l:
    y = i[1]
    if show:
        print('{:>10.4}:'.format(i[0]), end='')
    else:
        print(' ' * 10 + ':', end='')
    if y_min > 0 or y_max < 0:
        print(' ' * round(((y - y_min) / y_l) * line_y) + '*')
    else:
        x_base = round(-y_min / y_l * line_y)
        v = round(((y - y_min) / y_l) * line_y)
        if v > x_base:
            print('{}|{}*'.format(' ' * x_base, ' ' * (v - x_base - 1)))
            pass
        elif v == x_base:
            print('{}*'.format(' ' * v))
            pass
        else:
            print('{}*{}|'.format(' ' * v, ' ' * (x_base - v - 1)))
            pass

    show = not show