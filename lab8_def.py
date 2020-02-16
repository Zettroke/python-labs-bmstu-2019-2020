# Серединные прямоугольники, x**2 с заданной точностью eps


def F(x):
    return x**3/3


def f(x):
    return x**2


def integrate(a, b, n):
    step = (b-a)/n
    res = 0.0
    for i in range(n-1):
        res += f(a + step/2 + step*i) * step
    return res


a, b = map(float, input('Введите начало и конец отрезка: ').split())

eps = float(input('Введите точность eps: '))

v = F(b) - F(a)
n = 1
print(v)
prev = integrate(a, b, n)
curr = integrate(a, b, n)
while abs(curr - prev) > eps:
    n *= 2
    prev = curr
    curr = integrate(a, b, n)
print('Метод серединных прямоугольников дает точность eps={:.5} при {} шагов. Результат: {:.8}'.format(eps, n, curr))

