##
# Вводит три вершины треугольника
# Вычисляет длинны сторон треугольника, находит биссектрису проведенную из наименьшего
# угла, проверяет тупоугольность треугольника. Вводит координаты точки,
# проверяет её принадлежность треугольнику, находит расстояние до самой
# удаленной стороны.
#
# Медяновский Олег Вячеславович ИУ7-14Б

# Значение погрешности
eps = 0.00000001

a = tuple(map(float, input('Введите координаты точки a: ').split()))
b = tuple(map(float, input('Введите координаты точки b: ').split()))
c = tuple(map(float, input('Введите координаты точки c: ').split()))


# # Сравнение с учетом погрешности
# def eq(v1, v2):
#     return abs(v1 - v2) < eps
# 
# 
# # Расстояние между двумя точками
# def dist(p1, p2):
#     return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5


if abs(a[0] - b[0]) < eps and abs(b[0] - c[0]) < eps or abs(a[1] - b[1]) < eps and abs(b[1] - c[1]) < eps:
    print('Точки не могут лежать на одной прямой')
elif a[0] - b[0] != 0 and b[0] - c[0] != 0 and abs((a[1] - b[1]) / (a[0] - b[0]) - (b[1] - c[1]) / (b[0] - c[0])) < eps:
    print('Точки не могут лежать на одной прямой')
else:
    ab_l = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5  # Длина ab
    bc_l = ((b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2) ** 0.5  # Длина bc
    ca_l = ((c[0] - a[0]) ** 2 + (c[1] - a[1]) ** 2) ** 0.5  # Длина ca

    print('Длина стороны ab: {:.6}'.format(ab_l))
    print('Длина стороны bc: {:.6}'.format(bc_l))
    print('Длина стороны ca: {:.6}'.format(ca_l))

    cos_ang1 = ((a[0] - b[0])*(c[0] - b[0]) + (a[1] - b[1])*(c[1] - b[1]))/(ab_l * bc_l)  # cos ab^bc
    cos_ang2 = ((b[0] - c[0])*(a[0] - c[0]) + (b[1] - c[1])*(a[1] - c[1]))/(bc_l * ca_l)  # cos bc^ca
    cos_ang3 = ((c[0] - a[0])*(b[0] - a[0]) + (c[1] - a[1])*(b[1] - a[1]))/(ca_l * ab_l)  # cos ca^ab

    if cos_ang1 < 0 or cos_ang2 < 0 or cos_ang3 < 0:
        print('Треугольник тупоуголный')
    else:
        print('Треугольник не тупоугольный')
    
    # Ориентирую треугольник так что бы наименьший угол был ab^bc
    if cos_ang2 > cos_ang3 and cos_ang2 > cos_ang1:
        a, b, c = b, c, a
        ab_l, bc_l, ca_l = bc_l, ca_l, ab_l
        cos_ang1, cos_ang2, cos_ang3 = cos_ang2, cos_ang3, cos_ang1
    elif cos_ang3 > cos_ang2 and cos_ang3 > cos_ang1:
        a, b, c = c, a, b
        ab_l, bc_l, ca_l = ca_l, ab_l, bc_l
        cos_ang1, cos_ang2, cos_ang3 = cos_ang3, cos_ang1, cos_ang2
    
    biss_cos = ((cos_ang1 + 1) / 2) ** 0.5  # Косинус биссектрисы
    if biss_cos != 0:
        biss_k = (1 - biss_cos**2) / biss_cos  # Тангенс биссектрисы, коэффицент k
        biss_b = a[1] - biss_k * a[0]  # Коэффицент b

        if c[0] - a[0] == 0:
            biss_x = a[0]
        else:
            ac_k = (c[1] - a[1]) / (c[0] - a[0])  # Тангенс стороны aс, коэффицент k
            ac_b = a[1] - a[0] * ac_k  # Коэффицент b
            biss_x = (ac_b - biss_b) / (biss_k - ac_k)  # Координата x точки пересечания биссектрисы и стороны ac

        biss_y = biss_k * biss_x + biss_b  # Координата y точки пересечания биссектрисы и стороны ac
    else:  # Случай вертикальной биссектрисы
        biss_x = b[0]
        if c[0] - a[0] == 0:
            biss_y = a[0]
        else:
            ac_k = (c[1] - a[1]) / (c[0] - a[0])  # Тангенс стороны aс, коэффицент k
            ac_b = a[1] - a[0] * ac_k  # Коэффицент b
            biss_y = ac_k * biss_x + ac_b
    biss_l = ((biss_x - b[0])**2 + (biss_y - b[0])**2) ** 0.5  # Длина биссектрисы
    print('Длина биссектрисы проведенной из наименьшего угла: {:.6}'.format(biss_l))

    p = tuple(map(float, input('Введите координаты точки: ').split()))

    pa = ((p[0] - a[0])**2 + (p[1]-a[1])**2)**0.5
    pb = ((p[0] - b[0])**2 + (p[1]-b[1])**2)**0.5
    pc = ((p[0] - c[0])**2 + (p[1]-c[1])**2)**0.5

    #abc
    pp = (ab_l + bc_l + ca_l) / 2  # Полупериметр треугольника abc
    abc = (pp * (pp - ab_l) * (pp - bc_l) * (pp - ca_l)) ** 0.5  # Площадь треугольника abc
    #pab
    pp = (pa + pb + ab_l) / 2  # Полупериметр треугольника pab
    pab = (pp * (pp - pa) * (pp - pb) * (pp - ab_l)) ** 0.5  # Площадь труигольника pab
    #pac
    pp = (pa + pc + ca_l) / 2  # Полупериметр треугольника paс
    pac = (pp * (pp - pa) * (pp - pc) * (pp - ca_l)) ** 0.5  # Площадь труигольника paс
    #pbc
    pp = (pb + pc + bc_l) / 2  # Полупериметр треугольника pbc
    pbc = (pp * (pp - pb) * (pp - pc) * (pp - bc_l)) ** 0.5  # Площадь труигольника pbc

    if abs((pbc + pab + pac) - abc) < eps:
        print('Точка принадлежит треугольнику abc')
        d_ab = pab / ab_l * 2
        d_bc = pbc / bc_l * 2
        d_ca = pac / ca_l * 2
        if d_ab > d_bc and d_ab > d_ca:
            print('Наиболее удаленная сторона ab расстояние до неё {:.6}'.format(d_ab))
        elif d_bc > d_ab and d_bc > d_ca:
            print('Наиболее удаленная сторона bc расстояние до неё {:.6}'.format(d_bc))
        else:
            print('Наиболее удаленная сторона ca расстояние до неё {:.6}'.format(d_ca))
    else:
        print('Точка не принадлежит треугольнику abc')
