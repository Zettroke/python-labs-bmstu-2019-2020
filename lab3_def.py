##
# Защита лабораторной работы №3
# Нахождение биссектрисы треугольника из наибольшего угла
# Медяновский Олег ИУ7-14Б
eps = 0.00000001

a = tuple(map(float, input('Введите координаты точки a: ').split()))
b = tuple(map(float, input('Введите координаты точки b: ').split()))
c = tuple(map(float, input('Введите координаты точки c: ').split()))

if abs(a[0] - b[0]) < eps and abs(b[0] - c[0]) < eps or abs(a[1] - b[1]) < eps and abs(b[1] - c[1]) < eps:
    print('Точки не могут лежать на одной прямой')
elif a[0] - b[0] != 0 and b[0] - c[0] != 0 and abs((a[1] - b[1]) / (a[0] - b[0]) - (b[1] - c[1]) / (b[0] - c[0])) < eps:
    print('Точки не могут лежать на одной прямой')
else:
    ab_l = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5  # Длина ab
    bc_l = ((b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2) ** 0.5  # Длина bc
    ca_l = ((c[0] - a[0]) ** 2 + (c[1] - a[1]) ** 2) ** 0.5  # Длина ca

    # Ориентирую треугольник так что бы биссектриса выходила из точки b в сторону ca
    if bc_l > ca_l and bc_l > ab_l:
        a, b, c = c, a, b
        ab_l, bc_l, ca_l = ca_l, ab_l, bc_l
    elif ab_l > bc_l and ab_l > ca_l:
        a, b, c = b, c, a
        ab_l, bc_l, ca_l = bc_l, ca_l, ab_l

    am_coef = ab_l / (ab_l + bc_l)

    m_x = a[0] + (c[0] - a[0]) * am_coef
    m_y = a[1] + (c[1] - a[1]) * am_coef
    biss_l = ((m_x - b[0]) ** 2 + (m_y - b[1]) ** 2) ** 0.5
    print('Координаты точки пересечения биссектрисы и стороны треугольника: {:.5}, {:.5}'.format(m_x, m_y))
    print('Длина биссектрисы {:.5}'.format(biss_l))